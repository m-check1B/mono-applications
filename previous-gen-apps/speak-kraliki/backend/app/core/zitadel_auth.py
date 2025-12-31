"""
Zitadel OIDC Authentication for Speak by Kraliki

Validates JWT tokens from Zitadel identity provider.
Replaces Ed25519Auth for production use with centralized auth.

Environment Variables:
    ZITADEL_ISSUER: Zitadel instance URL (default: https://identity.verduona.dev)
    ZITADEL_CLIENT_ID: OIDC client ID for this app
    AUTH_MODE: 'zitadel' or 'ed25519' (default: ed25519 for backward compatibility)
"""

import os
from typing import Optional
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Try to import from auth-core
try:
    from auth_core.zitadel import (
        ZitadelAuth,
        ZitadelTokenPayload,
        ZitadelTokenError,
        ZitadelTokenExpiredError,
        ZitadelTokenInvalidError,
    )
    from auth_core.fastapi_zitadel import FastAPIZitadelAuth
    ZITADEL_AVAILABLE = True
except ImportError:
    ZITADEL_AVAILABLE = False
    ZitadelAuth = None
    ZitadelTokenPayload = None


def create_auth_exception(detail: str) -> HTTPException:
    """Create standard 401 Unauthorized exception."""
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


class SpeakKralikiZitadelAuth:
    """Zitadel authentication for Speak by Kraliki."""

    def __init__(
        self,
        issuer: Optional[str] = None,
        client_id: Optional[str] = None,
    ):
        if not ZITADEL_AVAILABLE:
            raise ImportError(
                "auth-core package with Zitadel support not installed. "
                "Install with: pip install auth-core[zitadel]"
            )

        self.issuer = issuer or os.getenv(
            "ZITADEL_ISSUER", "https://identity.verduona.dev"
        )
        self.client_id = client_id or os.getenv("ZITADEL_CLIENT_ID")

        self.zitadel = ZitadelAuth(
            issuer=self.issuer,
            audience=self.client_id,
        )

    def verify_token(self, token: str) -> ZitadelTokenPayload:
        """Verify JWT token from Zitadel."""
        try:
            return self.zitadel.verify_token(token)
        except ZitadelTokenExpiredError:
            raise create_auth_exception("Token has expired")
        except ZitadelTokenInvalidError as e:
            raise create_auth_exception(str(e))
        except ZitadelTokenError as e:
            raise create_auth_exception(f"Token verification failed: {e}")


# Global instance
_zitadel_auth: Optional[SpeakKralikiZitadelAuth] = None


def get_zitadel_auth() -> SpeakKralikiZitadelAuth:
    """Get or create Zitadel auth instance."""
    global _zitadel_auth
    if _zitadel_auth is None:
        _zitadel_auth = SpeakKralikiZitadelAuth()
    return _zitadel_auth


_http_bearer = HTTPBearer(auto_error=False)


async def get_current_user_zitadel(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(_http_bearer),
) -> ZitadelTokenPayload:
    """FastAPI dependency for getting current user from Zitadel token."""
    if not credentials:
        raise create_auth_exception("Not authenticated")

    auth = get_zitadel_auth()
    return auth.verify_token(credentials.credentials)


async def get_current_user_optional_zitadel(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(_http_bearer),
) -> Optional[ZitadelTokenPayload]:
    """FastAPI dependency for optional authentication."""
    if not credentials:
        return None

    auth = get_zitadel_auth()
    return auth.verify_token(credentials.credentials)


def is_zitadel_enabled() -> bool:
    """Check if Zitadel auth is enabled."""
    return os.getenv("AUTH_MODE", "ed25519").lower() == "zitadel"


def get_auth_mode() -> str:
    """Get current auth mode."""
    return os.getenv("AUTH_MODE", "ed25519")
