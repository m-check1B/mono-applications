"""API endpoint tests for TL;DR Bot."""
from unittest.mock import AsyncMock, patch


class TestRootEndpoint:
    """Tests for the root endpoint."""

    def test_root_returns_ok(self, client):
        """GET / should return status ok."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "app" in data
        assert "version" in data

    def test_root_has_version(self, client):
        """GET / should include version info."""
        response = client.get("/")
        data = response.json()
        assert data["version"] == "0.1.0"


class TestHealthEndpoint:
    """Tests for the health endpoint."""

    def test_health_returns_status(self, client):
        """GET /health should return health status."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "redis" in data

    def test_health_shows_redis_status(self, client, mock_buffer):
        """GET /health should show Redis connection status."""
        response = client.get("/health")
        data = response.json()
        # With mock, Redis should appear connected
        assert data["redis"] in ["connected", "disconnected"]


class TestWebhookEndpoint:
    """Tests for the Telegram webhook endpoint."""

    def test_webhook_requires_post(self, client):
        """Webhook should only accept POST requests."""
        response = client.get("/webhook")
        assert response.status_code == 405  # Method not allowed

    def test_webhook_rejects_missing_secret_header(self, client):
        """POST /webhook should reject requests without secret header."""
        update = {"update_id": 123456}
        response = client.post("/webhook", json=update)
        assert response.status_code == 403
        assert response.json()["detail"] == "Forbidden"

    def test_webhook_rejects_invalid_secret(self, client):
        """POST /webhook should reject requests with wrong secret."""
        update = {"update_id": 123456}
        response = client.post(
            "/webhook",
            json=update,
            headers={"X-Telegram-Bot-Api-Secret-Token": "wrong-secret"}
        )
        assert response.status_code == 403
        assert response.json()["detail"] == "Forbidden"

    def test_webhook_accepts_valid_secret(self, client):
        """POST /webhook should accept requests with valid secret."""
        with patch("app.main.process_update", new_callable=AsyncMock) as mock_process:
            mock_process.return_value = None

            update = {
                "update_id": 123456,
                "message": {
                    "message_id": 1,
                    "chat": {"id": -100123, "type": "supergroup"},
                    "text": "Hello, world!"
                }
            }

            response = client.post(
                "/webhook",
                json=update,
                headers={"X-Telegram-Bot-Api-Secret-Token": "test-secret-token"}
            )
            assert response.status_code == 200
            assert response.json() == {"ok": True}

    def test_webhook_handles_empty_body(self, client):
        """POST /webhook should handle empty body gracefully."""
        response = client.post(
            "/webhook",
            content="",
            headers={"X-Telegram-Bot-Api-Secret-Token": "test-secret-token"}
        )
        # Should return error for invalid JSON
        assert response.status_code in [400, 422, 500]


class TestAnalyticsDashboard:
    """Tests for the analytics dashboard endpoints."""

    def test_dashboard_requires_token(self, client):
        """GET /dashboard should require a token."""
        response = client.get("/dashboard")
        assert response.status_code == 422  # Missing query param

    def test_dashboard_rejects_invalid_token(self, client):
        """GET /dashboard should reject invalid token."""
        response = client.get("/dashboard?token=wrong-token")
        assert response.status_code == 403

    def test_dashboard_accepts_valid_token(self, client):
        """GET /dashboard should return HTML with valid token."""
        response = client.get("/dashboard?token=test-secret-token")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        assert "TL;DR Bot Analytics" in response.text

    def test_api_analytics_requires_token(self, client):
        """GET /api/analytics should require a token."""
        response = client.get("/api/analytics")
        assert response.status_code == 422  # Missing query param

    def test_api_analytics_rejects_invalid_token(self, client):
        """GET /api/analytics should reject invalid token."""
        response = client.get("/api/analytics?token=wrong-token")
        assert response.status_code == 403

    def test_api_analytics_returns_json(self, client, mock_analytics):
        """GET /api/analytics should return JSON data."""
        response = client.get("/api/analytics?token=test-secret-token")
        assert response.status_code == 200
        data = response.json()
        assert "generated_at" in data
        assert "all_time" in data
        assert "today" in data
        assert "commands" in data
        assert "trends_7d" in data


class TestErrorHandling:
    """Tests for error handling."""

    def test_404_for_unknown_route(self, client):
        """Unknown routes should return 404."""
        response = client.get("/unknown/route")
        assert response.status_code == 404

    def test_invalid_json_returns_error(self, client):
        """Invalid JSON should return appropriate error."""
        response = client.post(
            "/webhook",
            content="not valid json",
            headers={
                "Content-Type": "application/json",
                "X-Telegram-Bot-Api-Secret-Token": "test-secret-token"
            }
        )
        assert response.status_code in [400, 422, 500]
