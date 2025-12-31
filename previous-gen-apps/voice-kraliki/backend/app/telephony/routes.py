"""Telephony integration routes.

Provides placeholder endpoints for outbound call initiation and webhook reception.
These stubs validate configuration via the telephony adapters so the system can
progressively integrate PSTN flows without breaking API contracts.
"""

import logging
import time
from ipaddress import ip_address, ip_network
from typing import Any
from uuid import UUID

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

import app.telephony.state as telephony_state
from app.config.feature_flags import get_feature_flags
from app.config.settings import get_settings
from app.middleware.rate_limit import WEBHOOK_RATE_LIMIT, limiter
from app.providers.registry import TelephonyType, get_provider_registry
from app.services.compliance import ConsentType, compliance_service
from app.sessions.manager import get_session_manager
from app.sessions.models import SessionCreateRequest
from app.settings.provider import fetch_settings as fetch_provider_defaults

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/telephony", tags=["telephony"])


def _validate_webhook_ip(request: Request, telephony_type: TelephonyType) -> bool:
    """Validate webhook source IP against whitelist.

    Args:
        request: The FastAPI request object
        telephony_type: The telephony provider type

    Returns:
        bool: True if IP is whitelisted or validation is disabled, False otherwise
    """
    settings = get_settings()

    # If IP whitelisting is disabled, allow all IPs
    if not settings.enable_webhook_ip_whitelist:
        logger.debug("IP whitelisting disabled for webhooks")
        return True

    # Get client IP from request
    client_ip = request.client.host if request.client else None
    if not client_ip:
        logger.warning("Could not determine client IP for webhook")
        return False

    # Get whitelist for provider
    if telephony_type == TelephonyType.TWILIO:
        allowed_ips = settings.twilio_webhook_ips
    elif telephony_type == TelephonyType.TELNYX:
        allowed_ips = settings.telnyx_webhook_ips
    else:
        logger.warning("Unknown telephony provider for IP validation: %s", telephony_type.value)
        return False

    # Check if IP is in whitelist
    try:
        client_ip_obj = ip_address(client_ip)
        for allowed in allowed_ips:
            if '/' in allowed:  # CIDR notation
                try:
                    if client_ip_obj in ip_network(allowed):
                        logger.debug(
                            "Webhook IP %s matched CIDR %s for %s",
                            client_ip,
                            allowed,
                            telephony_type.value
                        )
                        return True
                except ValueError:
                    logger.warning("Invalid CIDR notation in whitelist: %s", allowed)
                    continue
            else:  # Single IP
                if str(client_ip_obj) == allowed:
                    logger.debug(
                        "Webhook IP %s matched whitelist for %s",
                        client_ip,
                        telephony_type.value
                    )
                    return True

        logger.warning(
            "Webhook rejected from non-whitelisted IP: %s for %s",
            client_ip,
            telephony_type.value
        )
        return False

    except ValueError as exc:
        logger.error("Invalid IP address: %s - %s", client_ip, exc)
        return False


class OutboundCallRequest(BaseModel):
    """Request payload for initiating outbound telephony calls."""

    from_number: str | None = Field(
        default=None, description="Caller phone number (E.164). Falls back to provider defaults."
    )
    to_number: str = Field(description="Destination phone number (E.164)")
    telephony_provider: str | None = Field(
        default=None, description="Telephony provider identifier (twilio, telnyx)"
    )
    stream_url: str | None = Field(
        default=None,
        description="Optional custom WebSocket URL for audio streaming",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata forwarded to the telephony adapter",
    )


def _build_stream_url(session_id: UUID, override: str | None = None) -> str:
    """Resolve the WebSocket stream URL for a session."""
    if override:
        return override

    settings = get_settings()

    # Build WebSocket URL similar to main.py
    scheme = "wss" if settings.environment == "production" else "ws"
    host = settings.host if settings.host != "0.0.0.0" else "localhost"
    ws_url = f"{scheme}://{host}:{settings.port}/ws/sessions/{session_id}"

    return ws_url


async def _validate_webhook_signature(
    telephony_type: TelephonyType, request: Request, payload: dict[str, Any] | str
) -> bool:
    """Validate webhook signature for telephony providers.

    Args:
        telephony_type: The telephony provider type
        request: The FastAPI request object
        payload: The webhook payload

    Returns:
        bool: True if signature is valid, False otherwise
    """
    try:
        # Get the provider adapter for validation
        adapter = get_provider_registry().create_telephony_adapter(telephony_type)

        # Get signature from headers
        signature_valid = False

        if telephony_type == TelephonyType.TWILIO:
            signature = request.headers.get("X-Twilio-Signature", "")
            if not signature:
                return False

            # Build the full URL for validation
            url = str(request.url)

            # Validate using Twilio's method
            signature_valid = await adapter.validate_webhook(signature, url, payload)

        elif telephony_type == TelephonyType.TELNYX:
            signature = request.headers.get("Telnyx-Signature-Ed25519", "")
            timestamp = request.headers.get("Telnyx-Timestamp", "")

            if not signature or not timestamp:
                return False

            # Build the full URL for validation
            url = str(request.url)

            # Validate using Telnyx's method
            signature_valid = await adapter.validate_webhook(signature, url, payload)

        else:
            # Unknown provider, skip validation for now
            logger.warning("Webhook validation not implemented for provider: %s", telephony_type.value)
            signature_valid = True

        # If signature validation failed, reject immediately
        if not signature_valid:
            return False

        # Timestamp validation (anti-replay attack)
        # Check both headers and payload for timestamp
        timestamp = request.headers.get("X-Twilio-Timestamp") or request.headers.get("Telnyx-Timestamp")

        if isinstance(payload, dict):
            timestamp = timestamp or payload.get("timestamp")

        if timestamp:
            try:
                webhook_time = int(timestamp)
                current_time = int(time.time())
                time_diff = abs(current_time - webhook_time)

                # Reject if older than 5 minutes (300 seconds)
                if time_diff > 300:
                    logger.warning(
                        "Webhook rejected for %s: timestamp too old (%d seconds)",
                        telephony_type.value,
                        time_diff
                    )
                    return False

                logger.debug(
                    "Webhook timestamp validated for %s: %d seconds old",
                    telephony_type.value,
                    time_diff
                )

            except (ValueError, TypeError) as exc:
                logger.warning(
                    "Webhook rejected for %s: invalid timestamp format - %s",
                    telephony_type.value,
                    exc
                )
                return False

        return True

    except Exception as exc:
        logger.error("Webhook validation error for %s: %s", telephony_type.value, exc)
        # Fail secure: reject webhook if validation fails
        return False


@router.post("/outbound")
async def initiate_outbound_call(request: OutboundCallRequest) -> JSONResponse:
    """Initiate an outbound call via the configured telephony adapter.

    This is a stub implementation that validates adapter configuration and reserves
    the interface for the full WS-C streaming bridge. The actual call initiation and
    streaming pipeline will be implemented in the dedicated workstream.
    """

    defaults, _ = fetch_provider_defaults()

    provider_id = request.telephony_provider or defaults.telephony_provider.value
    try:
        telephony_type = TelephonyType(provider_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported telephony provider '{provider_id}'",
        ) from exc

    registry = get_provider_registry()

    try:
        adapter = registry.create_telephony_adapter(telephony_type)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    session_manager = get_session_manager()

    from_number = request.from_number or defaults.telephony_from_number
    if not from_number:
        settings = get_settings()
        if telephony_type == TelephonyType.TELNYX:
            from_number = getattr(settings, "telnyx_phone_number", None)
        else:
            from_number = (
                getattr(settings, "twilio_phone_number_cz", None)
                or getattr(settings, "twilio_phone_number_us", None)
            )
        from_number = from_number or request.from_number

    if not from_number:
        raise HTTPException(
            status_code=400,
            detail="Caller ID (from_number) is required and no default is configured",
        )

    # Check recording consent before starting call
    has_recording_consent = compliance_service.check_consent(
        customer_phone=request.to_number,
        consent_type=ConsentType.RECORDING
    )

    if not has_recording_consent:
        logger.warning("No recording consent for phone number: %s", request.to_number)
        # Still allow call but mark as non-recorded
        recording_consent_status = "denied"
    else:
        logger.info("Recording consent granted for phone number: %s", request.to_number)
        recording_consent_status = "granted"

    session_request = SessionCreateRequest(
        provider=defaults.default_provider.value,
        provider_model=defaults.openai_model,
        strategy=defaults.strategy,
        telephony_provider=telephony_type.value,
        phone_number=request.to_number,
        metadata={
            "from_number": from_number,
            "to_number": request.to_number,
            "recording_consent": recording_consent_status,
            "compliance_checked": True,
            **request.metadata,
        },
    )

    session = await session_manager.create_session(session_request)

    try:
        await session_manager.start_session(session.id)
    except Exception as exc:
        logger.warning("Failed to start provider session %s: %s", session.id, exc)

    stream_url = _build_stream_url(session.id, request.stream_url)

    twiml = adapter.generate_answer_twiml(stream_url)

    call_sid = None
    try:
        call_result = await adapter.setup_call(
            {
                "from_number": from_number,
                "to_number": request.to_number,
                "stream_url": stream_url,
                "metadata": request.metadata,
            }
        )
        call_sid = call_result.get("call_id") if call_result else None
    except Exception as exc:
        logger.error("Telephony adapter failed to initiate call: %s", exc)
        await session_manager.end_session(session.id)
        raise HTTPException(status_code=500, detail="Failed to initiate outbound call") from exc
    finally:
        close_callable = getattr(adapter, "close", None)
        if callable(close_callable):  # type: ignore[call-arg]
            result = close_callable()  # type: ignore[misc]
            if result and hasattr(result, "__await__"):
                await result

    logger.info(
        "Prepared telephony adapter %s for call %s -> %s (session %s)",
        telephony_type.value,
        from_number,
        request.to_number,
        session.id,
    )

    if call_sid:
        telephony_state.register_call(call_sid, session.id)

    return JSONResponse(
        status_code=202,
        content={
            "status": "accepted",
            "session_id": str(session.id),
            "stream_url": stream_url,
            "twiML": twiml,
            "telephony_provider": telephony_type.value,
            "call_sid": call_sid,
            "from_number": from_number,
            "to_number": request.to_number,
        },
    )


@router.post("/webhooks/{provider}")
@limiter.limit(WEBHOOK_RATE_LIMIT)
async def receive_webhook(provider: str, request: Request) -> JSONResponse:
    """Receive webhook callbacks from telephony providers (Twilio/Telnyx).

    Security layers (applied in order):
    1. Rate Limiting - Prevent abuse (100 requests/minute per IP)
    2. IP Whitelisting - Verify source IP matches provider whitelist
    3. Signature Validation - Cryptographic verification of webhook authenticity
    4. Timestamp Validation - Prevent replay attacks (via _validate_webhook_signature)
    """

    try:
        telephony_type = TelephonyType(provider)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail="Unknown telephony provider") from exc

    # Security Layer 1: IP Whitelisting
    if not _validate_webhook_ip(request, telephony_type):
        logger.warning(
            "Webhook rejected from non-whitelisted IP: %s for provider %s",
            request.client.host if request.client else "unknown",
            provider
        )
        raise HTTPException(
            status_code=403,
            detail="Webhook rejected: IP not whitelisted"
        )

    content_type = request.headers.get("content-type", "")
    if "application/json" in content_type:
        payload = await request.json()
    else:
        form = await request.form()
        payload = {key: form[key] for key in form}

    # Security Layer 2 & 3: Signature and Timestamp Validation
    feature_flags = get_feature_flags()
    if feature_flags.enable_webhook_validation:
        if not await _validate_webhook_signature(telephony_type, request, payload):
            logger.warning(
                "Invalid webhook signature for provider %s from %s",
                provider,
                request.client.host if request.client else "unknown"
            )
            raise HTTPException(status_code=403, detail="Invalid webhook signature")

    call_sid = str(payload.get("CallSid") or payload.get("callSid") or "")

    session_manager = get_session_manager()

    if call_sid and not telephony_state.get_session_for_call(call_sid):
        defaults, _ = fetch_provider_defaults()
        session_manager = get_session_manager()

        to_number = str(payload.get("To") or "")
        from_number = str(payload.get("From") or "")

        session_request = SessionCreateRequest(
            provider=defaults.default_provider.value,
            provider_model=defaults.openai_model,
            strategy=defaults.strategy,
            telephony_provider=telephony_type.value,
            phone_number=to_number if to_number else None,
            metadata={
                "from_number": from_number,
                "call_sid": call_sid,
            },
        )

        session = await session_manager.create_session(session_request)

        try:
            await session_manager.start_session(session.id)
        except Exception as exc:
            logger.warning("Failed to start provider session %s: %s", session.id, exc)

        stream_url = _build_stream_url(session.id)

        adapter = get_provider_registry().create_telephony_adapter(telephony_type)
        twiml = adapter.generate_answer_twiml(stream_url)

        close_callable = getattr(adapter, "close", None)
        if callable(close_callable):  # type: ignore[call-arg]
            result = close_callable()  # type: ignore[misc]
            if result and hasattr(result, "__await__"):
                await result

        telephony_state.register_call(call_sid, session.id)

        return JSONResponse(
            status_code=200,
            content={
                "status": "accepted",
                "session_id": str(session.id),
                "stream_url": stream_url,
                "twiML": twiml,
                "telephony_provider": telephony_type.value,
            },
        )

    if call_sid:
        session_id = telephony_state.get_session_for_call(call_sid)
        event_type = str(payload.get("EventType") or payload.get("eventType") or "").lower()
        call_status = str(payload.get("CallStatus") or payload.get("callStatus") or "").lower()

        if session_id and (event_type in {"completed", "stop", "end"} or call_status in {"completed", "canceled"}):
            await session_manager.end_session(session_id)
            telephony_state.unregister_call(call_sid)
            return JSONResponse(
                status_code=202,
                content={
                    "status": "completed",
                    "telephony_provider": telephony_type.value,
                },
            )

    logger.info(
        "Received %s webhook payload: %s",
        telephony_type.value,
        payload,
    )

    return JSONResponse(
        status_code=202,
        content={
            "status": "accepted",
            "telephony_provider": telephony_type.value,
        },
    )
