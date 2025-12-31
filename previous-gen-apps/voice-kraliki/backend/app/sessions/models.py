"""Session data models and types.

Defines the session entity and its states.
"""

from datetime import UTC, datetime
from enum import Enum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class SessionStatus(str, Enum):
    """Session lifecycle status."""

    PENDING = "pending"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ERROR = "error"
    TERMINATED = "terminated"


class Session(BaseModel):
    """Session entity representing an active conversation session."""

    id: UUID = Field(default_factory=uuid4, description="Unique session ID")
    provider_type: str = Field(description="Provider type (openai, gemini, etc.)")
    provider_model: str = Field(description="Specific model being used")
    strategy: str = Field(
        default="realtime", description="Execution strategy (realtime, segmented)"
    )
    telephony_provider: str | None = Field(
        default=None, description="Telephony provider (twilio, telnyx, etc.)"
    )
    status: SessionStatus = Field(default=SessionStatus.PENDING)

    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    started_at: datetime | None = None
    ended_at: datetime | None = None

    metadata: dict[str, Any] = Field(default_factory=dict)

    # Telephony integration
    call_sid: str | None = Field(default=None, description="Twilio/Telnyx call SID")
    caller_number: str | None = None
    callee_number: str | None = None

    # Session configuration
    system_prompt: str | None = None
    temperature: float = 0.7

    # Analytics
    audio_chunks_sent: int = 0
    audio_chunks_received: int = 0
    text_messages_sent: int = 0
    text_messages_received: int = 0
    function_calls: int = 0

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "provider_type": "openai",
                "provider_model": "gpt-4o-mini-realtime-preview",
                "strategy": "realtime",
                "telephony_provider": "telnyx",
                "status": "active",
                "metadata": {"user_id": "user123"},
            }
        }
    }


class SessionCreateRequest(BaseModel):
    """Request to create a new session."""

    provider_type: str | None = Field(
        default=None, description="Provider type (openai, gemini, deepgram)"
    )
    provider: str | None = Field(
        default=None, description="Alias for provider_type (frontend compatibility)"
    )
    provider_model: str | None = Field(
        default=None, description="Specific model (uses default if not specified)"
    )
    strategy: str | None = Field(
        default=None, description="Execution strategy (realtime or segmented)"
    )
    telephony_provider: str | None = Field(
        default=None, description="Requested telephony provider (twilio, telnyx)"
    )
    use_premium_model: bool | None = Field(
        default=None,
        description="Hints to select premium/high quality model when available",
    )
    system_prompt: str | None = Field(
        default=None, description="System instructions for the AI"
    )
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    phone_number: str | None = Field(
        default=None, description="Target phone number for PSTN flows"
    )
    campaign: str | None = Field(default=None, description="Campaign identifier")
    persona: str | None = Field(default=None, description="Agent persona or script")
    metadata: dict[str, Any] = Field(default_factory=dict)

    def resolved_provider_type(self) -> str:
        """Resolve provider type from request aliases."""

        raw = self.provider_type or self.provider
        if not raw:
            raise ValueError("provider_type is required")
        return raw.lower()

    def resolved_telephony(self) -> str | None:
        """Resolve telephony provider if supplied."""

        if not self.telephony_provider:
            return None
        return self.telephony_provider.lower()

    def wants_premium(self) -> bool:
        """Determine if premium model is requested."""

        if self.use_premium_model is None:
            return False
        return bool(self.use_premium_model)


class SessionResponse(BaseModel):
    """Session response DTO."""

    id: UUID
    provider_type: str
    provider_model: str
    strategy: str
    telephony_provider: str | None
    status: SessionStatus
    created_at: datetime
    updated_at: datetime | None = None
    ended_at: datetime | None = None
    metadata: dict[str, Any]
