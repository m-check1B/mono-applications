"""
Speak by Kraliki - Telephony Webhook Router

Handles Telnyx webhooks for phone-based voice surveys.
Uses voice-core from platform-2026.
"""

import logging
from fastapi import APIRouter, Request, HTTPException, BackgroundTasks
from pydantic import BaseModel

from app.services.voice_streaming import voice_streaming_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/speak/telephony", tags=["telephony"])


class TelnyxWebhookPayload(BaseModel):
    """Telnyx webhook payload structure."""
    data: dict
    meta: dict | None = None


@router.post("/webhook")
async def telnyx_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
):
    """
    Handle Telnyx Call Control webhooks.

    SECURITY: All webhooks are validated using Ed25519 signature verification.

    Telnyx sends webhooks for:
    - call.initiated: Call started
    - call.answered: Call answered (start streaming)
    - call.hangup: Call ended
    - streaming.started: Audio stream active
    - streaming.stopped: Audio stream ended
    """
    # Get raw payload for signature validation
    body = await request.body()
    signature = request.headers.get("Telnyx-Signature-Ed25519", "")
    timestamp = request.headers.get("Telnyx-Timestamp", "")
    client_ip = request.client.host if request.client else "unknown"

    # SECURITY: Validate Telnyx webhook signature (Ed25519) and timestamp
    # This protects against forged webhook requests and replay attacks
    if not await voice_streaming_service.validate_webhook(signature, body, timestamp):
        logger.warning(
            f"SECURITY ALERT: Rejected unauthorized webhook from IP={client_ip}"
        )
        raise HTTPException(status_code=401, detail="Invalid webhook signature")

    # Audit log for successful webhook
    logger.info(f"AUDIT: Accepted Telnyx webhook from IP={client_ip}")

    # Parse payload
    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    data = payload.get("data", {})
    event_type = data.get("event_type", "unknown")
    event_payload = data.get("payload", {})

    logger.info(f"Received Telnyx webhook: {event_type}")

    # Handle events
    if event_type == "call.initiated":
        call_id = event_payload.get("call_control_id")
        logger.info(f"Call initiated: {call_id}")
        return {"status": "received"}

    elif event_type == "call.answered":
        call_id = event_payload.get("call_control_id")
        logger.info(f"Call answered: {call_id}")
        # Start audio streaming
        return {"status": "streaming"}

    elif event_type == "call.hangup":
        call_id = event_payload.get("call_control_id")
        hangup_cause = event_payload.get("hangup_cause")
        logger.info(f"Call hangup: {call_id}, cause: {hangup_cause}")
        # End the call session
        background_tasks.add_task(voice_streaming_service.end_call, call_id)
        return {"status": "ended"}

    elif event_type in ("streaming.started", "streaming.stopped"):
        # Audio streaming status updates
        return {"status": "acknowledged"}

    else:
        logger.warning(f"Unknown Telnyx event: {event_type}")
        return {"status": "ignored"}


@router.post("/audio-stream")
async def audio_stream_webhook(
    request: Request,
):
    """
    Handle Telnyx audio stream data.

    SECURITY: All webhooks are validated using Ed25519 signature verification.

    This endpoint receives raw audio data via WebSocket or HTTP POST
    depending on Telnyx configuration.

    For production, use WebSocket streaming instead of HTTP POST.
    """
    # Get raw payload for signature validation
    body = await request.body()
    signature = request.headers.get("Telnyx-Signature-Ed25519", "")
    timestamp = request.headers.get("Telnyx-Timestamp", "")
    client_ip = request.client.host if request.client else "unknown"

    # SECURITY: Validate Telnyx webhook signature (Ed25519) and timestamp
    # This protects against audio injection attacks
    if not await voice_streaming_service.validate_webhook(signature, body, timestamp):
        logger.warning(
            f"SECURITY ALERT: Rejected unauthorized audio-stream from IP={client_ip}"
        )
        raise HTTPException(status_code=401, detail="Invalid webhook signature")

    # Get call ID from headers or query params
    call_id = request.headers.get("X-Call-Control-Id")
    if not call_id:
        raise HTTPException(status_code=400, detail="Missing call ID")

    # Get raw audio data
    audio_data = await request.body()

    # Forward to voice streaming service
    await voice_streaming_service.handle_incoming_audio(call_id, audio_data)

    return {"status": "received"}


@router.get("/status")
async def telephony_status():
    """Check telephony service status."""
    return {
        "available": voice_streaming_service.is_available,
        "active_calls": len(voice_streaming_service._active_calls),
    }
