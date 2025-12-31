"""
Speak by Kraliki - Usage Service
Business logic for tracking and enforcing usage limits.
"""

import logging
from uuid import UUID
from datetime import datetime, timedelta
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.usage import UsageRecord
from app.models.company import Company

logger = logging.getLogger(__name__)

# Usage limits based on plan (in minutes)
# Updated to match B2C Strategy (Dec 2025)
PLAN_LIMITS = {
    "free": 10,
    "personal": 100,
    "premium": 500,
    "pro": 2000,
}

class UsageService:
    """Service for tracking and enforcing usage limits."""

    async def record_usage(
        self,
        db: AsyncSession,
        company_id: UUID,
        quantity: int,
        service_type: str = "voice_minutes",
        reference_id: str | None = None
    ) -> UsageRecord:
        """Record usage of a service."""
        usage = UsageRecord(
            company_id=company_id,
            service_type=service_type,
            quantity=quantity,
            reference_id=reference_id,
            timestamp=datetime.utcnow()
        )
        db.add(usage)
        await db.commit()
        await db.refresh(usage)
        logger.info(f"Recorded usage: {quantity} {service_type} for company {company_id}")
        return usage

    async def get_monthly_usage(
        self,
        db: AsyncSession,
        company_id: UUID,
        service_type: str = "voice_minutes"
    ) -> int:
        """Get total usage for the current month in seconds."""
        now = datetime.utcnow()
        start_of_month = datetime(now.year, now.month, 1)
        
        query = select(func.sum(UsageRecord.quantity)).where(
            UsageRecord.company_id == company_id,
            UsageRecord.service_type == service_type,
            UsageRecord.timestamp >= start_of_month
        )
        
        result = await db.execute(query)
        total_seconds = result.scalar() or 0
        return total_seconds

    async def check_limit(
        self,
        db: AsyncSession,
        company_id: UUID,
        service_type: str = "voice_minutes"
    ) -> bool:
        """Check if company has reached its monthly limit."""
        if service_type != "voice_minutes":
            return True # No limits for other services yet
            
        # Get company plan
        result = await db.execute(select(Company).where(Company.id == company_id))
        company = result.scalar_one_or_none()
        if not company:
            return False
            
        plan = company.plan.lower()
        limit_minutes = PLAN_LIMITS.get(plan, 10) # Default to free
        
        total_seconds = await self.get_monthly_usage(db, company_id, service_type)
        total_minutes = total_seconds / 60
        
        return total_minutes < limit_minutes

    async def get_usage_stats(
        self,
        db: AsyncSession,
        company_id: UUID
    ) -> dict:
        """Get detailed usage statistics for a company."""
        # Get company plan
        result = await db.execute(select(Company).where(Company.id == company_id))
        company = result.scalar_one_or_none()
        if not company:
            return {}
            
        plan = company.plan.lower()
        limit_minutes = PLAN_LIMITS.get(plan, 1000)
        
        voice_seconds = await self.get_monthly_usage(db, company_id, "voice_minutes")
        voice_minutes = round(voice_seconds / 60, 2)
        
        return {
            "plan": plan,
            "limit_minutes": limit_minutes,
            "used_minutes": voice_minutes,
            "remaining_minutes": max(0, limit_minutes - voice_minutes),
            "percent_used": round((voice_minutes / limit_minutes * 100), 2) if limit_minutes > 0 else 0
        }

usage_service = UsageService()
