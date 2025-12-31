"""Base types and protocols for telephony adapters.

This module defines the abstract interface that all telephony adapters
must implement to work with the unified telephony interface.
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Protocol

from pydantic import BaseModel, Field


class AudioFormat(str, Enum):
    """Supported audio formats."""

    PCM16 = "pcm16"  # 16-bit PCM (linear)
    ULAW = "ulaw"  # u-law encoding (8-bit, Twilio default)
    ALAW = "alaw"  # A-law encoding (8-bit)


class AudioChunk(BaseModel):
    """Audio data chunk."""

    data: bytes = Field(description="Raw audio bytes")
    format: AudioFormat = Field(description="Audio format")
    sample_rate: int = Field(description="Sample rate in Hz")
    timestamp: float | None = Field(default=None, description="Timestamp in seconds")


class CallDirection(str, Enum):
    """Call direction."""

    INBOUND = "inbound"
    OUTBOUND = "outbound"


class CallState(str, Enum):
    """Call lifecycle states."""

    INITIATED = "initiated"
    RINGING = "ringing"
    ANSWERED = "answered"
    ACTIVE = "active"
    ENDED = "ended"
    FAILED = "failed"


class CallInfo(BaseModel):
    """Information about a call."""

    call_id: str = Field(description="Provider-specific call ID")
    from_number: str = Field(description="Caller phone number")
    to_number: str = Field(description="Callee phone number")
    direction: CallDirection = Field(description="Call direction")
    state: CallState = Field(description="Current call state")
    metadata: dict[str, Any] = Field(default_factory=dict)


class TelephonyCapabilities(BaseModel):
    """Telephony adapter capabilities."""

    supports_inbound: bool = Field(description="Supports inbound calls")
    supports_outbound: bool = Field(description="Supports outbound calls")
    supports_streaming: bool = Field(description="Supports WebSocket audio streaming")
    supports_sms: bool = Field(description="Supports SMS")
    audio_formats: list[AudioFormat] = Field(description="Supported audio formats")
    native_sample_rate: int = Field(description="Native audio sample rate")


class TelephonyAdapter(Protocol):
    """Protocol for telephony service adapters (Telnyx, Twilio).

    These adapters handle the conversion between telephony protocols
    and a unified audio interface.
    """

    @property
    def capabilities(self) -> TelephonyCapabilities:
        """Adapter capabilities."""
        ...

    @abstractmethod
    async def setup_call(self, call_params: dict[str, Any]) -> CallInfo:
        """Set up a new outbound call."""
        ...

    @abstractmethod
    async def answer_call(self, call_id: str, stream_url: str) -> dict[str, Any]:
        """Answer an inbound call and start streaming."""
        ...

    @abstractmethod
    async def end_call(self, call_id: str) -> None:
        """End an active call."""
        ...

    @abstractmethod
    async def handle_webhook(
        self, event_type: str, payload: dict[str, Any]
    ) -> dict[str, Any] | None:
        """Handle incoming webhook from telephony service."""
        ...

    @abstractmethod
    async def validate_webhook(
        self, signature: str, payload: bytes | str
    ) -> bool:
        """Validate webhook signature."""
        ...

    @abstractmethod
    def generate_stream_response(self, stream_url: str) -> str:
        """Generate TwiML/TeXML response for streaming."""
        ...

    @abstractmethod
    async def convert_audio_from_telephony(self, audio_data: bytes) -> AudioChunk:
        """Convert telephony audio format to PCM16."""
        ...

    @abstractmethod
    async def convert_audio_to_telephony(self, audio: AudioChunk) -> bytes:
        """Convert PCM16 audio to telephony format."""
        ...


class BaseTelephonyAdapter(ABC):
    """Base class providing common functionality for telephony adapters."""

    def __init__(self, api_key: str):
        """Initialize adapter with API key."""
        self._api_key = api_key

    @property
    @abstractmethod
    def capabilities(self) -> TelephonyCapabilities:
        """Adapter capabilities (must be implemented by subclasses)."""
        ...

    def _validate_audio_format(self, format: AudioFormat) -> None:
        """Validate that audio format is supported."""
        if format not in self.capabilities.audio_formats:
            raise ValueError(
                f"Audio format {format} not supported. "
                f"Supported: {self.capabilities.audio_formats}"
            )
