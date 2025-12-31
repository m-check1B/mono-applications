"""Voicemail System Models.

Manages voicemail messages, mailboxes, greetings, and notifications.
"""

from datetime import UTC, datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel
from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.database import Base


class VoicemailStatus(str, Enum):
    """Voicemail message status."""

    NEW = "new"  # Unheard
    HEARD = "heard"  # Played at least once
    SAVED = "saved"  # Explicitly saved
    ARCHIVED = "archived"  # Moved to archive
    DELETED = "deleted"  # Soft deleted


class GreetingType(str, Enum):
    """Voicemail greeting types."""

    STANDARD = "standard"  # Default greeting
    UNAVAILABLE = "unavailable"  # Out of office
    BUSY = "busy"  # On another call
    TEMPORARY = "temporary"  # Temporary greeting
    HOLIDAY = "holiday"  # Holiday greeting


class NotificationChannel(str, Enum):
    """Notification delivery channels."""

    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    WEBHOOK = "webhook"


class Voicemail(Base):
    """Voicemail message."""

    __tablename__ = "voicemails"

    id = Column(Integer, primary_key=True, index=True)

    # Mailbox owner
    agent_id = Column(
        Integer, ForeignKey("agent_profiles.id", ondelete="CASCADE"), nullable=False, index=True
    )
    team_id = Column(Integer, ForeignKey("teams.id", ondelete="SET NULL"), nullable=True)

    # Caller information
    caller_phone = Column(String(50), nullable=False, index=True)
    caller_name = Column(String(200), nullable=True)
    call_sid = Column(String(100), nullable=True, unique=True)

    # Message details
    status = Column(String(50), default=VoicemailStatus.NEW.value, nullable=False, index=True)
    priority = Column(Integer, default=0, nullable=False)  # 0=normal, 1=urgent

    # Recording
    recording_url = Column(String(1000), nullable=False)
    recording_duration_seconds = Column(Integer, nullable=False)
    recording_format = Column(String(20), default="mp3", nullable=False)
    recording_size_bytes = Column(Integer, nullable=True)

    # Storage
    storage_provider = Column(String(50), nullable=True)
    storage_key = Column(String(500), nullable=True)

    # Transcription
    has_transcription = Column(Boolean, default=False, nullable=False)
    transcription_text = Column(Text, nullable=True)
    transcription_confidence = Column(Float, nullable=True)

    # Activity tracking
    play_count = Column(Integer, default=0, nullable=False)
    first_heard_at = Column(DateTime, nullable=True)
    last_heard_at = Column(DateTime, nullable=True)

    # Callback tracking
    callback_requested = Column(Boolean, default=False, nullable=False)
    callback_completed = Column(Boolean, default=False, nullable=False)
    callback_at = Column(DateTime, nullable=True)

    # Retention
    retention_days = Column(Integer, default=30, nullable=False)
    expires_at = Column(DateTime, nullable=False, index=True)
    auto_delete = Column(Boolean, default=True, nullable=False)

    # Metadata
    custom_metadata = Column("metadata", JSON, default=dict, nullable=False)
    tags = Column(JSON, default=list, nullable=False)

    # Timestamps
    created_at = Column(
        DateTime, default=lambda: datetime.now(UTC), nullable=False, index=True
    )
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )
    archived_at = Column(DateTime, nullable=True)
    deleted_at = Column(DateTime, nullable=True)

    # Relationships - link through agent_id (both tables reference agent_profiles)
    # This is a many-to-one relationship (many voicemails belong to one mailbox)
    mailbox = relationship(
        "VoicemailBox",
        back_populates="messages",
        primaryjoin="Voicemail.agent_id == VoicemailBox.agent_id",
        foreign_keys=[agent_id],
        uselist=False,
        viewonly=True,
    )

    __table_args__ = (
        Index("ix_voicemails_agent_status", "agent_id", "status"),
        Index("ix_voicemails_agent_created", "agent_id", "created_at"),
    )

    def __repr__(self):
        return f"<Voicemail(id={self.id}, agent_id={self.agent_id}, status={self.status})>"


class VoicemailBox(Base):
    """Voicemail box configuration for an agent."""

    __tablename__ = "voicemail_boxes"

    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(
        Integer,
        ForeignKey("agent_profiles.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    team_id = Column(Integer, ForeignKey("teams.id", ondelete="SET NULL"), nullable=True)

    # Configuration
    is_enabled = Column(Boolean, default=True, nullable=False)
    max_message_duration = Column(Integer, default=180, nullable=False)  # 3 minutes
    max_messages = Column(Integer, default=100, nullable=False)

    # Greetings
    current_greeting_id = Column(
        Integer, ForeignKey("voicemail_greetings.id", ondelete="SET NULL"), nullable=True
    )
    greeting_type = Column(String(50), default=GreetingType.STANDARD.value, nullable=False)

    # PIN protection
    pin_enabled = Column(Boolean, default=False, nullable=False)
    pin_hash = Column(String(128), nullable=True)

    # Notifications
    notification_enabled = Column(Boolean, default=True, nullable=False)
    notification_channels = Column(JSON, default=list, nullable=False)  # ["email", "sms"]
    notification_email = Column(String(255), nullable=True)
    notification_phone = Column(String(50), nullable=True)

    # Email-to-voicemail
    email_attachments = Column(Boolean, default=True, nullable=False)
    email_transcription = Column(Boolean, default=True, nullable=False)

    # Auto-response
    auto_reply_enabled = Column(Boolean, default=False, nullable=False)
    auto_reply_message = Column(Text, nullable=True)

    # Statistics
    total_messages = Column(Integer, default=0, nullable=False)
    unheard_messages = Column(Integer, default=0, nullable=False)
    storage_used_bytes = Column(Integer, default=0, nullable=False)

    # Settings
    settings = Column(JSON, default=dict, nullable=False)

    # Metadata
    custom_metadata = Column("metadata", JSON, default=dict, nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )
    last_checked_at = Column(DateTime, nullable=True)

    # Relationships - link through agent_id (both tables reference agent_profiles)
    # This is a one-to-many relationship (one mailbox has many voicemails)
    messages = relationship(
        "Voicemail",
        back_populates="mailbox",
        primaryjoin="VoicemailBox.agent_id == Voicemail.agent_id",
        foreign_keys="[Voicemail.agent_id]",
        uselist=True,
        viewonly=True,
    )
    greetings = relationship(
        "VoicemailGreeting",
        back_populates="mailbox",
        cascade="all, delete-orphan",
        foreign_keys="[VoicemailGreeting.mailbox_id]",
    )

    def __repr__(self):
        return f"<VoicemailBox(id={self.id}, agent_id={self.agent_id}, unheard={self.unheard_messages})>"


class VoicemailGreeting(Base):
    """Voicemail greeting audio."""

    __tablename__ = "voicemail_greetings"

    id = Column(Integer, primary_key=True, index=True)
    mailbox_id = Column(
        Integer, ForeignKey("voicemail_boxes.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Greeting details
    name = Column(String(200), nullable=False)
    greeting_type = Column(String(50), nullable=False)
    is_active = Column(Boolean, default=False, nullable=False)

    # Audio
    audio_url = Column(String(1000), nullable=False)
    audio_format = Column(String(20), default="mp3", nullable=False)
    audio_duration_seconds = Column(Integer, nullable=False)
    audio_size_bytes = Column(Integer, nullable=True)

    # Storage
    storage_provider = Column(String(50), nullable=True)
    storage_key = Column(String(500), nullable=True)

    # TTS option
    is_tts = Column(Boolean, default=False, nullable=False)
    tts_text = Column(Text, nullable=True)
    tts_voice = Column(String(50), nullable=True)

    # Schedule (for temporary/holiday greetings)
    active_from = Column(DateTime, nullable=True)
    active_until = Column(DateTime, nullable=True)

    # Metadata
    custom_metadata = Column("metadata", JSON, default=dict, nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )
    last_used_at = Column(DateTime, nullable=True)

    # Relationships - specify foreign_keys to disambiguate from current_greeting_id
    mailbox = relationship(
        "VoicemailBox",
        back_populates="greetings",
        foreign_keys=[mailbox_id],
    )

    def __repr__(self):
        return f"<VoicemailGreeting(id={self.id}, mailbox_id={self.mailbox_id}, type={self.greeting_type})>"


class VoicemailNotification(Base):
    """Voicemail notification log."""

    __tablename__ = "voicemail_notifications"

    id = Column(Integer, primary_key=True, index=True)
    voicemail_id = Column(
        Integer, ForeignKey("voicemails.id", ondelete="CASCADE"), nullable=False, index=True
    )
    agent_id = Column(Integer, ForeignKey("agent_profiles.id", ondelete="CASCADE"), nullable=False)

    # Notification details
    channel = Column(String(50), nullable=False)  # email, sms, push
    recipient = Column(String(255), nullable=False)

    # Status
    status = Column(String(50), nullable=False)  # sent, failed, pending
    sent_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)

    # Error handling
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0, nullable=False)

    # Metadata
    custom_metadata = Column("metadata", JSON, default=dict, nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)

    __table_args__ = (Index("ix_notifications_voicemail_channel", "voicemail_id", "channel"),)

    def __repr__(self):
        return f"<VoicemailNotification(id={self.id}, voicemail_id={self.voicemail_id}, channel={self.channel})>"


# ===== Pydantic Models =====


class VoicemailBase(BaseModel):
    """Base voicemail model."""

    agent_id: int
    caller_phone: str
    caller_name: str | None = None
    recording_url: str
    recording_duration_seconds: int
    recording_format: str = "mp3"
    priority: int = 0
    retention_days: int = 30


class VoicemailCreate(VoicemailBase):
    """Voicemail creation model."""

    call_sid: str | None = None
    team_id: int | None = None
    storage_provider: str | None = None
    storage_key: str | None = None


class VoicemailUpdate(BaseModel):
    """Voicemail update model."""

    status: VoicemailStatus | None = None
    transcription_text: str | None = None
    transcription_confidence: float | None = None
    callback_completed: bool | None = None
    tags: list[str] | None = None


class VoicemailResponse(VoicemailBase):
    """Voicemail response model."""

    id: int
    team_id: int | None = None
    call_sid: str | None = None
    status: VoicemailStatus
    recording_size_bytes: int | None = None
    has_transcription: bool
    transcription_text: str | None = None
    transcription_confidence: float | None = None
    play_count: int
    first_heard_at: datetime | None = None
    last_heard_at: datetime | None = None
    callback_requested: bool
    callback_completed: bool
    callback_at: datetime | None = None
    expires_at: datetime
    tags: list[str]
    created_at: datetime
    updated_at: datetime
    archived_at: datetime | None = None
    deleted_at: datetime | None = None

    class Config:
        from_attributes = True


class VoicemailBoxBase(BaseModel):
    """Base voicemail box model."""

    is_enabled: bool = True
    max_message_duration: int = 180
    max_messages: int = 100
    greeting_type: GreetingType = GreetingType.STANDARD
    notification_enabled: bool = True
    notification_channels: list[NotificationChannel] = []
    notification_email: str | None = None
    notification_phone: str | None = None
    email_attachments: bool = True
    email_transcription: bool = True


class VoicemailBoxCreate(VoicemailBoxBase):
    """Voicemail box creation model."""

    agent_id: int
    team_id: int | None = None


class VoicemailBoxUpdate(BaseModel):
    """Voicemail box update model."""

    is_enabled: bool | None = None
    max_message_duration: int | None = None
    max_messages: int | None = None
    greeting_type: GreetingType | None = None
    notification_enabled: bool | None = None
    notification_channels: list[NotificationChannel] | None = None
    notification_email: str | None = None
    notification_phone: str | None = None
    settings: dict[str, Any] | None = None


class VoicemailBoxResponse(VoicemailBoxBase):
    """Voicemail box response model."""

    id: int
    agent_id: int
    team_id: int | None = None
    current_greeting_id: int | None = None
    pin_enabled: bool
    auto_reply_enabled: bool
    total_messages: int
    unheard_messages: int
    storage_used_bytes: int
    settings: dict[str, Any]
    created_at: datetime
    updated_at: datetime
    last_checked_at: datetime | None = None

    class Config:
        from_attributes = True


class GreetingBase(BaseModel):
    """Base greeting model."""

    name: str
    greeting_type: GreetingType
    audio_url: str
    audio_duration_seconds: int
    audio_format: str = "mp3"
    is_tts: bool = False
    tts_text: str | None = None
    tts_voice: str | None = None
    active_from: datetime | None = None
    active_until: datetime | None = None


class GreetingCreate(GreetingBase):
    """Greeting creation model."""

    mailbox_id: int


class GreetingResponse(GreetingBase):
    """Greeting response model."""

    id: int
    mailbox_id: int
    is_active: bool
    audio_size_bytes: int | None = None
    storage_provider: str | None = None
    storage_key: str | None = None
    created_at: datetime
    updated_at: datetime
    last_used_at: datetime | None = None

    class Config:
        from_attributes = True


class VoicemailMarkRequest(BaseModel):
    """Request to mark voicemail status."""

    status: VoicemailStatus
    voicemail_ids: list[int]


class VoicemailStatsResponse(BaseModel):
    """Voicemail statistics response."""

    agent_id: int
    total_messages: int
    new_messages: int
    heard_messages: int
    saved_messages: int
    archived_messages: int
    total_duration_seconds: int
    average_duration_seconds: float
    oldest_message_date: datetime | None = None
    newest_message_date: datetime | None = None
