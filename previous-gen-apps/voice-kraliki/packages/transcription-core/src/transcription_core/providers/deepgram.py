"""Deepgram transcription provider using official SDK.

Deepgram provides fast, accurate speech-to-text:
- Nova-2: Best accuracy/speed balance
- Whisper: OpenAI Whisper model hosted by Deepgram
- Multiple languages supported
- Speaker diarization
- Word-level timestamps
"""

import logging
from typing import Any

from transcription_core.base import (
    BaseTranscriber,
    TranscriptionConfig,
    TranscriptionResult,
    WordInfo,
)

logger = logging.getLogger(__name__)


class DeepgramTranscriber(BaseTranscriber):
    """Deepgram transcription service using official SDK.

    Use for:
    - Call recording transcription
    - Meeting transcription
    - Podcast/video transcription
    - Any async audio file transcription
    """

    def __init__(self, api_key: str):
        """Initialize Deepgram transcriber.

        Args:
            api_key: Deepgram API key
        """
        super().__init__(api_key)
        self._client: Any = None

    def _ensure_client(self) -> Any:
        """Lazy-load Deepgram client."""
        if self._client is None:
            try:
                from deepgram import DeepgramClient
            except ImportError:
                raise ImportError(
                    "deepgram-sdk required. Install with: pip install deepgram-sdk"
                )
            self._client = DeepgramClient(self._api_key)
        return self._client

    async def transcribe_file(
        self,
        audio_data: bytes,
        config: TranscriptionConfig | None = None,
    ) -> TranscriptionResult:
        """Transcribe audio file data.

        Args:
            audio_data: Raw audio bytes (WAV, MP3, FLAC, etc.)
            config: Transcription configuration

        Returns:
            TranscriptionResult with text and metadata
        """
        config = config or TranscriptionConfig()
        client = self._ensure_client()

        try:
            from deepgram import PrerecordedOptions
        except ImportError:
            raise ImportError("deepgram-sdk required")

        options = PrerecordedOptions(
            model=config.model,
            language=config.language,
            punctuate=config.punctuate,
            diarize=config.diarize,
            smart_format=config.smart_format,
            utterances=config.utterances,
        )

        if config.keywords:
            options.keywords = config.keywords

        try:
            response = await client.listen.asyncrest.v("1").transcribe_file(
                {"buffer": audio_data},
                options,
            )
            return self._parse_response(response, config.language)

        except Exception as e:
            logger.error(f"Deepgram transcription failed: {e}")
            raise

    async def transcribe_url(
        self,
        url: str,
        config: TranscriptionConfig | None = None,
    ) -> TranscriptionResult:
        """Transcribe audio from URL.

        Args:
            url: URL to audio file
            config: Transcription configuration

        Returns:
            TranscriptionResult with text and metadata
        """
        config = config or TranscriptionConfig()
        client = self._ensure_client()

        try:
            from deepgram import PrerecordedOptions
        except ImportError:
            raise ImportError("deepgram-sdk required")

        options = PrerecordedOptions(
            model=config.model,
            language=config.language,
            punctuate=config.punctuate,
            diarize=config.diarize,
            smart_format=config.smart_format,
            utterances=config.utterances,
        )

        if config.keywords:
            options.keywords = config.keywords

        try:
            response = await client.listen.asyncrest.v("1").transcribe_url(
                {"url": url},
                options,
            )
            return self._parse_response(response, config.language)

        except Exception as e:
            logger.error(f"Deepgram transcription failed: {e}")
            raise

    def _parse_response(self, response: Any, language: str) -> TranscriptionResult:
        """Parse Deepgram response into TranscriptionResult."""
        result = response.results
        if not result or not result.channels:
            return TranscriptionResult(text="", confidence=0.0)

        channel = result.channels[0]
        if not channel.alternatives:
            return TranscriptionResult(text="", confidence=0.0)

        alt = channel.alternatives[0]

        words = []
        for w in (alt.words or []):
            words.append(WordInfo(
                word=w.word,
                start=w.start,
                end=w.end,
                confidence=w.confidence,
                speaker=getattr(w, "speaker", None),
            ))

        return TranscriptionResult(
            text=alt.transcript or "",
            confidence=alt.confidence or 0.0,
            words=words,
            duration=result.metadata.duration if result.metadata else None,
            language=language,
            speakers=None,  # Would need to count unique speakers from words
        )


def create_deepgram_transcriber(api_key: str) -> DeepgramTranscriber:
    """Create Deepgram transcriber instance."""
    return DeepgramTranscriber(api_key=api_key)
