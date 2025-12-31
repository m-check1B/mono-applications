"""
Speak by Kraliki - Conversation Model
Individual voice/text conversations with employees
"""

import uuid
from datetime import datetime
from decimal import Decimal
from sqlalchemy import String, DateTime, Integer, Boolean, Text, Numeric, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base


class Conversation(Base):
    """Individual conversation with an employee."""

    __tablename__ = "vop_conversations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    survey_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("vop_surveys.id", ondelete="CASCADE"),
        nullable=False
    )
    employee_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("employees.id", ondelete="CASCADE"),
        nullable=False
    )

    # Status: pending, invited, in_progress, completed, skipped, expired
    status: Mapped[str] = mapped_column(String(20), default="pending")

    # Timeline
    invited_at: Mapped[datetime | None] = mapped_column(DateTime)
    started_at: Mapped[datetime | None] = mapped_column(DateTime)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime)

    # Duration
    duration_seconds: Mapped[int | None] = mapped_column(Integer)

    # Transcript (JSON array of turns)
    # [{"role": "ai"|"user", "content": "...", "timestamp": "..."}, ...]
    transcript: Mapped[dict | None] = mapped_column(JSON)

    # Trust Layer v2.0: Employee can review/redact transcript
    transcript_reviewed_by_employee: Mapped[bool] = mapped_column(Boolean, default=False)
    redacted_sections: Mapped[list | None] = mapped_column(JSON)  # indices of redacted turns

    # Audio (optional)
    audio_url: Mapped[str | None] = mapped_column(String(500))

    # Fallback to text mode (v2.0)
    fallback_to_text: Mapped[bool] = mapped_column(Boolean, default=False)
    fallback_reason: Mapped[str | None] = mapped_column(String(100))  # mic_denied, network, browser

    # Analysis results
    sentiment_score: Mapped[Decimal | None] = mapped_column(Numeric(3, 2))  # -1.00 to 1.00
    topics: Mapped[list | None] = mapped_column(JSON)  # ["workload", "management", ...]
    flags: Mapped[list | None] = mapped_column(JSON)  # ["flight_risk", "burnout", ...]
    summary: Mapped[str | None] = mapped_column(Text)

    # Anonymous ID for display (protects employee identity)
    anonymous_id: Mapped[str | None] = mapped_column(String(50))

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    company = relationship("Company", back_populates="conversations")
    survey = relationship("Survey", back_populates="conversations")
    employee = relationship("Employee", back_populates="conversations")
    alerts = relationship("Alert", back_populates="conversation")
