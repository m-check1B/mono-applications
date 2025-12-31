"""Persistent storage for Sense by Kraliki bot using Redis and PostgreSQL."""
import json
import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

import redis.asyncio as redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_session_factory
from app.models.user import User

logger = logging.getLogger(__name__)

CURRENT_KEY_PREFIX = "sense-kraliki"
LEGACY_KEY_PREFIX = "senseit"

class BotStorage:
    """Store and retrieve user data and subscription status."""

    def __init__(self):
        self.redis: Optional[redis.Redis] = None

    async def connect(self):
        """Initialize Redis connection."""
        if not self.redis:
            self.redis = redis.from_url(settings.redis_url, decode_responses=True)

    async def close(self):
        """Close Redis connection."""
        if self.redis:
            await self.redis.close()

    def _user_key(self, user_id: int, prefix: str = CURRENT_KEY_PREFIX) -> str:
        """Generate Redis key for a user profile."""
        return f"{prefix}:user:{user_id}:profile"

    async def get_user(self, user_id: int) -> Dict[str, Any]:
        """Fetch user profile from Redis (cache) or Postgres (primary)."""
        await self.connect()
        
        # 1. Try Redis cache
        data = await self.redis.get(self._user_key(user_id))
        legacy_data = None
        if not data:
            legacy_data = await self.redis.get(self._user_key(user_id, LEGACY_KEY_PREFIX))
            data = legacy_data
        if data:
            try:
                user_dict = json.loads(data)
                # Convert back dates
                for key in ["birth_date", "premium_until"]:
                    if key in user_dict and user_dict[key]:
                        user_dict[key] = datetime.fromisoformat(user_dict[key])
                if legacy_data:
                    await self._update_cache(user_id, user_dict)
                return user_dict
            except (json.JSONDecodeError, ValueError) as e:
                logger.error(f"Error decoding user data for {user_id} from cache: {e}")

        # 2. Try Postgres primary store
        session_factory = get_session_factory()
        if session_factory is None:
            return {}  # Database not configured
        async with session_factory() as session:
            result = await session.execute(select(User).where(User.user_id == user_id))
            user_obj = result.scalar_one_or_none()
            
            if user_obj:
                user_dict = user_obj.to_dict()
                # Update Redis cache
                await self._update_cache(user_id, user_dict)
                return user_dict
        
        return {}

    async def _update_cache(self, user_id: int, user_dict: Dict[str, Any]):
        """Update Redis cache for a user."""
        await self.connect()
        # Prepare for JSON serialization
        json_user = user_dict.copy()
        for key in ["birth_date", "premium_until"]:
            if key in json_user and isinstance(json_user[key], datetime):
                json_user[key] = json_user[key].isoformat()
            
        await self.redis.set(self._user_key(user_id), json.dumps(json_user), ex=86400) # 24h cache

    async def update_user(self, user_id: int, updates: Dict[str, Any]):
        """Update user profile in both Postgres and Redis cache."""
        await self.connect()

        session_factory = get_session_factory()
        if session_factory is None:
            logger.warning("Database not configured, user update only in cache")
            return
        async with session_factory() as session:
            result = await session.execute(select(User).where(User.user_id == user_id))
            user_obj = result.scalar_one_or_none()
            
            if not user_obj:
                user_obj = User(user_id=user_id)
                session.add(user_obj)
            
            for key, value in updates.items():
                if hasattr(user_obj, key):
                    setattr(user_obj, key, value)
            
            await session.commit()
            user_dict = user_obj.to_dict()
        
        # Update Redis cache
        await self._update_cache(user_id, user_dict)

    async def set_premium(self, user_id: int, plan: str, months: int = 1):
        """Set user as premium for a specified number of months."""
        until = datetime.now(timezone.utc) + timedelta(days=30 * months)
        # SQLAlchemy handles timezone-aware datetimes if configured, but let's be safe
        # Ensure it's naive if DB expects naive, or aware if DB expects aware.
        # Usually standard DateTime in SQLAlchemy is naive.
        until_naive = until.replace(tzinfo=None)
        
        await self.update_user(user_id, {
            "premium": True,
            "premium_until": until_naive,
            "plan": plan
        })

    async def is_premium(self, user_id: int) -> bool:
        """Check if user has an active premium subscription."""
        user = await self.get_user(user_id)
        if not user.get("premium"):
            return False
        
        until = user.get("premium_until")
        if not until:
            return False
            
        if until.tzinfo is None:
            until = until.replace(tzinfo=timezone.utc)
            
        if until < datetime.now(timezone.utc):
            # Subscription expired
            await self.update_user(user_id, {"premium": False})
            return False
            
        return True

    # LLM Rate Limiting Keys (Redis only)
    def _llm_rate_key(self, user_id: int, window: str, prefix: str = CURRENT_KEY_PREFIX) -> str:
        """Generate Redis key for LLM rate limiting."""
        return f"{prefix}:user:{user_id}:llm_calls:{window}"

    async def check_llm_rate_limit(self, user_id: int) -> tuple[bool, str]:
        """Check if user is within LLM rate limits."""
        await self.connect()

        is_premium = await self.is_premium(user_id)

        # Limits based on subscription
        if is_premium:
            hourly_limit = 20
            daily_limit = 100
        else:
            hourly_limit = 3
            daily_limit = 10

        # Global burst limit (all users)
        minute_limit = 5

        now = datetime.now(timezone.utc)

        # Check minute burst limit
        minute_key = self._llm_rate_key(user_id, f"minute:{now.strftime('%Y%m%d%H%M')}")
        minute_count = await self.redis.incr(minute_key)
        if minute_count == 1:
            await self.redis.expire(minute_key, 60)  # 1 minute TTL
        if minute_count > minute_limit:
            return False, "Too many requests. Please wait a minute before trying again."

        # Check hourly limit
        hour_key = self._llm_rate_key(user_id, f"hour:{now.strftime('%Y%m%d%H')}")
        hour_count = await self.redis.incr(hour_key)
        if hour_count == 1:
            await self.redis.expire(hour_key, 3600)  # 1 hour TTL
        if hour_count > hourly_limit:
            if is_premium:
                return False, f"Hourly limit reached ({hourly_limit}/hour). Please wait."
            return False, (
                f"Free tier hourly limit reached ({hourly_limit}/hour). "
                "Upgrade with /subscribe for more."
            )

        # Check daily limit
        day_key = self._llm_rate_key(user_id, f"day:{now.strftime('%Y%m%d')}")
        day_count = await self.redis.incr(day_key)
        if day_count == 1:
            await self.redis.expire(day_key, 86400)  # 24 hour TTL
        if day_count > daily_limit:
            if is_premium:
                return False, f"Daily limit reached ({daily_limit}/day). Resets at midnight UTC."
            return False, (
                f"Free tier daily limit reached ({daily_limit}/day). "
                "Upgrade with /subscribe for more."
            )

        return True, ""

    async def get_llm_usage(self, user_id: int) -> dict:
        """Get current LLM usage for a user."""
        await self.connect()

        is_premium = await self.is_premium(user_id)
        now = datetime.now(timezone.utc)

        # Get current counts
        hour_key = self._llm_rate_key(user_id, f"hour:{now.strftime('%Y%m%d%H')}")
        day_key = self._llm_rate_key(user_id, f"day:{now.strftime('%Y%m%d')}")

        hour_count = await self.redis.get(hour_key)
        day_count = await self.redis.get(day_key)

        return {
            "hourly": {
                "used": int(hour_count or 0),
                "limit": 20 if is_premium else 3,
            },
            "daily": {
                "used": int(day_count or 0),
                "limit": 100 if is_premium else 10,
            },
            "is_premium": is_premium,
        }


# Global instance
storage = BotStorage()
