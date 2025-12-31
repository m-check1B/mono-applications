"""Base provider protocols and types for AI provider abstraction.

This module defines the abstract base classes and protocols that all
AI providers must implement to work with the unified provider interface.
"""

from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator
from enum import Enum
from typing import Any, Protocol

from pydantic import BaseModel, Field


class AudioFormat(str, Enum):
    """Supported audio formats."""

    PCM16 = "pcm16"  # 16-bit PCM
    ULAW = "ulaw"  # μ-law encoding (8-bit)
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
        """Establish connection to the provider.

        Args:
            config: Session configuration

        Raises:
            ConnectionError: If connection fails
        """
        ...

    @abstractmethod
    async def disconnect(self) -> None:
        """Gracefully disconnect from the provider."""
        ...

    @abstractmethod
    async def send_audio(self, audio: AudioChunk) -> None:
        """Send audio input to the provider.

        Args:
            audio: Audio chunk to send
        """
        ...

    @abstractmethod
    async def send_text(self, message: TextMessage) -> None:
        """Send text input to the provider.

        Args:
            message: Text message to send
        """
        ...

    @abstractmethod
    async def receive_events(self) -> AsyncGenerator[ProviderEvent]:
        """Receive events from the provider.

        Yields:
            ProviderEvent: Audio, text, function call, or other events
        """
        ...

    @abstractmethod
    async def handle_function_result(
        self, call_id: str, result: dict[str, Any]
    ) -> None:
        """Send function execution result back to provider.

        Args:
            call_id: Function call ID
            result: Function execution result
        """
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
        """Establish connections to all pipeline components.

        Args:
            config: Session configuration

        Raises:
            ConnectionError: If any component connection fails
        """
        ...

    @abstractmethod
    async def disconnect(self) -> None:
        """Disconnect from all pipeline components."""
        ...

    @abstractmethod
    async def send_audio(self, audio: AudioChunk) -> None:
        """Send audio to STT component.

        Args:
            audio: Audio chunk to transcribe
        """
        ...

    @abstractmethod
    async def send_text(self, message: TextMessage) -> None:
        """Send text directly to LLM component.

        Args:
            message: Text message to process
        """
        ...

    @abstractmethod
    async def receive_events(self) -> AsyncGenerator[ProviderEvent]:
        """Receive events from the provider.

        Yields:
            ProviderEvent: Audio, text, function call, or other events
        """
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
        """Set up a new telephony call.

        Args:
            call_params: Call parameters (number, webhook URLs, etc.)

        Returns:
            dict: Call metadata (call_id, status, etc.)
        """
        ...

    @abstractmethod
    async def handle_webhook(
        self, event_type: str, payload: dict[str, Any]
    ) -> dict[str, Any] | None:
        """Handle incoming webhook from telephony service.

        Args:
            event_type: Type of webhook event
            payload: Webhook payload

        Returns:
            Optional response data for the webhook
        """
        ...

    @abstractmethod
    async def validate_webhook(
        self, signature: str, url: str, payload: dict[str, Any] | str
    ) -> bool:
        """Validate webhook signature.

        Args:
            signature: Webhook signature header
            url: Full webhook URL
            payload: Request payload

        Returns:
            bool: True if signature is valid
        """
        ...

    @abstractmethod
    def generate_answer_twiml(self, stream_url: str) -> str:
        """Generate TwiML for answering calls with WebSocket stream.

        Args:
            stream_url: WebSocket URL for audio streaming

        Returns:
            str: TwiML response
        """
        ...
        ...

    @abstractmethod
    async def convert_audio_from_telephony(self, audio_data: bytes) -> AudioChunk:
        """Convert telephony audio format to unified format.

        Args:
            audio_data: Raw telephony audio data

        Returns:
            AudioChunk: Converted audio chunk
        """
        ...

    @abstractmethod
    async def convert_audio_to_telephony(self, audio: AudioChunk) -> bytes:
        """Convert unified audio format to telephony format.

        Args:
            audio: Audio chunk in unified format

        Returns:
            bytes: Telephony-formatted audio data
        """
        ...

    @abstractmethod
    async def end_call(self, call_id: str) -> None:
        """End an active call.

        Args:
            call_id: Call identifier
        """
        ...

    @property
    @abstractmethod
    def capabilities(self) -> ProviderCapabilities:
        """Telephony adapter capabilities."""
        ...


class BaseProvider(ABC):
    """Base class providing common functionality for providers."""

    def __init__(self, api_key: str):
        """Initialize base provider.

        Args:
            api_key: Provider API key
        """
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
        """Establish connection to the provider.

        Args:
            config: Session configuration

        Raises:
            ConnectionError: If connection fails
        """
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """Gracefully disconnect from the provider."""
        pass

    def _validate_audio_format(self, format: AudioFormat) -> None:
        """Validate that audio format is supported.

        Args:
            format: Audio format to validate

        Raises:
            ValueError: If format is not supported
        """
        if format not in self.capabilities.audio_formats:
            raise ValueError(
                f"Audio format {format} not supported. "
                f"Supported formats: {self.capabilities.audio_formats}"
            )
