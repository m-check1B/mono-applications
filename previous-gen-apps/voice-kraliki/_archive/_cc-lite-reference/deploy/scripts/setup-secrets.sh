#!/bin/bash
# Voice by Kraliki Docker Secrets Setup Script
# =====================================
# This script creates Docker secrets for production deployment
# Run this BEFORE starting the Docker Compose stack

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SECRETS_DIR="${SECRETS_DIR:-/tmp/cc-lite-secrets}"
ENV_FILE="${ENV_FILE:-/home/adminmatej/github/apps/cc-lite/.env.production}"

echo -e "${BLUE}🔐 Voice by Kraliki Docker Secrets Setup${NC}"
echo "================================"

# Function to generate secure random string
generate_secret() {
    local length=${1:-32}
    openssl rand -base64 $length | tr -d '\n'
}

# Function to create Docker secret
create_secret() {
    local secret_name=$1
    local secret_value=$2

    if docker secret ls --format "{{.Name}}" | grep -q "^${secret_name}$"; then
        echo -e "${YELLOW}⚠️  Secret '${secret_name}' already exists, skipping...${NC}"
        return 0
    fi

    echo "$secret_value" | docker secret create "$secret_name" - 2>/dev/null
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Created secret: ${secret_name}${NC}"
    else
        echo -e "${RED}❌ Failed to create secret: ${secret_name}${NC}"
        return 1
    fi
}

# Function to prompt for secret value
prompt_secret() {
    local secret_name=$1
    local description=$2
    local default_value=$3

    echo -e "${BLUE}📝 ${description}${NC}"
    if [ -n "$default_value" ]; then
        echo -e "${YELLOW}   Default: [Auto-generated secure value]${NC}"
        echo -n "   Enter value (or press Enter for auto-generated): "
    else
        echo -n "   Enter value: "
    fi

    read -s input_value
    echo

    if [ -z "$input_value" ] && [ -n "$default_value" ]; then
        echo "$default_value"
    else
        echo "$input_value"
    fi
}

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    echo -e "${RED}❌ Docker is not running or not accessible${NC}"
    echo "Please start Docker and ensure your user has permission to access it"
    exit 1
fi

# Check if Docker Swarm is initialized (required for secrets)
if ! docker node ls >/dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Docker Swarm not initialized. Initializing...${NC}"
    docker swarm init --advertise-addr 127.0.0.1 2>/dev/null || {
        echo -e "${RED}❌ Failed to initialize Docker Swarm${NC}"
        exit 1
    }
    echo -e "${GREEN}✅ Docker Swarm initialized${NC}"
fi

# Create secrets directory
mkdir -p "$SECRETS_DIR"

echo -e "${BLUE}🔧 Creating Docker secrets for Voice by Kraliki...${NC}"
echo

# JWT Secrets
echo -e "${YELLOW}🔑 JWT Authentication Secrets${NC}"
JWT_SECRET=$(prompt_secret "cc_lite_jwt_secret" "JWT Secret (for access tokens)" "$(generate_secret 64)")
JWT_REFRESH_SECRET=$(prompt_secret "cc_lite_jwt_refresh_secret" "JWT Refresh Secret (for refresh tokens)" "$(generate_secret 64)")

create_secret "cc_lite_jwt_secret" "$JWT_SECRET"
create_secret "cc_lite_jwt_refresh_secret" "$JWT_REFRESH_SECRET"

# Database Password
echo -e "${YELLOW}🗄️  Database Secrets${NC}"
DB_PASSWORD=$(prompt_secret "cc_lite_db_password" "PostgreSQL Database Password" "$(generate_secret 32)")
create_secret "cc_lite_db_password" "$DB_PASSWORD"

# Redis Password
echo -e "${YELLOW}📦 Redis Cache Secrets${NC}"
REDIS_PASSWORD=$(prompt_secret "cc_lite_redis_password" "Redis Password" "$(generate_secret 32)")
create_secret "cc_lite_redis_password" "$REDIS_PASSWORD"

# Session and Cookie Secrets
echo -e "${YELLOW}🍪 Session Management Secrets${NC}"
SESSION_SECRET=$(prompt_secret "cc_lite_session_secret" "Session Secret" "$(generate_secret 64)")
COOKIE_SECRET=$(prompt_secret "cc_lite_cookie_secret" "Cookie Secret" "$(generate_secret 32)")

create_secret "cc_lite_session_secret" "$SESSION_SECRET"
create_secret "cc_lite_cookie_secret" "$COOKIE_SECRET"

# External API Keys
echo -e "${YELLOW}🌐 External API Keys${NC}"
TWILIO_AUTH_TOKEN=$(prompt_secret "cc_lite_twilio_auth_token" "Twilio Auth Token" "")
OPENAI_API_KEY=$(prompt_secret "cc_lite_openai_api_key" "OpenAI API Key" "")
DEEPGRAM_API_KEY=$(prompt_secret "cc_lite_deepgram_api_key" "Deepgram API Key" "")

if [ -n "$TWILIO_AUTH_TOKEN" ]; then
    create_secret "cc_lite_twilio_auth_token" "$TWILIO_AUTH_TOKEN"
fi

if [ -n "$OPENAI_API_KEY" ]; then
    create_secret "cc_lite_openai_api_key" "$OPENAI_API_KEY"
fi

if [ -n "$DEEPGRAM_API_KEY" ]; then
    create_secret "cc_lite_deepgram_api_key" "$DEEPGRAM_API_KEY"
fi

echo
echo -e "${GREEN}✅ All secrets created successfully!${NC}"
echo

# Generate environment template
echo -e "${BLUE}📝 Generating production environment template...${NC}"

cat > "${SECRETS_DIR}/production.env.template" << EOF
# Voice by Kraliki Production Environment Configuration
# ============================================
# Generated on: $(date)
#
# SECURITY NOTICE:
# - All sensitive data is stored in Docker secrets
# - This file contains only non-sensitive configuration
# - Never commit this file with actual values to version control

# Application Configuration
NODE_ENV=production
PORT=3010
FRONTEND_PORT=3007
CORS_ORIGIN=https://cc-lite.yourdomain.com

# Database Configuration (connection details only, password in secrets)
DATABASE_URL=postgresql://cc_lite_user@postgres:5432/cc_light_prod?schema=public

# Redis Configuration (connection details only, password in secrets)
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_URL=redis://redis:6379

# Telephony Configuration
TELEPHONY_ENABLED=true
TELEPHONY_PROVIDER=twilio
TWILIO_ACCOUNT_SID=your_account_sid_here
TWILIO_PHONE_NUMBER=+1234567890
WEBHOOK_BASE_URL=https://cc-lite.yourdomain.com

# Multi-Language Support
ENABLE_LANGUAGE_DETECTION=true
DEFAULT_LANGUAGE=en
SUPPORTED_LANGUAGES=en,es,cs
CZECH_LANGUAGE_ENABLED=true
SPANISH_LANGUAGE_ENABLED=true
ENGLISH_LANGUAGE_ENABLED=true

# Monitoring and Logging
LOG_LEVEL=info
LOG_FORMAT=json
METRICS_ENABLED=true
TRACING_ENABLED=true
HEALTH_CHECK_ENABLED=true

# Security
SEED_DEMO_USERS=false
ENABLE_DEBUG_LOGGING=false
RATE_LIMIT_ENABLED=true
RATE_LIMIT_WINDOW_MS=900000
RATE_LIMIT_MAX_REQUESTS=100

# Stack 2025 Bug Reporting
LINEAR_API_KEY=your_linear_api_key_here
LINEAR_TEAM_ID=your_linear_team_id_here
APP_ENV=production

# Optional: Monitoring Services
SENTRY_DSN=your_sentry_dsn_here
GRAFANA_DOMAIN=localhost

# Backup Configuration
BACKUP_RETENTION_DAYS=30

# Build Information (set during deployment)
BUILDTIME=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
GIT_COMMIT=\${GIT_COMMIT:-unknown}
IMAGE_TAG=\${IMAGE_TAG:-latest}
EOF

echo -e "${GREEN}✅ Environment template created at: ${SECRETS_DIR}/production.env.template${NC}"

# Create secrets summary
echo -e "${BLUE}📋 Creating secrets summary...${NC}"

cat > "${SECRETS_DIR}/secrets-summary.txt" << EOF
Voice by Kraliki Docker Secrets Summary
==============================
Created on: $(date)

Docker Secrets Created:
- cc_lite_jwt_secret: JWT access token signing key
- cc_lite_jwt_refresh_secret: JWT refresh token signing key
- cc_lite_db_password: PostgreSQL database password
- cc_lite_redis_password: Redis cache password
- cc_lite_session_secret: Session management secret
- cc_lite_cookie_secret: Cookie signing secret
EOF

if [ -n "$TWILIO_AUTH_TOKEN" ]; then
    echo "- cc_lite_twilio_auth_token: Twilio API authentication token" >> "${SECRETS_DIR}/secrets-summary.txt"
fi

if [ -n "$OPENAI_API_KEY" ]; then
    echo "- cc_lite_openai_api_key: OpenAI API key for AI features" >> "${SECRETS_DIR}/secrets-summary.txt"
fi

if [ -n "$DEEPGRAM_API_KEY" ]; then
    echo "- cc_lite_deepgram_api_key: Deepgram API key for speech processing" >> "${SECRETS_DIR}/secrets-summary.txt"
fi

cat >> "${SECRETS_DIR}/secrets-summary.txt" << EOF

Next Steps:
1. Review and customize the production.env.template file
2. Copy it to .env.production in your project root
3. Create required directories: mkdir -p /opt/cc-lite/{data,logs,backups,cache,uploads}/{postgres,redis,app,nginx,prometheus,grafana,loki}
4. Start the Docker Compose stack: docker compose -f infra/docker/production.yml up -d

Security Reminders:
- Never commit secret values to version control
- Regularly rotate secrets (especially API keys)
- Monitor secret access via Docker audit logs
- Use different secrets for staging and production environments

For secret rotation, run this script again or use:
docker secret rm <secret_name>
echo "new_value" | docker secret create <secret_name> -
EOF

echo -e "${GREEN}✅ Secrets summary created at: ${SECRETS_DIR}/secrets-summary.txt${NC}"

# List created secrets
echo
echo -e "${BLUE}📋 Created Docker secrets:${NC}"
docker secret ls --format "table {{.Name}}\t{{.CreatedAt}}" | grep cc_lite

echo
echo -e "${GREEN}🎉 Docker secrets setup completed successfully!${NC}"
echo -e "${YELLOW}📁 Files created in: ${SECRETS_DIR}${NC}"
echo -e "${YELLOW}📖 Next: Review the production.env.template and create your .env.production file${NC}"
echo -e "${YELLOW}🚀 Then: Run 'docker compose -f infra/docker/production.yml up -d'${NC}"
echo
echo -e "${RED}⚠️  IMPORTANT: Keep the generated secrets secure and never commit them to version control!${NC}"