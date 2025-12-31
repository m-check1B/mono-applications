"""Twilio telephony adapter implementation.

This module provides the TelephonyAdapter implementation for Twilio,
handling MediaStream WebSocket connections, audio conversion (μ-law to PCM),
TwiML generation, and webhook validation.
"""

import base64
import hashlib
import hmac
import logging
from typing import Any

import audioop
import httpx

from app.providers.base import (
    AudioChunk,
    AudioFormat,
    ProviderCapabilities,
)

logger = logging.getLogger(__name__)


class TwilioAdapter:
    """Twilio telephony service adapter.

    Handles Twilio MediaStream protocol, audio format conversion,
    and webhook validation using HMAC-SHA1.
    """

    def __init__(
        self,
        account_sid: str,
        auth_token: str,
        api_base_url: str = "https://api.twilio.com",
    ):
        """Initialize Twilio adapter.

        Args:
            account_sid: Twilio account SID
            auth_token: Twilio auth token
            api_base_url: Twilio API base URL
        """
        self._account_sid = account_sid
        self._auth_token = auth_token
        self._api_base_url = api_base_url
        self._http_client = httpx.AsyncClient()

    @property
    def capabilities(self) -> ProviderCapabilities:
        """Twilio adapter capabilities."""
        return ProviderCapabilities(
            supports_realtime=True,
            supports_text=False,  # Telephony only
            supports_audio=True,
            supports_multimodal=False,
            supports_function_calling=False,
            supports_streaming=True,
            audio_formats=[AudioFormat.ULAW, AudioFormat.PCM16],
            max_session_duration=14400,  # 4 hours max call duration
            cost_tier="standard",
        )

    async def setup_call(self, call_params: dict[str, Any]) -> dict[str, Any]:
        """Set up a new outbound Twilio call.

        Args:
            call_params: Call parameters including:
                - from_number: Twilio phone number
                - to_number: Destination phone number
                - stream_url: WebSocket URL for MediaStream
                - status_callback: Optional webhook URL

        Returns:
            dict: Call metadata (call_sid, status, etc.)

        Raises:
            httpx.HTTPError: If API call fails
        """
        url = f"{self._api_base_url}/2010-04-01/Accounts/{self._account_sid}/Calls.json"

        # Build TwiML for streaming
        twiml = self._generate_stream_twiml(
            stream_url=call_params["stream_url"],
            stream_name=call_params.get("stream_name", "audio-stream"),
        )

        # Prepare call data
        data = {
            "From": call_params["from_number"],
            "To": call_params["to_number"],
            "Twiml": twiml,
        }

        if "status_callback" in call_params:
            data["StatusCallback"] = call_params["status_callback"]
            data["StatusCallbackEvent"] = ["initiated", "ringing", "answered", "completed"]

        # Make API call
        response = await self._http_client.post(
            url,
            data=data,
            auth=(self._account_sid, self._auth_token),
        )
        response.raise_for_status()

        result = response.json()
        return {
            "call_id": result.get("sid"),
            "status": result.get("status"),
            "from": result.get("from"),
            "to": result.get("to"),
            "direction": result.get("direction"),
        }

    def _generate_stream_twiml(
        self, stream_url: str, stream_name: str = "audio-stream"
    ) -> str:
        """Generate TwiML for MediaStream connection.

        Args:
            stream_url: WebSocket URL for audio streaming
            stream_name: Name for the stream

        Returns:
            str: TwiML XML string
        """
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Connect>
        <Stream name="{stream_name}" url="{stream_url}">
            <Parameter name="custom_param" value="value"/>
        </Stream>
    </Connect>
</Response>"""

    def generate_answer_twiml(
        self, stream_url: str, stream_name: str = "audio-stream"
    ) -> str:
        """Generate TwiML for answering incoming call with stream.

        Args:
            stream_url: WebSocket URL for audio streaming
            stream_name: Name for the stream

        Returns:
            str: TwiML XML string (public method for webhook responses)
        """
        return self._generate_stream_twiml(stream_url, stream_name)

    async def handle_webhook(
        self, event_type: str, payload: dict[str, Any]
    ) -> dict[str, Any] | None:
        """Handle incoming webhook from Twilio.

        Args:
            event_type: Type of webhook event
            payload: Webhook payload

        Returns:
            Optional response data for the webhook
        """
        if event_type == "call_status":
            return await self._handle_call_status(payload)
        elif event_type == "incoming_call":
            return await self._handle_incoming_call(payload)
        else:
            logger.warning(f"Unknown webhook event type: {event_type}")
            return None

    async def _handle_call_status(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Handle call status webhook.

        Args:
            payload: Status webhook payload

        Returns:
            dict: Status information
        """
        return {
            "call_sid": payload.get("CallSid"),
            "status": payload.get("CallStatus"),
            "duration": payload.get("CallDuration"),
            "from": payload.get("From"),
            "to": payload.get("To"),
        }

    async def _handle_incoming_call(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Handle incoming call webhook.

        Args:
            payload: Incoming call webhook payload

        Returns:
            dict: Call information
        """
        return {
            "call_sid": payload.get("CallSid"),
            "from": payload.get("From"),
            "to": payload.get("To"),
            "caller_city": payload.get("FromCity"),
            "caller_state": payload.get("FromState"),
            "caller_country": payload.get("FromCountry"),
        }

    async def validate_webhook(
        self, signature: str, url: str, payload: dict[str, Any] | str
    ) -> bool:
        """Validate Twilio webhook signature using HMAC-SHA1.

        Args:
            signature: X-Twilio-Signature header value
            url: Full webhook URL (including protocol and query params)
            payload: Request payload (form data as dict or string)

        Returns:
            bool: True if signature is valid
        """
        # Build the signature data string
        data_string = url

        # If payload is a dict (form data), sort and append
        if isinstance(payload, dict):
            for key in sorted(payload.keys()):
                data_string += f"{key}{payload[key]}"
        elif isinstance(payload, str):
            data_string += payload

        # Compute HMAC-SHA1
        expected_signature = base64.b64encode(
            hmac.new(
                self._auth_token.encode("utf-8"),
                data_string.encode("utf-8"),
                hashlib.sha1,
            ).digest()
        ).decode("utf-8")

        # Compare signatures
        return hmac.compare_digest(expected_signature, signature)

    async def convert_audio_from_telephony(self, audio_data: bytes) -> AudioChunk:
        """Convert Twilio μ-law audio to PCM16.

        Twilio MediaStream sends audio as base64-encoded μ-law.
        This method decodes and converts to PCM16.

        Args:
            audio_data: Base64-encoded μ-law audio data

        Returns:
            AudioChunk: PCM16 audio chunk
        """
        # Decode base64
        try:
            ulaw_data = base64.b64decode(audio_data)
        except Exception as e:
            logger.error(f"Failed to decode base64 audio: {e}")
            raise ValueError(f"Invalid base64 audio data: {e}") from e

        # Convert μ-law to PCM16 (linear16)
        # Twilio uses 8kHz μ-law, we convert to 16kHz PCM16
        try:
            # First convert μ-law to PCM at 8kHz
            pcm_8k = audioop.ulaw2lin(ulaw_data, 2)  # 2 = 16-bit samples

            # Resample from 8kHz to 16kHz (most AI models expect 16kHz)
            pcm_16k = audioop.ratecv(
                pcm_8k,
                2,  # sample width (bytes)
                1,  # channels
                8000,  # input rate
                16000,  # output rate
                None,  # state (None for first call)
            )[0]

            return AudioChunk(
                data=pcm_16k,
                format=AudioFormat.PCM16,
                sample_rate=16000,
            )
        except Exception as e:
            logger.error(f"Failed to convert audio format: {e}")
            raise ValueError(f"Audio conversion failed: {e}") from e

    async def convert_audio_to_telephony(self, audio: AudioChunk) -> bytes:
        """Convert PCM16 audio to Twilio μ-law format.

        Args:
            audio: Audio chunk in PCM16 format

        Returns:
            bytes: Base64-encoded μ-law audio data for Twilio
        """
        pcm_data = audio.data

        try:
            # Resample to 8kHz if needed
            if audio.sample_rate != 8000:
                pcm_8k = audioop.ratecv(
                    pcm_data,
                    2,  # sample width
                    1,  # channels
                    audio.sample_rate,
                    8000,  # Twilio expects 8kHz
                    None,
                )[0]
            else:
                pcm_8k = pcm_data

            # Convert PCM to μ-law
            ulaw_data = audioop.lin2ulaw(pcm_8k, 2)

            # Encode as base64
            b64_audio = base64.b64encode(ulaw_data)

            return b64_audio

        except Exception as e:
            logger.error(f"Failed to convert audio to telephony format: {e}")
            raise ValueError(f"Audio conversion failed: {e}") from e

    async def end_call(self, call_id: str) -> None:
        """End an active Twilio call.

        Args:
            call_id: Twilio call SID
        """
        url = f"{self._api_base_url}/2010-04-01/Accounts/{self._account_sid}/Calls/{call_id}.json"

        try:
            response = await self._http_client.post(
                url,
                data={"Status": "completed"},
                auth=(self._account_sid, self._auth_token),
            )
            response.raise_for_status()
            logger.info(f"Ended Twilio call {call_id}")
        except Exception as e:
            logger.error(f"Failed to end call {call_id}: {e}")
            raise

    async def close(self) -> None:
        """Close the HTTP client."""
        await self._http_client.aclose()


def create_twilio_adapter(account_sid: str, auth_token: str) -> TwilioAdapter:
    """Factory function to create Twilio adapter.

    Args:
        account_sid: Twilio account SID
        auth_token: Twilio auth token

    Returns:
        TwilioAdapter: Configured adapter instance
    """
    return TwilioAdapter(account_sid=account_sid, auth_token=auth_token)
