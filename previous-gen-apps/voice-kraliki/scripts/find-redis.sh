#!/bin/bash

################################################################################
# Find Redis Installation Script
#
# This script helps locate where Redis is installed and running
################################################################################

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${YELLOW}========================================${NC}"
echo -e "${YELLOW}Finding Redis Installation${NC}"
echo -e "${YELLOW}========================================${NC}"
echo ""

# Check if Redis process is running
echo -e "${BLUE}[1] Checking if Redis is running...${NC}"
REDIS_PS=$(ps aux | grep redis-server | grep -v grep)
if [ -n "$REDIS_PS" ]; then
    echo -e "${GREEN}✓ Redis is running${NC}"
    echo "$REDIS_PS"
    REDIS_USER=$(echo "$REDIS_PS" | awk '{print $1}')
    echo -e "  Running as user: ${YELLOW}${REDIS_USER}${NC}"
else
    echo -e "${RED}✗ Redis is not running${NC}"
    exit 1
fi
echo ""

# Check port binding
echo -e "${BLUE}[2] Checking port binding...${NC}"
BINDING=$(ss -tulpn 2>/dev/null | grep 6379 || netstat -tulpn 2>/dev/null | grep 6379 || echo "")
if [ -n "$BINDING" ]; then
    echo "$BINDING"
    if echo "$BINDING" | grep -q "0.0.0.0:6379"; then
        echo -e "${RED}⚠ WARNING: Redis is bound to ALL interfaces (0.0.0.0) - VULNERABLE!${NC}"
    elif echo "$BINDING" | grep -q "127.0.0.1:6379"; then
        echo -e "${GREEN}✓ Redis is bound to localhost only${NC}"
    fi
else
    echo -e "${YELLOW}! Could not determine binding${NC}"
fi
echo ""

# Check if Docker
echo -e "${BLUE}[3] Checking if Redis is in Docker...${NC}"
if command -v docker &> /dev/null; then
    DOCKER_REDIS=$(sudo docker ps 2>/dev/null | grep redis || echo "")
    if [ -n "$DOCKER_REDIS" ]; then
        echo -e "${GREEN}✓ Found Redis in Docker:${NC}"
        echo "$DOCKER_REDIS"
        CONTAINER_ID=$(echo "$DOCKER_REDIS" | awk '{print $1}')
        echo ""
        echo "Docker container ID: ${YELLOW}${CONTAINER_ID}${NC}"
        echo ""
        echo "To fix Redis in Docker:"
        echo "  1. Stop container: sudo docker stop $CONTAINER_ID"
        echo "  2. See: scripts/MANUAL_REDIS_FIX.md (Section 2a)"
    else
        echo "  No Redis found in Docker"
    fi
else
    echo "  Docker not installed"
fi
echo ""

# Check if LXD/LXC
echo -e "${BLUE}[4] Checking if Redis is in LXD/LXC...${NC}"
if [ "$REDIS_USER" = "lxd" ] || [ "$REDIS_USER" = "lxc" ]; then
    echo -e "${YELLOW}✓ Redis is running as ${REDIS_USER} user (likely in container)${NC}"

    if command -v lxc &> /dev/null; then
        echo "  Listing LXD containers:"
        sudo lxc list 2>/dev/null || echo "  Cannot list containers (need sudo)"
        echo ""
        echo "To fix Redis in LXD:"
        echo "  1. Find container: sudo lxc list"
        echo "  2. Enter container: sudo lxc exec <container-name> -- bash"
        echo "  3. See: scripts/MANUAL_REDIS_FIX.md (Section 2b)"
    else
        echo "  LXD tools not available"
    fi
else
    echo "  Not running as lxd/lxc user"
fi
echo ""

# Check if Snap
echo -e "${BLUE}[5] Checking if Redis is a Snap package...${NC}"
if command -v snap &> /dev/null; then
    SNAP_REDIS=$(snap list 2>/dev/null | grep redis || echo "")
    if [ -n "$SNAP_REDIS" ]; then
        echo -e "${GREEN}✓ Found Redis as Snap:${NC}"
        echo "$SNAP_REDIS"
        echo ""
        echo "Snap config location:"
        echo "  /var/snap/redis/common/"
    else
        echo "  No Redis snap found"
    fi
else
    echo "  Snap not installed"
fi
echo ""

# Look for config files
echo -e "${BLUE}[6] Looking for Redis config files...${NC}"
echo "  Searching common locations..."

CONFIG_FOUND=0

# Check common locations first (fast)
for path in "/etc/redis/redis.conf" "/etc/redis.conf" "/usr/local/etc/redis.conf" "/opt/redis/redis.conf"; do
    if [ -f "$path" ]; then
        echo -e "${GREEN}✓ Found: $path${NC}"
        CONFIG_FOUND=1
    fi
done

# If not found, search (slower)
if [ $CONFIG_FOUND -eq 0 ]; then
    echo "  Doing deeper search (this may take a minute)..."
    CONFIGS=$(sudo find /etc /var /opt /usr/local -name "redis*.conf" -type f 2>/dev/null | head -5)
    if [ -n "$CONFIGS" ]; then
        echo -e "${GREEN}✓ Found config files:${NC}"
        echo "$CONFIGS"
    else
        echo -e "${YELLOW}! No config files found in standard locations${NC}"
    fi
fi
echo ""

# Check systemd service
echo -e "${BLUE}[7] Checking if Redis is a systemd service...${NC}"
if systemctl list-units --all 2>/dev/null | grep -q redis; then
    echo -e "${GREEN}✓ Redis systemd service found${NC}"
    sudo systemctl status redis 2>/dev/null || sudo systemctl status redis-server 2>/dev/null || echo "  Cannot get status"
    echo ""
    echo "To restart: sudo systemctl restart redis-server"
else
    echo "  No systemd service found"
fi
echo ""

# Summary
echo -e "${YELLOW}========================================${NC}"
echo -e "${YELLOW}SUMMARY${NC}"
echo -e "${YELLOW}========================================${NC}"
echo ""

if [ "$REDIS_USER" = "lxd" ] || [ "$REDIS_USER" = "lxc" ]; then
    echo -e "${YELLOW}Redis appears to be running in an LXD/LXC container${NC}"
    echo ""
    echo "NEXT STEPS:"
    echo "  1. Read: scripts/MANUAL_REDIS_FIX.md"
    echo "  2. Run: sudo lxc list"
    echo "  3. Enter container: sudo lxc exec <container-name> -- bash"
    echo "  4. Find config inside container: find /etc -name redis.conf"
    echo "  5. Edit config and restart Redis"
    echo ""
elif [ -n "$DOCKER_REDIS" ]; then
    echo -e "${YELLOW}Redis is running in Docker container${NC}"
    echo ""
    echo "NEXT STEPS:"
    echo "  1. Read: scripts/MANUAL_REDIS_FIX.md (Section 2a)"
    echo "  2. Update docker-compose.yml or docker run command"
    echo "  3. Restart container with secure configuration"
    echo ""
elif [ $CONFIG_FOUND -eq 1 ]; then
    echo -e "${YELLOW}Redis is installed as system service${NC}"
    echo ""
    echo "NEXT STEPS:"
    echo "  1. Edit config file (found above)"
    echo "  2. Change: bind 0.0.0.0 → bind 127.0.0.1"
    echo "  3. Add: requirepass <strong-password>"
    echo "  4. Add: protected-mode yes"
    echo "  5. Restart: sudo systemctl restart redis-server"
    echo "  6. See: scripts/MANUAL_REDIS_FIX.md for details"
    echo ""
else
    echo -e "${RED}Could not determine Redis installation type${NC}"
    echo ""
    echo "NEXT STEPS:"
    echo "  1. Read: scripts/MANUAL_REDIS_FIX.md"
    echo "  2. Manually locate Redis installation"
    echo "  3. Contact system administrator if needed"
    echo ""
fi

echo -e "${RED}CRITICAL: Redis is currently VULNERABLE${NC}"
echo -e "${RED}Fix immediately to secure your data!${NC}"
echo ""
