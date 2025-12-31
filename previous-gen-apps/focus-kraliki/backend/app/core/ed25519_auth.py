"""
Stack 2026 Compliant Ed25519 JWT Authentication
Migration from HS256 to asymmetric Ed25519 (EdDSA)

This module now uses auth-core for the core implementation,
with FastAPI-specific extensions for HTTPException handling.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from pathlib import Path
import secrets
import jwt
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization
from fastapi import HTTPException, status
from app.core.config import settings

# Try to use auth-core, fall back to local implementation
try:
    from auth_core import (
        Ed25519Auth as BaseEd25519Auth,
        TokenConfig,
        TokenType,
        TokenPayload,
        TokenError,
        TokenExpiredError,
        TokenInvalidError,
        TokenTypeMismatchError,
    )
    AUTH_CORE_AVAILABLE = True
except ImportError:
    AUTH_CORE_AVAILABLE = False
    BaseEd25519Auth = None


class Ed25519Auth:
    """
    Stack 2026 compliant Ed25519 JWT authentication system.

    Uses asymmetric cryptography (EdDSA) instead of symmetric HS256:
    - Private key signs tokens
    - Public key verifies tokens
    - Stronger security with shorter keys
    - Compatible with microservices (public key can be shared)
    """

    def __init__(self, keys_dir: str = "keys"):
        """
        Initialize Ed25519 authentication with key pair.

        Args:
            keys_dir: Directory containing jwt_private.pem and jwt_public.pem
        """
        self.keys_dir = Path(keys_dir)
        self.private_key = self._load_private_key()
        self.public_key = self._load_public_key()

        # Token configuration from settings
        self.access_token_expire = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        self.refresh_token_expire = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    def _load_private_key(self) -> ed25519.Ed25519PrivateKey:
        """Load Ed25519 private key from PEM file."""
        private_key_path = self.keys_dir / "jwt_private.pem"

        if not private_key_path.exists():
            raise FileNotFoundError(
                f"Private key not found at {private_key_path}. "
                "Run scripts/generate-ed25519-keys.sh to generate keys."
            )

        with open(private_key_path, "rb") as f:
            return serialization.load_pem_private_key(
                f.read(),
                password=None  # Keys are protected by file system permissions
            )

    def _load_public_key(self) -> ed25519.Ed25519PublicKey:
        """Load Ed25519 public key from PEM file."""
        public_key_path = self.keys_dir / "jwt_public.pem"

        if not public_key_path.exists():
            raise FileNotFoundError(
                f"Public key not found at {public_key_path}. "
                "Run scripts/generate-ed25519-keys.sh to generate keys."
            )

        with open(public_key_path, "rb") as f:
            return serialization.load_pem_public_key(f.read())

    def create_access_token(
        self,
        data: Dict[str, Any],
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Create short-lived access token (15 minutes default).

        Args:
            data: Payload data (must include 'sub' for user ID)
            expires_delta: Optional custom expiration time

        Returns:
            Encoded JWT string
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + (expires_delta or self.access_token_expire)

        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access",
            "alg": "EdDSA",
            "jti": secrets.token_urlsafe(8)
        })

        return jwt.encode(
            to_encode,
            self.private_key,
            algorithm="EdDSA"
        )

    def create_refresh_token(
        self,
        data: Dict[str, Any],
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Create long-lived refresh token (7 days default).

        Args:
            data: Payload data (must include 'sub' for user ID)
            expires_delta: Optional custom expiration time

        Returns:
            Encoded JWT string
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + (expires_delta or self.refresh_token_expire)

        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "refresh",
            "alg": "EdDSA",
            "jti": secrets.token_urlsafe(8)
        })

        return jwt.encode(
            to_encode,
            self.private_key,
            algorithm="EdDSA"
        )

    def verify_token(
        self,
        token: str,
        expected_type: str = "access"
    ) -> Dict[str, Any]:
        """
        Verify JWT signature and return payload.

        Args:
            token: JWT token string
            expected_type: Expected token type ('access' or 'refresh')

        Returns:
            Decoded payload dictionary

        Raises:
            HTTPException: If token is invalid, expired, or wrong type
        """
        try:
            # Verify signature and decode
            payload = jwt.decode(
                token,
                self.public_key,
                algorithms=["EdDSA"]
            )

            # Verify token type
            token_type = payload.get("type")
            if token_type != expected_type:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Invalid token type. Expected '{expected_type}', got '{token_type}'",
                    headers={"WWW-Authenticate": "Bearer"}
                )

            return payload

        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"}
            )
        except jwt.InvalidTokenError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token: {str(e)}",
                headers={"WWW-Authenticate": "Bearer"}
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Token verification failed: {str(e)}",
                headers={"WWW-Authenticate": "Bearer"}
            )

    def decode_without_verification(self, token: str) -> Dict[str, Any]:
        """
        Decode token without verifying signature (for revocation checks).

        WARNING: Only use for non-security-critical operations like
        extracting user ID for blacklist checks.

        Args:
            token: JWT token string

        Returns:
            Decoded payload (unverified)
        """
        return jwt.decode(
            token,
            options={"verify_signature": False}
        )


# Global instance (initialized on import)
ed25519_auth = Ed25519Auth()
