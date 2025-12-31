"""
Database-integrated authentication routes
Production-ready auth with SQLAlchemy models
"""

from datetime import UTC, datetime
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, EmailStr, field_validator
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..middleware.rate_limit import LOGIN_RATE_LIMIT, limiter
from ..models.user import User, UserRole
from ..services.email_service import get_email_service
from ..services.rbac_service import get_rbac_service
from .jwt_auth import get_jwt_auth_manager

router = APIRouter(prefix="/api/v1/auth", tags=["authentication"])
security = HTTPBearer(auto_error=False)


# Response models
class UserRegister(BaseModel):
    """User registration request"""

    email: EmailStr
    password: str
    full_name: str
    organization: str | None = None


class UserLogin(BaseModel):
    """User login request"""

    email: EmailStr
    password: str


class RefreshTokenRequest(BaseModel):
    """Refresh token request payload"""

    refresh_token: str | None = None


class TokenResponse(BaseModel):
    """Token response"""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 86400  # 24 hours


class UserResponse(BaseModel):
    """User response"""

    id: str
    email: str
    full_name: str
    organization: str | None
    role: str
    is_active: bool
    is_verified: bool
    last_login_at: str | None
    created_at: str
    phone_number: str | None = None
    avatar_url: str | None = None
    timezone: str = "UTC"
    language: str = "en"
    is_premium: bool = False


def _build_user_response(user: User) -> UserResponse:
    """Build user response from User model"""
    role_value = user.role.value if isinstance(user.role, UserRole) else str(user.role)
    try:
        role_enum = UserRole(role_value)
    except ValueError:
        role_enum = UserRole.AGENT
    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        organization=user.organization,
        role=role_enum.value,
        is_active=user.is_active,
        is_verified=user.is_verified,
        last_login_at=str(user.last_login_at) if user.last_login_at else None,
        created_at=str(user.created_at),
        phone_number=getattr(user, "phone_number", None),
        avatar_url=getattr(user, "avatar_url", None),
        timezone=getattr(user, "timezone", "UTC"),
        language=getattr(user, "language", "en"),
        is_premium=getattr(user, "is_premium", False),
    )


@router.post("/register", response_model=TokenResponse)
@limiter.limit(LOGIN_RATE_LIMIT)
async def register(request: Request, user_data: UserRegister, db: Session = Depends(get_db)):
    """Register a new user. Rate limited to prevent abuse."""

    auth_manager = get_jwt_auth_manager()

    # Check if user already exists
    stmt = select(User).where(User.email == user_data.email)
    existing_user = db.execute(stmt).scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="User with this email already exists"
        )

    # Create new user
    password_hash = auth_manager.hash_password(user_data.password)

    default_role = UserRole.AGENT
    rbac_service = get_rbac_service()
    role_permissions = [
        permission.value for permission in rbac_service.get_role_permissions(default_role)
    ]

    new_user = User(
        id=str(uuid4()),  # Generate UUID for user ID
        email=user_data.email,
        password_hash=password_hash,
        full_name=user_data.full_name,
        organization=user_data.organization,
        role=default_role,
        is_active=True,
        is_verified=False,  # Require email verification
        password_changed_at=datetime.now(UTC),
        permissions=role_permissions,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Create tokens
    tokens = auth_manager.create_user_tokens(new_user)

    return TokenResponse(**tokens)


@router.post("/login", response_model=TokenResponse)
@limiter.limit(LOGIN_RATE_LIMIT)
async def login(request: Request, user_data: UserLogin, db: Session = Depends(get_db)):
    """Login with email and password. Rate limited to prevent brute force attacks."""

    auth_manager = get_jwt_auth_manager()

    # Authenticate user
    user = auth_manager.authenticate_user(user_data.email, user_data.password, db)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password"
        )

    # Create tokens
    tokens = auth_manager.create_user_tokens(user)

    return TokenResponse(**tokens)


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    db: Session = Depends(get_db),
):
    """Get current user from token"""

    auth_manager = get_jwt_auth_manager()

    # Get token from header or cookie
    token = None
    if credentials:
        token = credentials.credentials

    if not token:
        auth_cookie_name = getattr(request.app.state, "auth_cookie_name", "auth_token")
        token = request.cookies.get(auth_cookie_name)

    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    # Get user from token
    user = auth_manager.get_user_from_token(token, db)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials"
        )

    return _build_user_response(user)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_access_token(
    request: Request, payload: RefreshTokenRequest | None = None, db: Session = Depends(get_db)
):
    """Refresh access token using refresh token"""

    auth_manager = get_jwt_auth_manager()

    # Get refresh token from request or cookie
    refresh_token = None
    if payload and payload.refresh_token:
        refresh_token = payload.refresh_token
    else:
        refresh_cookie_name = getattr(request.app.state, "refresh_cookie_name", "refresh_token")
        refresh_token = request.cookies.get(refresh_cookie_name)

    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing refresh token"
        )

    # Verify refresh token
    token_payload = auth_manager.verify_token(refresh_token)
    if not token_payload or token_payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )

    # Get user from database
    stmt = select(User).where(User.id == token_payload["sub"], User.is_active == True)
    user = db.execute(stmt).scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Create new tokens
    tokens = auth_manager.create_user_tokens(user)

    return TokenResponse(**tokens)


@router.post("/logout")
async def logout():
    """Clear authentication cookies"""
    response = JSONResponse(content={"detail": "Logged out"})

    # Clear cookies if they exist
    response.delete_cookie("auth_token")
    response.delete_cookie("refresh_token")

    return response


@router.post("/resend-verification")
async def resend_verification(request: Request, db: Session = Depends(get_db)):
    """Resend verification email"""
    auth_manager = get_jwt_auth_manager()
    email_service = get_email_service()

    token = None
    credentials: HTTPAuthorizationCredentials | None = await security(request)
    if credentials:
        token = credentials.credentials

    if not token:
        auth_cookie_name = getattr(request.app.state, "auth_cookie_name", "auth_token")
        token = request.cookies.get(auth_cookie_name)

    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    user = auth_manager.get_user_from_token(token, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials"
        )

    if user.is_verified:
        return {"detail": "Email already verified"}

    # Generate token and hash - store hash in DB, send plaintext to user
    plaintext_token, hashed_token = email_service.generate_verification_token_with_hash()
    token_expires = email_service.generate_token_expiration(hours=24)

    user.email_verification_token = hashed_token
    user.email_verification_token_expires = token_expires
    db.commit()

    email_sent = email_service.send_verification_email(
        to_email=user.email, token=plaintext_token, user_name=user.full_name
    )

    return {"detail": "Verification email sent", "email_sent": email_sent}


@router.post("/verify-email/{token}")
async def verify_email(token: str, db: Session = Depends(get_db)):
    """Verify user email with token"""
    email_service = get_email_service()

    if not token:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token is required")

    # Hash the incoming token to compare with stored hash
    hashed_token = email_service.hash_token(token)

    stmt = select(User).where(User.email_verification_token == hashed_token, User.is_active == True)
    user = db.execute(stmt).scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Invalid or expired token"
        )

    if (
        user.email_verification_token_expires
        and user.email_verification_token_expires < datetime.now(UTC)
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token has expired. Please request a new verification email.",
        )

    if user.is_verified:
        return {"detail": "Email already verified"}

    user.is_verified = True
    user.email_verification_token = None
    user.email_verification_token_expires = None
    db.commit()

    return {"detail": "Email verified successfully"}


class ForgotPasswordRequest(BaseModel):
    """Forgot password request"""

    email: EmailStr


class ResetPasswordRequest(BaseModel):
    """Reset password request"""

    token: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def validate_password_length(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        return v


@router.post("/forgot-password")
@limiter.limit(LOGIN_RATE_LIMIT)
async def forgot_password(request: Request, request_data: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """Send password reset email. Rate limited to prevent abuse."""
    email_service = get_email_service()

    stmt = select(User).where(User.email == request_data.email, User.is_active == True)
    user = db.execute(stmt).scalar_one_or_none()

    if not user:
        # Return same response to prevent email enumeration
        return {"detail": "Password reset email sent"}

    # Generate token and hash - store hash in DB, send plaintext to user
    plaintext_token, hashed_token = email_service.generate_verification_token_with_hash()
    token_expires = email_service.generate_token_expiration(hours=1)

    user.password_reset_token = hashed_token
    user.password_reset_token_expires = token_expires
    db.commit()

    email_sent = email_service.send_password_reset_email(
        to_email=user.email, token=plaintext_token, user_name=user.full_name
    )

    return {"detail": "Password reset email sent", "email_sent": email_sent}


@router.post("/reset-password")
@limiter.limit(LOGIN_RATE_LIMIT)
async def reset_password(request: Request, request_data: ResetPasswordRequest, db: Session = Depends(get_db)):
    """Reset password with token. Rate limited to prevent abuse."""
    email_service = get_email_service()
    auth_manager = get_jwt_auth_manager()

    # Hash the incoming token to compare with stored hash
    hashed_token = email_service.hash_token(request_data.token)

    stmt = select(User).where(
        User.password_reset_token == hashed_token, User.is_active == True
    )
    user = db.execute(stmt).scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Invalid or expired token"
        )

    if user.password_reset_token_expires and user.password_reset_token_expires < datetime.now(
        UTC
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token has expired. Please request a new password reset.",
        )

    password_hash = auth_manager.hash_password(request_data.new_password)
    user.password_hash = password_hash
    user.password_reset_token = None
    user.password_reset_token_expires = None
    user.password_changed_at = datetime.now(UTC)
    user.failed_login_attempts = 0
    user.locked_until = None
    db.commit()

    return {"detail": "Password reset successfully"}
