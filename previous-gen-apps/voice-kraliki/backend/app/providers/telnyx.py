"""Telnyx telephony adapter implementation.

This module provides the TelephonyAdapter implementation for Telnyx,
handling Call Control API, audio streaming with native PCM support,
and webhook validation using Ed25519.
"""

import base64
import logging
from typing import Any

import httpx

from app.providers.base import (
    AudioChunk,
    AudioFormat,
    ProviderCapabilities,
)

logger = logging.getLogger(__name__)


class TelnyxAdapter:
    """Telnyx telephony service adapter.

    Handles Telnyx Call Control API, native PCM audio streaming,
    and webhook validation using Ed25519 signatures.
    """

    def __init__(
        self,
        api_key: str,
        api_base_url: str = "https://api.telnyx.com/v2",
        public_key: str | None = None,
    ):
        """Initialize Telnyx adapter.

        Args:
            api_key: Telnyx API key
            api_base_url: Telnyx API base URL
            public_key: Ed25519 public key for webhook validation (optional)
        """
        self._api_key = api_key
        self._api_base_url = api_base_url
        self._public_key = public_key
        self._http_client = httpx.AsyncClient()

    @property
    def capabilities(self) -> ProviderCapabilities:
        """Telnyx adapter capabilities."""
        return ProviderCapabilities(
            supports_realtime=True,
            supports_text=False,  # Telephony only
            supports_audio=True,
            supports_multimodal=False,
            supports_function_calling=False,
            supports_streaming=True,
            audio_formats=[AudioFormat.PCM16],  # Native PCM support
            max_session_duration=None,  # No hard limit
            cost_tier="standard",
        )

    async def setup_call(self, call_params: dict[str, Any]) -> dict[str, Any]:
        """Set up a new outbound Telnyx call.

        Args:
            call_params: Call parameters including:
                - connection_id: Telnyx connection ID
                - from_number: Telnyx phone number
                - to_number: Destination phone number
                - stream_url: WebSocket URL for audio streaming
                - webhook_url: Optional webhook URL

        Returns:
            dict: Call metadata (call_control_id, status, etc.)

        Raises:
            httpx.HTTPError: If API call fails
        """
        url = f"{self._api_base_url}/calls"
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

        # Build call request
        data = {
            "connection_id": call_params["connection_id"],
            "to": call_params["to_number"],
            "from": call_params["from_number"],
            "stream_url": call_params.get("stream_url"),
            "stream_track": "both_tracks",  # inbound and outbound
        }

        if "webhook_url" in call_params:
            data["webhook_url"] = call_params["webhook_url"]

        # Make API call
        response = await self._http_client.post(url, headers=headers, json=data)
        response.raise_for_status()

        result = response.json()
        call_data = result.get("data", {})

        return {
            "call_id": call_data.get("call_control_id"),
            "status": call_data.get("state"),
            "from": call_data.get("from"),
            "to": call_data.get("to"),
            "direction": call_data.get("direction"),
        }

    async def answer_call(self, call_control_id: str, stream_url: str) -> dict[str, Any]:
        """Answer an incoming Telnyx call and start streaming.

        Args:
            call_control_id: Telnyx call control ID
            stream_url: WebSocket URL for audio streaming

        Returns:
            dict: Answer response data
        """
        url = f"{self._api_base_url}/calls/{call_control_id}/actions/answer"
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

    async def handle_webhook(
        self, event_type: str, payload: dict[str, Any]
    ) -> dict[str, Any] | None:
        """Handle incoming webhook from Telnyx.

        Args:
            event_type: Type of webhook event
            payload: Webhook payload

        Returns:
            Optional response data for the webhook
        """
        data = payload.get("data", {})
        event_type_full = data.get("event_type", event_type)

        if event_type_full == "call.initiated":
            return await self._handle_call_initiated(data)
        elif event_type_full == "call.answered":
            return await self._handle_call_answered(data)
        elif event_type_full == "call.hangup":
            return await self._handle_call_hangup(data)
        else:
            logger.warning(f"Unknown Telnyx webhook event: {event_type_full}")
            return None

    async def _handle_call_initiated(self, data: dict[str, Any]) -> dict[str, Any]:
        """Handle call initiated webhook.

        Args:
            data: Event data

        Returns:
            dict: Call information
        """
        payload = data.get("payload", {})
        return {
            "call_control_id": payload.get("call_control_id"),
            "call_session_id": payload.get("call_session_id"),
            "from": payload.get("from"),
            "to": payload.get("to"),
            "state": payload.get("state"),
        }

    async def _handle_call_answered(self, data: dict[str, Any]) -> dict[str, Any]:
        """Handle call answered webhook.

        Args:
            data: Event data

        Returns:
            dict: Call information
        """
        payload = data.get("payload", {})
        return {
            "call_control_id": payload.get("call_control_id"),
            "state": payload.get("state"),
        }

    async def _handle_call_hangup(self, data: dict[str, Any]) -> dict[str, Any]:
        """Handle call hangup webhook.

        Args:
            data: Event data

        Returns:
            dict: Hangup information
        """
        payload = data.get("payload", {})
        return {
            "call_control_id": payload.get("call_control_id"),
            "hangup_cause": payload.get("hangup_cause"),
            "hangup_source": payload.get("hangup_source"),
        }

    async def validate_webhook(
        self, signature: str, url: str, payload: dict[str, Any] | str
    ) -> bool:
        """Validate Telnyx webhook signature using Ed25519.

        Args:
            signature: Telnyx-Signature-Ed25519 header value
            url: Webhook URL (not used for Telnyx, kept for interface compatibility)
            payload: Request payload as JSON string

        Returns:
            bool: True if signature is valid
        """
        if not self._public_key:
            logger.warning("Telnyx public key not configured, skipping validation")
            return True  # Allow in dev mode

        try:
            # Try to import nacl for Ed25519 verification
            try:
                from nacl.exceptions import BadSignatureError
                from nacl.signing import VerifyKey
            except ImportError:
                logger.error(
                    "PyNaCl required for Telnyx webhook validation. "
                    "Install with: pip install pynacl"
                )
                return False

            # Convert payload to bytes if needed
            if isinstance(payload, dict):
                import json
                payload_bytes = json.dumps(payload).encode("utf-8")
            else:
                payload_bytes = payload.encode("utf-8")

            # Verify signature
            verify_key = VerifyKey(bytes.fromhex(self._public_key))
            signature_bytes = bytes.fromhex(signature)

            try:
                verify_key.verify(payload_bytes, signature_bytes)
                return True
            except BadSignatureError:
                logger.warning("Invalid Telnyx webhook signature")
                return False

        except Exception as e:
            logger.error(f"Error validating Telnyx webhook: {e}")
            return False

    async def convert_audio_from_telephony(self, audio_data: bytes) -> AudioChunk:
        """Convert Telnyx audio to unified format.

        Telnyx supports native PCM16, so this is mostly a pass-through
        with metadata wrapping.

        Args:
            audio_data: Raw PCM16 audio data or base64-encoded

        Returns:
            AudioChunk: PCM16 audio chunk
        """
        # Check if data is base64-encoded
        try:
            # Try to decode as base64
            decoded = base64.b64decode(audio_data)
            audio_bytes = decoded
        except Exception:
            # Already raw bytes
            audio_bytes = audio_data

        return AudioChunk(
            data=audio_bytes,
            format=AudioFormat.PCM16,
            sample_rate=8000,  # Telnyx typically uses 8kHz
        )

    async def convert_audio_to_telephony(self, audio: AudioChunk) -> bytes:
        """Convert unified audio format to Telnyx format.

        Telnyx expects raw PCM16 data.

        Args:
            audio: Audio chunk in PCM16 format

        Returns:
            bytes: Raw PCM16 audio data for Telnyx
        """
        if audio.format != AudioFormat.PCM16:
            raise ValueError(f"Telnyx requires PCM16 format, got {audio.format}")

        # Resample if needed (Telnyx typically uses 8kHz)
        if audio.sample_rate != 8000:
            import audioop
            pcm_8k = audioop.ratecv(
                audio.data,
                2,  # sample width
                1,  # channels
                audio.sample_rate,
                8000,
                None,
            )[0]
            return pcm_8k

        return audio.data

    async def end_call(self, call_id: str) -> None:
        """End an active Telnyx call.

        Args:
            call_id: Telnyx call control ID
        """
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
            logger.error(f"Failed to end Telnyx call {call_id}: {e}")
            raise

    async def close(self) -> None:
        """Close the HTTP client."""
        await self._http_client.aclose()


def create_telnyx_adapter(
    api_key: str, public_key: str | None = None
) -> TelnyxAdapter:
    """Factory function to create Telnyx adapter.

    Args:
        api_key: Telnyx API key
        public_key: Ed25519 public key for webhook validation

    Returns:
        TelnyxAdapter: Configured adapter instance
    """
    return TelnyxAdapter(api_key=api_key, public_key=public_key)
