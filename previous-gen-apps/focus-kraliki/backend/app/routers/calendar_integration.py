from datetime import datetime, timedelta

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.core.config import settings
from app.services import calendar_adapter


router = APIRouter(prefix="/integration/calendar", tags=["calendar-integration"])


class CalendarEventRequest(BaseModel):
    title: str = Field(..., min_length=1)
    duration_minutes: int = Field(30, ge=1, le=480)


@router.get("/status")
async def get_calendar_status():
    if not getattr(settings, "ENABLE_CALENDAR_INTEGRATION", False):
        return {
            "enabled": False,
            "reachable": False,
            "reason": "Calendar integration disabled",
        }

    try:
        reachable = await calendar_adapter.ping_calendar()
        return {
            "enabled": True,
            "reachable": bool(reachable),
            "reason": None if reachable else "Calendar service unavailable",
        }
    except calendar_adapter.CalendarNotConfigured as exc:
        return {"enabled": False, "reachable": False, "reason": str(exc)}
    except Exception as exc:  # pragma: no cover - defensive fallback
        return {"enabled": True, "reachable": False, "reason": str(exc)}


@router.post("/events")
async def create_calendar_event(request: CalendarEventRequest):
    start = datetime.utcnow()
    end = start + timedelta(minutes=request.duration_minutes)

    try:
        event_id = await calendar_adapter.create_calendar_event(
            title=request.title,
            start_iso=start.isoformat(),
            end_iso=end.isoformat(),
        )
        return {"created": True, "event_id": event_id}
    except calendar_adapter.CalendarNotConfigured as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=503, detail=str(exc))
