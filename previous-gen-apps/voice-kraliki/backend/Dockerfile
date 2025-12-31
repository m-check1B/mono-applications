# syntax=docker/dockerfile:1

# Production image - Python 3.12 slim
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install uv for fast package management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy and filter requirements (exclude local -e packages)
COPY requirements.txt ./
RUN grep -v "^-e" requirements.txt > requirements-docker.txt || true

# Install dependencies using uv
RUN uv pip install --system -r requirements-docker.txt

# Copy application code
COPY app ./app

# Create non-root user for security and create keys directory
RUN useradd -m -u 1000 appuser && \
    mkdir -p /app/keys && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port 8000
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=5 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

# Run the application using python module
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
