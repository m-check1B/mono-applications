# Deployment Security Checklist

**Project:** Operator Demo 2026
**Version:** 1.0
**Last Updated:** October 15, 2025

---

## 🚀 Pre-Deployment Security Checklist

### Critical Security Items (P0)

#### Network Security
- [ ] **Verify port bindings:** All database ports bound to `127.0.0.1` only
  ```bash
  docker ps | grep -E "6379|5432|3306|27017"
  # Should show 127.0.0.1:PORT or no host port
  ```

- [ ] **Verify firewall configured:** UFW/iptables blocking database ports
  ```bash
  sudo ufw status verbose
  # Should show 6379, 5432 blocked or not listed
  ```

- [ ] **Verify Internet accessibility:** Database ports NOT accessible externally
  ```bash
  # From external machine:
  nc -zv YOUR_PUBLIC_IP 6379
  # Should FAIL to connect
  ```

#### Authentication
- [ ] **Redis password configured:** 32+ characters
  ```bash
  docker exec operator-demo-redis redis-cli ping
  # Should return: (error) NOAUTH Authentication required
  ```

- [ ] **PostgreSQL password configured:** Strong password in .env
  ```bash
  grep POSTGRES_PASSWORD backend/.env
  # Should show strong password
  ```

- [ ] **Application credentials:** All .env files configured
  ```bash
  ls -la backend/.env frontend/.env
  # Files should exist and not be empty
  ```

#### Secrets Management
- [ ] **No secrets in git:** Check git history for secrets
  ```bash
  git log --all --full-history -- "*.env" "*.key" "*.pem"
  # Should show no results or only deletions
  ```

- [ ] **.env files gitignored:** Verify .gitignore
  ```bash
  git check-ignore backend/.env frontend/.env
  # Should show both files are ignored
  ```

- [ ] **No hardcoded secrets:** Search codebase
  ```bash
  grep -r "password.*=.*['\"]" --include="*.py" --include="*.ts" --exclude-dir=node_modules
  # Should show no hardcoded passwords
  ```

### High Priority Items (P1)

#### Container Security
- [ ] **Health checks enabled:** All containers have health checks
  ```bash
  docker ps --format "{{.Names}}" | xargs -I {} docker inspect {} --format '{{.Name}}: {{.State.Health.Status}}'
  ```

- [ ] **Resource limits set:** CPU and memory limits configured
  ```bash
  docker stats --no-stream
  ```

- [ ] **Non-root users:** Containers not running as root
  ```bash
  docker ps -q | xargs docker inspect --format '{{.Name}}: {{.Config.User}}'
  ```

#### Application Security
- [ ] **Dependencies updated:** No critical vulnerabilities
  ```bash
  cd backend && pip audit
  cd frontend && pnpm audit
  ```

- [ ] **TLS/SSL configured:** HTTPS enabled for production
  ```bash
  curl -I https://yourdomain.com
  # Should return 200 with TLS certificate
  ```

- [ ] **Rate limiting enabled:** API has rate limiting
  ```bash
  # Test by making multiple rapid requests
  for i in {1..100}; do curl -I http://localhost:8000/api/test; done
  # Should eventually return 429 Too Many Requests
  ```

### Medium Priority Items (P2)

#### Monitoring & Logging
- [ ] **Logging enabled:** Application logs to files/stdout
- [ ] **Log rotation configured:** Logs don't fill disk
- [ ] **Monitoring configured:** Metrics collection enabled
- [ ] **Alerts configured:** Critical alerts set up

#### Backup & Recovery
- [ ] **Backup strategy:** Database backups configured
- [ ] **Backup tested:** Restore procedure tested
- [ ] **Disaster recovery plan:** Documented and tested

#### Documentation
- [ ] **Security policies:** All policies documented
- [ ] **Deployment guide:** Step-by-step instructions
- [ ] **Incident response:** Response procedures documented
- [ ] **Runbook:** Operational procedures documented

---

## 🔐 Post-Deployment Verification

### Immediate Verification (Within 1 hour)

1. **Verify Services Running**
   ```bash
   docker ps
   # All containers should be "Up" and "healthy"
   ```

2. **Test Application**
   ```bash
   curl http://localhost:8000/health
   # Should return 200 OK
   ```

3. **Check Logs for Errors**
   ```bash
   docker logs operator-demo-redis --tail 50
   docker logs operator-demo-postgres --tail 50
   docker logs operator-demo-backend --tail 50
   ```

4. **Run Security Verification**
   ```bash
   bash scripts/verify-redis-security.sh
   # Should show: ✓ ALL CHECKS PASSED
   ```

5. **Test Authentication**
   ```bash
   # Redis
   docker exec operator-demo-redis redis-cli ping
   # Should require password

   # PostgreSQL
   docker exec operator-demo-postgres psql -U postgres -c "SELECT 1"
   # Should require password
   ```

### Extended Verification (Within 24 hours)

1. **Monitor Resource Usage**
   ```bash
   docker stats --no-stream
   # Check CPU, memory within limits
   ```

2. **Review Access Logs**
   ```bash
   tail -100 /var/log/nginx/access.log
   # Check for unusual patterns
   ```

3. **Test Failover**
   ```bash
   # Restart containers to test auto-recovery
   docker restart operator-demo-redis
   # Application should reconnect automatically
   ```

4. **Test Backup & Restore**
   ```bash
   # Trigger backup
   # Verify backup file created
   # Test restore on test instance
   ```

---

## 🚨 Rollback Procedure

If deployment fails security checks:

1. **Stop New Deployment**
   ```bash
   docker-compose down
   ```

2. **Restore Previous Version**
   ```bash
   # Restore from backup containers
   docker rename operator-demo-redis-backup operator-demo-redis
   docker start operator-demo-redis
   ```

3. **Verify Rollback**
   ```bash
   docker ps
   bash scripts/verify-redis-security.sh
   ```

4. **Document Issue**
   - What failed
   - Why it failed
   - Steps to fix
   - Prevention measures

---

## 📋 Environment-Specific Checklists

### Development Environment
- [ ] Port bindings can be `0.0.0.0` (local only)
- [ ] Weak passwords acceptable
- [ ] Debug logging enabled
- [ ] Source maps enabled
- [ ] Test data loaded

### Staging Environment
- [ ] Port bindings `127.0.0.1` only
- [ ] Strong passwords required
- [ ] Info logging enabled
- [ ] No source maps
- [ ] Production-like data
- [ ] External access for testing team

### Production Environment
- [ ] Port bindings `127.0.0.1` only
- [ ] Strong passwords (32+ chars)
- [ ] Warn/error logging only
- [ ] No debug endpoints
- [ ] No source maps
- [ ] Real data
- [ ] Monitoring enabled
- [ ] Backups automated
- [ ] Firewall strictly configured
- [ ] TLS/SSL required

---

## 🎯 Quick Reference

### Critical Commands

**Check Port Bindings:**
```bash
ss -tulpn | grep -E "6379|5432|3306|27017"
```

**Check Docker Containers:**
```bash
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

**Run All Security Checks:**
```bash
bash scripts/verify-redis-security.sh
bash scripts/verify-postgres-security.sh  # If exists
```

**Check Firewall:**
```bash
sudo ufw status verbose
```

**Test External Access (should FAIL):**
```bash
nc -zv YOUR_PUBLIC_IP 6379
nc -zv YOUR_PUBLIC_IP 5432
```

---

## 📞 Emergency Contacts

If security checks fail:

1. **Stop deployment immediately**
2. **Contact security lead:** Matej Havlin
3. **Document the issue**
4. **Do not proceed until resolved**

---

## ✅ Sign-Off

**Deployment Date:** _______________
**Deployed By:** _______________
**Verified By:** _______________

I certify that:
- [ ] All critical security checks have passed
- [ ] All port bindings are secure
- [ ] Authentication is properly configured
- [ ] No secrets are exposed
- [ ] Services are not accessible from Internet
- [ ] Verification scripts have passed
- [ ] Rollback procedure is understood
- [ ] Incident response plan is ready

**Signature:** _______________
**Date:** _______________

---

**Next Review:** Within 24 hours of deployment
**Next Audit:** Within 1 week of deployment
