"""Voice core stub module for testing"""

from enum import Enum


class VoiceProvider(str, Enum):
    """Voice provider enum stub"""
    GEMINI_NATIVE = "gemini_native"
    OPENAI_REALTIME = "openai_realtime"
    DEEPGRAM_TRANSCRIPTION = "deepgram_transcription"


class VoiceProviderUnavailable(Exception):
    """Voice provider unavailable exception stub"""
    pass


class VoiceSession:
    """Voice session stub"""
    pass


class TranscriptionResult:
    """Transcription result stub"""
    pass


class VoiceSessionOptions:
    """Voice session options stub"""
    pass


class SpeechSynthesisOptions:
    """Speech synthesis options stub"""
    pass


class VoiceSessionManager:
    """Voice session manager stub"""
    def __init__(self, *args, **kwargs):
        pass

    @classmethod
    def from_config(cls, **kwargs):
        return cls()

    def available_providers(self):
        return []
