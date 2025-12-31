"""
JWT Authentication Dependencies
FastAPI dependencies for JWT authentication with database integration
"""

import logging
import secrets
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import uuid4

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.user import Permission, User, UserRole
from .ed25519_auth import get_auth_manager
from .token_revocation import get_revocation_service

logger = logging.getLogger(__name__)

security = HTTPBearer(auto_error=False)


class JWTAuthManager:
    """JWT Authentication Manager with database integration"""

    def __init__(self):
        self.auth = get_auth_manager()

    def verify_token(self, token: str) -> dict[str, Any] | None:
        """Verify JWT token and return payload, checking revocation status"""
        payload = self.auth.verify_token(token)
        if not payload:
            return None

        # Check if token is revoked
        jti = payload.get("jti")
        if jti:
            revocation_service = get_revocation_service()
            if revocation_service.is_token_revoked(jti):
                logger.warning(f"Token with JTI {jti} has been revoked")
                return None

            # Check if token was issued before user tokens were revoked
            user_id = payload.get("sub")
            iat = payload.get("iat")
            if user_id and iat:
                token_issued_at = datetime.fromtimestamp(iat)
                if revocation_service.is_token_revoked_for_user(user_id, token_issued_at):
                    logger.warning(f"Token issued before user {user_id} tokens were revoked")
                    return None

        return payload

    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        return self.auth.hash_password(password)

    def get_user_from_token(self, token: str, db: Session) -> User | None:
        """Get user from valid token with database lookup"""
        payload = self.verify_token(token)
        if not payload:
            return None

        stmt = select(User).where(
            User.id == payload["sub"],
            User.is_active == True
        )
        return db.execute(stmt).scalar_one_or_none()

    def authenticate_user(self, email: str, password: str, db: Session) -> User | None:
        """Authenticate user with email and password"""
        stmt = select(User).where(User.email == email, User.is_active == True)
        user = db.execute(stmt).scalar_one_or_none()

        if not user or not self.auth.verify_password(password, user.password_hash):
            return None

        # Update last login
        user.last_login_at = datetime.now(UTC)
        db.commit()

        return user

    def create_user_tokens(self, user: User) -> dict:
        """Create access and refresh tokens for user"""
        role_value = user.role.value if isinstance(user.role, UserRole) else str(user.role or "")
        access_token = self.auth.create_access_token(
            user_id=str(user.id),
            email=user.email,
            role=role_value,
            org_id=str(user.organization) if user.organization else None,
            expires_delta=timedelta(minutes=1440)  # 24 hours
        )

        refresh_token = self.auth.create_refresh_token(str(user.id))

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": 1440 * 60  # 24 hours in seconds
        }


# Global auth manager instance
jwt_auth_manager = None


def get_jwt_auth_manager() -> JWTAuthManager:
    """Get or create JWT auth manager instance"""
    global jwt_auth_manager
    if jwt_auth_manager is None:
        jwt_auth_manager = JWTAuthManager()
    return jwt_auth_manager


async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """FastAPI dependency to get current authenticated user

    This dependency supports both standard JWT tokens and Kraliki internal bypass.
    When requests come from Kraliki dashboard, they are trusted internal requests.
    """

    # Check for Kraliki internal bypass
    if request and request.headers:
        kraliki_session = request.headers.get("X-Kraliki-Session")
        if kraliki_session == "kraliki-internal":
            # Get user info from Kraliki headers
            user_email = request.headers.get("X-Kraliki-User-Email", "agent@kraliki.local")
            user_name = request.headers.get("X-Kraliki-User-Name", "Kraliki User")

            # Find existing user by email or create new one
            stmt = select(User).where(User.email == user_email)
            kraliki_user = db.execute(stmt).scalar_one_or_none()

            if not kraliki_user:
                # Create user matching the Kraliki identity
                auth_manager = get_jwt_auth_manager()

                kraliki_user = User(
                    id=str(uuid4()),  # Generate UUID for user ID
                    email=user_email,
                    full_name=user_name,
                    password_hash=auth_manager.hash_password(secrets.token_urlsafe(32)),
                    role=UserRole.ADMIN,  # Kraliki agents get admin access
                    is_active=True,
                    is_verified=True,
                    permissions=[p.value for p in Permission],  # All permissions
                )
                db.add(kraliki_user)
                db.commit()
                db.refresh(kraliki_user)
                logger.info(f"Created Kraliki-linked user: {user_email}")
            return kraliki_user

    auth_manager = get_jwt_auth_manager()

    # Get token from header or cookie
    token = None
    if credentials:
        token = credentials.credentials

    if not token:
        # Try to get from cookie
        auth_cookie_name = getattr(request.app.state, 'auth_cookie_name', 'auth_token')
        token = request.cookies.get(auth_cookie_name)

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = auth_manager.get_user_from_token(token, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current active user"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


async def get_current_verified_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """Get current verified user"""
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email not verified"
        )
    return current_user


def require_permissions(required_permissions: list[str | Permission]):
    """Decorator to require specific permissions"""

    async def permission_checker(
        current_user: User = Depends(get_current_active_user)
    ) -> User:
        user_permissions: set[str] = set()
        for stored_perm in current_user.permissions or []:
            if isinstance(stored_perm, Permission):
                user_permissions.add(stored_perm.value)
            else:
                try:
                    user_permissions.add(Permission(str(stored_perm)).value)
                except ValueError:
                    user_permissions.add(str(stored_perm))

        for perm in required_permissions:
            perm_enum = Permission(perm) if isinstance(perm, str) else perm

            if perm_enum.value not in user_permissions:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission required: {perm_enum.value}"
                )

        return current_user

    return permission_checker


def require_role(required_roles: list[str | UserRole]):
    """Decorator to require specific roles"""

    async def role_checker(
        current_user: User = Depends(get_current_active_user)
    ) -> User:
        user_role = (
            current_user.role
            if isinstance(current_user.role, UserRole)
            else UserRole(current_user.role)
        )

        for role in required_roles:
            if isinstance(role, str):
                role_enum = UserRole(role)
            else:
                role_enum = role

            if user_role == role_enum:
                return current_user

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Role required: one of {[r.value if isinstance(r, UserRole) else r for r in required_roles]}"
        )

    return role_checker


# Common role dependencies
require_admin = require_role([UserRole.ADMIN])
require_agent = require_role([UserRole.AGENT, UserRole.ADMIN, UserRole.SUPERVISOR])
require_supervisor = require_role([UserRole.SUPERVISOR, UserRole.ADMIN])

# Common permission dependencies
require_campaign_read = require_permissions([Permission.CAMPAIGN_READ])
require_campaign_write = require_permissions([Permission.CAMPAIGN_WRITE])
require_analytics_read = require_permissions([Permission.ANALYTICS_READ])
require_user_management = require_permissions([Permission.USER_WRITE])
require_system_admin = require_permissions([Permission.SYSTEM_ADMIN])

# Alias for backward compatibility
require_user = get_current_active_user
