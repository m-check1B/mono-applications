#!/bin/bash

################################################################################
# Redis Security Fix Script
#
# This script secures Redis by:
# 1. Binding to localhost only
# 2. Requiring authentication
# 3. Disabling dangerous commands
# 4. Enabling protected mode
#
# Run with: sudo bash fix-redis-security.sh
################################################################################

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}========================================${NC}"
echo -e "${YELLOW}Redis Security Fix Script${NC}"
echo -e "${YELLOW}========================================${NC}"
echo ""

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo -e "${RED}ERROR: This script must be run as root (use sudo)${NC}"
   exit 1
fi

# Find Redis config file
echo -e "${YELLOW}[1/6] Finding Redis configuration...${NC}"
REDIS_CONF=""
if [ -f "/etc/redis/redis.conf" ]; then
    REDIS_CONF="/etc/redis/redis.conf"
elif [ -f "/etc/redis.conf" ]; then
    REDIS_CONF="/etc/redis.conf"
else
    echo -e "${RED}ERROR: Redis config file not found!${NC}"
    echo "Please locate your redis.conf file and edit manually."
    exit 1
fi

echo -e "${GREEN}✓ Found: $REDIS_CONF${NC}"

# Backup original config
echo -e "${YELLOW}[2/6] Backing up original configuration...${NC}"
cp "$REDIS_CONF" "$REDIS_CONF.backup.$(date +%Y%m%d_%H%M%S)"
echo -e "${GREEN}✓ Backup created${NC}"

# Generate strong password
echo -e "${YELLOW}[3/6] Generating strong Redis password...${NC}"
REDIS_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-32)
echo -e "${GREEN}✓ Password generated${NC}"
echo -e "${YELLOW}IMPORTANT: Save this password - you'll need it to connect!${NC}"
echo -e "${GREEN}Redis Password: ${REDIS_PASSWORD}${NC}"
echo ""
echo "Add this to your .env file:"
echo "REDIS_PASSWORD=${REDIS_PASSWORD}"
echo ""

# Configure Redis
echo -e "${YELLOW}[4/6] Updating Redis configuration...${NC}"

# 1. Bind to localhost only
sed -i 's/^bind .*/bind 127.0.0.1 ::1/' "$REDIS_CONF"
if ! grep -q "^bind 127.0.0.1" "$REDIS_CONF"; then
    echo "bind 127.0.0.1 ::1" >> "$REDIS_CONF"
fi

# 2. Add password
sed -i "s/^# requirepass .*/requirepass $REDIS_PASSWORD/" "$REDIS_CONF"
if ! grep -q "^requirepass" "$REDIS_CONF"; then
    echo "requirepass $REDIS_PASSWORD" >> "$REDIS_CONF"
fi

# 3. Enable protected mode
sed -i 's/^protected-mode no/protected-mode yes/' "$REDIS_CONF"
if ! grep -q "^protected-mode yes" "$REDIS_CONF"; then
    echo "protected-mode yes" >> "$REDIS_CONF"
fi

# 4. Disable dangerous commands
echo "" >> "$REDIS_CONF"
echo "# Disabled dangerous commands for security" >> "$REDIS_CONF"
echo 'rename-command FLUSHDB ""' >> "$REDIS_CONF"
echo 'rename-command FLUSHALL ""' >> "$REDIS_CONF"
echo 'rename-command CONFIG ""' >> "$REDIS_CONF"
echo 'rename-command SHUTDOWN ""' >> "$REDIS_CONF"
echo 'rename-command BGREWRITEAOF ""' >> "$REDIS_CONF"
echo 'rename-command BGSAVE ""' >> "$REDIS_CONF"
echo 'rename-command SAVE ""' >> "$REDIS_CONF"
echo 'rename-command DEBUG ""' >> "$REDIS_CONF"

echo -e "${GREEN}✓ Configuration updated${NC}"

# Restart Redis
echo -e "${YELLOW}[5/6] Restarting Redis...${NC}"
if systemctl restart redis-server 2>/dev/null || systemctl restart redis 2>/dev/null; then
    echo -e "${GREEN}✓ Redis restarted${NC}"
else
    echo -e "${RED}WARNING: Could not restart Redis automatically${NC}"
    echo "Please restart Redis manually:"
    echo "  sudo systemctl restart redis-server"
    echo "  OR"
    echo "  sudo systemctl restart redis"
fi

# Verify security
echo -e "${YELLOW}[6/6] Verifying security...${NC}"
sleep 2

# Check binding
BINDING=$(ss -tulpn 2>/dev/null | grep 6379 || netstat -tulpn 2>/dev/null | grep 6379 || echo "")
if echo "$BINDING" | grep -q "127.0.0.1:6379"; then
    echo -e "${GREEN}✓ Redis is bound to localhost only${NC}"
elif echo "$BINDING" | grep -q "0.0.0.0:6379"; then
    echo -e "${RED}✗ WARNING: Redis is still bound to all interfaces!${NC}"
    echo "Please check your configuration and restart Redis."
else
    echo -e "${YELLOW}! Could not verify binding (Redis may not be running)${NC}"
fi

# Check authentication
if command -v redis-cli &> /dev/null; then
    if redis-cli ping 2>&1 | grep -q "NOAUTH"; then
        echo -e "${GREEN}✓ Authentication is required${NC}"
    elif redis-cli -a "$REDIS_PASSWORD" ping 2>&1 | grep -q "PONG"; then
        echo -e "${GREEN}✓ Authentication is working${NC}"
    else
        echo -e "${YELLOW}! Could not verify authentication${NC}"
    fi
else
    echo -e "${YELLOW}! redis-cli not found, skipping auth check${NC}"
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Security Fix Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "IMPORTANT NEXT STEPS:"
echo ""
echo "1. Save the Redis password to your .env file:"
echo "   echo 'REDIS_PASSWORD=${REDIS_PASSWORD}' >> /home/adminmatej/github/applications/voice-kraliki/backend/.env"
echo ""
echo "2. Update your application to use authentication:"
echo "   Redis URL: redis://:${REDIS_PASSWORD}@localhost:6379/0"
echo ""
echo "3. Verify Redis is secure:"
echo "   bash /home/adminmatej/github/applications/voice-kraliki/scripts/verify-redis-security.sh"
echo ""
echo "4. Test your application still works with the new password"
echo ""
echo "5. Check firewall rules:"
echo "   sudo ufw status"
echo "   sudo ufw deny 6379/tcp  # Block Redis port from external access"
echo ""
echo -e "${YELLOW}Original config backed up to: $REDIS_CONF.backup.*${NC}"
echo ""
