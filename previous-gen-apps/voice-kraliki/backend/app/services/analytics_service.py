"""Analytics Service

Comprehensive analytics and metrics tracking:
- Call metrics (duration, success rate, outcomes)
- Agent performance tracking
- Provider performance comparison
- Real-time and historical analytics
- Aggregated insights
"""

import logging
from collections import defaultdict
from datetime import UTC, datetime, timedelta
from enum import Enum
from uuid import UUID

from pydantic import BaseModel

logger = logging.getLogger(__name__)


class CallOutcome(str, Enum):
    """Call outcome types."""
    COMPLETED = "completed"
    FAILED = "failed"
    ABANDONED = "abandoned"
    TRANSFERRED = "transferred"
    VOICEMAIL = "voicemail"


class CallMetric(BaseModel):
    """Individual call metrics."""
    call_id: UUID
    session_id: UUID
    start_time: datetime
    end_time: datetime | None = None
    duration_seconds: float = 0.0
    outcome: CallOutcome
    provider_id: str
    agent_id: str | None = None

    # Quality metrics
    average_sentiment: float = 0.0  # -1 to 1
    transcription_accuracy: float = 0.0  # 0 to 1
    audio_quality_score: float = 0.0  # 0 to 100

    # Interaction metrics
    agent_messages: int = 0
    customer_messages: int = 0
    ai_suggestions_used: int = 0
    compliance_warnings: int = 0

    # Metadata
    tags: list[str] = []
    notes: str | None = None


class AgentPerformance(BaseModel):
    """Agent performance metrics."""
    agent_id: str
    total_calls: int
    completed_calls: int
    failed_calls: int
    average_call_duration: float
    average_sentiment: float
    total_suggestions_used: int
    compliance_warnings: int
    quality_score: float  # 0 to 100


class ProviderPerformance(BaseModel):
    """Provider performance metrics."""
    provider_id: str
    total_calls: int
    successful_calls: int
    failed_calls: int
    average_latency_ms: float
    average_audio_quality: float
    uptime_percentage: float
    error_rate: float


class TimeSeriesDataPoint(BaseModel):
    """Time series data point."""
    timestamp: datetime
    value: float
    label: str | None = None


class AnalyticsSummary(BaseModel):
    """Aggregated analytics summary."""
    period_start: datetime
    period_end: datetime

    # Call metrics
    total_calls: int
    completed_calls: int
    failed_calls: int
    average_call_duration: float
    success_rate: float

    # Quality metrics
    average_sentiment: float
    average_audio_quality: float
    average_transcription_accuracy: float

    # Provider metrics
    provider_performance: dict[str, ProviderPerformance]

    # Agent metrics
    agent_performance: dict[str, AgentPerformance]

    # Time series data
    calls_over_time: list[TimeSeriesDataPoint]
    sentiment_over_time: list[TimeSeriesDataPoint]
    quality_over_time: list[TimeSeriesDataPoint]


class AnalyticsService:
    """Real-time analytics and metrics tracking service.

    Tracks all call metrics, agent performance, provider performance,
    and provides aggregated analytics for dashboards and reporting.
    """

    def __init__(self):
        """Initialize analytics service."""
        # Call metrics storage
        self._call_metrics: dict[UUID, CallMetric] = {}

        # Active calls tracking
        self._active_calls: set[UUID] = set()

        # Agent performance tracking
        self._agent_metrics: dict[str, list[UUID]] = defaultdict(list)

        # Provider performance tracking
        self._provider_metrics: dict[str, list[UUID]] = defaultdict(list)

        # Time series data
        self._calls_timeline: list[TimeSeriesDataPoint] = []
        self._sentiment_timeline: list[TimeSeriesDataPoint] = []
        self._quality_timeline: list[TimeSeriesDataPoint] = []

    async def start_call_tracking(
        self,
        call_id: UUID,
        session_id: UUID,
        provider_id: str,
        agent_id: str | None = None
    ) -> CallMetric:
        """Start tracking a new call.

        Args:
            call_id: Call identifier
            session_id: Session identifier
            provider_id: Provider being used
            agent_id: Optional agent identifier

        Returns:
            Initial call metric
        """
        metric = CallMetric(
            call_id=call_id,
            session_id=session_id,
            start_time=datetime.now(UTC),
            outcome=CallOutcome.COMPLETED,  # Default, will be updated
            provider_id=provider_id,
            agent_id=agent_id
        )

        self._call_metrics[call_id] = metric
        self._active_calls.add(call_id)

        if agent_id:
            self._agent_metrics[agent_id].append(call_id)

        self._provider_metrics[provider_id].append(call_id)

        logger.info(f"Started tracking call {call_id}")
        return metric

    async def update_call_metric(
        self,
        call_id: UUID,
        **updates
    ) -> CallMetric | None:
        """Update call metrics.

        Args:
            call_id: Call identifier
            **updates: Fields to update

        Returns:
            Updated call metric if found
        """
        metric = self._call_metrics.get(call_id)
        if not metric:
            logger.warning(f"Call metric not found: {call_id}")
            return None

        # Update fields
        for field, value in updates.items():
            if hasattr(metric, field):
                setattr(metric, field, value)

        return metric

    async def end_call_tracking(
        self,
        call_id: UUID,
        outcome: CallOutcome
    ) -> CallMetric | None:
        """End call tracking and finalize metrics.

        Args:
            call_id: Call identifier
            outcome: Final call outcome

        Returns:
            Final call metric if found
        """
        metric = self._call_metrics.get(call_id)
        if not metric:
            logger.warning(f"Call metric not found: {call_id}")
            return None

        metric.end_time = datetime.now(UTC)
        metric.duration_seconds = (metric.end_time - metric.start_time).total_seconds()
        metric.outcome = outcome

        self._active_calls.discard(call_id)

        # Update time series
        await self._update_timeseries(metric)

        logger.info(f"Ended tracking call {call_id} - Duration: {metric.duration_seconds}s, Outcome: {outcome}")
        return metric

    async def _update_timeseries(self, metric: CallMetric) -> None:
        """Update time series data with completed call.

        Args:
            metric: Completed call metric
        """
        if not metric.end_time:
            return

        # Calls timeline
        self._calls_timeline.append(TimeSeriesDataPoint(
            timestamp=metric.end_time,
            value=1.0,
            label=metric.outcome.value
        ))

        # Sentiment timeline
        if metric.average_sentiment != 0.0:
            self._sentiment_timeline.append(TimeSeriesDataPoint(
                timestamp=metric.end_time,
                value=metric.average_sentiment,
                label="sentiment"
            ))

        # Quality timeline
        if metric.audio_quality_score != 0.0:
            self._quality_timeline.append(TimeSeriesDataPoint(
                timestamp=metric.end_time,
                value=metric.audio_quality_score,
                label="quality"
            ))

        # Keep only recent data (last 24 hours)
        cutoff_time = datetime.now(UTC) - timedelta(hours=24)
        self._calls_timeline = [p for p in self._calls_timeline if p.timestamp > cutoff_time]
        self._sentiment_timeline = [p for p in self._sentiment_timeline if p.timestamp > cutoff_time]
        self._quality_timeline = [p for p in self._quality_timeline if p.timestamp > cutoff_time]

    async def get_analytics_summary(
        self,
        start_time: datetime | None = None,
        end_time: datetime | None = None
    ) -> AnalyticsSummary:
        """Get aggregated analytics summary.

        Args:
            start_time: Start of period (default: 24 hours ago)
            end_time: End of period (default: now)

        Returns:
            Analytics summary
        """
        if not end_time:
            end_time = datetime.now(UTC)
        if not start_time:
            start_time = end_time - timedelta(hours=24)

        # Filter metrics by time period
        period_metrics = [
            m for m in self._call_metrics.values()
            if m.start_time >= start_time and m.start_time <= end_time
        ]

        # Calculate call metrics
        total_calls = len(period_metrics)
        completed_calls = sum(1 for m in period_metrics if m.outcome == CallOutcome.COMPLETED)
        failed_calls = sum(1 for m in period_metrics if m.outcome == CallOutcome.FAILED)

        average_call_duration = (
            sum(m.duration_seconds for m in period_metrics) / total_calls
            if total_calls > 0 else 0.0
        )

        success_rate = (completed_calls / total_calls * 100) if total_calls > 0 else 0.0

        # Calculate quality metrics
        sentiment_metrics = [m.average_sentiment for m in period_metrics if m.average_sentiment != 0.0]
        average_sentiment = sum(sentiment_metrics) / len(sentiment_metrics) if sentiment_metrics else 0.0

        audio_metrics = [m.audio_quality_score for m in period_metrics if m.audio_quality_score != 0.0]
        average_audio_quality = sum(audio_metrics) / len(audio_metrics) if audio_metrics else 0.0

        transcription_metrics = [m.transcription_accuracy for m in period_metrics if m.transcription_accuracy != 0.0]
        average_transcription_accuracy = (
            sum(transcription_metrics) / len(transcription_metrics)
            if transcription_metrics else 0.0
        )

        # Calculate provider performance
        provider_performance = {}
        for provider_id in self._provider_metrics:
            provider_calls = [
                self._call_metrics[call_id]
                for call_id in self._provider_metrics[provider_id]
                if call_id in self._call_metrics and
                self._call_metrics[call_id].start_time >= start_time and
                self._call_metrics[call_id].start_time <= end_time
            ]

            if provider_calls:
                total = len(provider_calls)
                successful = sum(1 for m in provider_calls if m.outcome == CallOutcome.COMPLETED)
                failed = sum(1 for m in provider_calls if m.outcome == CallOutcome.FAILED)

                avg_quality = sum(m.audio_quality_score for m in provider_calls) / total

                provider_performance[provider_id] = ProviderPerformance(
                    provider_id=provider_id,
                    total_calls=total,
                    successful_calls=successful,
                    failed_calls=failed,
                    average_latency_ms=0.0,  # Would come from health monitor
                    average_audio_quality=avg_quality,
                    uptime_percentage=(successful / total * 100) if total > 0 else 0.0,
                    error_rate=(failed / total * 100) if total > 0 else 0.0
                )

        # Calculate agent performance
        agent_performance = {}
        for agent_id in self._agent_metrics:
            agent_calls = [
                self._call_metrics[call_id]
                for call_id in self._agent_metrics[agent_id]
                if call_id in self._call_metrics and
                self._call_metrics[call_id].start_time >= start_time and
                self._call_metrics[call_id].start_time <= end_time
            ]

            if agent_calls:
                total = len(agent_calls)
                completed = sum(1 for m in agent_calls if m.outcome == CallOutcome.COMPLETED)
                failed = sum(1 for m in agent_calls if m.outcome == CallOutcome.FAILED)

                avg_duration = sum(m.duration_seconds for m in agent_calls) / total
                avg_sentiment = sum(m.average_sentiment for m in agent_calls) / total
                total_suggestions = sum(m.ai_suggestions_used for m in agent_calls)
                total_warnings = sum(m.compliance_warnings for m in agent_calls)

                quality_score = (completed / total * 100) if total > 0 else 0.0

                agent_performance[agent_id] = AgentPerformance(
                    agent_id=agent_id,
                    total_calls=total,
                    completed_calls=completed,
                    failed_calls=failed,
                    average_call_duration=avg_duration,
                    average_sentiment=avg_sentiment,
                    total_suggestions_used=total_suggestions,
                    compliance_warnings=total_warnings,
                    quality_score=quality_score
                )

        # Filter time series data for period
        calls_over_time = [p for p in self._calls_timeline if start_time <= p.timestamp <= end_time]
        sentiment_over_time = [p for p in self._sentiment_timeline if start_time <= p.timestamp <= end_time]
        quality_over_time = [p for p in self._quality_timeline if start_time <= p.timestamp <= end_time]

        return AnalyticsSummary(
            period_start=start_time,
            period_end=end_time,
            total_calls=total_calls,
            completed_calls=completed_calls,
            failed_calls=failed_calls,
            average_call_duration=round(average_call_duration, 2),
            success_rate=round(success_rate, 2),
            average_sentiment=round(average_sentiment, 3),
            average_audio_quality=round(average_audio_quality, 2),
            average_transcription_accuracy=round(average_transcription_accuracy, 3),
            provider_performance=provider_performance,
            agent_performance=agent_performance,
            calls_over_time=calls_over_time,
            sentiment_over_time=sentiment_over_time,
            quality_over_time=quality_over_time
        )

    def get_call_metric(self, call_id: UUID) -> CallMetric | None:
        """Get metrics for a specific call.

        Args:
            call_id: Call identifier

        Returns:
            Call metric if found
        """
        return self._call_metrics.get(call_id)

    def get_active_calls(self) -> list[UUID]:
        """Get list of active call IDs.

        Returns:
            List of active call IDs
        """
        return list(self._active_calls)

    def get_call_count(self) -> dict[str, int]:
        """Get call counts by status.

        Returns:
            Dictionary of call counts
        """
        return {
            "total": len(self._call_metrics),
            "active": len(self._active_calls),
            "completed": len([m for m in self._call_metrics.values() if m.outcome == CallOutcome.COMPLETED]),
            "failed": len([m for m in self._call_metrics.values() if m.outcome == CallOutcome.FAILED])
        }


# Singleton instance
_analytics_service: AnalyticsService | None = None


def get_analytics_service() -> AnalyticsService:
    """Get singleton analytics service instance.

    Returns:
        AnalyticsService instance
    """
    global _analytics_service
    if _analytics_service is None:
        _analytics_service = AnalyticsService()
    return _analytics_service
