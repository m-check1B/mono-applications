#!/bin/bash
# Voice by Kraliki Docker Secrets Setup Script
# Automatically creates Docker secrets for production deployment
#
# Usage: ./scripts/setup-docker-secrets.sh [secrets-file]
#
# Security: This script reads secrets from a secure file and creates Docker secrets
# The secrets file should be outside the git repository and properly secured

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SECRETS_FILE="${1:-/secure/cc-lite-secrets.env}"
REQUIRED_SECRETS=(
    "JWT_SECRET"
    "JWT_REFRESH_SECRET"
    "COOKIE_SECRET"
    "SESSION_ENCRYPTION_KEY"
    "CSRF_SECRET"
    "DB_PASSWORD"
    "REDIS_PASSWORD"
    "RABBITMQ_PASSWORD"
    "WEBHOOK_SECRET"
    "MONITORING_AUTH_KEY"
    "AUTH_PRIVATE_KEY"
    "AUTH_PUBLIC_KEY"
)

echo -e "${BLUE}🔐 Voice by Kraliki Docker Secrets Setup${NC}"
echo -e "${BLUE}=================================${NC}"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker is not running or not accessible${NC}"
    exit 1
fi

# Check if running in Docker Swarm mode
if ! docker node ls > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Not in Docker Swarm mode. Initializing...${NC}"
    docker swarm init --advertise-addr 127.0.0.1 || true
fi

# Check if secrets file exists
if [[ ! -f "$SECRETS_FILE" ]]; then
    echo -e "${RED}❌ Secrets file not found: $SECRETS_FILE${NC}"
    echo -e "${YELLOW}💡 Create secrets file using: pnpm tsx scripts/gen-keys.ts > $SECRETS_FILE${NC}"
    echo -e "${YELLOW}💡 Then secure it: chmod 600 $SECRETS_FILE${NC}"
    exit 1
fi

# Source the secrets file
echo -e "${BLUE}📖 Loading secrets from: $SECRETS_FILE${NC}"
source "$SECRETS_FILE"

# Function to create or update Docker secret
create_docker_secret() {
    local secret_name="$1"
    local secret_value="$2"

    if [[ -z "$secret_value" ]]; then
        echo -e "${RED}❌ Secret $secret_name is empty${NC}"
        return 1
    fi

    # Check if secret already exists
    if docker secret ls --format "{{.Name}}" | grep -q "^${secret_name}$"; then
        echo -e "${YELLOW}🔄 Updating existing secret: $secret_name${NC}"
        # Docker secrets are immutable, so we need to remove and recreate
        # Create new version with timestamp
        local new_secret_name="${secret_name}_$(date +%s)"
        echo "$secret_value" | docker secret create "$new_secret_name" -
        echo -e "${GREEN}✅ Created versioned secret: $new_secret_name${NC}"
        echo -e "${YELLOW}⚠️  Update your docker-compose.yml to use: $new_secret_name${NC}"
    else
        echo -e "${BLUE}🆕 Creating new secret: $secret_name${NC}"
        echo "$secret_value" | docker secret create "$secret_name" -
        echo -e "${GREEN}✅ Created secret: $secret_name${NC}"
    fi
}

# Create all required secrets
echo -e "\n${BLUE}🔑 Creating Docker secrets...${NC}"

# Authentication secrets
create_docker_secret "jwt_secret" "$JWT_SECRET"
create_docker_secret "jwt_refresh_secret" "$JWT_REFRESH_SECRET"
create_docker_secret "cookie_secret" "$COOKIE_SECRET"
create_docker_secret "session_encryption_key" "$SESSION_ENCRYPTION_KEY"
create_docker_secret "csrf_secret" "$CSRF_SECRET"

# Database secrets
create_docker_secret "db_password" "$DB_PASSWORD"
create_docker_secret "redis_password" "$REDIS_PASSWORD"
create_docker_secret "rabbitmq_password" "$RABBITMQ_PASSWORD"

# API secrets
create_docker_secret "webhook_secret" "$WEBHOOK_SECRET"
create_docker_secret "monitoring_auth_key" "$MONITORING_AUTH_KEY"

# Ed25519 keys (handle multiline)
create_docker_secret "auth_private_key" "$AUTH_PRIVATE_KEY"
create_docker_secret "auth_public_key" "$AUTH_PUBLIC_KEY"

# Optional API keys (if provided)
if [[ -n "${OPENAI_API_KEY:-}" ]]; then
    create_docker_secret "openai_api_key" "$OPENAI_API_KEY"
fi

if [[ -n "${ANTHROPIC_API_KEY:-}" ]]; then
    create_docker_secret "anthropic_api_key" "$ANTHROPIC_API_KEY"
fi

if [[ -n "${TWILIO_AUTH_TOKEN:-}" ]]; then
    create_docker_secret "twilio_auth_token" "$TWILIO_AUTH_TOKEN"
fi

if [[ -n "${LINEAR_API_KEY:-}" ]]; then
    create_docker_secret "linear_api_key" "$LINEAR_API_KEY"
fi

# List all created secrets
echo -e "\n${BLUE}📋 Docker secrets summary:${NC}"
docker secret ls --format "table {{.Name}}\t{{.CreatedAt}}\t{{.UpdatedAt}}"

# Generate docker-compose secrets section
echo -e "\n${BLUE}🐳 Docker Compose secrets configuration:${NC}"
cat << 'EOF'

# Add this to your docker-compose.production.yml:
secrets:
  jwt_secret:
    external: true
  jwt_refresh_secret:
    external: true
  cookie_secret:
    external: true
  session_encryption_key:
    external: true
  csrf_secret:
    external: true
  db_password:
    external: true
  redis_password:
    external: true
  rabbitmq_password:
    external: true
  webhook_secret:
    external: true
  monitoring_auth_key:
    external: true
  auth_private_key:
    external: true
  auth_public_key:
    external: true

# In your service definition:
services:
  app:
    secrets:
      - jwt_secret
      - jwt_refresh_secret
      - cookie_secret
      - session_encryption_key
      - csrf_secret
      - db_password
      - redis_password
      - rabbitmq_password
      - webhook_secret
      - monitoring_auth_key
      - auth_private_key
      - auth_public_key
    environment:
      - JWT_SECRET_FILE=/run/secrets/jwt_secret
      - JWT_REFRESH_SECRET_FILE=/run/secrets/jwt_refresh_secret
      - COOKIE_SECRET_FILE=/run/secrets/cookie_secret
      # ... etc
EOF

echo -e "\n${GREEN}🎉 Docker secrets setup completed successfully!${NC}"
echo -e "${BLUE}📝 Next steps:${NC}"
echo -e "  1. Update docker-compose.production.yml with secrets configuration"
echo -e "  2. Modify application to read secrets from /run/secrets/ files"
echo -e "  3. Test the deployment with: docker stack deploy -c docker-compose.production.yml cc-lite"
echo -e "  4. Monitor secrets usage and rotate regularly"

echo -e "\n${YELLOW}🔒 Security reminders:${NC}"
echo -e "  ✓ Secrets file permissions: $(ls -la "$SECRETS_FILE" | awk '{print $1, $3, $4}')"
echo -e "  ✓ Remove secrets file after setup: rm $SECRETS_FILE"
echo -e "  ✓ Rotate secrets every 90 days"
echo -e "  ✓ Monitor secret access logs"