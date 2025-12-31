"""Transcription Core - Audio transcription services for Platform 2026.

Supports:
- Deepgram (Nova-2, Whisper)
"""

from transcription_core.base import (
    BaseTranscriber,
    Transcriber,
    TranscriptionConfig,
    TranscriptionResult,
    WordInfo,
)

__all__ = [
    "BaseTranscriber",
    "Transcriber",
    "TranscriptionConfig",
    "TranscriptionResult",
    "WordInfo",
]

# Deepgram transcriber
try:
    from transcription_core.providers.deepgram import (
        DeepgramTranscriber,
        create_deepgram_transcriber,
    )
    __all__.extend(["DeepgramTranscriber", "create_deepgram_transcriber"])
except ImportError:
    pass
