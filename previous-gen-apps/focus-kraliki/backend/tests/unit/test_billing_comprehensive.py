"""
Comprehensive Unit tests for Billing Router
Tests Stripe integration, subscriptions, and payment flows
"""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime

from app.routers.billing import (
    CreateSubscriptionRequest,
    CreateSubscriptionResponse,
    PortalSessionResponse,
    CheckoutSessionRequest,
    CheckoutSessionResponse,
    SubscriptionPlan,
    SUBSCRIPTION_PLANS,
    _normalize_return_url,
)


class TestPydanticModels:
    """Tests for billing Pydantic models"""

    def test_create_subscription_request(self):
        """CreateSubscriptionRequest validates correctly"""
        req = CreateSubscriptionRequest(paymentMethodId="pm_test_123")
        assert req.paymentMethodId == "pm_test_123"

    def test_checkout_session_request_defaults(self):
        """CheckoutSessionRequest has correct defaults"""
        req = CheckoutSessionRequest()
        assert req.plan == "monthly"
        assert req.success_url is None
        assert req.cancel_url is None

    def test_checkout_session_request_yearly(self):
        """CheckoutSessionRequest accepts yearly plan"""
        req = CheckoutSessionRequest(plan="yearly")
        assert req.plan == "yearly"

    def test_subscription_plan_model(self):
        """SubscriptionPlan validates correctly"""
        plan = SubscriptionPlan(
            id="monthly",
            name="Pro Monthly",
            price=9.00,
            currency="USD",
            interval="month",
            features=["Feature 1", "Feature 2"],
            recommended=False
        )
        assert plan.id == "monthly"
        assert plan.price == 9.00

    def test_checkout_session_response(self):
        """CheckoutSessionResponse validates correctly"""
        resp = CheckoutSessionResponse(
            sessionId="cs_test_123",
            url="https://checkout.stripe.com/c/pay/cs_test_123"
        )
        assert resp.sessionId == "cs_test_123"
        assert "checkout.stripe.com" in resp.url


class TestSubscriptionPlans:
    """Tests for subscription plan configuration"""

    def test_monthly_plan_exists(self):
        """Monthly plan is configured"""
        assert "monthly" in SUBSCRIPTION_PLANS
        plan = SUBSCRIPTION_PLANS["monthly"]
        assert plan["price"] == 9.00
        assert plan["interval"] == "month"

    def test_yearly_plan_exists(self):
        """Yearly plan is configured"""
        assert "yearly" in SUBSCRIPTION_PLANS
        plan = SUBSCRIPTION_PLANS["yearly"]
        assert plan["price"] == 79.00
        assert plan["interval"] == "year"

    def test_yearly_plan_recommended(self):
        """Yearly plan is marked as recommended"""
        assert SUBSCRIPTION_PLANS["yearly"]["recommended"] is True
        assert SUBSCRIPTION_PLANS["monthly"]["recommended"] is False

    def test_plans_have_features(self):
        """Plans have feature lists"""
        for plan_id, plan in SUBSCRIPTION_PLANS.items():
            assert "features" in plan
            assert len(plan["features"]) > 0


class TestNormalizeReturnUrl:
    """Tests for URL normalization helper"""

    def test_normalize_none_url(self):
        """None URL returns fallback path"""
        result = _normalize_return_url(
            None,
            "https://app.example.com",
            "/dashboard"
        )
        assert result == "https://app.example.com/dashboard"

    def test_normalize_relative_path(self):
        """Relative path is joined with base"""
        result = _normalize_return_url(
            "/settings",
            "https://app.example.com",
            "/dashboard"
        )
        assert result == "https://app.example.com/settings"

    def test_normalize_full_matching_url(self):
        """Full URL matching base is accepted"""
        result = _normalize_return_url(
            "https://app.example.com/custom",
            "https://app.example.com",
            "/dashboard"
        )
        assert result == "https://app.example.com/custom"

    def test_normalize_different_host_rejected(self):
        """Different host URL is rejected"""
        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc_info:
            _normalize_return_url(
                "https://evil.com/phishing",
                "https://app.example.com",
                "/dashboard"
            )
        assert exc_info.value.status_code == 400

    def test_normalize_invalid_scheme_rejected(self):
        """Invalid URL scheme is rejected"""
        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc_info:
            _normalize_return_url(
                "javascript:alert(1)",
                "https://app.example.com",
                "/dashboard"
            )
        assert exc_info.value.status_code == 400

    def test_normalize_missing_base_scheme(self):
        """Missing base URL scheme raises error"""
        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc_info:
            _normalize_return_url(
                "/path",
                "app.example.com",  # Missing scheme
                "/dashboard"
            )
        assert exc_info.value.status_code == 500


class TestGetPlansEndpoint:
    """Tests for get subscription plans endpoint"""

    def test_get_plans_returns_all(self, client):
        """Get plans returns all available plans"""
        response = client.get("/billing/plans")
        assert response.status_code == 200
        data = response.json()
        assert "plans" in data
        assert "currency" in data
        assert data["currency"] == "USD"
        assert len(data["plans"]) == 2

    def test_get_plans_structure(self, client):
        """Plans have correct structure"""
        response = client.get("/billing/plans")
        data = response.json()

        for plan in data["plans"]:
            assert "id" in plan
            assert "name" in plan
            assert "price" in plan
            assert "interval" in plan
            assert "features" in plan


class TestCheckoutSessionEndpoint:
    """Tests for checkout session creation"""

    def test_create_checkout_session_monthly(self, client, db, test_user, auth_headers):
        """Create checkout session for monthly plan"""
        with patch("app.routers.billing.stripe") as mock_stripe:
            # Mock customer creation
            mock_stripe.Customer.create.return_value = MagicMock(id="cus_test123")

            # Mock session creation
            mock_session = MagicMock()
            mock_session.id = "cs_test_session"
            mock_session.url = "https://checkout.stripe.com/c/pay/cs_test"
            mock_stripe.checkout.Session.create.return_value = mock_session

            response = client.post(
                "/billing/checkout-session",
                json={"plan": "monthly"},
                headers=auth_headers
            )

        assert response.status_code == 200
        data = response.json()
        assert data["sessionId"] == "cs_test_session"
        assert "url" in data

    def test_create_checkout_session_yearly(self, client, db, test_user, auth_headers):
        """Create checkout session for yearly plan"""
        with patch("app.routers.billing.stripe") as mock_stripe:
            mock_stripe.Customer.create.return_value = MagicMock(id="cus_test123")
            mock_session = MagicMock()
            mock_session.id = "cs_test_yearly"
            mock_session.url = "https://checkout.stripe.com/c/pay/cs_yearly"
            mock_stripe.checkout.Session.create.return_value = mock_session

            response = client.post(
                "/billing/checkout-session",
                json={"plan": "yearly"},
                headers=auth_headers
            )

        assert response.status_code == 200

    def test_checkout_session_unauthorized(self, client):
        """Checkout requires authentication"""
        response = client.post(
            "/billing/checkout-session",
            json={"plan": "monthly"}
        )
        assert response.status_code in [401, 422]


class TestSubscriptionStatusEndpoint:
    """Tests for subscription status endpoint"""

    def test_get_status_no_subscription(self, client, db, test_user, auth_headers):
        """Get status for user without subscription"""
        response = client.get("/billing/subscription-status", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["hasSubscription"] is False

    def test_get_status_with_subscription(self, client, db, test_user, auth_headers):
        """Get status for user with subscription"""
        test_user.stripeSubscriptionId = "sub_test123"
        db.commit()

        with patch("app.routers.billing.stripe") as mock_stripe:
            mock_sub = MagicMock()
            mock_sub.status = "active"
            mock_sub.current_period_end = 1735689600  # Timestamp
            mock_sub.cancel_at_period_end = False
            mock_stripe.Subscription.retrieve.return_value = mock_sub

            response = client.get("/billing/subscription-status", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["hasSubscription"] is True
        assert data["status"] == "active"


class TestCancelSubscriptionEndpoint:
    """Tests for subscription cancellation"""

    def test_cancel_subscription_no_active(self, client, db, test_user, auth_headers):
        """Cancel fails without active subscription"""
        response = client.post("/billing/cancel-subscription", headers=auth_headers)
        assert response.status_code == 404

    def test_cancel_subscription_success(self, client, db, test_user, auth_headers):
        """Cancel subscription successfully"""
        test_user.stripeSubscriptionId = "sub_test123"
        db.commit()

        with patch("app.routers.billing.stripe") as mock_stripe:
            mock_sub = MagicMock()
            mock_sub.cancel_at = 1735689600
            mock_stripe.Subscription.modify.return_value = mock_sub

            response = client.post("/billing/cancel-subscription", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True


class TestReactivateSubscriptionEndpoint:
    """Tests for subscription reactivation"""

    def test_reactivate_no_subscription(self, client, db, test_user, auth_headers):
        """Reactivate fails without subscription"""
        response = client.post("/billing/reactivate-subscription", headers=auth_headers)
        assert response.status_code == 404

    def test_reactivate_success(self, client, db, test_user, auth_headers):
        """Reactivate subscription successfully"""
        test_user.stripeSubscriptionId = "sub_test123"
        db.commit()

        with patch("app.routers.billing.stripe") as mock_stripe:
            mock_sub = MagicMock()
            mock_sub.status = "active"
            mock_stripe.Subscription.modify.return_value = mock_sub

            response = client.post("/billing/reactivate-subscription", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True


class TestPortalSessionEndpoint:
    """Tests for customer portal session"""

    def test_portal_session_no_customer(self, client, db, test_user, auth_headers):
        """Portal fails without Stripe customer"""
        response = client.get("/billing/portal-session", headers=auth_headers)
        assert response.status_code == 404

    def test_portal_session_success(self, client, db, test_user, auth_headers):
        """Portal session created successfully"""
        test_user.stripeCustomerId = "cus_test123"
        db.commit()

        with patch("app.routers.billing.stripe") as mock_stripe:
            mock_session = MagicMock()
            mock_session.url = "https://billing.stripe.com/p/session/test"
            mock_stripe.billing_portal.Session.create.return_value = mock_session

            response = client.get("/billing/portal-session", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert "url" in data
        assert "billing.stripe.com" in data["url"]


class TestStripeWebhook:
    """Tests for Stripe webhook handling"""

    def test_webhook_missing_secret(self, client, db):
        """Webhook fails without configured secret"""
        response = client.post(
            "/billing/webhook",
            content=b"{}",
            headers={"stripe-signature": "test"}
        )
        # May return 500 if secret not configured
        assert response.status_code in [400, 500]

    def test_webhook_checkout_completed(self, client, db, test_user):
        """Webhook handles checkout.session.completed"""
        test_user.stripeCustomerId = "cus_test123"
        db.commit()

        with patch("app.routers.billing.STRIPE_WEBHOOK_SECRET", "whsec_test"), \
             patch("app.routers.billing.stripe") as mock_stripe:

            mock_stripe.Webhook.construct_event.return_value = {
                "type": "checkout.session.completed",
                "data": {
                    "object": {
                        "customer": "cus_test123",
                        "subscription": "sub_new123",
                        "metadata": {"user_id": test_user.id},
                        "payment_status": "paid"
                    }
                }
            }

            mock_sub = MagicMock()
            mock_sub.status = "active"
            mock_stripe.Subscription.retrieve.return_value = mock_sub

            response = client.post(
                "/billing/webhook",
                content=b'{"test": "data"}',
                headers={"stripe-signature": "test_sig"}
            )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_webhook_subscription_updated(self, client, db, test_user):
        """Webhook handles customer.subscription.updated"""
        test_user.stripeSubscriptionId = "sub_test123"
        db.commit()

        with patch("app.routers.billing.STRIPE_WEBHOOK_SECRET", "whsec_test"), \
             patch("app.routers.billing.stripe") as mock_stripe:

            mock_stripe.Webhook.construct_event.return_value = {
                "type": "customer.subscription.updated",
                "data": {
                    "object": {
                        "id": "sub_test123",
                        "status": "active"
                    }
                }
            }

            response = client.post(
                "/billing/webhook",
                content=b'{"test": "data"}',
                headers={"stripe-signature": "test_sig"}
            )

        assert response.status_code == 200

    def test_webhook_subscription_deleted(self, client, db, test_user):
        """Webhook handles customer.subscription.deleted"""
        test_user.stripeSubscriptionId = "sub_test123"
        test_user.isPremium = True
        db.commit()

        with patch("app.routers.billing.STRIPE_WEBHOOK_SECRET", "whsec_test"), \
             patch("app.routers.billing.stripe") as mock_stripe:

            mock_stripe.Webhook.construct_event.return_value = {
                "type": "customer.subscription.deleted",
                "data": {
                    "object": {
                        "id": "sub_test123"
                    }
                }
            }

            response = client.post(
                "/billing/webhook",
                content=b'{"test": "data"}',
                headers={"stripe-signature": "test_sig"}
            )

        assert response.status_code == 200

        # Verify premium status updated
        db.refresh(test_user)
        assert test_user.isPremium is False

    def test_webhook_invoice_payment_succeeded(self, client, db, test_user):
        """Webhook handles invoice.payment_succeeded"""
        test_user.stripeCustomerId = "cus_test123"
        db.commit()

        with patch("app.routers.billing.STRIPE_WEBHOOK_SECRET", "whsec_test"), \
             patch("app.routers.billing.stripe") as mock_stripe:

            mock_stripe.Webhook.construct_event.return_value = {
                "type": "invoice.payment_succeeded",
                "data": {
                    "object": {
                        "customer": "cus_test123",
                        "id": "in_test123",
                        "amount_paid": 900,
                        "currency": "usd"
                    }
                }
            }

            response = client.post(
                "/billing/webhook",
                content=b'{"test": "data"}',
                headers={"stripe-signature": "test_sig"}
            )

        assert response.status_code == 200

        # Verify premium status enabled
        db.refresh(test_user)
        assert test_user.isPremium is True
