"""Authentication router - FastAPI"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import uuid4

from app.core.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, UserWithToken, TokenRefresh, TokenResponse, UserResponse
from app.services.auth_service import AuthService
from app.dependencies import get_current_user

router = APIRouter(prefix="/api/auth", tags=["authentication"])


@router.post("/register", response_model=UserWithToken, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Register a new user

    Args:
        user_data: User registration data
        db: Database session

    Returns:
        User with authentication tokens
    """
    # Check if email already exists
    result = await db.execute(
        select(User).where(User.email == user_data.email)
    )
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Hash password
    password_hash = AuthService.hash_password(user_data.password)

    # Create user
    user = User(
        id=str(uuid4()),
        email=user_data.email,
        username=user_data.username,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        password_hash=password_hash,
        role=user_data.role,
        department=user_data.department,
        phone_extension=user_data.phone_extension,
        organization_id=user_data.organization_id
    )
    if user.skills is None:
        user.skills = []

    db.add(user)
    await db.commit()
    await db.refresh(user)

    # Generate tokens
    tokens = AuthService.create_tokens_for_user(user)

    return {
        "user": user,
        **tokens
    }


@router.post("/login", response_model=UserWithToken)
async def login(
    credentials: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """
    Login with email and password

    Args:
        credentials: User login credentials
        db: Database session

    Returns:
        User with authentication tokens
    """
    # Authenticate user
    user = await AuthService.authenticate_user(db, credentials.email, credentials.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Generate tokens
    tokens = AuthService.create_tokens_for_user(user)

    return {
        "user": user,
        **tokens
    }


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    token_data: TokenRefresh,
    db: AsyncSession = Depends(get_db)
):
    """
    Refresh access token using refresh token

    Args:
        token_data: Refresh token
        db: Database session

    Returns:
        New access and refresh tokens
    """
    # TODO: Implement token refresh
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Token refresh not yet implemented"
    )


@router.post("/logout")
async def logout(
    db: AsyncSession = Depends(get_db)
):
    """
    Logout current user (revoke tokens)

    Args:
        db: Database session

    Returns:
        Success message
    """
    # TODO: Implement logout (revoke session)
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: User = Depends(get_current_user)
):
    """
    Get current authenticated user

    Args:
        current_user: Current authenticated user

    Returns:
        Current user details
    """
    return current_user
