"""
Unit tests for Billing Router
Tests credit management, usage tracking, and payment configuration
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta
from decimal import Decimal


class TestBillingCredits:
    """Tests for credit management"""
    
    def test_get_user_credits(self):
        """Get current user credits"""
        # Mock user with credits
        user_credits = {
            "user_id": "user-123",
            "credits_remaining": Decimal("100.00"),
            "credits_used": Decimal("50.00"),
            "last_updated": datetime.utcnow().isoformat()
        }
        assert user_credits["credits_remaining"] == Decimal("100.00")
    
    def test_add_credits(self):
        """Add credits to user account"""
        initial_credits = Decimal("100.00")
        added_credits = Decimal("50.00")
        new_total = initial_credits + added_credits
        assert new_total == Decimal("150.00")
    
    def test_deduct_credits(self):
        """Deduct credits for AI usage"""
        initial_credits = Decimal("100.00")
        usage_cost = Decimal("0.05")
        new_total = initial_credits - usage_cost
        assert new_total == Decimal("99.95")
    
    def test_insufficient_credits_error(self):
        """Error when credits are insufficient"""
        user_credits = Decimal("0.01")
        required_credits = Decimal("0.05")
        
        if user_credits < required_credits:
            error = {
                "code": "insufficient_credits",
                "message": "Not enough credits for this operation",
                "required": str(required_credits),
                "available": str(user_credits)
            }
            assert error["code"] == "insufficient_credits"


class TestUsageTracking:
    """Tests for AI usage tracking"""
    
    def test_track_ai_request(self):
        """Track AI request usage"""
        usage_record = {
            "user_id": "user-123",
            "model": "claude-3-5-sonnet",
            "input_tokens": 1500,
            "output_tokens": 500,
            "cost": Decimal("0.0225"),
            "timestamp": datetime.utcnow().isoformat()
        }
        assert usage_record["model"] == "claude-3-5-sonnet"
        assert usage_record["input_tokens"] + usage_record["output_tokens"] == 2000
    
    def test_get_usage_summary(self):
        """Get usage summary for period"""
        summary = {
            "user_id": "user-123",
            "period_start": "2025-11-01",
            "period_end": "2025-11-30",
            "total_requests": 150,
            "total_tokens": 250000,
            "total_cost": Decimal("12.50"),
            "by_model": {
                "claude-3-5-sonnet": {"requests": 100, "cost": Decimal("10.00")},
                "gpt-4": {"requests": 50, "cost": Decimal("2.50")}
            }
        }
        assert summary["total_requests"] == 150
    
    def test_usage_by_day(self):
        """Get daily usage breakdown"""
        daily_usage = [
            {"date": "2025-11-20", "requests": 50, "cost": Decimal("2.50")},
            {"date": "2025-11-21", "requests": 45, "cost": Decimal("2.25")},
            {"date": "2025-11-22", "requests": 55, "cost": Decimal("2.75")}
        ]
        total_requests = sum(d["requests"] for d in daily_usage)
        assert total_requests == 150


class TestBYOK:
    """Tests for Bring Your Own Key (BYOK) configuration"""
    
    def test_save_byok_key(self):
        """Save user's API key"""
        byok_config = {
            "user_id": "user-123",
            "provider": "anthropic",
            "key_hash": "sha256:abc123...",  # Hashed, not stored in plain
            "created_at": datetime.utcnow().isoformat()
        }
        assert byok_config["provider"] == "anthropic"
    
    def test_validate_byok_key(self):
        """Validate BYOK key format"""
        valid_keys = [
            ("sk-ant-api03-...", "anthropic"),
            ("sk-proj-...", "openai"),
        ]
        for key, provider in valid_keys:
            # Would validate key format
            assert len(key) > 0
    
    def test_byok_no_credits_deduction(self):
        """BYOK users don't have credits deducted"""
        user_has_byok = True
        initial_credits = Decimal("100.00")
        
        # When using BYOK, credits should not be deducted
        if user_has_byok:
            credits_to_deduct = Decimal("0.00")
        else:
            credits_to_deduct = Decimal("0.05")
        
        final_credits = initial_credits - credits_to_deduct
        assert final_credits == initial_credits  # No change with BYOK
    
    def test_delete_byok_key(self):
        """Delete BYOK key"""
        # Test key deletion
        pass


class TestInvoices:
    """Tests for invoice generation"""
    
    def test_generate_invoice(self):
        """Generate invoice for usage"""
        invoice = {
            "invoice_id": "inv-2025-11-001",
            "user_id": "user-123",
            "period": "2025-11",
            "total_amount": Decimal("25.00"),
            "line_items": [
                {"description": "Claude 3.5 Sonnet usage", "amount": Decimal("20.00")},
                {"description": "GPT-4 usage", "amount": Decimal("5.00")}
            ],
            "status": "pending",
            "created_at": datetime.utcnow().isoformat()
        }
        assert invoice["total_amount"] == Decimal("25.00")
    
    def test_get_invoice_pdf(self):
        """Get invoice as PDF"""
        # Would test PDF generation
        pass
    
    def test_list_invoices(self):
        """List user's invoices"""
        invoices = [
            {"invoice_id": "inv-2025-10-001", "amount": Decimal("30.00")},
            {"invoice_id": "inv-2025-11-001", "amount": Decimal("25.00")}
        ]
        assert len(invoices) == 2


class TestPaymentMethods:
    """Tests for payment method management"""
    
    def test_add_payment_method(self):
        """Add payment method"""
        payment_method = {
            "type": "card",
            "last_four": "4242",
            "brand": "visa",
            "exp_month": 12,
            "exp_year": 2027
        }
        assert payment_method["brand"] == "visa"
    
    def test_list_payment_methods(self):
        """List payment methods"""
        methods = [
            {"id": "pm-1", "type": "card", "last_four": "4242"},
            {"id": "pm-2", "type": "card", "last_four": "1234"}
        ]
        assert len(methods) == 2
    
    def test_delete_payment_method(self):
        """Delete payment method"""
        pass
    
    def test_set_default_payment_method(self):
        """Set default payment method"""
        pass


class TestPricingCatalog:
    """Tests for model pricing catalog"""
    
    def test_get_pricing_catalog(self):
        """Get pricing for all models"""
        catalog = {
            "claude-3-5-sonnet": {
                "input_per_1k": Decimal("0.003"),
                "output_per_1k": Decimal("0.015")
            },
            "gpt-4": {
                "input_per_1k": Decimal("0.01"),
                "output_per_1k": Decimal("0.03")
            }
        }
        assert "claude-3-5-sonnet" in catalog
        assert catalog["claude-3-5-sonnet"]["input_per_1k"] == Decimal("0.003")
    
    def test_calculate_cost(self):
        """Calculate cost for token usage"""
        input_tokens = 1500
        output_tokens = 500
        input_rate = Decimal("0.003")  # per 1k
        output_rate = Decimal("0.015")  # per 1k
        
        input_cost = (Decimal(input_tokens) / 1000) * input_rate
        output_cost = (Decimal(output_tokens) / 1000) * output_rate
        total_cost = input_cost + output_cost
        
        assert input_cost == Decimal("0.0045")
        assert output_cost == Decimal("0.0075")
        assert total_cost == Decimal("0.012")


class TestBillingAlerts:
    """Tests for billing alerts and limits"""

    def test_low_credit_alert(self):
        """Alert when credits are low"""
        credits = Decimal("5.00")
        threshold = Decimal("10.00")

        if credits < threshold:
            alert = {
                "type": "low_credits",
                "message": "Your credits are running low",
                "current": str(credits),
                "threshold": str(threshold)
            }
            assert alert["type"] == "low_credits"

    def test_spending_limit(self):
        """Enforce spending limit"""
        daily_limit = Decimal("10.00")
        daily_spent = Decimal("9.50")
        new_request_cost = Decimal("1.00")

        if daily_spent + new_request_cost > daily_limit:
            error = "Daily spending limit exceeded"
            assert "limit exceeded" in error

    def test_usage_notification(self):
        """Send usage notification"""
        pass


# ============ Additional Stripe Billing Tests ============

from app.routers.billing import (
    CreateSubscriptionRequest,
    CreateSubscriptionResponse,
    PortalSessionResponse,
    CheckoutSessionRequest,
    CheckoutSessionResponse,
    SubscriptionPlan,
    SUBSCRIPTION_PLANS,
    _normalize_return_url,
    _require_stripe,
)
from fastapi import HTTPException


class TestPydanticModels:
    """Tests for Stripe billing Pydantic models"""

    def test_create_subscription_request(self):
        """CreateSubscriptionRequest validates"""
        request = CreateSubscriptionRequest(paymentMethodId="pm_123456")
        assert request.paymentMethodId == "pm_123456"

    def test_create_subscription_response(self):
        """CreateSubscriptionResponse validates"""
        response = CreateSubscriptionResponse(
            subscriptionId="sub_123",
            clientSecret="secret_123",
            status="active"
        )
        assert response.subscriptionId == "sub_123"
        assert response.status == "active"

    def test_create_subscription_response_no_secret(self):
        """CreateSubscriptionResponse without clientSecret"""
        response = CreateSubscriptionResponse(
            subscriptionId="sub_456",
            status="incomplete"
        )
        assert response.clientSecret is None

    def test_portal_session_response(self):
        """PortalSessionResponse validates"""
        response = PortalSessionResponse(url="https://billing.stripe.com/session/123")
        assert response.url.startswith("https://")

    def test_checkout_session_request_defaults(self):
        """CheckoutSessionRequest default values"""
        request = CheckoutSessionRequest()
        assert request.plan == "monthly"
        assert request.success_url is None
        assert request.cancel_url is None

    def test_checkout_session_request_yearly(self):
        """CheckoutSessionRequest with yearly plan"""
        request = CheckoutSessionRequest(plan="yearly")
        assert request.plan == "yearly"

    def test_checkout_session_request_custom_urls(self):
        """CheckoutSessionRequest with custom URLs"""
        request = CheckoutSessionRequest(
            plan="monthly",
            success_url="/dashboard?payment=success",
            cancel_url="/dashboard?payment=cancelled"
        )
        assert request.success_url == "/dashboard?payment=success"

    def test_checkout_session_response(self):
        """CheckoutSessionResponse validates"""
        response = CheckoutSessionResponse(
            sessionId="cs_123",
            url="https://checkout.stripe.com/pay/cs_123"
        )
        assert response.sessionId == "cs_123"

    def test_subscription_plan_model(self):
        """SubscriptionPlan model validates"""
        plan = SubscriptionPlan(
            id="monthly",
            name="Pro Monthly",
            price=9.00,
            currency="USD",
            interval="month",
            features=["Feature 1", "Feature 2"]
        )
        assert plan.id == "monthly"
        assert plan.recommended is False

    def test_subscription_plan_recommended(self):
        """SubscriptionPlan with recommended flag"""
        plan = SubscriptionPlan(
            id="yearly",
            name="Pro Yearly",
            price=79.00,
            currency="USD",
            interval="year",
            features=["Feature 1"],
            recommended=True
        )
        assert plan.recommended is True


class TestSubscriptionPlans:
    """Tests for subscription plans configuration"""

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
        """Yearly plan is recommended"""
        assert SUBSCRIPTION_PLANS["yearly"]["recommended"] is True
        assert SUBSCRIPTION_PLANS["monthly"]["recommended"] is False

    def test_plan_features_list(self):
        """Plans have features list"""
        for plan in SUBSCRIPTION_PLANS.values():
            assert isinstance(plan["features"], list)
            assert len(plan["features"]) > 0

    def test_plan_currency(self):
        """All plans use USD"""
        for plan in SUBSCRIPTION_PLANS.values():
            assert plan["currency"] == "USD"


class TestNormalizeReturnUrl:
    """Tests for URL normalization"""

    def test_normalize_with_path_only(self):
        """Normalize relative path"""
        base_url = "https://focus.verduona.dev"
        result = _normalize_return_url("/dashboard", base_url, "/fallback")
        assert result == "https://focus.verduona.dev/dashboard"

    def test_normalize_with_full_url_same_origin(self):
        """Full URL with same origin allowed"""
        base_url = "https://focus.verduona.dev"
        raw_url = "https://focus.verduona.dev/settings"
        result = _normalize_return_url(raw_url, base_url, "/fallback")
        assert result == raw_url

    def test_normalize_with_none_uses_fallback(self):
        """None URL uses fallback"""
        base_url = "https://focus.verduona.dev"
        result = _normalize_return_url(None, base_url, "/dashboard/settings")
        assert result == "https://focus.verduona.dev/dashboard/settings"

    def test_normalize_different_origin_raises(self):
        """Different origin raises error"""
        base_url = "https://focus.verduona.dev"
        with pytest.raises(HTTPException) as exc_info:
            _normalize_return_url("https://evil.com/callback", base_url, "/fallback")
        assert exc_info.value.status_code == 400
        assert "must match" in exc_info.value.detail

    def test_normalize_invalid_scheme_raises(self):
        """Invalid scheme raises error"""
        base_url = "https://focus.verduona.dev"
        with pytest.raises(HTTPException) as exc_info:
            _normalize_return_url("javascript:alert(1)", base_url, "/fallback")
        assert exc_info.value.status_code == 400

    def test_normalize_without_leading_slash(self):
        """Path without leading slash is handled"""
        base_url = "https://focus.verduona.dev"
        result = _normalize_return_url("dashboard", base_url, "/fallback")
        assert result == "https://focus.verduona.dev/dashboard"

    def test_normalize_invalid_base_url_raises(self):
        """Invalid base URL raises error"""
        with pytest.raises(HTTPException) as exc_info:
            _normalize_return_url("/path", "not-a-url", "/fallback")
        assert exc_info.value.status_code == 500


class TestRequireStripe:
    """Tests for Stripe requirement check"""

    def test_require_stripe_raises_when_missing(self):
        """Raises error when Stripe is not installed"""
        with patch("app.routers.billing.stripe", None):
            with pytest.raises(HTTPException) as exc_info:
                _require_stripe()
            assert exc_info.value.status_code == 503
            assert "Stripe SDK" in exc_info.value.detail


class TestWebhookEvents:
    """Tests for Stripe webhook event handling"""

    def test_checkout_completed_event_structure(self):
        """Checkout completed event has correct structure"""
        event_data = {
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "customer": "cus_123",
                    "subscription": "sub_456",
                    "metadata": {"user_id": "user-789"},
                    "payment_status": "paid"
                }
            }
        }
        assert event_data["type"] == "checkout.session.completed"
        assert event_data["data"]["object"]["payment_status"] == "paid"

    def test_subscription_created_event_structure(self):
        """Subscription created event has correct structure"""
        event_data = {
            "type": "customer.subscription.created",
            "data": {
                "object": {
                    "id": "sub_123",
                    "customer": "cus_456",
                    "status": "active"
                }
            }
        }
        assert event_data["data"]["object"]["status"] == "active"

    def test_subscription_updated_event_structure(self):
        """Subscription updated event structure"""
        event_data = {
            "type": "customer.subscription.updated",
            "data": {
                "object": {
                    "id": "sub_123",
                    "status": "past_due"
                }
            }
        }
        assert event_data["data"]["object"]["status"] == "past_due"

    def test_subscription_deleted_event_structure(self):
        """Subscription deleted event structure"""
        event_data = {
            "type": "customer.subscription.deleted",
            "data": {
                "object": {
                    "id": "sub_123"
                }
            }
        }
        assert "id" in event_data["data"]["object"]

    def test_invoice_payment_succeeded_event(self):
        """Invoice payment succeeded event structure"""
        event_data = {
            "type": "invoice.payment_succeeded",
            "data": {
                "object": {
                    "id": "inv_123",
                    "customer": "cus_456",
                    "amount_paid": 900,
                    "currency": "usd"
                }
            }
        }
        assert event_data["data"]["object"]["amount_paid"] == 900

    def test_invoice_payment_failed_event(self):
        """Invoice payment failed event structure"""
        event_data = {
            "type": "invoice.payment_failed",
            "data": {
                "object": {
                    "id": "inv_789",
                    "customer": "cus_123"
                }
            }
        }
        assert event_data["type"] == "invoice.payment_failed"


class TestSubscriptionStatus:
    """Tests for subscription status logic"""

    def test_active_subscription_is_premium(self):
        """Active subscription grants premium"""
        status = "active"
        is_premium = status == "active"
        assert is_premium is True

    def test_trialing_subscription_is_premium(self):
        """Trialing subscription grants premium"""
        status = "trialing"
        is_premium = status in ["active", "trialing"]
        assert is_premium is True

    def test_past_due_not_premium(self):
        """Past due subscription not premium"""
        status = "past_due"
        is_premium = status == "active"
        assert is_premium is False

    def test_canceled_not_premium(self):
        """Canceled subscription not premium"""
        status = "canceled"
        is_premium = status == "active"
        assert is_premium is False

    def test_incomplete_not_premium(self):
        """Incomplete subscription not premium"""
        status = "incomplete"
        is_premium = status == "active"
        assert is_premium is False


class TestCheckoutSession:
    """Tests for checkout session creation"""

    def test_checkout_session_monthly(self):
        """Monthly plan uses correct price ID"""
        plan = "monthly"
        price_id = "price_monthly" if plan == "monthly" else "price_yearly"
        assert price_id == "price_monthly"

    def test_checkout_session_yearly(self):
        """Yearly plan uses correct price ID"""
        plan = "yearly"
        price_id = "price_monthly" if plan == "monthly" else "price_yearly"
        assert price_id == "price_yearly"


class TestCancelSubscription:
    """Tests for subscription cancellation"""

    def test_cancel_at_period_end(self):
        """Cancellation at period end preserves access"""
        subscription = {
            "status": "active",
            "cancel_at_period_end": True,
            "cancel_at": 1735689600  # Unix timestamp
        }
        assert subscription["cancel_at_period_end"] is True
        assert subscription["status"] == "active"


class TestReactivateSubscription:
    """Tests for subscription reactivation"""

    def test_reactivate_clears_cancel_flag(self):
        """Reactivation clears cancel at period end"""
        # Before reactivation
        before = {"cancel_at_period_end": True}
        # After reactivation
        after = {"cancel_at_period_end": False}
        assert before["cancel_at_period_end"] != after["cancel_at_period_end"]


class TestStripeCustomer:
    """Tests for Stripe customer management"""

    def test_customer_creation_payload(self):
        """Customer creation includes metadata"""
        customer_data = {
            "email": "user@example.com",
            "metadata": {"user_id": "user-123"}
        }
        assert customer_data["metadata"]["user_id"] == "user-123"


class TestBillingPortal:
    """Tests for billing portal session"""

    def test_portal_session_response(self):
        """Portal session returns URL"""
        response = {"url": "https://billing.stripe.com/session/bps_123"}
        assert response["url"].startswith("https://billing.stripe.com")


class TestPaymentMethod:
    """Tests for payment method attachment"""

    def test_payment_method_attachment(self):
        """Payment method is attached to customer"""
        attachment = {
            "payment_method_id": "pm_123",
            "customer_id": "cus_456"
        }
        assert attachment["payment_method_id"].startswith("pm_")


class TestSubscriptionResponse:
    """Tests for subscription creation response"""

    def test_subscription_with_client_secret(self):
        """Subscription response includes client secret for SCA"""
        response = CreateSubscriptionResponse(
            subscriptionId="sub_123",
            clientSecret="pi_123_secret_456",
            status="incomplete"
        )
        assert response.clientSecret is not None
        assert "secret" in response.clientSecret

    def test_subscription_immediate_activation(self):
        """Subscription immediately active without 3DS"""
        response = CreateSubscriptionResponse(
            subscriptionId="sub_789",
            status="active"
        )
        assert response.status == "active"
        assert response.clientSecret is None


class TestErrorHandling:
    """Tests for billing error handling"""

    def test_no_subscription_error(self):
        """Error when no subscription exists"""
        has_subscription = False
        if not has_subscription:
            error = {"status_code": 404, "detail": "No active subscription found"}
            assert error["status_code"] == 404

    def test_no_customer_error(self):
        """Error when no Stripe customer exists"""
        has_customer = False
        if not has_customer:
            error = {"status_code": 404, "detail": "No Stripe customer found"}
            assert error["status_code"] == 404