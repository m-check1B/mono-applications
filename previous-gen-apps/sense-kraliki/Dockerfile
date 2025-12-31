# Sense by Kraliki Bot Dockerfile
# Production-ready multi-stage build with uv

FROM python:3.11-slim AS builder

# Install uv and build dependencies for pyswisseph
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

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

# Set environment
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Non-root user for security
RUN useradd --create-home --shell /bin/bash appuser && \
    chown -R appuser:appuser /app
USER appuser

# Run the bot
CMD ["python", "-m", "app.main"]
