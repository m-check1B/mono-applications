"""Contact list and contact models for campaign management."""

from datetime import UTC, datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, EmailStr, validator
from sqlalchemy import JSON, Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class ContactStatus(str, Enum):
    """Contact status enumeration."""
    PENDING = "pending"
    CALLING = "calling"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    DO_NOT_CALL = "do_not_call"


class ContactList(Base):
    """Contact list model for organizing campaign contacts."""

    __tablename__ = "contact_lists"

    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)

    # Import tracking
    import_file_name = Column(String(255), nullable=True)
    import_status = Column(String(50), default="pending", nullable=False)  # pending, processing, completed, failed
    import_errors = Column(JSON, default=list, nullable=False)

    # Contact statistics
    total_contacts = Column(Integer, default=0, nullable=False)
    processed_contacts = Column(Integer, default=0, nullable=False)
    successful_contacts = Column(Integer, default=0, nullable=False)
    failed_contacts = Column(Integer, default=0, nullable=False)

    # Metadata
    tags = Column(JSON, default=list, nullable=False)
    custom_metadata = Column("metadata", JSON, default=dict, nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC), nullable=False)

    # Relationships
    campaign = relationship("Campaign", back_populates="contact_lists")
    contacts = relationship("Contact", back_populates="contact_list", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<ContactList(id={self.id}, name={self.name}, campaign_id={self.campaign_id})>"


class Contact(Base):
    """Contact model for individual contacts in campaign."""

    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)
    contact_list_id = Column(Integer, ForeignKey("contact_lists.id", ondelete="CASCADE"), nullable=False)

    # Contact information
    phone_number = Column(String(20), nullable=False, index=True)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    email = Column(String(255), nullable=True)
    company = Column(String(200), nullable=True)

    # Custom fields (flexible schema)
    custom_fields = Column(JSON, default=dict, nullable=False)

    # Status tracking
    status = Column(String(50), default=ContactStatus.PENDING, nullable=False)
    last_attempt_at = Column(DateTime, nullable=True)
    attempts = Column(Integer, default=0, nullable=False)
    max_attempts = Column(Integer, default=3, nullable=False)

    # Call disposition
    disposition = Column(String(100), nullable=True)  # interested, not_interested, callback, dnc
    notes = Column(Text, nullable=True)

    # Scheduling
    preferred_call_time = Column(DateTime, nullable=True)
    timezone = Column(String(50), default="UTC", nullable=False)
    do_not_call_before = Column(DateTime, nullable=True)
    do_not_call_after = Column(DateTime, nullable=True)

    # Opt-out and compliance
    opted_out = Column(Boolean, default=False, nullable=False)
    opted_out_at = Column(DateTime, nullable=True)
    compliance_flags = Column(JSON, default=dict, nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC), nullable=False)

    # Relationships
    contact_list = relationship("ContactList", back_populates="contacts")
    campaign_calls = relationship("CampaignCall", back_populates="contact")

    def __repr__(self):
        return f"<Contact(id={self.id}, phone={self.phone_number}, status={self.status})>"


# Pydantic models for API
class ContactListBase(BaseModel):
    """Base contact list model."""
    name: str
    description: str | None = None
    tags: list[str] | None = []
    metadata: dict[str, Any] | None = {}


class ContactListCreate(ContactListBase):
    """Contact list creation model."""
    campaign_id: int


class ContactListUpdate(BaseModel):
    """Contact list update model."""
    name: str | None = None
    description: str | None = None
    tags: list[str] | None = None
    metadata: dict[str, Any] | None = None


class ContactListResponse(ContactListBase):
    """Contact list response model."""
    id: int
    campaign_id: int
    import_file_name: str | None = None
    import_status: str
    total_contacts: int
    processed_contacts: int
    successful_contacts: int
    failed_contacts: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ContactBase(BaseModel):
    """Base contact model."""
    phone_number: str
    first_name: str | None = None
    last_name: str | None = None
    email: EmailStr | None = None
    company: str | None = None
    custom_fields: dict[str, Any] | None = {}
    preferred_call_time: datetime | None = None
    timezone: str = "UTC"
    max_attempts: int = 3

    @validator('phone_number')
    def validate_phone_number(cls, v):
        """Validate phone number format."""
        # Remove common formatting characters
        cleaned = ''.join(c for c in v if c.isdigit() or c == '+')
        if len(cleaned) < 10:
            raise ValueError('Phone number must be at least 10 digits')
        return cleaned


class ContactCreate(ContactBase):
    """Contact creation model."""
    contact_list_id: int


class ContactUpdate(BaseModel):
    """Contact update model."""
    phone_number: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    email: EmailStr | None = None
    company: str | None = None
    custom_fields: dict[str, Any] | None = None
    status: ContactStatus | None = None
    disposition: str | None = None
    notes: str | None = None
    preferred_call_time: datetime | None = None
    timezone: str | None = None
    max_attempts: int | None = None
    opted_out: bool | None = None


class ContactResponse(ContactBase):
    """Contact response model."""
    id: int
    contact_list_id: int
    status: ContactStatus
    last_attempt_at: datetime | None = None
    attempts: int
    disposition: str | None = None
    notes: str | None = None
    opted_out: bool
    opted_out_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ContactBulkCreate(BaseModel):
    """Bulk contact creation model."""
    contact_list_id: int
    contacts: list[ContactBase]


class ContactImportResult(BaseModel):
    """Contact import result model."""
    total: int
    successful: int
    failed: int
    errors: list[dict[str, Any]] = []
