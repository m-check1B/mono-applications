"""SMS router - FastAPI endpoints for SMS messaging"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime
from typing import Optional
from uuid import uuid4

from app.core.database import get_db
from app.core.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/sms", tags=["sms"])


# Pydantic schemas for SMS
from pydantic import BaseModel, Field


class SMSMessage(BaseModel):
    """SMS message schema"""
    id: str
    from_number: str
    to_number: str
    body: str
    direction: str  # "inbound" or "outbound"
    status: str
    created_at: datetime
    organization_id: str


class SMSCreate(BaseModel):
    """Schema for creating outbound SMS"""
    to_number: str = Field(..., min_length=10, max_length=20)
    body: str = Field(..., min_length=1, max_length=1600)


class SMSList(BaseModel):
    """Schema for SMS list response"""
    items: list[SMSMessage]
    total: int
    page: int
    page_size: int


@router.get("/inbox", response_model=SMSList)
async def get_sms_inbox(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """
    Get SMS inbox messages

    Args:
        page: Page number
        page_size: Items per page
        db: Database session

    Returns:
        Paginated list of SMS messages
    """
    # TODO: Implement with actual SMS table
    # For now, return mock data
    messages = [
        {
            "id": str(uuid4()),
            "from_number": "+1234567890",
            "to_number": "+1987654321",
            "body": "Hello, this is a test SMS message",
            "direction": "inbound",
            "status": "received",
            "created_at": datetime.utcnow(),
            "organization_id": "default-org"
        }
    ]

    return {
        "items": messages,
        "total": len(messages),
        "page": page,
        "page_size": page_size
    }


@router.post("/send", response_model=SMSMessage, status_code=status.HTTP_201_CREATED)
async def send_sms(
    sms_data: SMSCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Send an outbound SMS message

    Args:
        sms_data: SMS data
        db: Database session

    Returns:
        Sent SMS message details
    """
    from app.services.telephony_service import telephony_service

    if not telephony_service.is_available():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="SMS service not available - Twilio not configured"
        )

    try:
        # Send SMS via Twilio
        # TODO: Implement actual SMS sending via Twilio
        # message = telephony_service.client.messages.create(
        #     to=sms_data.to_number,
        #     from_=telephony_service.phone_number,
        #     body=sms_data.body
        # )

        # Create SMS record
        sms_message = {
            "id": str(uuid4()),
            "from_number": telephony_service.phone_number or "+1000000000",
            "to_number": sms_data.to_number,
            "body": sms_data.body,
            "direction": "outbound",
            "status": "sent",
            "created_at": datetime.utcnow(),
            "organization_id": "default-org"
        }

        logger.info(f"SMS sent to {sms_data.to_number}")

        return sms_message

    except Exception as e:
        logger.error(f"Failed to send SMS: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send SMS: {str(e)}"
        )


@router.get("/conversations", response_model=list[dict])
async def get_sms_conversations(
    db: AsyncSession = Depends(get_db)
):
    """
    Get list of SMS conversations grouped by contact

    Args:
        db: Database session

    Returns:
        List of conversations
    """
    # TODO: Implement with actual data
    conversations = [
        {
            "contact_number": "+1234567890",
            "contact_name": "John Doe",
            "last_message": "Hello, this is a test",
            "unread_count": 2,
            "last_message_at": datetime.utcnow()
        }
    ]

    return conversations
