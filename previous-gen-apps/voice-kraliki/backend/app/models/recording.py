"""Call Recording Management Models.

Manages call recordings, storage, transcription, and retention policies.
"""

from datetime import UTC, datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field
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


class RecordingStatus(str, Enum):
    """Recording status."""
    PENDING = "pending"  # Recording initiated
    RECORDING = "recording"  # Currently recording
    PROCESSING = "processing"  # Post-processing
    COMPLETED = "completed"  # Ready for playback
    FAILED = "failed"  # Recording failed
    DELETED = "deleted"  # Marked for deletion


class StorageProvider(str, Enum):
    """Storage provider types."""
    LOCAL = "local"  # Local filesystem
    S3 = "s3"  # AWS S3
    AZURE = "azure"  # Azure Blob Storage
    GCS = "gcs"  # Google Cloud Storage
    MINIO = "minio"  # MinIO (S3-compatible)


class TranscriptionStatus(str, Enum):
    """Transcription status."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Recording(Base):
    """Call recording metadata and storage information."""
    __tablename__ = "recordings"

    id = Column(Integer, primary_key=True, index=True)
    call_sid = Column(String(100), nullable=False, unique=True, index=True)

    # Associated entities
    agent_id = Column(Integer, ForeignKey("agent_profiles.id", ondelete="SET NULL"), nullable=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id", ondelete="SET NULL"), nullable=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id", ondelete="SET NULL"), nullable=True)

    # Recording details
    status = Column(String(50), default=RecordingStatus.PENDING.value, nullable=False, index=True)

    # Call information
    caller_phone = Column(String(50), nullable=True)
    direction = Column(String(20), nullable=True)  # inbound/outbound

    # Timing
    started_at = Column(DateTime, nullable=False, default=lambda: datetime.now(UTC), index=True)
    ended_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Integer, nullable=True)

    # Storage
    storage_provider = Column(String(50), default=StorageProvider.LOCAL.value, nullable=False)
    storage_bucket = Column(String(200), nullable=True)
    storage_key = Column(String(500), nullable=False)  # File path or S3 key
    storage_region = Column(String(50), nullable=True)

    # File details
    file_format = Column(String(20), default="mp3", nullable=False)
    file_size_bytes = Column(Integer, nullable=True)
    checksum_md5 = Column(String(32), nullable=True)

    # Security
    is_encrypted = Column(Boolean, default=False, nullable=False)
    encryption_key_id = Column(String(100), nullable=True)

    # Access control
    is_public = Column(Boolean, default=False, nullable=False)
    download_url = Column(String(1000), nullable=True)  # Signed URL
    download_url_expires_at = Column(DateTime, nullable=True)

    # Quality metrics
    audio_quality_score = Column(Float, nullable=True)  # 0-100
    silence_percentage = Column(Float, nullable=True)

    # Retention policy
    retention_days = Column(Integer, default=90, nullable=False)
    expires_at = Column(DateTime, nullable=True, index=True)
    auto_delete = Column(Boolean, default=True, nullable=False)

    # Compliance
    redacted = Column(Boolean, default=False, nullable=False)
    redaction_reason = Column(String(500), nullable=True)

    # Metadata
    custom_metadata = Column("metadata", JSON, default=dict, nullable=False)
    tags = Column(JSON, default=list, nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC), nullable=False)
    deleted_at = Column(DateTime, nullable=True)

    # Relationships
    transcripts = relationship("RecordingTranscript", back_populates="recording", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_recordings_agent_created", "agent_id", "created_at"),
        Index("ix_recordings_campaign_created", "campaign_id", "created_at"),
        Index("ix_recordings_expires", "expires_at", "auto_delete"),
    )

    def __repr__(self):
        return f"<Recording(id={self.id}, call_sid={self.call_sid}, status={self.status})>"


class RecordingTranscript(Base):
    """Transcription of call recording."""
    __tablename__ = "recording_transcripts"

    id = Column(Integer, primary_key=True, index=True)
    recording_id = Column(Integer, ForeignKey("recordings.id", ondelete="CASCADE"), nullable=False, index=True)

    # Transcription details
    status = Column(String(50), default=TranscriptionStatus.PENDING.value, nullable=False, index=True)
    provider = Column(String(50), nullable=True)  # Google, AWS, Azure, etc.

    # Content
    text = Column(Text, nullable=True)
    language = Column(String(10), default="en", nullable=False)
    confidence_score = Column(Float, nullable=True)  # 0-1

    # Structured transcript (with timestamps)
    # Format: [{"speaker": "agent", "text": "...", "start": 0.0, "end": 2.5}]
    segments = Column(JSON, default=list, nullable=False)

    # Speaker identification
    num_speakers = Column(Integer, nullable=True)
    speaker_labels = Column(JSON, default=list, nullable=False)  # ["agent", "customer"]

    # Processing
    processing_time_seconds = Column(Float, nullable=True)
    word_count = Column(Integer, nullable=True)

    # Search optimization
    searchable_text = Column(Text, nullable=True)  # Normalized for search

    # Metadata
    custom_metadata = Column("metadata", JSON, default=dict, nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    recording = relationship("Recording", back_populates="transcripts")

    __table_args__ = (
        Index("ix_transcripts_recording_status", "recording_id", "status"),
    )

    def __repr__(self):
        return f"<RecordingTranscript(id={self.id}, recording_id={self.recording_id}, status={self.status})>"


class RecordingStorage(Base):
    """Storage provider configuration."""
    __tablename__ = "recording_storage"

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id", ondelete="CASCADE"), nullable=True)

    # Provider details
    provider = Column(String(50), nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_default = Column(Boolean, default=False, nullable=False)

    # Configuration (encrypted in production)
    config = Column(JSON, nullable=False)  # Provider-specific config

    # Example configs:
    # S3: {"bucket": "recordings", "region": "us-east-1", "access_key_id": "...", "secret_key": "..."}
    # Azure: {"container": "recordings", "account_name": "...", "account_key": "..."}
    # MinIO: {"endpoint": "minio:9000", "bucket": "recordings", "access_key": "...", "secret_key": "..."}

    # Capacity
    total_storage_bytes = Column(Integer, default=0, nullable=False)
    used_storage_bytes = Column(Integer, default=0, nullable=False)
    max_storage_bytes = Column(Integer, nullable=True)  # Quota limit

    # Encryption
    encryption_enabled = Column(Boolean, default=True, nullable=False)
    encryption_type = Column(String(50), nullable=True)  # AES-256, AWS-KMS, etc.

    # Retention
    default_retention_days = Column(Integer, default=90, nullable=False)

    # Metadata
    custom_metadata = Column("metadata", JSON, default=dict, nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC), nullable=False)
    last_sync_at = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<RecordingStorage(id={self.id}, provider={self.provider}, name={self.name})>"


# ===== Pydantic Models =====

class RecordingBase(BaseModel):
    """Base recording model."""
    call_sid: str
    agent_id: int | None = None
    team_id: int | None = None
    campaign_id: int | None = None
    caller_phone: str | None = None
    direction: str | None = None
    storage_provider: StorageProvider = StorageProvider.LOCAL
    storage_bucket: str | None = None
    storage_key: str
    file_format: str = "mp3"
    is_encrypted: bool = False
    retention_days: int = 90
    auto_delete: bool = True


class RecordingCreate(RecordingBase):
    """Recording creation model."""
    started_at: datetime | None = None


class RecordingUpdate(BaseModel):
    """Recording update model."""
    status: RecordingStatus | None = None
    ended_at: datetime | None = None
    duration_seconds: int | None = None
    file_size_bytes: int | None = None
    checksum_md5: str | None = None
    audio_quality_score: float | None = None
    tags: list[str] | None = None


class RecordingResponse(RecordingBase):
    """Recording response model."""
    id: int
    status: RecordingStatus
    started_at: datetime
    ended_at: datetime | None = None
    duration_seconds: int | None = None
    file_size_bytes: int | None = None
    storage_region: str | None = None
    is_encrypted: bool
    is_public: bool
    download_url: str | None = None
    download_url_expires_at: datetime | None = None
    audio_quality_score: float | None = None
    expires_at: datetime | None = None
    redacted: bool
    tags: list[str]
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None

    class Config:
        from_attributes = True


class TranscriptCreate(BaseModel):
    """Transcript creation model."""
    recording_id: int
    provider: str | None = None
    language: str = "en"


class TranscriptUpdate(BaseModel):
    """Transcript update model."""
    status: TranscriptionStatus | None = None
    text: str | None = None
    confidence_score: float | None = None
    segments: list[dict[str, Any]] | None = None
    num_speakers: int | None = None
    speaker_labels: list[str] | None = None
    word_count: int | None = None


class TranscriptResponse(BaseModel):
    """Transcript response model."""
    id: int
    recording_id: int
    status: TranscriptionStatus
    provider: str | None = None
    text: str | None = None
    language: str
    confidence_score: float | None = None
    segments: list[dict[str, Any]]
    num_speakers: int | None = None
    speaker_labels: list[str]
    word_count: int | None = None
    created_at: datetime
    completed_at: datetime | None = None

    class Config:
        from_attributes = True


class StorageConfigBase(BaseModel):
    """Base storage configuration model."""
    provider: StorageProvider
    name: str
    description: str | None = None
    is_active: bool = True
    is_default: bool = False
    config: dict[str, Any]
    encryption_enabled: bool = True
    default_retention_days: int = 90


class StorageConfigCreate(StorageConfigBase):
    """Storage configuration creation model."""
    team_id: int | None = None


class StorageConfigResponse(StorageConfigBase):
    """Storage configuration response model."""
    id: int
    team_id: int | None = None
    total_storage_bytes: int
    used_storage_bytes: int
    max_storage_bytes: int | None = None
    created_at: datetime
    updated_at: datetime
    last_sync_at: datetime | None = None

    class Config:
        from_attributes = True


class DownloadUrlRequest(BaseModel):
    """Request for signed download URL."""
    recording_id: int
    expires_in_seconds: int = Field(default=3600, ge=60, le=86400)  # 1 hour default, max 24 hours


class DownloadUrlResponse(BaseModel):
    """Response with signed download URL."""
    recording_id: int
    download_url: str
    expires_at: datetime
    file_format: str
    file_size_bytes: int | None = None
