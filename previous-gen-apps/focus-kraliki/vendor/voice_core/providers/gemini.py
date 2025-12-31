from __future__ import annotations

import asyncio
import secrets
from datetime import timedelta
from typing import Dict

try:
    import google.generativeai as genai
except ImportError:  # pragma: no cover - optional dependency
    genai = None  # type: ignore

from ..errors import VoiceProviderUnavailable
from ..types import VoiceProvider, VoiceSession, VoiceSessionOptions, SpeechSynthesisOptions, TranscriptionResult
from .base import BaseVoiceProvider


class GeminiNativeAudioProvider(BaseVoiceProvider):
    """Implements live audio session provisioning for Gemini 2.5 Flash Native Audio Preview."""

    def __init__(
        self,
        *,
        api_key: str | None,
        model: str = "gemini-2.5-flash-native-audio-preview-09-2025",
        region: str | None = None,
    ) -> None:
        super().__init__(enabled=bool(api_key))
        self.api_key = api_key
        self.model = model
        self.region = region or "us"
        self._client = None

        if self.enabled and genai is not None:
            genai.configure(api_key=self.api_key)
            self._client = genai.GenerativeModel(model_name=self.model)

    def _perform_health_check(self) -> bool:
        return bool(self.api_key and genai is not None)

    def create_session(self, options: VoiceSessionOptions) -> VoiceSession:
        if not self.api_key:
            raise VoiceProviderUnavailable("Gemini API key missing")

        session_id = secrets.token_urlsafe(16)
        transport: Dict[str, str] = {
            "handshake": f"/assistant/voice/session/{session_id}/gemini/offer",
            "protocol": "webrtc",
            "iceServer": "stun:stun.l.google.com:19302",
            "model": self.model,
        }

        metadata = {
            "language": options.language,
            "region": self.region,
        }

        return VoiceSession.ephemeral(
            provider=VoiceProvider.GEMINI_NATIVE,
            session_id=session_id,
            ttl=timedelta(minutes=5),
            transport=transport,
            metadata=metadata,
        )

    async def synthesise(self, options: SpeechSynthesisOptions) -> bytes:
        if not self._client:
            raise VoiceProviderUnavailable("Gemini SDK not available")

        prompt = f"Synthesize the following text as natural speech in {options.language}: {options.text}"

        loop = asyncio.get_running_loop()
        response = await loop.run_in_executor(
            None,
            lambda: self._client.generate_content(
                [
                    {
                        "role": "user",
                        "parts": [
                            {"text": prompt},
                        ],
                    }
                ],
                generation_config={"response_mime_type": f"audio/{options.format}"},
            ),
        )

        audio = b""
        for part in getattr(response, "parts", []) or []:
            if hasattr(part, "audio") and part.audio:
                audio += part.audio

        if not audio:
            raise VoiceProviderUnavailable("Gemini did not return audio data")

        return audio

    async def transcribe(self, audio: bytes, *, mimetype: str, language: str) -> TranscriptionResult:
        if not self._client:
            raise VoiceProviderUnavailable("Gemini SDK not available")

        loop = asyncio.get_running_loop()
        response = await loop.run_in_executor(
            None,
            lambda: self._client.generate_content(
                [
                    {
                        "role": "user",
                        "parts": [
                            {
                                "inline_data": {
                                    "mime_type": mimetype,
                                    "data": audio,
                                }
                            },
                            {"text": f"Transcribe the supplied audio to {language} text."},
                        ],
                    }
                ],
                generation_config={"temperature": 0.2},
            ),
        )

        transcript = "".join(part.text for part in getattr(response, "parts", []) if getattr(part, "text", None))
        if not transcript:
            raise VoiceProviderUnavailable("Gemini returned an empty transcription")

        return TranscriptionResult(
            transcript=transcript.strip(),
            confidence=0.85,
            language=language,
            raw={"model": self.model},
        )


__all__ = ["GeminiNativeAudioProvider"]
