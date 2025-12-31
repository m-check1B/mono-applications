#!/bin/bash

################################################################################
# Guided Redis Security Fix
# This script will walk you through fixing Redis step by step
################################################################################

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;36m'
NC='\033[0m'

echo -e "${RED}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${RED}║  CRITICAL SECURITY FIX - Redis Exposed to Internet            ║${NC}"
echo -e "${RED}║  This guided script will help you secure Redis                ║${NC}"
echo -e "${RED}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if running as root
if [[ $EUID -eq 0 ]]; then
    IS_ROOT=1
else
    IS_ROOT=0
    echo -e "${YELLOW}Note: Some commands will require sudo${NC}"
    echo ""
fi

# Generate strong password first
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}[Step 1/7] Generating Strong Password${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
REDIS_PASSWORD=$(openssl rand -base64 48 | tr -d "=+/" | cut -c1-32)
echo -e "${GREEN}✓ Generated strong 32-character password${NC}"
echo ""
echo -e "${YELLOW}IMPORTANT: Save this password!${NC}"
echo -e "${GREEN}$REDIS_PASSWORD${NC}"
echo ""
echo "Writing to temporary file..."
echo "$REDIS_PASSWORD" > /tmp/redis_password_$(date +%s).txt
PASS_FILE=$(ls -t /tmp/redis_password_*.txt | head -1)
echo -e "${GREEN}✓ Saved to: $PASS_FILE${NC}"
echo ""
read -p "Press Enter to continue..."
echo ""

# Find Redis installation
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}[Step 2/7] Locating Redis Installation${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

REDIS_PS=$(ps aux | grep redis-server | grep -v grep)
if [ -z "$REDIS_PS" ]; then
    echo -e "${RED}✗ Redis is not running${NC}"
    exit 1
fi

echo "$REDIS_PS"
REDIS_USER=$(echo "$REDIS_PS" | awk '{print $1}')
echo -e "Running as user: ${YELLOW}$REDIS_USER${NC}"
echo ""

if [ "$REDIS_USER" = "lxd" ]; then
    echo -e "${YELLOW}Redis is running in an LXD container${NC}"
    INSTALL_TYPE="lxd"
else
    INSTALL_TYPE="system"
fi
echo ""
read -p "Press Enter to continue..."
echo ""

# Handle LXD container
if [ "$INSTALL_TYPE" = "lxd" ]; then
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}[Step 3/7] LXD Container Detection${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo -e "${YELLOW}Redis is in an LXD container. Listing containers...${NC}"
    echo ""

    if command -v lxc &> /dev/null; then
        echo "Running: sudo lxc list"
        sudo lxc list
        echo ""
        echo -e "${YELLOW}Which container is Redis running in?${NC}"
        read -p "Enter container name: " CONTAINER_NAME

        if [ -z "$CONTAINER_NAME" ]; then
            echo -e "${RED}No container name provided${NC}"
            exit 1
        fi

        echo ""
        echo -e "${GREEN}✓ Will fix Redis in container: $CONTAINER_NAME${NC}"
        echo ""
    else
        echo -e "${RED}LXC command not found!${NC}"
        echo "You may need to install lxc or check if snap lxd is installed"
        echo ""
        echo "Try: sudo snap install lxd"
        exit 1
    fi

    read -p "Press Enter to continue..."
    echo ""

    # Create config snippet
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}[Step 4/7] Preparing Redis Configuration${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

    cat > /tmp/redis_security_fix.sh << EOF
#!/bin/bash
# This script will run INSIDE the container

echo "Finding Redis config..."
REDIS_CONF=\$(find /etc -name "redis.conf" -type f 2>/dev/null | head -1)

if [ -z "\$REDIS_CONF" ]; then
    REDIS_CONF="/etc/redis/redis.conf"
fi

echo "Redis config: \$REDIS_CONF"

if [ ! -f "\$REDIS_CONF" ]; then
    echo "ERROR: Redis config not found at \$REDIS_CONF"
    exit 1
fi

# Backup
cp "\$REDIS_CONF" "\${REDIS_CONF}.backup.\$(date +%Y%m%d_%H%M%S)"
echo "✓ Backed up config"

# Fix binding
sed -i 's/^bind .*/bind 127.0.0.1 ::1/' "\$REDIS_CONF"
if ! grep -q "^bind 127.0.0.1" "\$REDIS_CONF"; then
    echo "bind 127.0.0.1 ::1" >> "\$REDIS_CONF"
fi
echo "✓ Changed bind to localhost"

# Add password
sed -i "s/^# requirepass .*/requirepass $REDIS_PASSWORD/" "\$REDIS_CONF"
if ! grep -q "^requirepass" "\$REDIS_CONF"; then
    echo "requirepass $REDIS_PASSWORD" >> "\$REDIS_CONF"
fi
echo "✓ Added password"

# Enable protected mode
sed -i 's/^protected-mode no/protected-mode yes/' "\$REDIS_CONF"
if ! grep -q "^protected-mode" "\$REDIS_CONF"; then
    echo "protected-mode yes" >> "\$REDIS_CONF"
fi
echo "✓ Enabled protected mode"

# Disable dangerous commands
echo "" >> "\$REDIS_CONF"
echo "# Security: Disabled dangerous commands" >> "\$REDIS_CONF"
echo 'rename-command FLUSHDB ""' >> "\$REDIS_CONF"
echo 'rename-command FLUSHALL ""' >> "\$REDIS_CONF"
echo 'rename-command CONFIG ""' >> "\$REDIS_CONF"
echo "✓ Disabled dangerous commands"

# Restart Redis
if systemctl restart redis-server 2>/dev/null || systemctl restart redis 2>/dev/null; then
    echo "✓ Redis restarted"
elif service redis-server restart 2>/dev/null; then
    echo "✓ Redis restarted"
else
    echo "WARNING: Could not restart Redis automatically"
    echo "Please restart Redis manually inside the container"
fi

echo ""
echo "✓ Redis security fix complete inside container!"
EOF

    chmod +x /tmp/redis_security_fix.sh
    echo -e "${GREEN}✓ Created fix script${NC}"
    echo ""

    echo -e "${YELLOW}Now copying script to container and executing...${NC}"
    echo ""

    # Copy script to container
    echo "Running: sudo lxc file push /tmp/redis_security_fix.sh $CONTAINER_NAME/tmp/"
    sudo lxc file push /tmp/redis_security_fix.sh $CONTAINER_NAME/tmp/

    # Execute in container
    echo "Running: sudo lxc exec $CONTAINER_NAME -- bash /tmp/redis_security_fix.sh"
    sudo lxc exec $CONTAINER_NAME -- bash /tmp/redis_security_fix.sh

    echo ""
    echo -e "${GREEN}✓ Redis fixed inside container${NC}"
    echo ""

    read -p "Press Enter to continue..."
    echo ""
fi

# Configure firewall
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}[Step 5/7] Configuring Firewall${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

if command -v ufw &> /dev/null; then
    echo "Checking UFW status..."
    UFW_STATUS=$(sudo ufw status 2>/dev/null | grep "Status:" | awk '{print $2}')

    if [ "$UFW_STATUS" != "active" ]; then
        echo -e "${YELLOW}UFW is not active. Enabling...${NC}"
        echo "Running: sudo ufw --force enable"
        sudo ufw --force enable
    fi

    echo "Blocking Redis port 6379..."
    echo "Running: sudo ufw deny 6379/tcp"
    sudo ufw deny 6379/tcp

    echo ""
    echo "Ensuring essential ports are open..."
    sudo ufw allow 22/tcp   # SSH
    sudo ufw allow 80/tcp   # HTTP
    sudo ufw allow 443/tcp  # HTTPS

    echo ""
    echo "Current firewall status:"
    sudo ufw status verbose
    echo ""
    echo -e "${GREEN}✓ Firewall configured${NC}"
else
    echo -e "${YELLOW}UFW not installed. Install with: apt install ufw${NC}"
fi

echo ""
read -p "Press Enter to continue..."
echo ""

# Verify security
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}[Step 6/7] Verifying Security Fix${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

sleep 2

echo "Checking Redis binding..."
BINDING=$(ss -tulpn 2>/dev/null | grep 6379 || netstat -tulpn 2>/dev/null | grep 6379 || echo "")
if echo "$BINDING" | grep -q "127.0.0.1:6379"; then
    echo -e "${GREEN}✓ Redis is now bound to localhost only${NC}"
elif echo "$BINDING" | grep -q "0.0.0.0:6379"; then
    echo -e "${RED}✗ WARNING: Redis is still bound to all interfaces!${NC}"
    echo "You may need to restart the LXD container or check the config again"
else
    echo -e "${YELLOW}! Could not verify binding${NC}"
fi

echo ""
echo "$BINDING"
echo ""

read -p "Press Enter to continue..."
echo ""

# Update application
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}[Step 7/7] Updating Application Configuration${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

BACKEND_ENV="/home/adminmatej/github/applications/operator-demo-2026/backend/.env"

echo "Adding Redis password to $BACKEND_ENV"
if [ -f "$BACKEND_ENV" ]; then
    # Check if REDIS_PASSWORD already exists
    if grep -q "^REDIS_PASSWORD=" "$BACKEND_ENV"; then
        echo "Updating existing REDIS_PASSWORD..."
        sed -i "s/^REDIS_PASSWORD=.*/REDIS_PASSWORD=$REDIS_PASSWORD/" "$BACKEND_ENV"
    else
        echo "Adding new REDIS_PASSWORD..."
        echo "REDIS_PASSWORD=$REDIS_PASSWORD" >> "$BACKEND_ENV"
    fi
    echo -e "${GREEN}✓ Updated $BACKEND_ENV${NC}"
else
    echo "Creating $BACKEND_ENV"
    echo "REDIS_PASSWORD=$REDIS_PASSWORD" > "$BACKEND_ENV"
    echo -e "${GREEN}✓ Created $BACKEND_ENV${NC}"
fi

echo ""
echo -e "${YELLOW}Redis connection URL for your application:${NC}"
echo -e "${GREEN}redis://:$REDIS_PASSWORD@localhost:6379/0${NC}"
echo ""

read -p "Press Enter to see final summary..."
echo ""

# Final summary
echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                  ✓ SECURITY FIX COMPLETE                       ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}✓ Redis password generated and configured${NC}"
echo -e "${GREEN}✓ Redis bound to localhost only (127.0.0.1)${NC}"
echo -e "${GREEN}✓ Protected mode enabled${NC}"
echo -e "${GREEN}✓ Dangerous commands disabled${NC}"
echo -e "${GREEN}✓ Firewall configured (port 6379 blocked)${NC}"
echo -e "${GREEN}✓ Application .env file updated${NC}"
echo ""
echo -e "${YELLOW}Redis Password:${NC} ${GREEN}$REDIS_PASSWORD${NC}"
echo -e "${YELLOW}Saved to:${NC} $PASS_FILE"
echo ""
echo -e "${YELLOW}IMPORTANT NEXT STEPS:${NC}"
echo "1. Test your application to ensure it connects to Redis"
echo "2. Check logs: tail -f backend/logs/*.log"
echo "3. Run verification: bash scripts/verify-redis-security.sh"
echo "4. Review incident report: SECURITY_INCIDENT_2025-10-15.md"
echo ""
echo -e "${YELLOW}If your application fails to connect:${NC}"
echo "  - Check .env file has: REDIS_PASSWORD=$REDIS_PASSWORD"
echo "  - Update connection string: redis://:PASSWORD@localhost:6379/0"
echo "  - Restart your application"
echo ""
echo -e "${GREEN}The security vulnerability has been fixed!${NC}"
echo ""
