"""Database service for persisting AI insights and conversation analysis."""

import logging
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.ai_insights import (
    AgentSuggestion as AgentSuggestionModel,
)
from app.models.ai_insights import (
    ConversationInsights as ConversationInsightsModel,
)
from app.models.ai_insights import (
    ConversationTranscript as ConversationTranscriptModel,
)
from app.models.ai_insights_types import (
    AgentSuggestion,
    ConversationInsights,
    ConversationMetrics,
    ConversationTranscript,
    IntentAnalysis,
    IntentCategory,
    SentimentAnalysis,
    SentimentScore,
    UrgencyLevel,
)

logger = logging.getLogger(__name__)


class AIInsightsDatabaseService:
    """Service for persisting and retrieving AI insights from database."""

    def __init__(self, session_factory: Callable[[], Session] | None = None):
        """Initialize the database service."""
        self._session_factory = session_factory or SessionLocal

    @contextmanager
    def _session(self) -> Iterator[Session]:
        """Provide a managed database session."""
        session = self._session_factory()
        try:
            yield session
        finally:
            session.close()

    async def save_conversation_insights(
        self,
        insights: ConversationInsights,
        ai_providers_used: list[str],
        processing_time_ms: float | None = None,
        model_versions: dict[str, str] = None
    ) -> int:
        """Save conversation insights to database.
        
        Args:
            insights: Conversation insights to save
            ai_providers_used: List of AI providers used
            processing_time_ms: Processing time in milliseconds
            model_versions: Dictionary of model versions used
            
        Returns:
            ID of the saved insights record
        """
        try:
            with self._session() as session:
                # Create insights record
                db_insights = ConversationInsightsModel(
                    session_id=insights.session_id,
                    intent=insights.intent.intent,
                    intent_category=insights.intent.category.value,
                    intent_confidence=insights.intent.confidence,
                    intent_keywords=insights.intent.keywords,
                    intent_context=insights.intent.context,
                    intent_urgency=insights.intent.urgency.value,
                    sentiment_score=insights.sentiment.score.value,
                    sentiment_confidence=insights.sentiment.confidence,
                    sentiment_emotions=insights.sentiment.emotions,
                    sentiment_key_phrases=insights.sentiment.key_phrases,
                    sentiment_trajectory=insights.sentiment.sentiment_trajectory,
                    clarity_score=insights.metrics.clarity_score,
                    engagement_score=insights.metrics.engagement_score,
                    resolution_probability=insights.metrics.resolution_probability,
                    customer_satisfaction_prediction=insights.metrics.customer_satisfaction_prediction,
                    handling_time_estimate=insights.metrics.handling_time_estimate,
                    complexity_score=insights.metrics.complexity_score,
                    summary=insights.summary,
                    key_topics=insights.key_topics,
                    action_items=insights.action_items,
                    ai_providers_used=ai_providers_used,
                    processing_time_ms=processing_time_ms,
                    model_versions=model_versions or {},
                    created_at=insights.timestamp,
                    updated_at=insights.timestamp,
                )

                session.add(db_insights)
                session.commit()
                session.refresh(db_insights)

                # Save agent suggestions
                for suggestion in insights.suggestions:
                    db_suggestion = AgentSuggestionModel(
                        insight_id=db_insights.id,
                        suggestion_type=suggestion.type,
                        title=suggestion.title,
                        description=suggestion.description,
                        priority=suggestion.priority,
                        confidence=suggestion.confidence,
                        reasoning=suggestion.reasoning,
                        suggested_response=suggestion.suggested_response,
                        ai_provider=ai_providers_used[0] if ai_providers_used else None,
                        model_version=model_versions.get("primary") if model_versions else None,
                    )
                    session.add(db_suggestion)

                session.commit()

                logger.info(
                    "Saved insights for session %s with ID %s",
                    insights.session_id,
                    db_insights.id,
                )
                return db_insights.id

        except Exception as e:
            logger.error("Error saving conversation insights: %s", e)
            raise

    async def get_conversation_insights(
        self,
        session_id: str
    ) -> ConversationInsights | None:
        """Get conversation insights by session ID.
        
        Args:
            session_id: Session ID to retrieve insights for
            
        Returns:
            Conversation insights or None if not found
        """
        try:
            with self._session() as session:
                db_insights = (
                    session.query(ConversationInsightsModel)
                    .filter(ConversationInsightsModel.session_id == session_id)
                    .first()
                )

                if not db_insights:
                    return None

                # Get agent suggestions
                suggestions = (
                    session.query(AgentSuggestionModel)
                    .filter(AgentSuggestionModel.insight_id == db_insights.id)
                    .all()
                )

                # Convert to domain objects
                intent = IntentAnalysis(
                    intent=db_insights.intent,
                    category=IntentCategory(db_insights.intent_category),
                    confidence=db_insights.intent_confidence,
                    keywords=db_insights.intent_keywords,
                    context=db_insights.intent_context,
                    urgency=UrgencyLevel(db_insights.intent_urgency),
                )

                sentiment = SentimentAnalysis(
                    score=SentimentScore(db_insights.sentiment_score),
                    confidence=db_insights.sentiment_confidence,
                    emotions=db_insights.sentiment_emotions,
                    key_phrases=db_insights.sentiment_key_phrases,
                    sentiment_trajectory=db_insights.sentiment_trajectory,
                )

                metrics = ConversationMetrics(
                    clarity_score=db_insights.clarity_score,
                    engagement_score=db_insights.engagement_score,
                    resolution_probability=db_insights.resolution_probability,
                    customer_satisfaction_prediction=db_insights.customer_satisfaction_prediction,
                    handling_time_estimate=db_insights.handling_time_estimate,
                    complexity_score=db_insights.complexity_score,
                )

                agent_suggestions = [
                    AgentSuggestion(
                        type=s.suggestion_type,
                        title=s.title,
                        description=s.description,
                        priority=s.priority,
                        confidence=s.confidence,
                        reasoning=s.reasoning,
                        suggested_response=s.suggested_response,
                    )
                    for s in suggestions
                ]

                return ConversationInsights(
                    session_id=db_insights.session_id,
                    timestamp=db_insights.created_at,
                    intent=intent,
                    sentiment=sentiment,
                    suggestions=agent_suggestions,
                    metrics=metrics,
                    summary=db_insights.summary,
                    key_topics=db_insights.key_topics,
                    action_items=db_insights.action_items,
                )

        except Exception as e:
            logger.error(
                "Error retrieving conversation insights for %s: %s", session_id, e
            )
            return None

    async def save_conversation_transcript(
        self,
        session_id: str,
        raw_transcript: str,
        formatted_transcript: str | None = None,
        speaker_labels: list[dict[str, Any]] = None,
        timestamps: list[dict[str, Any]] = None,
        word_count: int | None = None,
        speaker_count: int | None = None,
        language_detected: str | None = None,
        confidence_score: float | None = None,
        transcription_provider: str | None = None,
        processing_time_ms: float | None = None,
        transcript_metadata: dict[str, Any] = None
    ) -> int:
        """Save conversation transcript to database.
        
        Args:
            session_id: Session ID
            raw_transcript: Raw transcript text
            formatted_transcript: Formatted transcript with speaker labels
            speaker_labels: List of speaker label information
            timestamps: List of timestamp information
            word_count: Total word count
            speaker_count: Number of speakers
            language_detected: Detected language
            confidence_score: Transcription confidence score
            transcription_provider: Provider used for transcription
            processing_time_ms: Processing time in milliseconds
            transcript_metadata: Additional metadata
            
        Returns:
            ID of the saved transcript record
        """
        try:
            if word_count is None:
                word_count = len(raw_transcript.split())

            if speaker_count is None:
                speaker_count = 1

            db_transcript = ConversationTranscriptModel(
                session_id=session_id,
                raw_transcript=raw_transcript,
                formatted_transcript=formatted_transcript,
                speaker_labels=speaker_labels or [],
                timestamps=timestamps or [],
                word_count=word_count,
                speaker_count=speaker_count,
                language_detected=language_detected,
                confidence_score=confidence_score,
                transcription_provider=transcription_provider,
                processing_time_ms=processing_time_ms,
                transcript_metadata=transcript_metadata or {},
            )

            with self._session() as session:
                session.add(db_transcript)
                session.commit()
                session.refresh(db_transcript)

            logger.info(
                "Saved transcript for session %s with ID %s",
                session_id,
                db_transcript.id,
            )
            return db_transcript.id

        except Exception as e:
            logger.error("Error saving conversation transcript: %s", e)
            raise

    async def get_conversation_transcript(
        self,
        session_id: str
    ) -> ConversationTranscript | None:
        """Get conversation transcript by session ID.
        
        Args:
            session_id: Session ID to retrieve transcript for
            
        Returns:
            Conversation transcript or None if not found
        """
        try:
            with self._session() as session:
                db_transcript = (
                    session.query(ConversationTranscriptModel)
                    .filter(ConversationTranscriptModel.session_id == session_id)
                    .first()
                )

                if not db_transcript:
                    return None

                return ConversationTranscript(
                    session_id=db_transcript.session_id,
                    raw_transcript=db_transcript.raw_transcript,
                    formatted_transcript=db_transcript.formatted_transcript,
                    speaker_labels=db_transcript.speaker_labels,
                    timestamps=db_transcript.timestamps,
                    word_count=db_transcript.word_count,
                    speaker_count=db_transcript.speaker_count,
                    language_detected=db_transcript.language_detected,
                    confidence_score=db_transcript.confidence_score,
                    transcription_provider=db_transcript.transcription_provider,
                    processing_time_ms=db_transcript.processing_time_ms,
                    transcript_metadata=db_transcript.transcript_metadata,
                    created_at=db_transcript.created_at,
                    updated_at=db_transcript.updated_at,
                )

        except Exception as e:
            logger.error(
                "Error retrieving conversation transcript for %s: %s", session_id, e
            )
            return None

    async def update_agent_suggestion_status(
        self,
        suggestion_id: int,
        status: str,
        agent_feedback: str | None = None
    ) -> bool:
        """Update agent suggestion status.
        
        Args:
            suggestion_id: ID of the suggestion to update
            status: New status (pending, accepted, rejected, implemented)
            agent_feedback: Optional feedback from agent
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with self._session() as session:
                suggestion = (
                    session.query(AgentSuggestionModel)
                    .filter(AgentSuggestionModel.id == suggestion_id)
                    .first()
                )

                if not suggestion:
                    return False

                suggestion.status = status
                suggestion.agent_feedback = agent_feedback

                if status == "implemented":
                    suggestion.implemented_at = datetime.now(UTC)

                session.commit()

            logger.info("Updated suggestion %s status to %s", suggestion_id, status)
            return True

        except Exception as e:
            logger.error("Error updating agent suggestion status: %s", e)
            return False

    async def get_insights_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime,
        limit: int = 100
    ) -> list[ConversationInsights]:
        """Get conversation insights within a date range.
        
        Args:
            start_date: Start date for filtering
            end_date: End date for filtering
            limit: Maximum number of results to return
            
        Returns:
            List of conversation insights
        """
        try:
            with self._session() as session:
                db_insights = (
                    session.query(ConversationInsightsModel)
                    .filter(
                        ConversationInsightsModel.created_at >= start_date,
                        ConversationInsightsModel.created_at <= end_date,
                    )
                    .order_by(desc(ConversationInsightsModel.created_at))
                    .limit(limit)
                    .all()
                )

            results: list[ConversationInsights] = []
            for db_insight in db_insights:
                insights = await self.get_conversation_insights(db_insight.session_id)
                if insights:
                    results.append(insights)

            return results

        except Exception as e:
            logger.error("Error retrieving insights by date range: %s", e)
            return []

    async def get_agent_suggestions_by_status(
        self,
        status: str,
        limit: int = 50
    ) -> list[AgentSuggestion]:
        """Get agent suggestions by status.
        
        Args:
            status: Status to filter by
            limit: Maximum number of results to return
            
        Returns:
            List of agent suggestions
        """
        try:
            with self._session() as session:
                db_suggestions = (
                    session.query(AgentSuggestionModel)
                    .filter(AgentSuggestionModel.status == status)
                    .order_by(desc(AgentSuggestionModel.created_at))
                    .limit(limit)
                    .all()
                )

            return [
                AgentSuggestion(
                    type=s.suggestion_type,
                    title=s.title,
                    description=s.description,
                    priority=s.priority,
                    confidence=s.confidence,
                    reasoning=s.reasoning,
                    suggested_response=s.suggested_response,
                )
                for s in db_suggestions
            ]

        except Exception as e:
            logger.error("Error retrieving agent suggestions by status: %s", e)
            return []

    def close(self):
        """No-op retained for backwards compatibility."""
        return None


# Global instance
ai_insights_db_service = AIInsightsDatabaseService()
