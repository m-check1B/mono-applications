"""FastAPI dependencies for authentication and authorization"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.models.user import User, UserRole
from app.services.auth_service import AuthService
from app.core.logger import get_logger

logger = get_logger(__name__)

# HTTP Bearer token scheme (allow graceful 401 when credentials missing)
security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Get current authenticated user from JWT token

    Args:
        credentials: HTTP Authorization credentials
        db: Database session

    Returns:
        Current user

    Raises:
        HTTPException: If authentication fails
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )

    token = credentials.credentials

    try:
        # Decode token
        payload = AuthService.decode_token(token)

        # Check token type
        if payload.get("type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )

        # Get user ID from payload
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )

        # Fetch user from database
        result = await db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )

        # Check if user is active
        if user.status.value not in ["ACTIVE", "AVAILABLE"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is not active"
            )

        return user

    except ValueError as e:
        logger.warning(f"Token validation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed"
        )


async def require_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Require admin role

    Args:
        current_user: Current authenticated user

    Returns:
        Current user if admin

    Raises:
        HTTPException: If user is not admin
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


async def require_supervisor(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Require supervisor or admin role

    Args:
        current_user: Current authenticated user

    Returns:
        Current user if supervisor or admin

    Raises:
        HTTPException: If user is not supervisor/admin
    """
    if current_user.role not in [UserRole.SUPERVISOR, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Supervisor or admin access required"
        )
    return current_user
