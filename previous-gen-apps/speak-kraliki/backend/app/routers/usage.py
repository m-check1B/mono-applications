"""
Speak by Kraliki - Usage Router
API endpoints for checking usage stats and limits.
"""

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.auth import get_current_user
from app.services.usage_service import usage_service

router = APIRouter(prefix="/speak/usage", tags=["usage"])

@router.get("/stats")
async def get_usage_stats(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get usage stats for the current company."""
    company_id = UUID(current_user["company_id"])
    stats = await usage_service.get_usage_stats(db, company_id)
    return stats

@router.get("/check")
async def check_usage_limit(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Check if company has reached its monthly limit."""
    company_id = UUID(current_user["company_id"])
    has_capacity = await usage_service.check_limit(db, company_id)
    return {"has_capacity": has_capacity}
