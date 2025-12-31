"""Contact schemas - Pydantic models for contact validation"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime


class ContactCreate(BaseModel):
    """Schema for creating a contact"""
    campaign_id: str
    phone_number: str = Field(..., min_length=10, max_length=20)
    name: Optional[str] = Field(None, max_length=255)
    email: Optional[str] = Field(None, max_length=255)
    notes: Optional[str] = Field(None, max_length=2000)
    extra_metadata: Optional[dict] = None


class ContactUpdate(BaseModel):
    """Schema for updating a contact"""
    phone_number: Optional[str] = Field(None, min_length=10, max_length=20)
    name: Optional[str] = Field(None, max_length=255)
    email: Optional[str] = Field(None, max_length=255)
    status: Optional[str] = None
    attempts: Optional[int] = None
    outcome: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = Field(None, max_length=2000)
    extra_metadata: Optional[dict] = None


class ContactResponse(BaseModel):
    """Schema for contact response"""
    id: str
    campaign_id: str
    phone_number: str
    name: Optional[str]
    email: Optional[str]
    status: str
    attempts: int
    last_attempt: Optional[datetime]
    next_attempt: Optional[datetime]
    outcome: Optional[str]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ContactListResponse(BaseModel):
    """Schema for contact list response with pagination"""
    contacts: list[ContactResponse]
    total: int
    skip: int
    limit: int


class BulkImportResponse(BaseModel):
    """Schema for bulk import response"""
    imported: int
    failed: int
    total: int
    errors: list[str]
