# Speak by Kraliki - Backend Dockerfile
FROM python:3.13-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy platform packages first
COPY platform-packages/ /platform-packages/

# Install platform packages
RUN pip install --no-cache-dir /platform-packages/auth-core \
    && pip install --no-cache-dir /platform-packages/ai-core[gemini] \
    && pip install --no-cache-dir /platform-packages/voice-core \
    && pip install --no-cache-dir /platform-packages/telephony-core[telnyx] \
    && pip install --no-cache-dir /platform-packages/events-core[rabbitmq]

# Copy and install production requirements
COPY requirements-prod.txt .
RUN pip install --no-cache-dir -r requirements-prod.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
