"""Real-time transcription service for AI-first call center.

This service provides real-time speech-to-text transcription with:
- Multi-language support
- Speaker identification
- Real-time streaming
- Confidence scoring
"""

import logging
from datetime import UTC, datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel

from app.services.context_sharing import (
    ChannelType,
    ContextEvent,
    ContextEventType,
    context_sharing_service,
)

logger = logging.getLogger(__name__)


class TranscriptionLanguage(str, Enum):
    """Supported transcription languages."""
    ENGLISH = "en"
    SPANISH = "es"
    CZECH = "cs"
    GERMAN = "de"
    FRENCH = "fr"


class SpeakerRole(str, Enum):
    """Speaker roles in conversation."""
    AGENT = "agent"
    CUSTOMER = "customer"
    SYSTEM = "system"


class TranscriptionSegment(BaseModel):
    """A single transcription segment."""
    id: str
    session_id: UUID
    text: str
    speaker: SpeakerRole
    language: TranscriptionLanguage
    confidence: float
    start_time: datetime
    end_time: datetime | None = None
    is_final: bool = False

    class Config:
        json_schema_extra = {
            "example": {
                "id": "seg_123",
                "session_id": "550e8400-e29b-41d4-a716-446655440000",
                "text": "Hello, how can I help you today?",
                "speaker": "agent",
                "language": "en",
                "confidence": 0.95,
                "start_time": "2025-10-12T12:00:00Z",
                "is_final": True
            }
        }


class TranscriptionConfig(BaseModel):
    """Configuration for transcription service."""
    language: TranscriptionLanguage = TranscriptionLanguage.ENGLISH
    enable_speaker_detection: bool = True
    enable_punctuation: bool = True
    enable_interim_results: bool = True
    min_confidence: float = 0.7

    class Config:
        json_schema_extra = {
            "example": {
                "language": "en",
                "enable_speaker_detection": True,
                "enable_punctuation": True,
                "enable_interim_results": True,
                "min_confidence": 0.7
            }
        }


class TranscriptionService:
    """Real-time transcription service.

    Provides speech-to-text with speaker detection and multi-language support.
    Integrates with voice providers for real-time transcription.
    """

    def __init__(self):
        """Initialize transcription service."""
        self._active_sessions: dict[UUID, TranscriptionConfig] = {}
        self._transcription_history: dict[UUID, list[TranscriptionSegment]] = {}

    async def start_transcription(
        self,
        session_id: UUID,
        config: TranscriptionConfig
    ) -> None:
        """Start transcription for a session.

        Args:
            session_id: Session identifier
            config: Transcription configuration
        """
        self._active_sessions[session_id] = config
        self._transcription_history[session_id] = []
        logger.info(f"Started transcription for session {session_id}")

    async def stop_transcription(self, session_id: UUID) -> None:
        """Stop transcription for a session.

        Args:
            session_id: Session identifier
        """
        if session_id in self._active_sessions:
            del self._active_sessions[session_id]
        logger.info(f"Stopped transcription for session {session_id}")

    async def process_audio_chunk(
        self,
        session_id: UUID,
        audio_data: bytes
    ) -> TranscriptionSegment | None:
        """Process audio chunk and return transcription if available.

        Args:
            session_id: Session identifier
            audio_data: Raw audio bytes

        Returns:
            TranscriptionSegment if transcription available, None otherwise
        """
        if session_id not in self._active_sessions:
            logger.warning(f"No active transcription for session {session_id}")
            return None

        # This is a placeholder - actual implementation would integrate
        # with the voice provider's transcription capabilities
        # For now, we'll rely on the provider's transcription events
        return None

    async def add_transcription(
        self,
        session_id: UUID,
        text: str,
        speaker: SpeakerRole,
        confidence: float = 1.0,
        is_final: bool = True
    ) -> TranscriptionSegment:
        """Add a transcription segment.

        Args:
            session_id: Session identifier
            text: Transcribed text
            speaker: Speaker role
            confidence: Confidence score (0-1)
            is_final: Whether this is a final transcription

        Returns:
            Created transcription segment
        """
        config = self._active_sessions.get(session_id)
        if not config:
            raise ValueError(f"No active transcription for session {session_id}")

        segment = TranscriptionSegment(
            id=f"seg_{len(self._transcription_history.get(session_id, []))}",
            session_id=session_id,
            text=text,
            speaker=speaker,
            language=config.language,
            confidence=confidence,
            start_time=datetime.now(UTC),
            is_final=is_final
        )

        if session_id not in self._transcription_history:
            self._transcription_history[session_id] = []

        self._transcription_history[session_id].append(segment)

        # Add to shared context
        try:
            context_sharing_service.add_event(
                str(session_id),
                ContextEvent(
                    event_type=ContextEventType.MESSAGE_SENT,
                    channel=ChannelType.VOICE,
                    session_id=str(session_id),
                    data={
                        "role": "assistant" if speaker == SpeakerRole.AGENT else "user",
                        "content": text,
                        "metadata": {
                            "speaker": speaker.value,
                            "confidence": confidence,
                            "is_final": is_final
                        }
                    }
                )
            )
        except Exception as e:
            logger.warning(f"Failed to add transcription to shared context for session {session_id}: {e}")

        logger.debug(
            f"Added transcription for {session_id}: "
            f"{speaker}({confidence:.2f}): {text[:50]}..."
        )

        return segment

    def get_transcription_history(
        self,
        session_id: UUID,
        limit: int | None = None
    ) -> list[TranscriptionSegment]:
        """Get transcription history for a session.

        Args:
            session_id: Session identifier
            limit: Maximum number of segments to return

        Returns:
            List of transcription segments
        """
        history = self._transcription_history.get(session_id, [])

        if limit:
            return history[-limit:]

        return history

    def get_full_transcript(
        self,
        session_id: UUID,
        include_interim: bool = False
    ) -> str:
        """Get full transcript as formatted text.

        Args:
            session_id: Session identifier
            include_interim: Whether to include interim results

        Returns:
            Formatted transcript text
        """
        history = self._transcription_history.get(session_id, [])

        lines = []
        for segment in history:
            if not include_interim and not segment.is_final:
                continue

            speaker_label = segment.speaker.value.upper()
            lines.append(f"{speaker_label}: {segment.text}")

        return "\n".join(lines)

    async def get_session_stats(self, session_id: UUID) -> dict:
        """Get transcription statistics for a session.

        Args:
            session_id: Session identifier

        Returns:
            Dictionary of transcription stats
        """
        history = self._transcription_history.get(session_id, [])

        if not history:
            return {
                "total_segments": 0,
                "agent_segments": 0,
                "customer_segments": 0,
                "average_confidence": 0.0,
                "total_words": 0
            }

        agent_count = sum(1 for s in history if s.speaker == SpeakerRole.AGENT)
        customer_count = sum(1 for s in history if s.speaker == SpeakerRole.CUSTOMER)
        avg_confidence = sum(s.confidence for s in history) / len(history)
        total_words = sum(len(s.text.split()) for s in history)

        return {
            "total_segments": len(history),
            "agent_segments": agent_count,
            "customer_segments": customer_count,
            "average_confidence": round(avg_confidence, 3),
            "total_words": total_words
        }


# Singleton instance
_transcription_service: TranscriptionService | None = None


def get_transcription_service() -> TranscriptionService:
    """Get singleton transcription service instance.

    Returns:
        TranscriptionService instance
    """
    global _transcription_service
    if _transcription_service is None:
        _transcription_service = TranscriptionService()
    return _transcription_service
