"""Sentiment analysis schemas - Pydantic models"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from enum import Enum


class ConversationPhase(str, Enum):
    """Conversation phase"""
    OPENING = "opening"
    MIDDLE = "middle"
    RESOLUTION = "resolution"
    CLOSING = "closing"


class CustomerType(str, Enum):
    """Customer type"""
    NEW = "new"
    RETURNING = "returning"
    VIP = "vip"
    ESCALATED = "escalated"


class UrgencyLevel(str, Enum):
    """Urgency level"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SentimentType(str, Enum):
    """Sentiment classification"""
    POSITIVE = "POSITIVE"
    NEUTRAL = "NEUTRAL"
    NEGATIVE = "NEGATIVE"


class EmotionType(str, Enum):
    """Emotion types"""
    JOY = "JOY"
    SADNESS = "SADNESS"
    ANGER = "ANGER"
    FEAR = "FEAR"
    SURPRISE = "SURPRISE"
    DISGUST = "DISGUST"
    TRUST = "TRUST"
    ANTICIPATION = "ANTICIPATION"
    FRUSTRATION = "FRUSTRATION"
    SATISFACTION = "SATISFACTION"
    CONFUSION = "CONFUSION"
    EXCITEMENT = "EXCITEMENT"


class TrendType(str, Enum):
    """Trend type"""
    IMPROVING = "IMPROVING"
    DECLINING = "DECLINING"
    STABLE = "STABLE"


class SentimentContext(BaseModel):
    """Context for sentiment analysis"""
    conversation_phase: Optional[ConversationPhase] = None
    customer_type: Optional[CustomerType] = None
    call_reason: Optional[str] = None
    agent_performance: Optional[float] = Field(None, ge=0.0, le=1.0)
    urgency: Optional[UrgencyLevel] = None


class AnalyzeSentimentRequest(BaseModel):
    """Request to analyze sentiment"""
    text: str = Field(..., min_length=1, max_length=5000)
    call_id: str
    session_id: Optional[str] = None
    transcript_id: Optional[str] = None
    context: Optional[SentimentContext] = None


class BatchAnalyzeSentimentRequest(BaseModel):
    """Request to batch analyze sentiment"""
    analyses: List[AnalyzeSentimentRequest] = Field(..., min_length=1, max_length=10)


class EmotionResult(BaseModel):
    """Emotion detection result"""
    emotion: EmotionType
    score: float = Field(..., ge=0.0, le=1.0)
    confidence: float = Field(..., ge=0.0, le=1.0)


class TriggerResult(BaseModel):
    """Trigger keyword result"""
    keyword: str
    context: Optional[str] = None
    impact_score: float


class SentimentResult(BaseModel):
    """Sentiment analysis result"""
    id: str
    call_id: str
    session_id: Optional[str] = None
    transcript_id: Optional[str] = None
    overall: SentimentType
    confidence: float
    intensity: float
    trend: Optional[TrendType] = None
    emotions: List[EmotionResult]
    triggers: List[TriggerResult]
    timestamp: datetime
    metadata: Optional[dict] = Field(None, alias="metadata_payload")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class SentimentHistoryResponse(BaseModel):
    """Response for sentiment history"""
    history: List[SentimentResult]
    total: int
    has_more: bool


class RealTimeSentimentSnapshot(BaseModel):
    """Single real-time sentiment snapshot"""
    timestamp: datetime
    sentiment: SentimentType
    confidence: float
    intensity: float


class RealTimeSentimentResponse(BaseModel):
    """Real-time sentiment data"""
    session_id: str
    call_id: str
    current_sentiment: SentimentType
    current_confidence: float
    current_intensity: float
    trend: TrendType
    is_active: bool
    started_at: datetime
    last_updated: datetime
    sentiment_history: List[RealTimeSentimentSnapshot]
    alerts: List[dict]


class SentimentDistribution(BaseModel):
    """Sentiment distribution stats"""
    POSITIVE: int
    NEUTRAL: int
    NEGATIVE: int


class TrendDistribution(BaseModel):
    """Trend distribution stats"""
    IMPROVING: int
    DECLINING: int
    STABLE: int


class TopEmotion(BaseModel):
    """Top emotion with count"""
    emotion: str
    count: int


class DailyAnalytics(BaseModel):
    """Daily sentiment analytics"""
    date: str
    total: int
    positive: int
    neutral: int
    negative: int
    avg_confidence: float


class SentimentAnalyticsSummary(BaseModel):
    """Summary of sentiment analytics"""
    total_analyses: int
    avg_confidence: float
    avg_intensity: float
    date_range: dict


class SentimentAnalyticsResponse(BaseModel):
    """Full sentiment analytics response"""
    summary: SentimentAnalyticsSummary
    sentiment_distribution: SentimentDistribution
    trend_distribution: TrendDistribution
    top_emotions: List[TopEmotion]
    daily_analytics: List[DailyAnalytics]


class SentimentAlert(BaseModel):
    """Sentiment alert"""
    id: str
    session_id: str
    call_id: str
    alert_type: str  # escalation, satisfaction, frustration, confusion
    severity: str  # low, medium, high
    message: str
    triggered_at: datetime
    agent: Optional[str] = None
    customer_number: Optional[str] = None


class SentimentAlertsResponse(BaseModel):
    """Response for sentiment alerts"""
    alerts: List[SentimentAlert]
    total: int
    active_sessions_count: int


class ServiceHealth(BaseModel):
    """Service health status"""
    status: str
    active_sessions: int
    total_analyses_today: int
    average_response_time_ms: float
    error_rate: float
