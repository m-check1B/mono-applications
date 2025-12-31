"""
Speak by Kraliki - Stripe Service
Integration with Stripe for subscription management.
"""

import logging
import stripe
from uuid import UUID
from typing import Optional, Dict, Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.company import Company

logger = logging.getLogger(__name__)

# Initialize stripe
stripe.api_key = settings.stripe_secret_key

class StripeService:
    """Service for managing Stripe subscriptions."""

    def __init__(self):
        self.price_map = {
            "personal": settings.stripe_price_personal,
            "premium": settings.stripe_price_premium,
            "pro": settings.stripe_price_pro,
        }

    async def create_customer(
        self,
        db: AsyncSession,
        company_id: UUID,
        email: str,
        name: str
    ) -> str:
        """Create a Stripe customer for a company."""
        # Check if customer already exists
        result = await db.execute(select(Company).where(Company.id == company_id))
        company = result.scalar_one_or_none()
        
        if company and company.stripe_customer_id:
            return company.stripe_customer_id

        # Create Stripe customer
        customer = stripe.Customer.create(
            email=email,
            name=name,
            metadata={"company_id": str(company_id)}
        )
        
        if company:
            company.stripe_customer_id = customer.id
            await db.commit()
            
        logger.info(f"Created Stripe customer {customer.id} for company {company_id}")
        return customer.id

    async def create_checkout_session(
        self,
        company_id: UUID,
        customer_id: str,
        plan_name: str,
        success_url: str,
        cancel_url: str
    ) -> str:
        """Create a Stripe checkout session for a subscription."""
        price_id = self.price_map.get(plan_name.lower())
        if not price_id:
            raise ValueError(f"Invalid plan name: {plan_name}")

        session = stripe.checkout.Session.create(
            customer=customer_id,
            payment_method_types=["card"],
            line_items=[{"price": price_id, "quantity": 1}],
            mode="subscription",
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={"company_id": str(company_id), "plan": plan_name.lower()},
            subscription_data={
                "metadata": {"company_id": str(company_id), "plan": plan_name.lower()}
            }
        )
        
        logger.info(f"Created Stripe checkout session {session.id} for company {company_id}")
        return session.url

    async def handle_webhook(self, payload: bytes, sig_header: str, db: AsyncSession):
        """Handle Stripe webhook events."""
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.stripe_webhook_secret
            )
        except ValueError:
            # Invalid payload
            raise ValueError("Invalid payload")
        except stripe.error.SignatureVerificationError:
            # Invalid signature
            raise ValueError("Invalid signature")

        logger.info(f"Processing Stripe webhook event: {event.type}")

        if event.type == "checkout.session.completed":
            session = event.data.object
            await self._handle_subscription_success(session, db)
        elif event.type == "customer.subscription.updated":
            subscription = event.data.object
            await self._handle_subscription_updated(subscription, db)
        elif event.type == "customer.subscription.deleted":
            subscription = event.data.object
            await self._handle_subscription_deleted(subscription, db)

    async def _handle_subscription_success(self, session: Any, db: AsyncSession):
        """Handle successful checkout session."""
        company_id_str = session.metadata.get("company_id")
        plan = session.metadata.get("plan", "personal")
        
        if not company_id_str:
            logger.error("No company_id in checkout session metadata")
            return

        company_id = UUID(company_id_str)
        result = await db.execute(select(Company).where(Company.id == company_id))
        company = result.scalar_one_or_none()
        
        if company:
            company.plan = plan
            company.stripe_subscription_id = session.subscription
            await db.commit()
            logger.info(f"Updated company {company_id} plan to {plan}")

    async def _handle_subscription_updated(self, subscription: Any, db: AsyncSession):
        """Handle subscription update event."""
        company_id_str = subscription.metadata.get("company_id")
        if not company_id_str:
            return

        company_id = UUID(company_id_str)
        result = await db.execute(select(Company).where(Company.id == company_id))
        company = result.scalar_one_or_none()
        
        if company:
            # In a real app, we'd check the new price ID to determine the plan
            # For now, we assume plan metadata is correct or handled by checkout
            pass

    async def _handle_subscription_deleted(self, subscription: Any, db: AsyncSession):
        """Handle subscription deletion (cancellation)."""
        company_id_str = subscription.metadata.get("company_id")
        if not company_id_str:
            return

        company_id = UUID(company_id_str)
        result = await db.execute(select(Company).where(Company.id == company_id))
        company = result.scalar_one_or_none()
        
        if company:
            company.plan = "free"  # Downgrade to free on cancellation
            company.stripe_subscription_id = None
            await db.commit()
            logger.info(f"Downgraded company {company_id} to free plan due to subscription cancellation")

stripe_service = StripeService()
