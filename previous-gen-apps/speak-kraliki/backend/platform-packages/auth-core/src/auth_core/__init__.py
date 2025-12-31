"""
Auth Core - Stack 2026 JWT Authentication

Provides:
- Ed25519 asymmetric JWT tokens (EdDSA algorithm) - legacy/custom auth
- Zitadel JWKS-based JWT validation - recommended for new apps
- Redis-based token revocation/blacklist
- Framework-agnostic core with FastAPI integration
"""

from auth_core.jwt import (
    Ed25519Auth,
    TokenConfig,
    TokenPayload,
    TokenType,
    TokenError,
    TokenExpiredError,
    TokenInvalidError,
    TokenTypeMismatchError,
)
from auth_core.revocation import (
    TokenBlacklist,
    RevocationStats,
)
from auth_core.keys import (
    generate_ed25519_keypair,
    load_private_key,
    load_public_key,
    save_keypair,
)

# Zitadel integration (recommended for new apps)
from auth_core.zitadel import (
    ZitadelAuth,
    ZitadelTokenPayload,
    ZitadelTokenError,
    ZitadelTokenExpiredError,
    ZitadelTokenInvalidError,
    create_zitadel_auth,
)

__all__ = [
    # Zitadel (recommended)
    "ZitadelAuth",
    "ZitadelTokenPayload",
    "ZitadelTokenError",
    "ZitadelTokenExpiredError",
    "ZitadelTokenInvalidError",
    "create_zitadel_auth",
    # Ed25519 JWT (legacy)
    "Ed25519Auth",
    "TokenConfig",
    "TokenPayload",
    "TokenType",
    "TokenError",
    "TokenExpiredError",
    "TokenInvalidError",
    "TokenTypeMismatchError",
    # Revocation
    "TokenBlacklist",
    "RevocationStats",
    # Key management (for Ed25519)
    "generate_ed25519_keypair",
    "load_private_key",
    "load_public_key",
    "save_keypair",
]

__version__ = "0.2.0"
