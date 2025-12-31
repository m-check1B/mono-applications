# Security Policy

**Project:** Operator Demo 2026
**Version:** 1.0
**Effective Date:** October 15, 2025
**Last Updated:** October 15, 2025

---

## 🔒 Security Principles

### Core Principles
1. **Security by Default** - All services must be secure by default
2. **Least Privilege** - Grant minimum necessary permissions
3. **Defense in Depth** - Multiple layers of security controls
4. **Zero Trust** - Never trust, always verify
5. **Privacy by Design** - Build privacy into systems from the start

---

## 🚨 Critical Security Rules (NEVER VIOLATE)

### 1. Database Security

#### Redis
- ✅ **MUST** bind to `127.0.0.1` only (never `0.0.0.0`)
- ✅ **MUST** require authentication (32+ character password)
- ✅ **MUST** enable protected mode
- ✅ **MUST** disable dangerous commands (FLUSHDB, FLUSHALL, CONFIG)
- ❌ **NEVER** expose to public Internet without authentication

#### PostgreSQL
- ✅ **MUST** set `listen_addresses = 'localhost'`
- ✅ **MUST** use strong authentication (scram-sha-256)
- ✅ **MUST** restrict connections in pg_hba.conf
- ❌ **NEVER** use trust authentication in production

#### All Databases
- ✅ **MUST** use TLS/SSL for remote connections
- ✅ **MUST** have strong passwords (16+ characters)
- ✅ **MUST** enable audit logging
- ✅ **MUST** perform regular backups

### 2. Container Security

#### Docker
- ✅ **MUST** bind services to `127.0.0.1` (not `0.0.0.0`)
- ✅ **MUST** use authentication for all services
- ✅ **MUST** use internal Docker networks
- ✅ **MUST** run as non-root user when possible
- ❌ **NEVER** expose internal services to Internet
- ❌ **NEVER** use privileged mode without justification

**Required Port Mapping:**
```yaml
# CORRECT
ports:
  - "127.0.0.1:6379:6379"

# WRONG
ports:
  - "6379:6379"  # Exposes to 0.0.0.0
```

### 3. Secrets Management

- ✅ **MUST** use environment variables for secrets
- ✅ **MUST** gitignore `.env` files
- ✅ **MUST** use secret management tools (Vault, AWS Secrets Manager)
- ✅ **MUST** rotate secrets quarterly
- ❌ **NEVER** commit secrets to git
- ❌ **NEVER** hardcode passwords in source code
- ❌ **NEVER** log secrets

**Required `.gitignore` entries:**
```
.env
.env.local
.env.*.local
*.key
*.pem
credentials.json
secrets.yaml
```

### 4. Network Security

#### Firewall
- ✅ **MUST** enable firewall (ufw/iptables)
- ✅ **MUST** use default deny for incoming
- ✅ **MUST** only allow necessary ports
- ✅ **MUST** regularly audit firewall rules

**Allowed Ports:**
- 22 (SSH) - Consider non-standard port
- 80 (HTTP) - Redirect to HTTPS
- 443 (HTTPS)

**Blocked Ports:**
- 6379 (Redis)
- 5432 (PostgreSQL)
- 3306 (MySQL)
- 27017 (MongoDB)
- 8000-9000 (Development servers)

### 5. Application Security

#### Authentication
- ✅ **MUST** use strong password hashing (bcrypt, argon2)
- ✅ **MUST** implement rate limiting
- ✅ **MUST** use HTTPS/TLS
- ✅ **MUST** validate all inputs
- ✅ **MUST** implement session management
- ❌ **NEVER** store passwords in plaintext

#### API Security
- ✅ **MUST** validate all API inputs
- ✅ **MUST** implement authentication
- ✅ **MUST** implement authorization
- ✅ **MUST** use rate limiting
- ✅ **MUST** log all API access
- ❌ **NEVER** expose debug endpoints in production

---

## 🛡️ Security Requirements by Environment

### Development
- Localhost binding acceptable
- Test credentials acceptable
- Debug logging acceptable
- Firewall optional

### Staging
- Internal network binding required
- Strong credentials required
- Info logging required
- Firewall required

### Production
- Localhost/internal binding required
- Strong credentials required (32+ chars)
- Warn logging required
- Firewall required
- TLS/SSL required
- Monitoring required
- Backups required

---

## 📋 Security Checklist

### Pre-Deployment
- [ ] All services bound to localhost or internal network
- [ ] Strong passwords configured (32+ characters)
- [ ] Protected mode enabled on all databases
- [ ] Dangerous commands disabled
- [ ] Firewall configured and enabled
- [ ] TLS/SSL certificates valid
- [ ] No secrets in git repository
- [ ] `.env` files gitignored
- [ ] Security audit completed
- [ ] Vulnerability scan passed

### Post-Deployment
- [ ] Verify services not accessible from Internet
- [ ] Verify authentication required
- [ ] Check logs for unauthorized access
- [ ] Test failover procedures
- [ ] Verify backups working
- [ ] Monitor for anomalies

### Regular Maintenance
- [ ] Update dependencies (weekly)
- [ ] Audit dependencies (weekly)
- [ ] Rotate secrets (quarterly)
- [ ] Review access logs (weekly)
- [ ] Update security policies (quarterly)
- [ ] Penetration testing (annually)

---

## 🚨 Incident Response

### Severity Levels

**P0 - Critical (Response: Immediate)**
- Data breach
- Service exposed to Internet without auth
- Active attack detected
- Total system compromise

**P1 - High (Response: 1 hour)**
- Vulnerability with active exploit
- Unauthorized access detected
- Data integrity compromised

**P2 - Medium (Response: 24 hours)**
- Vulnerability without active exploit
- Configuration issue
- Potential security gap

**P3 - Low (Response: 1 week)**
- Minor configuration issue
- Documentation update needed

### Response Procedure

1. **Detection** (0-15 minutes)
   - Identify the issue
   - Assess severity
   - Alert security team

2. **Containment** (15-60 minutes)
   - Stop the attack/exposure
   - Isolate affected systems
   - Preserve evidence

3. **Eradication** (1-4 hours)
   - Remove vulnerability
   - Apply security patch
   - Update configurations

4. **Recovery** (4-24 hours)
   - Restore services
   - Verify security
   - Monitor for recurrence

5. **Post-Incident** (24 hours - 1 week)
   - Document incident
   - Update policies
   - Implement prevention
   - Notify stakeholders if required

---

## 📞 Security Contacts

| Role | Contact | Response Time |
|------|---------|---------------|
| Security Lead | Matej Havlin | Immediate |
| Development Team | dev@operator-demo.com | 1 hour |
| Infrastructure | ops@operator-demo.com | 1 hour |

### External Contacts
- **BSI (Federal Office for Information Security):** certbund@bsi.bund.de
- **Hetzner Abuse:** abuse@hetzner.com
- **Emergency:** +49 (emergency contact)

---

## 🔍 Audit & Compliance

### Security Audits
- **Frequency:** Quarterly
- **Scope:** Full system review
- **Requirements:** All critical systems
- **Documentation:** Required

### Compliance Requirements
- **GDPR:** Data protection and privacy
- **ISO 27001:** Information security management
- **BSI Standards:** Federal security standards
- **Industry Standards:** OWASP Top 10

---

## 📊 Metrics & Reporting

### Security Metrics
- Failed login attempts
- API rate limit hits
- Firewall blocked connections
- Vulnerability scan results
- Incident response times
- Mean time to patch (MTTP)

### Reporting Requirements
- **Weekly:** Security incident summary
- **Monthly:** Vulnerability report
- **Quarterly:** Security audit
- **Annually:** Compliance review

---

## 🛠️ Approved Security Tools

### Required Tools
- **Password Manager:** 1Password, Bitwarden
- **Secret Management:** HashiCorp Vault, AWS Secrets Manager
- **Vulnerability Scanning:** Trivy, Snyk, OWASP Dependency-Check
- **Firewall:** UFW, iptables
- **Monitoring:** Prometheus, Grafana
- **Logging:** ELK Stack, CloudWatch

### Code Security
- **Git Secrets:** git-secrets, detect-secrets
- **Pre-commit Hooks:** pre-commit framework
- **SAST:** SonarQube, Bandit (Python), ESLint (JS)
- **Dependency Audit:** pip-audit, pnpm audit

---

## 🎓 Security Training

### Required Training
- **All Developers:** Security basics (annually)
- **DevOps:** Infrastructure security (annually)
- **Security Team:** Advanced training (quarterly)

### Topics
- Secure coding practices
- OWASP Top 10
- Container security
- Secrets management
- Incident response
- Privacy regulations (GDPR)

---

## 📝 Policy Updates

### Review Schedule
- **Quarterly:** Regular review
- **After Incident:** Immediate update
- **New Technology:** Before adoption
- **Regulatory Change:** As needed

### Change Process
1. Propose change
2. Security review
3. Team approval
4. Documentation update
5. Team notification
6. Training if needed

---

## ✅ Compliance Statement

By deploying to production, you certify that:
- [ ] I have read and understand this security policy
- [ ] All security requirements have been met
- [ ] All security checks have passed
- [ ] No known vulnerabilities exist
- [ ] Proper authentication is configured
- [ ] Services are not exposed to Internet inappropriately
- [ ] Secrets are properly managed
- [ ] Incident response plan is understood

---

## 📚 References

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [CIS Benchmarks](https://www.cisecurity.org/cis-benchmarks/)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
- [GDPR Compliance](https://gdpr.eu/)
- [BSI Standards](https://www.bsi.bund.de/)
- [Docker Security Best Practices](https://docs.docker.com/engine/security/)
- [Redis Security](https://redis.io/docs/management/security/)
- [PostgreSQL Security](https://www.postgresql.org/docs/current/security.html)

---

**Policy Owner:** Matej Havlin
**Approved By:** Development Team
**Effective Date:** October 15, 2025
**Next Review:** January 15, 2026

---

*This policy is binding for all team members and contractors working on this project.*
*Violations may result in access revocation and disciplinary action.*
