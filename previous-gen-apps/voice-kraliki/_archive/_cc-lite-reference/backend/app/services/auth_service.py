"""Authentication service - JWT token management and password hashing"""

from datetime import datetime
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.security import jwt_manager, hash_password, verify_password
from app.core.logger import get_logger
from app.models.user import User

logger = get_logger(__name__)


class AuthService:
    """
    Authentication service for user management and JWT tokens
    Uses Ed25519 JWT (Stack 2026 compliant)
    """

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt"""
        return hash_password(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return verify_password(plain_password, hashed_password)

    @staticmethod
    def create_access_token(data: dict) -> str:
        """Create Ed25519-signed JWT access token"""
        return jwt_manager.create_access_token(data)

    @staticmethod
    def create_refresh_token(data: dict) -> str:
        """Create Ed25519-signed JWT refresh token"""
        return jwt_manager.create_refresh_token(data)

    @staticmethod
    def decode_token(token: str) -> dict:
        """Decode and validate Ed25519-signed JWT token"""
        return jwt_manager.verify_token(token)

    @staticmethod
    async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
        """Get user by email"""
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    @staticmethod
    async def authenticate_user(db: AsyncSession, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password"""
        user = await AuthService.get_user_by_email(db, email)

        if not user:
            logger.warning(f"Login attempt for non-existent user: {email}")
            return None

        if not user.password_hash:
            logger.warning(f"User {email} has no password hash")
            return None

        if not AuthService.verify_password(password, user.password_hash):
            logger.warning(f"Invalid password for user: {email}")
            return None

        # Update last login
        user.last_login_at = datetime.utcnow()
        await db.commit()

        return user

    @staticmethod
    def create_tokens_for_user(user: User) -> dict:
        """Create access and refresh tokens for a user"""
        token_data = {
            "sub": user.id,
            "email": user.email,
            "role": user.role.value,
        }

        access_token = AuthService.create_access_token(token_data)
        refresh_token = AuthService.create_refresh_token(token_data)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }
