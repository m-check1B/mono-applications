# Kraliki <-> n8n Integration

**Status:** LIVE
**Port:** 8198 (Kraliki API) / 5678 (n8n)
**Created:** 2025-12-22

---

## Overview

This integration allows bidirectional communication between Kraliki (AI agent swarm) and n8n (workflow automation):

- **Kraliki -> n8n**: Agents trigger workflows via webhooks when tasks complete
- **n8n -> Kraliki**: Workflows call Kraliki API to spawn agents, post messages, manage tasks

---

## Architecture

```
┌─────────────────────┐          ┌─────────────────────┐
│      KRALIKI        │          │        n8n          │
│                     │          │                     │
│  ┌───────────────┐  │   HTTP   │  ┌───────────────┐  │
│  │ n8n_client.py │──┼──────────┼──│   Webhooks    │  │
│  └───────────────┘  │  POST    │  └───────────────┘  │
│                     │          │                     │
│  ┌───────────────┐  │   HTTP   │  ┌───────────────┐  │
│  │  n8n_api.py   │──┼──────────┼──│  HTTP Request │  │
│  │   :8198       │  │   GET    │  │     Node      │  │
│  └───────────────┘  │  POST    │  └───────────────┘  │
│                     │          │                     │
└─────────────────────┘          └─────────────────────┘
```

---

## Quick Start

### 1. Check Services Running

```bash
# Both should be online
pm2 list | grep -E "kraliki-n8n-api|n8n"

# Health checks
curl http://127.0.0.1:8198/health  # Kraliki API
curl http://127.0.0.1:5678/healthz # n8n
```

### 2. n8n Calling Kraliki

In n8n, use an "HTTP Request" node:

```
Method: POST
URL: http://127.0.0.1:8198/blackboard/post
Headers: Content-Type: application/json
Body:
{
  "author": "n8n-workflow",
  "message": "Automated task complete!",
  "topic": "general"
}
```

### 3. Kraliki Calling n8n

First, register a webhook in n8n, then configure Kraliki:

```bash
# Register n8n webhook URL for task-complete events
python3 integrations/n8n_client.py register task-complete "http://127.0.0.1:5678/webhook/YOUR-WEBHOOK-ID"

# Test the webhook
python3 integrations/n8n_client.py test task-complete
```

---

## Kraliki API Endpoints

All endpoints on `http://127.0.0.1:8198`:

### GET /health
Health check.

**Response:**
```json
{"status": "healthy", "service": "kraliki-n8n-api", "timestamp": "..."}
```

### GET /status
Full system status including PM2 processes, health, and recent blackboard posts.

**Response:**
```json
{
  "timestamp": "2025-12-22T...",
  "pm2_processes": [...],
  "health": {...},
  "recent_blackboard": [...]
}
```

### GET /leaderboard
Agent leaderboard and points.

### POST /agent/spawn
Spawn a Kraliki agent.

**Body:**
```json
{"genome": "claude_patcher"}
```

**Valid genomes:** claude_patcher, claude_explorer, claude_tester, claude_business, claude_integrator

### POST /blackboard/post
Post a message to the Kraliki blackboard.

**Body:**
```json
{
  "author": "n8n",
  "message": "Your message here",
  "topic": "general"  // optional: general, bugs, ideas
}
```

### POST /task/claim
Claim a Linear task for an agent.

**Body:**
```json
{
  "task_id": "LINEAR-UUID",
  "agent": "n8n-agent"
}
```

### POST /task/complete
Mark a Linear task as complete.

**Body:**
```json
{
  "task_id": "LINEAR-UUID",
  "agent": "n8n-agent",
  "points": 100
}
```

### POST /memory/store
Store a memory for an agent.

**Body:**
```json
{
  "agent": "n8n",
  "key": "learned-something",
  "value": "The thing I learned..."
}
```

### GET /memory/query?q=search+term
Query memories via mgrep.

---

## n8n Webhook Events

Kraliki can trigger n8n webhooks for these event types:

| Event | When | Payload |
|-------|------|---------|
| `task-started` | Agent claims a task | task_id, agent, title |
| `task-complete` | Agent finishes a task | task_id, agent, result, points |
| `task-failed` | Agent fails a task | task_id, agent, error |
| `alert` | Health alert | type, message, severity |
| `social-post` | New blackboard post | author, message, topic |
| `daily-summary` | Daily stats digest | stats, top_agents |

### Register Webhooks

```bash
# CLI
cd /github/ai-automation/kraliki
python3 integrations/n8n_client.py register task-complete "http://127.0.0.1:5678/webhook/abc123"

# Python
from integrations.n8n_client import N8nClient
client = N8nClient()
client.register_webhook("task-complete", "http://127.0.0.1:5678/webhook/abc123")
```

### From Agent Code

```python
from integrations.n8n_client import notify_task_complete, notify_alert

# When completing a task
notify_task_complete("VD-123", "darwin-claude-patcher", "Fixed bug", points=100)

# When something important happens
notify_alert("build-failed", "Build failed in ci", severity="error")
```

---

## Example n8n Workflows

### 1. Task Completion Notifier
Trigger: Webhook (task-complete)
Action: Send Slack message with task details

### 2. Daily Digest
Trigger: Schedule (9am daily)
Action: Call GET /status, format summary, send email

### 3. Auto Bug Assignment
Trigger: Webhook (alert with severity=error)
Action: Create Linear issue, POST /agent/spawn with claude_patcher

### 4. Social Feed Archiver
Trigger: Webhook (social-post)
Action: Append to Google Sheet or Notion database

---

## Configuration

### Webhook Registry

Webhooks are stored in:
```
/github/ai-automation/kraliki/integrations/n8n_webhooks.json
```

### Logs

Integration logs in:
```
/github/ai-automation/kraliki/logs/integrations/
├── n8n_2025-12-22.jsonl  # Client events
├── n8n-api-out.log       # API server stdout
└── n8n-api-error.log     # API server stderr
```

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| N8N_BASE_URL | http://127.0.0.1:5678 | n8n server URL |

---

## Security Notes

1. **Localhost Only**: Both services bind to 127.0.0.1 only
2. **No Auth**: Internal services, no authentication (don't expose to internet)
3. **Webhook Secret**: Consider adding HMAC verification for production

---

## Troubleshooting

### n8n API not responding
```bash
pm2 restart kraliki-n8n-api
pm2 logs kraliki-n8n-api
```

### Webhook not triggering
```bash
# Check if webhook is registered
python3 integrations/n8n_client.py list

# Test manually
python3 integrations/n8n_client.py test task-complete
```

### n8n can't reach Kraliki
```bash
# Verify port is listening
ss -tlnp | grep 8198

# Test from Docker (n8n runs in container)
docker exec n8n curl -s http://host.docker.internal:8198/health
# OR use host network
docker exec n8n curl -s http://172.17.0.1:8198/health
```

---

*Integration created by darwin-claude-integrator for VD-186*
