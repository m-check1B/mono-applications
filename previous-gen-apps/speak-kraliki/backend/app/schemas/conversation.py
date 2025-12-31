"""
Speak by Kraliki - Conversation Schemas
"""

from datetime import datetime
from uuid import UUID
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field


class TranscriptTurn(BaseModel):
    """Single turn in conversation transcript."""
    role: str = Field(pattern="^(ai|user)$")
    content: str
    timestamp: datetime
    redacted: bool = False


class ConversationStart(BaseModel):
    """Start conversation request."""
    mode: str = Field(default="voice", pattern="^(voice|text)$")
    consent_given: bool = True


class ConversationMessage(BaseModel):
    """Send message in conversation."""
    content: str
    is_audio: bool = False
    audio_data: str | None = None  # Base64 encoded audio


class ConversationComplete(BaseModel):
    """Complete conversation request (Reach voice)."""
    transcript: list[TranscriptTurn]
    duration_seconds: int | None = None


class RedactRequest(BaseModel):
    """Request to redact parts of transcript."""
    turn_indices: list[int]


class ConversationResponse(BaseModel):
    """Conversation response schema."""
    id: UUID
    survey_id: UUID
    employee_id: UUID
    status: str
    invited_at: datetime | None
    started_at: datetime | None
    completed_at: datetime | None
    duration_seconds: int | None
    transcript: list[TranscriptTurn] | None
    transcript_reviewed_by_employee: bool
    fallback_to_text: bool
    sentiment_score: Decimal | None
    topics: list[str] | None
    flags: list[str] | None
    summary: str | None
    anonymous_id: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ConversationEmployeeView(BaseModel):
    """Conversation view for employee (transcript review)."""
    id: UUID
    status: str
    started_at: datetime | None
    completed_at: datetime | None
    duration_seconds: int | None
    transcript: list[TranscriptTurn] | None
    transcript_reviewed_by_employee: bool

    model_config = ConfigDict(from_attributes=True)


class AIResponse(BaseModel):
    """AI response to employee."""
    message: str
    audio_url: str | None = None
    is_final: bool = False
    next_question_id: int | None = None
