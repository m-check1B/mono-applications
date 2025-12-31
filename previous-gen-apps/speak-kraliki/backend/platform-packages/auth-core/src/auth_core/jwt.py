"""
Stack 2026 Compliant Ed25519 JWT Authentication

Uses asymmetric EdDSA (Ed25519) instead of symmetric HS256:
- Private key signs tokens
- Public key verifies tokens
- Stronger security with shorter keys
- Compatible with microservices (public key can be shared)
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Union
from enum import Enum
from pathlib import Path
import secrets

import jwt
from cryptography.hazmat.primitives.asymmetric import ed25519
from pydantic import BaseModel, Field


class TokenType(str, Enum):
    """JWT token types."""
    ACCESS = "access"
    REFRESH = "refresh"


class TokenError(Exception):
    """Base exception for token errors."""
    pass


class TokenExpiredError(TokenError):
    """Token has expired."""
    pass


class TokenInvalidError(TokenError):
    """Token signature or format is invalid."""
    pass


class TokenTypeMismatchError(TokenError):
    """Token type doesn't match expected type."""
    def __init__(self, expected: str, got: str):
        self.expected = expected
        self.got = got
        super().__init__(f"Expected '{expected}' token, got '{got}'")


class TokenConfig(BaseModel):
    """Configuration for token generation."""
    access_token_expire_minutes: int = Field(default=15, ge=1)
    refresh_token_expire_days: int = Field(default=7, ge=1)


class TokenPayload(BaseModel):
    """Decoded JWT payload structure."""
    sub: str  # Subject (user ID)
    exp: datetime
    iat: datetime
    type: TokenType
    jti: str  # JWT ID for revocation
    # Additional claims
    extra: Dict[str, Any] = Field(default_factory=dict)


class Ed25519Auth:
    """
    Stack 2026 compliant Ed25519 JWT authentication system.

    Usage:
        auth = Ed25519Auth(keys_dir="keys")

        # Create tokens
        access = auth.create_access_token({"sub": "user123"})
        refresh = auth.create_refresh_token({"sub": "user123"})

        # Verify tokens
        payload = auth.verify_token(access, TokenType.ACCESS)
    """

    def __init__(
        self,
        private_key: Optional[ed25519.Ed25519PrivateKey] = None,
        public_key: Optional[ed25519.Ed25519PublicKey] = None,
        keys_dir: Optional[Union[str, Path]] = None,
        config: Optional[TokenConfig] = None,
    ):
        """
        Initialize Ed25519 authentication.

        Args:
            private_key: Ed25519 private key (for signing)
            public_key: Ed25519 public key (for verification)
            keys_dir: Directory containing jwt_private.pem and jwt_public.pem
            config: Token configuration (expiration times)

        Provide either (private_key, public_key) or keys_dir.
        """
        self.config = config or TokenConfig()

        if private_key and public_key:
            self._private_key = private_key
            self._public_key = public_key
        elif keys_dir:
            from auth_core.keys import load_private_key, load_public_key
            keys_path = Path(keys_dir)
            self._private_key = load_private_key(keys_path / "jwt_private.pem")
            self._public_key = load_public_key(keys_path / "jwt_public.pem")
        else:
            raise ValueError("Provide either (private_key, public_key) or keys_dir")

    @property
    def private_key(self) -> ed25519.Ed25519PrivateKey:
        """Get the private key for signing."""
        return self._private_key

    @property
    def public_key(self) -> ed25519.Ed25519PublicKey:
        """Get the public key for verification."""
        return self._public_key

    def create_access_token(
        self,
        data: Dict[str, Any],
        expires_delta: Optional[timedelta] = None,
    ) -> str:
        """
        Create short-lived access token.

        Args:
            data: Payload data (must include 'sub' for user ID)
            expires_delta: Optional custom expiration time

        Returns:
            Encoded JWT string
        """
        return self._create_token(
            data=data,
            token_type=TokenType.ACCESS,
            expires_delta=expires_delta or timedelta(
                minutes=self.config.access_token_expire_minutes
            ),
        )

    def create_refresh_token(
        self,
        data: Dict[str, Any],
        expires_delta: Optional[timedelta] = None,
    ) -> str:
        """
        Create long-lived refresh token.

        Args:
            data: Payload data (must include 'sub' for user ID)
            expires_delta: Optional custom expiration time

        Returns:
            Encoded JWT string
        """
        return self._create_token(
            data=data,
            token_type=TokenType.REFRESH,
            expires_delta=expires_delta or timedelta(
                days=self.config.refresh_token_expire_days
            ),
        )

    def _create_token(
        self,
        data: Dict[str, Any],
        token_type: TokenType,
        expires_delta: timedelta,
    ) -> str:
        """Internal token creation."""
        now = datetime.utcnow()
        expire = now + expires_delta

        to_encode = {
            **data,
            "exp": expire,
            "iat": now,
            "type": token_type.value,
            "jti": secrets.token_urlsafe(8),
        }

        return jwt.encode(
            to_encode,
            self._private_key,
            algorithm="EdDSA",
        )

    def verify_token(
        self,
        token: str,
        expected_type: TokenType = TokenType.ACCESS,
    ) -> TokenPayload:
        """
        Verify JWT signature and return payload.

        Args:
            token: JWT token string
            expected_type: Expected token type

        Returns:
            Decoded TokenPayload

        Raises:
            TokenExpiredError: If token has expired
            TokenInvalidError: If token is invalid
            TokenTypeMismatchError: If token type doesn't match
        """
        try:
            payload = jwt.decode(
                token,
                self._public_key,
                algorithms=["EdDSA"],
            )

            # Verify token type
            token_type = payload.get("type")
            if token_type != expected_type.value:
                raise TokenTypeMismatchError(expected_type.value, token_type)

            # Extract standard claims
            return TokenPayload(
                sub=payload["sub"],
                exp=datetime.fromtimestamp(payload["exp"]),
                iat=datetime.fromtimestamp(payload["iat"]),
                type=TokenType(payload["type"]),
                jti=payload["jti"],
                extra={
                    k: v for k, v in payload.items()
                    if k not in ("sub", "exp", "iat", "type", "jti")
                },
            )

        except jwt.ExpiredSignatureError:
            raise TokenExpiredError("Token has expired")
        except jwt.InvalidTokenError as e:
            raise TokenInvalidError(f"Invalid token: {e}")

    def decode_without_verification(self, token: str) -> Dict[str, Any]:
        """
        Decode token without verifying signature.

        WARNING: Only use for non-security-critical operations like
        extracting user ID for blacklist checks before full verification.

        Args:
            token: JWT token string

        Returns:
            Decoded payload (unverified)
        """
        return jwt.decode(
            token,
            options={"verify_signature": False},
        )

    def get_token_jti(self, token: str) -> Optional[str]:
        """Extract JTI (token ID) from token without verification."""
        try:
            payload = self.decode_without_verification(token)
            return payload.get("jti")
        except Exception:
            return None

    def get_token_exp(self, token: str) -> Optional[int]:
        """Extract expiration timestamp from token without verification."""
        try:
            payload = self.decode_without_verification(token)
            return payload.get("exp")
        except Exception:
            return None
