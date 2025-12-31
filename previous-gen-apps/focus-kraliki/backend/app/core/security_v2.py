"""
Security Module V2 - Stack 2026 Compliant
Integrates Ed25519 JWT + Token Revocation + Password Hashing
"""

from datetime import timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import bcrypt
import secrets

from app.core.database import get_db
from app.core.ed25519_auth import ed25519_auth
from app.core.token_revocation import token_blacklist
from app.models.user import User


security = HTTPBearer(auto_error=False)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against bcrypt hash."""
    try:
        return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())
    except ValueError:
        # Invalid salt or hash format should not raise to callers.
        return False


def get_password_hash(password: str) -> str:
    """Hash password using bcrypt."""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def generate_id() -> str:
    """Generate a unique ID similar to Prisma's cuid()."""
    return secrets.token_urlsafe(16)


def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create Ed25519 JWT access token.

    Args:
        data: Payload data (must include 'sub' for user ID)
        expires_delta: Optional custom expiration (default: 15 min)

    Returns:
        Encoded JWT string
    """
    return ed25519_auth.create_access_token(data, expires_delta)


def create_refresh_token(data: dict) -> str:
    """
    Create Ed25519 JWT refresh token.

    Args:
        data: Payload data (must include 'sub' for user ID)

    Returns:
        Encoded JWT string
    """
    return ed25519_auth.create_refresh_token(data)


def decode_token(token: str) -> dict:
    """
    Verify and decode Ed25519 JWT token.

    Args:
        token: JWT token string

    Returns:
        Decoded payload

    Raises:
        HTTPException: If token is invalid or expired
    """
    return ed25519_auth.verify_token(token, expected_type="access")


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current user from JWT token with revocation check.

    This dependency:
    1. Extracts token from Authorization header
    2. Verifies Ed25519 signature
    3. Checks if token is blacklisted
    4. Checks if user tokens are globally revoked
    5. Fetches user from database

    Args:
        credentials: HTTP Bearer credentials
        db: Database session

    Returns:
        User object

    Raises:
        HTTPException: If authentication fails
    """
    if credentials is None or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )

    token = credentials.credentials

    # Verify token signature and expiration
    payload = decode_token(token)
    user_id: str = payload.get("sub")

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials (missing user ID)"
        )

    # Check if token is blacklisted (logout)
    if await token_blacklist.is_revoked(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked (logged out)"
        )

    # Check if all user tokens are revoked (password change)
    if await token_blacklist.is_user_revoked(user_id):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="All user tokens have been revoked (security action)"
        )

    # Fetch user from database
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    return user


async def revoke_token(token: str):
    """
    Revoke a specific token (logout).

    Args:
        token: JWT token to revoke
    """
    # Decode without verification to get expiration
    payload = ed25519_auth.decode_without_verification(token)
    exp = payload.get("exp")

    if exp:
        await token_blacklist.revoke_token(token, exp)


async def revoke_all_user_tokens(user_id: str):
    """
    Revoke all tokens for a user (password change, security breach).

    Args:
        user_id: User ID to revoke all tokens for
    """
    await token_blacklist.revoke_all_user_tokens(user_id)
