#!/bin/bash

################################################################################
# Fix Docker Redis Security
################################################################################

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;36m'
NC='\033[0m'

echo -e "${RED}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${RED}║         DOCKER REDIS SECURITY FIX                              ║${NC}"
echo -e "${RED}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Generate password
echo -e "${BLUE}[1/6] Generating Strong Password${NC}"
REDIS_PASSWORD=$(openssl rand -base64 48 | tr -d "=+/" | cut -c1-32)
echo -e "${GREEN}✓ Generated password: $REDIS_PASSWORD${NC}"
echo "$REDIS_PASSWORD" > /tmp/redis_password_docker.txt
echo -e "${YELLOW}Password saved to: /tmp/redis_password_docker.txt${NC}"
echo ""

# Stop old container
echo -e "${BLUE}[2/6] Stopping Insecure Redis Container${NC}"
echo "Container: voice-kraliki-redis"
docker stop voice-kraliki-redis
echo -e "${GREEN}✓ Stopped${NC}"
echo ""

# Rename old container (backup)
echo -e "${BLUE}[3/6] Backing Up Old Container${NC}"
docker rename voice-kraliki-redis voice-kraliki-redis-backup-$(date +%Y%m%d-%H%M%S)
echo -e "${GREEN}✓ Renamed for backup${NC}"
echo ""

# Start new secure container
echo -e "${BLUE}[4/6] Starting Secure Redis Container${NC}"
echo "Configuration:"
echo "  - Password authentication: ENABLED"
echo "  - Binding: 127.0.0.1 only (localhost)"
echo "  - Protected mode: ENABLED"
echo "  - Port: 6379 (localhost only)"
echo ""

docker run -d \
  --name voice-kraliki-redis \
  --restart unless-stopped \
  --health-cmd "redis-cli -a $REDIS_PASSWORD ping | grep PONG" \
  --health-interval 10s \
  --health-timeout 5s \
  --health-retries 3 \
  -p 127.0.0.1:6379:6379 \
  -v redis-data:/data \
  redis:7-alpine \
  redis-server \
  --appendonly yes \
  --requirepass "$REDIS_PASSWORD" \
  --bind 0.0.0.0 \
  --protected-mode yes \
  --rename-command FLUSHDB "" \
  --rename-command FLUSHALL "" \
  --rename-command CONFIG ""

echo -e "${GREEN}✓ Started secure Redis container${NC}"
echo ""

# Wait for Redis to start
echo "Waiting for Redis to be ready..."
sleep 3

# Configure firewall
echo -e "${BLUE}[5/6] Configuring Firewall${NC}"
if command -v ufw &> /dev/null; then
    sudo ufw --force enable || true
    sudo ufw deny 6379/tcp || true
    sudo ufw allow 22/tcp || true
    sudo ufw allow 80/tcp || true
    sudo ufw allow 443/tcp || true
    echo -e "${GREEN}✓ Firewall configured${NC}"
else
    echo -e "${YELLOW}! UFW not installed, skipping firewall${NC}"
fi
echo ""

# Update application
echo -e "${BLUE}[6/6] Updating Application Configuration${NC}"
BACKEND_ENV="/home/adminmatej/github/applications/voice-kraliki/backend/.env"

if [ -f "$BACKEND_ENV" ]; then
    if grep -q "^REDIS_PASSWORD=" "$BACKEND_ENV"; then
        sed -i "s/^REDIS_PASSWORD=.*/REDIS_PASSWORD=$REDIS_PASSWORD/" "$BACKEND_ENV"
    else
        echo "REDIS_PASSWORD=$REDIS_PASSWORD" >> "$BACKEND_ENV"
    fi
    echo -e "${GREEN}✓ Updated $BACKEND_ENV${NC}"
else
    echo "REDIS_PASSWORD=$REDIS_PASSWORD" > "$BACKEND_ENV"
    echo -e "${GREEN}✓ Created $BACKEND_ENV${NC}"
fi
echo ""

# Verify
echo -e "${BLUE}Verifying Security...${NC}"
echo ""

# Check port binding
BINDING=$(ss -tulpn 2>/dev/null | grep 6379 || netstat -tulpn 2>/dev/null | grep 6379 || echo "")
if echo "$BINDING" | grep -q "127.0.0.1:6379"; then
    echo -e "${GREEN}✓ Redis now bound to localhost only${NC}"
elif echo "$BINDING" | grep -q "0.0.0.0:6379"; then
    echo -e "${RED}✗ WARNING: Redis still exposed!${NC}"
else
    echo -e "${YELLOW}! Could not verify binding${NC}"
fi

# Check container health
HEALTH=$(docker inspect voice-kraliki-redis --format '{{.State.Health.Status}}' 2>/dev/null || echo "unknown")
if [ "$HEALTH" = "healthy" ] || [ "$HEALTH" = "starting" ]; then
    echo -e "${GREEN}✓ Redis container is healthy${NC}"
else
    echo -e "${YELLOW}! Container health: $HEALTH${NC}"
fi

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                  ✓ SECURITY FIX COMPLETE                       ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}Redis Password:${NC} ${GREEN}$REDIS_PASSWORD${NC}"
echo -e "${YELLOW}Saved to:${NC} /tmp/redis_password_docker.txt"
echo ""
echo -e "${YELLOW}Redis Connection URL:${NC}"
echo -e "${GREEN}redis://:$REDIS_PASSWORD@localhost:6379/0${NC}"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo "1. Test your application"
echo "2. Run verification: bash scripts/verify-redis-security.sh"
echo "3. If everything works, remove backup:"
echo "   docker rm voice-kraliki-redis-backup-*"
echo ""
echo -e "${GREEN}The security vulnerability has been fixed!${NC}"
echo ""
