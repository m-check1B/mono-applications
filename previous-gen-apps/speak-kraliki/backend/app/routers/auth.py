"""
Speak by Kraliki - Auth Router
Login, registration, token refresh

Rate limited to prevent brute force attacks.
"""

from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.auth import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_token,
    get_current_user,
    create_user_token_payload,
)
from app.core.config import settings
from app.models.user import User
from app.models.company import Company
from app.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
    RefreshRequest,
)
from app.middleware.rate_limit import limiter, LOGIN_RATE_LIMIT, REGISTER_RATE_LIMIT

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
@limiter.limit(LOGIN_RATE_LIMIT)
async def login(
    request: Request,
    login_request: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """Login with email and password. Rate limited to prevent brute force."""
    # Find user
    result = await db.execute(
        select(User).where(User.email == login_request.email)
    )
    user = result.scalar_one_or_none()

    if not user or not verify_password(login_request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated"
        )

    # Get company for token payload
    company_result = await db.execute(
        select(Company).where(Company.id == user.company_id)
    )
    company = company_result.scalar_one()

    # Check company is active
    if not company.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Company subscription is inactive"
        )

    # Update last login (strip tz for postgres timestamp without time zone)
    user.last_login = datetime.utcnow()
    await db.commit()

    # Create tokens with full payload (Focus by Kraliki pattern)
    token_data = create_user_token_payload(
        user_id=user.id,
        company_id=user.company_id,
        email=user.email,
        role=user.role,
        first_name=user.first_name,
        last_name=user.last_name,
        company_name=company.name,
        department_id=user.department_id,
    )

    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.access_token_expire_minutes * 60,
    )


@router.post("/register", response_model=UserResponse)
@limiter.limit(REGISTER_RATE_LIMIT)
async def register(
    request: Request,
    register_request: RegisterRequest,
    db: AsyncSession = Depends(get_db)
):
    """Register new company and admin user. Rate limited to prevent abuse."""
    # Check if email exists
    result = await db.execute(
        select(User).where(User.email == register_request.email)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create company
    slug = register_request.company_name.lower().replace(" ", "-")[:50]
    company = Company(
        name=register_request.company_name,
        slug=slug,
    )
    db.add(company)
    await db.flush()

    # Create admin user
    user = User(
        company_id=company.id,
        email=register_request.email,
        password_hash=hash_password(register_request.password),
        first_name=register_request.first_name,
        last_name=register_request.last_name,
        role="owner",
        is_verified=True,  # Auto-verify for now
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    return user


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: RefreshRequest,
    db: AsyncSession = Depends(get_db)
):
    """Refresh access token."""
    payload = verify_token(request.refresh_token, token_type="refresh")

    # Verify user still exists and is active
    result = await db.execute(
        select(User).where(User.id == UUID(payload["sub"]))
    )
    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

    # Get company for token payload
    company_result = await db.execute(
        select(Company).where(Company.id == user.company_id)
    )
    company = company_result.scalar_one()

    # Create new tokens with full payload
    token_data = create_user_token_payload(
        user_id=user.id,
        company_id=user.company_id,
        email=user.email,
        role=user.role,
        first_name=user.first_name,
        last_name=user.last_name,
        company_name=company.name,
        department_id=user.department_id,
    )

    access_token = create_access_token(token_data)
    new_refresh_token = create_refresh_token(token_data)

    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        expires_in=settings.access_token_expire_minutes * 60,
    )


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current user info."""
    result = await db.execute(
        select(User).where(User.id == UUID(current_user["sub"]))
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user


@router.post("/logout")
async def logout():
    """Logout (client should discard tokens)."""
    return {"message": "Logged out successfully"}
