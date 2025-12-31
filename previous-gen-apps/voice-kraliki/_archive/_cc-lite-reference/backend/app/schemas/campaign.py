"""Pydantic schemas for Campaign endpoints"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

from app.models.campaign import CampaignType


class CampaignBase(BaseModel):
    """Base campaign schema"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    type: CampaignType
    language: str = "en"
    version: str = "1.0.0"
    active: bool = False

    model_config = ConfigDict(populate_by_name=True)


class CampaignCreate(CampaignBase):
    """Schema for creating a campaign"""
    organization_id: str
    instructions: dict
    tools: Optional[dict] = None
    voice: Optional[dict] = None
    analytics: Optional[dict] = None
    metadata: Optional[dict] = Field(None, alias="metadata_payload")


class CampaignUpdate(BaseModel):
    """Schema for updating a campaign"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    type: Optional[CampaignType] = None
    language: Optional[str] = None
    active: Optional[bool] = None
    instructions: Optional[dict] = None
    tools: Optional[dict] = None
    voice: Optional[dict] = None
    analytics: Optional[dict] = None
    metadata: Optional[dict] = Field(None, alias="metadata_payload")


class CampaignResponse(CampaignBase):
    """Schema for campaign response"""
    id: str
    organization_id: str
    instructions: dict
    tools: Optional[dict] = None
    voice: Optional[dict] = None
    analytics: Optional[dict] = None
    metadata: Optional[dict] = Field(None, alias="metadata_payload")
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class CampaignMetricResponse(BaseModel):
    """Schema for campaign metrics"""
    id: str
    campaign_id: str
    calls_handled: int
    successful_completions: int
    average_handle_time: float
    customer_satisfaction: Optional[float] = None
    tools_used: dict
    error_rate: float
    last_used: datetime
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
