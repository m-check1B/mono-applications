"""
Speak by Kraliki - User Model
Admin/HR users who access the dashboard
"""

import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base


class User(Base):
    """User model for dashboard access (HR, CEO, Managers)."""

    __tablename__ = "users"

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

    # Auth
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    # Profile
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)

    # Role: owner, hr_director, manager
    role: Mapped[str] = mapped_column(String(50), default="manager")

    # Department scope (for managers - they only see their department)
    department_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("departments.id", ondelete="SET NULL")
    )

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login: Mapped[datetime | None] = mapped_column(DateTime)

    # Relationships
    company = relationship("Company", back_populates="users")
    department = relationship("Department")
    assigned_actions = relationship("Action", back_populates="assigned_to_user")

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def can_view_all_departments(self) -> bool:
        """Check if user can see all departments (owner/HR) or just their own."""
        return self.role in ("owner", "hr_director")
