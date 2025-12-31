"""Webhooks router - FastAPI endpoints for Twilio webhooks"""

from fastapi import APIRouter, Depends, HTTPException, status, Request, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from typing import Optional
import hmac
import hashlib

from app.core.database import get_db
from app.core.config import settings
from app.core.logger import get_logger
from app.models.call import Call, CallStatus, CallTranscript, TranscriptRole
from app.schemas.webhook import (
    TwilioCallStatusWebhook,
    TwilioRecordingWebhook,
    TwilioTranscriptionWebhook,
    IVRInputWebhook,
    WebhookResponse
)

logger = get_logger(__name__)

router = APIRouter(prefix="/api/webhooks", tags=["webhooks"])


def verify_twilio_signature(
    url: str,
    params: dict,
    signature: str,
    auth_token: str
) -> bool:
    """
    Verify Twilio webhook signature

    Args:
        url: Full webhook URL
        params: Request parameters
        signature: X-Twilio-Signature header
        auth_token: Twilio auth token

    Returns:
        True if signature is valid
    """
    # Sort parameters and build string
    sorted_params = sorted(params.items())
    data = url + ''.join([f'{k}{v}' for k, v in sorted_params])

    # Compute signature
    computed = hmac.new(
        auth_token.encode('utf-8'),
        data.encode('utf-8'),
        hashlib.sha1
    ).digest()

    # Base64 encode and compare
    import base64
    computed_sig = base64.b64encode(computed).decode('utf-8')

    return hmac.compare_digest(computed_sig, signature)


@router.post("/twilio/call-status", response_model=WebhookResponse)
async def twilio_call_status(
    webhook: TwilioCallStatusWebhook,
    request: Request,
    db: AsyncSession = Depends(get_db),
    x_twilio_signature: Optional[str] = Header(None)
):
    """
    Handle Twilio call status webhooks

    Twilio sends:
    - initiated: Call initiated
    - ringing: Phone is ringing
    - answered: Call was answered
    - completed: Call ended
    """
    # Verify signature if configured
    if settings.TWILIO_AUTH_TOKEN and x_twilio_signature:
        url = str(request.url)
        params = dict(request.query_params)

        if not verify_twilio_signature(url, params, x_twilio_signature, settings.TWILIO_AUTH_TOKEN):
            logger.warning(f"Invalid Twilio signature for call {webhook.CallSid}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid webhook signature"
            )

    # Find call by Twilio SID
    result = await db.execute(
        select(Call).where(Call.twilio_call_sid == webhook.CallSid)
    )
    call = result.scalar_one_or_none()

    if not call:
        logger.warning(f"Call not found for Twilio SID: {webhook.CallSid}")
        return {"success": True, "message": "Call not found"}

    # Update call status
    status_mapping = {
        "initiated": CallStatus.QUEUED,
        "ringing": CallStatus.RINGING,
        "in-progress": CallStatus.IN_PROGRESS,
        "answered": CallStatus.IN_PROGRESS,
        "completed": CallStatus.COMPLETED,
        "busy": CallStatus.BUSY,
        "no-answer": CallStatus.NO_ANSWER,
        "failed": CallStatus.FAILED,
        "canceled": CallStatus.CANCELED
    }

    new_status = status_mapping.get(webhook.CallStatus, CallStatus.FAILED)
    call.status = new_status

    # Update duration and end time for completed calls
    if new_status == CallStatus.COMPLETED:
        call.end_time = datetime.utcnow()
        if webhook.CallDuration:
            call.duration = int(webhook.CallDuration)

    await db.commit()

    logger.info(f"Updated call {call.id} status to {new_status}")

    return {"success": True, "message": f"Call status updated to {new_status}"}


@router.post("/twilio/recording", response_model=WebhookResponse)
async def twilio_recording(
    webhook: TwilioRecordingWebhook,
    request: Request,
    db: AsyncSession = Depends(get_db),
    x_twilio_signature: Optional[str] = Header(None)
):
    """
    Handle Twilio recording webhooks

    Called when a recording is available
    """
    # Verify signature
    if settings.TWILIO_AUTH_TOKEN and x_twilio_signature:
        url = str(request.url)
        params = dict(request.query_params)

        if not verify_twilio_signature(url, params, x_twilio_signature, settings.TWILIO_AUTH_TOKEN):
            logger.warning(f"Invalid Twilio signature for recording {webhook.RecordingSid}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid webhook signature"
            )

    # Find call by Twilio SID
    result = await db.execute(
        select(Call).where(Call.twilio_call_sid == webhook.CallSid)
    )
    call = result.scalar_one_or_none()

    if not call:
        logger.warning(f"Call not found for recording: {webhook.CallSid}")
        return {"success": True, "message": "Call not found"}

    # Update call with recording URL
    call.recording_url = webhook.RecordingUrl

    await db.commit()

    logger.info(f"Added recording URL to call {call.id}")

    return {"success": True, "message": "Recording stored"}


@router.post("/twilio/transcription", response_model=WebhookResponse)
async def twilio_transcription(
    webhook: TwilioTranscriptionWebhook,
    request: Request,
    db: AsyncSession = Depends(get_db),
    x_twilio_signature: Optional[str] = Header(None)
):
    """
    Handle Twilio transcription webhooks

    Called when a transcription is available
    """
    # Verify signature
    if settings.TWILIO_AUTH_TOKEN and x_twilio_signature:
        url = str(request.url)
        params = dict(request.query_params)

        if not verify_twilio_signature(url, params, x_twilio_signature, settings.TWILIO_AUTH_TOKEN):
            logger.warning(f"Invalid Twilio signature for transcription {webhook.TranscriptionSid}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid webhook signature"
            )

    # Find call by Twilio SID
    result = await db.execute(
        select(Call).where(Call.twilio_call_sid == webhook.CallSid)
    )
    call = result.scalar_one_or_none()

    if not call:
        logger.warning(f"Call not found for transcription: {webhook.CallSid}")
        return {"success": True, "message": "Call not found"}

    # Create transcript entry
    from uuid import uuid4
    transcript = CallTranscript(
        id=str(uuid4()),
        call_id=call.id,
        role=TranscriptRole.USER,  # Assuming customer speech
        content=webhook.TranscriptionText,
        timestamp=datetime.utcnow(),
        extra_metadata={
            "twilio_sid": webhook.TranscriptionSid,
            "recording_sid": webhook.RecordingSid
        }
    )

    db.add(transcript)
    await db.commit()

    logger.info(f"Added transcription to call {call.id}")

    return {"success": True, "message": "Transcription stored"}


@router.post("/twilio/ivr", response_model=WebhookResponse)
async def twilio_ivr_input(
    webhook: IVRInputWebhook,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Handle IVR input from Twilio

    Process DTMF digits or speech input
    """
    # Determine action based on input
    action = "queue"
    target = "support"

    if webhook.Digits:
        digit_actions = {
            "1": ("queue", "sales"),
            "2": ("queue", "support"),
            "3": ("queue", "billing"),
            "0": ("transfer", "operator"),
        }
        action, target = digit_actions.get(webhook.Digits, ("repeat", "menu"))

    logger.info(f"IVR input for call {webhook.CallSid}: {webhook.Digits} -> {action}/{target}")

    return {
        "success": True,
        "message": f"IVR action: {action} to {target}",
        "data": {
            "action": action,
            "target": target
        }
    }


@router.get("/health", response_model=WebhookResponse)
async def webhook_health():
    """Health check endpoint for webhook system"""
    return {
        "success": True,
        "message": "Webhook system operational"
    }
