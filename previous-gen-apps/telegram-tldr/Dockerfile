# TL;DR Bot Dockerfile
# Production-ready multi-stage build with uv

FROM python:3.11-slim AS builder

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies with uv (no dev deps)
RUN uv sync --frozen --no-dev --no-install-project

# Copy application code
COPY app/ ./app/

# Production stage
FROM python:3.11-slim AS production

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Copy application code
COPY --from=builder /app/app ./app

# Copy entrypoint script
COPY docker-entrypoint.sh /app/docker-entrypoint.sh

# Set environment
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app"
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Non-root user for security
RUN chmod +x /app/docker-entrypoint.sh && \
    useradd --create-home --shell /bin/bash appuser && \
    chown -R appuser:appuser /app
USER appuser

# Entrypoint validates environment and starts uvicorn
# (0.0.0.0 inside container is safe - external access controlled by docker-compose)
ENTRYPOINT ["/app/docker-entrypoint.sh"]
CMD []
