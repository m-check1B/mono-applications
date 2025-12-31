# Security Incident Report - Redis Exposure

**Date:** October 15, 2025
**Severity:** 🔴 CRITICAL
**Status:** ⚠️ REQUIRES IMMEDIATE ACTION
**Reported By:** BSI (German Federal Office for Information Security)

---

## 📋 Incident Summary

### What Happened
Redis server (version 7.4.5) running on IP address `5.9.38.218:6379` was discovered to be openly accessible from the Internet without authentication.

### When Discovered
- **Detection:** October 14, 2025 at 15:59:44 UTC
- **Notification:** October 15, 2025 at 2:29 PM
- **Report ID:** CB-Report#20251015-10007949
- **Abuse ID:** 10818B7:1E

### Affected System
- **Server IP:** 5.9.38.218
- **Port:** 6379 (Redis)
- **Redis Version:** 7.4.5
- **ASN:** 24940 (Hetzner Online GmbH)
- **Binding:** 0.0.0.0:6379 (ALL INTERFACES - CRITICAL!)

---

## 🎯 Vulnerability Details

### What's Wrong
1. **No Authentication:** Redis is running without password (`requirepass` not configured)
2. **Public Binding:** Redis is bound to `0.0.0.0:6379` instead of `127.0.0.1:6379`
3. **No Protected Mode:** Protected mode is disabled or not effective
4. **No Firewall:** Port 6379 is not blocked by firewall rules

### What Could Happen
- ❌ Attackers can read ALL data stored in Redis
- ❌ Attackers can modify or delete ANY data
- ❌ Potential exposure of:
  - Session tokens
  - User credentials
  - API keys
  - Application secrets
  - Customer data
  - Cache data
- ❌ Attackers could use Redis for:
  - Data exfiltration
  - Lateral movement
  - Cryptomining
  - Ransomware
  - Botnet operations

### Current Risk Level
🔴 **CRITICAL** - Actively exploitable, no authentication required

---

## ✅ Immediate Actions Required

### 1. Verify the Issue (2 minutes)
```bash
# Check Redis binding
ss -tulpn | grep 6379

# Expected BAD output: 0.0.0.0:6379 (exposes to Internet)
# Expected GOOD output: 127.0.0.1:6379 (localhost only)

# Run verification script
bash /home/adminmatej/github/applications/operator-demo-2026/scripts/verify-redis-security.sh
```

### 2. Apply Security Fix (5 minutes)
```bash
# Run automated fix script (REQUIRES SUDO)
cd /home/adminmatej/github/applications/operator-demo-2026
sudo bash scripts/fix-redis-security.sh

# This will:
# - Bind Redis to localhost only (127.0.0.1)
# - Generate and set a strong password
# - Enable protected mode
# - Disable dangerous commands
# - Restart Redis
```

### 3. Update Application Configuration (5 minutes)
```bash
# The fix script will generate a password like:
# REDIS_PASSWORD=abc123...xyz789

# Add it to your backend .env file:
echo 'REDIS_PASSWORD=<generated-password>' >> backend/.env

# Update application code to use authentication:
# Redis URL format: redis://:PASSWORD@localhost:6379/0
```

### 4. Configure Firewall (2 minutes)
```bash
# Enable UFW firewall
sudo ufw enable

# Explicitly block Redis port from external access
sudo ufw deny 6379/tcp

# Allow only necessary ports
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS

# Verify
sudo ufw status verbose
```

### 5. Verify Fix (2 minutes)
```bash
# Run verification script again
bash /home/adminmatej/github/applications/operator-demo-2026/scripts/verify-redis-security.sh

# Should show:
# ✓ ALL CHECKS PASSED
# Redis is properly secured!

# Verify externally (optional)
# From another machine, try: nc -zv 5.9.38.218 6379
# Should fail to connect
```

---

## 🔍 Investigation Checklist

After securing Redis, investigate potential unauthorized access:

### Check Redis Logs
```bash
# View Redis logs
sudo tail -100 /var/log/redis/redis-server.log

# Look for:
# - Unusual connection patterns
# - Unknown IP addresses
# - Suspicious commands (KEYS, FLUSHALL, CONFIG)
# - High command rate from unknown sources
```

### Check System Logs
```bash
# Check system auth logs
sudo tail -100 /var/log/auth.log

# Check for unusual activity
sudo last | head -20
sudo lastb | head -20  # Failed login attempts
```

### Check Redis Data
```bash
# Connect to Redis (with password)
redis-cli -a <password>

# Check for unusual keys
KEYS *

# Check server info
INFO server
INFO stats

# Check connected clients
CLIENT LIST
```

### Check for Data Exfiltration
```bash
# Check network connections
sudo netstat -ant | grep :6379
sudo ss -ant | grep :6379

# Check Redis command stats
redis-cli -a <password> INFO commandstats
```

---

## 📊 Impact Assessment

### Data Potentially Exposed

Depending on what your application stores in Redis:

| Data Type | Likely Stored | Risk Level |
|-----------|---------------|------------|
| Session tokens | ✅ High probability | 🔴 Critical |
| User credentials | ❓ Possible (cached) | 🔴 Critical |
| API keys | ❓ Possible | 🔴 Critical |
| OAuth tokens | ✅ Likely | 🔴 Critical |
| User data | ✅ Likely (cached) | 🟡 High |
| Application secrets | ❓ Possible | 🔴 Critical |
| Rate limit data | ✅ Likely | 🟢 Low |
| Cache data | ✅ Certain | 🟡 Medium |

### Recommended Actions Based on Exposure

1. **If session tokens exposed:**
   - ✅ Invalidate ALL active sessions
   - ✅ Force all users to re-login
   - ✅ Rotate session secret keys

2. **If credentials exposed:**
   - ✅ Force password reset for all users
   - ✅ Enable 2FA if not already enabled
   - ✅ Monitor for account takeover attempts

3. **If API keys exposed:**
   - ✅ Rotate ALL API keys immediately
   - ✅ Review API usage logs for anomalies
   - ✅ Notify affected service providers

4. **If customer data exposed:**
   - ✅ Assess GDPR/privacy law requirements
   - ✅ Consider breach notification obligations
   - ✅ Document incident for compliance

---

## 🛠️ Long-Term Prevention

### Automated Monitoring
```bash
# Set up automated security checks (add to crontab)
# Check Redis security every hour
0 * * * * /home/adminmatej/github/applications/operator-demo-2026/scripts/verify-redis-security.sh

# Alert if issues found
0 * * * * /home/adminmatej/github/applications/operator-demo-2026/scripts/verify-redis-security.sh || echo "Redis security issue detected!" | mail -s "SECURITY ALERT" your@email.com
```

### Infrastructure as Code
```yaml
# docker-compose.yml - Secure Redis configuration
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
      - "127.0.0.1:6379:6379"  # Bind to localhost only
    volumes:
      - redis-data:/data
    restart: unless-stopped
    networks:
      - internal
```

### Security Scanning
```bash
# Install security scanning tools
pip install safety
npm install -g snyk

# Scan for vulnerabilities regularly
safety check  # Python dependencies
snyk test     # Node.js dependencies
```

---

## 📞 Communication

### Internal Notification
- [x] Security team notified
- [ ] Development team notified
- [ ] Infrastructure team notified
- [ ] Management notified (if data breach confirmed)

### External Notification
- [ ] Hetzner (hosting provider) - No response needed per their email
- [ ] BSI (certbund@bsi.bund.de) - No response needed per their email
- [ ] Users (if data breach confirmed) - GDPR requirement
- [ ] Regulators (if required by law)

---

## 📚 References

- **BSI Report:** CB-Report#20251015-10007949
- **Abuse ID:** 10818B7:1E
- **Redis Security Guide:** https://redis.io/docs/management/security/
- **BSI Advisory Info:** https://reports.cert-bund.de/en/
- **OWASP Top 10:** https://owasp.org/www-project-top-ten/

---

## ✅ Resolution Checklist

- [ ] Issue verified and reproduced
- [ ] Security fix applied
- [ ] Redis now bound to localhost only
- [ ] Strong password configured (32+ characters)
- [ ] Protected mode enabled
- [ ] Dangerous commands disabled
- [ ] Firewall configured to block port 6379
- [ ] Application updated with password
- [ ] Application tested and working
- [ ] Security verification passed
- [ ] Logs reviewed for unauthorized access
- [ ] Impact assessment completed
- [ ] Stakeholders notified (if needed)
- [ ] Security documentation updated
- [ ] Automated monitoring configured
- [ ] Post-incident review scheduled

---

## 📝 Timeline

| Time | Event | Action |
|------|-------|--------|
| Oct 14, 15:59 UTC | BSI scan detected open Redis | - |
| Oct 15, 14:29 | Notification received from Hetzner | - |
| Oct 15, 14:58 | Investigation started | Verified issue |
| Oct 15, 15:00 | Security fix prepared | Created fix scripts |
| Oct 15, TBD | Fix applied | **PENDING** |
| Oct 15, TBD | Verification completed | **PENDING** |
| Oct 15, TBD | Incident resolved | **PENDING** |

---

## 🎯 Next Steps

1. **IMMEDIATE (next 15 minutes):**
   ```bash
   sudo bash /home/adminmatej/github/applications/operator-demo-2026/scripts/fix-redis-security.sh
   ```

2. **SHORT TERM (next hour):**
   - Update application with Redis password
   - Test application functionality
   - Review logs for unauthorized access
   - Run security verification

3. **MEDIUM TERM (next day):**
   - Complete impact assessment
   - Review all other services for similar issues
   - Set up automated monitoring
   - Document lessons learned

4. **LONG TERM (next week):**
   - Implement infrastructure as code
   - Set up automated security scanning
   - Review and update security policies
   - Schedule penetration testing

---

**Status:** ⚠️ **INCIDENT OPEN - REQUIRES IMMEDIATE ACTION**

**Priority:** 🔴 **P0 - CRITICAL**

**Assigned To:** Matej Havlin

**Due Date:** October 15, 2025 (TODAY)

---

*This incident will be closed when all checklist items are completed and verified.*
