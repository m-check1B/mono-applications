"""Real-time sentiment analysis service for AI-first call center.

This service provides intelligent emotion detection with:
- Real-time sentiment tracking
- Emotion classification
- Sentiment trend analysis
- Alert generation for negative sentiment
"""

import logging
from datetime import UTC, datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel

logger = logging.getLogger(__name__)


class SentimentScore(str, Enum):
    """Sentiment classification."""
    VERY_POSITIVE = "very_positive"
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    VERY_NEGATIVE = "very_negative"


class EmotionType(str, Enum):
    """Detected emotion types."""
    HAPPY = "happy"
    SATISFIED = "satisfied"
    NEUTRAL = "neutral"
    FRUSTRATED = "frustrated"
    ANGRY = "angry"
    CONFUSED = "confused"
    ANXIOUS = "anxious"


class SentimentAnalysis(BaseModel):
    """Sentiment analysis result."""
    id: str
    session_id: UUID
    sentiment: SentimentScore
    emotions: list[EmotionType]
    confidence: float  # 0-1
    polarity_score: float  # -1 to 1
    intensity: float  # 0-1
    timestamp: datetime
    text_analyzed: str
    speaker: str  # agent or customer

    class Config:
        json_schema_extra = {
            "example": {
                "id": "sent_123",
                "session_id": "550e8400-e29b-41d4-a716-446655440000",
                "sentiment": "negative",
                "emotions": ["frustrated", "anxious"],
                "confidence": 0.87,
                "polarity_score": -0.65,
                "intensity": 0.72,
                "timestamp": "2025-10-12T12:00:00Z",
                "text_analyzed": "I've been waiting for 3 weeks and still no resolution!",
                "speaker": "customer"
            }
        }


class SentimentTrend(BaseModel):
    """Sentiment trend over time."""
    session_id: UUID
    current_sentiment: SentimentScore
    average_polarity: float
    sentiment_changes: int
    is_improving: bool
    alert_level: str  # none, low, medium, high


class SentimentConfig(BaseModel):
    """Configuration for sentiment analysis."""
    enable_real_time: bool = True
    enable_emotions: bool = True
    alert_on_negative: bool = True
    negative_threshold: float = -0.5
    track_trends: bool = True


class SentimentService:
    """Real-time sentiment analysis service.

    Analyzes customer and agent sentiment in real-time to help
    agents respond appropriately and supervisors intervene when needed.
    """

    def __init__(self):
        """Initialize sentiment service."""
        self._active_sessions: dict[UUID, SentimentConfig] = {}
        self._sentiment_history: dict[UUID, list[SentimentAnalysis]] = {}
        self._alerts_generated: dict[UUID, list[dict]] = {}

    async def start_analysis(
        self,
        session_id: UUID,
        config: SentimentConfig
    ) -> None:
        """Start sentiment analysis for a session.

        Args:
            session_id: Session identifier
            config: Sentiment configuration
        """
        self._active_sessions[session_id] = config
        self._sentiment_history[session_id] = []
        self._alerts_generated[session_id] = []
        logger.info(f"Started sentiment analysis for session {session_id}")

    async def stop_analysis(self, session_id: UUID) -> None:
        """Stop sentiment analysis for a session.

        Args:
            session_id: Session identifier
        """
        if session_id in self._active_sessions:
            del self._active_sessions[session_id]
        logger.info(f"Stopped sentiment analysis for session {session_id}")

    async def analyze_text(
        self,
        session_id: UUID,
        text: str,
        speaker: str
    ) -> SentimentAnalysis | None:
        """Analyze sentiment of text in real-time.

        Args:
            session_id: Session identifier
            text: Text to analyze
            speaker: Who spoke (agent or customer)

        Returns:
            SentimentAnalysis if successful, None otherwise
        """
        config = self._active_sessions.get(session_id)
        if not config or not text.strip():
            return None

        # Perform sentiment analysis
        polarity_score = await self._calculate_polarity(text)
        sentiment = self._classify_sentiment(polarity_score)
        emotions = []

        if config.enable_emotions:
            emotions = await self._detect_emotions(text, polarity_score)

        confidence = await self._calculate_confidence(text, polarity_score)
        intensity = abs(polarity_score)

        analysis = SentimentAnalysis(
            id=f"sent_{len(self._sentiment_history.get(session_id, []))}",
            session_id=session_id,
            sentiment=sentiment,
            emotions=emotions,
            confidence=confidence,
            polarity_score=polarity_score,
            intensity=intensity,
            timestamp=datetime.now(UTC),
            text_analyzed=text[:200],  # Limit stored text
            speaker=speaker
        )

        # Store in history
        if session_id not in self._sentiment_history:
            self._sentiment_history[session_id] = []
        self._sentiment_history[session_id].append(analysis)

        # Check for alerts
        if config.alert_on_negative and speaker == "customer":
            if polarity_score < config.negative_threshold:
                await self._generate_alert(session_id, analysis)

        logger.debug(
            f"Analyzed sentiment for {session_id}: {sentiment} "
            f"(polarity: {polarity_score:.2f})"
        )

        return analysis

    async def _calculate_polarity(self, text: str) -> float:
        """Calculate sentiment polarity score.

        Args:
            text: Text to analyze

        Returns:
            Polarity score from -1 (very negative) to 1 (very positive)
        """
        # Placeholder sentiment analysis
        # In production, use proper NLP library (VADER, TextBlob, Transformers)

        text_lower = text.lower()

        # Simple word-based sentiment
        positive_words = [
            "great", "excellent", "happy", "satisfied", "thank", "perfect",
            "amazing", "wonderful", "fantastic", "good", "love", "appreciate"
        ]

        negative_words = [
            "bad", "terrible", "awful", "frustrated", "angry", "disappointed",
            "hate", "horrible", "worst", "never", "always", "problem", "issue",
            "upset", "annoyed", "poor", "useless"
        ]

        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)

        total_words = len(text.split())
        if total_words == 0:
            return 0.0

        # Calculate polarity
        polarity = (positive_count - negative_count) / max(total_words, 1)

        # Normalize to -1 to 1 range
        polarity = max(-1.0, min(1.0, polarity * 10))

        return round(polarity, 3)

    def _classify_sentiment(self, polarity: float) -> SentimentScore:
        """Classify sentiment based on polarity score.

        Args:
            polarity: Polarity score (-1 to 1)

        Returns:
            Sentiment classification
        """
        if polarity >= 0.5:
            return SentimentScore.VERY_POSITIVE
        elif polarity >= 0.15:
            return SentimentScore.POSITIVE
        elif polarity >= -0.15:
            return SentimentScore.NEUTRAL
        elif polarity >= -0.5:
            return SentimentScore.NEGATIVE
        else:
            return SentimentScore.VERY_NEGATIVE

    async def _detect_emotions(
        self,
        text: str,
        polarity: float
    ) -> list[EmotionType]:
        """Detect specific emotions in text.

        Args:
            text: Text to analyze
            polarity: Sentiment polarity

        Returns:
            List of detected emotions
        """
        emotions = []
        text_lower = text.lower()

        # Emotion detection based on keywords and polarity
        if polarity > 0.3:
            if any(word in text_lower for word in ["great", "excellent", "love"]):
                emotions.append(EmotionType.HAPPY)
            else:
                emotions.append(EmotionType.SATISFIED)

        elif polarity < -0.3:
            if any(word in text_lower for word in ["frustrated", "annoyed", "waiting"]):
                emotions.append(EmotionType.FRUSTRATED)
            if any(word in text_lower for word in ["angry", "furious", "unacceptable"]):
                emotions.append(EmotionType.ANGRY)

        elif -0.3 <= polarity <= 0.3:
            if any(word in text_lower for word in ["confused", "understand", "not sure"]):
                emotions.append(EmotionType.CONFUSED)
            elif any(word in text_lower for word in ["worried", "concerned", "anxious"]):
                emotions.append(EmotionType.ANXIOUS)
            else:
                emotions.append(EmotionType.NEUTRAL)

        return emotions if emotions else [EmotionType.NEUTRAL]

    async def _calculate_confidence(
        self,
        text: str,
        polarity: float
    ) -> float:
        """Calculate confidence in sentiment analysis.

        Args:
            text: Analyzed text
            polarity: Calculated polarity

        Returns:
            Confidence score (0-1)
        """
        # Higher confidence for:
        # - Longer texts
        # - Stronger polarity
        # - Clear sentiment indicators

        text_length = len(text.split())
        length_factor = min(1.0, text_length / 20.0)  # Max confidence at 20 words

        polarity_factor = abs(polarity)  # Stronger sentiment = higher confidence

        confidence = (length_factor + polarity_factor) / 2.0

        return round(min(confidence, 0.95), 2)  # Cap at 0.95

    async def _generate_alert(
        self,
        session_id: UUID,
        analysis: SentimentAnalysis
    ) -> None:
        """Generate alert for negative sentiment.

        Args:
            session_id: Session identifier
            analysis: Sentiment analysis that triggered alert
        """
        alert = {
            "id": f"alert_{len(self._alerts_generated.get(session_id, []))}",
            "session_id": str(session_id),
            "type": "negative_sentiment",
            "severity": "high" if analysis.polarity_score < -0.7 else "medium",
            "message": f"Customer sentiment is {analysis.sentiment.value}",
            "analysis": analysis.dict(),
            "timestamp": datetime.now(UTC).isoformat()
        }

        if session_id not in self._alerts_generated:
            self._alerts_generated[session_id] = []

        self._alerts_generated[session_id].append(alert)

        logger.warning(
            f"Negative sentiment alert for {session_id}: "
            f"{analysis.sentiment} (score: {analysis.polarity_score})"
        )

    async def get_sentiment_trend(
        self,
        session_id: UUID
    ) -> SentimentTrend | None:
        """Get sentiment trend analysis for a session.

        Args:
            session_id: Session identifier

        Returns:
            SentimentTrend if available, None otherwise
        """
        history = self._sentiment_history.get(session_id, [])

        if not history:
            return None

        # Calculate trend
        current_sentiment = history[-1].sentiment
        average_polarity = sum(a.polarity_score for a in history) / len(history)

        # Count sentiment changes
        sentiment_changes = 0
        for i in range(1, len(history)):
            if history[i].sentiment != history[i-1].sentiment:
                sentiment_changes += 1

        # Determine if improving
        is_improving = False
        if len(history) >= 3:
            recent_avg = sum(h.polarity_score for h in history[-3:]) / 3
            older_avg = sum(h.polarity_score for h in history[:-3]) / max(len(history) - 3, 1)
            is_improving = recent_avg > older_avg

        # Determine alert level
        if average_polarity < -0.5:
            alert_level = "high"
        elif average_polarity < -0.2:
            alert_level = "medium"
        elif average_polarity < 0:
            alert_level = "low"
        else:
            alert_level = "none"

        return SentimentTrend(
            session_id=session_id,
            current_sentiment=current_sentiment,
            average_polarity=round(average_polarity, 3),
            sentiment_changes=sentiment_changes,
            is_improving=is_improving,
            alert_level=alert_level
        )

    def get_sentiment_history(
        self,
        session_id: UUID,
        limit: int | None = None
    ) -> list[SentimentAnalysis]:
        """Get sentiment history for a session.

        Args:
            session_id: Session identifier
            limit: Maximum number of analyses to return

        Returns:
            List of sentiment analyses
        """
        history = self._sentiment_history.get(session_id, [])

        if limit:
            return history[-limit:]

        return history

    def get_alerts(self, session_id: UUID) -> list[dict]:
        """Get alerts for a session.

        Args:
            session_id: Session identifier

        Returns:
            List of alerts
        """
        return self._alerts_generated.get(session_id, [])


# Singleton instance
_sentiment_service: SentimentService | None = None


def get_sentiment_service() -> SentimentService:
    """Get singleton sentiment service instance.

    Returns:
        SentimentService instance
    """
    global _sentiment_service
    if _sentiment_service is None:
        _sentiment_service = SentimentService()
    return _sentiment_service
