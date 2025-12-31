"""
Abstract base class for telephony providers.
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any

from pydantic import BaseModel


class CallStatus(str, Enum):
    QUEUED = "queued"
    RINGING = "ringing"
    IN_PROGRESS = "in-progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BUSY = "busy"
    NO_ANSWER = "no-answer"
    CANCELED = "canceled"


class CallDirection(str, Enum):
    INBOUND = "inbound"
    OUTBOUND = "outbound"


class CallRecord(BaseModel):
    id: str
    from_number: str
    to_number: str
    status: CallStatus
    direction: CallDirection
    provider: str
    script_id: int | None = None
    company_id: int
    duration: int | None = None  # in seconds
    recording_url: str | None = None
    transcription: str | None = None
    cost: float | None = None
    created_at: str
    answered_at: str | None = None
    ended_at: str | None = None
    metadata: dict[str, Any] = {}


class CallRequest(BaseModel):
    to: str
    from_: str
    script_id: int | None = None
    company_id: int
    provider: str | None = None
    metadata: dict[str, Any] = {}


class CallResponse(BaseModel):
    success: bool
    call_id: str | None = None
    status: CallStatus | None = None
    error: str | None = None
    provider: str
    metadata: dict[str, Any] = {}


class TelephonyProvider(ABC):
    """Abstract base class for telephony providers."""

    def __init__(self, config: dict[str, Any]):
        self.config = config
        self.provider_name = self.__class__.__name__.replace('Service', '').lower()

    @abstractmethod
    async def make_call(self, request: CallRequest) -> CallResponse:
        """Initiate an outbound call."""
        pass

    @abstractmethod
    async def get_call_status(self, call_id: str) -> CallRecord:
        """Get the current status of a call."""
        pass

    @abstractmethod
    async def end_call(self, call_id: str) -> bool:
        """End an active call."""
        pass

    @abstractmethod
    async def get_call_recording(self, call_id: str) -> str | None:
        """Get the recording URL for a call."""
        pass

    @abstractmethod
    async def get_call_transcription(self, call_id: str) -> str | None:
        """Get the transcription for a call."""
        pass

    @abstractmethod
    async def get_available_numbers(self, country_code: str = "US") -> list[str]:
        """Get available phone numbers for provisioning."""
        pass

    @abstractmethod
    async def purchase_number(self, phone_number: str) -> bool:
        """Purchase a phone number."""
        pass

    @abstractmethod
    async def release_number(self, phone_number: str) -> bool:
        """Release a phone number."""
        pass

    @abstractmethod
    async def get_call_cost(self, call_id: str) -> float | None:
        """Get the cost of a call."""
        pass

    @abstractmethod
    async def validate_phone_number(self, phone_number: str) -> dict[str, Any]:
        """Validate a phone number."""
        pass

    async def health_check(self) -> dict[str, Any]:
        """Check the health of the provider connection."""
        try:
            # Basic health check - try to validate a number
            result = await self.validate_phone_number("+1234567890")
            return {
                "provider": self.provider_name,
                "status": "healthy" if result.get("valid") else "degraded",
                "timestamp": "2025-10-11T10:30:00Z",
                "details": result
            }
        except Exception as e:
            return {
                "provider": self.provider_name,
                "status": "unhealthy",
                "timestamp": "2025-10-11T10:30:00Z",
                "error": str(e)
            }

    def get_provider_config(self) -> dict[str, Any]:
        """Get the provider configuration."""
        return self.config

    def supports_feature(self, feature: str) -> bool:
        """Check if the provider supports a specific feature."""
        supported_features = self.get_supported_features()
        return feature in supported_features

    def get_supported_features(self) -> list[str]:
        """Get the list of supported features."""
        return [
            "outbound_calls",
            "inbound_calls",
            "call_recording",
            "call_transcription",
            "number_provisioning",
            "call_validation",
            "cost_tracking"
        ]
