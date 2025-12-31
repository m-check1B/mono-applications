"""
Events Router - CRUD operations for calendar events
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timedelta
import logging

from app.core.database import get_db

logger = logging.getLogger(__name__)
from app.core.security import get_current_user, generate_id
from app.models.user import User
from app.models.event import Event
from app.schemas.event import (
    EventCreate,
    EventUpdate,
    EventResponse,
    EventListResponse
)

router = APIRouter(prefix="/events", tags=["events"])


@router.get("/", response_model=EventListResponse)
async def list_events(
    start_date: Optional[str] = Query(None, description="ISO format start date"),
    end_date: Optional[str] = Query(None, description="ISO format end date"),
    limit: int = Query(default=100, ge=1, le=500),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List events for the current user within date range.

    If no dates provided, returns events for next 30 days.
    """
    query = db.query(Event).filter(Event.user_id == current_user.id)

    # Apply date filters
    if start_date:
        start_dt = datetime.fromisoformat(start_date)
        query = query.filter(Event.start_time >= start_dt)
    else:
        # Default: from now
        query = query.filter(Event.start_time >= datetime.utcnow())

    if end_date:
        end_dt = datetime.fromisoformat(end_date)
        query = query.filter(Event.end_time <= end_dt)
    else:
        # Default: next 30 days
        default_end = datetime.utcnow() + timedelta(days=30)
        query = query.filter(Event.end_time <= default_end)

    # Order by start time
    query = query.order_by(Event.start_time.asc())

    events = query.limit(limit).all()
    total = query.count()

    return EventListResponse(
        events=[EventResponse.model_validate(event) for event in events],
        total=total
    )


@router.post("/", response_model=EventResponse, status_code=201)
async def create_event(
    event_data: EventCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new calendar event."""
    event = Event(
        id=generate_id(),
        user_id=current_user.id,
        **event_data.model_dump(exclude_unset=True)
    )

    db.add(event)
    db.commit()
    db.refresh(event)

    return EventResponse.model_validate(event)


@router.get("/{event_id}", response_model=EventResponse)
async def get_event(
    event_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a single event."""
    event = db.query(Event).filter(
        Event.id == event_id,
        Event.user_id == current_user.id
    ).first()

    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    return EventResponse.model_validate(event)


@router.patch("/{event_id}", response_model=EventResponse)
async def update_event(
    event_id: str,
    event_update: EventUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update an event."""
    event = db.query(Event).filter(
        Event.id == event_id,
        Event.user_id == current_user.id
    ).first()

    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    update_data = event_update.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(event, key, value)

    event.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(event)

    return EventResponse.model_validate(event)


@router.delete("/{event_id}")
async def delete_event(
    event_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete an event."""
    event = db.query(Event).filter(
        Event.id == event_id,
        Event.user_id == current_user.id
    ).first()

    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    db.delete(event)
    db.commit()

    return {"success": True, "deletedId": event_id}


async def _refresh_google_token(refresh_token: str, db: Session, user: User) -> Optional[str]:
    """
    Refresh Google OAuth access token using refresh token.

    Returns new access token or None if refresh fails.
    """
    from app.core.config import settings
    import httpx

    if not settings.GOOGLE_OAUTH_CLIENT_ID or not settings.GOOGLE_OAUTH_CLIENT_SECRET:
        return None

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "client_id": settings.GOOGLE_OAUTH_CLIENT_ID,
                    "client_secret": settings.GOOGLE_OAUTH_CLIENT_SECRET,
                    "refresh_token": refresh_token,
                    "grant_type": "refresh_token"
                }
            )

            if response.status_code == 200:
                token_data = response.json()
                new_access_token = token_data.get("access_token")
                expires_in = token_data.get("expires_in", 3600)

                # Update user preferences with new token
                prefs = user.preferences or {}
                if "calendar_sync" in prefs:
                    prefs["calendar_sync"]["access_token"] = new_access_token
                    prefs["calendar_sync"]["expires_at"] = (datetime.utcnow() + timedelta(seconds=expires_in)).isoformat()
                    user.preferences = prefs
                    db.commit()

                return new_access_token
    except Exception as e:
        logger.warning(f"Token refresh failed: {e}")

    return None


@router.post("/sync/google", status_code=200)
async def sync_google_calendar(
    calendar_id: str = Query(default="primary"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Sync events from Google Calendar.

    Requires Google OAuth token stored in user preferences.
    Automatically refreshes expired tokens.
    """
    from app.services.google_calendar import GoogleCalendarService
    from app.core.security import generate_id

    # Get calendar sync preferences
    prefs = current_user.preferences or {}
    calendar_sync = prefs.get("calendar_sync", {})

    if not calendar_sync.get("enabled"):
        raise HTTPException(status_code=400, detail="Calendar sync is not enabled")

    access_token = calendar_sync.get("access_token")
    refresh_token = calendar_sync.get("refresh_token")
    expires_at_str = calendar_sync.get("expires_at")

    if not access_token:
        raise HTTPException(status_code=400, detail="No Google Calendar access token found. Please connect your Google account.")

    # Check if token is expired and refresh if needed
    if expires_at_str:
        try:
            expires_at = datetime.fromisoformat(expires_at_str)
            if expires_at <= datetime.utcnow() + timedelta(minutes=5):  # Refresh if expires in 5 minutes
                if refresh_token:
                    new_token = await _refresh_google_token(refresh_token, db, current_user)
                    if new_token:
                        access_token = new_token
                    else:
                        raise HTTPException(status_code=401, detail="Failed to refresh Google Calendar token. Please reconnect your account.")
                else:
                    raise HTTPException(status_code=401, detail="Google Calendar token expired. Please reconnect your account.")
        except (ValueError, TypeError) as e:
            logger.warning(f"Token expiry parsing failed: {e}. Proceeding with existing token.")

    # Initialize Google Calendar service
    try:
        calendar_service = GoogleCalendarService(
            oauth_token=access_token,
            refresh_token=refresh_token
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initialize Google Calendar service: {str(e)}")

    # Sync events from Google Calendar
    try:
        focus_events = await calendar_service.sync_events(
            user_id=current_user.id,
            calendar_id=calendar_id
        )

        # Upsert events into database
        synced_count = 0
        for event_data in focus_events:
            # Check if event already exists
            existing = db.query(Event).filter(
                Event.user_id == current_user.id,
                Event.google_event_id == event_data.get("google_event_id")
            ).first()

            if existing:
                # Update existing event
                for key, value in event_data.items():
                    if key != "id":  # Don't update primary key
                        setattr(existing, key, value)
                existing.updated_at = datetime.utcnow()
            else:
                # Create new event
                new_event = Event(**event_data)
                db.add(new_event)

            synced_count += 1

        db.commit()

        # Update last sync timestamp
        prefs["calendar_sync"]["last_sync"] = datetime.utcnow().isoformat()
        current_user.preferences = prefs
        db.commit()

        return {
            "success": True,
            "message": f"Successfully synced {synced_count} events from Google Calendar",
            "synced_count": synced_count,
            "calendar_id": calendar_id
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Calendar sync failed: {str(e)}")
