"""
API endpoints for telephony operations.
"""

import logging
import uuid
from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel, Field

from app.middleware.rate_limit import (
    API_RATE_LIMIT,
    BILLING_RATE_LIMIT,
    CALL_INITIATION_RATE_LIMIT,
    limiter,
)
from app.providers.registry import TelephonyType, get_provider_registry
from app.sessions.manager import get_session_manager
from app.sessions.models import SessionCreateRequest, SessionStatus
from app.settings.provider import fetch_settings as fetch_provider_defaults
from app.telephony.state import register_call, unregister_call

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/telephony", tags=["telephony"])


class CallRequest(BaseModel):
    to: str = Field(..., description="Phone number to call")
    from_: str | None = Field(None, description="Phone number to call from")
    script_id: int | None = Field(None, description="Script ID to use")
    company_id: int = Field(..., description="Company ID")
    provider: str | None = Field(None, description="Specific provider to use")
    metadata: dict[str, Any] = Field(default_factory=dict)


class CallResponse(BaseModel):
    success: bool
    call_id: str | None = None
    status: str | None = None
    error: str | None = None
    provider: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class CallRecord(BaseModel):
    id: str
    session_id: str
    from_number: str
    to_number: str
    status: str
    direction: str
    provider: str
    script_id: int | None = None
    company_id: int
    duration: int | None = None
    recording_url: str | None = None
    transcription: str | None = None
    cost: float | None = None
    created_at: str
    answered_at: str | None = None
    ended_at: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class PhoneNumberValidation(BaseModel):
    valid: bool
    phone_number: str
    country_code: str | None = None
    carrier: dict[str, Any] | None = None
    error: str | None = None


class ProviderHealth(BaseModel):
    provider: str
    status: str
    timestamp: str
    details: dict[str, Any] | None = None
    error: str | None = None


# In-memory call storage (persists for process lifetime)
calls_db: dict[str, CallRecord] = {}


def _utc_iso(dt: datetime | None) -> str | None:
    if not dt:
        return None
    return dt.replace(microsecond=0, tzinfo=None).isoformat() + "Z"


async def _sync_call_with_session(call: CallRecord) -> CallRecord:
    """Update call status metadata based on session manager."""

    try:
        session_uuid = UUID(call.session_id)
    except ValueError:
        return call

    session_manager = get_session_manager()
    session = await session_manager.get_session(session_uuid)
    if not session:
        return call

    call.status = session.status.value
    call.metadata["session_status"] = session.status.value
    call.metadata["updated_at"] = _utc_iso(session.updated_at)
    if session.ended_at:
        call.ended_at = _utc_iso(session.ended_at)

    return call


@router.post("/call", response_model=CallResponse)
@limiter.limit(CALL_INITIATION_RATE_LIMIT)
async def make_call(http_request: Request, request: CallRequest):
    """Make an outbound call backed by session manager. Rate limited to prevent call flooding."""
    try:
        if not request.to.startswith('+'):
            return CallResponse(
                success=False,
                error="Phone number must be in E.164 format (e.g., +1234567890)",
                provider="none"
            )

        call_id = f"call_{uuid.uuid4().hex[:12]}"
        session_manager = get_session_manager()
        defaults, _ = fetch_provider_defaults()
        registry = get_provider_registry()

        provider_id = request.provider or defaults.telephony_provider.value

        try:
            telephony_provider = TelephonyType(provider_id)
        except ValueError as exc:
            raise HTTPException(
                status_code=400, detail=f"Unsupported telephony provider '{provider_id}'"
            ) from exc

        telephony_info = registry.get_telephony_info(telephony_provider)
        if not telephony_info or not telephony_info.is_configured:
            raise HTTPException(
                status_code=400,
                detail=f"Telephony provider '{telephony_provider.value}' is not configured",
            )

        from_number = request.from_ or defaults.telephony_from_number
        if not from_number:
            raise HTTPException(
                status_code=400,
                detail="Caller ID (from_number) is required and no default is configured",
            )

        metadata = {
            "from_number": from_number,
            "company_id": request.company_id,
            "script_id": request.script_id,
            **request.metadata,
        }

        session_request = SessionCreateRequest(
            provider=defaults.default_provider.value,
            provider_model=defaults.openai_model,
            telephony_provider=telephony_provider.value,
            phone_number=request.to,
            metadata=metadata,
        )

        session = await session_manager.create_session(session_request)

        status = "queued"
        try:
            await session_manager.start_session(session.id)
            status = SessionStatus.ACTIVE.value
        except Exception as exc:  # pragma: no cover - logged for observability
            logger.warning("Failed to start session %s: %s", session.id, exc)
            status = SessionStatus.PENDING.value

        timestamp = datetime.now(UTC).isoformat(timespec="seconds") + "Z"
        call_record = CallRecord(
            id=call_id,
            session_id=str(session.id),
            from_number=from_number,
            to_number=request.to,
            status=status,
            direction="outbound",
            provider=telephony_provider.value,
            script_id=request.script_id,
            company_id=request.company_id,
            created_at=timestamp,
            metadata={**metadata, "session_id": str(session.id)},
        )

        calls_db[call_id] = call_record
        register_call(call_id, session.id)

        return CallResponse(
            success=True,
            call_id=call_id,
            status=status,
            provider=telephony_provider.value,
            metadata={
                "session_id": str(session.id),
                "telephony_provider": telephony_provider.value,
            },
        )

    except HTTPException:
        raise
    except Exception as e:  # pragma: no cover - unexpected failure
        logger.exception("Failed to initiate telephony call")
        return CallResponse(
            success=False,
            error=str(e),
            provider="none"
        )


@router.get("/call/{call_id}", response_model=CallRecord)
async def get_call_status(call_id: str):
    """Get the status of a call."""
    call = calls_db.get(call_id)
    if not call:
        raise HTTPException(status_code=404, detail="Call not found")

    updated = await _sync_call_with_session(call)
    calls_db[call_id] = updated
    return updated


@router.post("/call/{call_id}/end")
@limiter.limit(API_RATE_LIMIT)
async def end_call(request: Request, call_id: str):
    """End an active call. Rate limited."""
    call = calls_db.get(call_id)
    if not call:
        raise HTTPException(status_code=404, detail="Call not found")

    if call.status in ["completed", "failed", "canceled", SessionStatus.COMPLETED.value]:
        raise HTTPException(status_code=400, detail="Call is already ended")

    session_uuid: UUID | None = None
    try:
        session_uuid = UUID(call.session_id)
    except ValueError:
        logger.warning("Call %s has invalid session_id %s", call_id, call.session_id)

    if session_uuid:
        try:
            session_manager = get_session_manager()
            await session_manager.end_session(session_uuid)
        except Exception as exc:  # pragma: no cover - best effort shutdown
            logger.warning("Failed to end session %s for call %s: %s", session_uuid, call_id, exc)

    call.status = SessionStatus.COMPLETED.value
    call.ended_at = _utc_iso(datetime.now(UTC))
    call.metadata["session_status"] = SessionStatus.COMPLETED.value
    unregister_call(call_id)

    return {"message": "Call ended successfully", "call_id": call_id}


@router.get("/calls", response_model=list[CallRecord])
async def get_calls(
    company_id: int | None = Query(None),
    status: str | None = Query(None),
    provider: str | None = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """Get list of calls with filtering."""
    calls = []
    for call_id, record in calls_db.items():
        updated = await _sync_call_with_session(record)
        calls_db[call_id] = updated
        calls.append(updated)

    # Apply filters
    if company_id:
        calls = [c for c in calls if c.company_id == company_id]
    if status:
        calls = [c for c in calls if c.status == status]
    if provider:
        calls = [c for c in calls if c.provider == provider]

    return calls[offset:offset + limit]


@router.post("/validate-number", response_model=PhoneNumberValidation)
@limiter.limit(API_RATE_LIMIT)
async def validate_phone_number(
    request: Request,
    phone_number: str = Query(..., description="Phone number to validate"),
    provider: str | None = Query(None, description="Provider to use for validation")
):
    """Validate a phone number. Rate limited."""
    try:
        # Mock validation
        if not phone_number.startswith('+'):
            return PhoneNumberValidation(
                valid=False,
                phone_number=phone_number,
                error="Phone number must be in E.164 format"
            )

        # Simulate successful validation
        return PhoneNumberValidation(
            valid=True,
            phone_number=phone_number,
            country_code="US",
            carrier={
                "name": "Mock Carrier",
                "type": "mobile",
                "mobile": True
            }
        )

    except Exception as e:
        return PhoneNumberValidation(
            valid=False,
            phone_number=phone_number,
            error=str(e)
        )


@router.get("/providers", response_model=dict[str, Any])
async def get_providers():
    """Get available telephony providers."""
    registry = get_provider_registry()
    defaults, _ = fetch_provider_defaults()

    providers: dict[str, Any] = {}
    adapters = registry.list_telephony_adapters()
    for adapter in adapters:
        providers[adapter.id] = {
            "name": adapter.name,
            "is_configured": adapter.is_configured,
            "capabilities": adapter.capabilities.model_dump(),
            "is_primary": adapter.id == defaults.telephony_provider.value,
        }

    fallback_providers = [
        adapter.id for adapter in adapters if adapter.id != defaults.telephony_provider.value
    ]

    return {
        "providers": providers,
        "primary_provider": defaults.telephony_provider.value,
        "fallback_providers": fallback_providers,
    }


@router.get("/providers/health", response_model=list[ProviderHealth])
async def get_provider_health():
    """Get health status of all providers."""
    registry = get_provider_registry()
    defaults, _ = fetch_provider_defaults()
    now = datetime.now(UTC).isoformat(timespec="seconds") + "Z"

    health_results = []
    for adapter in registry.list_telephony_adapters():
        status = "healthy" if adapter.is_configured else "unconfigured"
        health_results.append(
            ProviderHealth(
                provider=adapter.id,
                status=status,
                timestamp=now,
                details={
                    "name": adapter.name,
                    "is_primary": adapter.id == defaults.telephony_provider.value,
                    "capabilities": adapter.capabilities.model_dump(),
                },
            )
        )

    return health_results


@router.get("/providers/{provider_id}/numbers")
async def get_available_numbers(
    provider_id: str,
    country_code: str = Query("US", description="Country code")
):
    """Get available phone numbers for a provider."""
    try:
        telephony_type = TelephonyType(provider_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Provider not found")

    registry = get_provider_registry()
    adapter = registry.get_telephony_info(telephony_type)
    if not adapter:
        raise HTTPException(status_code=404, detail="Provider not found")

    # Mock available numbers
    mock_numbers = [
        f"+1202555{i:04d}" for i in range(1000, 1010)
    ]

    return {
        "provider": provider_id,
        "country_code": country_code,
        "available_numbers": mock_numbers
    }


@router.post("/providers/{provider_id}/numbers/purchase")
@limiter.limit(BILLING_RATE_LIMIT)
async def purchase_number(
    request: Request,
    provider_id: str,
    phone_number: str = Query(..., description="Phone number to purchase")
):
    """Purchase a phone number from a provider. Rate limited (billing operation)."""
    try:
        telephony_type = TelephonyType(provider_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Provider not found")

    registry = get_provider_registry()
    adapter = registry.get_telephony_info(telephony_type)
    if not adapter:
        raise HTTPException(status_code=404, detail="Provider not found")

    # Mock purchase
    return {
        "success": True,
        "provider": provider_id,
        "phone_number": phone_number,
        "message": "Number purchased successfully"
    }


@router.get("/call/{call_id}/recording")
async def get_call_recording(call_id: str):
    """Get the recording URL for a call."""
    call = calls_db.get(call_id)
    if not call:
        raise HTTPException(status_code=404, detail="Call not found")

    call = await _sync_call_with_session(call)
    calls_db[call_id] = call

    # Mock recording URL
    recording_url = f"https://api.mock-provider.com/recordings/{call_id}.mp3"

    return {
        "call_id": call_id,
        "recording_url": recording_url,
        "duration": call.duration or 0
    }


@router.get("/call/{call_id}/transcription")
async def get_call_transcription(call_id: str):
    """Get the transcription for a call."""
    call = calls_db.get(call_id)
    if not call:
        raise HTTPException(status_code=404, detail="Call not found")

    call = await _sync_call_with_session(call)
    calls_db[call_id] = call

    # Mock transcription
    mock_transcription = "Hello, this is a mock transcription of the call content."

    return {
        "call_id": call_id,
        "transcription": mock_transcription,
        "confidence": 0.95
    }


@router.get("/stats")
async def get_telephony_stats():
    """Get telephony statistics."""
    calls = []
    for call_id, record in calls_db.items():
        updated = await _sync_call_with_session(record)
        calls_db[call_id] = updated
        calls.append(updated)

    total_calls = len(calls)
    active_calls = len(
        [c for c in calls if c.status not in {SessionStatus.COMPLETED.value, "completed", "failed", "canceled"}]
    )
    completed_calls = len(
        [c for c in calls if c.status in {SessionStatus.COMPLETED.value, "completed"}]
    )

    registry = get_provider_registry()
    adapters = registry.list_telephony_adapters()

    return {
        "total_calls": total_calls,
        "active_calls": active_calls,
        "completed_calls": completed_calls,
        "providers": len(adapters),
        "calls_by_provider": {
            adapter.id: len([c for c in calls if c.provider == adapter.id])
            for adapter in adapters
        },
    }
