"""Base types and protocols for transcription services.

This module defines the abstract interface for audio transcription.
"""

from abc import ABC, abstractmethod
from typing import Any, Protocol

from pydantic import BaseModel, Field


class TranscriptionConfig(BaseModel):
    """Configuration for transcription requests."""

    model: str = Field(default="nova-2", description="Transcription model")
    language: str = Field(default="en", description="Language code")
    punctuate: bool = Field(default=True, description="Add punctuation")
    diarize: bool = Field(default=False, description="Speaker diarization")
    smart_format: bool = Field(default=True, description="Smart formatting")
    utterances: bool = Field(default=False, description="Split into utterances")
    keywords: list[str] = Field(default_factory=list, description="Keyword boosting")


class WordInfo(BaseModel):
    """Word-level transcription details."""

    word: str = Field(description="The transcribed word")
    start: float = Field(description="Start time in seconds")
    end: float = Field(description="End time in seconds")
    confidence: float = Field(description="Confidence score 0-1")
    speaker: int | None = Field(default=None, description="Speaker ID if diarized")


class TranscriptionResult(BaseModel):
    """Result of a transcription request."""

    text: str = Field(description="Full transcription text")
    confidence: float = Field(description="Overall confidence score 0-1")
    words: list[WordInfo] = Field(default_factory=list, description="Word-level details")
    duration: float | None = Field(default=None, description="Audio duration in seconds")
    language: str | None = Field(default=None, description="Detected/specified language")
    speakers: int | None = Field(default=None, description="Number of speakers detected")


class Transcriber(Protocol):
    """Protocol for transcription services."""

    @abstractmethod
    async def transcribe_file(
        self,
        audio_data: bytes,
        config: TranscriptionConfig | None = None,
    ) -> TranscriptionResult:
        """Transcribe audio file data."""
        ...

    @abstractmethod
    async def transcribe_url(
        self,
        url: str,
        config: TranscriptionConfig | None = None,
    ) -> TranscriptionResult:
        """Transcribe audio from URL."""
        ...


class BaseTranscriber(ABC):
    """Base class for transcription providers."""

    def __init__(self, api_key: str):
        """Initialize with API key."""
        self._api_key = api_key

    @abstractmethod
    async def transcribe_file(
        self,
        audio_data: bytes,
        config: TranscriptionConfig | None = None,
    ) -> TranscriptionResult:
        """Transcribe audio file data."""
        ...

    @abstractmethod
    async def transcribe_url(
        self,
        url: str,
        config: TranscriptionConfig | None = None,
    ) -> TranscriptionResult:
        """Transcribe audio from URL."""
        ...
