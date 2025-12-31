from __future__ import annotations

import asyncio
from typing import Dict

try:
    from deepgram import Deepgram
except ImportError:  # pragma: no cover - optional dependency
    Deepgram = None  # type: ignore

from ..errors import VoiceProviderUnavailable
from ..types import VoiceProvider, VoiceSession, VoiceSessionOptions, SpeechSynthesisOptions, TranscriptionResult
from .base import BaseVoiceProvider


class DeepgramTranscriptionProvider(BaseVoiceProvider):
    def __init__(self, *, api_key: str | None, model: str = "nova-2-general") -> None:
        super().__init__(enabled=bool(api_key))
        self.api_key = api_key
        self.model = model
        self._client = Deepgram(api_key) if (api_key and Deepgram is not None) else None

    def _perform_health_check(self) -> bool:
        return bool(self.api_key and self._client)

    def create_session(self, options: VoiceSessionOptions) -> VoiceSession:
        raise VoiceProviderUnavailable("Deepgram is transcription-only in Stack 2026")

    async def transcribe(self, audio: bytes, *, mimetype: str, language: str) -> TranscriptionResult:
        if not self._client:
            raise VoiceProviderUnavailable("Deepgram client not available")

        loop = asyncio.get_running_loop()
        response = await loop.run_in_executor(
            None,
            lambda: self._client.transcription.sync_prerecorded(
                {
                    "buffer": audio,
                    "mimetype": mimetype,
                },
                {
                    "model": self.model,
                    "language": language,
                    "smart_format": True,
                    "punctuate": True,
                },
            ),
        )

        channel = response.get("results", {}).get("channels", [{}])[0]
        alt = channel.get("alternatives", [{}])[0]
        transcript = alt.get("transcript", "")

        if not transcript:
            raise VoiceProviderUnavailable("Deepgram returned an empty transcript")

        return TranscriptionResult(
            transcript=transcript,
            confidence=alt.get("confidence", 0.8),
            language=language,
            raw=response,
        )

    async def synthesise(self, options: SpeechSynthesisOptions) -> bytes:
        raise VoiceProviderUnavailable("Deepgram TTS disabled in Stack 2026 alignment")


__all__ = ["DeepgramTranscriptionProvider"]
