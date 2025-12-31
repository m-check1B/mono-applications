"""Tests for Monitoring API.

Tests cover:
- Prometheus metrics endpoint
- Database health check
- Overall monitoring health
"""

import pytest
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from app.main import create_app


@pytest.fixture
def client() -> TestClient:
    """Create a test client for the application."""
    app = create_app()
    return TestClient(app)


class TestPrometheusMetrics:
    """Tests for Prometheus metrics endpoint."""

    def test_metrics_endpoint(self, client: TestClient):
        """Test that metrics endpoint returns Prometheus format."""
        with patch("app.api.monitoring.check_database_health") as mock_db_health, \
             patch("app.api.monitoring.update_db_pool_metrics") as mock_update_metrics, \
             patch("app.api.monitoring.set_app_info") as mock_set_info:

            mock_db_health.return_value = {
                "status": "healthy",
                "pool_size": 5,
                "checked_out": 1,
                "overflow": 0,
            }

            response = client.get("/api/v1/monitoring/metrics")

            assert response.status_code == 200
            # Prometheus metrics should contain HELP and TYPE comments
            content = response.text
            assert "# " in content or response.headers.get("content-type", "").startswith("text/")

    def test_metrics_content_type(self, client: TestClient):
        """Test that metrics endpoint returns correct content type."""
        with patch("app.api.monitoring.check_database_health") as mock_db_health:
            mock_db_health.return_value = {"status": "healthy"}

            response = client.get("/api/v1/monitoring/metrics")

            assert response.status_code == 200
            # Content type should be text/plain or text/... for Prometheus
            content_type = response.headers.get("content-type", "")
            assert "text/" in content_type

    def test_metrics_handles_db_check_failure(self, client: TestClient):
        """Test that metrics endpoint works even if DB check fails."""
        with patch("app.api.monitoring.check_database_health") as mock_db_health:
            mock_db_health.side_effect = Exception("DB connection failed")

            response = client.get("/api/v1/monitoring/metrics")

            # Should still return 200 even if DB check fails
            assert response.status_code == 200


class TestDatabaseHealth:
    """Tests for database health check endpoint."""

    def test_database_health_endpoint(self, client: TestClient):
        """Test database health check returns status."""
        with patch("app.api.monitoring.check_database_health") as mock_db_health:
            mock_db_health.return_value = {
                "status": "healthy",
                "pool_size": 5,
                "checked_out": 2,
                "overflow": 0,
                "timeout": 30,
            }

            response = client.get("/api/v1/monitoring/health/database")

            assert response.status_code == 200
            data = response.json()
            assert "status" in data
            assert data["status"] == "healthy"

    def test_database_health_returns_pool_metrics(self, client: TestClient):
        """Test database health check returns pool metrics."""
        with patch("app.api.monitoring.check_database_health") as mock_db_health:
            mock_db_health.return_value = {
                "status": "healthy",
                "pool_size": 10,
                "checked_out": 3,
                "overflow": 1,
            }

            response = client.get("/api/v1/monitoring/health/database")

            assert response.status_code == 200
            data = response.json()
            assert data["pool_size"] == 10
            assert data["checked_out"] == 3
            assert data["overflow"] == 1

    def test_database_health_unhealthy(self, client: TestClient):
        """Test database health check when database is unhealthy."""
        with patch("app.api.monitoring.check_database_health") as mock_db_health:
            mock_db_health.return_value = {
                "status": "unhealthy",
                "error": "Connection timeout",
            }

            response = client.get("/api/v1/monitoring/health/database")

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "unhealthy"


class TestMonitoringHealth:
    """Tests for overall monitoring health endpoint."""

    def test_monitoring_health_endpoint(self, client: TestClient):
        """Test overall monitoring health check."""
        with patch("app.api.monitoring.check_database_health") as mock_db_health, \
             patch("app.api.monitoring.get_settings") as mock_settings, \
             patch("app.api.monitoring.get_feature_flags") as mock_flags:

            mock_db_health.return_value = {"status": "healthy"}

            mock_settings_obj = MagicMock()
            mock_settings_obj.app_name = "Voice by Kraliki"
            mock_settings_obj.version = "1.0.0"
            mock_settings_obj.environment = "test"
            mock_settings.return_value = mock_settings_obj

            mock_flags_obj = MagicMock()
            mock_flags_obj.enable_metrics_collection = True
            mock_flags.return_value = mock_flags_obj

            response = client.get("/api/v1/monitoring/health")

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            assert "service" in data
            assert "version" in data
            assert "environment" in data

    def test_monitoring_health_response_structure(self, client: TestClient):
        """Test monitoring health response has required fields."""
        with patch("app.api.monitoring.check_database_health") as mock_db_health, \
             patch("app.api.monitoring.get_settings") as mock_settings, \
             patch("app.api.monitoring.get_feature_flags") as mock_flags:

            mock_db_health.return_value = {"status": "healthy"}

            mock_settings_obj = MagicMock()
            mock_settings_obj.app_name = "Voice by Kraliki"
            mock_settings_obj.version = "2.0.0"
            mock_settings_obj.environment = "production"
            mock_settings.return_value = mock_settings_obj

            mock_flags_obj = MagicMock()
            mock_flags_obj.enable_metrics_collection = False
            mock_flags.return_value = mock_flags_obj

            response = client.get("/api/v1/monitoring/health")

            assert response.status_code == 200
            data = response.json()

            assert "status" in data
            assert "service" in data
            assert "version" in data
            assert "environment" in data
            assert "metrics_enabled" in data
            assert "database" in data

    def test_monitoring_health_includes_metrics_status(self, client: TestClient):
        """Test monitoring health includes metrics collection status."""
        with patch("app.api.monitoring.check_database_health") as mock_db_health, \
             patch("app.api.monitoring.get_settings") as mock_settings, \
             patch("app.api.monitoring.get_feature_flags") as mock_flags:

            mock_db_health.return_value = {"status": "healthy"}

            mock_settings_obj = MagicMock()
            mock_settings_obj.app_name = "Voice by Kraliki"
            mock_settings_obj.version = "1.0.0"
            mock_settings_obj.environment = "development"
            mock_settings.return_value = mock_settings_obj

            mock_flags_obj = MagicMock()
            mock_flags_obj.enable_metrics_collection = True
            mock_flags.return_value = mock_flags_obj

            response = client.get("/api/v1/monitoring/health")

            assert response.status_code == 200
            data = response.json()
            assert data["metrics_enabled"] is True

    def test_monitoring_health_includes_database_info(self, client: TestClient):
        """Test monitoring health includes database status."""
        with patch("app.api.monitoring.check_database_health") as mock_db_health, \
             patch("app.api.monitoring.get_settings") as mock_settings, \
             patch("app.api.monitoring.get_feature_flags") as mock_flags:

            mock_db_health.return_value = {
                "status": "healthy",
                "pool_size": 5,
                "checked_out": 1,
            }

            mock_settings_obj = MagicMock()
            mock_settings_obj.app_name = "Voice by Kraliki"
            mock_settings_obj.version = "1.0.0"
            mock_settings_obj.environment = "test"
            mock_settings.return_value = mock_settings_obj

            mock_flags_obj = MagicMock()
            mock_flags_obj.enable_metrics_collection = True
            mock_flags.return_value = mock_flags_obj

            response = client.get("/api/v1/monitoring/health")

            assert response.status_code == 200
            data = response.json()
            assert "database" in data
            assert data["database"]["status"] == "healthy"
