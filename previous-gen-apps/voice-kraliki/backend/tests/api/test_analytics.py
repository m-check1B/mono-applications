"""Tests for Analytics API.

Tests cover:
- Call tracking (start, update, end)
- Analytics summaries
- Agent and provider performance
- Real-time metrics
"""

import pytest
from uuid import uuid4
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

from fastapi.testclient import TestClient

from app.main import create_app
from app.services.analytics_service import (
    AnalyticsService,
    AnalyticsSummary,
    CallMetric,
    CallOutcome,
    AgentPerformance,
    ProviderPerformance,
    TimeSeriesDataPoint,
)


@pytest.fixture
def client() -> TestClient:
    """Create a test client for the application."""
    app = create_app()
    return TestClient(app)


@pytest.fixture
def mock_analytics_service():
    """Create a mock analytics service."""
    service = MagicMock(spec=AnalyticsService)
    return service


@pytest.fixture
def sample_call_metric():
    """Create a sample call metric."""
    return CallMetric(
        call_id=uuid4(),
        session_id=uuid4(),
        start_time=datetime.now(timezone.utc),
        outcome=CallOutcome.COMPLETED,
        provider_id="openai",
        agent_id="agent-1",
        average_sentiment=0.75,
        transcription_accuracy=0.95,
        audio_quality_score=85.0,
        agent_messages=10,
        customer_messages=8,
        ai_suggestions_used=3,
        compliance_warnings=0,
        tags=["sales", "follow-up"],
        notes="Good call",
    )


@pytest.fixture
def sample_analytics_summary():
    """Create a sample analytics summary."""
    now = datetime.now(timezone.utc)
    return AnalyticsSummary(
        period_start=now,
        period_end=now,
        total_calls=100,
        completed_calls=85,
        failed_calls=15,
        average_call_duration=300.0,
        success_rate=0.85,
        average_sentiment=0.6,
        average_audio_quality=80.0,
        average_transcription_accuracy=0.92,
        provider_performance={
            "openai": ProviderPerformance(
                provider_id="openai",
                total_calls=60,
                successful_calls=55,
                failed_calls=5,
                average_latency_ms=150.0,
                average_audio_quality=85.0,
                uptime_percentage=99.5,
                error_rate=0.08,
            )
        },
        agent_performance={
            "agent-1": AgentPerformance(
                agent_id="agent-1",
                total_calls=40,
                completed_calls=38,
                failed_calls=2,
                average_call_duration=280.0,
                average_sentiment=0.7,
                total_suggestions_used=25,
                compliance_warnings=1,
                quality_score=88.0,
            )
        },
        calls_over_time=[TimeSeriesDataPoint(timestamp=now, value=10.0)],
        sentiment_over_time=[TimeSeriesDataPoint(timestamp=now, value=0.6)],
        quality_over_time=[TimeSeriesDataPoint(timestamp=now, value=80.0)],
    )


class TestCallTracking:
    """Tests for call tracking endpoints."""

    def test_start_call_tracking(self, client: TestClient, sample_call_metric):
        """Test starting call tracking."""
        call_id = uuid4()
        session_id = uuid4()

        with patch("app.api.analytics.get_analytics_service") as mock_get_service:
            mock_service = AsyncMock()
            mock_service.start_call_tracking.return_value = sample_call_metric
            mock_get_service.return_value = mock_service

            response = client.post(
                "/api/v1/analytics/calls/start",
                json={
                    "call_id": str(call_id),
                    "session_id": str(session_id),
                    "provider_id": "openai",
                    "agent_id": "agent-1",
                },
            )

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert "call_metric" in data

    def test_start_call_tracking_without_agent(self, client: TestClient, sample_call_metric):
        """Test starting call tracking without agent ID."""
        call_id = uuid4()
        session_id = uuid4()

        with patch("app.api.analytics.get_analytics_service") as mock_get_service:
            mock_service = AsyncMock()
            mock_service.start_call_tracking.return_value = sample_call_metric
            mock_get_service.return_value = mock_service

            response = client.post(
                "/api/v1/analytics/calls/start",
                json={
                    "call_id": str(call_id),
                    "session_id": str(session_id),
                    "provider_id": "openai",
                },
            )

            assert response.status_code == 200

    def test_start_call_tracking_error(self, client: TestClient):
        """Test error handling in start call tracking."""
        with patch("app.api.analytics.get_analytics_service") as mock_get_service:
            mock_service = AsyncMock()
            mock_service.start_call_tracking.side_effect = Exception("Service error")
            mock_get_service.return_value = mock_service

            response = client.post(
                "/api/v1/analytics/calls/start",
                json={
                    "call_id": str(uuid4()),
                    "session_id": str(uuid4()),
                    "provider_id": "openai",
                },
            )

            assert response.status_code == 500

    def test_update_call_metric(self, client: TestClient, sample_call_metric):
        """Test updating call metrics."""
        call_id = uuid4()

        with patch("app.api.analytics.get_analytics_service") as mock_get_service:
            mock_service = AsyncMock()
            mock_service.update_call_metric.return_value = sample_call_metric
            mock_get_service.return_value = mock_service

            response = client.patch(
                "/api/v1/analytics/calls/update",
                json={
                    "call_id": str(call_id),
                    "average_sentiment": 0.8,
                    "agent_messages": 15,
                    "tags": ["important"],
                },
            )

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"

    def test_update_call_metric_not_found(self, client: TestClient):
        """Test updating non-existent call metric."""
        with patch("app.api.analytics.get_analytics_service") as mock_get_service:
            mock_service = AsyncMock()
            mock_service.update_call_metric.return_value = None
            mock_get_service.return_value = mock_service

            response = client.patch(
                "/api/v1/analytics/calls/update",
                json={
                    "call_id": str(uuid4()),
                    "average_sentiment": 0.8,
                },
            )

            assert response.status_code == 404

    def test_end_call_tracking(self, client: TestClient, sample_call_metric):
        """Test ending call tracking."""
        call_id = uuid4()

        with patch("app.api.analytics.get_analytics_service") as mock_get_service:
            mock_service = AsyncMock()
            mock_service.end_call_tracking.return_value = sample_call_metric
            mock_get_service.return_value = mock_service

            response = client.post(
                "/api/v1/analytics/calls/end",
                json={
                    "call_id": str(call_id),
                    "outcome": "completed",
                },
            )

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"

    def test_end_call_tracking_not_found(self, client: TestClient):
        """Test ending non-existent call tracking."""
        with patch("app.api.analytics.get_analytics_service") as mock_get_service:
            mock_service = AsyncMock()
            mock_service.end_call_tracking.return_value = None
            mock_get_service.return_value = mock_service

            response = client.post(
                "/api/v1/analytics/calls/end",
                json={
                    "call_id": str(uuid4()),
                    "outcome": "completed",
                },
            )

            assert response.status_code == 404


class TestAnalyticsSummary:
    """Tests for analytics summary endpoints."""

    def test_get_analytics_summary(self, client: TestClient, sample_analytics_summary):
        """Test getting analytics summary."""
        with patch("app.api.analytics.get_analytics_service") as mock_get_service:
            mock_service = AsyncMock()
            mock_service.get_analytics_summary.return_value = sample_analytics_summary
            mock_get_service.return_value = mock_service

            response = client.get("/api/v1/analytics/summary")

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert "summary" in data
            assert data["summary"]["total_calls"] == 100

    def test_get_analytics_summary_with_time_range(
        self, client: TestClient, sample_analytics_summary
    ):
        """Test getting analytics summary with time range."""
        with patch("app.api.analytics.get_analytics_service") as mock_get_service:
            mock_service = AsyncMock()
            mock_service.get_analytics_summary.return_value = sample_analytics_summary
            mock_get_service.return_value = mock_service

            response = client.get(
                "/api/v1/analytics/summary",
                params={
                    "start_time": "2024-01-01T00:00:00Z",
                    "end_time": "2024-01-31T23:59:59Z",
                },
            )

            assert response.status_code == 200

    def test_get_analytics_summary_error(self, client: TestClient):
        """Test error handling in analytics summary."""
        with patch("app.api.analytics.get_analytics_service") as mock_get_service:
            mock_service = AsyncMock()
            mock_service.get_analytics_summary.side_effect = Exception("Service error")
            mock_get_service.return_value = mock_service

            response = client.get("/api/v1/analytics/summary")

            assert response.status_code == 500


class TestCallMetrics:
    """Tests for call metrics endpoints."""

    def test_get_call_metric(self, client: TestClient, sample_call_metric):
        """Test getting a specific call metric."""
        call_id = uuid4()

        with patch("app.api.analytics.get_analytics_service") as mock_get_service:
            mock_service = MagicMock()
            mock_service.get_call_metric.return_value = sample_call_metric
            mock_get_service.return_value = mock_service

            response = client.get(f"/api/v1/analytics/calls/{call_id}")

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert "metric" in data

    def test_get_call_metric_not_found(self, client: TestClient):
        """Test getting non-existent call metric."""
        call_id = uuid4()

        with patch("app.api.analytics.get_analytics_service") as mock_get_service:
            mock_service = MagicMock()
            mock_service.get_call_metric.return_value = None
            mock_get_service.return_value = mock_service

            response = client.get(f"/api/v1/analytics/calls/{call_id}")

            assert response.status_code == 404

    def test_get_active_calls(self, client: TestClient):
        """Test getting active calls list."""
        active_call_ids = [uuid4(), uuid4(), uuid4()]

        with patch("app.api.analytics.get_analytics_service") as mock_get_service:
            mock_service = MagicMock()
            mock_service.get_active_calls.return_value = active_call_ids
            mock_get_service.return_value = mock_service

            response = client.get("/api/v1/analytics/calls")

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert data["count"] == 3

    def test_get_call_counts(self, client: TestClient):
        """Test getting call counts."""
        counts = {"total": 100, "active": 5, "completed": 85, "failed": 10}

        with patch("app.api.analytics.get_analytics_service") as mock_get_service:
            mock_service = MagicMock()
            mock_service.get_call_count.return_value = counts
            mock_get_service.return_value = mock_service

            response = client.get("/api/v1/analytics/counts")

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert data["counts"]["total"] == 100


class TestPerformanceEndpoints:
    """Tests for agent and provider performance endpoints."""

    def test_get_agent_performance(self, client: TestClient, sample_analytics_summary):
        """Test getting agent performance."""
        with patch("app.api.analytics.get_analytics_service") as mock_get_service:
            mock_service = AsyncMock()
            mock_service.get_analytics_summary.return_value = sample_analytics_summary
            mock_get_service.return_value = mock_service

            response = client.get("/api/v1/analytics/agents/agent-1")

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert data["agent_id"] == "agent-1"

    def test_get_agent_performance_not_found(self, client: TestClient, sample_analytics_summary):
        """Test getting non-existent agent performance."""
        with patch("app.api.analytics.get_analytics_service") as mock_get_service:
            mock_service = AsyncMock()
            mock_service.get_analytics_summary.return_value = sample_analytics_summary
            mock_get_service.return_value = mock_service

            response = client.get("/api/v1/analytics/agents/unknown-agent")

            assert response.status_code == 404

    def test_get_provider_performance(self, client: TestClient, sample_analytics_summary):
        """Test getting provider performance."""
        with patch("app.api.analytics.get_analytics_service") as mock_get_service:
            mock_service = AsyncMock()
            mock_service.get_analytics_summary.return_value = sample_analytics_summary
            mock_get_service.return_value = mock_service

            response = client.get("/api/v1/analytics/providers/openai")

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert data["provider_id"] == "openai"

    def test_get_provider_performance_not_found(
        self, client: TestClient, sample_analytics_summary
    ):
        """Test getting non-existent provider performance."""
        with patch("app.api.analytics.get_analytics_service") as mock_get_service:
            mock_service = AsyncMock()
            mock_service.get_analytics_summary.return_value = sample_analytics_summary
            mock_get_service.return_value = mock_service

            response = client.get("/api/v1/analytics/providers/unknown-provider")

            assert response.status_code == 404


class TestRealtimeMetrics:
    """Tests for real-time metrics endpoint."""

    def test_get_realtime_metrics(self, client: TestClient, sample_analytics_summary):
        """Test getting real-time metrics."""
        active_calls = [uuid4(), uuid4()]
        counts = {"total": 100, "active": 2}

        with patch("app.api.analytics.get_analytics_service") as mock_get_service:
            mock_service = MagicMock()
            mock_service.get_active_calls.return_value = active_calls
            mock_service.get_call_count.return_value = counts
            mock_service.get_analytics_summary = AsyncMock(
                return_value=sample_analytics_summary
            )
            mock_get_service.return_value = mock_service

            response = client.get("/api/v1/analytics/metrics/realtime")

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert data["active_calls"] == 2
            assert data["total_calls"] == 100
            assert "timestamp" in data

    def test_get_realtime_metrics_error(self, client: TestClient):
        """Test error handling in real-time metrics."""
        with patch("app.api.analytics.get_analytics_service") as mock_get_service:
            mock_service = MagicMock()
            mock_service.get_active_calls.side_effect = Exception("Service error")
            mock_get_service.return_value = mock_service

            response = client.get("/api/v1/analytics/metrics/realtime")

            assert response.status_code == 500
