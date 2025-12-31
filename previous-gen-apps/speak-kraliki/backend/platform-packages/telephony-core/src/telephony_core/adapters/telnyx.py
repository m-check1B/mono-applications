"""Telnyx telephony adapter.

Telnyx is the recommended telephony provider for platform-2026:
- 47% cheaper than Twilio
- Native PCM16 support (no transcoding needed)
- WebSocket streaming built-in
- Ed25519 webhook validation
"""

import base64
import logging
from typing import Any

import httpx

from telephony_core.base import (
    AudioChunk,
    AudioFormat,
    BaseTelephonyAdapter,
    CallDirection,
    CallInfo,
    CallState,
    TelephonyCapabilities,
)

logger = logging.getLogger(__name__)


class TelnyxAdapter(BaseTelephonyAdapter):
    """Telnyx telephony adapter.

    Handles Telnyx Call Control API, native PCM audio streaming,
    and webhook validation using Ed25519 signatures.
    """

    def __init__(
        self,
        api_key: str,
        public_key: str | None = None,
        api_base_url: str = "https://api.telnyx.com/v2",
    ):
        """Initialize Telnyx adapter.

        Args:
            api_key: Telnyx API key
            public_key: Ed25519 public key for webhook validation
            api_base_url: Telnyx API base URL
        """
        super().__init__(api_key)
        self._public_key = public_key
        self._api_base_url = api_base_url
        self._http_client = httpx.AsyncClient()

    @property
    def capabilities(self) -> TelephonyCapabilities:
        """Telnyx capabilities."""
        return TelephonyCapabilities(
            supports_inbound=True,
            supports_outbound=True,
            supports_streaming=True,
            supports_sms=True,
            audio_formats=[AudioFormat.PCM16],
            native_sample_rate=8000,
        )

    async def setup_call(self, call_params: dict[str, Any]) -> CallInfo:
        """Set up outbound Telnyx call.

        Args:
            call_params: Must include:
                - connection_id: Telnyx connection ID
                - from_number: Your Telnyx number
                - to_number: Destination number
                - stream_url: WebSocket URL for audio
        """
        url = f"{self._api_base_url}/calls"
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

        data = {
            "connection_id": call_params["connection_id"],
            "to": call_params["to_number"],
            "from": call_params["from_number"],
            "stream_url": call_params.get("stream_url"),
            "stream_track": "both_tracks",
        }

        if "webhook_url" in call_params:
            data["webhook_url"] = call_params["webhook_url"]

        response = await self._http_client.post(url, headers=headers, json=data)
        response.raise_for_status()

        result = response.json()
        call_data = result.get("data", {})

        return CallInfo(
            call_id=call_data.get("call_control_id", ""),
            from_number=call_data.get("from", call_params["from_number"]),
            to_number=call_data.get("to", call_params["to_number"]),
            direction=CallDirection.OUTBOUND,
            state=CallState(call_data.get("state", "initiated")),
        )

    async def answer_call(self, call_id: str, stream_url: str) -> dict[str, Any]:
        """Answer inbound call and start streaming."""
        url = f"{self._api_base_url}/calls/{call_id}/actions/answer"
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

        data = {
            "stream_url": stream_url,
            "stream_track": "both_tracks",
        }

        response = await self._http_client.post(url, headers=headers, json=data)
        response.raise_for_status()

        return response.json()

    async def end_call(self, call_id: str) -> None:
        """End active call."""
        url = f"{self._api_base_url}/calls/{call_id}/actions/hangup"
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

        try:
            response = await self._http_client.post(url, headers=headers, json={})
            response.raise_for_status()
            logger.info(f"Ended Telnyx call {call_id}")
        except Exception as e:
            logger.error(f"Failed to end call {call_id}: {e}")
            raise

    async def handle_webhook(
        self, event_type: str, payload: dict[str, Any]
    ) -> dict[str, Any] | None:
        """Handle Telnyx webhook events."""
        data = payload.get("data", {})
        event = data.get("event_type", event_type)
        event_payload = data.get("payload", {})

        handlers = {
            "call.initiated": self._handle_call_initiated,
            "call.answered": self._handle_call_answered,
            "call.hangup": self._handle_call_hangup,
        }

        handler = handlers.get(event)
        if handler:
            return await handler(event_payload)

        logger.debug(f"Unhandled Telnyx event: {event}")
        return None

    async def _handle_call_initiated(self, payload: dict[str, Any]) -> dict[str, Any]:
        return {
            "call_id": payload.get("call_control_id"),
            "from": payload.get("from"),
            "to": payload.get("to"),
            "direction": payload.get("direction"),
            "state": "initiated",
        }

    async def _handle_call_answered(self, payload: dict[str, Any]) -> dict[str, Any]:
        return {
            "call_id": payload.get("call_control_id"),
            "state": "answered",
        }

    async def _handle_call_hangup(self, payload: dict[str, Any]) -> dict[str, Any]:
        return {
            "call_id": payload.get("call_control_id"),
            "hangup_cause": payload.get("hangup_cause"),
            "state": "ended",
        }

    async def validate_webhook(self, signature: str, payload: bytes | str) -> bool:
        """Validate webhook using Ed25519 signature."""
        if not self._public_key:
            logger.warning("No public key configured, skipping validation")
            return True

        try:
            from nacl.signing import VerifyKey
            from nacl.exceptions import BadSignatureError
        except ImportError:
            logger.error("pynacl required for webhook validation")
            return False

        try:
            payload_bytes = payload if isinstance(payload, bytes) else payload.encode()
            verify_key = VerifyKey(bytes.fromhex(self._public_key))
            verify_key.verify(payload_bytes, bytes.fromhex(signature))
            return True
        except BadSignatureError:
            logger.warning("Invalid webhook signature")
            return False
        except Exception as e:
            logger.error(f"Webhook validation error: {e}")
            return False

    def generate_stream_response(self, stream_url: str) -> str:
        """Generate TeXML for streaming (rarely used - REST API preferred)."""
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Connect>
        <Stream url="{stream_url}" />
    </Connect>
</Response>"""

    async def convert_audio_from_telephony(self, audio_data: bytes) -> AudioChunk:
        """Convert Telnyx audio to PCM16 chunk.

        Telnyx uses native PCM16, so minimal conversion needed.
        """
        # Check if base64 encoded
        try:
            decoded = base64.b64decode(audio_data)
            audio_bytes = decoded
        except Exception:
            audio_bytes = audio_data

        return AudioChunk(
            data=audio_bytes,
            format=AudioFormat.PCM16,
            sample_rate=8000,
        )

    async def convert_audio_to_telephony(self, audio: AudioChunk) -> bytes:
        """Convert PCM16 audio to Telnyx format.

        Resamples to 8kHz if needed.
        """
        if audio.format != AudioFormat.PCM16:
            raise ValueError(f"Expected PCM16, got {audio.format}")

        if audio.sample_rate != 8000:
            import audioop
            resampled = audioop.ratecv(
                audio.data, 2, 1,
                audio.sample_rate, 8000, None
            )[0]
            return resampled

        return audio.data

    async def close(self) -> None:
        """Close HTTP client."""
        await self._http_client.aclose()


def create_telnyx_adapter(
    api_key: str,
    public_key: str | None = None,
) -> TelnyxAdapter:
    """Create Telnyx adapter instance."""
    return TelnyxAdapter(api_key=api_key, public_key=public_key)
