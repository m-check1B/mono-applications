"""
Speak by Kraliki - Department Model
Hierarchical department structure with optional parent
"""

import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base


class Department(Base):
    """Department model for organizational structure."""

    __tablename__ = "departments"

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
    name: Mapped[str] = mapped_column(String(100), nullable=False)

    # Hierarchical structure
    parent_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("departments.id", ondelete="SET NULL")
    )
    manager_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("employees.id", ondelete="SET NULL")
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    company = relationship("Company", back_populates="departments")
    parent = relationship("Department", remote_side=[id], backref="children")
    manager = relationship("Employee", foreign_keys=[manager_id])
    employees = relationship("Employee", back_populates="department", foreign_keys="Employee.department_id")
    alerts = relationship("Alert", back_populates="department")
