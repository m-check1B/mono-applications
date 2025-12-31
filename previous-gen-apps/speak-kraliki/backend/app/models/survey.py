"""
Speak by Kraliki - Survey Model
Survey campaigns with questions and scheduling
"""

import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base


class Survey(Base):
    """Survey/campaign model for employee feedback rounds."""

    __tablename__ = "vop_surveys"

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

    # Survey info
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)

    # Status: draft, scheduled, active, paused, completed
    status: Mapped[str] = mapped_column(String(20), default="draft")

    # Frequency: once, weekly, monthly, quarterly
    frequency: Mapped[str] = mapped_column(String(20), default="monthly")

    # Questions configuration (JSON array)
    # [{"id": 1, "question": "...", "follow_up_count": 1}, ...]
    questions: Mapped[dict] = mapped_column(JSON, default=list)

    # Custom AI prompts (optional)
    custom_system_prompt: Mapped[str | None] = mapped_column(Text)

    # Scheduling
    starts_at: Mapped[datetime | None] = mapped_column(DateTime)
    ends_at: Mapped[datetime | None] = mapped_column(DateTime)

    # Targeting
    target_departments: Mapped[list | None] = mapped_column(JSON)  # null = all
    target_employee_ids: Mapped[list | None] = mapped_column(JSON)  # null = all

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    company = relationship("Company", back_populates="surveys")
    conversations = relationship("Conversation", back_populates="survey", cascade="all, delete-orphan")

    @property
    def is_active(self) -> bool:
        now = datetime.utcnow()
        if self.status != "active":
            return False
        if self.starts_at and now < self.starts_at:
            return False
        if self.ends_at and now > self.ends_at:
            return False
        return True
