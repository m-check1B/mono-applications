"""Payments router - Billing and payment processing"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.core.database import get_db
from app.dependencies import get_current_user, require_supervisor
from app.core.logger import get_logger
from app.models.user import User

router = APIRouter(prefix="/api/payments", tags=["payments"])
logger = get_logger(__name__)


class PaymentMethodRequest(BaseModel):
    """Add payment method"""
    type: str  # card, bank_account
    token: str  # Stripe/payment processor token


@router.get("/subscription", response_model=dict)
async def get_subscription(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get organization subscription details"""
    return {
        'organization_id': current_user.organization_id,
        'plan': 'professional',
        'status': 'active',
        'billing_cycle': 'monthly',
        'amount_usd': 99.00,
        'next_billing_date': '2025-11-01',
        'features': {
            'max_agents': 25,
            'max_concurrent_calls': 10,
            'recording': True,
            'transcription': True,
            'ai_features': True
        }
    }


@router.get("/usage", response_model=dict)
async def get_usage(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current billing period usage"""
    return {
        'billing_period': {
            'start': '2025-10-01',
            'end': '2025-10-31'
        },
        'usage': {
            'calls_minutes': 1543,
            'transcription_minutes': 892,
            'ai_requests': 2341,
            'storage_gb': 12.5
        },
        'costs': {
            'calls': 77.15,
            'transcription': 13.38,
            'ai': 23.41,
            'storage': 2.50,
            'total_usd': 116.44
        }
    }


@router.get("/invoices", response_model=dict)
async def get_invoices(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get billing invoices"""
    invoices = [
        {
            'id': 'inv_001',
            'date': '2025-09-01',
            'amount_usd': 99.00,
            'status': 'paid',
            'pdf_url': '/api/payments/invoices/inv_001/pdf'
        },
        {
            'id': 'inv_002',
            'date': '2025-10-01',
            'amount_usd': 116.44,
            'status': 'pending',
            'pdf_url': None
        }
    ]
    return {'invoices': invoices}


@router.post("/payment-method", response_model=dict, dependencies=[Depends(require_supervisor)])
async def add_payment_method(
    request: PaymentMethodRequest,
    current_user: User = Depends(get_current_user)
):
    """Add payment method"""
    # Would integrate with Stripe/payment processor
    return {
        'success': True,
        'message': 'Payment method added',
        'payment_method_id': 'pm_' + request.token[:10]
    }


@router.get("/payment-methods", response_model=dict)
async def get_payment_methods(current_user: User = Depends(get_current_user)):
    """Get payment methods"""
    return {
        'payment_methods': [
            {
                'id': 'pm_visa1234',
                'type': 'card',
                'last4': '4242',
                'brand': 'visa',
                'exp_month': 12,
                'exp_year': 2026,
                'is_default': True
            }
        ]
    }
