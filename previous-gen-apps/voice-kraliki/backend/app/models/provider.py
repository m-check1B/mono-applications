"""Provider configuration and health models."""

from datetime import UTC, datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel
from sqlalchemy import JSON, Boolean, Column, DateTime, Float, Integer, String, Text

from app.database import Base


class ProviderType(str, Enum):
    """Provider type enumeration."""
    OPENAI_REALTIME = "openai_realtime"
    GEMINI_NATIVE_AUDIO = "gemini_native_audio"
    DEEPGRAM_NOVA3 = "deepgram_nova3"
    DEEPGRAM_SEGMENTED = "deepgram_segmented"
    TWILIO_MEDIA_STREAM = "twilio_media_stream"
    TELNYX_CALL_CONTROL = "telnyx_call_control"


class ProviderStatus(str, Enum):
    """Provider status enumeration."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    DEGRADED = "degraded"
    ERROR = "error"
    MAINTENANCE = "maintenance"


class ProviderConfig(Base):
    """Provider configuration model."""

    __tablename__ = "provider_configs"

    id = Column(Integer, primary_key=True, index=True)
    provider_type = Column(String(50), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)

    # Status and availability
    status = Column(String(20), default=ProviderStatus.ACTIVE, nullable=False)
    is_enabled = Column(Boolean, default=True, nullable=False)
    priority = Column(Integer, default=1, nullable=False)  # Lower number = higher priority

    # Configuration
    api_key = Column(String(500), nullable=True)  # Encrypted
    api_endpoint = Column(String(500), nullable=True)
    configuration = Column(JSON, default=dict, nullable=False)

    # Capabilities
    supported_languages = Column(JSON, default=list, nullable=False)
    supported_voices = Column(JSON, default=list, nullable=False)
    supported_formats = Column(JSON, default=list, nullable=False)
    max_concurrent_sessions = Column(Integer, default=10, nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC), nullable=False)
    last_tested = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<ProviderConfig(id={self.id}, provider_type={self.provider_type}, status={self.status})>"


class ProviderHealth(Base):
    """Provider health monitoring model."""

    __tablename__ = "provider_health"

    id = Column(Integer, primary_key=True, index=True)
    provider_type = Column(String(50), nullable=False)

    # Health status
    status = Column(String(20), default=ProviderStatus.ACTIVE, nullable=False)
    is_healthy = Column(Boolean, default=True, nullable=False)
    last_check = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)

    # Performance metrics
    response_time_ms = Column(Float, nullable=True)
    success_rate = Column(Float, default=100.0, nullable=False)
    error_rate = Column(Float, default=0.0, nullable=False)

    # Availability metrics
    uptime_percentage = Column(Float, default=100.0, nullable=False)
    consecutive_failures = Column(Integer, default=0, nullable=False)
    total_requests = Column(Integer, default=0, nullable=False)
    successful_requests = Column(Integer, default=0, nullable=False)
    failed_requests = Column(Integer, default=0, nullable=False)

    # Quality metrics
    audio_quality_score = Column(Float, nullable=True)
    latency_p50_ms = Column(Float, nullable=True)
    latency_p95_ms = Column(Float, nullable=True)
    latency_p99_ms = Column(Float, nullable=True)

    # Additional metadata
    health_check_config = Column(JSON, default=dict, nullable=False)
    provider_custom_metadata = Column("metadata", JSON, default=dict, nullable=False)
    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC), nullable=False)

    def __repr__(self):
        return f"<ProviderHealth(id={self.id}, provider_type={self.provider_type}, status={self.status})>"


# Pydantic models for API
class ProviderConfigBase(BaseModel):
    """Base provider configuration model."""
    provider_type: ProviderType
    name: str
    description: str | None = None
    is_enabled: bool = True
    priority: int = 1
    configuration: dict[str, Any] | None = {}
    supported_languages: list[str] = []
    supported_voices: list[str] = []
    supported_formats: list[str] = []
    max_concurrent_sessions: int = 10


class ProviderConfigCreate(ProviderConfigBase):
    """Provider configuration creation model."""
    api_key: str | None = None
    api_endpoint: str | None = None


class ProviderConfigUpdate(BaseModel):
    """Provider configuration update model."""
    name: str | None = None
    description: str | None = None
    status: ProviderStatus | None = None
    is_enabled: bool | None = None
    priority: int | None = None
    api_key: str | None = None
    api_endpoint: str | None = None
    configuration: dict[str, Any] | None = None
    supported_languages: list[str] | None = None
    supported_voices: list[str] | None = None
    supported_formats: list[str] | None = None
    max_concurrent_sessions: int | None = None


class ProviderConfigResponse(ProviderConfigBase):
    """Provider configuration response model."""
    id: int
    status: ProviderStatus
    created_at: datetime
    updated_at: datetime
    last_tested: datetime | None = None

    class Config:
        from_attributes = True


class ProviderHealthBase(BaseModel):
    """Base provider health model."""
    provider_type: ProviderType
    status: ProviderStatus = ProviderStatus.ACTIVE
    is_healthy: bool = True
    response_time_ms: float | None = None
    success_rate: float = 100.0
    error_rate: float = 0.0
    uptime_percentage: float = 100.0
    consecutive_failures: int = 0
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    audio_quality_score: float | None = None
    latency_p50_ms: float | None = None
    latency_p95_ms: float | None = None
    latency_p99_ms: float | None = None


class ProviderHealthCreate(ProviderHealthBase):
    """Provider health creation model."""
    pass


class ProviderHealthUpdate(BaseModel):
    """Provider health update model."""
    status: ProviderStatus | None = None
    is_healthy: bool | None = None
    response_time_ms: float | None = None
    success_rate: float | None = None
    error_rate: float | None = None
    uptime_percentage: float | None = None
    consecutive_failures: int | None = None
    total_requests: int | None = None
    successful_requests: int | None = None
    failed_requests: int | None = None
    audio_quality_score: float | None = None
    latency_p50_ms: float | None = None
    latency_p95_ms: float | None = None
    latency_p99_ms: float | None = None
    error_details: list[dict[str, Any]] | None = None
    warnings: list[str] | None = None
    provider_metadata: dict[str, Any] | None = None


class ProviderHealthResponse(ProviderHealthBase):
    """Provider health response model."""
    id: int
    last_check: datetime
    created_at: datetime
    updated_at: datetime
    error_details: list[dict[str, Any]]
    warnings: list[str]
    provider_metadata: dict[str, Any]

    class Config:
        from_attributes = True


class ProviderStatusSummary(BaseModel):
    """Provider status summary model."""
    provider_type: ProviderType
    name: str
    status: ProviderStatus
    is_healthy: bool
    is_enabled: bool
    response_time_ms: float | None = None
    success_rate: float
    uptime_percentage: float
    consecutive_failures: int
    last_check: datetime


class ProviderComparison(BaseModel):
    """Provider comparison model."""
    providers: list[ProviderStatusSummary]
    recommendation: str | None = None
    comparison_metrics: dict[str, dict[str, float]]
