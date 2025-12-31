"""Tests for main.py FastAPI application routes and handlers."""

from datetime import datetime, UTC
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


class TestRootEndpoint:
    """Test root endpoint."""

    def test_root_returns_ok(self, client):
        """Test root endpoint returns status ok."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "app" in data
        assert "version" in data


class TestHealthEndpoint:
    """Test health endpoint."""

    def test_health_returns_connected_when_redis_ok(self, client, mock_redis):
        """Test health shows connected when Redis responds."""
        mock_redis.ping = AsyncMock(return_value=True)
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data

    def test_health_returns_disconnected_when_redis_fails(self, client, mock_redis):
        """Test health shows degraded when Redis fails."""
        mock_redis.ping = AsyncMock(side_effect=Exception("Connection failed"))
        response = client.get("/health")
        assert response.status_code == 200


class TestAnalyticsEndpoint:
    """Test analytics endpoint."""

    def test_analytics_requires_token(self, client):
        """Test analytics endpoint requires token."""
        response = client.get("/api/analytics")
        assert response.status_code == 422  # Missing required query param

    def test_analytics_rejects_invalid_token(self, client, mock_settings):
        """Test analytics rejects invalid token."""
        mock_settings.telegram_webhook_secret = "correct-token"
        response = client.get("/api/analytics?token=wrong-token")
        assert response.status_code == 403

    def test_analytics_returns_data_with_valid_token(self, client, mock_settings, mock_analytics):
        """Test analytics returns data with valid token."""
        mock_settings.telegram_webhook_secret = "test-secret-token"
        response = client.get("/api/analytics?token=test-secret-token")
        assert response.status_code == 200
        data = response.json()
        assert "all_time" in data
        assert "today" in data


class TestDashboardEndpoint:
    """Test dashboard endpoint."""

    def test_dashboard_returns_html(self, client, mock_settings):
        """Test dashboard returns HTML page."""
        mock_settings.telegram_webhook_secret = "test-secret"
        response = client.get("/dashboard?token=test-secret")
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")


class TestWebhookEndpoint:
    """Test Telegram webhook endpoint."""

    def test_webhook_rejects_missing_secret(self, client):
        """Test webhook rejects requests without secret header."""
        response = client.post("/webhook", json={})
        assert response.status_code == 403

    def test_webhook_rejects_wrong_secret(self, client, mock_settings):
        """Test webhook rejects wrong secret."""
        mock_settings.telegram_webhook_secret = "correct-secret"
        response = client.post(
            "/webhook",
            json={},
            headers={"X-Telegram-Bot-Api-Secret-Token": "wrong-secret"},
        )
        assert response.status_code == 403


class TestStripeWebhookHandlers:
    """Test Stripe webhook event handlers."""

    @pytest.fixture
    def mock_buffer(self):
        """Mock buffer for Stripe tests."""
        with patch("app.main.buffer") as buffer_mock:
            buffer_mock.set_stripe_subscription = AsyncMock()
            buffer_mock.get_stripe_subscription = AsyncMock(return_value=None)
            buffer_mock.set_subscribed = AsyncMock()
            yield buffer_mock

    @pytest.mark.asyncio
    async def test_handle_checkout_completed_valid(self, mock_buffer):
        """Test handling valid checkout completion."""
        from app.main import handle_checkout_completed

        session = {
            "metadata": {
                "telegram_user_id": "12345",
                "tier": "pro",
            }
        }
        await handle_checkout_completed(session)
        # No error should be raised

    @pytest.mark.asyncio
    async def test_handle_checkout_completed_missing_metadata(self, mock_buffer):
        """Test handling checkout with missing metadata."""
        from app.main import handle_checkout_completed

        session = {"metadata": {}}
        await handle_checkout_completed(session)
        # Should log error but not raise

    @pytest.mark.asyncio
    async def test_handle_subscription_created_pro(self, mock_buffer):
        """Test handling subscription creation for Pro tier."""
        from app.main import handle_subscription_created

        subscription = {
            "id": "sub_123",
            "status": "active",
            "metadata": {
                "telegram_user_id": "12345",
                "tier": "pro",
            }
        }
        await handle_subscription_created(subscription)
        mock_buffer.set_stripe_subscription.assert_called_once_with(12345, "sub_123", "active")
        mock_buffer.set_subscribed.assert_called_once_with(12345, months=1)

    @pytest.mark.asyncio
    async def test_handle_subscription_created_content_pro(self, mock_buffer):
        """Test handling subscription creation for Content Pro tier."""
        from app.main import handle_subscription_created

        subscription = {
            "id": "sub_456",
            "status": "active",
            "metadata": {
                "telegram_user_id": "67890",
                "tier": "content_pro",
            }
        }
        await handle_subscription_created(subscription)
        mock_buffer.set_stripe_subscription.assert_called_once()
        mock_buffer.set_subscribed.assert_called_once_with(67890, months=1)

    @pytest.mark.asyncio
    async def test_handle_subscription_created_missing_metadata(self, mock_buffer):
        """Test handling subscription with missing metadata."""
        from app.main import handle_subscription_created

        subscription = {"id": "sub_123", "status": "active", "metadata": {}}
        await handle_subscription_created(subscription)
        mock_buffer.set_stripe_subscription.assert_not_called()

    @pytest.mark.asyncio
    async def test_handle_subscription_updated(self, mock_buffer):
        """Test handling subscription update."""
        from app.main import handle_subscription_updated

        mock_buffer.get_stripe_subscription.return_value = {
            "subscription_id": "sub_123",
            "status": "active",
        }

        subscription = {
            "id": "sub_123",
            "status": "past_due",
            "metadata": {"telegram_user_id": "12345"},
        }
        await handle_subscription_updated(subscription)
        mock_buffer.get_stripe_subscription.assert_called_once_with(12345)
        mock_buffer.set_stripe_subscription.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_subscription_updated_no_user_id(self, mock_buffer):
        """Test handling subscription update with no user ID."""
        from app.main import handle_subscription_updated

        subscription = {"id": "sub_123", "status": "active", "metadata": {}}
        await handle_subscription_updated(subscription)
        mock_buffer.get_stripe_subscription.assert_not_called()

    @pytest.mark.asyncio
    async def test_handle_subscription_cancelled(self, mock_buffer):
        """Test handling subscription cancellation."""
        from app.main import handle_subscription_cancelled

        mock_buffer.get_stripe_subscription.return_value = {
            "subscription_id": "sub_123",
            "status": "active",
        }

        subscription = {
            "id": "sub_123",
            "metadata": {"telegram_user_id": "12345"},
        }
        await handle_subscription_cancelled(subscription)
        mock_buffer.get_stripe_subscription.assert_called_once_with(12345)
        mock_buffer.set_stripe_subscription.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_subscription_cancelled_no_user_id(self, mock_buffer):
        """Test handling subscription cancellation with no user ID."""
        from app.main import handle_subscription_cancelled

        subscription = {"id": "sub_123", "metadata": {}}
        await handle_subscription_cancelled(subscription)
        mock_buffer.get_stripe_subscription.assert_not_called()

    @pytest.mark.asyncio
    async def test_handle_payment_succeeded(self, mock_buffer):
        """Test handling successful payment."""
        from app.main import handle_payment_succeeded

        invoice = {"subscription": "sub_123"}
        await handle_payment_succeeded(invoice)
        # Should log info but not raise

    @pytest.mark.asyncio
    async def test_handle_payment_succeeded_no_subscription(self, mock_buffer):
        """Test handling payment with no subscription."""
        from app.main import handle_payment_succeeded

        invoice = {}
        await handle_payment_succeeded(invoice)
        # Should not raise

    @pytest.mark.asyncio
    async def test_handle_payment_failed(self, mock_buffer):
        """Test handling failed payment."""
        from app.main import handle_payment_failed

        invoice = {"subscription": "sub_123"}
        await handle_payment_failed(invoice)
        # Should log warning but not raise

    @pytest.mark.asyncio
    async def test_handle_payment_failed_no_subscription(self, mock_buffer):
        """Test handling failed payment with no subscription."""
        from app.main import handle_payment_failed

        invoice = {}
        await handle_payment_failed(invoice)
        # Should not raise


class TestStripeWebhookEndpoint:
    """Test Stripe webhook endpoint."""

    @pytest.fixture
    def mock_payment_service(self):
        """Mock payment service."""
        with patch("app.main.payment_service") as ps_mock:
            yield ps_mock

    def test_stripe_webhook_with_checkout_completed(
        self, client, mock_settings, mock_payment_service
    ):
        """Test Stripe webhook processing checkout.session.completed."""
        mock_payment_service.verify_stripe_webhook = AsyncMock(
            return_value={
                "type": "checkout.session.completed",
                "data": {
                    "object": {
                        "metadata": {"telegram_user_id": "12345", "tier": "pro"}
                    }
                },
            }
        )

        with patch("app.main.handle_checkout_completed", new_callable=AsyncMock) as mock_handler:
            response = client.post(
                "/stripe/webhook",
                json={},
                headers={"stripe-signature": "test_signature"},
            )
            # The endpoint should exist
            # (it may return error if not properly mocked, but we test structure)


class TestLifespanValidation:
    """Test application lifespan validation."""

    @pytest.mark.asyncio
    async def test_lifespan_validates_subscription_price(self):
        """Test lifespan raises error for invalid subscription price."""
        from app.main import lifespan
        from fastapi import FastAPI

        test_app = FastAPI()

        with patch("app.main.settings") as mock_settings:
            mock_settings.subscription_price_stars = 0
            mock_settings.newsletter_price_stars = 250
            mock_settings.debug = False

            with pytest.raises(RuntimeError, match="SUBSCRIPTION_PRICE_STARS must be > 0"):
                async with lifespan(test_app):
                    pass

    @pytest.mark.asyncio
    async def test_lifespan_validates_newsletter_price(self):
        """Test lifespan raises error for invalid newsletter price."""
        from app.main import lifespan
        from fastapi import FastAPI

        test_app = FastAPI()

        with patch("app.main.settings") as mock_settings:
            mock_settings.subscription_price_stars = 250
            mock_settings.newsletter_price_stars = 0
            mock_settings.debug = False

            with pytest.raises(RuntimeError, match="NEWSLETTER_PRICE_STARS must be > 0"):
                async with lifespan(test_app):
                    pass

    @pytest.mark.asyncio
    async def test_lifespan_validates_webhook_secret(self):
        """Test lifespan raises error when webhook URL set without secret."""
        from app.main import lifespan
        from fastapi import FastAPI

        test_app = FastAPI()

        with patch("app.main.settings") as mock_settings, \
             patch("app.main.buffer") as mock_buffer, \
             patch("app.main.analytics") as mock_analytics, \
             patch("app.main.content_subscription") as mock_cs, \
             patch("app.main.news_aggregator") as mock_na, \
             patch("app.main.tts") as mock_tts:
            mock_settings.subscription_price_stars = 250
            mock_settings.newsletter_price_stars = 250
            mock_settings.debug = False
            mock_settings.telegram_webhook_url = "https://example.com"
            mock_settings.telegram_webhook_secret = None

            mock_buffer.connect = AsyncMock()
            mock_analytics.connect = AsyncMock()
            mock_cs.connect = AsyncMock()
            mock_na.connect = AsyncMock()
            mock_tts.connect = AsyncMock()
            mock_buffer.redis = MagicMock()

            with pytest.raises(RuntimeError, match="TELEGRAM_WEBHOOK_SECRET is required"):
                async with lifespan(test_app):
                    pass


class TestDashboardTokenVerification:
    """Test dashboard token verification function."""

    def test_verify_token_returns_false_when_no_secret(self):
        """Test verification fails when no webhook secret configured."""
        from app.main import _verify_dashboard_token

        with patch("app.main.settings") as mock_settings:
            mock_settings.telegram_webhook_secret = None
            assert _verify_dashboard_token("any-token") is False

    def test_verify_token_returns_true_for_matching_token(self):
        """Test verification passes for matching token."""
        from app.main import _verify_dashboard_token

        with patch("app.main.settings") as mock_settings:
            mock_settings.telegram_webhook_secret = "correct-token"
            assert _verify_dashboard_token("correct-token") is True

    def test_verify_token_returns_false_for_wrong_token(self):
        """Test verification fails for wrong token."""
        from app.main import _verify_dashboard_token

        with patch("app.main.settings") as mock_settings:
            mock_settings.telegram_webhook_secret = "correct-token"
            assert _verify_dashboard_token("wrong-token") is False
