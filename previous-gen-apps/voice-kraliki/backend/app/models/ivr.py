"""IVR (Interactive Voice Response) System Models.

Manages IVR flows, menus, and call routing through automated voice prompts.
"""

from datetime import UTC, datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel
from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.database import Base


class IVRNodeType(str, Enum):
    """Types of IVR nodes in a flow."""
    MENU = "menu"  # Play options and capture input
    PLAY_MESSAGE = "play_message"  # Play audio message
    GATHER_INPUT = "gather_input"  # Capture DTMF or speech
    TRANSFER = "transfer"  # Transfer to agent/queue
    VOICEMAIL = "voicemail"  # Send to voicemail
    WEBHOOK = "webhook"  # HTTP callback
    CONDITIONAL = "conditional"  # Conditional branching
    SET_VARIABLE = "set_variable"  # Set session variable
    END_CALL = "end_call"  # Terminate call


class InputType(str, Enum):
    """Types of input capture."""
    DTMF = "dtmf"  # Touch-tone digits
    SPEECH = "speech"  # Voice recognition
    BOTH = "both"  # Either DTMF or speech


class IVRFlow(Base):
    """IVR flow definition."""
    __tablename__ = "ivr_flows"

    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=True)
    team_id = Column(Integer, ForeignKey("teams.id", ondelete="CASCADE"), nullable=True)

    # Flow metadata
    name = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=True)
    version = Column(Integer, default=1, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    # Entry point
    entry_node_id = Column(String(100), nullable=False)  # ID of starting node

    # Flow definition
    # Structure: { node_id: { type, config, transitions } }
    nodes = Column(JSON, nullable=False, default=dict)

    # Variables and context
    default_language = Column(String(10), default="en", nullable=False)
    max_retries = Column(Integer, default=3, nullable=False)
    timeout_seconds = Column(Integer, default=10, nullable=False)
    inter_digit_timeout = Column(Integer, default=5, nullable=False)  # Seconds between digits

    # Audio settings
    default_voice = Column(String(50), nullable=True)  # TTS voice
    default_tts_provider = Column(String(50), nullable=True)  # e.g., "google", "aws"

    # Error handling
    invalid_input_message = Column(Text, nullable=True)
    timeout_message = Column(Text, nullable=True)
    error_node_id = Column(String(100), nullable=True)  # Fallback node

    # Analytics
    total_sessions = Column(Integer, default=0, nullable=False)
    completed_sessions = Column(Integer, default=0, nullable=False)
    abandoned_sessions = Column(Integer, default=0, nullable=False)
    average_duration_seconds = Column(Float, default=0.0, nullable=False)

    # Metadata
    custom_metadata = Column("metadata", JSON, default=dict, nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC), nullable=False)
    published_at = Column(DateTime, nullable=True)

    # Relationships
    sessions = relationship("IVRSession", back_populates="flow", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_ivr_flows_active_name", "is_active", "name"),
    )

    def __repr__(self):
        return f"<IVRFlow(id={self.id}, name={self.name}, version={self.version})>"


class IVRSession(Base):
    """IVR session tracking for analytics."""
    __tablename__ = "ivr_sessions"

    id = Column(Integer, primary_key=True, index=True)
    flow_id = Column(Integer, ForeignKey("ivr_flows.id", ondelete="CASCADE"), nullable=False, index=True)
    call_sid = Column(String(100), nullable=False, unique=True, index=True)

    # Session info
    caller_phone = Column(String(50), nullable=True)
    language = Column(String(10), default="en", nullable=False)

    # Status
    status = Column(String(50), default="in_progress", nullable=False)  # in_progress, completed, abandoned
    current_node_id = Column(String(100), nullable=True)

    # Timing
    started_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False, index=True)
    ended_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Integer, nullable=True)

    # Session data
    variables = Column(JSON, default=dict, nullable=False)  # Session variables
    node_history = Column(JSON, default=list, nullable=False)  # Path taken through flow
    input_history = Column(JSON, default=list, nullable=False)  # User inputs

    # Outcome
    exit_node_id = Column(String(100), nullable=True)
    exit_reason = Column(String(100), nullable=True)  # completed, timeout, error, transfer
    transferred_to = Column(String(100), nullable=True)  # Agent/queue ID if transferred

    # Metadata
    custom_metadata = Column("metadata", JSON, default=dict, nullable=False)

    # Relationships
    flow = relationship("IVRFlow", back_populates="sessions")

    __table_args__ = (
        Index("ix_ivr_sessions_flow_started", "flow_id", "started_at"),
    )

    def __repr__(self):
        return f"<IVRSession(id={self.id}, call_sid={self.call_sid}, status={self.status})>"


class IVRAnalytics(Base):
    """Aggregated IVR analytics."""
    __tablename__ = "ivr_analytics"

    id = Column(Integer, primary_key=True, index=True)
    flow_id = Column(Integer, ForeignKey("ivr_flows.id", ondelete="CASCADE"), nullable=False, index=True)
    node_id = Column(String(100), nullable=False, index=True)

    # Time period
    period_start = Column(DateTime, nullable=False, index=True)
    period_end = Column(DateTime, nullable=False)

    # Node metrics
    total_visits = Column(Integer, default=0, nullable=False)
    unique_sessions = Column(Integer, default=0, nullable=False)

    # Input metrics (for menu/gather nodes)
    total_inputs = Column(Integer, default=0, nullable=False)
    valid_inputs = Column(Integer, default=0, nullable=False)
    invalid_inputs = Column(Integer, default=0, nullable=False)
    timeout_count = Column(Integer, default=0, nullable=False)

    # Transitions (where users went from this node)
    # Structure: { next_node_id: count }
    transition_counts = Column(JSON, default=dict, nullable=False)

    # Average time spent
    average_duration_seconds = Column(Float, default=0.0, nullable=False)

    # Abandonment
    abandoned_from_node = Column(Integer, default=0, nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)

    __table_args__ = (
        Index("ix_ivr_analytics_flow_node_period", "flow_id", "node_id", "period_start"),
    )

    def __repr__(self):
        return f"<IVRAnalytics(flow_id={self.flow_id}, node_id={self.node_id}, visits={self.total_visits})>"


# ===== Pydantic Models =====

class IVRNodeConfig(BaseModel):
    """Configuration for a specific IVR node."""
    type: IVRNodeType
    label: str

    # Audio/message settings
    message: str | None = None
    audio_url: str | None = None
    use_tts: bool = True

    # Input settings (for menu/gather nodes)
    input_type: InputType | None = None
    num_digits: int | None = None
    finish_on_key: str | None = "#"
    valid_inputs: list[str] | None = None

    # Menu options (for menu nodes)
    options: dict[str, str] | None = None  # { "1": "next_node_id", "2": "another_node_id" }

    # Transfer settings
    transfer_to: str | None = None  # Phone number or queue ID
    transfer_type: str | None = "warm"  # warm, cold, queue

    # Conditional settings
    condition: str | None = None  # Expression to evaluate
    true_node: str | None = None
    false_node: str | None = None

    # Variable settings
    variable_name: str | None = None
    variable_value: Any | None = None

    # Webhook settings
    webhook_url: str | None = None
    webhook_method: str | None = "POST"

    # Transitions
    next_node: str | None = None  # Default next node
    timeout_node: str | None = None
    error_node: str | None = None


class IVRFlowBase(BaseModel):
    """Base IVR flow model."""
    name: str
    description: str | None = None
    is_active: bool = True
    entry_node_id: str
    nodes: dict[str, IVRNodeConfig]
    default_language: str = "en"
    max_retries: int = 3
    timeout_seconds: int = 10
    inter_digit_timeout: int = 5
    invalid_input_message: str | None = None
    timeout_message: str | None = None
    error_node_id: str | None = None


class IVRFlowCreate(IVRFlowBase):
    """IVR flow creation model."""
    campaign_id: int | None = None
    team_id: int | None = None


class IVRFlowUpdate(BaseModel):
    """IVR flow update model."""
    name: str | None = None
    description: str | None = None
    is_active: bool | None = None
    entry_node_id: str | None = None
    nodes: dict[str, IVRNodeConfig] | None = None
    default_language: str | None = None
    max_retries: int | None = None
    timeout_seconds: int | None = None


class IVRFlowResponse(IVRFlowBase):
    """IVR flow response model."""
    id: int
    campaign_id: int | None = None
    team_id: int | None = None
    version: int
    total_sessions: int
    completed_sessions: int
    abandoned_sessions: int
    average_duration_seconds: float
    created_at: datetime
    updated_at: datetime
    published_at: datetime | None = None

    class Config:
        from_attributes = True


class IVRSessionCreate(BaseModel):
    """IVR session creation model."""
    flow_id: int
    call_sid: str
    caller_phone: str | None = None
    language: str = "en"


class IVRSessionUpdate(BaseModel):
    """IVR session update model."""
    current_node_id: str | None = None
    status: str | None = None
    variables: dict[str, Any] | None = None
    exit_reason: str | None = None
    transferred_to: str | None = None


class IVRSessionResponse(BaseModel):
    """IVR session response model."""
    id: int
    flow_id: int
    call_sid: str
    caller_phone: str | None = None
    language: str
    status: str
    current_node_id: str | None = None
    started_at: datetime
    ended_at: datetime | None = None
    duration_seconds: int | None = None
    variables: dict[str, Any]
    node_history: list[str]
    input_history: list[dict[str, Any]]
    exit_node_id: str | None = None
    exit_reason: str | None = None
    transferred_to: str | None = None

    class Config:
        from_attributes = True


class IVRAnalyticsResponse(BaseModel):
    """IVR analytics response model."""
    id: int
    flow_id: int
    node_id: str
    period_start: datetime
    period_end: datetime
    total_visits: int
    unique_sessions: int
    total_inputs: int
    valid_inputs: int
    invalid_inputs: int
    timeout_count: int
    transition_counts: dict[str, int]
    average_duration_seconds: float
    abandoned_from_node: int

    class Config:
        from_attributes = True
