"""AI Insights models for storing conversation analysis results."""

from datetime import UTC, datetime
from enum import Enum
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel
from sqlalchemy import JSON, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base

if TYPE_CHECKING:
    pass


class IntentCategory(str, Enum):
    """Intent categories for customer interactions."""

    INQUIRY = "inquiry"
    COMPLAINT = "complaint"
    PURCHASE = "purchase"
    SUPPORT = "support"
    BILLING = "billing"
    TECHNICAL = "technical"
    CANCELLATION = "cancellation"
    FEEDBACK = "feedback"
    GENERAL = "general"


class SentimentScore(str, Enum):
    """Sentiment classifications."""

    VERY_POSITIVE = "very_positive"
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    VERY_NEGATIVE = "very_negative"


class UrgencyLevel(str, Enum):
    """Urgency levels for customer requests."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ConversationInsights(Base):
    """AI insights for conversation analysis."""

    __tablename__ = "conversation_insights"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(
        String(255), ForeignKey("call_sessions.session_id"), nullable=False, index=True
    )

    # Intent analysis
    intent = Column(String(100), nullable=False)
    intent_category = Column(String(50), nullable=False)
    intent_confidence = Column(Float, nullable=False)
    intent_keywords = Column(JSON, default=list, nullable=False)
    intent_context = Column(Text, nullable=True)
    intent_urgency = Column(String(20), nullable=False)

    # Sentiment analysis
    sentiment_score = Column(String(20), nullable=False)
    sentiment_confidence = Column(Float, nullable=False)
    sentiment_emotions = Column(JSON, default=list, nullable=False)
    sentiment_key_phrases = Column(JSON, default=list, nullable=False)
    sentiment_trajectory = Column(JSON, default=list, nullable=False)

    # Conversation metrics
    clarity_score = Column(Float, nullable=False)
    engagement_score = Column(Float, nullable=False)
    resolution_probability = Column(Float, nullable=False)
    customer_satisfaction_prediction = Column(Float, nullable=False)
    handling_time_estimate = Column(Integer, nullable=False)
    complexity_score = Column(Float, nullable=False)

    # Generated content
    summary = Column(Text, nullable=True)
    key_topics = Column(JSON, default=list, nullable=False)
    action_items = Column(JSON, default=list, nullable=False)

    # Metadata
    ai_providers_used = Column(JSON, default=list, nullable=False)
    processing_time_ms = Column(Float, nullable=True)
    model_versions = Column(JSON, default=dict, nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    # Relationships
    session = relationship("CallSession", back_populates="insights")
    suggestions = relationship("AgentSuggestion", back_populates="insight", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<ConversationInsights(id={self.id}, session_id={self.session_id}, intent={self.intent})>"


class AgentSuggestion(Base):
    """AI-generated suggestions for agents."""

    __tablename__ = "agent_suggestions"

    id = Column(Integer, primary_key=True, index=True)
    insight_id = Column(Integer, ForeignKey("conversation_insights.id"), nullable=False)

    # Suggestion details
    suggestion_type = Column(String(50), nullable=False)  # response, action, escalation
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    priority = Column(String(20), nullable=False)  # high, medium, low
    confidence = Column(Float, nullable=False)
    reasoning = Column(Text, nullable=True)
    suggested_response = Column(Text, nullable=True)

    # Status
    status = Column(
        String(20), default="pending", nullable=False
    )  # pending, accepted, rejected, implemented
    agent_feedback = Column(Text, nullable=True)
    implemented_at = Column(DateTime, nullable=True)

    # Metadata
    ai_provider = Column(String(50), nullable=True)
    model_version = Column(String(50), nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    # Relationships
    insight = relationship("ConversationInsights", back_populates="suggestions")

    def __repr__(self):
        return f"<AgentSuggestion(id={self.id}, type={self.suggestion_type}, priority={self.priority})>"


class ConversationTranscript(Base):
    """Complete conversation transcripts with metadata."""

    __tablename__ = "conversation_transcripts"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(
        String(255), ForeignKey("call_sessions.session_id"), nullable=False, index=True
    )

    # Transcript content
    raw_transcript = Column(Text, nullable=False)
    formatted_transcript = Column(Text, nullable=True)
    speaker_labels = Column(JSON, default=list, nullable=False)
    timestamps = Column(JSON, default=list, nullable=False)

    # Quality metrics
    word_count = Column(Integer, nullable=False)
    speaker_count = Column(Integer, nullable=False)
    language_detected = Column(String(10), nullable=True)
    confidence_score = Column(Float, nullable=True)

    # Processing info
    transcription_provider = Column(String(50), nullable=True)
    processing_time_ms = Column(Float, nullable=True)

    # Metadata
    transcript_custom_metadata = Column("metadata", JSON, default=dict, nullable=False)
    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    # Relationships
    session = relationship("CallSession", back_populates="transcripts")

    def __repr__(self):
        return f"<ConversationTranscript(id={self.id}, session_id={self.session_id}, words={self.word_count})>"


# Pydantic models for API
class ConversationInsightsBase(BaseModel):
    """Base conversation insights model."""

    intent: str
    intent_category: IntentCategory
    intent_confidence: float
    intent_keywords: list[str]
    intent_context: str | None = None
    intent_urgency: UrgencyLevel
    sentiment_score: SentimentScore
    sentiment_confidence: float
    sentiment_emotions: list[dict[str, float]]
    sentiment_key_phrases: list[str]
    sentiment_trajectory: list[float]
    clarity_score: float
    engagement_score: float
    resolution_probability: float
    customer_satisfaction_prediction: float
    handling_time_estimate: int
    complexity_score: float
    summary: str | None = None
    key_topics: list[str]
    action_items: list[str]


class ConversationInsightsCreate(ConversationInsightsBase):
    """Conversation insights creation model."""

    session_id: str
    ai_providers_used: list[str]
    processing_time_ms: float | None = None
    model_versions: dict[str, str] = {}


class ConversationInsightsResponse(ConversationInsightsBase):
    """Conversation insights response model."""

    id: int
    session_id: str
    ai_providers_used: list[str]
    processing_time_ms: float | None = None
    model_versions: dict[str, str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AgentSuggestionBase(BaseModel):
    """Base agent suggestion model."""

    suggestion_type: str
    title: str
    description: str
    priority: str
    confidence: float
    reasoning: str | None = None
    suggested_response: str | None = None


class AgentSuggestionCreate(AgentSuggestionBase):
    """Agent suggestion creation model."""

    insight_id: int
    ai_provider: str | None = None
    model_version: str | None = None


class AgentSuggestionResponse(AgentSuggestionBase):
    """Agent suggestion response model."""

    id: int
    insight_id: int
    status: str
    agent_feedback: str | None = None
    implemented_at: datetime | None = None
    ai_provider: str | None = None
    model_version: str | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ConversationTranscriptBase(BaseModel):
    """Base conversation transcript model."""

    raw_transcript: str
    formatted_transcript: str | None = None
    speaker_labels: list[dict[str, Any]]
    timestamps: list[dict[str, Any]]
    word_count: int
    speaker_count: int
    language_detected: str | None = None
    confidence_score: float | None = None


class ConversationTranscriptCreate(ConversationTranscriptBase):
    """Conversation transcript creation model."""

    session_id: str
    transcription_provider: str | None = None
    processing_time_ms: float | None = None
    transcript_metadata: dict[str, Any] = {}


class ConversationTranscriptResponse(ConversationTranscriptBase):
    """Conversation transcript response model."""

    id: int
    session_id: str
    transcription_provider: str | None = None
    processing_time_ms: float | None = None
    transcript_metadata: dict[str, Any]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
