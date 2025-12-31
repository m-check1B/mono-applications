"""
Speak by Kraliki - Alert Model
Automated alerts for flight risk, burnout, toxic manager, etc.
"""

import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base


class Alert(Base):
    """Automated alert triggered by conversation analysis."""

    __tablename__ = "vop_alerts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False
    )
    conversation_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("vop_conversations.id", ondelete="SET NULL")
    )

    # Alert type: flight_risk, burnout, toxic_manager, team_conflict,
    #             low_engagement, sentiment_drop
    type: Mapped[str] = mapped_column(String(50), nullable=False)

    # Severity: low, medium, high
    severity: Mapped[str] = mapped_column(String(20), default="medium")

    # Department context (aggregated alerts)
    department_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("departments.id", ondelete="SET NULL")
    )

    # Description of the alert
    description: Mapped[str] = mapped_column(Text, nullable=False)

    # Trigger keywords/phrases (for transparency)
    trigger_keywords: Mapped[str | None] = mapped_column(Text)

    # Status
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    is_resolved: Mapped[bool] = mapped_column(Boolean, default=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    read_at: Mapped[datetime | None] = mapped_column(DateTime)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime)

    # Relationships
    company = relationship("Company", back_populates="alerts")
    conversation = relationship("Conversation", back_populates="alerts")
    department = relationship("Department", back_populates="alerts")
    action = relationship("Action", back_populates="created_from_alert", foreign_keys="Action.created_from_alert_id")
