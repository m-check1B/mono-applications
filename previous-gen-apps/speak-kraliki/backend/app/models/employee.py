"""
Speak by Kraliki - Employee Model
Employee data with VoP-specific fields
"""

import uuid
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import String, DateTime, Date, Boolean, Numeric, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base


class Employee(Base):
    """Employee model - targets of voice conversations."""

    __tablename__ = "employees"

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
    department_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("departments.id", ondelete="SET NULL")
    )
    manager_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("employees.id", ondelete="SET NULL")
    )

    # Personal info
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(50))

    # Employment
    hire_date: Mapped[date | None] = mapped_column(Date)
    job_title: Mapped[str | None] = mapped_column(String(200))

    # VoP-specific fields
    vop_opted_out: Mapped[bool] = mapped_column(Boolean, default=False)
    vop_last_survey: Mapped[datetime | None] = mapped_column(DateTime)
    vop_participation_rate: Mapped[Decimal | None] = mapped_column(Numeric(3, 2))  # 0.00 - 1.00

    # Magic link token for survey access
    magic_link_token: Mapped[str | None] = mapped_column(String(100), unique=True)
    magic_link_expires: Mapped[datetime | None] = mapped_column(DateTime)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    company = relationship("Company", back_populates="employees")
    department = relationship("Department", back_populates="employees", foreign_keys=[department_id])
    manager = relationship("Employee", remote_side=[id], backref="direct_reports", foreign_keys=[manager_id])
    conversations = relationship("Conversation", back_populates="employee")

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
