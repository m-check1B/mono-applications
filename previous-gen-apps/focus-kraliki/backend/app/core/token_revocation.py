"""
Redis-based Token Revocation System
Provides logout mechanism and security controls for Ed25519 JWT

This module now uses auth-core for the core implementation.
"""
import logging
from datetime import datetime, timedelta
from typing import Optional
import redis.asyncio as redis
from app.core.config import settings

logger = logging.getLogger(__name__)

# Try to use auth-core, fall back to local implementation
try:
    from auth_core import TokenBlacklist as BaseTokenBlacklist, RevocationStats
    AUTH_CORE_AVAILABLE = True
except ImportError:
    AUTH_CORE_AVAILABLE = False
    BaseTokenBlacklist = None


class TokenBlacklist:
    """
    Redis-based token blacklist for logout and security.

    Features:
    - Revoke individual tokens (logout)
    - Revoke all user tokens (password change, security breach)
    - Automatic expiration (TTL matches token expiry)
    - Fast O(1) lookup for token validation
    """

    def __init__(self, redis_url: Optional[str] = None):
        """
        Initialize Redis connection for token blacklist.

        Args:
            redis_url: Redis connection URL (defaults to settings.REDIS_URL)
        """
        self.redis_url = redis_url or settings.REDIS_URL
        self._redis: Optional[redis.Redis] = None

    async def connect(self):
        """Establish Redis connection."""
        if not self._redis:
            self._redis = await redis.from_url(
                self.redis_url,
                decode_responses=True,
                encoding="utf-8"
            )
            await self._redis.ping()

    async def disconnect(self):
        """Close Redis connection."""
        if self._redis:
            try:
                await self._redis.close()
            except Exception as e:
                logger.info(f"Redis close failed during shutdown (non-critical): {e}")
            self._redis = None

    async def _ensure_connection(self) -> bool:
        """
        Ensure Redis connection exists.

        Returns:
            True if connection available, False otherwise (graceful degradation)
        """
        if self._redis:
            return True

        try:
            await self.connect()
            return True
        except Exception as e:
            # Redis optional in local/dev/testing environments, but log at info for visibility
            logger.info(f"Redis connection unavailable for token blacklist (graceful degradation): {e}")
            return False

    async def revoke_token(self, token: str, exp: int):
        """
        Add token to blacklist until its natural expiration.

        Args:
            token: JWT token string
            exp: Token expiration timestamp (Unix epoch)
        """
        # Calculate TTL (time until token expires)
        now = int(datetime.utcnow().timestamp())
        ttl = max(0, exp - now)

        if ttl > 0 and await self._ensure_connection():
            try:
                await self._redis.setex(
                    f"blacklist:token:{token}",
                    ttl,
                    "revoked"
                )
            except Exception as e:
                logger.warning(f"Failed to revoke token (security risk): {e}")

    async def is_revoked(self, token: str) -> bool:
        """
        Check if token is blacklisted.

        Args:
            token: JWT token string

        Returns:
            True if token is revoked, False otherwise
        """
        if not await self._ensure_connection():
            return False

        try:
            exists = await self._redis.exists(f"blacklist:token:{token}")
            return bool(exists)
        except Exception as e:
            # Security: Log at warning level since failing to check revocation is a potential security issue
            logger.warning(f"Token revocation check failed, allowing token (potential security risk): {e}")
            return False

    async def revoke_all_user_tokens(self, user_id: str):
        """
        Revoke all tokens for a user (e.g., password change, security breach).

        This creates a global revocation for the user that lasts longer than
        the maximum token lifetime (from settings).

        Args:
            user_id: User ID to revoke all tokens for
        """
        # Revoke for max refresh token lifetime (from settings)
        ttl = int(timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS).total_seconds())

        if not await self._ensure_connection():
            return

        try:
            await self._redis.setex(
                f"blacklist:user:{user_id}",
                ttl,
                "all_revoked"
            )
        except Exception as e:
            logger.warning(f"Failed to revoke all tokens for user {user_id} (security risk): {e}")

    async def is_user_revoked(self, user_id: str) -> bool:
        """
        Check if all user tokens are revoked.

        Args:
            user_id: User ID to check

        Returns:
            True if all user tokens are revoked, False otherwise
        """
        if not await self._ensure_connection():
            return False

        try:
            exists = await self._redis.exists(f"blacklist:user:{user_id}")
            return bool(exists)
        except Exception as e:
            # Security: Log at warning level since failing to check revocation is a potential security issue
            logger.warning(f"User revocation check failed, allowing user (potential security risk): {e}")
            return False

    async def get_revocation_stats(self) -> dict:
        """
        Get statistics about revoked tokens.

        Returns:
            Dictionary with revocation stats
        """
        # Count blacklisted tokens
        if not await self._ensure_connection():
            return {
                "revoked_tokens": 0,
                "revoked_users": 0,
                "total_revocations": 0
            }

        try:
            token_keys = await self._redis.keys("blacklist:token:*")
            user_keys = await self._redis.keys("blacklist:user:*")

            return {
                "revoked_tokens": len(token_keys),
                "revoked_users": len(user_keys),
                "total_revocations": len(token_keys) + len(user_keys)
            }
        except Exception as e:
            # Stats are non-critical, but log at info level for visibility in monitoring
            logger.info(f"Failed to get revocation stats (non-critical): {e}")
            return {
                "revoked_tokens": 0,
                "revoked_users": 0,
                "total_revocations": 0
            }

    async def clear_expired(self):
        """
        Clear expired entries (Redis does this automatically via TTL).

        This is a no-op but provided for API completeness.
        Redis automatically removes keys when TTL expires.
        """
        # Redis handles expiration automatically
        pass


# Global instance (initialize in main.py startup)
token_blacklist = TokenBlacklist()
