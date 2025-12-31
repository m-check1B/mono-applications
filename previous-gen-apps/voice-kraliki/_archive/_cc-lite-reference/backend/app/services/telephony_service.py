"""Telephony service - Twilio integration"""

from typing import Optional
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)


class TelephonyService:
    """Service for telephony operations using Twilio"""

    def __init__(self):
        """Initialize Twilio client"""
        if not settings.has_telephony():
            logger.warning("Telephony not configured - service will be disabled")
            self.client = None
            return

        self.client = Client(
            settings.TWILIO_ACCOUNT_SID,
            settings.TWILIO_AUTH_TOKEN
        )
        self.phone_number = settings.TWILIO_PHONE_NUMBER
        logger.info(f"Telephony service initialized with number: {self.phone_number}")

    def is_available(self) -> bool:
        """Check if telephony service is available"""
        return self.client is not None

    async def create_call(
        self,
        to_number: str,
        from_number: Optional[str] = None,
        twiml_url: Optional[str] = None,
        status_callback_url: Optional[str] = None
    ) -> dict:
        """
        Create an outbound call

        Args:
            to_number: Destination phone number
            from_number: Source phone number (default: configured number)
            twiml_url: TwiML URL for call instructions
            status_callback_url: URL for status callbacks

        Returns:
            Call details from Twilio

        Raises:
            ValueError: If telephony not configured
            TwilioRestException: If call creation fails
        """
        if not self.is_available():
            raise ValueError("Telephony service not configured")

        from_number = from_number or self.phone_number

        try:
            call = self.client.calls.create(
                to=to_number,
                from_=from_number,
                url=twiml_url,
                status_callback=status_callback_url,
                status_callback_event=['initiated', 'ringing', 'answered', 'completed'],
                status_callback_method='POST'
            )

            logger.info(f"Call created: {call.sid} from {from_number} to {to_number}")

            return {
                "call_sid": call.sid,
                "status": call.status,
                "direction": call.direction,
                "from_number": call.from_,
                "to_number": call.to
            }

        except TwilioRestException as e:
            logger.error(f"Twilio error creating call: {e}")
            raise

    async def get_call(self, call_sid: str) -> dict:
        """
        Get call details from Twilio

        Args:
            call_sid: Twilio call SID

        Returns:
            Call details

        Raises:
            ValueError: If telephony not configured
            TwilioRestException: If call not found
        """
        if not self.is_available():
            raise ValueError("Telephony service not configured")

        try:
            call = self.client.calls(call_sid).fetch()

            return {
                "call_sid": call.sid,
                "status": call.status,
                "direction": call.direction,
                "from_number": call.from_,
                "to_number": call.to,
                "duration": call.duration,
                "start_time": call.start_time,
                "end_time": call.end_time
            }

        except TwilioRestException as e:
            logger.error(f"Twilio error fetching call {call_sid}: {e}")
            raise

    async def update_call(self, call_sid: str, status: str) -> dict:
        """
        Update call status (e.g., cancel, complete)

        Args:
            call_sid: Twilio call SID
            status: New call status (completed, canceled)

        Returns:
            Updated call details

        Raises:
            ValueError: If telephony not configured
            TwilioRestException: If update fails
        """
        if not self.is_available():
            raise ValueError("Telephony service not configured")

        try:
            call = self.client.calls(call_sid).update(status=status)

            logger.info(f"Call {call_sid} updated to status: {status}")

            return {
                "call_sid": call.sid,
                "status": call.status
            }

        except TwilioRestException as e:
            logger.error(f"Twilio error updating call {call_sid}: {e}")
            raise

    async def get_recording(self, recording_sid: str) -> dict:
        """
        Get call recording details

        Args:
            recording_sid: Twilio recording SID

        Returns:
            Recording details

        Raises:
            ValueError: If telephony not configured
            TwilioRestException: If recording not found
        """
        if not self.is_available():
            raise ValueError("Telephony service not configured")

        try:
            recording = self.client.recordings(recording_sid).fetch()

            return {
                "recording_sid": recording.sid,
                "call_sid": recording.call_sid,
                "duration": recording.duration,
                "url": f"https://api.twilio.com{recording.uri.replace('.json', '.mp3')}"
            }

        except TwilioRestException as e:
            logger.error(f"Twilio error fetching recording {recording_sid}: {e}")
            raise


# Singleton instance
telephony_service = TelephonyService()


def get_telephony_service() -> TelephonyService:
    """Lightweight accessor to the shared telephony service."""
    return telephony_service
