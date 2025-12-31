"""Sentiment analysis models - SQLAlchemy 2.0"""
from datetime import datetime
from typing import Optional
import enum
from sqlalchemy import String, DateTime, Float, Boolean, ForeignKey, JSON, Text, Enum as SQLEnum, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class SentimentType(str, enum.Enum):
    """Sentiment classification"""
    POSITIVE = "POSITIVE"
    NEUTRAL = "NEUTRAL"
    NEGATIVE = "NEGATIVE"


class TrendType(str, enum.Enum):
    """Sentiment trend over time"""
    IMPROVING = "IMPROVING"
    DECLINING = "DECLINING"
    STABLE = "STABLE"


class EmotionType(str, enum.Enum):
    """Detected emotions"""
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


class ConversationPhase(str, enum.Enum):
    """Phase of conversation"""
    OPENING = "opening"
    MIDDLE = "middle"
    RESOLUTION = "resolution"
    CLOSING = "closing"


class UrgencyLevel(str, enum.Enum):
    """Urgency level"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SentimentAnalysis(Base):
    """Sentiment analysis record"""
    __tablename__ = "sentiment_analyses"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    call_id: Mapped[str] = mapped_column(ForeignKey("calls.id", ondelete="CASCADE"))
    session_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    transcript_id: Mapped[Optional[str]] = mapped_column(ForeignKey("call_transcripts.id", ondelete="SET NULL"), nullable=True)

    # Sentiment results
    overall: Mapped[SentimentType] = mapped_column(SQLEnum(SentimentType))
    confidence: Mapped[float] = mapped_column(Float)
    intensity: Mapped[float] = mapped_column(Float)  # 0.0 to 1.0
    trend: Mapped[Optional[TrendType]] = mapped_column(SQLEnum(TrendType), nullable=True)

    # Context
    conversation_phase: Mapped[Optional[ConversationPhase]] = mapped_column(SQLEnum(ConversationPhase), nullable=True)
    customer_type: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    call_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    urgency: Mapped[Optional[UrgencyLevel]] = mapped_column(SQLEnum(UrgencyLevel), nullable=True)

    # Analysis metadata
    text_analyzed: Mapped[str] = mapped_column(Text)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Additional data stored alongside the sentiment analysis
    metadata_payload: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)


    # Relationships
    call: Mapped["Call"] = relationship(back_populates="sentiment_analyses")
    transcript: Mapped[Optional["CallTranscript"]] = relationship()
    emotions: Mapped[list["SentimentEmotion"]] = relationship(back_populates="analysis", cascade="all, delete-orphan")
    triggers: Mapped[list["SentimentTrigger"]] = relationship(back_populates="analysis", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_sentiment_call_timestamp", "call_id", "timestamp"),
        Index("idx_sentiment_session", "session_id"),
        Index("idx_sentiment_overall", "overall"),
    )


class SentimentEmotion(Base):
    """Detected emotions in sentiment analysis"""
    __tablename__ = "sentiment_emotions"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    analysis_id: Mapped[str] = mapped_column(ForeignKey("sentiment_analyses.id", ondelete="CASCADE"))

    emotion: Mapped[EmotionType] = mapped_column(SQLEnum(EmotionType))
    score: Mapped[float] = mapped_column(Float)  # 0.0 to 1.0
    confidence: Mapped[float] = mapped_column(Float)  # 0.0 to 1.0

    # Relationships
    analysis: Mapped["SentimentAnalysis"] = relationship(back_populates="emotions")

    __table_args__ = (
        Index("idx_emotion_type", "emotion"),
    )


class SentimentTrigger(Base):
    """Keywords/phrases that triggered sentiment detection"""
    __tablename__ = "sentiment_triggers"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    analysis_id: Mapped[str] = mapped_column(ForeignKey("sentiment_analyses.id", ondelete="CASCADE"))

    keyword: Mapped[str] = mapped_column(String)
    context: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    impact_score: Mapped[float] = mapped_column(Float)  # How much it influenced sentiment

    # Relationships
    analysis: Mapped["SentimentAnalysis"] = relationship(back_populates="triggers")


class RealTimeSentiment(Base):
    """Real-time sentiment tracking for active calls"""
    __tablename__ = "real_time_sentiments"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    session_id: Mapped[str] = mapped_column(String, unique=True)
    call_id: Mapped[str] = mapped_column(ForeignKey("calls.id", ondelete="CASCADE"))

    # Current state
    current_sentiment: Mapped[SentimentType] = mapped_column(SQLEnum(SentimentType))
    current_confidence: Mapped[float] = mapped_column(Float)
    current_intensity: Mapped[float] = mapped_column(Float)
    trend: Mapped[TrendType] = mapped_column(SQLEnum(TrendType))

    # Session info
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    last_updated: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Historical data (stored as JSON)
    sentiment_history: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)  # List of sentiment snapshots
    alerts: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)  # Active alerts

    # Relationships
    call: Mapped["Call"] = relationship()

    __table_args__ = (
        Index("idx_realtime_session", "session_id"),
        Index("idx_realtime_active", "is_active"),
    )


class SentimentAlert(Base):
    """Sentiment alerts for supervisors"""
    __tablename__ = "sentiment_alerts"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    session_id: Mapped[str] = mapped_column(String)
    call_id: Mapped[str] = mapped_column(ForeignKey("calls.id", ondelete="CASCADE"))

    # Alert details
    alert_type: Mapped[str] = mapped_column(String)  # escalation, satisfaction, frustration, confusion
    severity: Mapped[str] = mapped_column(String)  # low, medium, high
    message: Mapped[str] = mapped_column(Text)

    # Timing
    triggered_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    acknowledged_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    acknowledged_by: Mapped[Optional[str]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    # Additional context captured when raising the alert
    metadata_payload: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)


    # Relationships
    call: Mapped["Call"] = relationship()

    __table_args__ = (
        Index("idx_alert_session", "session_id"),
        Index("idx_alert_severity", "severity"),
        Index("idx_alert_type", "alert_type"),
        Index("idx_alert_triggered", "triggered_at"),
    )
