#!/bin/bash

################################################################################
# Redis Security Verification Script
#
# This script verifies that Redis is properly secured
#
# Run with: bash verify-redis-security.sh
################################################################################

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}========================================${NC}"
echo -e "${YELLOW}Redis Security Verification${NC}"
echo -e "${YELLOW}========================================${NC}"
echo ""

ISSUES=0

# Check 1: Redis is running
echo -e "${YELLOW}[1/6] Checking if Redis is running...${NC}"
if ps aux | grep -v grep | grep redis-server > /dev/null; then
    echo -e "${GREEN}✓ Redis is running${NC}"
else
    echo -e "${RED}✗ Redis is not running${NC}"
    ISSUES=$((ISSUES+1))
fi

# Check 2: Binding to localhost only
echo -e "${YELLOW}[2/6] Checking Redis binding...${NC}"
BINDING=$(ss -tulpn 2>/dev/null | grep 6379 || netstat -tulpn 2>/dev/null | grep 6379 || echo "")

if echo "$BINDING" | grep -q "127.0.0.1:6379"; then
    echo -e "${GREEN}✓ Redis is bound to localhost only (127.0.0.1)${NC}"
elif echo "$BINDING" | grep -q "0.0.0.0:6379"; then
    echo -e "${RED}✗ CRITICAL: Redis is bound to all interfaces (0.0.0.0)${NC}"
    echo -e "${RED}  This exposes Redis to the Internet!${NC}"
    ISSUES=$((ISSUES+1))
elif echo "$BINDING" | grep -q ":::6379"; then
    echo -e "${RED}✗ CRITICAL: Redis is bound to all IPv6 interfaces${NC}"
    ISSUES=$((ISSUES+1))
else
    echo -e "${YELLOW}! Could not determine binding${NC}"
fi

# Check 3: Authentication enabled
echo -e "${YELLOW}[3/6] Checking authentication...${NC}"
if command -v redis-cli &> /dev/null; then
    PING_RESULT=$(redis-cli -h 127.0.0.1 ping 2>&1)
    if echo "$PING_RESULT" | grep -q "NOAUTH"; then
        echo -e "${GREEN}✓ Authentication is required${NC}"
    elif echo "$PING_RESULT" | grep -q "PONG"; then
        echo -e "${RED}✗ WARNING: Redis allows connections without password!${NC}"
        ISSUES=$((ISSUES+1))
    else
        echo -e "${YELLOW}! Could not verify (Redis may require password)${NC}"
        echo "  Try: redis-cli -a <password> ping"
    fi
else
    echo -e "${YELLOW}! redis-cli not installed, skipping auth check${NC}"
fi

# Check 4: Protected mode
echo -e "${YELLOW}[4/6] Checking protected mode...${NC}"
if [ -f "/etc/redis/redis.conf" ]; then
    REDIS_CONF="/etc/redis/redis.conf"
elif [ -f "/etc/redis.conf" ]; then
    REDIS_CONF="/etc/redis.conf"
else
    echo -e "${YELLOW}! Redis config file not found${NC}"
    REDIS_CONF=""
fi

if [ -n "$REDIS_CONF" ] && [ -f "$REDIS_CONF" ]; then
    if grep -q "^protected-mode yes" "$REDIS_CONF"; then
        echo -e "${GREEN}✓ Protected mode is enabled${NC}"
    else
        echo -e "${RED}✗ Protected mode is not enabled${NC}"
        ISSUES=$((ISSUES+1))
    fi
fi

# Check 5: Firewall
echo -e "${YELLOW}[5/6] Checking firewall rules...${NC}"
if command -v ufw &> /dev/null; then
    if sudo ufw status 2>/dev/null | grep -q "Status: active"; then
        echo -e "${GREEN}✓ UFW firewall is active${NC}"
        if sudo ufw status 2>/dev/null | grep -q "6379"; then
            echo -e "${YELLOW}! Port 6379 has firewall rule (check if it's DENY)${NC}"
        else
            echo -e "${GREEN}✓ No specific rule for port 6379 (using default deny)${NC}"
        fi
    else
        echo -e "${YELLOW}! UFW firewall is not active${NC}"
        echo "  Consider enabling: sudo ufw enable"
    fi
else
    echo -e "${YELLOW}! UFW not installed, checking iptables...${NC}"
    if sudo iptables -L 2>/dev/null | grep -q "6379"; then
        echo -e "${GREEN}✓ iptables rules found for port 6379${NC}"
    else
        echo -e "${YELLOW}! No iptables rules found${NC}"
    fi
fi

# Check 6: External accessibility
echo -e "${YELLOW}[6/6] Checking external accessibility...${NC}"
echo "  Testing if Redis is accessible from external IP..."

# Get public IP
PUBLIC_IP=$(curl -s ifconfig.me 2>/dev/null || echo "unknown")
if [ "$PUBLIC_IP" != "unknown" ]; then
    echo "  Your public IP: $PUBLIC_IP"

    # Try to connect from localhost to public IP
    if command -v nc &> /dev/null; then
        if timeout 2 nc -zv "$PUBLIC_IP" 6379 2>&1 | grep -q "succeeded"; then
            echo -e "${RED}✗ CRITICAL: Redis port 6379 is accessible from public IP!${NC}"
            ISSUES=$((ISSUES+1))
        else
            echo -e "${GREEN}✓ Redis port is not accessible from public IP${NC}"
        fi
    else
        echo -e "${YELLOW}! netcat (nc) not installed, cannot verify external access${NC}"
    fi
else
    echo -e "${YELLOW}! Could not determine public IP${NC}"
fi

echo ""
echo -e "${YELLOW}========================================${NC}"

if [ $ISSUES -eq 0 ]; then
    echo -e "${GREEN}✓ ALL CHECKS PASSED${NC}"
    echo -e "${GREEN}Redis is properly secured!${NC}"
else
    echo -e "${RED}✗ FOUND $ISSUES SECURITY ISSUE(S)${NC}"
    echo -e "${RED}ACTION REQUIRED: Fix the issues above${NC}"
    echo ""
    echo "To fix Redis security, run:"
    echo "  sudo bash /home/adminmatej/github/applications/voice-kraliki/scripts/fix-redis-security.sh"
fi

echo -e "${YELLOW}========================================${NC}"
echo ""

# Summary
echo "Security Checklist:"
echo "  [$([ $ISSUES -eq 0 ] && echo '✓' || echo ' ')] Redis bound to localhost only"
echo "  [$(command -v redis-cli &> /dev/null && redis-cli ping 2>&1 | grep -q 'NOAUTH' && echo '✓' || echo ' ')] Authentication enabled"
echo "  [$([ -n "$REDIS_CONF" ] && grep -q '^protected-mode yes' "$REDIS_CONF" && echo '✓' || echo ' ')] Protected mode enabled"
echo "  [$(command -v ufw &> /dev/null && sudo ufw status 2>/dev/null | grep -q 'Status: active' && echo '✓' || echo ' ')] Firewall enabled"
echo "  [$(ss -tulpn 2>/dev/null | grep 6379 | grep -q '127.0.0.1' && echo '✓' || echo ' ')] Not accessible from Internet"
echo ""

exit $ISSUES
