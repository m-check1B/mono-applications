from __future__ import annotations

from typing import Dict, Optional

from .errors import VoiceProviderUnavailable, VoiceSessionNotFound
from .providers.base import BaseVoiceProvider
from .providers.deepgram import DeepgramTranscriptionProvider
from .providers.gemini import GeminiNativeAudioProvider
from .providers.openai_realtime import OpenAIRealtimeProvider
from .types import (
    VoiceProvider,
    VoiceSession,
    VoiceSessionOptions,
    SpeechSynthesisOptions,
    TranscriptionResult,
)


class VoiceSessionManager:
    """Coordinator that exposes a simple API to the application layer."""

    def __init__(
        self,
        *,
        gemini: Optional[GeminiNativeAudioProvider] = None,
        openai: Optional[OpenAIRealtimeProvider] = None,
        deepgram: Optional[DeepgramTranscriptionProvider] = None,
    ) -> None:
        self._providers: Dict[VoiceProvider, BaseVoiceProvider] = {}
        self._sessions: Dict[str, VoiceSession] = {}

        if gemini:
            self._providers[VoiceProvider.GEMINI_NATIVE] = gemini
        if openai:
            self._providers[VoiceProvider.OPENAI_REALTIME] = openai
        if deepgram:
            self._providers[VoiceProvider.DEEPGRAM_TRANSCRIPTION] = deepgram

    @classmethod
    def from_config(
        cls,
        *,
        gemini_api_key: Optional[str],
        gemini_model: str,
        openai_api_key: Optional[str],
        openai_model: str,
        openai_tts_model: str,
        deepgram_api_key: Optional[str],
        deepgram_model: str,
    ) -> "VoiceSessionManager":
        gemini = GeminiNativeAudioProvider(api_key=gemini_api_key, model=gemini_model) if gemini_api_key else None
        openai = (
            OpenAIRealtimeProvider(api_key=openai_api_key, model=openai_model, tts_model=openai_tts_model)
            if openai_api_key
            else None
        )
        deepgram = DeepgramTranscriptionProvider(api_key=deepgram_api_key, model=deepgram_model) if deepgram_api_key else None
        return cls(gemini=gemini, openai=openai, deepgram=deepgram)

    def is_provider_available(self, provider: VoiceProvider) -> bool:
        handler = self._providers.get(provider)
        return bool(handler and handler.is_available())

    def create_session(self, provider: VoiceProvider, options: VoiceSessionOptions) -> VoiceSession:
        handler = self._providers.get(provider)
        if not handler or not handler.is_available():
            raise VoiceProviderUnavailable(f"Provider {provider.value} is not configured")

        session = handler.create_session(options)
        self._sessions[session.session_id] = session
        return session

    def get_session(self, session_id: str) -> VoiceSession:
        session = self._sessions.get(session_id)
        if not session:
            raise VoiceSessionNotFound(session_id)
        return session

    async def close_session(self, session_id: str) -> None:
        session = self._sessions.pop(session_id, None)
        if not session:
            return
        handler = self._providers.get(session.provider)
        if handler:
            await handler.close_session(session)

    async def transcribe(
        self,
        audio: bytes,
        *,
        mimetype: str,
        language: str,
        provider: VoiceProvider | None = None,
    ) -> TranscriptionResult:
        provider = provider or VoiceProvider.DEEPGRAM_TRANSCRIPTION
        handler = self._providers.get(provider)
        if not handler:
            raise VoiceProviderUnavailable(f"Provider {provider.value} not available for transcription")
        return await handler.transcribe(audio, mimetype=mimetype, language=language)

    async def synthesise(self, options: SpeechSynthesisOptions) -> bytes:
        provider = options.provider
        handler = self._providers.get(provider)
        if not handler:
            raise VoiceProviderUnavailable(f"Provider {provider.value} cannot synthesise speech")
        return await handler.synthesise(options)

    @property
    def available_providers(self) -> Dict[VoiceProvider, bool]:
        return {provider: handler.is_available() for provider, handler in self._providers.items()}


__all__ = ["VoiceSessionManager"]
