"""Test Stripe error sanitization to prevent information disclosure"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
import stripe as stripe_lib

from app.main import app
from app.core.security import get_current_user


@pytest.fixture
def client():
    """Create a test client"""
    return TestClient(app)


@pytest.fixture
def auth_headers():
    """Mock authentication headers"""
    return {"Authorization": "Bearer mock_token"}

@pytest.fixture
def override_current_user():
    """Override auth dependency to avoid JWT validation in tests."""
    def _override(user):
        async def _get_current_user():
            return user

        app.dependency_overrides[get_current_user] = _get_current_user

    yield _override
    app.dependency_overrides.pop(get_current_user, None)

def _attach_stripe_errors(mock_stripe):
    """Ensure mocked Stripe retains real exception hierarchy."""
    mock_stripe.error = stripe_lib.error


class TestStripeErrorSanitization:
    """Verify that Stripe errors don't leak sensitive information to clients"""

    @patch("app.routers.billing.stripe")
    async def test_checkout_session_card_error_sanitized(
        self, mock_stripe, client, auth_headers, override_current_user
    ):
        """Test that card decline errors in checkout don't leak details"""
        mock_user = Mock()
        mock_user.id = "test-user-id"
        mock_user.email = "test@example.com"
        mock_user.stripeCustomerId = None
        mock_user.stripeSubscriptionId = None
        mock_user.isPremium = False
        mock_user.activeWorkspaceId = None
        override_current_user(mock_user)
        _attach_stripe_errors(mock_stripe)

        mock_stripe.Customer.create.return_value = Mock(id="cus_test123")
        mock_stripe.checkout.Session.create.side_effect = stripe_lib.error.CardError(
            message="Your card was declined",
            param="number",
            code="card_declined",
            http_status=402,
        )

        response = client.post(
            "/billing/checkout-session", json={"plan": "monthly"}, headers=auth_headers
        )

        assert response.status_code == 400
        error_detail = response.json()["detail"]
        assert error_detail == "Payment processing failed. Please try again."
        assert "card_declined" not in error_detail
        assert "Your card was declined" not in error_detail
        assert "number" not in error_detail

    @patch("app.routers.billing.stripe")
    async def test_subscription_creation_api_error_sanitized(
        self, mock_stripe, client, auth_headers, override_current_user
    ):
        """Test that API errors in subscription creation don't leak details"""
        mock_user = Mock()
        mock_user.id = "test-user-id"
        mock_user.email = "test@example.com"
        mock_user.stripeCustomerId = "cus_test123"
        mock_user.stripeSubscriptionId = None
        mock_user.isPremium = False
        mock_user.activeWorkspaceId = None
        override_current_user(mock_user)
        _attach_stripe_errors(mock_stripe)

        mock_stripe.Customer.retrieve.return_value = Mock(id="cus_test123")
        mock_stripe.Subscription.create.side_effect = stripe_lib.error.APIError(
            message="An error occurred while connecting to Stripe's API",
            http_status=500,
        )

        response = client.post(
            "/billing/create-subscription",
            json={"paymentMethodId": "pm_test123"},
            headers=auth_headers,
        )

        assert response.status_code == 400
        error_detail = response.json()["detail"]
        assert (
            error_detail
            == "Payment processing failed. Please check your payment details."
        )
        assert "APIError" not in error_detail
        assert "Stripe's API" not in error_detail

    @patch("app.routers.billing.stripe")
    async def test_subscription_cancellation_invalid_request_sanitized(
        self, mock_stripe, client, auth_headers, override_current_user
    ):
        """Test that invalid request errors in cancellation don't leak details"""
        mock_user = Mock()
        mock_user.id = "test-user-id"
        mock_user.email = "test@example.com"
        mock_user.stripeCustomerId = "cus_test123"
        mock_user.stripeSubscriptionId = "sub_test123"
        mock_user.isPremium = False
        mock_user.activeWorkspaceId = None
        override_current_user(mock_user)
        _attach_stripe_errors(mock_stripe)

        mock_stripe.Subscription.modify.side_effect = (
            stripe_lib.error.InvalidRequestError(
                message="No such subscription: sub_test123",
                param="subscription",
                http_status=404,
            )
        )

        response = client.post("/billing/cancel-subscription", headers=auth_headers)

        assert response.status_code == 400
        error_detail = response.json()["detail"]
        assert error_detail == "Failed to cancel subscription. Please try again."
        assert "No such subscription" not in error_detail
        assert "sub_test123" not in error_detail
        assert "InvalidRequestError" not in error_detail

    @patch("app.routers.billing.stripe")
    async def test_reactivation_auth_error_sanitized(
        self, mock_stripe, client, auth_headers, override_current_user
    ):
        """Test that authentication errors in reactivation don't leak API keys"""
        mock_user = Mock()
        mock_user.id = "test-user-id"
        mock_user.email = "test@example.com"
        mock_user.stripeCustomerId = "cus_test123"
        mock_user.stripeSubscriptionId = "sub_test123"
        mock_user.isPremium = False
        mock_user.activeWorkspaceId = None
        override_current_user(mock_user)
        _attach_stripe_errors(mock_stripe)

        mock_stripe.Subscription.modify.side_effect = (
            stripe_lib.error.AuthenticationError(
                message="Invalid API Key provided: sk_test_abc123xyz789",
                http_status=401,
            )
        )

        response = client.post("/billing/reactivate-subscription", headers=auth_headers)

        assert response.status_code == 400
        error_detail = response.json()["detail"]
        assert (
            error_detail == "Failed to reactivate subscription. Please contact support."
        )
        assert "sk_test_" not in error_detail
        assert "API Key" not in error_detail
        assert "AuthenticationError" not in error_detail

    @patch("app.routers.billing.stripe")
    async def test_portal_session_rate_limit_sanitized(
        self, mock_stripe, client, auth_headers, override_current_user
    ):
        """Test that rate limit errors in portal session don't leak details"""
        mock_user = Mock()
        mock_user.id = "test-user-id"
        mock_user.email = "test@example.com"
        mock_user.stripeCustomerId = "cus_test123"
        mock_user.stripeSubscriptionId = None
        mock_user.isPremium = False
        mock_user.activeWorkspaceId = None
        override_current_user(mock_user)
        _attach_stripe_errors(mock_stripe)

        mock_stripe.billing_portal.Session.create.side_effect = (
            stripe_lib.error.RateLimitError(
                message="Rate limit exceeded", http_status=429
            )
        )

        response = client.get("/billing/portal-session", headers=auth_headers)

        assert response.status_code == 400
        error_detail = response.json()["detail"]
        assert error_detail == "Failed to access billing portal."
        assert "Rate limit" not in error_detail
        assert "RateLimitError" not in error_detail
