"""AI Insights Data Types

Shared dataclasses and types for AI insights service.
Separated to avoid circular imports.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any


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


class SentimentPolarity(str, Enum):
    """Sentiment polarity classifications."""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    MIXED = "mixed"


class EmotionType(str, Enum):
    """Emotion types for advanced sentiment analysis."""
    JOY = "joy"
    SADNESS = "sadness"
    ANGER = "anger"
    FEAR = "fear"
    SURPRISE = "surprise"
    DISGUST = "disgust"
    TRUST = "trust"
    ANTICIPATION = "anticipation"


class SuggestionType(str, Enum):
    """Types of agent suggestions."""
    RESPONSE_TEMPLATE = "response_template"
    KNOWLEDGE_BASE = "knowledge_base"
    ESCALATION = "escalation"
    FOLLOW_UP = "follow_up"
    PRODUCT_RECOMMENDATION = "product_recommendation"
    PROCESS_GUIDANCE = "process_guidance"
    SENTIMENT_AWARENESS = "sentiment_awareness"


class UrgencyLevel(str, Enum):
    """Urgency levels for customer requests."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class SentimentAnalysis:
    """Sentiment analysis result."""
    score: SentimentScore
    confidence: float
    emotions: list[dict[str, float]]
    key_phrases: list[str]
    sentiment_trajectory: list[float]  # Sentiment over time


@dataclass
class IntentAnalysis:
    """Intent analysis result."""
    intent: str
    category: IntentCategory
    confidence: float
    keywords: list[str]
    context: str
    urgency: UrgencyLevel


@dataclass
class AgentSuggestion:
    """Agent suggestion result."""
    type: str  # response, action, escalation
    title: str
    description: str
    priority: str  # high, medium, low
    confidence: float
    reasoning: str
    suggested_response: str | None = None


@dataclass
class ConversationMetrics:
    """Conversation quality metrics."""
    clarity_score: float  # 0-100
    engagement_score: float  # 0-100
    resolution_probability: float  # 0-100
    customer_satisfaction_prediction: float  # 0-100
    handling_time_estimate: int  # minutes
    complexity_score: float  # 0-100


@dataclass
class ConversationInsights:
    """Complete conversation insights."""
    session_id: str
    timestamp: datetime
    intent: IntentAnalysis
    sentiment: SentimentAnalysis
    suggestions: list[AgentSuggestion]
    metrics: ConversationMetrics
    summary: str
    key_topics: list[str]
    action_items: list[str]


@dataclass
class ConversationTranscript:
    """Conversation transcript with metadata."""
    session_id: str
    raw_transcript: str
    formatted_transcript: str | None = None
    speaker_labels: list[dict[str, Any]] | None = None
    timestamps: list[dict[str, Any]] | None = None
    word_count: int | None = None
    speaker_count: int | None = None
    language_detected: str | None = None
    confidence_score: float | None = None
    transcription_provider: str | None = None
    processing_time_ms: float | None = None
    transcript_metadata: dict[str, Any] | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
