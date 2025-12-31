"""
Speak by Kraliki - Company Model
Multi-tenant structure: each company sees only its own data
"""

import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base


class Company(Base):
    """Company/tenant model for multi-tenancy."""

    __tablename__ = "companies"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

    # Subscription
    plan: Mapped[str] = mapped_column(String(50), default="free")  # free, personal, premium, pro
    stripe_customer_id: Mapped[str | None] = mapped_column(String(100))
    stripe_subscription_id: Mapped[str | None] = mapped_column(String(100))

    # Settings
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    settings: Mapped[str | None] = mapped_column(Text)  # JSON settings

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    departments = relationship("Department", back_populates="company", cascade="all, delete-orphan")
    employees = relationship("Employee", back_populates="company", cascade="all, delete-orphan")
    users = relationship("User", back_populates="company", cascade="all, delete-orphan")
    surveys = relationship("Survey", back_populates="company", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="company", cascade="all, delete-orphan")
    actions = relationship("Action", back_populates="company", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="company", cascade="all, delete-orphan")
