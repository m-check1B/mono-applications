"""Rate limiting middleware using slowapi and Redis."""
import os

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address


def get_redis_url() -> str:
    """Get Redis URL from environment or default."""
    return os.getenv("REDIS_URL", "redis://redis:6379")


def rate_limit_key_func(request: Request) -> str:
    """
    Generate rate limit key from request.
    Uses X-Forwarded-For if behind proxy, otherwise remote address.
    """
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        # Get first IP from X-Forwarded-For chain
        ip = forwarded.split(",")[0].strip()
    else:
        ip = get_remote_address(request)

    # Add user ID for authenticated requests
    if hasattr(request.state, "user") and request.state.user:
        return f"user:{request.state.user.id}"

    return f"ip:{ip}"


# Initialize limiter with Redis backend
limiter = Limiter(
    key_func=rate_limit_key_func,
    storage_uri=get_redis_url(),
    default_limits=["1000/hour"],  # Global default
    headers_enabled=True,  # Return rate limit headers
)


def rate_limit_handler(request: Request, exc: RateLimitExceeded) -> Response:
    """Custom handler for rate limit exceeded errors."""
    return JSONResponse(
        status_code=429,
        content={
            "error": "rate_limit_exceeded",
            "message": "Too many requests. Please try again later.",
            "retry_after": exc.detail,
        },
        headers={
            "Retry-After": str(int(exc.detail.split()[-2])),
            "X-RateLimit-Limit": request.headers.get("X-RateLimit-Limit", "unknown"),
            "X-RateLimit-Remaining": "0",
            "X-RateLimit-Reset": request.headers.get("X-RateLimit-Reset", "unknown"),
        },
    )


# Rate limit decorators for common use cases
LOGIN_RATE_LIMIT = "5/15 minutes"  # 5 attempts per 15 minutes
API_RATE_LIMIT = "100/minute"      # 100 requests per minute
HEALTH_RATE_LIMIT = "10/second"    # Health checks can be frequent
WEBHOOK_RATE_LIMIT = "100/minute"  # Webhooks from telephony providers (per IP)

# Additional rate limits for API abuse prevention
CALL_INITIATION_RATE_LIMIT = "20/minute"  # Prevent call flooding
SESSION_RATE_LIMIT = "30/minute"          # Session creation
AI_SERVICE_RATE_LIMIT = "50/minute"       # AI-powered endpoints (higher cost)
BILLING_RATE_LIMIT = "10/minute"          # Billing operations
WRITE_OPERATION_RATE_LIMIT = "60/minute"  # POST/PUT/DELETE operations
BULK_OPERATION_RATE_LIMIT = "10/minute"   # Bulk imports and operations
