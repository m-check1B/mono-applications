# Multi-stage build for optimized production image

# Production stage
FROM python:3.13-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy and filter requirements (exclude local -e packages)
COPY requirements.txt .
RUN grep -v "^-e" requirements.txt > requirements-docker.txt || true

# Install Python dependencies system-wide
RUN pip install --no-cache-dir -r requirements-docker.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 3017

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:3017/health', timeout=5)"

# Run the application - listen on all interfaces within container
# Container port is not exposed to host (no port mapping), only to docker network
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "3017"]
