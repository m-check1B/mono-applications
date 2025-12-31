"""
Stripe Subscription & Billing Router
Handles subscription creation, management, and webhooks
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, Literal
from urllib.parse import urlparse, urljoin
import os

try:
    import stripe  # type: ignore
except ImportError:  # pragma: no cover - optional dependency
    stripe = None

from app.core.security import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.core.events import event_publisher
from app.services.workspace_service import WorkspaceService
from app.middleware.rate_limit import limiter
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/billing", tags=["billing"])

# Initialize Stripe
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")
STRIPE_PRICE_ID_MONTHLY = os.getenv("STRIPE_PRICE_ID_MONTHLY", "price_monthly")
STRIPE_PRICE_ID_YEARLY = os.getenv("STRIPE_PRICE_ID_YEARLY", "price_yearly")
# Backwards compat
PRICE_ID_PREMIUM = os.getenv("STRIPE_PRICE_ID_PREMIUM", STRIPE_PRICE_ID_MONTHLY)

if stripe:
    stripe.api_key = os.getenv("STRIPE_SECRET_KEY")


def _require_stripe():
    if not stripe:
        raise HTTPException(status_code=503, detail="Stripe SDK is not installed in this environment.")


def _normalize_return_url(raw_url: Optional[str], base_url: str, fallback_path: str) -> str:
    base = urlparse(base_url)
    if not base.scheme or not base.netloc:
        raise HTTPException(status_code=500, detail="FRONTEND_URL must include scheme and host.")

    base_origin = f"{base.scheme}://{base.netloc}"

    if not raw_url:
        return urljoin(f"{base_origin}/", fallback_path.lstrip("/"))

    parsed = urlparse(raw_url)
    if parsed.scheme or parsed.netloc:
        if parsed.scheme not in ("http", "https"):
            raise HTTPException(status_code=400, detail="Invalid return URL scheme.")
        if parsed.scheme != base.scheme or parsed.netloc != base.netloc:
            raise HTTPException(status_code=400, detail="Return URL must match configured frontend domain.")
        return raw_url

    path = raw_url if raw_url.startswith("/") else f"/{raw_url}"
    return urljoin(f"{base_origin}/", path.lstrip("/"))

class CreateSubscriptionRequest(BaseModel):
    paymentMethodId: str

class CreateSubscriptionResponse(BaseModel):
    subscriptionId: str
    clientSecret: Optional[str] = None
    status: str

class PortalSessionResponse(BaseModel):
    url: str

class CheckoutSessionRequest(BaseModel):
    plan: Literal["monthly", "yearly"] = "monthly"
    success_url: Optional[str] = None
    cancel_url: Optional[str] = None

class CheckoutSessionResponse(BaseModel):
    sessionId: str
    url: str

class SubscriptionPlan(BaseModel):
    id: str
    name: str
    price: float
    currency: str
    interval: str
    features: list[str]
    recommended: bool = False

# Subscription plans configuration
SUBSCRIPTION_PLANS = {
    "monthly": {
        "id": "monthly",
        "name": "Pro Monthly",
        "price": 9.00,
        "currency": "USD",
        "interval": "month",
        "features": [
            "Unlimited AI requests",
            "Priority support",
            "Advanced analytics",
            "Calendar sync",
            "Voice commands",
            "Team features (coming soon)"
        ],
        "recommended": False
    },
    "yearly": {
        "id": "yearly",
        "name": "Pro Yearly",
        "price": 79.00,
        "currency": "USD",
        "interval": "year",
        "features": [
            "Unlimited AI requests",
            "Priority support",
            "Advanced analytics",
            "Calendar sync",
            "Voice commands",
            "Team features (coming soon)",
            "2 months free (save $29)"
        ],
        "recommended": True
    }
}


@router.get("/plans")
async def get_subscription_plans():
    """Get available subscription plans with pricing"""
    return {
        "plans": list(SUBSCRIPTION_PLANS.values()),
        "currency": "USD"
    }


@router.post("/checkout-session", response_model=CheckoutSessionResponse)
@limiter.limit("10/minute")
async def create_checkout_session(
    request: Request,
    request_data: CheckoutSessionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a Stripe Checkout session for subscription purchase.
    Redirects user to Stripe's hosted checkout page.

    Rate limited: 10 requests per minute per IP.
    """
    _require_stripe()

    # Get price ID based on plan
    if request_data.plan == "yearly":
        price_id = STRIPE_PRICE_ID_YEARLY
    else:
        price_id = STRIPE_PRICE_ID_MONTHLY

    # Default URLs
    base_url = os.getenv("FRONTEND_URL", "http://127.0.0.1:5175")
    success_url = _normalize_return_url(
        request_data.success_url,
        base_url,
        "/dashboard/settings?payment=success"
    )
    cancel_url = _normalize_return_url(
        request_data.cancel_url,
        base_url,
        "/dashboard/settings?payment=cancelled"
    )

    try:
        # Create or retrieve Stripe customer
        if not current_user.stripeCustomerId:
            customer = stripe.Customer.create(
                email=current_user.email,
                metadata={"user_id": current_user.id}
            )
            current_user.stripeCustomerId = customer.id
            db.commit()

        # Check if user already has an active subscription
        if current_user.stripeSubscriptionId:
            try:
                existing_sub = stripe.Subscription.retrieve(current_user.stripeSubscriptionId)
                if existing_sub.status in ["active", "trialing"]:
                    raise HTTPException(
                        status_code=400,
                        detail="You already have an active subscription. Please manage it from the billing portal."
                    )
            except stripe.error.InvalidRequestError:
                # Subscription doesn't exist anymore
                current_user.stripeSubscriptionId = None
                db.commit()

        # Create Checkout Session
        session = stripe.checkout.Session.create(
            customer=current_user.stripeCustomerId,
            payment_method_types=["card"],
            line_items=[{
                "price": price_id,
                "quantity": 1
            }],
            mode="subscription",
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={
                "user_id": current_user.id,
                "plan": request_data.plan
            },
            subscription_data={
                "metadata": {
                    "user_id": current_user.id,
                    "plan": request_data.plan
                }
            },
            allow_promotion_codes=True
        )

        return CheckoutSessionResponse(
            sessionId=session.id,
            url=session.url
        )

    except stripe.error.StripeError as e:
        logger.error(f"Stripe error during checkout session creation: {str(e)}")
        raise HTTPException(status_code=400, detail="Payment processing failed. Please try again.")
    except Exception as e:
        logger.error(f"Unexpected error during checkout session creation: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred. Please contact support.")


@router.post("/create-subscription", response_model=CreateSubscriptionResponse)
@limiter.limit("10/minute")
async def create_subscription(
    request: Request,
    request_data: CreateSubscriptionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a Stripe subscription for premium access ($9/month).

    Rate limited: 10 requests per minute per IP.
    """
    _require_stripe()

    try:
        # Create or retrieve Stripe customer
        if not current_user.stripeCustomerId:
            customer = stripe.Customer.create(
                email=current_user.email,
                metadata={"user_id": current_user.id}
            )
            current_user.stripeCustomerId = customer.id
            db.commit()
        else:
            customer = stripe.Customer.retrieve(current_user.stripeCustomerId)

        # Attach payment method to customer
        stripe.PaymentMethod.attach(
            request_data.paymentMethodId,
            customer=current_user.stripeCustomerId
        )

        # Set as default payment method
        stripe.Customer.modify(
            current_user.stripeCustomerId,
            invoice_settings={"default_payment_method": request_data.paymentMethodId}
        )

        # Create subscription
        subscription = stripe.Subscription.create(
            customer=current_user.stripeCustomerId,
            items=[{"price": PRICE_ID_PREMIUM}],
            payment_settings={
                "payment_method_types": ["card"],
                "save_default_payment_method": "on_subscription"
            },
            expand=["latest_invoice.payment_intent"]
        )

        # Update user record
        current_user.stripeSubscriptionId = subscription.id
        current_user.isPremium = subscription.status == "active"
        db.commit()

        return CreateSubscriptionResponse(
            subscriptionId=subscription.id,
            clientSecret=subscription.latest_invoice.payment_intent.client_secret if subscription.latest_invoice else None,
            status=subscription.status
        )

    except stripe.error.StripeError as e:
        logger.error(f"Stripe error during subscription creation: {str(e)}")
        raise HTTPException(status_code=400, detail="Payment processing failed. Please check your payment details.")
    except Exception as e:
        logger.error(f"Unexpected error during subscription creation: {str(e)}")
        raise HTTPException(status_code=500, detail="Subscription creation failed. Please try again later.")


@router.post("/cancel-subscription")
async def cancel_subscription(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cancel the user's subscription at period end"""
    if not current_user.stripeSubscriptionId:
        raise HTTPException(status_code=404, detail="No active subscription found")

    _require_stripe()

    try:
        subscription = stripe.Subscription.modify(
            current_user.stripeSubscriptionId,
            cancel_at_period_end=True
        )

        return {
            "success": True,
            "message": "Subscription will be canceled at period end",
            "cancel_at": subscription.cancel_at
        }

    except stripe.error.StripeError as e:
        logger.error(f"Stripe error during subscription cancellation: {str(e)}")
        raise HTTPException(status_code=400, detail="Failed to cancel subscription. Please try again.")


@router.post("/reactivate-subscription")
async def reactivate_subscription(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Reactivate a canceled subscription"""
    if not current_user.stripeSubscriptionId:
        raise HTTPException(status_code=404, detail="No subscription found")

    _require_stripe()

    try:
        subscription = stripe.Subscription.modify(
            current_user.stripeSubscriptionId,
            cancel_at_period_end=False
        )

        current_user.isPremium = subscription.status == "active"
        db.commit()

        return {
            "success": True,
            "message": "Subscription reactivated",
            "status": subscription.status
        }

    except stripe.error.StripeError as e:
        logger.error(f"Stripe error during subscription reactivation: {str(e)}")
        raise HTTPException(status_code=400, detail="Failed to reactivate subscription. Please contact support.")


@router.get("/portal-session", response_model=PortalSessionResponse)
async def create_portal_session(
    current_user: User = Depends(get_current_user),
    return_url: Optional[str] = None
):
    """Create a Stripe Customer Portal session for subscription management"""
    if not current_user.stripeCustomerId:
        raise HTTPException(status_code=404, detail="No Stripe customer found")

    _require_stripe()

    try:
        base_url = os.getenv("FRONTEND_URL", "http://127.0.0.1:5175")
        normalized_return_url = _normalize_return_url(
            return_url,
            base_url,
            "/dashboard/settings"
        )
        session = stripe.billing_portal.Session.create(
            customer=current_user.stripeCustomerId,
            return_url=normalized_return_url
        )

        return PortalSessionResponse(url=session.url)

    except stripe.error.StripeError as e:
        logger.error(f"Stripe error during portal session creation: {str(e)}")
        raise HTTPException(status_code=400, detail="Failed to access billing portal.")


@router.get("/subscription-status")
async def get_subscription_status(
    current_user: User = Depends(get_current_user)
):
    """Get current subscription status"""
    if not current_user.stripeSubscriptionId:
        return {
            "hasSubscription": False,
            "isPremium": current_user.isPremium,
            "hasCustomKey": current_user.openRouterApiKey is not None
        }

    _require_stripe()

    try:
        subscription = stripe.Subscription.retrieve(current_user.stripeSubscriptionId)

        return {
            "hasSubscription": True,
            "isPremium": current_user.isPremium,
            "status": subscription.status,
            "currentPeriodEnd": subscription.current_period_end,
            "cancelAtPeriodEnd": subscription.cancel_at_period_end,
            "hasCustomKey": current_user.openRouterApiKey is not None
        }

    except stripe.error.StripeError as e:
        logger.error(f"Stripe error retrieving subscription status: {str(e)}")
        return {
            "hasSubscription": False,
            "isPremium": current_user.isPremium,
            "error": "Unable to retrieve subscription status."
        }


@router.post("/webhook")
@limiter.limit("100/minute")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Handle Stripe webhooks for subscription events.

    Rate limited: 100 requests per minute per IP to allow Stripe retries.
    """
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    if not STRIPE_WEBHOOK_SECRET:
        raise HTTPException(status_code=500, detail="Webhook secret not configured")

    _require_stripe()

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    # Handle the event
    event_type = event["type"]
    data = event["data"]["object"]

    if event_type == "checkout.session.completed":
        # Checkout session completed - link subscription to user
        customer_id = data.get("customer")
        subscription_id = data.get("subscription")
        user_id = data.get("metadata", {}).get("user_id")

        if user_id:
            user = db.query(User).filter(User.id == user_id).first()
        elif customer_id:
            user = db.query(User).filter(User.stripeCustomerId == customer_id).first()
        else:
            user = None

        if user:
            updated = False
            if customer_id and not user.stripeCustomerId:
                user.stripeCustomerId = customer_id
                updated = True

            if subscription_id:
                user.stripeSubscriptionId = subscription_id
                subscription_status = None
                try:
                    subscription = stripe.Subscription.retrieve(subscription_id)
                    subscription_status = subscription.status
                except stripe.error.StripeError as e:
                    logger.warning(f"Failed to retrieve subscription {subscription_id}: {e}")
                    subscription_status = None

                if subscription_status is not None:
                    user.isPremium = subscription_status in ["active", "trialing"]
                elif data.get("payment_status") == "paid":
                    user.isPremium = True
                updated = True

            if updated:
                db.commit()
                # Publish event for new subscription from checkout
                if subscription_id and os.getenv("SKIP_EVENT_PUBLISH") != "1":
                    try:
                        workspace_settings = None
                        if user.activeWorkspaceId:
                            workspace_settings = WorkspaceService.get_settings(user.activeWorkspaceId, db)

                        await event_publisher.publish(
                            event_type="billing.subscription.created",
                            data={
                                "subscription_id": subscription_id,
                                "customer_id": customer_id,
                                "status": "active"
                            },
                            organization_id=user.activeWorkspaceId or "default",
                            user_id=user.id,
                            workspace_settings=workspace_settings
                        )
                    except Exception as e:
                        logger.warning(f"Failed to publish billing.subscription.created event: {e}")

    elif event_type == "customer.subscription.created":
        # Subscription created
        subscription_id = data["id"]
        customer_id = data["customer"]

        user = db.query(User).filter(User.stripeCustomerId == customer_id).first()
        if user:
            user.stripeSubscriptionId = subscription_id
            user.isPremium = data["status"] == "active"
            db.commit()
            
            # Publish event
            if os.getenv("SKIP_EVENT_PUBLISH") != "1":
                try:
                    workspace_settings = None
                    if user.activeWorkspaceId:
                        workspace_settings = WorkspaceService.get_settings(user.activeWorkspaceId, db)

                    await event_publisher.publish(
                        event_type="billing.subscription.created",
                        data={
                            "subscription_id": subscription_id,
                            "customer_id": customer_id,
                            "status": data["status"]
                        },
                        organization_id=user.activeWorkspaceId or "default",
                        user_id=user.id,
                        workspace_settings=workspace_settings
                    )
                except Exception as e:
                    logger.warning(f"Failed to publish billing.subscription.created event: {e}")

    elif event_type == "customer.subscription.updated":
        # Subscription status changed
        subscription_id = data["id"]
        status = data["status"]

        user = db.query(User).filter(User.stripeSubscriptionId == subscription_id).first()
        if user:
            user.isPremium = status == "active"
            db.commit()

    elif event_type == "customer.subscription.deleted":
        # Subscription canceled
        subscription_id = data["id"]

        user = db.query(User).filter(User.stripeSubscriptionId == subscription_id).first()
        if user:
            user.isPremium = False
            # Optionally clear subscription ID
            # user.stripeSubscriptionId = None
            db.commit()

    elif event_type == "invoice.payment_succeeded":
        # Payment successful - ensure premium status
        customer_id = data["customer"]

        user = db.query(User).filter(User.stripeCustomerId == customer_id).first()
        if user:
            user.isPremium = True
            db.commit()
            
            # Publish event
            if os.getenv("SKIP_EVENT_PUBLISH") != "1":
                try:
                    workspace_settings = None
                    if user.activeWorkspaceId:
                        workspace_settings = WorkspaceService.get_settings(user.activeWorkspaceId, db)

                    await event_publisher.publish(
                        event_type="billing.invoice.paid",
                        data={
                            "invoice_id": data["id"],
                            "amount": data["amount_paid"],
                            "currency": data["currency"],
                            "customer_id": customer_id
                        },
                        organization_id=user.activeWorkspaceId or "default",
                        user_id=user.id,
                        workspace_settings=workspace_settings
                    )
                except Exception as e:
                    logger.warning(f"Failed to publish billing.invoice.paid event: {e}")

    elif event_type == "invoice.payment_failed":
        # Payment failed - handle gracefully
        customer_id = data["customer"]

        user = db.query(User).filter(User.stripeCustomerId == customer_id).first()
        if user:
            # Optionally notify user or mark for attention
            pass

    return {"success": True, "event": event_type}
