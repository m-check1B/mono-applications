"""Call and telephony models - SQLAlchemy 2.0"""

from datetime import datetime
from typing import Optional
import enum
from sqlalchemy import String, DateTime, JSON, Integer, ForeignKey, Enum as SQLEnum, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class TelephonyProvider(str, enum.Enum):
    """Telephony providers"""
    TWILIO = "TWILIO"
    TELNYX = "TELNYX"


class CallStatus(str, enum.Enum):
    """Call status"""
    QUEUED = "QUEUED"
    RINGING = "RINGING"
    IN_PROGRESS = "IN_PROGRESS"
    ON_HOLD = "ON_HOLD"
    COMPLETED = "COMPLETED"
    NO_ANSWER = "NO_ANSWER"
    BUSY = "BUSY"
    FAILED = "FAILED"
    CANCELED = "CANCELED"


class CallDirection(str, enum.Enum):
    """Call direction"""
    INBOUND = "INBOUND"
    OUTBOUND = "OUTBOUND"


class Call(Base):
    """Call model"""

    __tablename__ = "calls"

    id: Mapped[str] = mapped_column(String(30), primary_key=True)
    twilio_call_sid: Mapped[Optional[str]] = mapped_column(String(100), unique=True, nullable=True)
    from_number: Mapped[str] = mapped_column(String(20))
    to_number: Mapped[str] = mapped_column(String(20))
    status: Mapped[CallStatus] = mapped_column(SQLEnum(CallStatus), default=CallStatus.QUEUED)
    direction: Mapped[CallDirection] = mapped_column(SQLEnum(CallDirection))
    provider: Mapped[TelephonyProvider] = mapped_column(SQLEnum(TelephonyProvider), default=TelephonyProvider.TWILIO)

    # Foreign keys
    organization_id: Mapped[str] = mapped_column(String(30), ForeignKey("organizations.id", ondelete="CASCADE"))
    agent_id: Mapped[Optional[str]] = mapped_column(String(30), ForeignKey("users.id"), nullable=True)
    supervisor_id: Mapped[Optional[str]] = mapped_column(String(30), ForeignKey("users.id"), nullable=True)
    campaign_id: Mapped[Optional[str]] = mapped_column(String(30), ForeignKey("campaigns.id"), nullable=True)
    contact_id: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)  # ForeignKey added later

    # Call details
    start_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    end_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    duration: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # seconds
    recording_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    disposition: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # call outcome
    notes: Mapped[Optional[str]] = mapped_column(String(2000), nullable=True)
    extra_metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    sentiment_analyses: Mapped[list["SentimentAnalysis"]] = relationship(
        back_populates="call",
        cascade="all, delete-orphan"
    )
    # organization: Mapped["Organization"] = relationship(back_populates="calls")
    # agent: Mapped[Optional["User"]] = relationship(foreign_keys=[agent_id], back_populates="agent_calls")
    # supervisor: Mapped[Optional["User"]] = relationship(foreign_keys=[supervisor_id], back_populates="supervisor_calls")
    # campaign: Mapped[Optional["Campaign"]] = relationship(back_populates="calls")

    # Indexes for performance
    __table_args__ = (
        Index('idx_calls_org_status', 'organization_id', 'status'),
        Index('idx_calls_org_agent', 'organization_id', 'agent_id'),
        Index('idx_calls_org_start', 'organization_id', 'start_time'),
        Index('idx_calls_agent_start', 'agent_id', 'start_time'),
        Index('idx_calls_status_start', 'status', 'start_time'),
    )

    def __repr__(self) -> str:
        return f"<Call {self.id} {self.from_number} -> {self.to_number} ({self.status})>"


class TranscriptRole(str, enum.Enum):
    """Transcript roles"""
    USER = "USER"
    ASSISTANT = "ASSISTANT"
    SYSTEM = "SYSTEM"


class CallTranscript(Base):
    """Call transcript model"""

    __tablename__ = "call_transcripts"

    id: Mapped[str] = mapped_column(String(30), primary_key=True)
    call_id: Mapped[str] = mapped_column(String(30), ForeignKey("calls.id", ondelete="CASCADE"))
    role: Mapped[TranscriptRole] = mapped_column(SQLEnum(TranscriptRole))
    content: Mapped[str] = mapped_column(String(10000))
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    confidence: Mapped[Optional[float]] = mapped_column(nullable=True)  # Transcription confidence
    speaker_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    extra_metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Relationships
    # call: Mapped["Call"] = relationship(back_populates="transcripts")

    def __repr__(self) -> str:
        return f"<CallTranscript {self.call_id} {self.role}>"
