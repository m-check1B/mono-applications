"""Unified payment service supporting multiple providers."""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional

import httpx
import stripe
from fastapi import HTTPException, Request, Response

from app.core.config import settings


def _resolve_stripe_exception(name: str) -> type[BaseException]:
    """Resolve a valid Stripe exception type, falling back safely."""
    candidate = getattr(getattr(stripe, "error", None), name, None)
    if isinstance(candidate, type) and issubclass(candidate, BaseException):
        return candidate
    candidate = getattr(stripe, name, None)
    if isinstance(candidate, type) and issubclass(candidate, BaseException):
        return candidate
    return Exception


_STRIPE_ERROR = _resolve_stripe_exception("StripeError")
_STRIPE_SIGNATURE_ERROR = _resolve_stripe_exception("SignatureVerificationError")


class PaymentProvider(str, Enum):
    """Supported payment providers."""

    TELEGRAM_STARS = "telegram_stars"
    STRIPE = "stripe"


class SubscriptionTier(str, Enum):
    """Subscription tiers."""

    FREE = "free"
    PRO = "pro"
    CONTENT_PRO = "content_pro"


class PaymentProviderBase(ABC):
    """Abstract base for payment providers."""

    @abstractmethod
    async def create_subscription(
        self,
        tier: SubscriptionTier,
        user_id: int,
        user_email: Optional[str] = None,
        billing_interval: str = "monthly",
    ) -> dict:
        """Create a subscription for a user.

        Args:
            tier: Subscription tier
            user_id: Telegram user/chat ID
            user_email: User email (optional, required for Stripe)
            billing_interval: "monthly" or "yearly" (Stripe only)

        Returns:
            Dict with checkout_url, subscription_id, provider
        """
        pass

    @abstractmethod
    async def cancel_subscription(self, subscription_id: str) -> bool:
        """Cancel a subscription.

        Args:
            subscription_id: Provider-specific subscription ID

        Returns:
            True if cancelled successfully
        """
        pass

    @abstractmethod
    async def get_subscription_status(self, subscription_id: str) -> dict:
        """Get subscription status.

        Args:
            subscription_id: Provider-specific subscription ID

        Returns:
            Dict with status, current_period_end, cancel_at_period_end
        """
        pass


class TelegramStarsProvider(PaymentProviderBase):
    """Telegram Stars payment provider."""

    def __init__(self):
        self.provider_token = settings.telegram_stars_provider_token

    async def create_subscription(
        self,
        tier: SubscriptionTier,
        user_id: int,
        user_email: Optional[str] = None,
        billing_interval: str = "monthly",
    ) -> dict:
        """Create Telegram Stars invoice.

        Returns invoice payload for bot to send.
        """
        prices = {
            SubscriptionTier.PRO: settings.subscription_price_stars,
            SubscriptionTier.CONTENT_PRO: settings.newsletter_price_stars,
        }

        if tier not in prices:
            raise ValueError(f"Invalid tier: {tier}")

        price = prices[tier]

        return {
            "checkout_url": None,  # Telegram handles inline payment
            "subscription_id": f"stars_{tier.value}_{user_id}",
            "provider": PaymentProvider.TELEGRAM_STARS,
            "price_stars": price,
            "payload": f"sub:{tier.value}:{user_id}"
            if tier == SubscriptionTier.PRO
            else f"content_sub:{user_id}",
        }

    async def cancel_subscription(self, subscription_id: str) -> bool:
        """Telegram Stars subscriptions are one-time purchases (no recurring cancel)."""
        return False

    async def get_subscription_status(self, subscription_id: str) -> dict:
        """Telegram Stars don't have subscription status tracking."""
        return {
            "status": "active",
            "current_period_end": None,
            "cancel_at_period_end": False,
        }


class StripeProvider(PaymentProviderBase):
    """Stripe payment provider with recurring subscriptions."""

    def __init__(self):
        if not settings.stripe_api_key:
            raise ValueError("Stripe not configured: missing STRIPE_API_KEY")

        self.client = stripe.AsyncStripe(api_key=settings.stripe_api_key)
        self.price_ids = {
            (SubscriptionTier.PRO, "monthly"): settings.stripe_price_pro_monthly,
            (SubscriptionTier.PRO, "yearly"): settings.stripe_price_pro_yearly,
            (SubscriptionTier.CONTENT_PRO, "monthly"): settings.stripe_price_content_monthly,
            (SubscriptionTier.CONTENT_PRO, "yearly"): settings.stripe_price_content_yearly,
        }

    def _get_base_url(self) -> str:
        """Resolve the public base URL for Stripe checkout callbacks."""
        base_url = settings.stripe_webhook_url or settings.telegram_webhook_url
        if not base_url:
            raise ValueError(
                "Stripe not configured: set STRIPE_WEBHOOK_URL or TELEGRAM_WEBHOOK_URL"
            )
        return base_url.rstrip("/")

    async def create_subscription(
        self,
        tier: SubscriptionTier,
        user_id: int,
        user_email: Optional[str] = None,
        billing_interval: str = "monthly",
    ) -> dict:
        """Create Stripe checkout session for subscription.

        Args:
            tier: Subscription tier
            user_id: Telegram user/chat ID
            user_email: User email (optional)
            billing_interval: "monthly" or "yearly"

        Returns:
            Dict with checkout_url, subscription_id, provider
        """
        if (tier, billing_interval) not in self.price_ids:
            raise ValueError(
                f"Invalid tier/billing_interval combination: {tier}/{billing_interval}"
            )

        price_id = self.price_ids[(tier, billing_interval)]

        if not price_id:
            raise ValueError(f"Price ID not configured for {tier}/{billing_interval}")

        try:
            base_url = self._get_base_url()
            checkout_session = await self.client.checkout.sessions.create(
                customer_email=user_email,
                payment_method_types=["card"],
                line_items=[
                    {
                        "price": price_id,
                        "quantity": 1,
                    }
                ],
                mode="subscription",
                success_url=f"{base_url}/subscribe/success?session_id={{CHECKOUT_SESSION_ID}}",
                cancel_url=f"{base_url}/subscribe/cancel",
                metadata={
                    "telegram_user_id": str(user_id),
                    "tier": tier.value,
                    "billing_interval": billing_interval,
                },
                subscription_data={
                    "metadata": {
                        "telegram_user_id": str(user_id),
                        "tier": tier.value,
                    }
                },
            )

            return {
                "checkout_url": checkout_session.url,
                "subscription_id": checkout_session.subscription,
                "provider": PaymentProvider.STRIPE,
                "session_id": checkout_session.id,
            }

        except _STRIPE_ERROR as e:
            raise HTTPException(status_code=500, detail=f"Stripe error: {str(e)}")

    async def cancel_subscription(self, subscription_id: str) -> bool:
        """Cancel Stripe subscription at period end.

        Args:
            subscription_id: Stripe subscription ID

        Returns:
            True if cancelled successfully
        """
        try:
            await self.client.subscriptions.modify(
                subscription_id,
                cancel_at_period_end=True,
            )
            return True
        except _STRIPE_ERROR:
            return False

    async def get_subscription_status(self, subscription_id: str) -> dict:
        """Get Stripe subscription status.

        Returns:
            Dict with status, current_period_end, cancel_at_period_end
        """
        try:
            subscription = await self.client.subscriptions.retrieve(subscription_id)
            return {
                "status": subscription.status,
                "current_period_end": subscription.current_period_end,
                "cancel_at_period_end": subscription.cancel_at_period_end,
            }
        except _STRIPE_ERROR:
            return {
                "status": "unknown",
                "current_period_end": None,
                "cancel_at_period_end": False,
            }


class PaymentService:
    """Unified payment service supporting multiple providers."""

    def __init__(self):
        self.providers = {}
        self._init_providers()

    def _init_providers(self):
        """Initialize configured payment providers."""
        # Telegram Stars (XTR) does not require a token, so we always enable it
        self.providers[PaymentProvider.TELEGRAM_STARS] = TelegramStarsProvider()

        if settings.stripe_api_key:
            self.providers[PaymentProvider.STRIPE] = StripeProvider()

    def get_provider(self, provider: PaymentProvider) -> PaymentProviderBase:
        """Get payment provider instance."""
        if provider not in self.providers:
            raise ValueError(f"Provider {provider} not configured")
        return self.providers[provider]

    async def create_subscription(
        self,
        provider: PaymentProvider,
        tier: SubscriptionTier,
        user_id: int,
        user_email: Optional[str] = None,
        billing_interval: str = "monthly",
    ) -> dict:
        """Create subscription via specified provider."""
        provider_instance = self.get_provider(provider)
        return await provider_instance.create_subscription(
            tier=tier,
            user_id=user_id,
            user_email=user_email,
            billing_interval=billing_interval,
        )

    async def cancel_subscription(self, provider: PaymentProvider, subscription_id: str) -> bool:
        """Cancel subscription via specified provider."""
        provider_instance = self.get_provider(provider)
        return await provider_instance.cancel_subscription(subscription_id)

    async def get_subscription_status(
        self, provider: PaymentProvider, subscription_id: str
    ) -> dict:
        """Get subscription status via specified provider."""
        provider_instance = self.get_provider(provider)
        return await provider_instance.get_subscription_status(subscription_id)

    async def verify_stripe_webhook(self, request: Request) -> dict:
        """Verify Stripe webhook signature and parse payload.

        Args:
            request: FastAPI request object

        Returns:
            Parsed webhook event

        Raises:
            HTTPException if signature invalid
        """
        if not settings.stripe_webhook_secret:
            raise HTTPException(status_code=500, detail="Stripe webhook secret not configured")

        payload = await request.body()
        sig_header = request.headers.get("stripe-signature")

        if not sig_header:
            raise HTTPException(status_code=400, detail="Missing stripe-signature header")

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.stripe_webhook_secret
            )
            return event
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid payload")
        except _STRIPE_SIGNATURE_ERROR:
            raise HTTPException(status_code=400, detail="Invalid signature")


# Global instance
payment_service = PaymentService()
