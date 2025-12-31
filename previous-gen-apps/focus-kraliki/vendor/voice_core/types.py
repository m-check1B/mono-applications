from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Dict, Optional


class VoiceProvider(str, Enum):
    GEMINI_NATIVE = "gemini-native"
    OPENAI_REALTIME = "openai-realtime"
    DEEPGRAM_TRANSCRIPTION = "deepgram-transcription"


@dataclass(slots=True)
class VoiceSessionOptions:
    language: str = "en-US"
    voice: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class VoiceSession:
    provider: VoiceProvider
    session_id: str
    created_at: datetime
    expires_at: datetime
    transport: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def ephemeral(
        cls,
        provider: VoiceProvider,
        session_id: str,
        ttl: timedelta,
        transport: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> "VoiceSession":
        now = datetime.now(timezone.utc)
        return cls(
            provider=provider,
            session_id=session_id,
            created_at=now,
            expires_at=now + ttl,
            transport=transport,
            metadata=metadata or {},
        )

    def is_expired(self, buffer_seconds: int = 15) -> bool:
        return datetime.now(timezone.utc) > (self.expires_at - timedelta(seconds=buffer_seconds))


@dataclass(slots=True)
class SpeechSynthesisOptions:
    text: str
    voice: Optional[str] = None
    format: str = "wav"
    language: str = "en"
    provider: VoiceProvider = VoiceProvider.OPENAI_REALTIME


@dataclass(slots=True)
class TranscriptionResult:
    transcript: str
    confidence: float
    language: str
    raw: Dict[str, Any] = field(default_factory=dict)


__all__ = [
    "VoiceProvider",
    "VoiceSessionOptions",
    "VoiceSession",
    "SpeechSynthesisOptions",
    "TranscriptionResult",
]
