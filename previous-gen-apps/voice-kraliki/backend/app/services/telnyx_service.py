"""
Telnyx telephony provider implementation.
"""

import os
from datetime import UTC, datetime
from typing import Any

try:
    import telnyx
    TELNYX_AVAILABLE = True
except ImportError:
    TELNYX_AVAILABLE = False

from app.providers.telephony_provider import (
    CallDirection,
    CallRecord,
    CallRequest,
    CallResponse,
    CallStatus,
    TelephonyProvider,
)


class TelnyxService(TelephonyProvider):
    """Telnyx telephony provider implementation."""

    def __init__(self, config: dict[str, Any]):
        super().__init__(config)

        if not TELNYX_AVAILABLE:
            raise ImportError("Telnyx library not installed. Install with: pip install telnyx")

        self.api_key = config.get("api_key") or os.getenv("TELNYX_API_KEY")
        self.from_number = config.get("from_number") or os.getenv("TELNYX_FROM_NUMBER")

        if not self.api_key:
            raise ValueError("Telnyx API key is required")

        telnyx.api_key = self.api_key

    async def make_call(self, request: CallRequest) -> CallResponse:
        """Initiate an outbound call using Telnyx."""
        try:
            # Use provided from number or default
            from_number = request.from_ or self.from_number

            if not from_number:
                return CallResponse(
                    success=False,
                    error="No from number provided and no default configured",
                    provider=self.provider_name
                )

            # Create call with Telnyx
            call = telnyx.Call.create(
                connection_id=request.to,
                from_number=from_number,
                to_number=request.to,
                webhook_url="https://your-domain.com/api/telnyx/webhook",
                webhook_url_method="POST",
                recording_enabled="true",
                transcription_enabled="true",
                answer_method="POST",
                hangup_method="POST"
            )

            return CallResponse(
                success=True,
                call_id=call.id,
                status=CallStatus.QUEUED,
                provider=self.provider_name,
                metadata={"telnyx_call_id": call.id}
            )

        except Exception as e:
            return CallResponse(
                success=False,
                error=f"Telnyx error: {str(e)}",
                provider=self.provider_name
            )

    async def get_call_status(self, call_id: str) -> CallRecord:
        """Get the current status of a Telnyx call."""
        try:
            call = telnyx.Call.retrieve(call_id)

            # Map Telnyx status to our enum
            status_mapping = {
                "queued": CallStatus.QUEUED,
                "ringing": CallStatus.RINGING,
                "answered": CallStatus.IN_PROGRESS,
                "completed": CallStatus.COMPLETED,
                "failed": CallStatus.FAILED,
                "busy": CallStatus.BUSY,
                "no-answer": CallStatus.NO_ANSWER,
                "canceled": CallStatus.CANCELED,
                "hangup": CallStatus.COMPLETED
            }

            status = status_mapping.get(call.status, CallStatus.FAILED)

            # Get recording if available
            recording_url = None
            if hasattr(call, 'recording') and call.recording:
                recording_url = call.recording.get('url')

            return CallRecord(
                id=call.id,
                from_number=call.from_number,
                to_number=call.to_number,
                status=status,
                direction=CallDirection.OUTBOUND,
                provider=self.provider_name,
                duration=call.duration_seconds if hasattr(call, 'duration_seconds') else None,
                recording_url=recording_url,
                cost=float(call.cost) if hasattr(call, 'cost') and call.cost else None,
                created_at=call.created_at if hasattr(call, 'created_at') else datetime.now(UTC).isoformat(),
                answered_at=call.answered_at if hasattr(call, 'answered_at') else None,
                ended_at=call.ended_at if hasattr(call, 'ended_at') else None,
                metadata={
                    "telnyx_status": call.status,
                    "telnyx_direction": call.direction if hasattr(call, 'direction') else 'outbound'
                }
            )

        except Exception as e:
            raise Exception(f"Failed to get Telnyx call status: {str(e)}")

    async def end_call(self, call_id: str) -> bool:
        """End an active Telnyx call."""
        try:
            call = telnyx.Call.retrieve(call_id)
            call.hangup()
            return True
        except Exception:
            return False

    async def get_call_recording(self, call_id: str) -> str | None:
        """Get the recording URL for a Telnyx call."""
        try:
            call = telnyx.Call.retrieve(call_id)
            if hasattr(call, 'recording') and call.recording:
                return call.recording.get('url')
            return None
        except Exception:
            return None

    async def get_call_transcription(self, call_id: str) -> str | None:
        """Get the transcription for a Telnyx call."""
        try:
            call = telnyx.Call.retrieve(call_id)
            if hasattr(call, 'transcription') and call.transcription:
                return call.transcription.get('text')
            return None
        except Exception:
            return None

    async def get_available_numbers(self, country_code: str = "US") -> list[str]:
        """Get available Telnyx phone numbers."""
        try:
            available_numbers = telnyx.AvailablePhoneNumber.list(
                country_code=country_code,
                limit=20,
                voice_enabled=True,
                features=["voice"]
            )
            return [num.phone_number for num in available_numbers]
        except Exception:
            return []

    async def purchase_number(self, phone_number: str) -> bool:
        """Purchase a Telnyx phone number."""
        try:
            incoming_phone_number = telnyx.IncomingPhoneNumber.create(
                phone_number=phone_number,
                connection_id=os.getenv("TELNYX_CONNECTION_ID"),
                webhook_url="https://your-domain.com/api/telnyx/webhook"
            )
            return bool(incoming_phone_number.id)
        except Exception:
            return False

    async def release_number(self, phone_number: str) -> bool:
        """Release a Telnyx phone number."""
        try:
            numbers = telnyx.IncomingPhoneNumber.list(phone_number=phone_number)
            if numbers:
                numbers[0].delete()
                return True
            return False
        except Exception:
            return False

    async def get_call_cost(self, call_id: str) -> float | None:
        """Get the cost of a Telnyx call."""
        try:
            call = telnyx.Call.retrieve(call_id)
            return float(call.cost) if hasattr(call, 'cost') and call.cost else None
        except Exception:
            return None

    async def validate_phone_number(self, phone_number: str) -> dict[str, Any]:
        """Validate a phone number using Telnyx Number Lookup API."""
        try:
            # Telnyx number validation
            number_lookup = telnyx.NumberLookup.create(
                phone_number=phone_number,
                type=["carrier"]
            )

            return {
                "valid": True,
                "phone_number": number_lookup.phone_number,
                "country_code": number_lookup.country_code,
                "carrier": {
                    "name": number_lookup.carrier.get('name') if number_lookup.carrier else None,
                    "type": number_lookup.carrier.get('type') if number_lookup.carrier else None,
                    "mobile": number_lookup.carrier.get('mobile') if number_lookup.carrier else None
                }
            }
        except Exception as e:
            return {
                "valid": False,
                "error": str(e),
                "phone_number": phone_number
            }

    def get_supported_features(self) -> list[str]:
        """Get the list of supported features for Telnyx."""
        return [
            "outbound_calls",
            "inbound_calls",
            "call_recording",
            "call_transcription",
            "number_provisioning",
            "call_validation",
            "cost_tracking",
            "sms_support",
            "fax_support",
            "webhook_support",
            "sip_support"
        ]
