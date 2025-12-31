"""Tests for AnalyticsService.

Tests cover:
- Call tracking lifecycle (start, update, end)
- Call metrics calculation
- Agent performance tracking
- Provider performance tracking
- Analytics summary aggregation
- Time series data management
"""

import pytest
from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

from app.services.analytics_service import (
    AnalyticsService,
    CallOutcome,
    CallMetric,
    get_analytics_service,
)


@pytest.fixture
def analytics_service():
    """Create a fresh AnalyticsService instance for each test."""
    return AnalyticsService()


@pytest.fixture
def sample_call_id():
    """Generate a sample call ID."""
    return uuid4()


@pytest.fixture
def sample_session_id():
    """Generate a sample session ID."""
    return uuid4()


class TestCallTracking:
    """Tests for call tracking lifecycle."""

    @pytest.mark.asyncio
    async def test_start_call_tracking(self, analytics_service, sample_call_id, sample_session_id):
        """Test starting call tracking creates a metric."""
        metric = await analytics_service.start_call_tracking(
            call_id=sample_call_id,
            session_id=sample_session_id,
            provider_id="twilio",
            agent_id="agent_123"
        )

        assert metric is not None
        assert metric.call_id == sample_call_id
        assert metric.session_id == sample_session_id
        assert metric.provider_id == "twilio"
        assert metric.agent_id == "agent_123"
        assert metric.outcome == CallOutcome.COMPLETED  # Default
        assert metric.duration_seconds == 0.0

    @pytest.mark.asyncio
    async def test_start_call_tracking_adds_to_active(self, analytics_service, sample_call_id, sample_session_id):
        """Test that starting tracking adds call to active set."""
        await analytics_service.start_call_tracking(
            call_id=sample_call_id,
            session_id=sample_session_id,
            provider_id="telnyx"
        )

        active = analytics_service.get_active_calls()
        assert sample_call_id in active

    @pytest.mark.asyncio
    async def test_start_call_tracking_no_agent(self, analytics_service, sample_call_id, sample_session_id):
        """Test starting call tracking without agent ID."""
        metric = await analytics_service.start_call_tracking(
            call_id=sample_call_id,
            session_id=sample_session_id,
            provider_id="twilio"
        )

        assert metric.agent_id is None

    @pytest.mark.asyncio
    async def test_update_call_metric(self, analytics_service, sample_call_id, sample_session_id):
        """Test updating call metrics."""
        await analytics_service.start_call_tracking(
            call_id=sample_call_id,
            session_id=sample_session_id,
            provider_id="twilio"
        )

        updated = await analytics_service.update_call_metric(
            call_id=sample_call_id,
            average_sentiment=0.75,
            audio_quality_score=85.0,
            agent_messages=5
        )

        assert updated is not None
        assert updated.average_sentiment == 0.75
        assert updated.audio_quality_score == 85.0
        assert updated.agent_messages == 5

    @pytest.mark.asyncio
    async def test_update_call_metric_not_found(self, analytics_service):
        """Test updating non-existent call returns None."""
        result = await analytics_service.update_call_metric(
            call_id=uuid4(),
            average_sentiment=0.5
        )

        assert result is None

    @pytest.mark.asyncio
    async def test_end_call_tracking(self, analytics_service, sample_call_id, sample_session_id):
        """Test ending call tracking finalizes metrics."""
        await analytics_service.start_call_tracking(
            call_id=sample_call_id,
            session_id=sample_session_id,
            provider_id="twilio"
        )

        # Wait a bit to have non-zero duration
        import asyncio
        await asyncio.sleep(0.01)

        metric = await analytics_service.end_call_tracking(
            call_id=sample_call_id,
            outcome=CallOutcome.COMPLETED
        )

        assert metric is not None
        assert metric.end_time is not None
        assert metric.duration_seconds > 0
        assert metric.outcome == CallOutcome.COMPLETED

    @pytest.mark.asyncio
    async def test_end_call_tracking_removes_from_active(self, analytics_service, sample_call_id, sample_session_id):
        """Test ending tracking removes call from active set."""
        await analytics_service.start_call_tracking(
            call_id=sample_call_id,
            session_id=sample_session_id,
            provider_id="twilio"
        )

        await analytics_service.end_call_tracking(
            call_id=sample_call_id,
            outcome=CallOutcome.FAILED
        )

        active = analytics_service.get_active_calls()
        assert sample_call_id not in active

    @pytest.mark.asyncio
    async def test_end_call_tracking_not_found(self, analytics_service):
        """Test ending non-existent call returns None."""
        result = await analytics_service.end_call_tracking(
            call_id=uuid4(),
            outcome=CallOutcome.FAILED
        )

        assert result is None


class TestCallMetrics:
    """Tests for call metrics retrieval."""

    @pytest.mark.asyncio
    async def test_get_call_metric(self, analytics_service, sample_call_id, sample_session_id):
        """Test retrieving a specific call metric."""
        await analytics_service.start_call_tracking(
            call_id=sample_call_id,
            session_id=sample_session_id,
            provider_id="twilio"
        )

        metric = analytics_service.get_call_metric(sample_call_id)

        assert metric is not None
        assert metric.call_id == sample_call_id

    def test_get_call_metric_not_found(self, analytics_service):
        """Test retrieving non-existent call returns None."""
        result = analytics_service.get_call_metric(uuid4())
        assert result is None

    @pytest.mark.asyncio
    async def test_get_call_count(self, analytics_service):
        """Test getting call counts by status.

        Note: The analytics service initializes calls with outcome=COMPLETED as default.
        When a call ends with FAILED, it changes from COMPLETED to FAILED.
        When it ends with COMPLETED, it stays COMPLETED.
        So the completed count = active calls + ended-as-completed calls.
        """
        # Get initial counts
        initial_counts = analytics_service.get_call_count()

        # Add 3 calls
        call_ids = []
        for i in range(3):
            call_id = uuid4()
            call_ids.append(call_id)
            await analytics_service.start_call_tracking(
                call_id=call_id,
                session_id=uuid4(),
                provider_id="twilio"
            )

        # After adding 3 calls, total should increase by 3
        counts_after_start = analytics_service.get_call_count()
        assert counts_after_start["total"] == initial_counts["total"] + 3
        assert counts_after_start["active"] == initial_counts["active"] + 3

        # End first call as COMPLETED (stays COMPLETED)
        await analytics_service.end_call_tracking(
            call_id=call_ids[0],
            outcome=CallOutcome.COMPLETED
        )

        # End second call as FAILED (changes from COMPLETED to FAILED)
        await analytics_service.end_call_tracking(
            call_id=call_ids[1],
            outcome=CallOutcome.FAILED
        )

        # Third call stays active

        final_counts = analytics_service.get_call_count()

        # Verify final state
        assert final_counts["total"] == initial_counts["total"] + 3
        assert final_counts["active"] == initial_counts["active"] + 1  # Only 1 still active
        assert final_counts["failed"] == initial_counts["failed"] + 1  # 1 failed


class TestAnalyticsSummary:
    """Tests for analytics summary aggregation."""

    @pytest.mark.asyncio
    async def test_get_analytics_summary_empty(self, analytics_service):
        """Test analytics summary with no calls."""
        summary = await analytics_service.get_analytics_summary()

        assert summary.total_calls == 0
        assert summary.completed_calls == 0
        assert summary.failed_calls == 0
        assert summary.success_rate == 0.0

    @pytest.mark.asyncio
    async def test_get_analytics_summary_with_calls(self, analytics_service):
        """Test analytics summary with completed calls."""
        # Create and complete some calls
        for i in range(5):
            call_id = uuid4()
            await analytics_service.start_call_tracking(
                call_id=call_id,
                session_id=uuid4(),
                provider_id="twilio",
                agent_id="agent_1"
            )
            await analytics_service.update_call_metric(
                call_id=call_id,
                average_sentiment=0.5,
                audio_quality_score=80.0,
                transcription_accuracy=0.95
            )
            await analytics_service.end_call_tracking(
                call_id=call_id,
                outcome=CallOutcome.COMPLETED if i < 4 else CallOutcome.FAILED
            )

        summary = await analytics_service.get_analytics_summary()

        assert summary.total_calls == 5
        assert summary.completed_calls == 4
        assert summary.failed_calls == 1
        assert summary.success_rate == 80.0

    @pytest.mark.asyncio
    async def test_get_analytics_summary_time_filter(self, analytics_service):
        """Test analytics summary with time period filter."""
        # Create a call
        call_id = uuid4()
        await analytics_service.start_call_tracking(
            call_id=call_id,
            session_id=uuid4(),
            provider_id="twilio"
        )
        await analytics_service.end_call_tracking(
            call_id=call_id,
            outcome=CallOutcome.COMPLETED
        )

        # Query for last hour - should include the call
        now = datetime.now(timezone.utc)
        summary = await analytics_service.get_analytics_summary(
            start_time=now - timedelta(hours=1),
            end_time=now + timedelta(minutes=1)
        )

        assert summary.total_calls >= 1

    @pytest.mark.asyncio
    async def test_get_analytics_summary_provider_performance(self, analytics_service):
        """Test that summary includes provider performance metrics."""
        # Create calls for multiple providers
        for provider in ["twilio", "telnyx"]:
            for _ in range(2):
                call_id = uuid4()
                await analytics_service.start_call_tracking(
                    call_id=call_id,
                    session_id=uuid4(),
                    provider_id=provider
                )
                await analytics_service.update_call_metric(
                    call_id=call_id,
                    audio_quality_score=90.0
                )
                await analytics_service.end_call_tracking(
                    call_id=call_id,
                    outcome=CallOutcome.COMPLETED
                )

        summary = await analytics_service.get_analytics_summary()

        assert "twilio" in summary.provider_performance
        assert "telnyx" in summary.provider_performance
        assert summary.provider_performance["twilio"].total_calls == 2
        assert summary.provider_performance["telnyx"].total_calls == 2

    @pytest.mark.asyncio
    async def test_get_analytics_summary_agent_performance(self, analytics_service):
        """Test that summary includes agent performance metrics."""
        # Create calls for different agents
        for agent_id in ["agent_1", "agent_2"]:
            for _ in range(3):
                call_id = uuid4()
                await analytics_service.start_call_tracking(
                    call_id=call_id,
                    session_id=uuid4(),
                    provider_id="twilio",
                    agent_id=agent_id
                )
                await analytics_service.update_call_metric(
                    call_id=call_id,
                    ai_suggestions_used=2
                )
                await analytics_service.end_call_tracking(
                    call_id=call_id,
                    outcome=CallOutcome.COMPLETED
                )

        summary = await analytics_service.get_analytics_summary()

        assert "agent_1" in summary.agent_performance
        assert "agent_2" in summary.agent_performance
        assert summary.agent_performance["agent_1"].total_calls == 3
        assert summary.agent_performance["agent_1"].total_suggestions_used == 6


class TestTimeSeries:
    """Tests for time series data management."""

    @pytest.mark.asyncio
    async def test_timeseries_updated_on_call_end(self, analytics_service, sample_call_id, sample_session_id):
        """Test that time series data is updated when call ends."""
        await analytics_service.start_call_tracking(
            call_id=sample_call_id,
            session_id=sample_session_id,
            provider_id="twilio"
        )
        await analytics_service.update_call_metric(
            call_id=sample_call_id,
            average_sentiment=0.8,
            audio_quality_score=95.0
        )
        await analytics_service.end_call_tracking(
            call_id=sample_call_id,
            outcome=CallOutcome.COMPLETED
        )

        summary = await analytics_service.get_analytics_summary()

        assert len(summary.calls_over_time) >= 1
        assert len(summary.sentiment_over_time) >= 1
        assert len(summary.quality_over_time) >= 1


class TestCallOutcomes:
    """Tests for different call outcomes."""

    @pytest.mark.asyncio
    async def test_call_outcome_completed(self, analytics_service, sample_call_id, sample_session_id):
        """Test completed call outcome."""
        await analytics_service.start_call_tracking(
            call_id=sample_call_id,
            session_id=sample_session_id,
            provider_id="twilio"
        )
        metric = await analytics_service.end_call_tracking(
            call_id=sample_call_id,
            outcome=CallOutcome.COMPLETED
        )

        assert metric.outcome == CallOutcome.COMPLETED

    @pytest.mark.asyncio
    async def test_call_outcome_failed(self, analytics_service, sample_call_id, sample_session_id):
        """Test failed call outcome."""
        await analytics_service.start_call_tracking(
            call_id=sample_call_id,
            session_id=sample_session_id,
            provider_id="twilio"
        )
        metric = await analytics_service.end_call_tracking(
            call_id=sample_call_id,
            outcome=CallOutcome.FAILED
        )

        assert metric.outcome == CallOutcome.FAILED

    @pytest.mark.asyncio
    async def test_call_outcome_abandoned(self, analytics_service, sample_call_id, sample_session_id):
        """Test abandoned call outcome."""
        await analytics_service.start_call_tracking(
            call_id=sample_call_id,
            session_id=sample_session_id,
            provider_id="twilio"
        )
        metric = await analytics_service.end_call_tracking(
            call_id=sample_call_id,
            outcome=CallOutcome.ABANDONED
        )

        assert metric.outcome == CallOutcome.ABANDONED

    @pytest.mark.asyncio
    async def test_call_outcome_transferred(self, analytics_service, sample_call_id, sample_session_id):
        """Test transferred call outcome."""
        await analytics_service.start_call_tracking(
            call_id=sample_call_id,
            session_id=sample_session_id,
            provider_id="twilio"
        )
        metric = await analytics_service.end_call_tracking(
            call_id=sample_call_id,
            outcome=CallOutcome.TRANSFERRED
        )

        assert metric.outcome == CallOutcome.TRANSFERRED

    @pytest.mark.asyncio
    async def test_call_outcome_voicemail(self, analytics_service, sample_call_id, sample_session_id):
        """Test voicemail call outcome."""
        await analytics_service.start_call_tracking(
            call_id=sample_call_id,
            session_id=sample_session_id,
            provider_id="twilio"
        )
        metric = await analytics_service.end_call_tracking(
            call_id=sample_call_id,
            outcome=CallOutcome.VOICEMAIL
        )

        assert metric.outcome == CallOutcome.VOICEMAIL


class TestSingleton:
    """Tests for singleton service instance."""

    def test_get_analytics_service_returns_singleton(self):
        """Test that get_analytics_service returns singleton."""
        service1 = get_analytics_service()
        service2 = get_analytics_service()

        assert service1 is service2

    @pytest.mark.asyncio
    async def test_singleton_preserves_state(self):
        """Test that singleton preserves state across calls."""
        service = get_analytics_service()

        call_id = uuid4()
        await service.start_call_tracking(
            call_id=call_id,
            session_id=uuid4(),
            provider_id="twilio"
        )

        # Get service again and check state
        service2 = get_analytics_service()
        metric = service2.get_call_metric(call_id)

        assert metric is not None
