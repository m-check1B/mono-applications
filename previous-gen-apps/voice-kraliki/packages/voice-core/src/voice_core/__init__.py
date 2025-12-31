"""
Voice Core - Unified real-time voice provider abstraction.

Provides:
- RealtimeEndToEndProvider protocol (OpenAI, Gemini)
- SegmentedVoiceProvider protocol (Deepgram)
- TelephonyAdapter protocol (Telnyx, Twilio)
- Provider registry with capability matching

Part of voice-kraliki core packages.
"""

from voice_core.base import (
    AudioFormat,
    SessionState,
    ProviderCapabilities,
    SessionConfig,
    AudioChunk,
    TextMessage,
    FunctionCall,
    ProviderEvent,
    RealtimeEndToEndProvider,
    SegmentedVoiceProvider,
    TelephonyAdapter,
    BaseProvider,
)

__version__ = "0.1.0"

__all__ = [
    # Enums
    "AudioFormat",
    "SessionState",
    # Models
    "ProviderCapabilities",
    "SessionConfig",
    "AudioChunk",
    "TextMessage",
    "FunctionCall",
    "ProviderEvent",
    # Protocols
    "RealtimeEndToEndProvider",
    "SegmentedVoiceProvider",
    "TelephonyAdapter",
    # Base class
    "BaseProvider",
]
