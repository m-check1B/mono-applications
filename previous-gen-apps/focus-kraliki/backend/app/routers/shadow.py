import json
import inspect
import logging
from datetime import datetime
from typing import Optional, List, Any, Dict

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.services.shadow_analyzer import ShadowAnalyzerService
from app.schemas.shadow import (
    ShadowProfileResponse,
    ShadowInsightResponse,
    DailyInsightResponse,
    ProgressResponse,
    UnlockResponse,
)

router = APIRouter(prefix="/shadow", tags=["shadow"])


# Lightweight placeholders used in unit tests (patched with mocks in tests).
class _AnthropicMessages:
    async def create(self, *args, **kwargs):
        raise NotImplementedError("Anthropic client not configured")


class _AnthropicClient:
    def __init__(self):
        self.messages = _AnthropicMessages()


anthropic_client = _AnthropicClient()


class _ShadowInsightsDB:
    """Simple in-memory store used in unit tests (patched)."""

    def __init__(self):
        self._data: Dict[str, List[dict]] = {}

    async def get(self, user_id: str) -> List[dict]:
        return self._data.get(user_id, [])

    async def upsert(self, user_id: str, insights: List[dict]):
        self._data[user_id] = insights

    async def acknowledge(self, user_id: str, insight_id: str) -> bool:
        insights = self._data.get(user_id, [])
        for insight in insights:
            if insight.get("id") == insight_id:
                insight["acknowledged"] = True
                return True
        return False


shadow_insights_db = _ShadowInsightsDB()


async def _maybe_await(value: Any):
    return await value if inspect.isawaitable(value) else value


def get_shadow_service(db: Session = Depends(get_db)) -> ShadowAnalyzerService:
    """Get shadow analyzer service"""
    return ShadowAnalyzerService(db)


@router.post("/analyze")
async def analyze_shadow(
    payload: Dict[str, Any],
    current_user: User = Depends(get_current_user)
):
    """Analyze task patterns via Anthropic (mocked in tests)."""
    task_patterns = payload.get("taskPatterns", [])

    try:
        ai_response = await _maybe_await(
            anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1024,
                messages=[
                    {"role": "user", "content": json.dumps({"tasks": task_patterns})}
                ]
            )
        )
        content = ai_response.content[0].text if getattr(ai_response, "content", None) else "{}"
        parsed = json.loads(content or "{}")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Shadow analysis failed: {exc}")

    return {
        "patterns": parsed.get("patterns", []),
        "insights": parsed.get("insights", []),
        "recommendations": parsed.get("recommendations", []),
        "shadowScore": parsed.get("shadowScore", 0),
    }


@router.post("/profile", response_model=ShadowProfileResponse)
async def create_shadow_profile(
    current_user: User = Depends(get_current_user),
    shadow_service: ShadowAnalyzerService = Depends(get_shadow_service)
):
    """Create or get shadow profile with archetype analysis"""
    try:
        profile = await shadow_service.create_profile(current_user.id)
        return profile
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create profile: {str(e)}")


@router.get("/profile", response_model=ShadowProfileResponse)
async def get_shadow_profile(
    current_user: User = Depends(get_current_user),
    shadow_service: ShadowAnalyzerService = Depends(get_shadow_service)
):
    """Get user's shadow profile"""
    profile = await shadow_service.get_profile(current_user.id)
    if not profile:
        # Auto-create if doesn't exist
        return await shadow_service.create_profile(current_user.id)
    return profile


@router.get("/insight", response_model=DailyInsightResponse)
async def get_daily_insight(
    day: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    shadow_service: ShadowAnalyzerService = Depends(get_shadow_service)
):
    """Get shadow insight for a specific day (or current day)"""
    try:
        insight = await shadow_service.get_daily_insight(current_user.id, day)
        return insight
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get insight: {str(e)}")


@router.post("/unlock", response_model=UnlockResponse)
async def unlock_next_insight(
    current_user: User = Depends(get_current_user),
    shadow_service: ShadowAnalyzerService = Depends(get_shadow_service)
):
    """Unlock the next day's insight"""
    try:
        result = await shadow_service.unlock_next_day(current_user.id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to unlock: {str(e)}")


@router.get("/progress", response_model=ProgressResponse)
async def get_progress(
    current_user: User = Depends(get_current_user),
    shadow_service: ShadowAnalyzerService = Depends(get_shadow_service)
):
    """Get overall shadow work progress"""
    progress = await shadow_service.get_progress(current_user.id)
    if not progress:
        raise HTTPException(status_code=404, detail="No shadow profile found. Create a profile first.")
    return progress


@router.get("/insights")
async def get_insights(
    current_user: User = Depends(get_current_user),
):
    """Return unlocked insights (patched DB in tests)."""
    insights = await _maybe_await(shadow_insights_db.get(current_user.id))
    total = len(insights)
    if total == 0:
        return {"insights": [], "total": 0, "currentDay": 0}

    # Determine current day based on earliest createdAt
    try:
        earliest = min(datetime.fromisoformat(i["createdAt"]) for i in insights if i.get("createdAt"))
        days_since = (datetime.utcnow() - earliest).days + 1
    except Exception as e:
        logger.warning(f"Failed to calculate days_since from insights for user {current_user.id}: {e}")
        days_since = total

    current_day = min(30, max(days_since, total))
    unlocked = insights[:current_day]

    return {
        "insights": unlocked,
        "total": total,
        "currentDay": current_day
    }


@router.post("/insights/{insight_id}/acknowledge")
async def acknowledge_insight(
    insight_id: str,
    current_user: User = Depends(get_current_user),
):
    insights = await _maybe_await(shadow_insights_db.get(current_user.id))
    if not any(i.get("id") == insight_id for i in insights):
        raise HTTPException(status_code=404, detail="Insight not found")

    await _maybe_await(shadow_insights_db.acknowledge(current_user.id, insight_id))
    return {"success": True, "message": "Insight acknowledged"}


@router.get("/unlock-status")
async def unlock_status(
    current_user: User = Depends(get_current_user),
):
    insights = await _maybe_await(shadow_insights_db.get(current_user.id))
    total_days = 30

    if not insights:
        return {
            "currentDay": 0,
            "totalDays": total_days,
            "unlockedInsights": 0,
            "nextUnlockDay": 1
        }

    try:
        earliest = min(datetime.fromisoformat(i["createdAt"]) for i in insights if i.get("createdAt"))
        days_since = (datetime.utcnow() - earliest).days + 1
    except Exception as e:
        logger.warning(f"Failed to calculate days_since from insights for user {current_user.id}: {e}")
        days_since = len(insights)

    current_day = min(total_days, days_since)
    unlocked = min(total_days, len(insights), current_day)
    next_unlock_day = min(total_days, current_day + 1)

    return {
        "currentDay": current_day,
        "totalDays": total_days,
        "unlockedInsights": unlocked,
        "nextUnlockDay": next_unlock_day
    }
