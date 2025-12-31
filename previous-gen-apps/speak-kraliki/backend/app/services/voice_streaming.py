"""
Speak by Kraliki - Real-time Voice Streaming Service

Uses platform-2026/voice-core for phone-based employee surveys.
Supports Telnyx for telephony and Gemini Live 2.5 Flash Native Audio (GA).

Model: models/gemini-2.5-flash-native-audio-preview-12-2025
Audio: 16kHz PCM16 input, 24kHz PCM16 output
"""

import logging
from typing import Callable, Awaitable, Any
from uuid import UUID
from datetime import datetime

from app.core.config import settings
from app.core.database import async_session
from app.models.conversation import Conversation
from app.services.usage_service import usage_service
from sqlalchemy import update, select

logger = logging.getLogger(__name__)

# Try to import voice-core (AI providers)
VOICE_CORE_AVAILABLE = False
TELEPHONY_AVAILABLE = False

try:
    from voice_core import SessionConfig, AudioFormat
    from voice_core.providers import GeminiLiveProvider, create_gemini_provider
    from voice_core.streaming import WebSocketBridge, create_websocket_bridge
    VOICE_CORE_AVAILABLE = True
    logger.info("voice-core loaded successfully")
except ImportError as e:
    logger.warning(f"voice-core not installed: {e}")

# Try to import telephony-core (Telnyx/Twilio adapters)
try:
    from telephony_core.adapters.telnyx import TelnyxAdapter, create_telnyx_adapter
    TELEPHONY_AVAILABLE = True
    logger.info("telephony-core loaded successfully")
except ImportError as e:
    logger.warning(f"telephony-core not installed: {e}")


class VoiceStreamingService:
    """Service for managing real-time voice calls with AI.

    Uses voice-core for:
    - Gemini Live 2.5 Flash Native Audio for AI conversation
    - WebSocket bridge for audio streaming

    Uses telephony-core for:
    - Telnyx telephony (outbound/inbound calls)
    """

    def __init__(self):
        self._provider: Any = None
        self._telephony: Any = None
        self._active_calls: dict[str, dict] = {}  # {call_id: {"bridge": bridge, "conversation_id": UUID, "started_at": datetime}}

    @property
    def is_available(self) -> bool:
        """Check if voice streaming is available (Gemini provider)."""
        return VOICE_CORE_AVAILABLE and bool(settings.gemini_api_key)

    @property
    def is_telephony_available(self) -> bool:
        """Check if telephony (phone calls) is available."""
        return TELEPHONY_AVAILABLE and bool(getattr(settings, 'telnyx_api_key', None))

    async def initialize(self):
        """Initialize voice providers."""
        if not VOICE_CORE_AVAILABLE:
            raise RuntimeError("voice-core package not installed")

        # Initialize Gemini Live 2.5 Flash Native Audio provider
        if settings.gemini_api_key:
            self._provider = create_gemini_provider(
                api_key=settings.gemini_api_key,
                model=settings.gemini_model  # models/gemini-2.5-flash-native-audio-preview-12-2025
            )
            logger.info(f"Gemini Live provider initialized (model={settings.gemini_model})")

        # Initialize Telnyx telephony (if available)
        if TELEPHONY_AVAILABLE and getattr(settings, 'telnyx_api_key', None):
            self._telephony = create_telnyx_adapter(
                api_key=settings.telnyx_api_key,
                public_key=getattr(settings, 'telnyx_public_key', None),
            )
            logger.info("Telnyx telephony adapter initialized")

    async def start_outbound_call(
        self,
        conversation_id: UUID,
        phone_number: str,
        employee_name: str,
        company_name: str,
        system_prompt: str,
        on_transcript: Callable[[str, str], Awaitable[None]] | None = None,
    ) -> dict:
        """Start an outbound voice call for survey.

        Args:
            conversation_id: Conversation UUID
            phone_number: Employee phone number (E.164 format)
            employee_name: Employee first name for personalization
            company_name: Company name for context
            system_prompt: Custom system prompt for the AI
            on_transcript: Callback for transcript updates (role, text)

        Returns:
            dict: Call metadata including call_id
        """
        if not self._telephony:
            raise RuntimeError("Telephony not configured (missing TELNYX_API_KEY)")

        if not self._provider:
            raise RuntimeError("Voice provider not configured (missing GEMINI_API_KEY)")

        # Build system prompt for employee survey
        full_prompt = f"""You are conducting a confidential employee feedback survey for {company_name}.
You are speaking with {employee_name}. Be warm, professional, and empathetic.

Guidelines:
- Keep responses concise (2-3 sentences max)
- Listen actively and ask follow-up questions
- Be sensitive to concerns about workplace issues
- Assure anonymity and confidentiality
- If employee seems uncomfortable, offer to switch to text mode

{system_prompt}"""

        # Configure session with Gemini Live 2.5 Flash Native Audio (December 2025 GA)
        config = SessionConfig(
            model_id=settings.gemini_model,  # models/gemini-2.5-flash-native-audio-preview-12-2025
            audio_format=AudioFormat.PCM16,
            sample_rate=16000,  # Input sample rate
            system_prompt=full_prompt,
            temperature=0.7,
        )

        # Create bridge
        bridge = create_websocket_bridge(
            provider=self._provider,
            telephony=self._telephony,
            on_transcript=on_transcript,
        )

        # Start bridge
        await bridge.start(config)

        # Make outbound call
        call_result = await self._telephony.setup_call({
            "connection_id": getattr(settings, 'telnyx_connection_id', ''),
            "from_number": getattr(settings, 'telnyx_phone_number', ''),
            "to_number": phone_number,
            "webhook_url": f"{settings.api_base_url}/api/speak/telephony/webhook",
        })

        # Track active call
        call_id = call_result.get("call_id")
        if call_id:
            self._active_calls[call_id] = {
                "bridge": bridge,
                "conversation_id": conversation_id,
                "started_at": datetime.utcnow()
            }

        logger.info(f"Started outbound call {call_id} for conversation {conversation_id}")

        return {
            "call_id": call_id,
            "conversation_id": str(conversation_id),
            "status": call_result.get("status"),
        }

    async def handle_incoming_audio(self, call_id: str, audio_data: bytes):
        """Handle incoming audio from telephony.

        Args:
            call_id: Telnyx call control ID
            audio_data: Raw audio bytes from telephony
        """
        call_info = self._active_calls.get(call_id)
        if call_info:
            bridge = call_info["bridge"]
            await bridge.handle_telephony_audio(audio_data)

    async def end_call(self, call_id: str):
        """End an active call.

        Args:
            call_id: Telnyx call control ID
        """
        call_info = self._active_calls.pop(call_id, None)
        if call_info:
            bridge = call_info["bridge"]
            conv_id = call_info["conversation_id"]
            started_at = call_info["started_at"]
            duration = (datetime.utcnow() - started_at).total_seconds()
            
            await bridge.stop()
            logger.info(f"Ended call {call_id} for conversation {conv_id}. Duration: {duration:.2f}s")
            
            # Update database with duration
            async with async_session() as db:
                try:
                    stmt = (
                        update(Conversation)
                        .where(Conversation.id == conv_id)
                        .values(
                            duration_seconds=int(duration),
                            completed_at=datetime.utcnow(),
                            status="completed"
                        )
                    )
                    await db.execute(stmt)
                    await db.commit()
                    logger.info(f"Updated conversation {conv_id} with duration {int(duration)}s")
                    
                    # Record usage
                    # We need company_id for usage record. Get it from conversation.
                    result = await db.execute(select(Conversation.company_id).where(Conversation.id == conv_id))
                    company_id = result.scalar()
                    if company_id:
                        await usage_service.record_usage(
                            db=db,
                            company_id=company_id,
                            quantity=int(duration),
                            service_type="voice_minutes",
                            reference_id=str(conv_id)
                        )
                except Exception as e:
                    logger.error(f"Failed to update conversation {conv_id}: {e}")

        if self._telephony:
            try:
                await self._telephony.end_call(call_id)
            except Exception as e:
                logger.error(f"Failed to end call {call_id}: {e}")

    async def handle_webhook(self, event_type: str, payload: dict) -> dict | None:
        """Handle Telnyx webhook events.

        Args:
            event_type: Webhook event type
            payload: Webhook payload

        Returns:
            Optional response data
        """
        if not self._telephony:
            return None

        return await self._telephony.handle_webhook(event_type, payload)

    async def validate_webhook(self, signature: str, body: bytes, timestamp: str = "") -> bool:
        """Validate Telnyx webhook signature using Ed25519.

        SECURITY: This method fails securely - returns False if validation cannot be performed.

        Args:
            signature: The Ed25519 signature from Telnyx-Signature-Ed25519 header
            body: The raw request body
            timestamp: The Telnyx-Timestamp header for replay attack prevention

        Returns:
            bool: True only if signature is cryptographically valid
        """
        import time

        # Get the public key from settings
        telnyx_public_key = getattr(settings, 'telnyx_public_key', None)

        # SECURITY: Fail securely if no public key configured
        if not telnyx_public_key:
            logger.warning(
                "SECURITY: Telnyx webhook rejected - no public key configured. "
                "Set TELNYX_PUBLIC_KEY environment variable."
            )
            return False

        # SECURITY: Require signature header
        if not signature:
            logger.warning("SECURITY: Telnyx webhook rejected - missing signature header")
            return False

        # Timestamp validation (anti-replay attack)
        if timestamp:
            try:
                webhook_time = int(timestamp)
                current_time = int(time.time())
                time_diff = abs(current_time - webhook_time)

                # Reject if older than 5 minutes (300 seconds)
                if time_diff > 300:
                    logger.warning(
                        f"SECURITY: Telnyx webhook rejected - timestamp too old ({time_diff}s)"
                    )
                    return False
            except (ValueError, TypeError) as e:
                logger.warning(f"SECURITY: Telnyx webhook rejected - invalid timestamp: {e}")
                return False

        try:
            # Import PyNaCl for Ed25519 verification
            try:
                from nacl.signing import VerifyKey
                from nacl.exceptions import BadSignatureError
            except ImportError:
                logger.error(
                    "SECURITY: PyNaCl required for Telnyx webhook validation. "
                    "Install with: pip install pynacl"
                )
                return False

            # Verify Ed25519 signature
            verify_key = VerifyKey(bytes.fromhex(telnyx_public_key))
            signature_bytes = bytes.fromhex(signature)

            try:
                verify_key.verify(body, signature_bytes)
                logger.debug("Telnyx webhook signature validated successfully")
                return True
            except BadSignatureError:
                logger.warning("SECURITY: Telnyx webhook rejected - invalid signature")
                return False

        except Exception as e:
            logger.error(f"SECURITY: Telnyx webhook validation error: {e}")
            return False

    async def shutdown(self):
        """Shutdown all active calls and connections."""
        # End all active calls
        for call_id in list(self._active_calls.keys()):
            await self.end_call(call_id)

        # Close telephony adapter
        if self._telephony:
            await self._telephony.close()

        logger.info("Voice streaming service shutdown complete")


# Singleton instance
voice_streaming_service = VoiceStreamingService()
