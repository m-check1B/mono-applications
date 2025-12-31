"""
Stripe Subscription & Billing Router for Voice by Kraliki
Handles subscription creation, management, and webhooks
Supports both CC-Lite (B2B) and Voice of People (B2C) plans
"""

import logging
import os
from typing import Literal
from urllib.parse import urljoin, urlparse

import stripe
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.jwt_auth import get_current_user
from app.config.settings import get_settings
from app.database import get_db
from app.middleware.rate_limit import BILLING_RATE_LIMIT, WEBHOOK_RATE_LIMIT, limiter
from app.models.user import User

logger = logging.getLogger(__name__)
settings = get_settings()

router = APIRouter(prefix="/api/v1/billing", tags=["billing"])

# Initialize Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")

# Price IDs from environment or defaults for CC-Lite (B2B)
STRIPE_PRICE_ID_CCLITE_STARTER = os.getenv(
    "STRIPE_PRICE_ID_CCLITE_STARTER", "price_cclite_starter_1500"
)
STRIPE_PRICE_ID_CCLITE_PROFESSIONAL = os.getenv(
    "STRIPE_PRICE_ID_CCLITE_PROFESSIONAL", "price_cclite_pro_3500"
)
STRIPE_PRICE_ID_CCLITE_EARLY_ADOPTER = os.getenv(
    "STRIPE_PRICE_ID_CCLITE_EARLY_ADOPTER", "price_cclite_early_adopter_750"
)

# Price IDs for Voice of People (B2C)
STRIPE_PRICE_ID_VOP_PERSONAL = os.getenv("STRIPE_PRICE_ID_VOP_PERSONAL", "price_vop_personal_999")
STRIPE_PRICE_ID_VOP_PREMIUM = os.getenv("STRIPE_PRICE_ID_VOP_PREMIUM", "price_vop_premium_2999")
STRIPE_PRICE_ID_VOP_PRO = os.getenv("STRIPE_PRICE_ID_VOP_PRO", "price_vop_pro_9999")

# CC-Lite (B2B) subscription plans
CCLITE_PLANS = {
    "starter": {
        "id": "starter",
        "name": "Starter",
        "product": "cc_lite",
        "price": 1500.00,
        "currency": "USD",
        "interval": "month",
        "features": [
            "Up to 5 agents",
            "1,000 AI minutes included",
            "Basic IVR setup",
            "Standard call routing",
            "Real-time monitoring dashboard",
        ],
        "recommended": False,
    },
    "early_adopter": {
        "id": "early_adopter",
        "name": "Early Adopter (50% OFF)",
        "product": "cc_lite",
        "price": 750.00,
        "currency": "USD",
        "interval": "month",
        "features": [
            "Limited Time Offer: 50% OFF for first 3 months",
            "Up to 10 agents",
            "2,000 AI minutes included",
            "Advanced call flows",
            "Campaign management",
            "Priority support",
        ],
        "recommended": False,
    },
    "professional": {
        "id": "professional",
        "name": "Professional",
        "product": "cc_lite",
        "price": 3500.00,
        "currency": "USD",
        "interval": "month",
        "features": [
            "Up to 15 agents",
            "3,000 AI minutes included",
            "Advanced call flows",
            "Campaign management",
            "Call analytics & reporting",
            "Priority support",
        ],
        "recommended": True,
    },
}

# Voice of People (B2C) subscription plans
VOP_PLANS = {
    "personal": {
        "id": "personal",
        "name": "Personal",
        "product": "vop",
        "price": 9.99,
        "currency": "USD",
        "interval": "month",
        "voice_minutes_included": 100,
        "features": [
            "100 AI voice minutes/month",
            "Full voice input + output",
            "Conversation history",
            "Mobile app access",
            "Email support",
        ],
        "recommended": False,
    },
    "premium": {
        "id": "premium",
        "name": "Premium",
        "product": "vop",
        "price": 29.99,
        "currency": "USD",
        "interval": "month",
        "voice_minutes_included": 500,
        "features": [
            "500 AI voice minutes/month",
            "Priority response time",
            "Custom voice personalities",
            "Advanced conversation modes",
            "Priority support",
        ],
        "recommended": True,
    },
    "pro": {
        "id": "pro",
        "name": "Pro",
        "product": "vop",
        "price": 99.99,
        "currency": "USD",
        "interval": "month",
        "voice_minutes_included": 2000,
        "features": [
            "2,000 AI voice minutes/month",
            "API access",
            "Custom integrations",
            "Business use license",
            "Dedicated support",
        ],
        "recommended": False,
    },
}


def _normalize_return_url(raw_url: str | None, base_url: str, fallback_path: str) -> str:
    base = urlparse(base_url)
    if not base.scheme or not base.netloc:
        return urljoin("https://voice.kraliki.com", fallback_path.lstrip("/"))

    base_origin = f"{base.scheme}://{base.netloc}"

    if not raw_url:
        return urljoin(f"{base_origin}/", fallback_path.lstrip("/"))

    parsed = urlparse(raw_url)
    if parsed.scheme or parsed.netloc:
        return raw_url

    path = raw_url if raw_url.startswith("/") else f"/{raw_url}"
    return urljoin(f"{base_origin}/", path.lstrip("/"))


class CheckoutSessionRequest(BaseModel):
    product: Literal["cc_lite", "vop"] = "vop"
    plan: str
    success_url: str | None = None
    cancel_url: str | None = None


class CheckoutSessionResponse(BaseModel):
    sessionId: str
    url: str


class PortalSessionResponse(BaseModel):
    url: str


@router.get("/plans")
async def get_subscription_plans():
    """Get available subscription plans with pricing"""
    return {
        "plans": list(CCLITE_PLANS.values()),  # For backward compatibility
        "cc_lite": list(CCLITE_PLANS.values()),
        "vop": list(VOP_PLANS.values()),
        "currency": "USD",
    }


@router.post("/checkout-session", response_model=CheckoutSessionResponse)
@limiter.limit(BILLING_RATE_LIMIT)
async def create_checkout_session(
    request: Request,
    request_data: CheckoutSessionRequest,
    current_user_data: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a Stripe Checkout session for subscription purchase.
    Supports both CC-Lite (B2B) and Voice of People (B2C) plans.
    Rate limited to prevent billing abuse.
    """
    # Get full user object from DB - User.id is UUID string
    user_id = str(current_user_data["sub"])
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get price ID based on product and plan
    if request_data.product == "cc_lite":
        if request_data.plan == "professional":
            price_id = STRIPE_PRICE_ID_CCLITE_PROFESSIONAL
        elif request_data.plan == "early_adopter":
            price_id = STRIPE_PRICE_ID_CCLITE_EARLY_ADOPTER
        else:
            price_id = STRIPE_PRICE_ID_CCLITE_STARTER
    else:  # vop
        if request_data.plan == "premium":
            price_id = STRIPE_PRICE_ID_VOP_PREMIUM
        elif request_data.plan == "pro":
            price_id = STRIPE_PRICE_ID_VOP_PRO
        else:
            price_id = STRIPE_PRICE_ID_VOP_PERSONAL

    # Default URLs
    base_url = os.getenv("FRONTEND_URL", "https://voice.kraliki.com")
    success_url = _normalize_return_url(
        request_data.success_url, base_url, "/settings/billing?payment=success"
    )
    cancel_url = _normalize_return_url(
        request_data.cancel_url, base_url, "/settings/billing?payment=cancelled"
    )

    try:
        # Create or retrieve Stripe customer
        if not user.stripe_customer_id:
            customer = stripe.Customer.create(
                email=user.email, name=user.full_name, metadata={"user_id": user.id}
            )
            user.stripe_customer_id = customer.id
            await db.commit()

        # Create Checkout Session
        session = stripe.checkout.Session.create(
            customer=user.stripe_customer_id,
            payment_method_types=["card"],
            line_items=[{"price": price_id, "quantity": 1}],
            mode="subscription",
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={
                "user_id": user.id,
                "product": request_data.product,
                "plan": request_data.plan,
            },
        )

        return CheckoutSessionResponse(sessionId=session.id, url=session.url)

    except stripe.error.StripeError as e:
        logger.error(f"Stripe error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/portal-session", response_model=PortalSessionResponse)
async def create_portal_session(
    current_user_data: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    return_url: str | None = None,
):
    """Create a Stripe Customer Portal session for subscription management"""
    user_id = str(current_user_data["sub"])
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user or not user.stripe_customer_id:
        raise HTTPException(status_code=404, detail="Stripe customer not found")

    try:
        base_url = os.getenv("FRONTEND_URL", "https://voice.kraliki.com")
        normalized_return_url = _normalize_return_url(return_url, base_url, "/settings/billing")
        session = stripe.billing_portal.Session.create(
            customer=user.stripe_customer_id, return_url=normalized_return_url
        )

        return PortalSessionResponse(url=session.url)

    except stripe.error.StripeError as e:
        logger.error(f"Stripe error: {str(e)}")
        raise HTTPException(status_code=400, detail="Failed to access billing portal.")


@router.post("/webhook")
@limiter.limit(WEBHOOK_RATE_LIMIT)
async def stripe_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    """
    Handle Stripe webhooks. Rate limited to prevent abuse.
    """
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    if not STRIPE_WEBHOOK_SECRET:
        raise HTTPException(status_code=500, detail="Webhook secret not configured")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, STRIPE_WEBHOOK_SECRET)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Handle event
    event_type = event["type"]
    data = event["data"]["object"]

    if event_type == "checkout.session.completed":
        customer_id = data.get("customer")
        subscription_id = data.get("subscription")
        user_id = data.get("metadata", {}).get("user_id")

        if user_id:
            # User.id is a UUID string, no int conversion needed
            result = await db.execute(select(User).where(User.id == str(user_id)))
            user = result.scalar_one_or_none()
            if user:
                user.stripe_customer_id = customer_id
                user.stripe_subscription_id = subscription_id
                user.is_premium = True

                # Store plan and product in preferences
                product = data.get("metadata", {}).get("product", "vop")
                plan = data.get("metadata", {}).get("plan", "personal")
                user.preferences = user.preferences or {}
                user.preferences.update({"subscription": {"product": product, "plan": plan}})

                await db.commit()
                logger.info(f"Subscription activated for user {user_id}: {product}/{plan}")

    elif event_type == "customer.subscription.deleted":
        subscription_id = data["id"]
        result = await db.execute(
            select(User).where(User.stripe_subscription_id == subscription_id)
        )
        user = result.scalar_one_or_none()
        if user:
            user.is_premium = False
            user.preferences = user.preferences or {}
            user.preferences["subscription"] = {"product": None, "plan": None}
            await db.commit()
            logger.info(f"Subscription canceled for user {user.id}")

    return {"success": True}
