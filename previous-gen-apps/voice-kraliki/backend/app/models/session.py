"""Call session and related models."""

from datetime import UTC, datetime
from enum import Enum
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel
from sqlalchemy import JSON, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base

if TYPE_CHECKING:
    pass


class CallStatus(str, Enum):
    """Call status enumeration."""
    INITIATED = "initiated"
    RINGING = "ringing"
    CONNECTED = "connected"
    ACTIVE = "active"
    ON_HOLD = "on_hold"
    DISCONNECTED = "disconnected"
    FAILED = "failed"
    COMPLETED = "completed"


class CallDirection(str, Enum):
    """Call direction enumeration."""
    INBOUND = "inbound"
    OUTBOUND = "outbound"


class CallSession(Base):
    """Call session model for tracking voice interactions."""

    __tablename__ = "call_sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), unique=True, index=True, nullable=False)

    # User and provider information
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    provider_type = Column(String(50), nullable=False)  # openai, gemini, deepgram, etc.
    provider_session_id = Column(String(255), nullable=True)

    # Call details
    call_direction = Column(String(20), default=CallDirection.INBOUND, nullable=False)
    phone_number = Column(String(20), nullable=True)
    caller_id = Column(String(50), nullable=True)
    status = Column(String(20), default=CallStatus.INITIATED, nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
    started_at = Column(DateTime, nullable=True)
    connected_at = Column(DateTime, nullable=True)
    ended_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Integer, default=0, nullable=False)

    # Configuration and metadata
    configuration = Column(JSON, default=dict, nullable=False)
    session_custom_metadata = Column("metadata", JSON, default=dict, nullable=False)

    # Quality metrics
    audio_quality_score = Column(Float, nullable=True)
    latency_ms = Column(Float, nullable=True)
    packet_loss = Column(Float, nullable=True)

    # Relationships
    user = relationship("User", back_populates="sessions")
    messages = relationship("SessionMessage", back_populates="session", cascade="all, delete-orphan")
    analytics = relationship("SessionAnalytics", back_populates="session", cascade="all, delete-orphan")
    insights = relationship("ConversationInsights", back_populates="session", cascade="all, delete-orphan")
    transcripts = relationship("ConversationTranscript", back_populates="session", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<CallSession(id={self.id}, session_id={self.session_id}, status={self.status})>"


class MessageRole(str, Enum):
    """Message role enumeration."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    FUNCTION = "function"


class SessionMessage(Base):
    """Individual messages within a call session."""

    __tablename__ = "session_messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("call_sessions.id"), nullable=False)

    # Message content
    role = Column(String(20), nullable=False)
    content = Column(Text, nullable=True)
    audio_data = Column(Text, nullable=True)  # Base64 encoded audio
    transcription = Column(Text, nullable=True)

    # Timestamps and metadata
    created_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC), nullable=False)
    message_custom_metadata = Column("metadata", JSON, default=dict, nullable=False)
    # Processing information
    processing_time_ms = Column(Float, nullable=True)
    confidence_score = Column(Float, nullable=True)
    sentiment_score = Column(Float, nullable=True)
    intent = Column(String(100), nullable=True)

    # Relationships
    session = relationship("CallSession", back_populates="messages")

    def __repr__(self):
        return f"<SessionMessage(id={self.id}, role={self.role}, session_id={self.session_id})>"


class SessionAnalytics(Base):
    """Analytics data for call sessions."""

    __tablename__ = "session_analytics"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("call_sessions.id"), nullable=False)

    # Performance metrics
    total_messages = Column(Integer, default=0, nullable=False)
    user_messages = Column(Integer, default=0, nullable=False)
    assistant_messages = Column(Integer, default=0, nullable=False)
    system_messages = Column(Integer, default=0, nullable=False)

    # Audio metrics
    total_audio_duration_ms = Column(Float, default=0.0, nullable=False)
    user_speaking_time_ms = Column(Float, default=0.0, nullable=False)
    assistant_speaking_time_ms = Column(Float, default=0.0, nullable=False)
    silence_time_ms = Column(Float, default=0.0, nullable=False)

    # Quality metrics
    average_latency_ms = Column(Float, nullable=True)
    peak_latency_ms = Column(Float, nullable=True)
    audio_quality_score = Column(Float, nullable=True)
    connection_stability = Column(Float, nullable=True)

    # AI metrics
    function_calls_count = Column(Integer, default=0, nullable=False)
    successful_function_calls = Column(Integer, default=0, nullable=False)
    average_confidence_score = Column(Float, nullable=True)

    # Business metrics
    conversion_score = Column(Float, nullable=True)
    satisfaction_score = Column(Float, nullable=True)
    resolution_status = Column(String(50), nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC), nullable=False)

    # Relationships
    session = relationship("CallSession", back_populates="analytics")

    def __repr__(self):
        return f"<SessionAnalytics(id={self.id}, session_id={self.session_id})>"


# Pydantic models for API
class CallSessionBase(BaseModel):
    """Base call session model."""
    provider_type: str
    call_direction: CallDirection = CallDirection.INBOUND
    phone_number: str | None = None
    caller_id: str | None = None
    configuration: dict[str, Any] | None = {}


class CallSessionCreate(CallSessionBase):
    """Call session creation model."""
    user_id: int


class CallSessionUpdate(BaseModel):
    """Call session update model."""
    status: CallStatus | None = None
    provider_session_id: str | None = None
    session_metadata: dict[str, Any] | None = None
    audio_quality_score: float | None = None
    latency_ms: float | None = None
    packet_loss: float | None = None


class CallSessionResponse(CallSessionBase):
    """Call session response model."""
    id: int
    session_id: str
    user_id: int
    status: CallStatus
    created_at: datetime
    started_at: datetime | None = None
    connected_at: datetime | None = None
    ended_at: datetime | None = None
    duration_seconds: int
    session_metadata: dict[str, Any]

    class Config:
        from_attributes = True


class SessionMessageBase(BaseModel):
    """Base session message model."""
    role: MessageRole
    content: str | None = None
    audio_data: str | None = None
    transcription: str | None = None
    message_metadata: dict[str, Any] | None = {}


class SessionMessageCreate(SessionMessageBase):
    """Session message creation model."""
    session_id: int
    sequence_number: int


class SessionMessageResponse(SessionMessageBase):
    """Session message response model."""
    id: int
    session_id: int
    timestamp: datetime
    sequence_number: int
    processing_time_ms: float | None = None
    confidence_score: float | None = None
    sentiment_score: float | None = None
    intent: str | None = None

    class Config:
        from_attributes = True


class SessionAnalyticsBase(BaseModel):
    """Base session analytics model."""
    total_messages: int = 0
    user_messages: int = 0
    assistant_messages: int = 0
    system_messages: int = 0
    total_audio_duration_ms: float = 0.0
    user_speaking_time_ms: float = 0.0
    assistant_speaking_time_ms: float = 0.0
    silence_time_ms: float = 0.0


class SessionAnalyticsCreate(SessionAnalyticsBase):
    """Session analytics creation model."""
    session_id: int


class SessionAnalyticsResponse(SessionAnalyticsBase):
    """Session analytics response model."""
    id: int
    session_id: int
    average_latency_ms: float | None = None
    peak_latency_ms: float | None = None
    audio_quality_score: float | None = None
    connection_stability: float | None = None
    function_calls_count: int
    successful_function_calls: int
    average_confidence_score: float | None = None
    conversion_score: float | None = None
    satisfaction_score: float | None = None
    resolution_status: str | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
