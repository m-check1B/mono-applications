# Security Policies

**Operator Demo 2026**
**Version:** 1.0
**Effective Date:** October 15, 2025

---

## 📋 Policy Overview

This directory contains all security policies for the Operator Demo 2026 project. These policies are **mandatory** and must be followed for all deployments, development, and operations.

---

## 📚 Policy Documents

### 1. [Security Policy](SECURITY_POLICY.md) ⭐ **START HERE**
**Primary security policy document**

Contains:
- Critical security rules (NEVER VIOLATE)
- Database security requirements
- Container security requirements
- Secrets management
- Network security
- Incident response procedures
- Compliance requirements

**When to read:** Before any deployment, when handling security incidents

---

### 2. [Docker Security Policy](DOCKER_SECURITY_POLICY.md)
**Container-specific security requirements**

Contains:
- Port binding requirements
- Authentication configuration
- Network isolation
- Resource limits
- Security verification
- Secure docker-compose template

**When to read:** Before deploying Docker containers, when writing docker-compose.yml

---

### 3. [Deployment Checklist](DEPLOYMENT_CHECKLIST.md)
**Pre and post-deployment verification**

Contains:
- Pre-deployment security checklist
- Post-deployment verification steps
- Environment-specific requirements
- Rollback procedures
- Quick reference commands

**When to read:** Before EVERY deployment, during deployment verification

---

## 🚨 Critical Rules Summary

### Port Binding (P0 - CRITICAL)
```yaml
# ✅ CORRECT
ports:
  - "127.0.0.1:6379:6379"

# ❌ WRONG - Exposes to Internet
ports:
  - "6379:6379"
```

### Authentication (P0 - CRITICAL)
- ✅ All databases MUST require authentication
- ✅ Passwords MUST be 32+ characters
- ✅ Protected mode MUST be enabled

### Secrets Management (P0 - CRITICAL)
- ❌ NEVER commit secrets to git
- ✅ ALWAYS use .env files (gitignored)
- ✅ ALWAYS use environment variables

### Network Security (P0 - CRITICAL)
- ❌ NEVER expose database ports to Internet
- ✅ ALWAYS bind to 127.0.0.1 or internal network
- ✅ ALWAYS use firewall

---

## 🎯 Quick Start

### For Developers

1. **Read:** [Security Policy](SECURITY_POLICY.md) (15 minutes)
2. **Understand:** Critical security rules
3. **Follow:** Docker security requirements
4. **Verify:** Run security checks before committing

### For DevOps

1. **Read:** All three policy documents (30 minutes)
2. **Follow:** [Deployment Checklist](DEPLOYMENT_CHECKLIST.md) for every deployment
3. **Verify:** Run all security verification scripts
4. **Monitor:** Regular security audits

### For Security Team

1. **Maintain:** Keep policies updated
2. **Audit:** Regular compliance checks
3. **Respond:** Handle security incidents
4. **Train:** Educate team on security

---

## 📖 Related Documentation

### Project Documentation
- **`.claude/claude.md`** - Claude Code security guidelines
- **`SECURITY_INCIDENT_2025-10-15.md`** - Redis incident report
- **`SECURITY_FIX_COMPLETE.md`** - Incident resolution summary

### Scripts
- **`scripts/verify-redis-security.sh`** - Redis security verification
- **`scripts/fix-docker-redis.sh`** - Redis security fix
- **`scripts/find-redis.sh`** - Redis installation diagnostic

---

## 🔍 Policy Compliance

### Before Deployment
- [ ] Read relevant policies
- [ ] Complete deployment checklist
- [ ] Run verification scripts
- [ ] Get security approval

### During Deployment
- [ ] Follow deployment procedures
- [ ] Verify each step
- [ ] Document any issues
- [ ] Complete post-deployment checks

### After Deployment
- [ ] Verify all security checks passed
- [ ] Monitor for 24 hours
- [ ] Document deployment
- [ ] Update policies if needed

---

## 🚨 Security Incidents

### Incident History

#### October 15, 2025 - Redis Exposure (RESOLVED)
- **Severity:** P0 - Critical
- **Issue:** Redis exposed to Internet without authentication
- **Resolution:** Container reconfigured with secure settings
- **Status:** ✅ Resolved
- **Documentation:** See `SECURITY_INCIDENT_2025-10-15.md`

**Lessons Learned:**
1. Always bind to 127.0.0.1, never 0.0.0.0
2. Always enable authentication
3. Verify port bindings after deployment
4. Run verification scripts regularly

---

## 📞 Contacts

### Security Questions
- **Security Lead:** Matej Havlin
- **DevOps:** ops@operator-demo.com
- **Development:** dev@operator-demo.com

### External Contacts
- **BSI:** certbund@bsi.bund.de
- **Hetzner:** abuse@hetzner.com

---

## 🔄 Policy Updates

### How to Update Policies

1. **Identify need** for policy change
2. **Propose change** via pull request
3. **Security review** by security team
4. **Team approval** required
5. **Update documentation**
6. **Notify team** of changes
7. **Train if needed**

### Review Schedule
- **Quarterly:** Regular review
- **After incident:** Immediate update
- **New technology:** Before adoption

---

## 🎓 Training

### Required Reading
- All developers: Security Policy
- DevOps: All policies
- Security team: All policies + external references

### Training Schedule
- **Onboarding:** Read all policies
- **Quarterly:** Security refresher
- **After incident:** Incident-specific training
- **New policy:** Policy overview

---

## ✅ Compliance Certification

By deploying to production, you certify:
- [ ] I have read and understood all applicable policies
- [ ] All security requirements have been met
- [ ] All verification checks have passed
- [ ] I understand the incident response procedures
- [ ] I agree to follow these policies

---

## 📊 Policy Metrics

### Compliance Metrics
- Policy violations: 0 (target)
- Security incidents: Track and trend
- Time to patch: < 1 hour (critical)
- Audit pass rate: 100% (target)

### Regular Reviews
- Weekly: Deployment checklist compliance
- Monthly: Policy adherence audit
- Quarterly: Policy effectiveness review
- Annually: Comprehensive security audit

---

## 📚 External References

### Security Standards
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [CIS Benchmarks](https://www.cisecurity.org/cis-benchmarks/)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)

### Compliance
- [GDPR](https://gdpr.eu/)
- [ISO 27001](https://www.iso.org/isoiec-27001-information-security.html)
- [BSI Standards](https://www.bsi.bund.de/)

### Technology-Specific
- [Docker Security](https://docs.docker.com/engine/security/)
- [Redis Security](https://redis.io/docs/management/security/)
- [PostgreSQL Security](https://www.postgresql.org/docs/current/security.html)

---

## 🆘 Emergency Procedures

### Security Incident
1. **Stop** - Halt deployment/system
2. **Assess** - Determine severity
3. **Contain** - Isolate affected systems
4. **Document** - Record all actions
5. **Fix** - Apply security patch
6. **Verify** - Test the fix
7. **Report** - Notify stakeholders
8. **Learn** - Update policies

### Contact for Emergency
- **Immediate:** Matej Havlin
- **Escalation:** Security team
- **External:** BSI, Hetzner

---

**Policy Owner:** Security Team
**Approved By:** Development Team
**Effective Date:** October 15, 2025
**Next Review:** January 15, 2026

---

*These policies are mandatory for all team members and contractors.*
*Violations may result in access revocation and disciplinary action.*
*Questions? Contact the security team.*
