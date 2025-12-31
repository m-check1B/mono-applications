"""
Calendar Adapter

Thin boundary that attempts to use tools-core Google Calendar service if available.
Falls back gracefully when not installed/enabled.
"""

from typing import Optional

from app.core.config import settings

try:
    from tools_core import GoogleCalendarService, CalendarEvent  # type: ignore
except Exception as e:
    import logging
    logging.getLogger(__name__).warning(f"Failed to import optional calendar dependencies: {e}")
    GoogleCalendarService = None
    CalendarEvent = None


class CalendarNotConfigured(Exception):
    pass


def get_calendar_service():
    if not getattr(settings, "ENABLE_CALENDAR_INTEGRATION", False):
        raise CalendarNotConfigured("Calendar integration disabled")
    if GoogleCalendarService is None:
        raise CalendarNotConfigured("tools-core not available")
    return GoogleCalendarService()


async def ping_calendar() -> bool:
    """Basic readiness check for calendar integration."""
    svc = get_calendar_service()
    # If import succeeded, consider integration reachable (no external call here)
    return svc is not None


async def create_calendar_event(
    title: str,
    start_iso: str,
    end_iso: str,
    calendar_id: Optional[str] = None
) -> str:
    svc = get_calendar_service()
    if CalendarEvent is None:
        raise CalendarNotConfigured("CalendarEvent model not available")
    event = CalendarEvent(
        title=title,
        start=start_iso,
        end=end_iso,
        calendar_id=calendar_id or "primary",
    )
    created = await svc.create_event(event)
    return created.id
