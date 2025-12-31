"""
Webhook Security Module - Ed25519/HMAC Signature Verification
Provides secure webhook validation for II-Agent and Google Calendar callbacks.
"""

import hmac
import hashlib
import base64
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from fastapi import HTTPException, status, Header, Request
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization
from cryptography.exceptions import InvalidSignature
import json

from app.core.config import settings

logger = logging.getLogger(__name__)


class WebhookSignatureVerifier:
    """
    Webhook signature verification for II-Agent callbacks.

    Supports both Ed25519 (asymmetric) and HMAC-SHA256 (symmetric) signatures.
    """

    def __init__(self):
        """Initialize with public key for Ed25519 verification."""
        self.public_key = None
        # Try to load Ed25519 public key if available
        try:
            from pathlib import Path
            public_key_path = Path("keys/webhook_public.pem")
            if public_key_path.exists():
                with open(public_key_path, "rb") as f:
                    self.public_key = serialization.load_pem_public_key(f.read())
                logger.info("Ed25519 public key loaded successfully for webhook verification")
            else:
                logger.warning(f"Ed25519 public key not found at {public_key_path}, falling back to HMAC verification")
        except Exception as e:
            logger.error(f"Failed to load Ed25519 public key: {e}. Falling back to HMAC verification")

    async def verify_ii_agent_webhook(
        self,
        request: Request,
        x_signature: Optional[str] = Header(None, alias="X-II-Agent-Signature"),
        x_timestamp: Optional[str] = Header(None, alias="X-II-Agent-Timestamp"),
        x_signature_type: Optional[str] = Header(None, alias="X-II-Agent-Signature-Type")
    ) -> Dict[str, Any]:
        """
        Verify II-Agent webhook signature.

        Supports two signature types:
        1. Ed25519 (preferred): Asymmetric signature verification
        2. HMAC-SHA256 (fallback): Symmetric HMAC verification

        Headers required:
        - X-II-Agent-Signature: Base64-encoded signature
        - X-II-Agent-Timestamp: Unix timestamp (for replay protection)
        - X-II-Agent-Signature-Type: "ed25519" or "hmac-sha256"

        Args:
            request: FastAPI request object
            x_signature: Signature header
            x_timestamp: Timestamp header
            x_signature_type: Signature type header

        Returns:
            Parsed request body as dict

        Raises:
            HTTPException: If signature verification fails
        """
        # Check for required headers
        if not x_signature or not x_timestamp:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing required signature headers (X-II-Agent-Signature, X-II-Agent-Timestamp)"
            )

        # Get webhook secret from config
        webhook_secret = getattr(settings, "II_AGENT_WEBHOOK_SECRET", None)
        if not webhook_secret and not self.public_key:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Webhook signature verification not configured (missing II_AGENT_WEBHOOK_SECRET or keys)"
            )

        # Verify timestamp (prevent replay attacks)
        try:
            timestamp = int(x_timestamp)
            now = int(datetime.utcnow().timestamp())
            # Allow 5 minute window for clock skew
            if abs(now - timestamp) > 300:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Webhook timestamp too old or in future (replay attack?)"
                )
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid timestamp format"
            )

        # Read request body
        body_bytes = await request.body()

        # Verify signature based on type
        signature_type = x_signature_type or "hmac-sha256"

        if signature_type == "ed25519":
            self._verify_ed25519_signature(body_bytes, x_signature, x_timestamp)
        elif signature_type == "hmac-sha256":
            self._verify_hmac_signature(body_bytes, x_signature, x_timestamp, webhook_secret)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported signature type: {signature_type}"
            )

        # Parse and return body
        try:
            return json.loads(body_bytes.decode('utf-8'))
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid JSON body"
            )

    def _verify_ed25519_signature(
        self,
        body_bytes: bytes,
        signature_b64: str,
        timestamp: str
    ):
        """Verify Ed25519 signature."""
        if not self.public_key:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Ed25519 verification not available (missing public key)"
            )

        try:
            # Decode signature from base64
            signature = base64.b64decode(signature_b64)

            # Message is: timestamp + "." + body
            message = f"{timestamp}.".encode('utf-8') + body_bytes

            # Verify signature
            self.public_key.verify(signature, message)

        except InvalidSignature:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Ed25519 signature"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Ed25519 signature verification failed: {str(e)}"
            )

    def _verify_hmac_signature(
        self,
        body_bytes: bytes,
        signature_hex: str,
        timestamp: str,
        secret: str
    ):
        """Verify HMAC-SHA256 signature."""
        if not secret:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="HMAC verification not available (missing webhook secret)"
            )

        try:
            # Message is: timestamp + "." + body
            message = f"{timestamp}.".encode('utf-8') + body_bytes

            # Compute expected signature
            expected_signature = hmac.new(
                secret.encode('utf-8'),
                message,
                hashlib.sha256
            ).hexdigest()

            # Compare signatures (constant-time comparison to prevent timing attacks)
            if not hmac.compare_digest(expected_signature, signature_hex):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid HMAC signature"
                )

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"HMAC signature verification failed: {str(e)}"
            )


class GoogleCalendarWebhookVerifier:
    """
    Google Calendar webhook verification.

    Verifies webhook notifications from Google Calendar API using:
    1. Channel ID validation
    2. Channel expiration checking
    3. X-Goog-Channel-* header validation
    """

    def verify_google_calendar_webhook(
        self,
        x_goog_resource_id: Optional[str] = Header(None),
        x_goog_resource_state: Optional[str] = Header(None),
        x_goog_channel_id: Optional[str] = Header(None),
        x_goog_channel_expiration: Optional[str] = Header(None),
        x_goog_channel_token: Optional[str] = Header(None),
        x_goog_message_number: Optional[str] = Header(None)
    ) -> Dict[str, Any]:
        """
        Verify Google Calendar webhook notification.

        Google Calendar sends push notifications via webhooks when calendar events change.
        These headers are used to verify the authenticity of the notification.

        Args:
            x_goog_resource_id: Resource ID being watched
            x_goog_resource_state: State of the resource (sync, exists, not_exists)
            x_goog_channel_id: Unique channel ID
            x_goog_channel_expiration: Channel expiration timestamp (RFC3339)
            x_goog_channel_token: Optional verification token
            x_goog_message_number: Incremental message number

        Returns:
            Dict containing validated webhook information

        Raises:
            HTTPException: If verification fails
        """
        # Verify required headers are present
        if not x_goog_channel_id or not x_goog_resource_state:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing required Google Calendar webhook headers"
            )

        # Verify channel hasn't expired
        if x_goog_channel_expiration:
            try:
                from dateutil import parser
                expiration = parser.isoparse(x_goog_channel_expiration)
                if datetime.now(expiration.tzinfo) > expiration:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Calendar webhook channel has expired"
                    )
            except Exception as e:
                # Log but don't fail - expiration check is best-effort
                logger.debug(f"Calendar webhook expiration check skipped: {e}")

        # Verify channel token if configured
        expected_token = getattr(settings, "GOOGLE_CALENDAR_WEBHOOK_TOKEN", None)
        if expected_token and x_goog_channel_token != expected_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid calendar webhook token"
            )

        # Return validated webhook data
        return {
            "channel_id": x_goog_channel_id,
            "resource_id": x_goog_resource_id,
            "resource_state": x_goog_resource_state,
            "expiration": x_goog_channel_expiration,
            "message_number": int(x_goog_message_number) if x_goog_message_number else None
        }


class LinearWebhookVerifier:
    """
    Linear webhook verification.

    Linear signs the request with X-Linear-Signature header.
    The signature is HMAC-SHA256 hash of the raw body using the webhook secret.
    """

    async def verify_linear_webhook(
        self,
        request: Request,
        x_linear_signature: Optional[str] = Header(None, alias="X-Linear-Signature")
    ) -> Dict[str, Any]:
        """
        Verify Linear webhook signature.

        Args:
            request: FastAPI request object
            x_linear_signature: HMAC-SHA256 hex signature from Linear

        Returns:
            Parsed request body as dict

        Raises:
            HTTPException: If signature verification fails
        """
        if not x_linear_signature:
            # For development, allow unauthenticated if secret not set
            if not getattr(settings, "LINEAR_WEBHOOK_SECRET", None):
                body_bytes = await request.body()
                try:
                    return json.loads(body_bytes.decode('utf-8'))
                except json.JSONDecodeError:
                    raise HTTPException(status_code=400, detail="Invalid JSON body")
            
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing X-Linear-Signature header"
            )

        secret = getattr(settings, "LINEAR_WEBHOOK_SECRET", None)
        if not secret:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Linear webhook secret not configured"
            )

        # Read raw body for HMAC verification
        body_bytes = await request.body()

        # Compute HMAC signature
        expected_signature = hmac.new(
            secret.encode('utf-8'),
            body_bytes,
            hashlib.sha256
        ).hexdigest()

        # Compare signatures
        if not hmac.compare_digest(expected_signature, x_linear_signature):
            logger.warning(f"Invalid Linear signature. Expected {expected_signature}, got {x_linear_signature}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Linear signature"
            )

        # Parse body
        try:
            return json.loads(body_bytes.decode('utf-8'))
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid JSON body"
            )


# Global instances
webhook_verifier = WebhookSignatureVerifier()
google_webhook_verifier = GoogleCalendarWebhookVerifier()
linear_webhook_verifier = LinearWebhookVerifier()
