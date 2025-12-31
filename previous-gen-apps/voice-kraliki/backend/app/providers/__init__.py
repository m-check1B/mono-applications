"""Provider abstraction layer for multi-provider AI integration.

This package provides a unified interface for integrating multiple AI providers
including OpenAI, Gemini, and Deepgram with telephony adapters.

NOTE: This module re-exports from the local voice-core package in /packages
for shared functionality. Local extensions (circuit breaker, metrics) are added
on top.
"""

# Try to import from voice-core (local shared module)
try:
    from voice_core import (
        AudioChunk,
        AudioFormat,
        BaseProvider,
        FunctionCall,
        ProviderCapabilities,
        ProviderEvent,
        RealtimeEndToEndProvider,
        SegmentedVoiceProvider,
        SessionConfig,
        SessionState,
        TelephonyAdapter,
        TextMessage,
    )
    VOICE_CORE_AVAILABLE = True
except ImportError:
    # Fallback to local implementation if voice-core not installed
    from app.providers.base import (
        AudioChunk,
        AudioFormat,
        BaseProvider,
        FunctionCall,
        ProviderCapabilities,
        ProviderEvent,
        RealtimeEndToEndProvider,
        SegmentedVoiceProvider,
        SessionConfig,
        SessionState,
        TelephonyAdapter,
        TextMessage,
    )
    VOICE_CORE_AVAILABLE = False

__all__ = [
    "AudioFormat",
    "AudioChunk",
    "ProviderCapabilities",
    "ProviderEvent",
    "RealtimeEndToEndProvider",
    "SegmentedVoiceProvider",
    "SessionConfig",
    "SessionState",
    "TelephonyAdapter",
    "TextMessage",
    "FunctionCall",
    "BaseProvider",
    "VOICE_CORE_AVAILABLE",
]
