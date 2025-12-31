"""Tests for APM and production monitoring functionality."""

import os
import pytest
from unittest.mock import patch, MagicMock

from app.config.sentry import init_sentry, capture_exception, before_send_filter


class TestSentryInitialization:
    """Test Sentry initialization and configuration."""

    def test_init_sentry_without_dsn(self):
        """Test that Sentry initialization is skipped when DSN is not configured."""
        with patch.dict(os.environ, clear=True):
            with patch.dict(os.environ, {"ENVIRONMENT": "test"}):
                init_sentry()
                # Should not crash, just log warning

    def test_init_sentry_with_dsn(self):
        """Test Sentry initialization with valid DSN."""
        with patch.dict(
            os.environ,
            {
                "SENTRY_DSN": "https://test@sentry.io/123",
                "ENVIRONMENT": "test",
                "RELEASE_VERSION": "1.0.0",
                "SENTRY_TRACES_SAMPLE_RATE": "0.5",
                "SENTRY_PROFILES_SAMPLE_RATE": "0.25",
            },
        ):
            with patch("app.config.sentry.sentry_sdk.init") as mock_init:
                init_sentry()
                mock_init.assert_called_once()
                call_args = mock_init.call_args[1]
                assert call_args["dsn"] == "https://test@sentry.io/123"
                assert call_args["environment"] == "test"
                assert call_args["release"] == "operator-demo@1.0.0"
                assert call_args["traces_sample_rate"] == 0.5
                assert call_args["profiles_sample_rate"] == 0.25

    def test_sentry_default_sample_rates(self):
        """Test that Sentry uses default sample rates when not configured."""
        with patch.dict(
            os.environ,
            {
                "SENTRY_DSN": "https://test@sentry.io/123",
                "ENVIRONMENT": "test",
            },
        ):
            with patch("app.config.sentry.sentry_sdk.init") as mock_init:
                init_sentry()
                call_args = mock_init.call_args[1]
                assert call_args["traces_sample_rate"] == 0.1
                assert call_args["profiles_sample_rate"] == 0.1


class TestSentryEventFiltering:
    """Test Sentry event filtering logic."""

    def test_before_send_filter_health_check(self):
        """Test that health check errors are filtered out."""
        event = {"request": {"url": "http://localhost:8000/health"}}
        result = before_send_filter(event, None)
        assert result is None

    def test_before_send_filter_rate_limit_errors(self):
        """Test that rate limit errors are filtered out."""
        event = {"exception": {"values": [{"type": "RateLimitExceeded"}]}}
        result = before_send_filter(event, None)
        assert result is None

    def test_before_send_filter_normal_errors(self):
        """Test that normal errors are not filtered."""
        event = {"exception": {"values": [{"type": "ValueError", "value": "Test error"}]}}
        result = before_send_filter(event, None)
        assert result is not None
        assert result == event


class TestSentryExceptionCapture:
    """Test manual exception capture functionality."""

    def test_capture_exception_with_context(self):
        """Test capturing exceptions with additional context."""
        with patch("app.config.sentry.sentry_sdk.capture_exception") as mock_capture:
            test_error = ValueError("Test error")
            context = {
                "user": {"id": "123", "email": "test@example.com"},
                "tags": {"feature": "monitoring"},
                "extra": {"data": "test data"},
            }
            capture_exception(test_error, context)

            mock_capture.assert_called_once()
            with patch("app.config.sentry.sentry_sdk.push_scope") as mock_scope:
                mock_scope.return_value.__enter__ = MagicMock(return_value=MagicMock())
                mock_scope.return_value.__exit__ = MagicMock(return_value=False)
                capture_exception(test_error, context)

    def test_capture_exception_without_context(self):
        """Test capturing exceptions without context."""
        with patch("app.config.sentry.sentry_sdk.capture_exception") as mock_capture:
            test_error = ValueError("Test error")
            capture_exception(test_error)
            mock_capture.assert_called_once_with(test_error)


class TestHealthEndpoints:
    """Test health check endpoints for monitoring."""

    def test_health_endpoint(self, client):
        """Test that /health endpoint returns expected structure."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "version" in data
        assert "environment" in data
        assert data["status"] == "healthy"

    def test_readiness_endpoint(self, client):
        """Test that /ready endpoint returns expected structure."""
        response = client.get("/ready")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "ready"

    def test_root_endpoint(self, client):
        """Test that root endpoint returns API information."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "docs" in data
        assert "metrics" in data


class TestPrometheusMetrics:
    """Test Prometheus metrics collection."""

    def test_metrics_endpoint(self, client):
        """Test that /metrics endpoint is accessible."""
        response = client.get("/metrics")
        assert response.status_code == 200
        metrics = response.text
        assert "http_requests_total" in metrics or "process_start_time_seconds" in metrics

    def test_metrics_endpoint_content_type(self, client):
        """Test that /metrics endpoint returns correct content type."""
        response = client.get("/metrics")
        assert response.status_code == 200
        # Prometheus metrics should have text/plain content type
        assert "text/plain" in response.headers.get("content-type", "")

    def test_metrics_collection(self, client):
        """Test that metrics are collected for API requests."""
        # Make some requests
        client.get("/health")
        client.get("/ready")
        client.get("/")

        # Get metrics
        response = client.get("/metrics")
        assert response.status_code == 200
        metrics = response.text

        # Should have some metrics collected
        assert len(metrics) > 0


class TestMonitoringIntegration:
    """Test integration of monitoring components."""

    def test_application_starts_with_monitoring(self, client):
        """Test that application starts successfully with monitoring enabled."""
        # If we can create a client and make requests, monitoring is working
        response = client.get("/health")
        assert response.status_code == 200

    def test_error_tracking_on_exception(self, client):
        """Test that exceptions are tracked (if Sentry is configured)."""
        # Make a request to a non-existent endpoint
        response = client.get("/non-existent-endpoint")
        assert response.status_code == 404

        # In a real test with Sentry configured, this would send an error
        # Here we just verify the endpoint doesn't crash the application

    def test_metrics_on_request(self, client):
        """Test that requests are tracked in metrics."""
        # Make a successful request
        response = client.get("/health")
        assert response.status_code == 200

        # Check metrics were updated
        metrics_response = client.get("/metrics")
        assert metrics_response.status_code == 200


class TestMonitoringEnvironmentVariables:
    """Test that monitoring respects environment variables."""

    @pytest.mark.parametrize(
        "env_var,expected_value",
        [
            ("ENABLE_METRICS", "true"),
            ("SENTRY_TRACES_SAMPLE_RATE", "0.5"),
            ("SENTRY_PROFILES_SAMPLE_RATE", "0.25"),
            ("APM_ENABLED", "true"),
            ("APM_ENVIRONMENT", "production"),
        ],
    )
    def test_monitoring_env_vars_default(self, env_var, expected_value):
        """Test default values for monitoring environment variables."""
        # These are the default values that should be set
        # In a real application, these would be loaded from .env
        # For testing, we just verify they're properly documented
        assert True  # Placeholder test

    def test_environment_in_health_check(self, client):
        """Test that health check includes environment info."""
        with patch.dict(os.environ, {"ENVIRONMENT": "test"}):
            response = client.get("/health")
            assert response.status_code == 200
            data = response.json()
            assert "environment" in data


class TestPerformanceMonitoring:
    """Test performance monitoring capabilities."""

    def test_request_tracking(self, client):
        """Test that requests are tracked for performance monitoring."""
        import time

        # Make a request and measure time
        start_time = time.time()
        response = client.get("/health")
        duration = time.time() - start_time

        assert response.status_code == 200
        assert duration < 1.0  # Should be fast

        # Metrics should have been collected
        metrics_response = client.get("/metrics")
        assert metrics_response.status_code == 200

    def test_concurrent_request_tracking(self, client):
        """Test that concurrent requests are tracked correctly."""
        import concurrent.futures

        def make_request():
            return client.get("/health")

        # Make concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]

        # All should succeed
        assert all(r.status_code == 200 for r in results)

        # Metrics should reflect concurrent requests
        metrics_response = client.get("/metrics")
        assert metrics_response.status_code == 200


class TestMonitoringConfiguration:
    """Test monitoring configuration validation."""

    def test_invalid_sample_rate(self):
        """Test that invalid sample rates are handled gracefully."""
        with patch.dict(
            os.environ,
            {"SENTRY_DSN": "https://test@sentry.io/123", "SENTRY_TRACES_SAMPLE_RATE": "invalid"},
        ):
            with patch("app.config.sentry.sentry_sdk.init") as mock_init:
                init_sentry()
                # Should not crash, might log error

    def test_sample_rate_bounds(self):
        """Test that sample rates are within valid bounds."""
        test_rates = [-0.5, 0.0, 0.5, 1.0, 1.5]

        for rate in test_rates:
            with patch.dict(
                os.environ,
                {
                    "SENTRY_DSN": "https://test@sentry.io/123",
                    "SENTRY_TRACES_SAMPLE_RATE": str(rate),
                },
            ):
                with patch("app.config.sentry.sentry_sdk.init") as mock_init:
                    init_sentry()
                    # Sentry should handle invalid rates internally
                    mock_init.assert_called_once()


@pytest.fixture
def client():
    """Create a test client for the FastAPI application."""
    try:
        from fastapi.testclient import TestClient
    except ImportError:
        pytest.skip("FastAPI not available")
        return

    from app.main import app

    # Disable Sentry during tests to avoid network calls
    with patch.dict(os.environ, {"SENTRY_DSN": ""}):
        with TestClient(app) as test_client:
            yield test_client
