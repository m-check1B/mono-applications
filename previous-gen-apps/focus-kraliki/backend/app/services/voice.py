from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional

from vendor.voice_core import (
    VoiceProvider,
    VoiceSessionManager,
    VoiceSessionOptions,
    SpeechSynthesisOptions,
    VoiceSession,
    TranscriptionResult,
    VoiceProviderUnavailable,
)
from vendor.voice_core.errors import VoiceSessionNotFound


@dataclass(slots=True)
class VoiceServiceConfig:
    gemini_api_key: Optional[str]
    gemini_model: str
    openai_api_key: Optional[str]
    openai_model: str
    openai_tts_model: str
    deepgram_api_key: Optional[str]
    deepgram_model: str


class VoiceService:
    def __init__(self, config: VoiceServiceConfig) -> None:
        self._manager = VoiceSessionManager.from_config(
            gemini_api_key=config.gemini_api_key,
            gemini_model=config.gemini_model,
            openai_api_key=config.openai_api_key,
            openai_model=config.openai_model,
            openai_tts_model=config.openai_tts_model,
            deepgram_api_key=config.deepgram_api_key,
            deepgram_model=config.deepgram_model,
        )

    def available_providers(self) -> Dict[str, bool]:
        providers = self._manager.available_providers
        if callable(providers):
            providers = providers()
        if isinstance(providers, list):
            providers = {provider: True for provider in providers}
        return {provider.value: available for provider, available in providers.items()}

    def create_session(
        self,
        provider: VoiceProvider,
        *,
        language: str,
        voice: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
    ) -> VoiceSession:
        options = VoiceSessionOptions(language=language, voice=voice, metadata=metadata or {})
        return self._manager.create_session(provider, options)

    async def close_session(self, session_id: str) -> None:
        await self._manager.close_session(session_id)

    def get_session(self, session_id: str) -> VoiceSession:
        return self._manager.get_session(session_id)

    async def transcribe(
        self,
        audio: bytes,
        *,
        mimetype: str,
        language: str,
        provider: VoiceProvider | None = None,
    ) -> TranscriptionResult:
        return await self._manager.transcribe(audio, mimetype=mimetype, language=language, provider=provider)

    async def synthesise(
        self,
        *,
        text: str,
        provider: VoiceProvider,
        voice: Optional[str] = None,
        format: str = "wav",
        language: str = "en",
    ) -> bytes:
        options = SpeechSynthesisOptions(
            text=text,
            voice=voice,
            format=format,
            language=language,
            provider=provider,
        )
        return await self._manager.synthesise(options)


__all__ = ["VoiceService", "VoiceServiceConfig", "VoiceProviderUnavailable", "VoiceSessionNotFound", "VoiceProvider"]
