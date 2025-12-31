"""
Event Schemas - Request/Response models for calendar events
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class EventBase(BaseModel):
    """Base event schema."""
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    all_day: bool = False
    location: Optional[str] = None
    attendees: Optional[List[str]] = None
    color: Optional[str] = None
    reminder_minutes: Optional[str] = None


class EventCreate(EventBase):
    """Schema for creating an event."""
    task_id: Optional[str] = None
    google_calendar_id: Optional[str] = None


class EventUpdate(BaseModel):
    """Schema for updating an event (all fields optional)."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    all_day: Optional[bool] = None
    location: Optional[str] = None
    attendees: Optional[List[str]] = None
    color: Optional[str] = None
    reminder_minutes: Optional[str] = None
    task_id: Optional[str] = None


class EventResponse(EventBase):
    """Schema for event response."""
    id: str
    user_id: str
    task_id: Optional[str] = None
    google_event_id: Optional[str] = None
    google_calendar_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class EventListResponse(BaseModel):
    """Schema for event list response."""
    events: List[EventResponse]
    total: int
