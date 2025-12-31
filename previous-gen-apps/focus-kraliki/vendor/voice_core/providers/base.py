from __future__ import annotations

import abc
from typing import Any, Dict, Optional

from ..types import VoiceSession, VoiceSessionOptions, SpeechSynthesisOptions, TranscriptionResult


class BaseVoiceProvider(abc.ABC):
    """Abstract interface for voice providers."""

    def __init__(self, *, enabled: bool = True) -> None:
        self._enabled = enabled

    @property
    def enabled(self) -> bool:
        return self._enabled

    def is_available(self) -> bool:
        return self._enabled and self._perform_health_check()

    def _perform_health_check(self) -> bool:
        return True

    @abc.abstractmethod
    def create_session(self, options: VoiceSessionOptions) -> VoiceSession:
        """Provision a live audio session for the provider."""

    async def synthesise(self, options: SpeechSynthesisOptions) -> bytes:
        raise NotImplementedError

    async def transcribe(self, audio: bytes, *, mimetype: str, language: str) -> TranscriptionResult:
        raise NotImplementedError

    async def close_session(self, session: VoiceSession) -> None:
        return None


__all__ = ["BaseVoiceProvider"]
