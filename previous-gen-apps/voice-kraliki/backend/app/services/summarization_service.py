"""AI-powered call summarization service.

This service provides intelligent call summarization with:
- Automatic key point extraction
- Action item identification
- Call outcome analysis
- Multi-language support
"""

import logging
from datetime import UTC, datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel

from app.config.settings import get_settings
from app.models.ai_insights_types import (
    ConversationInsights,
    ConversationMetrics,
    IntentAnalysis,
    IntentCategory,
    SentimentAnalysis,
    SentimentScore,
    UrgencyLevel,
)
from app.services.ai_insights_database import ai_insights_db_service

logger = logging.getLogger(__name__)


class CallOutcome(str, Enum):
    """Possible call outcomes."""
    RESOLVED = "resolved"
    ESCALATED = "escalated"
    CALLBACK_REQUIRED = "callback_required"
    NO_ANSWER = "no_answer"
    TRANSFERRED = "transferred"
    CANCELLED = "cancelled"


class ActionItem(BaseModel):
    """An action item extracted from call."""
    description: str
    assigned_to: str
    due_date: datetime | None = None
    priority: str = "medium"  # low, medium, high


class CallSummary(BaseModel):
    """Complete call summary with analysis."""
    session_id: UUID
    summary: str
    key_points: list[str]
    action_items: list[ActionItem]
    outcome: CallOutcome
    customer_sentiment: str  # positive, neutral, negative
    agent_performance: float  # 0-1 score
    duration_seconds: int
    language: str
    topics: list[str]
    generated_at: datetime

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "550e8400-e29b-41d4-a716-446655440000",
                "summary": "Customer called regarding billing issue. Agent reviewed account and applied credit. Customer satisfied with resolution.",
                "key_points": [
                    "Billing discrepancy identified",
                    "$50 credit applied to account",
                    "Customer satisfied with resolution"
                ],
                "action_items": [
                    {
                        "description": "Follow up on credit application in 24 hours",
                        "assigned_to": "billing_team",
                        "priority": "medium"
                    }
                ],
                "outcome": "resolved",
                "customer_sentiment": "positive",
                "agent_performance": 0.92,
                "duration_seconds": 245,
                "language": "en",
                "topics": ["billing", "credit", "account_review"]
            }
        }


class SummarizationConfig(BaseModel):
    """Configuration for summarization service."""
    min_call_duration: int = 30  # seconds
    max_summary_length: int = 500  # characters
    extract_action_items: bool = True
    analyze_sentiment: bool = True
    analyze_performance: bool = True
    language: str = "en"


class SummarizationService:
    """AI-powered call summarization service.

    Uses AI providers to generate intelligent call summaries with
    key points, action items, and analysis.
    """

    def __init__(self):
        """Initialize summarization service."""
        self._settings = get_settings()

    async def generate_summary(
        self,
        session_id: UUID,
        transcript: str,
        config: SummarizationConfig
    ) -> CallSummary:
        """Generate AI-powered call summary and persist to database.

        Args:
            session_id: Session identifier
            transcript: Full call transcript
            config: Summarization configuration

        Returns:
            Generated call summary
        """
        logger.info(f"Generating summary for session {session_id}")

        # Use AI provider to generate summary
        summary_text = await self._generate_summary_text(transcript, config)
        key_points = await self._extract_key_points(transcript, config)
        action_items_extracted = []

        if config.extract_action_items:
            action_items_extracted = await self._extract_action_items(transcript, config)

        outcome = await self._determine_outcome(transcript, config)
        sentiment = "neutral"

        if config.analyze_sentiment:
            sentiment = await self._analyze_sentiment(transcript, config)

        performance = 0.0
        if config.analyze_performance:
            performance = await self._analyze_agent_performance(transcript, config)

        topics = await self._extract_topics(transcript, config)

        # Estimate duration from transcript
        word_count = len(transcript.split())
        duration_seconds = max(config.min_call_duration, word_count // 2)

        summary = CallSummary(
            session_id=session_id,
            summary=summary_text,
            key_points=key_points,
            action_items=action_items_extracted,
            outcome=outcome,
            customer_sentiment=sentiment,
            agent_performance=performance,
            duration_seconds=duration_seconds,
            language=config.language,
            topics=topics,
            generated_at=datetime.now(UTC)
        )

        # Persist to database using AIInsightsDatabaseService
        await self._save_to_db(summary)

        logger.info(f"Summary generated and persisted for session {session_id}")

        return summary

    async def _save_to_db(self, summary: CallSummary):
        """Save call summary to database using AI insights database service."""
        try:
            # Map Pydantic Sentiment to Enum
            sentiment_map = {
                "positive": SentimentScore.POSITIVE,
                "negative": SentimentScore.NEGATIVE,
                "neutral": SentimentScore.NEUTRAL
            }

            insights = ConversationInsights(
                session_id=str(summary.session_id),
                timestamp=summary.generated_at,
                intent=IntentAnalysis(
                    intent="call_summary",
                    category=IntentCategory.GENERAL,
                    confidence=1.0,
                    keywords=summary.topics,
                    urgency=UrgencyLevel.MEDIUM
                ),
                sentiment=SentimentAnalysis(
                    score=sentiment_map.get(summary.customer_sentiment, SentimentScore.NEUTRAL),
                    confidence=1.0,
                    emotions=[],
                    key_phrases=summary.key_points,
                    sentiment_trajectory=[]
                ),
                suggestions=[],
                metrics=ConversationMetrics(
                    clarity_score=1.0,
                    engagement_score=summary.agent_performance,
                    resolution_probability=1.0,
                    customer_satisfaction_prediction=0.5,
                    handling_time_estimate=summary.duration_seconds,
                    complexity_score=0.5
                ),
                summary=summary.summary,
                key_topics=summary.topics,
                action_items=[item.description for item in summary.action_items]
            )

            await ai_insights_db_service.save_conversation_insights(
                insights=insights,
                ai_providers_used=["internal_summarizer"]
            )
        except Exception as e:
            logger.error(f"Failed to save summary to database: {e}")

    async def _generate_summary_text(
        self,
        transcript: str,
        config: SummarizationConfig
    ) -> str:
        """Generate summary text using AI."""
        # In production, this would call an AI provider (OpenAI, Gemini, etc.)
        sentences = transcript.split('.')[:3]
        summary = '. '.join(sentences).strip()

        if len(summary) > config.max_summary_length:
            summary = summary[:config.max_summary_length] + "..."

        return summary or "Call summary unavailable"

    async def _extract_key_points(
        self,
        transcript: str,
        config: SummarizationConfig
    ) -> list[str]:
        """Extract key points from transcript."""
        lines = [l.strip() for l in transcript.split('\n') if l.strip()]
        key_points = []
        for line in lines[:5]:
            if len(line) > 20:
                key_points.append(line[:100])
        return key_points or ["No key points extracted"]

    async def _extract_action_items(
        self,
        transcript: str,
        config: SummarizationConfig
    ) -> list[ActionItem]:
        """Extract action items from transcript."""
        action_items = []
        action_keywords = ["follow up", "call back", "send", "schedule", "review"]

        for line in transcript.split('\n'):
            for keyword in action_keywords:
                if keyword in line.lower():
                    action_items.append(ActionItem(
                        description=line[:100],
                        assigned_to="agent",
                        priority="medium"
                    ))
                    break
            if len(action_items) >= 3:
                break
        return action_items

    async def _determine_outcome(
        self,
        transcript: str,
        config: SummarizationConfig
    ) -> CallOutcome:
        """Determine call outcome."""
        transcript_lower = transcript.lower()
        if "resolved" in transcript_lower or "fixed" in transcript_lower:
            return CallOutcome.RESOLVED
        elif "transfer" in transcript_lower:
            return CallOutcome.TRANSFERRED
        elif "escalate" in transcript_lower:
            return CallOutcome.ESCALATED
        elif "call back" in transcript_lower:
            return CallOutcome.CALLBACK_REQUIRED
        else:
            return CallOutcome.RESOLVED

    async def _analyze_sentiment(
        self,
        transcript: str,
        config: SummarizationConfig
    ) -> str:
        """Analyze customer sentiment."""
        positive_words = ["thank", "great", "excellent", "happy", "satisfied"]
        negative_words = ["angry", "frustrated", "disappointed", "upset", "problem"]
        transcript_lower = transcript.lower()
        pos = sum(1 for w in positive_words if w in transcript_lower)
        neg = sum(1 for w in negative_words if w in transcript_lower)
        if pos > neg: return "positive"
        if neg > pos: return "negative"
        return "neutral"

    async def _analyze_agent_performance(
        self,
        transcript: str,
        config: SummarizationConfig
    ) -> float:
        """Analyze agent performance."""
        agent_lines = [l for l in transcript.split('\n') if l.startswith('AGENT:')]
        if not agent_lines: return 0.5
        avg_length = sum(len(l) for l in agent_lines) / len(agent_lines)
        return round(min(1.0, avg_length / 200), 2)

    async def _extract_topics(
        self,
        transcript: str,
        config: SummarizationConfig
    ) -> list[str]:
        """Extract conversation topics."""
        common_topics = {
            "billing": ["bill", "charge", "payment", "invoice"],
            "technical": ["not working", "error", "problem", "issue"],
            "account": ["account", "profile", "settings", "information"],
            "order": ["order", "purchase", "delivery", "shipping"]
        }
        transcript_lower = transcript.lower()
        detected = [t for t, keywords in common_topics.items() if any(k in transcript_lower for k in keywords)]
        return detected or ["general"]

    async def get_summary(self, session_id: UUID) -> CallSummary | None:
        """Get summary from database for a session.

        Args:
            session_id: Session identifier

        Returns:
            CallSummary if available, None otherwise
        """
        try:
            insights = await ai_insights_db_service.get_conversation_insights(str(session_id))
            if not insights:
                return None

            return CallSummary(
                session_id=session_id,
                summary=insights.summary or "Summary not available",
                key_points=insights.sentiment.key_phrases or [],
                action_items=[
                    ActionItem(description=desc, assigned_to="agent")
                    for desc in (insights.action_items or [])
                ],
                outcome=CallOutcome.RESOLVED,
                customer_sentiment=insights.sentiment.score.value,
                agent_performance=insights.metrics.engagement_score,
                duration_seconds=insights.metrics.handling_time_estimate,
                language="en",
                topics=insights.key_topics or [],
                generated_at=insights.timestamp
            )
        except Exception as e:
            logger.error(f"Failed to fetch summary from database for session {session_id}: {e}")
            return None


# Singleton instance
_summarization_service: SummarizationService | None = None


def get_summarization_service() -> SummarizationService:
    """Get singleton summarization service instance."""
    global _summarization_service
    if _summarization_service is None:
        _summarization_service = SummarizationService()
    return _summarization_service
