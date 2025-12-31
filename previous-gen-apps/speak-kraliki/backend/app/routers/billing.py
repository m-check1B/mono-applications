"""
Speak by Kraliki - Billing Router
API endpoints for managing subscriptions and Stripe integration.

RBAC enforced:
- owner: Full billing access (create checkout, view status)
- Others: No billing access
"""

import logging
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Request, status, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.auth import get_current_user
from app.core.config import settings
from app.core.rbac import Permission, require_permission
from app.services.stripe_service import stripe_service
from app.models.company import Company
from sqlalchemy import select

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/speak/billing", tags=["billing"])

@router.post("/checkout/{plan}")
async def create_checkout_session(
    plan: str,
    current_user: dict = Depends(require_permission(Permission.BILLING_MANAGE)),
    db: AsyncSession = Depends(get_db)
):
    """Create a Stripe checkout session for a subscription.

    RBAC: Only owners can manage billing.
    """
    company_id = UUID(current_user["company_id"])
    
    # Get company and user details for Stripe customer creation
    result = await db.execute(select(Company).where(Company.id == company_id))
    company = result.scalar_one_or_none()
    
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    # Create or get Stripe customer
    customer_id = await stripe_service.create_customer(
        db, company_id, current_user["email"], company.name
    )

    try:
        checkout_url = await stripe_service.create_checkout_session(
            company_id=company_id,
            customer_id=customer_id,
            plan_name=plan,
            success_url=f"{settings.api_base_url}/billing/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{settings.api_base_url}/billing/cancel"
        )
        return {"checkout_url": checkout_url}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to create checkout session: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(None),
    db: AsyncSession = Depends(get_db)
):
    """Handle Stripe webhook events."""
    if not stripe_signature:
        raise HTTPException(status_code=400, detail="Missing stripe-signature header")

    payload = await request.body()
    
    try:
        await stripe_service.handle_webhook(payload, stripe_signature, db)
        return {"status": "success"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Webhook processing failed: {e}")
        return {"status": "error", "message": str(e)}

@router.get("/status")
async def get_billing_status(
    current_user: dict = Depends(require_permission(Permission.BILLING_VIEW)),
    db: AsyncSession = Depends(get_db)
):
    """Get current billing status for the company.

    RBAC: Only owners can view billing.
    """
    company_id = UUID(current_user["company_id"])
    result = await db.execute(select(Company).where(Company.id == company_id))
    company = result.scalar_one_or_none()
    
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
        
    return {
        "plan": company.plan,
        "is_subscribed": company.stripe_subscription_id is not None,
        "stripe_customer_id": company.stripe_customer_id
    }
