"""
Token Revocation Service
Redis-backed token revocation list for JWT authentication
Prevents compromised tokens from being used
"""

import logging
from datetime import UTC, datetime

import redis
from redis.exceptions import RedisError

from app.config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class TokenRevocationService:
    """
    Redis-backed token revocation service

    Manages revoked tokens with automatic expiration based on JWT expiration time.
    Uses Redis for fast lookups and distributed token blacklisting.
    """

    def __init__(self):
        """Initialize Redis connection for token revocation"""
        try:
            self.redis_client = redis.Redis(
                host=settings.redis_host,
                port=settings.redis_port,
                db=settings.redis_db,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
            )
            # Test connection
            self.redis_client.ping()
            logger.info(
                f"Token revocation service initialized with Redis at {settings.redis_host}:{settings.redis_port}"
            )
        except RedisError as e:
            logger.error(f"Failed to connect to Redis for token revocation: {e}")
            # Fallback to None - graceful degradation
            self.redis_client = None

        self.prefix = "revoked_token:"
        self.user_tokens_prefix = "user_tokens:"

    def revoke_token(self, jti: str, expires_at: datetime) -> bool:
        """
        Add token to revocation list

        Args:
            jti: JWT Token ID (unique identifier)
            expires_at: Token expiration timestamp

        Returns:
            bool: True if token was revoked successfully, False otherwise
        """
        if not self.redis_client:
            logger.warning("Redis not available, cannot revoke token")
            return False

        try:
            key = f"{self.prefix}{jti}"
            # Calculate TTL: only store until token would expire anyway
            ttl = int((expires_at - datetime.now(UTC)).total_seconds())

            if ttl > 0:
                # Store with automatic expiration
                self.redis_client.setex(key, ttl, "revoked")
                logger.info(f"Token revoked: {jti} (expires in {ttl}s)")
                return True
            else:
                logger.warning(f"Token already expired: {jti}")
                return False
        except RedisError as e:
            logger.error(f"Failed to revoke token {jti}: {e}")
            return False

    def is_token_revoked(self, jti: str) -> bool:
        """
        Check if token is revoked

        Args:
            jti: JWT Token ID

        Returns:
            bool: True if token is revoked, False otherwise
        """
        if not self.redis_client:
            # If Redis is down, fail open (allow tokens) to prevent service disruption
            # In production, you might want to fail closed (deny all) instead
            logger.warning("Redis not available, cannot check token revocation status")
            return False

        try:
            key = f"{self.prefix}{jti}"
            return self.redis_client.exists(key) > 0
        except RedisError as e:
            logger.error(f"Failed to check token revocation status for {jti}: {e}")
            return False

    def revoke_all_user_tokens(self, user_id: str) -> bool:
        """
        Revoke all tokens for a user by invalidating user token tracking

        Note: This is a marker that all previous tokens for this user should be invalid.
        You could extend this to track all JTIs per user for more granular control.

        Args:
            user_id: User identifier

        Returns:
            bool: True if operation succeeded, False otherwise
        """
        if not self.redis_client:
            logger.warning("Redis not available, cannot revoke user tokens")
            return False

        try:
            key = f"{self.user_tokens_prefix}{user_id}"
            # Set revocation timestamp
            revocation_time = datetime.now(UTC).isoformat()
            self.redis_client.set(key, revocation_time)
            logger.info(f"All tokens revoked for user: {user_id}")
            return True
        except RedisError as e:
            logger.error(f"Failed to revoke all tokens for user {user_id}: {e}")
            return False

    def get_user_revocation_time(self, user_id: str) -> str | None:
        """
        Get the timestamp when all user tokens were revoked

        Args:
            user_id: User identifier

        Returns:
            Optional[str]: ISO format timestamp or None
        """
        if not self.redis_client:
            return None

        try:
            key = f"{self.user_tokens_prefix}{user_id}"
            return self.redis_client.get(key)
        except RedisError as e:
            logger.error(f"Failed to get user revocation time for {user_id}: {e}")
            return None

    def is_token_revoked_for_user(self, user_id: str, token_issued_at: datetime) -> bool:
        """
        Check if a token was issued before user tokens were revoked

        Args:
            user_id: User identifier
            token_issued_at: When the token was issued (iat claim)

        Returns:
            bool: True if token should be considered revoked
        """
        revocation_time_str = self.get_user_revocation_time(user_id)
        if not revocation_time_str:
            return False

        try:
            revocation_time = datetime.fromisoformat(revocation_time_str)
            # Token is revoked if it was issued before the revocation time
            return token_issued_at < revocation_time
        except (ValueError, TypeError) as e:
            logger.error(f"Failed to parse revocation time: {e}")
            return False

    def clear_user_revocation(self, user_id: str) -> bool:
        """
        Clear user token revocation (allow new tokens)

        Args:
            user_id: User identifier

        Returns:
            bool: True if operation succeeded
        """
        if not self.redis_client:
            return False

        try:
            key = f"{self.user_tokens_prefix}{user_id}"
            self.redis_client.delete(key)
            logger.info(f"Cleared token revocation for user: {user_id}")
            return True
        except RedisError as e:
            logger.error(f"Failed to clear revocation for user {user_id}: {e}")
            return False

    def health_check(self) -> bool:
        """
        Check if Redis connection is healthy

        Returns:
            bool: True if Redis is available and responsive
        """
        if not self.redis_client:
            return False

        try:
            return self.redis_client.ping()
        except RedisError:
            return False


# Global revocation service instance
_revocation_service: TokenRevocationService | None = None


def get_revocation_service() -> TokenRevocationService:
    """
    Get or create token revocation service instance

    Returns:
        TokenRevocationService: Singleton instance
    """
    global _revocation_service
    if _revocation_service is None:
        _revocation_service = TokenRevocationService()
    return _revocation_service


# Export for convenience
revocation_service = get_revocation_service()
