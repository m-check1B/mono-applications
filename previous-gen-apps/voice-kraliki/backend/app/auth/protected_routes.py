"""
Protected routes using JWT authentication with database integration
Examples of how to use the JWT auth dependencies with User models
"""

from typing import Any

from fastapi import APIRouter, Depends

from .jwt_auth import (
    get_current_active_user,
    get_current_user,
    require_admin,
    require_agent,
    require_campaign_read,
    require_user_management,
)

router = APIRouter(prefix="/api/v1/protected", tags=["protected"])


@router.get("/me")
async def get_current_user_info(
    current_user = Depends(get_current_user)
) -> dict[str, Any]:
    """Get current user information"""
    return {
        "message": "Access granted",
        "user": {
            "id": current_user.id,
            "email": current_user.email,
            "full_name": current_user.full_name,
            "role": current_user.role.value,
            "is_active": current_user.is_active,
            "is_verified": current_user.is_verified,
            "permissions": [p.value if hasattr(p, "value") else str(p) for p in (current_user.permissions or [])],
            "last_login_at": current_user.last_login_at.isoformat() if current_user.last_login_at else None
        }
    }


@router.get("/admin")
async def admin_only_endpoint(
    current_user = Depends(require_admin)
) -> dict[str, Any]:
    """Admin only endpoint"""
    return {
        "message": "Admin access granted",
        "user": {
            "id": current_user.id,
            "email": current_user.email,
            "role": current_user.role.value
        }
    }


@router.get("/agent")
async def agent_only_endpoint(
    current_user = Depends(require_agent)
) -> dict[str, Any]:
    """Agent and above endpoint"""
    return {
        "message": "Agent access granted",
        "user": {
            "id": current_user.id,
            "email": current_user.email,
            "role": current_user.role.value
        }
    }


@router.get("/campaigns")
async def campaigns_read_endpoint(
    current_user = Depends(require_campaign_read)
) -> dict[str, Any]:
    """Campaign read access endpoint"""
    return {
        "message": "Campaign read access granted",
        "user": {
            "id": current_user.id,
            "email": current_user.email,
            "permissions": [p.value if hasattr(p, "value") else str(p) for p in (current_user.permissions or [])]
        }
    }


@router.get("/users")
async def user_management_endpoint(
    current_user = Depends(require_user_management)
) -> dict[str, Any]:
    """User management access endpoint"""
    return {
        "message": "User management access granted",
        "user": {
            "id": current_user.id,
            "email": current_user.email,
            "role": current_user.role.value,
            "permissions": [p.value if hasattr(p, "value") else str(p) for p in (current_user.permissions or [])]
        }
    }


@router.get("/active")
async def active_user_endpoint(
    current_user = Depends(get_current_active_user)
) -> dict[str, Any]:
    """Active user endpoint"""
    return {
        "message": "Active user access granted",
        "user": {
            "id": current_user.id,
            "email": current_user.email,
            "is_active": current_user.is_active
        }
    }
