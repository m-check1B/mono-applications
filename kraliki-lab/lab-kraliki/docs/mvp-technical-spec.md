# Lab by Kraliki - Technical MVP Specification

**Source:** Codex consultation (Dec 2, 2025)

---

## MVP Scope (Ship in ~28-30 hours)

### What's Included

| Component | Description | Effort |
|-----------|-------------|--------|
| VM Image | Pre-configured Hetzner CPX31 | 4h |
| CLIProxyAPI | Unified AI gateway (Claude/GPT/Gemini) | Already built |
| Claude Code | Orchestrator CLI | 2h config |
| Gemini CLI | Worker #1 (frontend/research) | 2h config |
| Codex CLI | Worker #2 (audit/backend) | 2h config |
| mgrep | Semantic memory/search | 4h setup |
| Auth Layer | JWT + Traefik middleware | 4h |
| Starter Script | One-command setup | 4h |
| Documentation | Setup + first workflow | 4h |

**Total estimate:** 28-30 hours

### What's NOT in MVP

- Dashboard/UI (CLI only)
- Usage metering
- Billing integration
- Multi-tenant isolation
- Auto-scaling

---

## Infrastructure Spec

### VM Size: Hetzner CPX31

| Resource | Spec |
|----------|------|
| vCPUs | 4 |
| RAM | 8 GB |
| Storage | 160 GB NVMe |
| Traffic | 20 TB |
| Price | ~€30/mo |

**Capacity:** 1-3 concurrent users

### Scale Path

| Usage Level | VM Type | Price |
|-------------|---------|-------|
| Single user | CPX21 | €15/mo |
| Light team (1-3) | CPX31 | €30/mo |
| Heavy team (3-6) | CPX41 | €60/mo |
| Enterprise | Dedicated | Custom |

---

## Security Architecture

### Auth Flow

```
User → Traefik → JWT Validation → CLIProxyAPI → AI Providers
```

### Required Security Layers

| Layer | Implementation | Priority |
|-------|---------------|----------|
| API Auth | JWT tokens via Traefik middleware | HIGH |
| Network | Firewall rules, SSH only from allowed IPs | HIGH |
| Sandboxing | nsjail or bubblewrap per session | MEDIUM |
| Rate Limiting | Traefik rate limiter | MEDIUM |
| Secrets | HashiCorp Vault or encrypted env files | LOW (MVP) |

### Risk Mitigations

| Risk | Mitigation |
|------|-----------|
| Command injection | Sandboxed execution environment |
| API key exposure | Keys in Vault, rotated monthly |
| Resource exhaustion | Per-user resource limits |
| Data leakage | Tenant isolation, encrypted storage |

---

## Deployment Script

### One-Click Setup Goal

```bash
curl -fsSL https://magic-box.dev/install.sh | bash
```

### Script Flow

1. Verify Hetzner VM specs
2. Install Docker + Docker Compose
3. Pull pre-built images
4. Configure API keys (prompt user)
5. Generate JWT secrets
6. Start all services
7. Run health check
8. Print access credentials

### Manual Steps (Cannot Automate)

1. User provides their API keys (Claude, GPT, Gemini)
2. User sets up DNS (optional, for custom domain)
3. User configures SSH access

---

## Observability Stack

### Day 1 Requirements

| Tool | Purpose | Priority |
|------|---------|----------|
| Prometheus | Metrics collection | HIGH |
| Loki | Log aggregation | HIGH |
| Grafana | Dashboards | MEDIUM |
| Alertmanager | Critical alerts | MEDIUM |

### Key Metrics to Track

- API request latency (by provider)
- Token usage (by user/session)
- Error rates (by type)
- VM resource utilization
- Session duration

---

## File Structure

```
/opt/magic-box/
├── docker-compose.yml
├── .env                    # API keys, secrets
├── traefik/
│   ├── traefik.yml
│   └── dynamic/
│       └── middleware.yml  # JWT auth
├── cli-proxy/
│   └── config.yml          # Model routing
├── mgrep/
│   ├── data/               # Vector store
│   └── config.yml
├── prompts/                # Prompt library
│   ├── orchestrator/
│   ├── research/
│   └── coding/
├── patterns/               # Workflow patterns
│   ├── build-audit-fix.md
│   ├── parallel-execution.md
│   └── hard-problem-voting.md
└── logs/                   # Execution logs
```

---

## API Key Requirements

### User Must Provide

| Provider | Required | Purpose |
|----------|----------|---------|
| Anthropic (Claude) | Yes | Orchestrator |
| OpenAI | Optional | Codex worker |
| Google (Gemini) | Optional | Gemini worker |

### Our Keys (If Offering Unified Billing)

- Single API key covers all providers
- Markup on token usage
- Simplifies customer onboarding

---

## First Workflow: "Build & Audit"

### Pattern

```
User Input → Opus (plan) → Gemini (build) → Codex (audit) → Opus (fix) → Output
```

### Demo Flow

1. User: "Build me a landing page for my SaaS"
2. Opus: Plans structure, sections, copy approach
3. Gemini: Generates HTML + CSS + content
4. Codex: Audits for accessibility, performance, SEO
5. Opus: Incorporates audit feedback
6. Output: Production-ready landing page

### Success Metric

Time to first working output < 15 minutes

---

## Go/No-Go Checklist

### Before First Beta

- [ ] VM image tested and documented
- [ ] Setup script runs without errors
- [ ] All three CLIs (Claude, Gemini, Codex) respond
- [ ] mgrep indexes and searches correctly
- [ ] JWT auth blocks unauthorized requests
- [ ] Basic monitoring shows system health
- [ ] Recovery procedure documented (VM dies)
- [ ] One complete workflow demonstrated end-to-end

---

*Consultation: Dec 2, 2025*
