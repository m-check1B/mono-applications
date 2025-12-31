"""
Voice by Kraliki - Usage Router
API endpoints for checking usage stats and limits.
"""

import logging

from app.auth.jwt_auth import get_current_user
from app.database import get_db
from app.models.user import User
from app.services.usage_service import usage_service
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/usage", tags=["usage"])

@router.get("/stats")
async def get_usage_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get usage stats for the current user/organization."""
    stats = usage_service.get_usage_stats(db, current_user.id)
    return stats

@router.get("/check")
async def check_usage_limit(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Check if user has reached their monthly limit."""
    has_capacity = usage_service.check_limit(db, current_user.id)
    return {"has_capacity": has_capacity}
