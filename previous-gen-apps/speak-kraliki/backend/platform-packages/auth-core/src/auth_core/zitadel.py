"""
Zitadel OIDC/JWT Integration for Auth Core

Validates JWT tokens issued by Zitadel using JWKS (JSON Web Key Set).
No private keys needed - only fetches public keys from Zitadel.

Usage:
    auth = ZitadelAuth(issuer="https://identity.verduona.dev")
    payload = auth.verify_token(token)
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from functools import lru_cache
import time

import jwt
from jwt import PyJWKClient
from pydantic import BaseModel, ConfigDict, Field


class ZitadelTokenError(Exception):
    """Base exception for Zitadel token errors."""
    pass


class ZitadelTokenExpiredError(ZitadelTokenError):
    """Token has expired."""
    pass


class ZitadelTokenInvalidError(ZitadelTokenError):
    """Token signature or format is invalid."""
    pass


class ZitadelTokenPayload(BaseModel):
    """Decoded Zitadel JWT payload structure."""
    sub: str  # Subject (user ID in Zitadel)
    exp: datetime
    iat: datetime
    iss: str  # Issuer (Zitadel URL)
    aud: List[str]  # Audience (client IDs)

    # Zitadel-specific claims
    azp: Optional[str] = None  # Authorized party (client ID)
    client_id: Optional[str] = None

    # User info claims (if included in token)
    email: Optional[str] = None
    email_verified: Optional[bool] = None
    name: Optional[str] = None
    preferred_username: Optional[str] = None

    # Organization claims
    org_id: Optional[str] = Field(default=None, alias="urn:zitadel:iam:org:id")
    org_name: Optional[str] = Field(default=None, alias="urn:zitadel:iam:org:name")

    # Roles (if RBAC configured)
    roles: Dict[str, Dict[str, str]] = Field(
        default_factory=dict,
        alias="urn:zitadel:iam:org:project:roles"
    )

    # All extra claims
    extra: Dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(populate_by_name=True)


class ZitadelAuth:
    """
    Validates JWT tokens from Zitadel using JWKS.

    Fetches public keys from Zitadel's JWKS endpoint and validates
    token signatures. No private keys needed.

    Usage:
        auth = ZitadelAuth(
            issuer="https://identity.verduona.dev",
            audience="your-client-id"
        )

        # Verify token
        payload = auth.verify_token(token)
        print(f"User: {payload.sub}, Email: {payload.email}")
    """

    # JWKS client cache TTL (5 minutes)
    _jwks_cache_ttl = 300
    _jwks_client_cache: Dict[str, tuple] = {}

    def __init__(
        self,
        issuer: str,
        audience: Optional[str] = None,
        audiences: Optional[List[str]] = None,
        leeway: int = 10,
    ):
        """
        Initialize Zitadel authentication.

        Args:
            issuer: Zitadel instance URL (e.g., https://identity.verduona.dev)
            audience: Expected audience (client ID) - single value
            audiences: Expected audiences (client IDs) - multiple values
            leeway: Seconds of leeway for expiration checks
        """
        self.issuer = issuer.rstrip("/")
        self.leeway = leeway

        # Handle audience(s)
        if audiences:
            self.audiences = audiences
        elif audience:
            self.audiences = [audience]
        else:
            self.audiences = None

        self.jwks_uri = f"{self.issuer}/oauth/v2/keys"

    def _get_jwks_client(self) -> PyJWKClient:
        """Get or create cached JWKS client."""
        cache_key = self.jwks_uri
        now = time.time()

        # Check cache
        if cache_key in self._jwks_client_cache:
            client, created_at = self._jwks_client_cache[cache_key]
            if now - created_at < self._jwks_cache_ttl:
                return client

        # Create new client
        client = PyJWKClient(
            self.jwks_uri,
            cache_keys=True,
            lifespan=self._jwks_cache_ttl,
        )
        self._jwks_client_cache[cache_key] = (client, now)
        return client

    def verify_token(
        self,
        token: str,
        verify_audience: bool = True,
    ) -> ZitadelTokenPayload:
        """
        Verify JWT token from Zitadel.

        Args:
            token: JWT token string (from Authorization header)
            verify_audience: Whether to verify audience claim

        Returns:
            ZitadelTokenPayload with decoded claims

        Raises:
            ZitadelTokenExpiredError: If token has expired
            ZitadelTokenInvalidError: If token is invalid
        """
        try:
            # Get signing key from JWKS
            jwks_client = self._get_jwks_client()
            signing_key = jwks_client.get_signing_key_from_jwt(token)

            # Build decode options
            options = {}
            if not verify_audience or not self.audiences:
                options["verify_aud"] = False

            # Decode and verify
            payload = jwt.decode(
                token,
                signing_key.key,
                algorithms=["RS256", "ES256", "EdDSA"],
                issuer=self.issuer,
                audience=self.audiences if verify_audience else None,
                leeway=self.leeway,
                options=options,
            )

            # Extract standard claims
            standard_claims = {
                "sub", "exp", "iat", "iss", "aud", "azp", "client_id",
                "email", "email_verified", "name", "preferred_username",
                "urn:zitadel:iam:org:id", "urn:zitadel:iam:org:name",
                "urn:zitadel:iam:org:project:roles",
            }

            # Ensure aud is a list
            aud = payload.get("aud", [])
            if isinstance(aud, str):
                aud = [aud]

            return ZitadelTokenPayload(
                sub=payload["sub"],
                exp=datetime.fromtimestamp(payload["exp"]),
                iat=datetime.fromtimestamp(payload["iat"]),
                iss=payload["iss"],
                aud=aud,
                azp=payload.get("azp"),
                client_id=payload.get("client_id"),
                email=payload.get("email"),
                email_verified=payload.get("email_verified"),
                name=payload.get("name"),
                preferred_username=payload.get("preferred_username"),
                org_id=payload.get("urn:zitadel:iam:org:id"),
                org_name=payload.get("urn:zitadel:iam:org:name"),
                roles=payload.get("urn:zitadel:iam:org:project:roles", {}),
                extra={k: v for k, v in payload.items() if k not in standard_claims},
            )

        except jwt.ExpiredSignatureError:
            raise ZitadelTokenExpiredError("Token has expired")
        except jwt.InvalidAudienceError:
            raise ZitadelTokenInvalidError("Invalid audience")
        except jwt.InvalidIssuerError:
            raise ZitadelTokenInvalidError("Invalid issuer")
        except jwt.InvalidTokenError as e:
            raise ZitadelTokenInvalidError(f"Invalid token: {e}")
        except Exception as e:
            raise ZitadelTokenInvalidError(f"Token verification failed: {e}")

    def decode_without_verification(self, token: str) -> Dict[str, Any]:
        """
        Decode token without verifying signature.

        WARNING: Only use for non-security-critical operations.
        """
        return jwt.decode(token, options={"verify_signature": False})

    def get_user_id(self, token: str) -> Optional[str]:
        """Extract user ID (sub) from token without verification."""
        try:
            payload = self.decode_without_verification(token)
            return payload.get("sub")
        except Exception:
            return None


# Factory for common configurations
def create_zitadel_auth(
    issuer: str = "https://identity.verduona.dev",
    client_id: Optional[str] = None,
) -> ZitadelAuth:
    """
    Create ZitadelAuth with common defaults.

    Args:
        issuer: Zitadel issuer URL
        client_id: Optional client ID for audience validation

    Returns:
        Configured ZitadelAuth instance
    """
    return ZitadelAuth(issuer=issuer, audience=client_id)
