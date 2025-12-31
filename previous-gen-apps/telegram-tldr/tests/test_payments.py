"""Comprehensive tests for payment services."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import stripe
from fastapi import HTTPException

from app.services.payments import (
    PaymentProvider,
    PaymentService,
    StripeProvider,
    SubscriptionTier,
    TelegramStarsProvider,
)


class TestPaymentProviderEnum:
    """Test PaymentProvider enum values."""

    def test_telegram_stars_value(self):
        assert PaymentProvider.TELEGRAM_STARS == "telegram_stars"

    def test_stripe_value(self):
        assert PaymentProvider.STRIPE == "stripe"


class TestSubscriptionTierEnum:
    """Test SubscriptionTier enum values."""

    def test_free_value(self):
        assert SubscriptionTier.FREE == "free"

    def test_pro_value(self):
        assert SubscriptionTier.PRO == "pro"

    def test_content_pro_value(self):
        assert SubscriptionTier.CONTENT_PRO == "content_pro"


class TestTelegramStarsProvider:
    """Test TelegramStarsProvider functionality."""

    @pytest.fixture
    def provider(self):
        """Create a Telegram Stars provider with mocked settings."""
        with patch("app.services.payments.settings") as mock_settings:
            mock_settings.telegram_stars_provider_token = "test_token"
            mock_settings.subscription_price_stars = 250
            mock_settings.newsletter_price_stars = 400
            yield TelegramStarsProvider()

    @pytest.mark.asyncio
    async def test_create_subscription_pro_tier(self, provider):
        """Test creating PRO subscription."""
        result = await provider.create_subscription(
            tier=SubscriptionTier.PRO,
            user_id=12345,
        )

        assert result["checkout_url"] is None
        assert result["subscription_id"] == "stars_pro_12345"
        assert result["provider"] == PaymentProvider.TELEGRAM_STARS
        assert result["price_stars"] == 250
        assert result["payload"] == "sub:pro:12345"

    @pytest.mark.asyncio
    async def test_create_subscription_content_pro_tier(self, provider):
        """Test creating CONTENT_PRO subscription."""
        result = await provider.create_subscription(
            tier=SubscriptionTier.CONTENT_PRO,
            user_id=67890,
        )

        assert result["checkout_url"] is None
        assert result["subscription_id"] == "stars_content_pro_67890"
        assert result["provider"] == PaymentProvider.TELEGRAM_STARS
        assert result["price_stars"] == 400
        assert result["payload"] == "content_sub:67890"

    @pytest.mark.asyncio
    async def test_create_subscription_invalid_tier(self, provider):
        """Test creating subscription with invalid tier raises error."""
        with pytest.raises(ValueError, match="Invalid tier"):
            await provider.create_subscription(
                tier=SubscriptionTier.FREE,
                user_id=12345,
            )

    @pytest.mark.asyncio
    async def test_cancel_subscription_returns_false(self, provider):
        """Telegram Stars don't support cancel (one-time purchases)."""
        result = await provider.cancel_subscription("stars_pro_12345")
        assert result is False

    @pytest.mark.asyncio
    async def test_get_subscription_status(self, provider):
        """Test getting subscription status (always active for Stars)."""
        result = await provider.get_subscription_status("stars_pro_12345")
        assert result["status"] == "active"
        assert result["current_period_end"] is None
        assert result["cancel_at_period_end"] is False


class TestStripeProvider:
    """Test StripeProvider functionality."""

    @pytest.fixture
    def mock_stripe_client(self):
        """Create mock stripe client."""
        client = MagicMock()
        client.checkout = MagicMock()
        client.checkout.sessions = MagicMock()
        client.checkout.sessions.create = AsyncMock()
        client.subscriptions = MagicMock()
        client.subscriptions.modify = AsyncMock()
        client.subscriptions.retrieve = AsyncMock()
        return client

    @pytest.fixture
    def provider(self, mock_stripe_client):
        """Create a Stripe provider with mocked settings and client."""
        with patch("app.services.payments.settings") as mock_settings, \
             patch("app.services.payments.stripe") as mock_stripe:
            mock_settings.stripe_api_key = "sk_test_123"
            mock_settings.stripe_price_pro_monthly = "price_pro_monthly"
            mock_settings.stripe_price_pro_yearly = "price_pro_yearly"
            mock_settings.stripe_price_content_monthly = "price_content_monthly"
            mock_settings.stripe_price_content_yearly = "price_content_yearly"
            mock_settings.stripe_webhook_url = "https://stripe.bot.example.com/"
            mock_settings.telegram_webhook_url = "https://bot.example.com"

            # Create provider instance and preserve real exception classes
            mock_stripe.AsyncStripe = MagicMock(return_value=mock_stripe_client)
            mock_stripe.StripeError = stripe.StripeError
            mock_stripe.SignatureVerificationError = stripe.SignatureVerificationError
            provider = StripeProvider()
            provider.client = mock_stripe_client
            yield provider

    def test_init_without_api_key_raises_error(self):
        """Test initialization without API key raises error."""
        with patch("app.services.payments.settings") as mock_settings:
            mock_settings.stripe_api_key = None
            with pytest.raises(ValueError, match="Stripe not configured"):
                StripeProvider()

    @pytest.mark.asyncio
    async def test_create_subscription_success(self, provider, mock_stripe_client):
        """Test successful subscription creation."""
        mock_session = MagicMock()
        mock_session.url = "https://checkout.stripe.com/session/123"
        mock_session.subscription = "sub_123"
        mock_session.id = "cs_test_123"
        mock_stripe_client.checkout.sessions.create.return_value = mock_session

        result = await provider.create_subscription(
            tier=SubscriptionTier.PRO,
            user_id=12345,
            user_email="test@example.com",
            billing_interval="monthly",
        )

        assert result["checkout_url"] == "https://checkout.stripe.com/session/123"
        assert result["subscription_id"] == "sub_123"
        assert result["provider"] == PaymentProvider.STRIPE
        assert result["session_id"] == "cs_test_123"

        called_kwargs = mock_stripe_client.checkout.sessions.create.call_args.kwargs
        assert (
            called_kwargs["success_url"]
            == "https://stripe.bot.example.com/subscribe/success?session_id={CHECKOUT_SESSION_ID}"
        )
        assert called_kwargs["cancel_url"] == "https://stripe.bot.example.com/subscribe/cancel"

    @pytest.mark.asyncio
    async def test_create_subscription_invalid_tier_billing(self, provider):
        """Test creating subscription with invalid tier/billing combination."""
        with pytest.raises(ValueError, match="Invalid tier/billing_interval"):
            await provider.create_subscription(
                tier=SubscriptionTier.FREE,
                user_id=12345,
                billing_interval="monthly",
            )

    @pytest.mark.asyncio
    async def test_create_subscription_missing_price_id(self, provider):
        """Test creating subscription when price ID is not configured."""
        provider.price_ids[(SubscriptionTier.PRO, "monthly")] = None
        with pytest.raises(ValueError, match="Price ID not configured"):
            await provider.create_subscription(
                tier=SubscriptionTier.PRO,
                user_id=12345,
                billing_interval="monthly",
            )

    @pytest.mark.asyncio
    async def test_create_subscription_stripe_error(self, provider, mock_stripe_client):
        """Test handling Stripe error during subscription creation."""
        mock_stripe_client.checkout.sessions.create.side_effect = stripe.StripeError("Stripe API error")
        with pytest.raises(HTTPException) as exc_info:
            await provider.create_subscription(
                tier=SubscriptionTier.PRO,
                user_id=12345,
                billing_interval="monthly",
            )
        assert exc_info.value.status_code == 500

    @pytest.mark.asyncio
    async def test_create_subscription_falls_back_to_telegram_url(self, mock_stripe_client):
        """Fallback to Telegram webhook URL when Stripe URL is not set."""
        with patch("app.services.payments.settings") as mock_settings, \
             patch("app.services.payments.stripe") as mock_stripe:
            mock_settings.stripe_api_key = "sk_test_123"
            mock_settings.stripe_price_pro_monthly = "price_pro_monthly"
            mock_settings.stripe_price_pro_yearly = "price_pro_yearly"
            mock_settings.stripe_price_content_monthly = "price_content_monthly"
            mock_settings.stripe_price_content_yearly = "price_content_yearly"
            mock_settings.stripe_webhook_url = ""
            mock_settings.telegram_webhook_url = "https://bot.example.com"

            mock_stripe.AsyncStripe = MagicMock(return_value=mock_stripe_client)
            mock_stripe.StripeError = stripe.StripeError
            provider = StripeProvider()
            provider.client = mock_stripe_client

            mock_session = MagicMock()
            mock_session.url = "https://checkout.stripe.com/session/456"
            mock_session.subscription = "sub_456"
            mock_session.id = "cs_test_456"
            mock_stripe_client.checkout.sessions.create.return_value = mock_session

            await provider.create_subscription(
                tier=SubscriptionTier.PRO,
                user_id=12345,
                user_email="test@example.com",
                billing_interval="monthly",
            )

            called_kwargs = mock_stripe_client.checkout.sessions.create.call_args.kwargs
            assert (
                called_kwargs["success_url"]
                == "https://bot.example.com/subscribe/success?session_id={CHECKOUT_SESSION_ID}"
            )
            assert called_kwargs["cancel_url"] == "https://bot.example.com/subscribe/cancel"

    @pytest.mark.asyncio
    async def test_create_subscription_missing_base_url_raises(self, mock_stripe_client):
        """Stripe subscriptions require a public base URL."""
        with patch("app.services.payments.settings") as mock_settings, \
             patch("app.services.payments.stripe") as mock_stripe:
            mock_settings.stripe_api_key = "sk_test_123"
            mock_settings.stripe_price_pro_monthly = "price_pro_monthly"
            mock_settings.stripe_price_pro_yearly = "price_pro_yearly"
            mock_settings.stripe_price_content_monthly = "price_content_monthly"
            mock_settings.stripe_price_content_yearly = "price_content_yearly"
            mock_settings.stripe_webhook_url = ""
            mock_settings.telegram_webhook_url = ""

            mock_stripe.AsyncStripe = MagicMock(return_value=mock_stripe_client)
            mock_stripe.StripeError = stripe.StripeError
            provider = StripeProvider()
            provider.client = mock_stripe_client

            with pytest.raises(
                ValueError,
                match="Stripe not configured: set STRIPE_WEBHOOK_URL or TELEGRAM_WEBHOOK_URL",
            ):
                await provider.create_subscription(
                    tier=SubscriptionTier.PRO,
                    user_id=12345,
                    user_email="test@example.com",
                    billing_interval="monthly",
                )

    @pytest.mark.asyncio
    async def test_cancel_subscription_success(self, provider, mock_stripe_client):
        """Test successful subscription cancellation."""
        mock_stripe_client.subscriptions.modify.return_value = MagicMock()

        result = await provider.cancel_subscription("sub_123")
        assert result is True
        mock_stripe_client.subscriptions.modify.assert_called_once_with(
            "sub_123",
            cancel_at_period_end=True,
        )

    @pytest.mark.asyncio
    async def test_cancel_subscription_failure(self, provider, mock_stripe_client):
        """Test subscription cancellation failure."""
        mock_stripe_client.subscriptions.modify.side_effect = stripe.StripeError("Error")
        result = await provider.cancel_subscription("sub_123")
        assert result is False

    @pytest.mark.asyncio
    async def test_get_subscription_status_success(self, provider, mock_stripe_client):
        """Test getting subscription status."""
        mock_subscription = MagicMock()
        mock_subscription.status = "active"
        mock_subscription.current_period_end = 1735689600
        mock_subscription.cancel_at_period_end = False
        mock_stripe_client.subscriptions.retrieve.return_value = mock_subscription

        result = await provider.get_subscription_status("sub_123")
        assert result["status"] == "active"
        assert result["current_period_end"] == 1735689600
        assert result["cancel_at_period_end"] is False

    @pytest.mark.asyncio
    async def test_get_subscription_status_error(self, provider, mock_stripe_client):
        """Test getting subscription status when error occurs."""
        mock_stripe_client.subscriptions.retrieve.side_effect = stripe.StripeError("Error")
        result = await provider.get_subscription_status("sub_123")
        assert result["status"] == "unknown"
        assert result["current_period_end"] is None
        assert result["cancel_at_period_end"] is False


class TestPaymentService:
    """Test PaymentService unified interface."""

    @pytest.fixture
    def service(self):
        """Create PaymentService with mocked providers."""
        with patch("app.services.payments.settings") as mock_settings:
            mock_settings.telegram_stars_provider_token = "test_token"
            mock_settings.subscription_price_stars = 250
            mock_settings.newsletter_price_stars = 400
            mock_settings.stripe_api_key = None  # Disable Stripe for basic tests
            service = PaymentService()
            yield service

    def test_init_providers_telegram_only(self, service):
        """Test that Telegram Stars provider is initialized when configured."""
        assert PaymentProvider.TELEGRAM_STARS in service.providers
        assert isinstance(service.providers[PaymentProvider.TELEGRAM_STARS], TelegramStarsProvider)

    def test_get_provider_success(self, service):
        """Test getting a configured provider."""
        provider = service.get_provider(PaymentProvider.TELEGRAM_STARS)
        assert isinstance(provider, TelegramStarsProvider)

    def test_get_provider_not_configured(self, service):
        """Test getting an unconfigured provider raises error."""
        with pytest.raises(ValueError, match="Provider.*not configured"):
            service.get_provider(PaymentProvider.STRIPE)

    @pytest.mark.asyncio
    async def test_create_subscription(self, service):
        """Test creating subscription through unified service."""
        result = await service.create_subscription(
            provider=PaymentProvider.TELEGRAM_STARS,
            tier=SubscriptionTier.PRO,
            user_id=12345,
        )
        assert result["provider"] == PaymentProvider.TELEGRAM_STARS
        assert result["subscription_id"] == "stars_pro_12345"

    @pytest.mark.asyncio
    async def test_cancel_subscription(self, service):
        """Test cancelling subscription through unified service."""
        result = await service.cancel_subscription(
            provider=PaymentProvider.TELEGRAM_STARS,
            subscription_id="stars_pro_12345",
        )
        assert result is False  # Telegram Stars don't support cancel

    @pytest.mark.asyncio
    async def test_get_subscription_status(self, service):
        """Test getting subscription status through unified service."""
        result = await service.get_subscription_status(
            provider=PaymentProvider.TELEGRAM_STARS,
            subscription_id="stars_pro_12345",
        )
        assert result["status"] == "active"


class TestPaymentServiceWithStripe:
    """Test PaymentService with Stripe configured."""

    @pytest.fixture
    def service_with_stripe(self):
        """Create PaymentService with both providers."""
        with patch("app.services.payments.settings") as mock_settings, \
             patch("app.services.payments.stripe") as mock_stripe:
            mock_settings.telegram_stars_provider_token = "test_token"
            mock_settings.subscription_price_stars = 250
            mock_settings.newsletter_price_stars = 400
            mock_settings.stripe_api_key = "sk_test_123"
            mock_settings.stripe_price_pro_monthly = "price_pro_monthly"
            mock_settings.stripe_price_pro_yearly = "price_pro_yearly"
            mock_settings.stripe_price_content_monthly = "price_content_monthly"
            mock_settings.stripe_price_content_yearly = "price_content_yearly"
            mock_settings.telegram_webhook_url = "https://bot.example.com"

            mock_client = MagicMock()
            mock_stripe.AsyncStripe = MagicMock(return_value=mock_client)

            service = PaymentService()
            yield service

    def test_init_both_providers(self, service_with_stripe):
        """Test that both providers are initialized when configured."""
        assert PaymentProvider.TELEGRAM_STARS in service_with_stripe.providers
        assert PaymentProvider.STRIPE in service_with_stripe.providers


class TestVerifyStripeWebhook:
    """Test Stripe webhook verification."""

    @pytest.fixture
    def service(self):
        """Create PaymentService."""
        with patch("app.services.payments.settings") as mock_settings:
            mock_settings.telegram_stars_provider_token = "test_token"
            mock_settings.subscription_price_stars = 250
            mock_settings.newsletter_price_stars = 400
            mock_settings.stripe_api_key = None
            mock_settings.stripe_webhook_secret = None
            service = PaymentService()
            yield service

    @pytest.mark.asyncio
    async def test_verify_webhook_no_secret_configured(self, service):
        """Test webhook verification fails when secret not configured."""
        from fastapi import HTTPException

        mock_request = MagicMock()
        mock_request.body = AsyncMock(return_value=b'{"test": "data"}')
        mock_request.headers = {"stripe-signature": "test_sig"}

        with patch("app.services.payments.settings") as mock_settings:
            mock_settings.stripe_webhook_secret = None
            with pytest.raises(HTTPException) as exc_info:
                await service.verify_stripe_webhook(mock_request)
            assert exc_info.value.status_code == 500
            assert "not configured" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_verify_webhook_missing_signature(self, service):
        """Test webhook verification fails when signature header missing."""
        from fastapi import HTTPException

        mock_request = MagicMock()
        mock_request.body = AsyncMock(return_value=b'{"test": "data"}')
        mock_request.headers = MagicMock()
        mock_request.headers.get = MagicMock(return_value=None)

        with patch("app.services.payments.settings") as mock_settings:
            mock_settings.stripe_webhook_secret = "whsec_test"
            with pytest.raises(HTTPException) as exc_info:
                await service.verify_stripe_webhook(mock_request)
            assert exc_info.value.status_code == 400
            assert "Missing stripe-signature" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_verify_webhook_success(self, service):
        """Test successful webhook verification."""
        mock_request = MagicMock()
        mock_request.body = AsyncMock(return_value=b'{"test": "data"}')
        mock_request.headers = MagicMock()
        mock_request.headers.get = MagicMock(return_value="test_signature")

        mock_event = {"type": "checkout.session.completed", "data": {"object": {}}}

        with patch("app.services.payments.settings") as mock_settings, \
             patch("app.services.payments.stripe.Webhook.construct_event") as mock_construct:
            mock_settings.stripe_webhook_secret = "whsec_test"
            mock_construct.return_value = mock_event

            result = await service.verify_stripe_webhook(mock_request)
            assert result == mock_event

    @pytest.mark.asyncio
    async def test_verify_webhook_invalid_payload(self, service):
        """Test webhook verification fails with invalid payload."""
        from fastapi import HTTPException

        mock_request = MagicMock()
        mock_request.body = AsyncMock(return_value=b'invalid')
        mock_request.headers = MagicMock()
        mock_request.headers.get = MagicMock(return_value="test_signature")

        with patch("app.services.payments.settings") as mock_settings, \
             patch("app.services.payments.stripe.Webhook.construct_event") as mock_construct:
            mock_settings.stripe_webhook_secret = "whsec_test"
            mock_construct.side_effect = ValueError("Invalid payload")

            with pytest.raises(HTTPException) as exc_info:
                await service.verify_stripe_webhook(mock_request)
            assert exc_info.value.status_code == 400
            assert "Invalid payload" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_verify_webhook_invalid_signature(self, service):
        """Test webhook verification fails with invalid signature."""
        from fastapi import HTTPException

        mock_request = MagicMock()
        mock_request.body = AsyncMock(return_value=b'{"test": "data"}')
        mock_request.headers = MagicMock()
        mock_request.headers.get = MagicMock(return_value="invalid_signature")

        with patch("app.services.payments.settings") as mock_settings, \
             patch("app.services.payments.stripe.Webhook.construct_event") as mock_construct:
            mock_settings.stripe_webhook_secret = "whsec_test"
            mock_construct.side_effect = stripe.SignatureVerificationError(
                "Invalid signature", sig_header="test_sig"
            )

            with pytest.raises(HTTPException) as exc_info:
                await service.verify_stripe_webhook(mock_request)
            assert exc_info.value.status_code == 400


class TestGlobalPaymentService:
    """Test the global payment_service instance."""

    def test_global_instance_exists(self):
        """Test that global payment_service instance is created."""
        with patch("app.services.payments.settings") as mock_settings:
            mock_settings.telegram_stars_provider_token = None
            mock_settings.stripe_api_key = None
            from app.services.payments import payment_service
            assert payment_service is not None
            assert isinstance(payment_service, PaymentService)
