"""
Twilio telephony provider implementation.
"""

import os
from typing import Any

try:
    from twilio.base.exceptions import TwilioRestException
    from twilio.rest import Client
    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False

from app.providers.telephony_provider import (
    CallDirection,
    CallRecord,
    CallRequest,
    CallResponse,
    CallStatus,
    TelephonyProvider,
)


class TwilioService(TelephonyProvider):
    """Twilio telephony provider implementation."""

    def __init__(self, config: dict[str, Any]):
        super().__init__(config)

        if not TWILIO_AVAILABLE:
            raise ImportError("Twilio library not installed. Install with: pip install twilio")

        self.account_sid = config.get("account_sid") or os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = config.get("auth_token") or os.getenv("TWILIO_AUTH_TOKEN")
        self.from_number = config.get("from_number") or os.getenv("TWILIO_FROM_NUMBER")

        if not self.account_sid or not self.auth_token:
            raise ValueError("Twilio account_sid and auth_token are required")

        self.client = Client(self.account_sid, self.auth_token)

    async def make_call(self, request: CallRequest) -> CallResponse:
        """Initiate an outbound call using Twilio."""
        try:
            # Use provided from number or default
            from_number = request.from_ or self.from_number

            if not from_number:
                return CallResponse(
                    success=False,
                    error="No from number provided and no default configured",
                    provider=self.provider_name
                )

            # Create TwiML application URL with script and company info
            twiml_url = f"https://your-domain.com/api/twilio/webhook?script_id={request.script_id}&company_id={request.company_id}"

            # Make the call
            call = self.client.calls.create(
                to=request.to,
                from_=from_number,
                url=twiml_url,
                method="POST",
                record=True,
                recording_status_callback="https://your-domain.com/api/twilio/recording-callback",
                status_callback="https://your-domain.com/api/twilio/status-callback",
                status_callback_method="POST"
            )

            return CallResponse(
                success=True,
                call_id=call.sid,
                status=CallStatus.QUEUED,
                provider=self.provider_name,
                metadata={"twilio_call_sid": call.sid}
            )

        except TwilioRestException as e:
            return CallResponse(
                success=False,
                error=str(e),
                provider=self.provider_name
            )
        except Exception as e:
            return CallResponse(
                success=False,
                error=f"Unexpected error: {str(e)}",
                provider=self.provider_name
            )

    async def get_call_status(self, call_id: str) -> CallRecord:
        """Get the current status of a Twilio call."""
        try:
            call = self.client.calls(call_id).fetch()

            # Map Twilio status to our enum
            status_mapping = {
                "queued": CallStatus.QUEUED,
                "ringing": CallStatus.RINGING,
                "in-progress": CallStatus.IN_PROGRESS,
                "completed": CallStatus.COMPLETED,
                "failed": CallStatus.FAILED,
                "busy": CallStatus.BUSY,
                "no-answer": CallStatus.NO_ANSWER,
                "canceled": CallStatus.CANCELED
            }

            status = status_mapping.get(call.status, CallStatus.FAILED)

            # Get recording if available
            recording_url = None
            if call.recordings:
                recording = call.recordings.list(limit=1)[0]
                recording_url = recording.url

            return CallRecord(
                id=call.sid,
                from_number=call.from_,
                to_number=call.to,
                status=status,
                direction=CallDirection.OUTBOUND if call.direction == "outbound-api" else CallDirection.INBOUND,
                provider=self.provider_name,
                duration=call.duration,
                recording_url=recording_url,
                cost=float(call.price) if call.price else None,
                created_at=call.date_created.isoformat(),
                answered_at=call.date_answered.isoformat() if call.date_answered else None,
                ended_at=call.end_time.isoformat() if call.end_time else None,
                metadata={
                    "twilio_status": call.status,
                    "twilio_from_country": call.from_country,
                    "twilio_to_country": call.to_country
                }
            )

        except Exception as e:
            raise Exception(f"Failed to get call status: {str(e)}")

    async def end_call(self, call_id: str) -> bool:
        """End an active Twilio call."""
        try:
            call = self.client.calls(call_id).update(status="completed")
            return call.status == "completed"
        except Exception:
            return False

    async def get_call_recording(self, call_id: str) -> str | None:
        """Get the recording URL for a Twilio call."""
        try:
            recordings = self.client.recordings(call=call_id).list()
            if recordings:
                recording = recordings[0]
                return f"https://api.twilio.com/2010-04-01/Accounts/{self.account_sid}/Recordings/{recording.sid}.mp3"
            return None
        except Exception:
            return None

    async def get_call_transcription(self, call_id: str) -> str | None:
        """Get the transcription for a Twilio call."""
        try:
            # Twilio transcriptions are separate from recordings
            transcriptions = self.client.transcriptions(call=call_id).list()
            if transcriptions:
                transcription = transcriptions[0]
                return transcription.transcription_text
            return None
        except Exception:
            return None

    async def get_available_numbers(self, country_code: str = "US") -> list[str]:
        """Get available Twilio phone numbers."""
        try:
            available_numbers = self.client.available_phone_numbers(country_code).local
            numbers = available_numbers.list(limit=20, voice_enabled=True, sms_enabled=False)
            return [num.phone_number for num in numbers]
        except Exception:
            return []

    async def purchase_number(self, phone_number: str) -> bool:
        """Purchase a Twilio phone number."""
        try:
            incoming_phone_number = self.client.incoming_phone_numbers.create(
                phone_number=phone_number,
                voice_url="https://your-domain.com/api/twilio/voice-webhook",
                voice_method="POST"
            )
            return bool(incoming_phone_number.sid)
        except Exception:
            return False

    async def release_number(self, phone_number: str) -> bool:
        """Release a Twilio phone number."""
        try:
            numbers = self.client.incoming_phone_numbers.list(phone_number=phone_number)
            if numbers:
                numbers[0].delete()
                return True
            return False
        except Exception:
            return False

    async def get_call_cost(self, call_id: str) -> float | None:
        """Get the cost of a Twilio call."""
        try:
            call = self.client.calls(call_id).fetch()
            return float(call.price) if call.price else None
        except Exception:
            return None

    async def validate_phone_number(self, phone_number: str) -> dict[str, Any]:
        """Validate a phone number using Twilio Lookup API."""
        try:
            lookup = self.client.lookups.v1.phone_numbers(phone_number).fetch(
                type=["carrier", "caller-name"]
            )

            return {
                "valid": True,
                "phone_number": lookup.phone_number,
                "country_code": lookup.country_code,
                "carrier": {
                    "name": lookup.carrier["name"] if lookup.carrier else None,
                    "type": lookup.carrier["type"] if lookup.carrier else None,
                    "mobile": lookup.carrier["mobile"] if lookup.carrier else None
                },
                "caller_name": {
                    "caller_name": lookup.caller_name["caller_name"] if lookup.caller_name else None,
                    "caller_type": lookup.caller_name["caller_type"] if lookup.caller_name else None
                }
            }
        except Exception as e:
            return {
                "valid": False,
                "error": str(e),
                "phone_number": phone_number
            }

    def get_supported_features(self) -> list[str]:
        """Get the list of supported features for Twilio."""
        return [
            "outbound_calls",
            "inbound_calls",
            "call_recording",
            "call_transcription",
            "number_provisioning",
            "call_validation",
            "cost_tracking",
            "sms_support",
            "voice_insights",
            "stream_support"
        ]
