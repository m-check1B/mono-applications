"""
Voice by Kraliki - Usage Service
Business logic for tracking and enforcing usage limits.
"""

import logging
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.usage import UsageRecord
from app.models.user import User

logger = logging.getLogger(__name__)

# Usage limits based on plan (in minutes)
# CC-Lite (B2B) plans
PLAN_LIMITS_CCLITE = {
    "starter": 1000,
    "professional": 3000,
    "enterprise": 10000,
}

# Voice of People (B2C) plans
PLAN_LIMITS_VOP = {
    "personal": 100,
    "premium": 500,
    "pro": 2000,
}

PLAN_LIMITS = {**PLAN_LIMITS_CCLITE, **PLAN_LIMITS_VOP}


class UsageService:
    """Service for tracking and enforcing usage limits."""

    def record_usage(
        self,
        db: Session,
        user_id: str,
        quantity: int,
        service_type: str = "voice_minutes",
        reference_id: str | None = None,
    ) -> UsageRecord:
        """Record usage of a service."""
        usage = UsageRecord(
            user_id=user_id,
            service_type=service_type,
            quantity=quantity,
            reference_id=reference_id,
            timestamp=datetime.now(UTC),
        )
        db.add(usage)
        db.commit()
        db.refresh(usage)
        logger.info(f"Recorded usage: {quantity} {service_type} for user {user_id}")
        return usage

    def get_monthly_usage(
        self, db: Session, user_id: str, service_type: str = "voice_minutes"
    ) -> int:
        """Get total usage for the current month in seconds."""
        now = datetime.now(UTC)
        start_of_month = datetime(now.year, now.month, 1)

        query = select(func.sum(UsageRecord.quantity)).where(
            UsageRecord.user_id == user_id,
            UsageRecord.service_type == service_type,
            UsageRecord.timestamp >= start_of_month,
        )

        result = db.execute(query)
        total_seconds = result.scalar() or 0
        return total_seconds

    def check_limit(self, db: Session, user_id: str, service_type: str = "voice_minutes") -> bool:
        """Check if user has reached their monthly limit."""
        if service_type != "voice_minutes":
            return True

        # Get user plan/tier
        result = db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            return False

        # Determine plan from subscription metadata (set by Stripe webhook)
        # Fall back to preferences for backward compatibility
        if "subscription" in user.preferences:
            plan = user.preferences["subscription"].get("plan", "starter").lower()
        else:
            plan = user.preferences.get("plan", "starter").lower()

        limit_minutes = PLAN_LIMITS.get(plan, 1000)

        total_seconds = self.get_monthly_usage(db, user_id, service_type)
        total_minutes = total_seconds / 60

        return total_minutes < limit_minutes

    def get_usage_stats(self, db: Session, user_id: str) -> dict:
        """Get detailed usage statistics for a user/organization."""
        result = db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            return {}

        # Determine plan from subscription metadata (set by Stripe webhook)
        # Fall back to preferences for backward compatibility
        if "subscription" in user.preferences:
            plan = user.preferences["subscription"].get("plan", "starter").lower()
        else:
            plan = user.preferences.get("plan", "starter").lower()

        limit_minutes = PLAN_LIMITS.get(plan, 1000)

        voice_seconds = self.get_monthly_usage(db, user_id, "voice_minutes")
        voice_minutes = round(voice_seconds / 60, 2)

        gemini_seconds = self.get_monthly_usage(db, user_id, "voice_gemini")
        gemini_minutes = round(gemini_seconds / 60, 2)

        openai_seconds = self.get_monthly_usage(db, user_id, "voice_openai")
        openai_minutes = round(openai_seconds / 60, 2)

        return {
            "plan": plan,
            "limit_minutes": limit_minutes,
            "used_minutes": voice_minutes,
            "remaining_minutes": max(0, limit_minutes - voice_minutes),
            "percent_used": round((voice_minutes / limit_minutes * 100), 2)
            if limit_minutes > 0
            else 0,
            "breakdown": {
                "gemini_minutes": gemini_minutes,
                "openai_minutes": openai_minutes,
                "other_minutes": round(max(0, voice_minutes - gemini_minutes - openai_minutes), 2)
            }
        }


usage_service = UsageService()
