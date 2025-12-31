# Secret Management Tool Evaluation: Doppler vs Infisical

**Date:** 2025-12-28
**Task:** VD-255 - Evaluate secret management (Doppler vs Infisical)
**Evaluator:** darwin-opencode-builder

---

## Executive Summary

After evaluating both Doppler and Infisical for centralized secrets management for Kraliki, **Infisical is recommended** for the following reasons:
- Self-hosting capability (critical for data sovereignty)
- Open-source with no vendor lock-in
- Lower cost per identity ($18 vs $21/mo)
- More comprehensive feature set (secret scanning, PAM, certificate management)
- HIPAA compliance (valuable for healthcare clients)

---

## Doppler

### Overview
Doppler is a cloud-based secrets management platform focused on developer experience and security compliance.

### Pricing
- **Developer (Free):** Free for 3 users, $8/mo per additional user
  - 3 days activity log retention
  - 5 config syncs
  - Basic integrations
- **Team:** $21/mo per user (14-day free trial)
  - 90 days activity log retention
  - 100 config syncs
  - SAML SSO, RBAC, integration access scoping
  - Service accounts, config inheritance
  - Priority support
- **Enterprise:** Custom pricing
  - All Team features
  - Custom roles, user groups
  - Enterprise SCIM
  - 99.95% SLO, dedicated support

### Key Features
- **Secrets Management:** Centralized storage with CLI, API, SDKs
- **Integrations:** AWS, Azure, GCP, Vercel, Heroku, GitHub
- **Security:** SOC 2, ISO compliant, secret generation, MFA
- **Auditability:** Activity logs (3-90 days), webhooks, email alerts
- **Access Control:** User-based pricing, RBAC, SAML SSO, trusted IPs
- **Developer Experience:** Excellent CLI, SDKs, dashboard

### Pros
✅ Established product with large customer base (47,000+ startups)
✅ Excellent developer experience and documentation
✅ Strong compliance certifications (SOC 2, ISO)
✅ Many native integrations
✅ User-based pricing (no extra cost for machine identities)
✅ 99.99% historical uptime

### Cons
❌ SaaS-only (cannot self-host)
❌ No self-hosting option for data sovereignty
❌ Higher per-user cost ($21/mo)
❌ No secret scanning or leak prevention
❌ No certificate management
❌ No PAM (Privileged Access Management)
❌ Vendor lock-in (proprietary)

---

## Infisical

### Overview
Infisical is an open-source, end-to-end secrets management platform with both self-hosting and cloud options.

### Pricing
- **Free:** $0/mo
  - Up to 5 identities
  - Up to 3 projects
  - Up to 3 environments
  - Dashboard UI, API, CLI, SDKs
  - Kubernetes Operator
  - All integrations
  - Secret scanning and leak prevention
  - Secret sharing
  - Self-hosting or Infisical Cloud
- **Pro:** $18/identity/mo (free trial)
  - All Free features
  - Unlimited projects, environments, identities
  - Secret versioning and point-in-time recovery
  - Role-based access controls
  - Secret rotation, temporary access provisioning
  - SAML SSO, IP allowlisting
  - 90-day audit log retention
  - Priority support
- **Enterprise:** Custom pricing
  - All Pro features
  - LDAP authentication, dynamic secrets
  - AI Security Advisor, approval workflows
  - Sub-organizations, KMS/HSM support
  - 99.99% SLA, SOC 2 & penetration testing

### Key Features
- **Secrets Management:** Centralized with CLI, API, SDKs, Kubernetes Operator
- **Secret Scanning:** Automated leak prevention and scanning
- **Certificate Management:** Full X.509 certificate lifecycle management
- **SSH:** Ephemeral SSH credentials
- **KMS:** Key Management System
- **PAM:** Privileged Access Management
- **Dynamic Secrets:** On-demand secret generation, automatic rotation
- **Access Control:** RBAC, temporary access, approval workflows
- **Integrations:** AWS, Vercel, GitHub Actions, GitLab, Jenkins, Ansible, Docker, Kubernetes, Terraform

### Pros
✅ **Open-source** (no vendor lock-in)
✅ **Self-hostable** (data sovereignty, full control)
✅ Lower cost per identity ($18 vs $21/mo)
✅ More comprehensive feature set
✅ HIPAA compliant (valuable for healthcare sector clients)
✅ Secret scanning and leak prevention
✅ Certificate management (PKI)
✅ PAM (Privileged Access Management)
✅ Dynamic secrets with automatic rotation
✅ Approval workflows
✅ Strong security certifications (SOC 2, HIPAA, FIPS 140-3)
✅ Active community (3,000+ members, 12,000+ organizations)
✅ 99.99% uptime guarantee

### Cons
❌ Newer than Doppler (less mature)
❌ Smaller customer base
❌ Potentially less polished DX than Doppler

---

## Comparison Table

| Feature | Doppler | Infisical |
|----------|-----------|------------|
| **Deployment Model** | SaaS only | Self-hostable + Cloud |
| **Open Source** | No | Yes |
| **Pricing** | Free / $21/user/mo | Free / $18/identity/mo |
| **Machine Identities** | Free | Included in pricing |
| **Secret Scanning** | No | Yes |
| **Certificate Management** | No | Yes |
| **PAM** | No | Yes |
| **Dynamic Secrets** | No | Yes |
| **Approval Workflows** | No | Yes |
| **Compliance** | SOC 2, ISO | SOC 2, HIPAA, FIPS 140-3 |
| **Self-hosting** | No | Yes |
| **Kubernetes Operator** | No | Yes |
| **Integrations** | AWS, Azure, GCP, Vercel, Heroku, GitHub | AWS, Vercel, GitHub, GitLab, Jenkins, Ansible, Docker, K8s, Terraform |
| **Audit Log Retention** | 3-90 days | 90 days (Pro/Enterprise) |
| **CLI** | Yes | Yes |
| **SDKs** | Yes | Yes |
| **Webhooks** | Yes | Yes |
| **Secret Referencing** | Yes | Yes |
| **RBAC** | Yes | Yes |
| **SSO** | SAML | SAML |
| **Temporary Access** | No | Yes |
| **Secret Rotation** | API-based | Automatic + API-based |

---

## Recommendation: Infisical

### Primary Reasons

1. **Self-Hosting Capability**
   - Kraliki values data sovereignty and control
   - Ability to host on own infrastructure aligns with long-term strategy
   - Avoids vendor lock-in

2. **Open Source**
   - Community-driven development
   - Ability to audit and modify code
   - No proprietary dependencies

3. **Cost-Effective**
   - $18/identity/mo vs $21/user/mo (14% savings)
   - For 20 developers: $360/mo vs $420/mo = $60/mo savings

4. **Superior Feature Set**
   - Secret scanning (prevents leaks before deployment)
   - Certificate management (unified PKI)
   - PAM (privileged access control)
   - Dynamic secrets (automatic rotation)
   - Approval workflows (team collaboration)

5. **Stronger Compliance**
   - HIPAA certification (healthcare clients like SenseIt)
   - FIPS 140-3 (government/enterprise)
   - SOC 2 + continuous penetration testing

### Risk Mitigation

**Concern:** Infisical is newer than Doppler

**Mitigation:**
- Start with Pro tier (14-day trial, then $18/identity/mo)
- If issues arise, migration to Doppler is straightforward (both use similar patterns)
- Can self-host to control updates and stability
- Active community support (Slack, 12,000+ organizations)

### Implementation Plan

1. **Phase 1 (Immediate - 1 week)**
   - Sign up for Infisical Pro trial
   - Create project for dashboard application
   - Set up environments (dev, staging, production)
   - Test CLI and SDK integration
   - Evaluate developer experience

2. **Phase 2 (Migration - 2-3 weeks)**
   - Export secrets from current .env files
   - Import into Infisical
   - Update ecosystem.config.js to fetch secrets from Infisical
   - Test all applications with new secrets source
   - Remove .env files from git

3. **Phase 3 (Self-Hosting - 1 month, optional)**
   - Deploy Infisical to own infrastructure (Hetzner/Docker)
   - Configure backups and monitoring
   - Migrate from Infisical Cloud to self-hosted
   - Establish SLA and monitoring

4. **Phase 4 (Advanced Features - 2 weeks, optional)**
   - Enable secret scanning
   - Set up secret rotation for critical credentials
   - Configure approval workflows for production changes
   - Implement PAM for infrastructure access

---

## Next Steps

1. **Immediate Action (Today)**
   - Store this evaluation in darwin-opencode-builder memory
   - Post recommendation to blackboard
   - Mark VD-255 as complete in task queue

2. **Short Term (This Week)**
   - Create Linear issue for Infisical implementation
   - Begin Phase 1 trial
   - Gather team feedback

3. **Long Term (Next Quarter)**
   - Full migration to Infisical
   - Remove all .env files from repositories
   - Establish secrets management best practices

---

## Conclusion

**Infisical is the recommended choice** for Kraliki's centralized secrets management needs due to:
- Self-hosting capability (critical)
- Open-source (no lock-in)
- Lower cost ($60/mo savings for 20 developers)
- Superior features (scanning, PAM, dynamic secrets)
- Stronger compliance (HIPAA, FIPS 140-3)

The primary risk (newer product) is mitigated by:
- Pro tier trial period
- Straightforward migration path
- Active community support
- Self-hosting option for stability

**Estimated Cost Savings:** $60/month ($720/year) for a 20-person team

**Time to Implement:** 4-6 weeks for full migration

---

*Evaluation completed by darwin-opencode-builder on 2025-12-28*
