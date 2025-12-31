from __future__ import annotations

import asyncio
import secrets
from datetime import timedelta
from typing import Dict

try:
    from openai import OpenAI
except ImportError:  # pragma: no cover - optional dependency
    OpenAI = None  # type: ignore

from ..errors import VoiceProviderUnavailable
from ..types import VoiceProvider, VoiceSession, VoiceSessionOptions, SpeechSynthesisOptions, TranscriptionResult
from .base import BaseVoiceProvider


class OpenAIRealtimeProvider(BaseVoiceProvider):
    def __init__(
        self,
        *,
        api_key: str | None,
        model: str = "gpt-4o-realtime-preview-2024-12-17",
        tts_model: str = "gpt-4o-mini-tts",
    ) -> None:
        super().__init__(enabled=bool(api_key))
        self.api_key = api_key
        self.model = model
        self.tts_model = tts_model
        self._client = OpenAI(api_key=api_key) if (api_key and OpenAI is not None) else None

    def _perform_health_check(self) -> bool:
        return bool(self.api_key and self._client)

    def create_session(self, options: VoiceSessionOptions) -> VoiceSession:
        if not self.api_key:
            raise VoiceProviderUnavailable("OpenAI API key missing")

        session_id = secrets.token_urlsafe(16)
        transport: Dict[str, str | bool] = {
            "handshake": f"/assistant/voice/session/{session_id}/openai/offer",
            "protocol": "webrtc",
            "model": self.model,
            "voice": options.voice or "verse",
        }

        return VoiceSession.ephemeral(
            provider=VoiceProvider.OPENAI_REALTIME,
            session_id=session_id,
            ttl=timedelta(minutes=5),
            transport=transport,
            metadata={"language": options.language},
        )

    async def synthesise(self, options: SpeechSynthesisOptions) -> bytes:
        if not self._client:
            raise VoiceProviderUnavailable("OpenAI client not available")

        loop = asyncio.get_running_loop()
        response = await loop.run_in_executor(
            None,
            lambda: self._client.audio.speech.create(
                model=self.tts_model,
                voice=options.voice or "verse",
                input=options.text,
                format=options.format,
                language=options.language,
            ),
        )
        return response.read() if hasattr(response, "read") else bytes(response)

    async def transcribe(self, audio: bytes, *, mimetype: str, language: str) -> TranscriptionResult:
        if not self._client:
            raise VoiceProviderUnavailable("OpenAI client not available")

        loop = asyncio.get_running_loop()
        transcript = await loop.run_in_executor(
            None,
            lambda: self._client.audio.transcriptions.create(
                file=("audio", audio, mimetype),
                model="gpt-4o-transcribe-preview",
                language=language,
            ),
        )
        text = getattr(transcript, "text", "").strip()
        if not text:
            raise VoiceProviderUnavailable("OpenAI transcription failed")

        return TranscriptionResult(
            transcript=text,
            confidence=0.9,
            language=language,
            raw={"model": "gpt-4o-transcribe-preview"},
        )


__all__ = ["OpenAIRealtimeProvider"]
