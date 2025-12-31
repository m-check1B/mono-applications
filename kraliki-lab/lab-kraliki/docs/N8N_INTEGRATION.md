# Lab by Kraliki + n8n Integration

**Version:** 1.0
**Last Updated:** 2025-12-21

---

## Overview

n8n is a workflow automation platform that extends Lab by Kraliki capabilities beyond AI orchestration. While Lab by Kraliki excels at multi-AI agent coordination, n8n handles:

- External system integrations (CRM, email, databases)
- Scheduled automation (cron jobs, periodic tasks)
- Webhook triggers (GitHub, Stripe, custom APIs)
- Data pipelines between services

Together, they create a comprehensive automation platform.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    LAB BY KRALIKI + n8n STACK                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   LAB BY KRALIKI (AI Orchestration)                               │
│   ├── Claude Opus (orchestrator)                             │
│   ├── Gemini CLI (frontend/research worker)                  │
│   ├── Codex CLI (audit/backend worker)                       │
│   └── mgrep (semantic memory)                                │
│                                                              │
│   ↕ HTTP/Webhook Communication ↕                             │
│                                                              │
│   n8n (Workflow Automation)                                  │
│   ├── Visual workflow builder                                │
│   ├── 300+ integrations (Slack, Gmail, GitHub, etc.)         │
│   ├── Scheduled triggers                                     │
│   └── Webhook endpoints                                      │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 1. Workflow Orchestration

### How Lab by Kraliki and n8n Work Together

| Component | Role |
|-----------|------|
| Lab by Kraliki | Complex reasoning, multi-step AI tasks, code generation |
| n8n | Trigger workflows, route data, call external APIs |

### Example: Automated Code Review Pipeline

```
1. GitHub webhook triggers n8n workflow
2. n8n fetches PR details, sends to Lab by Kraliki
3. Lab by Kraliki runs multi-agent review:
   - Claude Opus: Architecture review
   - Codex CLI: Security audit
   - Gemini CLI: Documentation check
4. n8n posts results back to GitHub PR
5. n8n notifies team on Slack
```

### n8n Workflow Template

```json
{
  "name": "Lab by Kraliki Code Review",
  "nodes": [
    {
      "type": "n8n-nodes-base.webhook",
      "parameters": {
        "path": "github-pr",
        "method": "POST"
      }
    },
    {
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "url": "http://127.0.0.1:5001/magic-box/review",
        "method": "POST",
        "bodyParameters": {
          "pr_url": "={{$json.pull_request.html_url}}",
          "diff": "={{$json.pull_request.diff_url}}"
        }
      }
    },
    {
      "type": "n8n-nodes-base.github",
      "parameters": {
        "operation": "createComment",
        "body": "={{$json.review_result}}"
      }
    }
  ]
}
```

---

## 2. External System Integration

n8n provides 300+ pre-built integrations that Lab by Kraliki can leverage:

### Supported Integrations

| Category | Examples | Use Case |
|----------|----------|----------|
| **Communication** | Slack, Discord, Telegram, Email | Notifications, alerts, reports |
| **Development** | GitHub, GitLab, Jira, Linear | Issue tracking, PR automation |
| **Data** | PostgreSQL, MongoDB, Airtable | Data sync, backups, ETL |
| **Marketing** | HubSpot, Mailchimp, Notion | Lead management, content |
| **Finance** | Stripe, QuickBooks, Invoice Ninja | Billing, reporting |
| **Cloud** | AWS, Google Cloud, Azure | Infrastructure automation |

### Integration Patterns

#### Pattern 1: CRM Sync

```
New lead in HubSpot
  → n8n triggers
  → Lab by Kraliki enriches with AI research
  → n8n updates HubSpot with insights
```

#### Pattern 2: Support Automation

```
Customer email arrives
  → n8n parses email
  → Lab by Kraliki generates draft response
  → n8n routes to agent or auto-replies
```

#### Pattern 3: Reporting Pipeline

```
Scheduled trigger (daily 9am)
  → n8n collects data from multiple sources
  → Lab by Kraliki generates analysis
  → n8n sends report via email/Slack
```

---

## 3. Scheduled Automation

n8n handles time-based triggers that launch Lab by Kraliki workflows.

### Common Schedules

| Schedule | Use Case | n8n Cron |
|----------|----------|----------|
| Every hour | System health checks | `0 * * * *` |
| Daily 9am | Morning briefings | `0 9 * * *` |
| Weekly Monday | Sprint summaries | `0 9 * * 1` |
| Monthly 1st | Invoice generation | `0 9 1 * *` |

### Example: Daily Digest Workflow

```json
{
  "name": "Lab by Kraliki Daily Digest",
  "nodes": [
    {
      "type": "n8n-nodes-base.cron",
      "parameters": {
        "cronExpression": "0 9 * * *"
      }
    },
    {
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "url": "http://127.0.0.1:5001/magic-box/digest",
        "method": "POST"
      }
    },
    {
      "type": "n8n-nodes-base.slack",
      "parameters": {
        "channel": "#daily-updates",
        "text": "={{$json.digest}}"
      }
    }
  ]
}
```

### Scheduling Best Practices

1. **Avoid peak hours** - Schedule heavy jobs during off-peak times
2. **Use timezone awareness** - Set `GENERIC_TIMEZONE=Europe/Prague` in n8n config
3. **Add jitter** - For multiple jobs, stagger by 5-10 minutes
4. **Include retry logic** - Use n8n's built-in retry on failure

---

## 4. Webhook Triggers

Webhooks enable real-time event-driven automation.

### Setting Up Webhooks

n8n exposes webhook endpoints at:
```
http://127.0.0.1:5678/webhook/{path}
http://127.0.0.1:5678/webhook-test/{path}  (for testing)
```

### Common Webhook Sources

| Source | Events | Lab by Kraliki Action |
|--------|--------|------------------|
| GitHub | Push, PR, Issue | Code review, documentation |
| Stripe | Payment, Subscription | Customer onboarding |
| Slack | Message, Reaction | Team requests, support |
| Custom Apps | Any HTTP POST | Application-specific |

### Example: GitHub Push Webhook

1. **Configure GitHub webhook:**
   ```
   URL: https://your-domain.com/webhook/github-push
   Content type: application/json
   Secret: [your-secret]
   Events: Push
   ```

2. **n8n workflow:**
   ```json
   {
     "nodes": [
       {
         "type": "n8n-nodes-base.webhook",
         "parameters": {
           "path": "github-push",
           "authentication": "headerAuth",
           "headerAuthName": "X-Hub-Signature-256"
         }
       },
       {
         "type": "n8n-nodes-base.if",
         "parameters": {
           "conditions": {
             "string": [{
               "value1": "={{$json.ref}}",
               "value2": "refs/heads/main"
             }]
           }
         }
       },
       {
         "type": "n8n-nodes-base.httpRequest",
         "parameters": {
           "url": "http://127.0.0.1:5001/magic-box/deploy-check",
           "method": "POST"
         }
       }
     ]
   }
   ```

### Webhook Security

1. **Always verify signatures** - Use n8n's built-in header auth
2. **Bind to localhost** - n8n runs on `127.0.0.1:5678`
3. **Use Traefik/nginx for external access** - TLS termination, rate limiting
4. **Log all webhook events** - For debugging and audit trails

---

## Configuration

### n8n Docker Setup

Located at `/github/infra/compose/n8n.yml`:

```bash
# Start n8n
docker compose -f /home/adminmatej/github/infra/compose/n8n.yml up -d

# Check status
docker compose -f /home/adminmatej/github/infra/compose/n8n.yml ps

# View logs
docker compose -f /home/adminmatej/github/infra/compose/n8n.yml logs -f
```

### Connecting n8n to Lab by Kraliki

1. **Lab by Kraliki exposes API endpoints** (via CLIProxyAPI or custom server)
2. **n8n calls these endpoints** using HTTP Request node
3. **Results flow back** to n8n for routing to other systems

### Environment Variables

```env
# n8n configuration
N8N_HOST=127.0.0.1
N8N_PORT=5678
N8N_PROTOCOL=http
WEBHOOK_URL=http://127.0.0.1:5678/
GENERIC_TIMEZONE=Europe/Prague

# Lab by Kraliki API (if custom endpoint exists)
MAGIC_BOX_API_URL=http://127.0.0.1:5001
```

---

## Use Cases for Lab by Kraliki Customers

### Tier: Starter (Freelancers)

| Workflow | Description |
|----------|-------------|
| Email triage | Auto-categorize and draft responses |
| Social media posting | Generate and schedule content |
| Invoice reminders | Automated follow-ups |

### Tier: Pro (Agencies)

| Workflow | Description |
|----------|-------------|
| Client onboarding | Automated setup, welcome emails |
| Project kickoff | Create repos, tasks, docs |
| Weekly reporting | Auto-generate client reports |

### Tier: Enterprise

| Workflow | Description |
|----------|-------------|
| Multi-system sync | CRM, ERP, project management |
| Compliance automation | Audit logs, data retention |
| Custom integrations | Proprietary systems |

---

## Troubleshooting

### n8n Won't Start

```bash
# Check logs
docker logs n8n

# Reset data (caution: deletes workflows)
docker compose -f /github/infra/compose/n8n.yml down -v
docker compose -f /github/infra/compose/n8n.yml up -d
```

### Webhook Not Receiving Events

1. Verify n8n is running: `curl http://127.0.0.1:5678/healthz`
2. Check webhook URL is correct in source system
3. Use webhook-test endpoint for debugging
4. Check n8n execution logs for errors

### Lab by Kraliki Connection Failed

1. Verify Lab by Kraliki API is running
2. Check network connectivity: `curl http://127.0.0.1:5001/health`
3. Review n8n HTTP Request node configuration
4. Check for firewall/security group issues

---

## Roadmap

### Phase 1 (Current)

- [x] n8n infrastructure setup
- [x] Basic webhook integration
- [x] Documentation

### Phase 2 (Q1 2026)

- [ ] Pre-built workflow templates
- [ ] Lab by Kraliki API endpoint standardization
- [ ] Customer workflow library

### Phase 3 (Q2 2026)

- [ ] n8n as optional Lab by Kraliki add-on
- [ ] Workflow marketplace integration
- [ ] Custom n8n nodes for Lab by Kraliki

---

## Related Documentation

- [Lab by Kraliki README](/github/applications/kraliki-lab/lab-kraliki/README.md)
- [n8n Docker Config](/github/infra/compose/n8n.yml)
- [Port Registry](/github/infra/PORT_REGISTRY.md)
- [Competitive Analysis](/github/applications/kraliki-lab/lab-kraliki/docs/competitive-analysis.md)

---

*n8n extends Lab by Kraliki from AI orchestration to full business automation.*
