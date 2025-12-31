from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request, HTTPException
import redis.asyncio as redis
from typing import Optional
import time
import json
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

# Initialize Redis for rate limiting
redis_client: Optional[redis.Redis] = None
redis_available: bool = True  # Track Redis availability


async def get_redis_client():
    """Get Redis client for rate limiting with error handling"""
    global redis_client, redis_available
    if redis_client is None:
        try:
            # Use rate limiting on database 1 to separate from main cache (db 0)
            redis_url = settings.REDIS_URL.replace("/0", "/1") if "/0" in settings.REDIS_URL else f"{settings.REDIS_URL}/1"
            redis_client = redis.from_url(redis_url, decode_responses=True)
            # Test connection
            await redis_client.ping()
            logger.info("Redis client initialized for rate limiting")
            redis_available = True
        except Exception as e:
            logger.warning(f"Redis unavailable for rate limiting (degraded mode): {e}")
            redis_available = False
            return None
    return redis_client


def _create_limiter():
    """Create limiter with fallback for Redis connection issues"""
    try:
        redis_url_for_limiter = settings.REDIS_URL.replace("/0", "/1") if "/0" in settings.REDIS_URL else f"{settings.REDIS_URL}/1"
        lim = Limiter(
            key_func=get_remote_address,
            storage_uri=redis_url_for_limiter,
            default_limits=["1000/hour", "100/minute"],
        )
        return lim
    except Exception as e:
        # Fallback to in-memory limiter if Redis connection fails at startup
        logger.warning(f"Redis connection failed at startup, using in-memory rate limiting: {e}")
        return Limiter(
            key_func=get_remote_address,
            storage_uri="memory://",
            default_limits=["1000/hour", "100/minute"],
        )


# Initialize limiter with fallback
limiter = _create_limiter()


async def check_rate_limits(
    client_ip: str, endpoint_type: str, max_requests: int, window_seconds: int
):
    """Check specific rate limit for endpoint type"""
    redis_conn = await get_redis_client()

    # Skip rate limiting if Redis is unavailable (degraded mode)
    if redis_conn is None:
        logger.debug(f"Rate limiting skipped for {endpoint_type} - Redis unavailable")
        return

    current_time = int(time.time())
    window_start = current_time - window_seconds

    # Redis key for this client and endpoint type
    key = f"rate_limit:{endpoint_type}:{client_ip}"

    try:
        # Clean old entries and add current request
        pipe = redis_conn.pipeline()
        pipe.zremrangebyscore(key, 0, window_start)
        pipe.zcard(key)
        pipe.zadd(key, {str(current_time): current_time})
        pipe.expire(key, window_seconds)

        results = await pipe.execute()
        request_count = results[1]

        if request_count >= max_requests:
            raise HTTPException(
                status_code=429,
                detail={
                    "error": "Rate limit exceeded",
                    "message": f"Too many requests. Maximum {max_requests} requests per {window_seconds} seconds allowed.",
                    "retry_after": window_seconds,
                },
                headers={"Retry-After": str(window_seconds)},
            )
    except HTTPException:
        raise
    except Exception as e:
        # Log but don't fail the request if rate limiting has issues
        logger.warning(f"Rate limit check failed (allowing request): {e}")


def get_client_ip(request: Request) -> str:
    """Get client IP with proxy support"""
    # Check for forwarded headers
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()

    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip

    return request.client.host if request.client else "unknown"


async def check_endpoint_rate_limits(request: Request):
    """Check rate limits based on endpoint type"""
    client_ip = get_client_ip(request)
    path = request.url.path

    # Define rate limits for different endpoint types
    if path.startswith("/api/auth/"):
        # Stricter limits for auth endpoints
        await check_rate_limits(
            client_ip,
            "auth",
            max_requests=5,
            window_seconds=300,  # 5 requests per 5 minutes
        )
    elif path.startswith("/api/webhooks/"):
        # Moderate limits for webhook endpoints to prevent abuse
        await check_rate_limits(
            client_ip,
            "webhooks",
            max_requests=30,
            window_seconds=60,  # 30 requests per minute
        )
    elif path.startswith("/api/ai/"):
        # Moderate limits for AI endpoints
        await check_rate_limits(
            client_ip,
            "ai",
            max_requests=50,
            window_seconds=3600,  # 50 requests per hour
        )
    elif path.startswith("/api/"):
        # General API limits
        await check_rate_limits(
            client_ip,
            "api",
            max_requests=1000,
            window_seconds=3600,  # 1000 requests per hour
        )


# Rate limit decorators for specific endpoints
def auth_rate_limit(max_requests: int = 5, window_seconds: int = 300):
    """Rate limiting decorator for auth endpoints"""

    def decorator(func):
        return limiter.limit(f"{max_requests}/{window_seconds}seconds")(func)

    return decorator


def ai_rate_limit(max_requests: int = 50, window_seconds: int = 3600):
    """Rate limiting decorator for AI endpoints"""

    def decorator(func):
        return limiter.limit(f"{max_requests}/{window_seconds}seconds")(func)

    return decorator


def general_rate_limit(max_requests: int = 1000, window_seconds: int = 3600):
    """Rate limiting decorator for general API endpoints"""

    def decorator(func):
        return limiter.limit(f"{max_requests}/{window_seconds}seconds")(func)

    return decorator


def webhook_rate_limit(max_requests: int = 30, window_seconds: int = 60):
    """
    Rate limiting decorator for webhook endpoints.

    Default: 30 requests per minute per client IP.
    This prevents abuse from automated systems while allowing
    reasonable webhook traffic from legitimate integrations.
    """

    def decorator(func):
        return limiter.limit(f"{max_requests}/{window_seconds}seconds")(func)

    return decorator
