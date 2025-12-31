"""
Redis-based caching system for AI responses and flow memory
"""
import asyncio
import json
import hashlib
import logging
from typing import Optional, Any, Dict
from datetime import timedelta
import redis.asyncio as redis
from app.core.config import settings

logger = logging.getLogger(__name__)


class CacheManager:
    """Manages Redis caching operations"""

    def __init__(self):
        self._redis: Optional[redis.Redis] = None
        self._loop_id: Optional[int] = None

    async def get_redis(self) -> redis.Redis:
        """Get or create Redis connection"""
        current_loop = asyncio.get_running_loop()
        loop_id = id(current_loop)
        if self._redis is None or self._loop_id != loop_id:
            if self._redis is not None:
                try:
                    await self._redis.close()
                except Exception as e:
                    logger.debug(f"Redis close failed during reconnection (non-critical): {e}")
            self._redis = redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True
            )
            self._loop_id = loop_id
        return self._redis

    async def close(self):
        """Close Redis connection"""
        if self._redis:
            await self._redis.close()
        self._redis = None
        self._loop_id = None

    async def __aenter__(self):
        await self.get_redis()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    def _generate_key(self, prefix: str, data: Any) -> str:
        """Generate cache key from data"""
        if isinstance(data, dict):
            data_str = json.dumps(data, sort_keys=True)
        else:
            data_str = str(data)

        hash_obj = hashlib.sha256(data_str.encode())
        return f"{prefix}:{hash_obj.hexdigest()}"

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            redis_client = await self.get_redis()
            value = await redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.info(f"Cache get error (non-critical, falling back to uncached): {e}")
            return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl: int = 3600
    ) -> bool:
        """Set value in cache with TTL (seconds)"""
        try:
            redis_client = await self.get_redis()
            serialized = json.dumps(value)
            await redis_client.setex(key, ttl, serialized)
            return True
        except Exception as e:
            logger.info(f"Cache set error (non-critical, value not cached): {e}")
            return False

    async def delete(self, key: str) -> bool:
        """Delete key from cache"""
        try:
            redis_client = await self.get_redis()
            await redis_client.delete(key)
            return True
        except Exception as e:
            logger.info(f"Cache delete error (non-critical): {e}")
            return False

    async def get_ai_response(
        self,
        model: str,
        prompt: str,
        context: Optional[Dict] = None
    ) -> Optional[str]:
        """Get cached AI response"""
        cache_data = {
            "model": model,
            "prompt": prompt,
            "context": context or {}
        }
        key = self._generate_key("ai_response", cache_data)
        cached = await self.get(key)
        return cached.get("response") if cached else None

    async def cache_ai_response(
        self,
        model: str,
        prompt: str,
        response: str,
        context: Optional[Dict] = None,
        ttl: int = 3600
    ) -> bool:
        """Cache AI response"""
        cache_data = {
            "model": model,
            "prompt": prompt,
            "context": context or {}
        }
        key = self._generate_key("ai_response", cache_data)
        value = {
            "response": response,
            "model": model,
            "cached_at": json.dumps({"timestamp": "now"})
        }
        return await self.set(key, value, ttl)


class FlowMemory:
    """Manages flow memory and session context"""

    def __init__(self, cache_manager: CacheManager):
        self.cache = cache_manager
        self.ttl = 86400  # 24 hours

    async def save_context(
        self,
        user_id: str,
        session_id: str,
        context: Dict[str, Any]
    ) -> bool:
        """Save session context"""
        key = f"flow_memory:{user_id}:{session_id}"
        return await self.cache.set(key, context, self.ttl)

    async def get_context(
        self,
        user_id: str,
        session_id: str
    ) -> Optional[Dict[str, Any]]:
        """Retrieve session context"""
        key = f"flow_memory:{user_id}:{session_id}"
        return await self.cache.get(key)

    async def update_context(
        self,
        user_id: str,
        session_id: str,
        updates: Dict[str, Any]
    ) -> bool:
        """Update session context"""
        key = f"flow_memory:{user_id}:{session_id}"
        context = await self.cache.get(key) or {}
        context.update(updates)
        return await self.cache.set(key, context, self.ttl)

    async def save_memory(
        self,
        user_id: str,
        memory_key: str,
        memory_value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """Save long-term memory"""
        key = f"memory:{user_id}:{memory_key}"
        return await self.cache.set(key, memory_value, ttl or self.ttl)

    async def recall_memory(
        self,
        user_id: str,
        memory_key: str
    ) -> Optional[Any]:
        """Recall long-term memory"""
        key = f"memory:{user_id}:{memory_key}"
        return await self.cache.get(key)

    async def get_recent_interactions(
        self,
        user_id: str,
        limit: int = 10
    ) -> list:
        """Get recent user interactions"""
        key = f"interactions:{user_id}"
        interactions = await self.cache.get(key) or []
        return interactions[-limit:]

    async def add_interaction(
        self,
        user_id: str,
        interaction: Dict[str, Any]
    ) -> bool:
        """Add interaction to history"""
        key = f"interactions:{user_id}"
        interactions = await self.cache.get(key) or []
        interactions.append(interaction)
        # Keep last 100 interactions
        interactions = interactions[-100:]
        return await self.cache.set(key, interactions, self.ttl * 7)  # 7 days


# Global instances
cache_manager = CacheManager()
flow_memory = FlowMemory(cache_manager)


async def get_cache_manager() -> CacheManager:
    """Dependency for cache manager"""
    return cache_manager


async def get_flow_memory() -> FlowMemory:
    """Dependency for flow memory"""
    return flow_memory
