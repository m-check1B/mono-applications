"""
Ed25519 JWT Authentication System
Implements secure JWT authentication with Ed25519 signatures
Based on Stack-2026 authentication patterns

Uses auth-core from local voice core packages when available.
"""

import logging
import os
import secrets
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import bcrypt
import jwt
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519

# Try to use auth-core for shared Ed25519 implementation
try:
    from auth_core import (
        Ed25519Auth as BaseEd25519Auth,
    )
    from auth_core import (
        TokenConfig,
        TokenType,
        generate_ed25519_keypair,
        save_keypair,
    )

    AUTH_CORE_AVAILABLE = True
except ImportError:
    AUTH_CORE_AVAILABLE = False

logger = logging.getLogger(__name__)


class Ed25519Auth:
    """Ed25519 JWT authentication manager"""

    def __init__(self, keys_dir: str | None = None):
        """
        Initialize Ed25519 auth with key management

        Args:
            keys_dir: Directory to store/load Ed25519 keys
        """
        keys_dir = keys_dir or os.getenv("JWT_KEYS_DIR", "keys")
        self.keys_dir = Path(keys_dir).expanduser().resolve()
        self.keys_dir.mkdir(parents=True, exist_ok=True)

        self.private_key_path = self.keys_dir / "jwt_private.pem"
        self.public_key_path = self.keys_dir / "jwt_public.pem"

        # Load or generate keys
        if not self.private_key_path.exists() or not self.public_key_path.exists():
            logger.warning("Ed25519 keys not found, generating new key pair...")
            self._generate_keys()

        self._load_keys()
        logger.info("Ed25519 JWT auth initialized successfully")

    def _generate_keys(self):
        """Generate new Ed25519 key pair"""
        # Generate private key
        private_key = ed25519.Ed25519PrivateKey.generate()

        # Save private key
        with open(self.private_key_path, "wb") as f:
            f.write(
                private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption(),
                )
            )

        # Extract and save public key
        public_key = private_key.public_key()
        with open(self.public_key_path, "wb") as f:
            f.write(
                public_key.public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo,
                )
            )

        # Set appropriate permissions (read-only for owner)
        os.chmod(self.private_key_path, 0o600)
        os.chmod(self.public_key_path, 0o644)

        logger.info("Ed25519 key pair generated successfully")

    def _load_keys(self):
        """Load Ed25519 keys from disk"""
        with open(self.private_key_path, "rb") as f:
            self.private_key = serialization.load_pem_private_key(
                f.read(), password=None, backend=default_backend()
            )

        with open(self.public_key_path, "rb") as f:
            self.public_key = serialization.load_pem_public_key(f.read(), backend=default_backend())

    def create_access_token(
        self,
        user_id: str,
        email: str,
        role: str = "user",
        org_id: str | None = None,
        expires_delta: timedelta | None = None,
    ) -> str:
        """
        Create JWT access token with Ed25519 signature

        Args:
            user_id: Unique user identifier
            email: User email
            role: User role (e.g., 'user', 'admin')
            org_id: Optional organization ID
            expires_delta: Token expiration time delta

        Returns:
            Signed JWT token string
        """
        expires = datetime.now(UTC) + (expires_delta or timedelta(hours=24))

        payload = {
            "sub": user_id,
            "email": email,
            "role": role,
            "org_id": org_id,
            "exp": expires,
            "iat": datetime.now(UTC),
            "jti": secrets.token_urlsafe(16),
        }

        token = jwt.encode(payload, self.private_key, algorithm="EdDSA")

        return token

    def verify_token(self, token: str) -> dict[str, Any] | None:
        """
        Verify and decode JWT token

        Args:
            token: JWT token string

        Returns:
            Decoded token payload or None if invalid
        """
        try:
            payload = jwt.decode(token, self.public_key, algorithms=["EdDSA"])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {e}")
            return None

    def hash_password(self, password: str) -> str:
        """
        Hash a password using bcrypt

        Args:
            password: Plain text password

        Returns:
            Hashed password
        """
        # Generate salt and hash password
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
        return hashed.decode("utf-8")

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify a password against its hash

        Args:
            plain_password: Plain text password
            hashed_password: Hashed password to verify against

        Returns:
            True if password matches, False otherwise
        """
        try:
            return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
        except Exception:
            return False

    def create_refresh_token(self, user_id: str) -> str:
        """
        Create a refresh token for token renewal

        Args:
            user_id: User identifier

        Returns:
            Refresh token string
        """
        payload = {
            "sub": user_id,
            "type": "refresh",
            "exp": datetime.now(UTC) + timedelta(days=30),
            "jti": secrets.token_urlsafe(32),
        }

        return jwt.encode(payload, self.private_key, algorithm="EdDSA")

    def rotate_keys(self) -> None:
        """
        Rotate Ed25519 keys (invalidates all existing tokens)
        """
        logger.warning("Rotating Ed25519 keys - all existing tokens will be invalid")
        self._generate_keys()
        self._load_keys()
        logger.info("Key rotation complete")


# Global auth instance
auth_manager = None


def get_auth_manager() -> Ed25519Auth:
    """Get or create auth manager instance"""
    global auth_manager
    if auth_manager is None:
        auth_manager = Ed25519Auth()
    return auth_manager
