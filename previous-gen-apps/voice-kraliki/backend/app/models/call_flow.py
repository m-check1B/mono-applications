"""Call flow and campaign call tracking models."""

from datetime import UTC, datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel
from sqlalchemy import JSON, Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class CallFlowNodeType(str, Enum):
    """Call flow node type enumeration."""

    START = "start"
    SPEAK = "speak"
    QUESTION = "question"
    MENU = "menu"
    CONDITIONAL = "conditional"
    TRANSFER = "transfer"
    VOICEMAIL = "voicemail"
    END = "end"


class CallFlow(Base):
    """Call flow model for campaign automation."""

    __tablename__ = "call_flows"

    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False)

    # Flow metadata
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    version = Column(Integer, default=1, nullable=False)

    # Flow definition (JSON structure for flexibility)
    # Example structure:
    # {
    #   "nodes": [
    #     {"id": "start", "type": "start", "next": "greeting"},
    #     {"id": "greeting", "type": "speak", "text": "Hello {first_name}", "next": "menu"},
    #     {"id": "menu", "type": "menu", "options": [...], "timeout": 10}
    #   ]
    # }
    flow_definition = Column(JSON, nullable=False)

    # Status
    is_active = Column(Boolean, default=True, nullable=False)

    # Performance tracking
    usage_count = Column(Integer, default=0, nullable=False)
    success_rate = Column(Float, default=0.0, nullable=False)
    average_duration = Column(Float, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    # Relationships
    campaign = relationship("Campaign", back_populates="call_flows")

    def __repr__(self):
        return f"<CallFlow(id={self.id}, name={self.name}, campaign_id={self.campaign_id})>"


class CampaignCallStatus(str, Enum):
    """Campaign call status enumeration."""

    SCHEDULED = "scheduled"
    QUEUED = "queued"
    CALLING = "calling"
    CONNECTED = "connected"
    NO_ANSWER = "no_answer"
    BUSY = "busy"
    FAILED = "failed"
    VOICEMAIL = "voicemail"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class CampaignCall(Base):
    """Campaign call tracking model."""

    __tablename__ = "campaign_calls"

    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=False)
    contact_id = Column(Integer, ForeignKey("contacts.id"), nullable=False)
    call_id = Column(
        String(255), ForeignKey("call_states.call_id"), nullable=True
    )  # Links to actual call

    # Call outcome
    status = Column(String(50), default=CampaignCallStatus.SCHEDULED, nullable=False)
    disposition = Column(String(100), nullable=True)  # interested, not_interested, callback, dnc

    # Timing
    scheduled_at = Column(DateTime, nullable=True)
    started_at = Column(DateTime, nullable=True)
    ended_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Integer, default=0, nullable=False)

    # Call metrics
    talk_time_seconds = Column(Integer, default=0, nullable=False)
    wait_time_seconds = Column(Integer, default=0, nullable=False)
    after_call_work_seconds = Column(Integer, default=0, nullable=False)

    # Call quality
    audio_quality_score = Column(Float, nullable=True)
    transcription_accuracy = Column(Float, nullable=True)

    # AI insights
    sentiment_score = Column(Float, nullable=True)
    intent_detected = Column(String(100), nullable=True)
    key_topics = Column(JSON, default=list, nullable=False)

    # Recording and transcription
    recording_url = Column(String(500), nullable=True)
    transcription = Column(Text, nullable=True)

    # Notes and follow-up
    agent_notes = Column(Text, nullable=True)
    system_notes = Column(Text, nullable=True)
    follow_up_required = Column(Boolean, default=False, nullable=False)
    follow_up_date = Column(DateTime, nullable=True)

    # Cost tracking
    cost = Column(Float, default=0.0, nullable=False)

    # Metadata
    custom_metadata = Column("metadata", JSON, default=dict, nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    # Relationships
    campaign = relationship("Campaign", back_populates="campaign_calls")
    contact = relationship("Contact", back_populates="campaign_calls")

    def __repr__(self):
        return f"<CampaignCall(id={self.id}, campaign_id={self.campaign_id}, status={self.status})>"


# Pydantic models for API
class CallFlowBase(BaseModel):
    """Base call flow model."""

    name: str
    description: str | None = None
    flow_definition: dict[str, Any]
    is_active: bool = True


class CallFlowCreate(CallFlowBase):
    """Call flow creation model."""

    campaign_id: int


class CallFlowUpdate(BaseModel):
    """Call flow update model."""

    name: str | None = None
    description: str | None = None
    flow_definition: dict[str, Any] | None = None
    is_active: bool | None = None


class CallFlowResponse(CallFlowBase):
    """Call flow response model."""

    id: int
    campaign_id: int
    version: int
    usage_count: int
    success_rate: float
    average_duration: float | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CampaignCallBase(BaseModel):
    """Base campaign call model."""

    scheduled_at: datetime | None = None
    disposition: str | None = None
    agent_notes: str | None = None
    follow_up_required: bool = False
    follow_up_date: datetime | None = None


class CampaignCallCreate(CampaignCallBase):
    """Campaign call creation model."""

    campaign_id: int
    contact_id: int


class CampaignCallUpdate(BaseModel):
    """Campaign call update model."""

    status: CampaignCallStatus | None = None
    disposition: str | None = None
    agent_notes: str | None = None
    system_notes: str | None = None
    follow_up_required: bool | None = None
    follow_up_date: datetime | None = None
    sentiment_score: float | None = None
    intent_detected: str | None = None


class CampaignCallResponse(CampaignCallBase):
    """Campaign call response model."""

    id: int
    campaign_id: int
    contact_id: int
    call_id: str | None = None
    status: CampaignCallStatus
    started_at: datetime | None = None
    ended_at: datetime | None = None
    duration_seconds: int
    talk_time_seconds: int
    wait_time_seconds: int
    sentiment_score: float | None = None
    intent_detected: str | None = None
    key_topics: list[str] | None = []
    recording_url: str | None = None
    cost: float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CampaignCallMetrics(BaseModel):
    """Campaign call metrics aggregation."""

    total_calls: int
    completed_calls: int
    failed_calls: int
    no_answer_calls: int
    voicemail_calls: int
    average_duration: float
    total_talk_time: float
    total_cost: float
    success_rate: float
    disposition_breakdown: dict[str, int]
