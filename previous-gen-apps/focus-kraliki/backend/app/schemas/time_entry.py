"""
Time Entry Schemas - Request/Response models for time tracking
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class TimeEntryBase(BaseModel):
    """Base time entry schema."""
    task_id: Optional[str] = None
    project_id: Optional[str] = None
    workspace_id: Optional[str] = None
    description: Optional[str] = None
    billable: bool = False
    hourly_rate: Optional[int] = None
    tags: Optional[List[str]] = None


class TimeEntryCreate(TimeEntryBase):
    """Schema for creating a time entry."""
    start_time: datetime
    end_time: Optional[datetime] = None  # Null if timer is running


class TimeEntryUpdate(BaseModel):
    """Schema for updating a time entry (all fields optional)."""
    task_id: Optional[str] = None
    project_id: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    description: Optional[str] = None
    billable: Optional[bool] = None
    hourly_rate: Optional[int] = None
    tags: Optional[List[str]] = None


class TimeEntryStopRequest(BaseModel):
    """Schema for stopping a running timer."""
    end_time: Optional[datetime] = None
    description: Optional[str] = None


class TimeEntryResponse(TimeEntryBase):
    """Schema for time entry response."""
    id: str
    user_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TimeEntryListResponse(BaseModel):
    """Schema for time entry list response."""
    entries: List[TimeEntryResponse]
    total: int
