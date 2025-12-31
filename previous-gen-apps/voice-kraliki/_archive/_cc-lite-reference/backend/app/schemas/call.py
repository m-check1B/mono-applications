"""Pydantic schemas for Call endpoints"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

from app.models.call import CallStatus, CallDirection, TelephonyProvider


class CallBase(BaseModel):
    """Base call schema"""
    from_number: str = Field(..., min_length=10, max_length=20)
    to_number: str = Field(..., min_length=10, max_length=20)
    direction: CallDirection


class CallCreate(CallBase):
    """Schema for creating a new call"""
    campaign_id: Optional[str] = None
    contact_id: Optional[str] = None
    metadata: Optional[dict] = None


class CallUpdate(BaseModel):
    """Schema for updating a call"""
    status: Optional[CallStatus] = None
    agent_id: Optional[str] = None
    supervisor_id: Optional[str] = None
    disposition: Optional[str] = None
    notes: Optional[str] = None
    metadata: Optional[dict] = None


class CallResponse(CallBase):
    """Schema for call response"""
    id: str
    status: CallStatus
    provider: TelephonyProvider
    organization_id: str
    agent_id: Optional[str] = None
    supervisor_id: Optional[str] = None
    campaign_id: Optional[str] = None
    contact_id: Optional[str] = None
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: Optional[int] = None
    recording_url: Optional[str] = None
    disposition: Optional[str] = None
    notes: Optional[str] = None
    metadata: Optional[dict] = Field(None, alias="extra_metadata")
    created_at: datetime

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class CallList(BaseModel):
    """Schema for paginated call list"""
    items: list[CallResponse]
    total: int
    page: int
    page_size: int
    has_more: bool
