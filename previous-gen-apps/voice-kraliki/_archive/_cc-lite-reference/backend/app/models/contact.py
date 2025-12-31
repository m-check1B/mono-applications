"""Contact models - SQLAlchemy 2.0"""

from datetime import datetime
from typing import Optional
import enum
from sqlalchemy import String, DateTime, JSON, Integer, ForeignKey, Enum as SQLEnum, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class ContactStatus(str, enum.Enum):
    """Contact statuses"""
    PENDING = "PENDING"
    DIALING = "DIALING"
    CONNECTED = "CONNECTED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    DO_NOT_CALL = "DO_NOT_CALL"


class Contact(Base):
    """Contact model for campaign outreach"""

    __tablename__ = "contacts"

    id: Mapped[str] = mapped_column(String(30), primary_key=True)
    campaign_id: Mapped[str] = mapped_column(String(30), ForeignKey("campaigns.id", ondelete="CASCADE"))
    phone_number: Mapped[str] = mapped_column(String(20))
    name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    status: Mapped[ContactStatus] = mapped_column(SQLEnum(ContactStatus), default=ContactStatus.PENDING)
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    last_attempt: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    next_attempt: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    outcome: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(String(2000), nullable=True)
    extra_metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    # campaign: Mapped["Campaign"] = relationship(back_populates="contacts")
    # calls: Mapped[list["Call"]] = relationship(back_populates="contact")

    # Indexes for performance
    __table_args__ = (
        Index('idx_contacts_campaign_status', 'campaign_id', 'status'),
        Index('idx_contacts_campaign_phone', 'campaign_id', 'phone_number'),
        Index('idx_contacts_phone', 'phone_number'),
    )

    def __repr__(self) -> str:
        return f"<Contact {self.phone_number} ({self.status})>"
