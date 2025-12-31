#!/bin/bash
# Security: Validate swarm container configuration

set -e

echo "=== Kraliki Swarm Security Validator ==="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

FAIL=0
WARN=0

# Check 1: SSH keys NOT mounted
echo "[1/10] Checking for SSH key mounts..."
if docker inspect kraliki-swarm-cli 2>/dev/null | grep -q "/.ssh"; then
    echo -e "${RED}✗ FAIL${NC}: SSH keys are mounted in container!"
    echo "   This allows agents to SSH to other servers."
    FAIL=$((FAIL + 1))
else
    echo -e "${GREEN}✓ PASS${NC}: SSH keys not mounted"
fi

# Check 2: Docker socket NOT mounted
echo "[2/10] Checking for Docker socket mount..."
if docker inspect kraliki-swarm-cli 2>/dev/null | grep -q "/var/run/docker.sock"; then
    echo -e "${RED}✗ FAIL${NC}: Docker socket is mounted!"
    echo "   This allows agents to control the Docker daemon."
    FAIL=$((FAIL + 1))
else
    echo -e "${GREEN}✓ PASS${NC}: Docker socket not mounted"
fi

# Check 3: Running as non-root
echo "[3/10] Checking if container runs as root..."
if docker inspect kraliki-swarm-cli 2>/dev/null | grep -q '"User": "0"'; then
    echo -e "${RED}✗ FAIL${NC}: Container running as root!"
    echo "   Agents should run as non-root user."
    FAIL=$((FAIL + 1))
elif docker inspect kraliki-swarm-cli 2>/dev/null | grep -q '"User": "1000"'; then
    echo -e "${GREEN}✓ PASS${NC}: Container running as non-root (UID 1000)"
else
    echo -e "${YELLOW}⚠ WARN${NC}: Could not verify user"
    WARN=$((WARN + 1))
fi

# Check 4: Privileged mode
echo "[4/10] Checking privileged mode..."
if docker inspect kraliki-swarm-cli 2>/dev/null | grep -q '"Privileged": true'; then
    echo -e "${RED}✗ FAIL${NC}: Container running in privileged mode!"
    echo "   This gives containers full host access."
    FAIL=$((FAIL + 1))
else
    echo -e "${GREEN}✓ PASS${NC}: Container not in privileged mode"
fi

# Check 5: Capabilities
echo "[5/10] Checking dropped capabilities..."
if docker inspect kraliki-swarm-cli 2>/dev/null | grep -q '"CapAdd": \[\]' && \
   docker inspect kraliki-swarm-cli 2>/dev/null | grep -q '"CapDrop": \["ALL"\]'; then
    echo -e "${GREEN}✓ PASS${NC}: All capabilities dropped"
else
    echo -e "${YELLOW}⚠ WARN${NC}: Capabilities not fully restricted"
    WARN=$((WARN + 1))
fi

# Check 6: Read-only filesystem
echo "[6/10] Checking read-only filesystem..."
if docker inspect kraliki-swarm-cli 2>/dev/null | grep -q '"ReadonlyRootfs": true'; then
    echo -e "${GREEN}✓ PASS${NC}: Root filesystem is read-only"
else
    echo -e "${YELLOW}⚠ WARN${NC}: Root filesystem is not read-only"
    WARN=$((WARN + 1))
fi

# Check 7: No system directory mounts
echo "[7/10] Checking for system directory mounts..."
if docker inspect kraliki-swarm-cli 2>/dev/null | grep -q '/etc/\|/var/\|/usr/\|/bin/\|/sbin/'; then
    echo -e "${RED}✗ FAIL${NC}: System directories are mounted!"
    echo "   This allows agents to access host system."
    FAIL=$((FAIL + 1))
else
    echo -e "${GREEN}✓ PASS${NC}: No system directories mounted"
fi

# Check 8: Secrets as environment variables
echo "[8/10] Checking secret file mounts..."
if docker inspect kraliki-swarm-cli 2>/dev/null | grep -q '/secrets/\|\.key\|\.pem\|\.crt'; then
    echo -e "${RED}✗ FAIL${NC}: Secret files are mounted!"
    echo "   Secrets should be passed as environment variables."
    FAIL=$((FAIL + 1))
else
    echo -e "${GREEN}✓ PASS${NC}: No secret file mounts"
fi

# Check 9: Network isolation
echo "[9/10] Checking network mode..."
if docker inspect kraliki-swarm-cli 2>/dev/null | grep -q '"NetworkMode": "bridge"'; then
    echo -e "${GREEN}✓ PASS${NC}: Container using bridge network (isolated)"
else
    echo -e "${YELLOW}⚠ WARN${NC}: Not using bridge network mode"
    WARN=$((WARN + 1))
fi

# Check 10: Production certificate blocking
echo "[10/10] Checking for production environment..."
if docker inspect kraliki-swarm-cli 2>/dev/null | grep -q 'ENVIRONMENT=production'; then
    echo -e "${RED}✗ FAIL${NC}: Container in production environment!"
    echo "   Dev container should not have production access."
    FAIL=$((FAIL + 1))
else
    echo -e "${GREEN}✓ PASS${NC}: Container not in production environment"
fi

# Summary
echo ""
echo "=== SUMMARY ==="
echo -e "Checks passed: ${GREEN}$(($(grep -c "✓ PASS" <<< "$0" || echo 0))${NC}"
echo -e "Warnings:      ${YELLOW}${WARN}${NC}"
echo -e "Failures:      ${RED}${FAIL}${NC}"

if [ $FAIL -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✓ All critical security checks passed!${NC}"
    exit 0
else
    echo ""
    echo -e "${RED}✗ Security validation failed!${NC}"
    echo "Please fix the issues above before running swarm."
    exit 1
fi
