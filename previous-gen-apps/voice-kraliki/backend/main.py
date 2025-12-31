"""
Operator Demo 2026 - Production Backend
Updated: October 12, 2025
Python 3.12+ with full monitoring and security
"""

import logging
import os
from contextlib import asynccontextmanager

# Import routers
from app.api.ai_services import router as ai_services_router
from app.api.analytics import router as analytics_router
from app.api.authenticated_ai import router as authenticated_ai_router
from app.api.billing import router as billing_router
from app.api.feature_flags import router as feature_flags_router
from app.api.provider_health import router as provider_health_router
from app.auth.database_routes import router as database_auth_router
from app.auth.protected_routes import router as protected_auth_router
from app.auth.routes import router as auth_router
from app.auth.simple_routes import router as simple_auth_router
from app.campaigns.simple_routes import router as simple_campaigns_router

# Import configuration
from app.config.sentry import init_sentry
from app.middleware.rate_limit import limiter, rate_limit_handler

# Import middleware
from app.middleware.security_headers import SecurityHeadersMiddleware
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from slowapi.errors import RateLimitExceeded

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info("🚀 Starting Operator Demo 2026...")

    # Initialize Sentry
    init_sentry()

    # Initialize Prometheus metrics
    instrumentator = Instrumentator(
        should_group_status_codes=False,
        should_ignore_untemplated=True,
        should_respect_env_var=True,
        should_instrument_requests_inprogress=True,
        excluded_handlers=["/metrics", "/health"],
        env_var_name="ENABLE_METRICS",
        inprogress_name="http_requests_inprogress",
        inprogress_labels=True,
    )
    instrumentator.instrument(app).expose(app, endpoint="/metrics", include_in_schema=False)

    logger.info("✅ Application started successfully")

    yield  # Application is running

    # Shutdown
    logger.info("🛑 Shutting down Operator Demo 2026...")


# Create FastAPI application
app = FastAPI(
    title="Operator Demo 2026",
    description="Production-ready multi-provider telephony platform",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS - Production Ready
ALLOWED_ORIGINS = [
    os.getenv("FRONTEND_URL", "http://localhost:5173"),
    os.getenv("PRODUCTION_URL", "https://yourdomain.com"),
    "http://localhost:3000",  # Alternative frontend port
]

# Only add wildcard in development
if os.getenv("ENVIRONMENT", "production") == "development":
    ALLOWED_ORIGINS.append("*")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
    max_age=86400,  # Cache preflight requests for 24 hours
)

# Add security headers middleware
app.add_middleware(SecurityHeadersMiddleware)

# Add rate limiting state
app.state.limiter = limiter


# Rate limit exception handler
@app.exception_handler(RateLimitExceeded)
async def rate_limit_exception_handler(request: Request, exc: RateLimitExceeded):
    """Handle rate limit exceeded exceptions."""
    return rate_limit_handler(request, exc)


# Include routers
app.include_router(ai_services_router)
app.include_router(analytics_router)
app.include_router(authenticated_ai_router)
app.include_router(billing_router)
app.include_router(database_auth_router)
app.include_router(feature_flags_router)
app.include_router(provider_health_router)
app.include_router(protected_auth_router)
app.include_router(auth_router)
app.include_router(simple_auth_router)
app.include_router(simple_campaigns_router)


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "python": "3.12+",
        "environment": os.getenv("ENVIRONMENT", "production"),
    }


@app.get("/", tags=["Root"])
async def root():
    """API root endpoint."""
    return {
        "message": "Operator Demo 2026 - Production API",
        "version": "2.0.0",
        "docs": "/docs",
        "health": "/health",
        "metrics": "/metrics",
    }


@app.get("/ready", tags=["Health"])
async def readiness_check():
    """Readiness check for Kubernetes/load balancers."""
    # Add actual checks here (database, Redis, etc.)
    return {"status": "ready"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=os.getenv("ENVIRONMENT") == "development",
        log_level="info",
    )
