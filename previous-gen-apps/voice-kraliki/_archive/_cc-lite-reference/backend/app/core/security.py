"""
Ed25519 JWT Security Module - Stack 2026 Compliant
Implements asymmetric JWT authentication using Ed25519 signatures
"""

import os
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)
from cryptography.hazmat.primitives import serialization
from passlib.context import CryptContext

from app.core.config import settings
try:
    # Optional shared auth package
    from auth_core import Ed25519JWT  # type: ignore
except Exception:
    Ed25519JWT = None  # type: ignore
from app.core.logger import get_logger

logger = get_logger(__name__)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Ed25519JWTManager:
    """
    Ed25519 JWT Token Manager

    Implements Stack 2026 standard:
    - EdDSA algorithm (Ed25519)
    - 15-minute access tokens
    - 7-day refresh tokens with rotation
    - Secure key management
    """

    def __init__(self):
        self.private_key: Optional[Ed25519PrivateKey] = None
        self.public_key: Optional[Ed25519PublicKey] = None
        self._shared = None
        self._load_or_generate_keys()

        # Enable shared auth if configured
        use_shared = settings.USE_SHARED_AUTH if hasattr(settings, 'USE_SHARED_AUTH') else False
        if use_shared and Ed25519JWT is not None:
            keys_dir = Path(__file__).parent.parent.parent / "keys"
            private_key_path = str(keys_dir / "jwt_private.pem")
            public_key_path = str(keys_dir / "jwt_public.pem")
            try:
                self._shared = Ed25519JWT(private_key_path=private_key_path, public_key_path=public_key_path)
            except Exception:
                self._shared = None

    def _load_or_generate_keys(self):
        """Load existing Ed25519 keys or generate new ones"""
        keys_dir = Path(__file__).parent.parent.parent / "keys"
        private_key_path = keys_dir / "jwt_private.pem"
        public_key_path = keys_dir / "jwt_public.pem"

        # Create keys directory if it doesn't exist
        keys_dir.mkdir(parents=True, exist_ok=True)

        # Check for existing keys
        if private_key_path.exists() and public_key_path.exists():
            logger.info("Loading existing Ed25519 keys...")
            self._load_keys(private_key_path, public_key_path)
        else:
            logger.warning("Ed25519 keys not found. Generating new keypair...")
            self._generate_and_save_keys(private_key_path, public_key_path)

    def _load_keys(self, private_path: Path, public_path: Path):
        """Load Ed25519 keys from PEM files"""
        try:
            # Load private key
            with open(private_path, "rb") as f:
                self.private_key = serialization.load_pem_private_key(
                    f.read(),
                    password=None,
                )

            # Load public key
            with open(public_path, "rb") as f:
                self.public_key = serialization.load_pem_public_key(f.read())

            logger.info("✅ Ed25519 keys loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load Ed25519 keys: {e}")
            raise

    def _generate_and_save_keys(self, private_path: Path, public_path: Path):
        """Generate new Ed25519 keypair and save to files"""
        try:
            # Generate keypair
            self.private_key = Ed25519PrivateKey.generate()
            self.public_key = self.private_key.public_key()

            # Serialize private key
            private_pem = self.private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption(),
            )

            # Serialize public key
            public_pem = self.public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo,
            )

            # Save keys
            with open(private_path, "wb") as f:
                f.write(private_pem)
                # Set restrictive permissions (owner read/write only)
                os.chmod(private_path, 0o600)

            with open(public_path, "wb") as f:
                f.write(public_pem)

            logger.info("✅ New Ed25519 keypair generated and saved")
            logger.warning("⚠️  SECURITY: Back up these keys securely!")
            logger.warning(f"    Private: {private_path}")
            logger.warning(f"    Public:  {public_path}")

        except Exception as e:
            logger.error(f"Failed to generate Ed25519 keys: {e}")
            raise

    def create_access_token(
        self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Create Ed25519-signed JWT access token

        Args:
            data: Payload data (sub, email, role, etc.)
            expires_delta: Optional custom expiration

        Returns:
            Signed JWT token string
        """
        to_encode = data.copy()

        # Set expiration
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )

        # Add standard claims
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access",
        })

        # Optional: use shared auth_core if available
        if self._shared is not None:
            subject = str(to_encode.get("sub")) if to_encode.get("sub") else "user"
            claims = {k: v for k, v in to_encode.items() if k not in {"sub", "exp", "iat"}}
            minutes = int((expire - datetime.utcnow()).total_seconds() // 60)
            return self._shared.create_access_token(subject=subject, claims=claims, minutes=max(minutes, 1))

        # Sign with local Ed25519 private key
        token = jwt.encode(to_encode, self.private_key, algorithm="EdDSA")
        return token

    def create_refresh_token(self, data: Dict[str, Any]) -> str:
        """
        Create Ed25519-signed JWT refresh token

        Args:
            data: Payload data (sub, email, etc.)

        Returns:
            Signed JWT refresh token
        """
        to_encode = data.copy()

        # Set 7-day expiration
        expire = datetime.utcnow() + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )

        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "refresh",
        })

        # Optional: shared auth_core
        if self._shared is not None:
            subject = str(to_encode.get("sub")) if to_encode.get("sub") else "user"
            claims = {k: v for k, v in to_encode.items() if k not in {"sub", "exp", "iat"}}
            return self._shared.create_refresh_token(subject=subject, claims=claims, days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

        # Local signing
        token = jwt.encode(to_encode, self.private_key, algorithm="EdDSA")
        return token

    def verify_token(self, token: str) -> Dict[str, Any]:
        """
        Verify and decode Ed25519-signed JWT token

        Args:
            token: JWT token string

        Returns:
            Decoded payload

        Raises:
            jwt.InvalidTokenError: If token is invalid or expired
        """
        try:
            if self._shared is not None:
                return self._shared.verify(token, expected_type=None)
            payload = jwt.decode(token, self.public_key, algorithms=["EdDSA"]) 
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token expired")
            raise ValueError("Token has expired")
        except jwt.InvalidTokenError as e:
            logger.error(f"Invalid token: {e}")
            raise ValueError("Invalid token")


# Global JWT manager instance
jwt_manager = Ed25519JWTManager()


# Password utilities
def hash_password(password: str) -> str:
    """Hash password using bcrypt (cost factor 12)"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against bcrypt hash"""
    return pwd_context.verify(plain_password, hashed_password)


# FastAPI Integration
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security)
) -> Dict[str, Any]:
    """
    FastAPI dependency to get current user from JWT

    Usage:
        @router.get("/protected")
        async def protected_route(user: dict = Depends(get_current_user)):
            return {"user": user}
    """
    token = credentials.credentials
    payload = jwt_manager.verify_token(token)
    return payload
