"""Rate limiting middleware using slowapi.

Protects authentication endpoints from brute force attacks.
Uses in-memory storage for simplicity (consider Redis for production clusters).
"""

from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request, Response
from fastapi.responses import JSONResponse


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

    return f"ip:{ip}"


# Initialize limiter with in-memory storage
# For multi-instance deployments, configure Redis:
#   storage_uri="redis://localhost:6379"
limiter = Limiter(
    key_func=rate_limit_key_func,
    default_limits=["1000/hour"],
    headers_enabled=True,
)


def rate_limit_handler(request: Request, exc: RateLimitExceeded) -> Response:
    """Custom handler for rate limit exceeded errors."""
    # Parse retry-after from exc.detail (format: "5 per 15 minutes")
    try:
        parts = exc.detail.split()
        retry_after = int(parts[-2]) * 60 if "minute" in exc.detail else 60
    except (IndexError, ValueError):
        retry_after = 60

    return JSONResponse(
        status_code=429,
        content={
            "error": "rate_limit_exceeded",
            "message": "Too many requests. Please try again later.",
            "detail": exc.detail,
        },
        headers={
            "Retry-After": str(retry_after),
            "X-RateLimit-Remaining": "0",
        },
    )


# Rate limit constants for endpoints
LOGIN_RATE_LIMIT = "5/15 minutes"      # 5 attempts per 15 minutes
REGISTER_RATE_LIMIT = "3/hour"         # 3 registrations per hour per IP
MAGIC_LINK_RATE_LIMIT = "10/hour"      # 10 magic link requests per hour
PASSWORD_RESET_RATE_LIMIT = "3/hour"   # 3 password reset requests per hour
