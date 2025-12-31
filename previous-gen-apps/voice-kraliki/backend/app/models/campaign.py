"""Campaign and campaign script models."""

from datetime import UTC, datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel
from sqlalchemy import JSON, Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class CampaignStatus(str, Enum):
    """Campaign status enumeration."""
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class CampaignType(str, Enum):
    """Campaign type enumeration."""
    OUTBOUND_SALES = "outbound_sales"
    INBOUND_SUPPORT = "inbound_support"
    SURVEY = "survey"
    NOTIFICATION = "notification"
    MARKETING = "marketing"


class Campaign(Base):
    """Campaign model for organizing call operations."""

    __tablename__ = "campaigns"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)

    # Campaign configuration
    campaign_type = Column(String(50), default=CampaignType.OUTBOUND_SALES, nullable=False)
    status = Column(String(20), default=CampaignStatus.DRAFT, nullable=False)

    # Provider and routing
    primary_provider = Column(String(50), nullable=False)
    backup_providers = Column(JSON, default=list, nullable=False)
    routing_strategy = Column(String(50), default="round_robin", nullable=False)

    # Schedule and timing
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
    timezone = Column(String(50), default="UTC", nullable=False)
    business_hours_only = Column(Boolean, default=True, nullable=False)

    # Targeting and configuration
    target_audience = Column(JSON, default=dict, nullable=False)
    dialing_rules = Column(JSON, default=dict, nullable=False)
    configuration = Column(JSON, default=dict, nullable=False)

    # Performance metrics
    total_calls = Column(Integer, default=0, nullable=False)
    connected_calls = Column(Integer, default=0, nullable=False)
    successful_calls = Column(Integer, default=0, nullable=False)
    conversion_rate = Column(Float, default=0.0, nullable=False)

    # Limits and controls
    max_concurrent_calls = Column(Integer, default=10, nullable=False)
    calls_per_hour = Column(Integer, default=100, nullable=False)
    budget_limit = Column(Float, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC), nullable=False)
    created_by = Column(String(36), ForeignKey("users.id"), nullable=False)

    # Relationships
    creator = relationship("User")
    scripts = relationship("CampaignScript", back_populates="campaign", cascade="all, delete-orphan")
    contact_lists = relationship("ContactList", back_populates="campaign", cascade="all, delete-orphan")
    call_flows = relationship("CallFlow", back_populates="campaign", cascade="all, delete-orphan")
    campaign_calls = relationship("CampaignCall", back_populates="campaign")

    def __repr__(self):
        return f"<Campaign(id={self.id}, name={self.name}, status={self.status})>"


class CampaignScript(Base):
    """Campaign script model for managing conversation flows."""

    __tablename__ = "campaign_scripts"

    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=False)

    # Script content
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    script_type = Column(String(50), default="conversation", nullable=False)  # conversation, voicemail, etc.

    # Script structure
    opening_script = Column(Text, nullable=True)
    main_script = Column(Text, nullable=True)
    closing_script = Column(Text, nullable=True)
    fallback_script = Column(Text, nullable=True)

    # AI configuration
    ai_instructions = Column(Text, nullable=True)
    personality_traits = Column(JSON, default=dict, nullable=False)
    response_guidelines = Column(JSON, default=dict, nullable=False)

    # Voice and audio settings
    voice_id = Column(String(100), nullable=True)
    voice_settings = Column(JSON, default=dict, nullable=False)
    language = Column(String(10), default="en", nullable=False)

    # Conditional logic
    conditions = Column(JSON, default=list, nullable=False)
    branches = Column(JSON, default=list, nullable=False)

    # Performance metrics
    usage_count = Column(Integer, default=0, nullable=False)
    success_rate = Column(Float, default=0.0, nullable=False)
    average_duration = Column(Float, nullable=True)

    # Status and versioning
    is_active = Column(Boolean, default=True, nullable=False)
    version = Column(Integer, default=1, nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC), nullable=False)

    # Relationships
    campaign = relationship("Campaign", back_populates="scripts")

    def __repr__(self):
        return f"<CampaignScript(id={self.id}, name={self.name}, campaign_id={self.campaign_id})>"


# Pydantic models for API
class CampaignBase(BaseModel):
    """Base campaign model."""
    name: str
    description: str | None = None
    campaign_type: CampaignType = CampaignType.OUTBOUND_SALES
    primary_provider: str
    backup_providers: list[str] = []
    routing_strategy: str = "round_robin"
    timezone: str = "UTC"
    business_hours_only: bool = True
    target_audience: dict[str, Any] | None = {}
    dialing_rules: dict[str, Any] | None = {}
    configuration: dict[str, Any] | None = {}
    max_concurrent_calls: int = 10
    calls_per_hour: int = 100
    budget_limit: float | None = None


class CampaignCreate(CampaignBase):
    """Campaign creation model."""
    start_time: datetime | None = None
    end_time: datetime | None = None
    created_by: int


class CampaignUpdate(BaseModel):
    """Campaign update model."""
    name: str | None = None
    description: str | None = None
    status: CampaignStatus | None = None
    campaign_type: CampaignType | None = None
    primary_provider: str | None = None
    backup_providers: list[str] | None = None
    routing_strategy: str | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None
    timezone: str | None = None
    business_hours_only: bool | None = None
    target_audience: dict[str, Any] | None = None
    dialing_rules: dict[str, Any] | None = None
    configuration: dict[str, Any] | None = None
    max_concurrent_calls: int | None = None
    calls_per_hour: int | None = None
    budget_limit: float | None = None


class CampaignResponse(CampaignBase):
    """Campaign response model."""
    id: int
    status: CampaignStatus
    total_calls: int
    connected_calls: int
    successful_calls: int
    conversion_rate: float
    created_at: datetime
    updated_at: datetime
    created_by: int
    start_time: datetime | None = None
    end_time: datetime | None = None

    class Config:
        from_attributes = True


class CampaignScriptBase(BaseModel):
    """Base campaign script model."""
    name: str
    description: str | None = None
    script_type: str = "conversation"
    opening_script: str | None = None
    main_script: str | None = None
    closing_script: str | None = None
    fallback_script: str | None = None
    ai_instructions: str | None = None
    personality_traits: dict[str, Any] | None = {}
    response_guidelines: dict[str, Any] | None = {}
    voice_id: str | None = None
    voice_settings: dict[str, Any] | None = {}
    language: str = "en"
    conditions: list[dict[str, Any]] | None = []
    branches: list[dict[str, Any]] | None = []
    is_active: bool = True


class CampaignScriptCreate(CampaignScriptBase):
    """Campaign script creation model."""
    campaign_id: int


class CampaignScriptUpdate(BaseModel):
    """Campaign script update model."""
    name: str | None = None
    description: str | None = None
    script_type: str | None = None
    opening_script: str | None = None
    main_script: str | None = None
    closing_script: str | None = None
    fallback_script: str | None = None
    ai_instructions: str | None = None
    personality_traits: dict[str, Any] | None = None
    response_guidelines: dict[str, Any] | None = None
    voice_id: str | None = None
    voice_settings: dict[str, Any] | None = None
    language: str | None = None
    conditions: list[dict[str, Any]] | None = None
    branches: list[dict[str, Any]] | None = None
    is_active: bool | None = None


class CampaignScriptResponse(CampaignScriptBase):
    """Campaign script response model."""
    id: int
    campaign_id: int
    usage_count: int
    success_rate: float
    average_duration: float | None = None
    version: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CampaignPerformance(BaseModel):
    """Campaign performance metrics model."""
    campaign_id: int
    campaign_name: str
    total_calls: int
    connected_calls: int
    successful_calls: int
    conversion_rate: float
    average_call_duration: float
    cost_per_call: float
    revenue_generated: float
    roi: float
    period_start: datetime
    period_end: datetime


class CampaignSummary(BaseModel):
    """Campaign summary model."""
    id: int
    name: str
    status: CampaignStatus
    campaign_type: CampaignType
    total_calls: int
    conversion_rate: float
    created_at: datetime
    last_activity: datetime | None = None
