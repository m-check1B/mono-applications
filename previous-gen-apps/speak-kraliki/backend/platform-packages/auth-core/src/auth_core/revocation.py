"""
Redis-based Token Revocation System

Provides logout mechanism and security controls for Ed25519 JWT:
- Revoke individual tokens (logout)
- Revoke all user tokens (password change, security breach)
- Automatic expiration (TTL matches token expiry)
- Fast O(1) lookup for token validation
"""

from datetime import datetime, timedelta
from typing import Optional, Protocol, runtime_checkable
from dataclasses import dataclass


@dataclass
class RevocationStats:
    """Statistics about revoked tokens."""
    revoked_tokens: int
    revoked_users: int
    total_revocations: int


@runtime_checkable
class AsyncRedisClient(Protocol):
    """Protocol for async Redis client."""
    async def setex(self, name: str, time: int, value: str) -> None: ...
    async def exists(self, name: str) -> int: ...
    async def keys(self, pattern: str) -> list: ...
    async def close(self) -> None: ...


class TokenBlacklist:
    """
    Redis-based token blacklist for logout and security.

    Features:
    - Revoke individual tokens (logout)
    - Revoke all user tokens (password change, security breach)
    - Automatic expiration (TTL matches token expiry)
    - Fast O(1) lookup for token validation
    - Graceful degradation when Redis unavailable

    Usage:
        blacklist = TokenBlacklist(redis_url="redis://localhost:6379")
        await blacklist.connect()

        # Revoke single token
        await blacklist.revoke_token(token, exp_timestamp)

        # Check if revoked
        if await blacklist.is_revoked(token):
            raise AuthError("Token revoked")

        # Revoke all user tokens (password change)
        await blacklist.revoke_all_user_tokens(user_id)
    """

    def __init__(
        self,
        redis_url: Optional[str] = None,
        redis_client: Optional[AsyncRedisClient] = None,
        refresh_token_expire_days: int = 7,
        key_prefix: str = "blacklist",
    ):
        """
        Initialize Redis connection for token blacklist.

        Args:
            redis_url: Redis connection URL
            redis_client: Pre-configured async Redis client
            refresh_token_expire_days: Max token lifetime for user revocation TTL
            key_prefix: Redis key prefix for namespacing
        """
        self.redis_url = redis_url
        self._redis: Optional[AsyncRedisClient] = redis_client
        self.refresh_token_expire_days = refresh_token_expire_days
        self.key_prefix = key_prefix

    async def connect(self) -> None:
        """Establish Redis connection."""
        if self._redis:
            return

        if not self.redis_url:
            return  # No Redis URL, graceful degradation

        try:
            import redis.asyncio as redis
            self._redis = await redis.from_url(
                self.redis_url,
                decode_responses=True,
                encoding="utf-8",
            )
        except ImportError:
            raise ImportError(
                "redis package required for token revocation. "
                "Install with: pip install auth-core[redis]"
            )

    async def disconnect(self) -> None:
        """Close Redis connection."""
        if self._redis:
            await self._redis.close()
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
            return self._redis is not None
        except Exception:
            # Redis optional - graceful degradation
            return False

    def _token_key(self, token: str) -> str:
        """Generate Redis key for token."""
        return f"{self.key_prefix}:token:{token}"

    def _user_key(self, user_id: str) -> str:
        """Generate Redis key for user revocation."""
        return f"{self.key_prefix}:user:{user_id}"

    async def revoke_token(self, token: str, exp: int) -> bool:
        """
        Add token to blacklist until its natural expiration.

        Args:
            token: JWT token string
            exp: Token expiration timestamp (Unix epoch)

        Returns:
            True if revoked successfully, False if Redis unavailable
        """
        now = int(datetime.utcnow().timestamp())
        ttl = max(0, exp - now)

        if ttl <= 0:
            return True  # Token already expired, no need to blacklist

        if not await self._ensure_connection():
            return False

        try:
            await self._redis.setex(
                self._token_key(token),
                ttl,
                "revoked",
            )
            return True
        except Exception:
            return False

    async def is_revoked(self, token: str) -> bool:
        """
        Check if token is blacklisted.

        Args:
            token: JWT token string

        Returns:
            True if token is revoked, False otherwise
        """
        if not await self._ensure_connection():
            return False  # Can't check, assume valid

        try:
            exists = await self._redis.exists(self._token_key(token))
            return bool(exists)
        except Exception:
            return False

    async def revoke_all_user_tokens(self, user_id: str) -> bool:
        """
        Revoke all tokens for a user (password change, security breach).

        Creates a global revocation for the user that lasts longer than
        the maximum token lifetime.

        Args:
            user_id: User ID to revoke all tokens for

        Returns:
            True if revoked successfully, False if Redis unavailable
        """
        ttl = int(timedelta(days=self.refresh_token_expire_days).total_seconds())

        if not await self._ensure_connection():
            return False

        try:
            await self._redis.setex(
                self._user_key(user_id),
                ttl,
                "all_revoked",
            )
            return True
        except Exception:
            return False

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
            exists = await self._redis.exists(self._user_key(user_id))
            return bool(exists)
        except Exception:
            return False

    async def is_token_or_user_revoked(self, token: str, user_id: str) -> bool:
        """
        Check if either the specific token or all user tokens are revoked.

        This is the recommended check for authorization middleware.

        Args:
            token: JWT token string
            user_id: User ID from token payload

        Returns:
            True if access should be denied, False if allowed
        """
        if await self.is_revoked(token):
            return True
        if await self.is_user_revoked(user_id):
            return True
        return False

    async def get_revocation_stats(self) -> RevocationStats:
        """
        Get statistics about revoked tokens.

        Returns:
            RevocationStats with counts
        """
        if not await self._ensure_connection():
            return RevocationStats(
                revoked_tokens=0,
                revoked_users=0,
                total_revocations=0,
            )

        try:
            token_keys = await self._redis.keys(f"{self.key_prefix}:token:*")
            user_keys = await self._redis.keys(f"{self.key_prefix}:user:*")

            return RevocationStats(
                revoked_tokens=len(token_keys),
                revoked_users=len(user_keys),
                total_revocations=len(token_keys) + len(user_keys),
            )
        except Exception:
            return RevocationStats(
                revoked_tokens=0,
                revoked_users=0,
                total_revocations=0,
            )

    async def clear_expired(self) -> None:
        """
        Clear expired entries.

        Note: This is a no-op as Redis handles expiration automatically via TTL.
        Provided for API completeness.
        """
        pass
