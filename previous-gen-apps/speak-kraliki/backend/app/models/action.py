"""
Speak by Kraliki - Action Model
Action Loop v2.0: CEO marks issues as heard/in progress/resolved
"""

import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base


class Action(Base):
    """Action item created from alerts - shows leadership is listening."""

    __tablename__ = "vop_actions"

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

    # Department scope (for RBAC - managers only see their department)
    department_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("departments.id", ondelete="SET NULL")
    )

    # Topic/issue description
    topic: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)

    # Status: new, heard, in_progress, resolved
    status: Mapped[str] = mapped_column(String(20), default="new")

    # Created from alert (optional link)
    created_from_alert_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("vop_alerts.id", ondelete="SET NULL")
    )

    # Assignment
    assigned_to: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL")
    )

    # Notes for internal tracking
    notes: Mapped[str | None] = mapped_column(Text)

    # Public message shown to employees (Action Loop widget)
    public_message: Mapped[str | None] = mapped_column(Text)

    # Visibility: Should employees see this in the Action Feed?
    visible_to_employees: Mapped[bool] = mapped_column(Boolean, default=True)

    # Priority: low, medium, high
    priority: Mapped[str] = mapped_column(String(20), default="medium")

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime)

    # Relationships
    company = relationship("Company", back_populates="actions")
    department = relationship("Department")
    created_from_alert = relationship("Alert", back_populates="action", foreign_keys=[created_from_alert_id])
    assigned_to_user = relationship("User", back_populates="assigned_actions")
