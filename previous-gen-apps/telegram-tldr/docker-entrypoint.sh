#!/bin/bash
# TL;DR Bot Docker Entrypoint
# Validates required environment variables and starts the webhook server

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting TL;DR Bot...${NC}"

# Check required environment variables
MISSING_VARS=()

if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
    MISSING_VARS+=("TELEGRAM_BOT_TOKEN")
fi

if [ -z "$GEMINI_API_KEY" ]; then
    MISSING_VARS+=("GEMINI_API_KEY")
fi

if [ -z "$TELEGRAM_WEBHOOK_URL" ]; then
    echo -e "${YELLOW}WARNING: TELEGRAM_WEBHOOK_URL not set - bot won't receive updates${NC}"
fi

if [ -n "$TELEGRAM_WEBHOOK_URL" ] && [ -z "$TELEGRAM_WEBHOOK_SECRET" ]; then
    MISSING_VARS+=("TELEGRAM_WEBHOOK_SECRET (required when using webhooks)")
fi

# Exit if missing required variables
if [ ${#MISSING_VARS[@]} -gt 0 ]; then
    echo -e "${RED}ERROR: Missing required environment variables:${NC}"
    for var in "${MISSING_VARS[@]}"; do
        echo -e "  - $var"
    done
    echo ""
    echo "Please configure these in your .env file or docker-compose environment."
    echo "See .env.example for reference."
    exit 1
fi

# Redis connectivity check (optional but helpful)
if [ -n "$REDIS_URL" ]; then
    echo -e "${GREEN}Redis URL: ${REDIS_URL}${NC}"
fi

echo -e "${GREEN}Webhook URL: ${TELEGRAM_WEBHOOK_URL:-NOT SET}${NC}"
echo -e "${GREEN}Starting uvicorn server on port 8000...${NC}"

# Start uvicorn
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 "$@"
