FROM python:3.12-slim

WORKDIR /app

# Install Node.js for Claude CLI
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Install Claude CLI globally
RUN npm install -g @anthropic-ai/claude-code

# Install uv and Python deps
RUN pip install --no-cache-dir uv

COPY pyproject.toml .
RUN uv pip install --system -e .

COPY app/ ./app/

# Create home dir for claude credentials
RUN mkdir -p /root/.claude

EXPOSE 8097

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8097"]
