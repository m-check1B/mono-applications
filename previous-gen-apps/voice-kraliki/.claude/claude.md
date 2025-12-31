# Claude Code - Project Guidelines and Security Rules

**Project:** Operator Demo 2026
**Last Updated:** October 15, 2025
**Version:** 1.0

---

## 🔒 CRITICAL SECURITY RULES - NEVER VIOLATE

### 1. **Database Security - Redis**

**RULE:** Redis MUST NEVER be exposed to the public Internet without authentication.

**Incident:** October 15, 2025 - BSI (German Federal Office for Information Security) reported openly accessible Redis server at `5.9.38.218:6379` running Redis 7.4.5 without authentication.

**Status:** ✅ **RESOLVED** - October 15, 2025

**Vulnerability (FIXED):**
- Redis was binding to `0.0.0.0:6379` (all interfaces) → **Fixed: Now 127.0.0.1:6379**
- No password authentication configured → **Fixed: Strong 32-char password enabled**
- Attackers could read, modify, or delete all data → **Fixed: Protected mode enabled**
- Potential exposure of login credentials, customer data, API keys → **Mitigated: Localhost only**

**Resolution:**
- Docker container `operator-demo-redis` reconfigured with secure settings
- Port mapping changed from `0.0.0.0:6379` to `127.0.0.1:6379`
- Password: `requirepass` enabled (32 characters)
- Protected mode: Enabled
- Dangerous commands: Disabled (FLUSHDB, FLUSHALL, CONFIG)
- Application updated with authentication credentials

**REQUIRED CONFIGURATION:**

#### For Production/External Servers:
```conf
# /etc/redis/redis.conf

# 1. BIND TO LOCALHOST ONLY (not 0.0.0.0)
bind 127.0.0.1 ::1

# 2. REQUIRE STRONG PASSWORD
requirepass YOUR_VERY_STRONG_PASSWORD_HERE_AT_LEAST_32_CHARS

# 3. DISABLE DANGEROUS COMMANDS
rename-command FLUSHDB ""
rename-command FLUSHALL ""
rename-command CONFIG ""
rename-command SHUTDOWN ""
rename-command BGREWRITEAOF ""
rename-command BGSAVE ""
rename-command SAVE ""
rename-command DEBUG ""

# 4. ENABLE PROTECTED MODE
protected-mode yes

# 5. SET MAXIMUM CONNECTIONS
maxclients 10000

# 6. ENABLE LOGGING
loglevel notice
logfile /var/log/redis/redis-server.log
```

#### Apply Fix Immediately:
```bash
# 1. Edit Redis configuration
sudo nano /etc/redis/redis.conf

# 2. Add/modify these lines:
#    bind 127.0.0.1 ::1
#    requirepass <strong-password>
#    protected-mode yes

# 3. Restart Redis
sudo systemctl restart redis-server
# OR
sudo systemctl restart redis

# 4. Verify Redis is only listening on localhost
ss -tulpn | grep 6379
# Should show: 127.0.0.1:6379 (NOT 0.0.0.0:6379)

# 5. Test authentication is required
redis-cli ping
# Should return: (error) NOAUTH Authentication required.

redis-cli -a <your-password> ping
# Should return: PONG
```

#### Docker/Container Configuration:
```yaml
# docker-compose.yml
services:
  redis:
    image: redis:7.4-alpine
    command: >
      --requirepass ${REDIS_PASSWORD}
      --bind 127.0.0.1
      --protected-mode yes
      --rename-command FLUSHDB ""
      --rename-command FLUSHALL ""
      --rename-command CONFIG ""
    ports:
      - "127.0.0.1:6379:6379"  # NEVER use "6379:6379"
    volumes:
      - redis-data:/data
    restart: unless-stopped
    networks:
      - internal  # Never expose to public network
```

**VERIFICATION CHECKLIST:**
- [x] Redis binds ONLY to 127.0.0.1 or internal network ✅ **VERIFIED Oct 15, 2025**
- [x] Strong password (32+ characters) configured ✅ **VERIFIED Oct 15, 2025**
- [x] Dangerous commands disabled ✅ **VERIFIED Oct 15, 2025**
- [x] Protected mode enabled ✅ **VERIFIED Oct 15, 2025**
- [x] Port 6379 NOT accessible from Internet ✅ **VERIFIED Oct 15, 2025**
- [ ] Firewall rules block external access ⚠️ **RECOMMENDED (sudo ufw enable)**
- [x] Application connects with authentication ✅ **CONFIGURED Oct 15, 2025**

---

### 2. **Database Security - PostgreSQL**

**RULE:** PostgreSQL MUST NEVER be exposed to the public Internet.

**REQUIRED CONFIGURATION:**
```conf
# postgresql.conf
listen_addresses = 'localhost'  # NEVER use '*'

# pg_hba.conf
# Only allow local connections
local   all             all                                     peer
host    all             all             127.0.0.1/32            scram-sha-256
host    all             all             ::1/128                 scram-sha-256
```

---

### 3. **API Key & Secrets Management**

**RULES:**
- ❌ NEVER commit API keys, passwords, or secrets to git
- ❌ NEVER expose secrets in environment variables visible to public
- ✅ ALWAYS use `.env` files (gitignored)
- ✅ ALWAYS use secret management tools (Vault, AWS Secrets Manager)
- ✅ ALWAYS rotate credentials regularly

**REQUIRED `.gitignore` entries:**
```gitignore
# Secrets and credentials
.env
.env.local
.env.*.local
*.key
*.pem
credentials.json
secrets.yaml
config/secrets.yml

# Database files
*.db
*.sqlite
*.sqlite3

# Redis dumps
dump.rdb
appendonly.aof
```

---

### 4. **Firewall & Network Security**

**RULES:**
- ✅ ALWAYS use firewall (ufw/iptables) to block unnecessary ports
- ✅ ONLY expose ports that MUST be public (80, 443)
- ❌ NEVER expose database ports (5432, 3306, 6379, 27017)
- ❌ NEVER expose admin panels without authentication

**Required Firewall Configuration:**
```bash
# Enable firewall
sudo ufw enable

# Allow only necessary ports
sudo ufw allow 22/tcp    # SSH (consider changing port)
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS

# Deny everything else (default)
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Verify status
sudo ufw status verbose

# CRITICAL: Ensure these ports are NOT open to public:
# 6379 (Redis)
# 5432 (PostgreSQL)
# 3306 (MySQL)
# 27017 (MongoDB)
# 8000 (Development servers)
```

---

### 5. **Docker & Container Security**

**RULES:**
- ❌ NEVER expose internal services to `0.0.0.0`
- ✅ ALWAYS bind to `127.0.0.1` or internal networks
- ✅ ALWAYS use strong passwords for all services
- ✅ ALWAYS use internal Docker networks

**Example Secure Docker Compose:**
```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "127.0.0.1:8000:8000"  # Only accessible locally
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/dbname
      - REDIS_URL=redis://:password@redis:6379/0
    networks:
      - internal

  redis:
    image: redis:7.4-alpine
    command: --requirepass ${REDIS_PASSWORD}
    # NO ports exposed to host (only accessible via internal network)
    networks:
      - internal

  postgres:
    image: postgres:16-alpine
    environment:
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    # NO ports exposed to host
    networks:
      - internal

networks:
  internal:
    driver: bridge
    internal: true  # Not connected to outside world
```

---

### 6. **Code Security - Never Commit Sensitive Data**

**RULES:**
- ✅ ALWAYS review changes before committing
- ✅ ALWAYS use `git diff` to check for secrets
- ❌ NEVER commit hardcoded passwords or API keys
- ✅ ALWAYS use environment variables

**Pre-commit checklist:**
```bash
# Check for potential secrets
git diff | grep -iE '(password|api_key|secret|token|credential)' || echo "✓ No obvious secrets"

# Check for common secret patterns
git diff | grep -iE '(AKIA|sk-|ghp_|gho_)' || echo "✓ No API keys detected"
```

---

### 7. **Dependency Security**

**RULES:**
- ✅ ALWAYS keep dependencies updated
- ✅ ALWAYS audit dependencies for vulnerabilities
- ✅ ALWAYS review security advisories

**Required Commands:**
```bash
# Backend (Python)
pip audit
safety check
pip list --outdated

# Frontend (Node.js)
pnpm audit
pnpm outdated
pnpm update
```

---

## 🔍 Security Audit Checklist

Run this checklist BEFORE any deployment:

### Network Security
- [ ] Redis bound to localhost only (127.0.0.1)
- [ ] PostgreSQL bound to localhost only
- [ ] Firewall enabled and configured
- [ ] Only ports 80/443 exposed to Internet
- [ ] All database ports blocked from Internet

### Authentication & Secrets
- [ ] Redis password configured (32+ chars)
- [ ] Database passwords strong (16+ chars)
- [ ] No secrets in git history
- [ ] `.env` files gitignored
- [ ] API keys rotated in last 90 days

### Application Security
- [ ] All dependencies updated
- [ ] No known vulnerabilities (audit passed)
- [ ] HTTPS/TLS enabled
- [ ] CORS configured properly
- [ ] Rate limiting enabled

### Monitoring
- [ ] Security logs enabled
- [ ] Failed login attempts monitored
- [ ] Unusual activity alerts configured
- [ ] Backup system verified

---

## 🚨 Incident Response

If you receive a security notification (like the BSI Redis report):

1. **IMMEDIATE ACTION** (within 1 hour):
   - Identify the vulnerable service
   - Apply security patch immediately
   - Verify fix is effective
   - Document the incident

2. **INVESTIGATION** (within 24 hours):
   - Check logs for unauthorized access
   - Identify what data was exposed
   - Assess impact and risk
   - Notify stakeholders if needed

3. **PREVENTION** (within 1 week):
   - Update security documentation
   - Add automated checks
   - Review similar services
   - Implement monitoring

---

## 📋 Security Review Schedule

| Task | Frequency | Last Done |
|------|-----------|-----------|
| Dependency audit | Weekly | TBD |
| Security scan | Weekly | TBD |
| Password rotation | Quarterly | TBD |
| Access review | Quarterly | TBD |
| Security training | Annually | TBD |
| Penetration test | Annually | TBD |

---

## 🛠️ Automated Security Tools

**Install and configure these tools:**

### 1. Git Secrets Prevention
```bash
# Install git-secrets
brew install git-secrets  # macOS
# OR
apt-get install git-secrets  # Linux

# Setup
cd /home/adminmatej/github/applications/operator-demo-2026
git secrets --install
git secrets --register-aws
```

### 2. Pre-commit Hooks
```bash
# Install pre-commit
pip install pre-commit

# Create .pre-commit-config.yaml
cat > .pre-commit-config.yaml << 'EOF'
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: check-added-large-files
      - id: check-merge-conflict
      - id: detect-private-key
      - id: trailing-whitespace

  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.4.0
    hooks:
      - id: detect-secrets
EOF

# Install hooks
pre-commit install
```

---

## 📞 Security Contacts

| Issue Type | Contact | Response Time |
|------------|---------|---------------|
| Critical Security | Matej Havlin | Immediate |
| BSI Notifications | certbund@bsi.bund.de | 24 hours |
| Hetzner Abuse | abuse@hetzner.com | 48 hours |

---

## 📚 References

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Redis Security](https://redis.io/docs/management/security/)
- [PostgreSQL Security](https://www.postgresql.org/docs/current/security.html)
- [Docker Security](https://docs.docker.com/engine/security/)
- [BSI Security Advisories](https://www.bsi.bund.de/EN/Home/home_node.html)

---

**Last Security Incident:** October 15, 2025 - Redis exposed (IP: 5.9.38.218)
**Status:** ✅ **RESOLVED** - October 15, 2025
**Resolution Time:** ~30 minutes
**Priority:** P0 - CRITICAL (Resolved)

**Fix Applied:**
- Container: `operator-demo-redis` reconfigured
- Binding: `0.0.0.0:6379` → `127.0.0.1:6379` ✅
- Authentication: Password enabled (32 chars) ✅
- Protected mode: Enabled ✅
- Verification: All checks passed ✅
- Documentation: `SECURITY_FIX_COMPLETE.md` created ✅

**Lessons Learned:**
1. Always bind Docker containers to `127.0.0.1`, never `0.0.0.0`
2. Always enable authentication on all database services
3. Verify port bindings after deployment
4. Use verification scripts regularly
5. Document all security incidents

**Next BSI Scan:** Will automatically detect fix and stop notifications

---

*This document must be reviewed and updated after every security incident.*
*Last Updated: October 15, 2025 - Post Redis Security Incident Resolution*
