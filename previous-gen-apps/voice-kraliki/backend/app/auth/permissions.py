"""Permission-based decorators for API endpoint security

Provides decorators to secure endpoints based on user roles and permissions.
Integrates with the RBAC system for fine-grained access control.
"""

from collections.abc import Callable
from functools import wraps

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.user import Permission, User, UserRole
from ..services.rbac_service import get_rbac_service
from .jwt_auth import get_current_active_user


def require_permissions(permissions: Permission | list[Permission]):
    """Decorator to require specific permissions for an endpoint
    
    Args:
        permissions: Single permission or list of permissions required
    """
    if isinstance(permissions, Permission):
        permissions = [permissions]

    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get user from kwargs (should be injected by FastAPI)
            current_user = kwargs.get('current_user')
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )

            rbac = get_rbac_service()
            user_role = UserRole(current_user.role)

            # Check if user has any of the required permissions
            if not rbac.has_any_permission(user_role, permissions):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Insufficient permissions. Required: {[p.value for p in permissions]}"
                )

            return await func(*args, **kwargs)
        return wrapper
    return decorator


def require_role(roles: UserRole | list[UserRole]):
    """Decorator to require specific roles for an endpoint
    
    Args:
        roles: Single role or list of roles required
    """
    if isinstance(roles, UserRole):
        roles = [roles]

    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get user from kwargs
            current_user = kwargs.get('current_user')
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )

            user_role = UserRole(current_user.role)

            if user_role not in roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Access denied. Required roles: {[r.value for r in roles]}"
                )

            return await func(*args, **kwargs)
        return wrapper
    return decorator


def require_min_role(min_role: UserRole):
    """Decorator to require minimum role level (hierarchical)
    
    Args:
        min_role: Minimum role required (hierarchy: agent < analyst < supervisor < admin)
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get user from kwargs
            current_user = kwargs.get('current_user')
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )

            rbac = get_rbac_service()
            user_role = UserRole(current_user.role)

            if not rbac.can_manage_role(min_role, user_role):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Access denied. Minimum role required: {min_role.value}"
                )

            return await func(*args, **kwargs)
        return wrapper
    return decorator


def require_resource_access(resource: str, action: str):
    """Decorator to require access to a specific resource and action
    
    Args:
        resource: Resource type (e.g., 'user', 'session', 'campaign')
        action: Action type (e.g., 'read', 'write', 'delete')
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get user from kwargs
            current_user = kwargs.get('current_user')
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )

            rbac = get_rbac_service()
            user_role = UserRole(current_user.role)

            if not rbac.can_access_resource(user_role, resource, action):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Access denied to {resource}:{action}"
                )

            return await func(*args, **kwargs)
        return wrapper
    return decorator


# FastAPI dependencies for common permission checks
def require_admin_user(current_user: User = Depends(get_current_active_user)) -> User:
    """Dependency to require admin user"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


def require_supervisor_or_admin(current_user: User = Depends(get_current_active_user)) -> User:
    """Dependency to require supervisor or admin user"""
    if current_user.role not in [UserRole.SUPERVISOR, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Supervisor or admin access required"
        )
    return current_user


def require_user_management_permission(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> User:
    """Dependency to require user management permissions"""
    rbac = get_rbac_service()
    user_role = UserRole(current_user.role)

    if not rbac.has_permission(user_role, Permission.USER_WRITE):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User management permissions required"
        )

    return current_user


def require_analytics_access(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> User:
    """Dependency to require analytics access"""
    rbac = get_rbac_service()
    user_role = UserRole(current_user.role)

    if not rbac.has_permission(user_role, Permission.ANALYTICS_READ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Analytics access required"
        )

    return current_user


def require_campaign_management(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> User:
    """Dependency to require campaign management permissions"""
    rbac = get_rbac_service()
    user_role = UserRole(current_user.role)

    if not rbac.has_permission(user_role, Permission.CAMPAIGN_WRITE):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Campaign management permissions required"
        )

    return current_user


def require_provider_management(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> User:
    """Dependency to require provider management permissions"""
    rbac = get_rbac_service()
    user_role = UserRole(current_user.role)

    if not rbac.has_permission(user_role, Permission.PROVIDER_WRITE):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Provider management permissions required"
        )

    return current_user


def require_system_admin(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> User:
    """Dependency to require system administration permissions"""
    rbac = get_rbac_service()
    user_role = UserRole(current_user.role)

    if not rbac.has_permission(user_role, Permission.SYSTEM_ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="System administration permissions required"
        )

    return current_user
