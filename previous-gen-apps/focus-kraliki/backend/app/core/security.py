from datetime import datetime, timedelta
from typing import Optional, TYPE_CHECKING
from jose import JWTError, jwt
import bcrypt
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.database import get_db
from app.core.ed25519_auth import ed25519_auth
import secrets
import logging

if TYPE_CHECKING:
    from app.models.user import User

logger = logging.getLogger(__name__)

security = HTTPBearer(auto_error=False)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())


def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def create_agent_token(
    user_id: Optional[str] = None, data: Optional[dict] = None
) -> str:
    """
    Create an agent-scoped JWT token for II-Agent.

    This token has a longer expiry (2 hours) and includes a scope claim
    to distinguish it from regular user tokens.

    Args:
        user_id: The user ID to encode in the token

    Returns:
        Encoded JWT token string
    """
    if data is not None:
        # Backwards compatibility path used by tests/fixtures
        user_id = data.get("sub") or user_id
    if not user_id:
        raise ValueError("user_id is required to create an agent token")

    expire = datetime.utcnow() + timedelta(minutes=settings.AGENT_TOKEN_EXPIRE_MINUTES)
    to_encode = {
        "sub": user_id,
        "scope": "agent",
        "exp": expire,
        "iat": datetime.utcnow(),
    }
    if data:
        # Merge any additional claims (e.g., organization) for testing overrides
        extra = data.copy()
        extra.pop("sub", None)
        to_encode.update(extra)

    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def decode_token(token: str) -> dict:
    """
    Decode a JWT, supporting both legacy HS256 tokens and new Ed25519 tokens.

    Returns:
        Decoded payload dictionary
    """
    # First try legacy HS256 tokens
    try:
        return jwt.decode(
            token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
    except JWTError as e:
        # Not an error - expected when token is Ed25519 format, so debug level is appropriate
        logger.debug(
            f"Legacy HS256 token decoding failed, falling back to Ed25519: {e}"
        )

    # Fallback to Ed25519 (Stack 2026) tokens
    try:
        return ed25519_auth.verify_token(token, expected_type="access")
    except HTTPException:
        raise
    except Exception as e:
        logger.warning(f"Token verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> "User":
    """
    Get the current authenticated user from a JWT token.

    This dependency supports both standard user tokens and agent-scoped tokens.
    The scope claim is optional - if present and set to "agent", it indicates
    the token was issued for II-Agent, but authentication works the same way.

    Also supports:
    - Platform mode: trusts X-User-Id/X-Org-Id headers (set via middleware)
    - Kraliki internal bypass: via X-Kraliki-Session header
    """
    # Lazy import to avoid circular dependency (security <-> user model)
    from app.models.user import User

    # Check for platform mode (middleware sets request.state.user_id)
    if hasattr(request.state, 'user_id') and request.state.user_id:
        platform_user_id = request.state.user_id
        platform_org_id = getattr(request.state, 'org_id', None)

        # Find existing user by platform ID or create new one
        platform_user = db.query(User).filter(User.id == platform_user_id).first()
        if not platform_user:
            # Create platform user with the trusted ID
            platform_user = User(
                id=platform_user_id,
                email=f"{platform_user_id}@platform.local",
                username=platform_user_id,
                firstName="Platform",
                lastName="User",
                passwordHash=get_password_hash(secrets.token_urlsafe(32)),
                onboardingCompleted=True,
            )
            db.add(platform_user)
            db.commit()
            db.refresh(platform_user)
            logger.info(f"Created platform user: {platform_user_id} (org: {platform_org_id})")
        return platform_user

    # Check for Kraliki internal bypass
    if request and request.headers:
        kraliki_session = request.headers.get("X-Kraliki-Session")
        if kraliki_session == "kraliki-internal":
            # Get user info from Kraliki headers
            user_email = request.headers.get(
                "X-Kraliki-User-Email", "agent@kraliki.local"
            )
            user_name = request.headers.get("X-Kraliki-User-Name", "Kraliki User")
            user_id = request.headers.get("X-Kraliki-User-Id", "unknown")

            # Find existing user by email or create new one
            kraliki_user = db.query(User).filter(User.email == user_email).first()
            if not kraliki_user:
                # Create user matching the Kraliki identity
                name_parts = user_name.split(" ", 1)
                first_name = name_parts[0] if name_parts else "User"
                last_name = name_parts[1] if len(name_parts) > 1 else ""

                kraliki_user = User(
                    id=generate_id(),
                    email=user_email,
                    username=user_email.split("@")[0],
                    firstName=first_name,
                    lastName=last_name,
                    passwordHash=get_password_hash(secrets.token_urlsafe(32)),
                    onboardingCompleted=True,
                )
                db.add(kraliki_user)
                db.commit()
                db.refresh(kraliki_user)
                logger.info(f"Created Kraliki-linked user: {user_email}")
            return kraliki_user

    if credentials is None or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    payload = decode_token(token)
    user_id: str = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
        )
    return user


async def get_optional_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db),
) -> Optional["User"]:
    """
    Optional version of get_current_user. Returns None if no valid token is provided.
    """
    try:
        return await get_current_user(request, credentials, db)
    except HTTPException as e:
        if e.status_code == status.HTTP_401_UNAUTHORIZED:
            return None
        raise e


def generate_id() -> str:
    """Generate a unique ID similar to Prisma's cuid()"""
    return secrets.token_urlsafe(16)
