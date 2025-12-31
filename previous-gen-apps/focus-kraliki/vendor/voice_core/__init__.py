"""Shared voice integration layer for Stack 2026 applications.

This package centralises the logic required to talk to real-time multimodal
providers (Gemini Native Audio Preview + OpenAI Realtime) while leaving
Deepgram available for high-quality offline transcription. It is implemented as
an optional vendor module so that other applications can vendor the same code
without converting to a mono-repo.
"""

from .manager import VoiceSessionManager
from .types import (
    VoiceProvider,
    VoiceSession,
    VoiceSessionOptions,
    SpeechSynthesisOptions,
    TranscriptionResult,
)
from .errors import VoiceProviderUnavailable, VoiceSessionNotFound

__all__ = [
    "VoiceSessionManager",
    "VoiceProvider",
    "VoiceSession",
    "VoiceSessionOptions",
    "SpeechSynthesisOptions",
    "TranscriptionResult",
    "VoiceProviderUnavailable",
    "VoiceSessionNotFound",
]
