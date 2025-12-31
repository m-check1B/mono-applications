"""Base provider protocols and types for AI voice provider abstraction.

This module defines the abstract base classes and protocols that all
voice providers must implement to work with the unified provider interface.
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, AsyncGenerator, Protocol

from pydantic import BaseModel, Field


class AudioFormat(str, Enum):
    """Supported audio formats."""

    PCM16 = "pcm16"  # 16-bit PCM
    ULAW = "ulaw"  # u-law encoding (8-bit)
    OPUS = "opus"  # Opus codec
    MP3 = "mp3"  # MP3 codec


class SessionState(str, Enum):
    """Session lifecycle states."""

    IDLE = "idle"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ACTIVE = "active"
    DISCONNECTING = "disconnecting"
    DISCONNECTED = "disconnected"
    ERROR = "error"


class ProviderCapabilities(BaseModel):
    """Provider capability descriptor."""

    supports_realtime: bool = Field(
        description="Supports real-time end-to-end processing"
    )
    supports_text: bool = Field(description="Supports text input/output")
    supports_audio: bool = Field(description="Supports audio input/output")
    supports_multimodal: bool = Field(description="Supports multimodal inputs")
    supports_function_calling: bool = Field(description="Supports function/tool calling")
    supports_streaming: bool = Field(description="Supports streaming responses")
    audio_formats: list[AudioFormat] = Field(
        default_factory=list, description="Supported audio formats"
    )
    max_session_duration: int | None = Field(
        default=None, description="Max session duration in seconds"
    )
    cost_tier: str = Field(default="standard", description="Cost tier (standard/premium)")


class SessionConfig(BaseModel):
    """Configuration for a provider session."""

    model_id: str = Field(description="Model identifier")
    audio_format: AudioFormat = Field(default=AudioFormat.PCM16)
    sample_rate: int = Field(default=16000, description="Audio sample rate in Hz")
    channels: int = Field(default=1, description="Number of audio channels")
    system_prompt: str | None = Field(default=None, description="System instructions")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int | None = Field(default=None, description="Max response tokens")
    tools: list[dict[str, Any]] | None = Field(
        default=None, description="Available tools/functions"
    )
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class AudioChunk(BaseModel):
    """Audio data chunk."""

    data: bytes = Field(description="Raw audio bytes")
    format: AudioFormat = Field(description="Audio format")
    sample_rate: int = Field(description="Sample rate in Hz")
    timestamp: float | None = Field(default=None, description="Timestamp in seconds")


class TextMessage(BaseModel):
    """Text message."""

    role: str = Field(description="Message role (user/assistant/system)")
    content: str = Field(description="Message content")
    timestamp: float | None = Field(default=None)


class FunctionCall(BaseModel):
    """Function/tool call request."""

    id: str = Field(description="Call ID")
    name: str = Field(description="Function name")
    arguments: dict[str, Any] = Field(description="Function arguments")


class ProviderEvent(BaseModel):
    """Generic provider event."""

    type: str = Field(description="Event type")
    data: Any = Field(description="Event data")
    timestamp: float | None = Field(default=None)


class RealtimeEndToEndProvider(Protocol):
    """Protocol for real-time end-to-end AI providers (OpenAI Realtime, Gemini Live).

    These providers handle the full audio-to-audio pipeline internally.
    """

    @abstractmethod
    async def connect(self, config: SessionConfig) -> None:
        """Establish connection to the provider."""
        ...

    @abstractmethod
    async def disconnect(self) -> None:
        """Gracefully disconnect from the provider."""
        ...

    @abstractmethod
    async def send_audio(self, audio: AudioChunk) -> None:
        """Send audio input to the provider."""
        ...

    @abstractmethod
    async def send_text(self, message: TextMessage) -> None:
        """Send text input to the provider."""
        ...

    @abstractmethod
    async def receive_events(self) -> AsyncGenerator[ProviderEvent, None]:
        """Receive events from the provider."""
        ...

    @abstractmethod
    async def handle_function_result(
        self, call_id: str, result: dict[str, Any]
    ) -> None:
        """Send function execution result back to provider."""
        ...

    @property
    @abstractmethod
    def state(self) -> SessionState:
        """Current session state."""
        ...

    @property
    @abstractmethod
    def capabilities(self) -> ProviderCapabilities:
        """Provider capabilities."""
        ...


class SegmentedVoiceProvider(Protocol):
    """Protocol for segmented voice pipeline providers (STT + LLM + TTS).

    These providers require separate components for speech recognition,
    language model processing, and speech synthesis.
    """

    @abstractmethod
    async def connect(self, config: SessionConfig) -> None:
        """Establish connections to all pipeline components."""
        ...

    @abstractmethod
    async def disconnect(self) -> None:
        """Disconnect from all pipeline components."""
        ...

    @abstractmethod
    async def send_audio(self, audio: AudioChunk) -> None:
        """Send audio to STT component."""
        ...

    @abstractmethod
    async def send_text(self, message: TextMessage) -> None:
        """Send text directly to LLM component."""
        ...

    @abstractmethod
    async def receive_events(self) -> AsyncGenerator[ProviderEvent, None]:
        """Receive events from the provider."""
        ...

    @property
    @abstractmethod
    def state(self) -> SessionState:
        """Current pipeline state."""
        ...

    @property
    @abstractmethod
    def capabilities(self) -> ProviderCapabilities:
        """Provider capabilities."""
        ...


class TelephonyAdapter(Protocol):
    """Protocol for telephony service adapters (Twilio, Telnyx).

    These adapters handle the conversion between telephony protocols
    and the unified audio interface.
    """

    @abstractmethod
    async def setup_call(self, call_params: dict[str, Any]) -> dict[str, Any]:
        """Set up a new telephony call."""
        ...

    @abstractmethod
    async def handle_webhook(
        self, event_type: str, payload: dict[str, Any]
    ) -> dict[str, Any] | None:
        """Handle incoming webhook from telephony service."""
        ...

    @abstractmethod
    async def validate_webhook(
        self, signature: str, url: str, payload: dict[str, Any] | str
    ) -> bool:
        """Validate webhook signature."""
        ...

    @abstractmethod
    def generate_answer_twiml(self, stream_url: str) -> str:
        """Generate TwiML/TeXML for answering calls with WebSocket stream."""
        ...

    @abstractmethod
    async def convert_audio_from_telephony(self, audio_data: bytes) -> AudioChunk:
        """Convert telephony audio format to unified format."""
        ...

    @abstractmethod
    async def convert_audio_to_telephony(self, audio: AudioChunk) -> bytes:
        """Convert unified audio format to telephony format."""
        ...

    @abstractmethod
    async def end_call(self, call_id: str) -> None:
        """End an active call."""
        ...

    @property
    @abstractmethod
    def capabilities(self) -> ProviderCapabilities:
        """Telephony adapter capabilities."""
        ...


class BaseProvider(ABC):
    """Base class providing common functionality for providers."""

    def __init__(self, api_key: str):
        """Initialize base provider."""
        self._api_key = api_key
        self._state = SessionState.IDLE
        self._config: SessionConfig | None = None

    @property
    def state(self) -> SessionState:
        """Current session state."""
        return self._state

    @property
    @abstractmethod
    def capabilities(self) -> ProviderCapabilities:
        """Provider capabilities (must be implemented by subclasses)."""
        ...

    @abstractmethod
    async def connect(self, config: SessionConfig) -> None:
        """Establish connection to the provider."""
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """Gracefully disconnect from the provider."""
        pass

    def _validate_audio_format(self, format: AudioFormat) -> None:
        """Validate that audio format is supported."""
        if format not in self.capabilities.audio_formats:
            raise ValueError(
                f"Audio format {format} not supported. "
                f"Supported formats: {self.capabilities.audio_formats}"
            )
