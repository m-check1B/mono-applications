"""
Learn by Kraliki - Main Application
Business-focused Learning Management System

Stack 2026: FastAPI + PostgreSQL
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import create_tables
from app.routers import (
    courses_router,
    progress_router,
    assessment_router,
    corporate_router,
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    if settings.debug:
        logger.warning(
            "DEBUG MODE ENABLED - This must be disabled in production! "
            "Set DEBUG=false in .env or environment variables."
        )
        await create_tables()
    else:
        logger.info("Starting in production mode (DEBUG=false)")

    yield
    # Shutdown
    pass


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Business-focused Learning Management System for Verduona",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(courses_router, prefix="/api")
app.include_router(progress_router, prefix="/api")
app.include_router(assessment_router, prefix="/api")
app.include_router(corporate_router, prefix="/api")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "running",
    }


@app.get("/health")
@app.get("/api/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )
