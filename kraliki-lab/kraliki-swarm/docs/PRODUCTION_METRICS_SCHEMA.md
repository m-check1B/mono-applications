# Production Metrics Schema

> Defines the daily production metrics schema for all Verduona revenue apps.
> Part of VD-176: Define daily production metrics schema

## Overview

Production metrics are collected every 60 seconds and stored in:
- `/kraliki/data/revenue-metrics.json` (latest snapshot)
- `/kraliki/logs/daily/YYYY-MM-DD.json` (daily aggregates)

API Endpoint: `GET http://127.0.0.1:8198/revenue/metrics`

## Schema Definition

### Root Object
```json
{
  "timestamp": "ISO 8601 datetime",
  "collection_time_s": "float (seconds)",
  "apps": { "app_id": AppMetrics },
  "summary": SummaryMetrics
}
```

### AppMetrics
```json
{
  "id": "string (app identifier)",
  "name": "string (display name)",
  "type": "enum: telegram_bot | web_app | cli_tool",
  "revenue": "string (revenue model)",
  "description": "string",
  "checked_at": "ISO 8601 datetime",
  "overall_status": "enum: healthy | degraded | down | unknown",
  "docker": DockerMetrics,
  "health": HealthMetrics,
  "external": ExternalMetrics
}
```

### DockerMetrics
```json
{
  "containers": [
    {
      "name": "string",
      "status": "string (Docker status)",
      "state": "string (running/stopped/etc)",
      "healthy": "boolean"
    }
  ],
  "count": "integer",
  "all_healthy": "boolean",
  "status": "enum: up | down | degraded"
}
```

### HealthMetrics (internal endpoint)
```json
{
  "status": "enum: healthy | error | unreachable",
  "http_code": "integer",
  "response_time_ms": "float",
  "response": "string (truncated body)",
  "error": "string (if failed)"
}
```

### ExternalMetrics (public URL)
```json
{
  "status": "enum: reachable | error | unreachable",
  "http_code": "integer",
  "response_time_s": "float",
  "error": "string (if failed)"
}
```

### SummaryMetrics
```json
{
  "total": "integer (total apps)",
  "healthy": "integer",
  "degraded": "integer",
  "down": "integer",
  "unknown": "integer"
}
```

## App Registry

| App ID | Name | Type | Revenue Model | Docker Filter |
|--------|------|------|---------------|---------------|
| sense_kraliki | Sense by Kraliki | telegram_bot | €500/audit | senseit |
| speak_kraliki | Speak by Kraliki | web_app | €400/mo | speak-kraliki |
| voice_kraliki | Voice by Kraliki | web_app | subscription | voice-kraliki |
| focus_kraliki | Focus by Kraliki | web_app | freemium | focus-kraliki |
| lab_kraliki | Lab by Kraliki | cli_tool | €299/mo | - |
| tldr_bot | TL;DR Bot | telegram_bot | $20/mo | tldr |
| learn_kraliki | Learn by Kraliki | web_app | B2C edu | learn-kraliki |

## Status Determination Logic

1. **healthy**: Docker containers up AND health endpoint OK (if exists) AND external URL reachable
2. **degraded**: Docker containers up BUT health/external issues
3. **down**: Docker containers not running
4. **unknown**: Unable to determine status

## Usage Examples

### Get All Metrics (CLI)
```bash
curl -s http://127.0.0.1:8198/revenue/metrics | jq
```

### Get Summary Only
```bash
curl -s http://127.0.0.1:8198/revenue/metrics | jq '.summary'
```

### Check Specific App
```bash
curl -s http://127.0.0.1:8198/revenue/metrics | jq '.apps.senseit'
```

### Python Integration
```python
import json
from pathlib import Path

metrics = json.loads(Path("/kraliki/data/revenue-metrics.json").read_text())
healthy_apps = [
    app["name"] for app in metrics["apps"].values()
    if app["overall_status"] == "healthy"
]
```

## Alerting Thresholds (Recommended)

| Metric | Warning | Critical |
|--------|---------|----------|
| Apps healthy | < 80% | < 50% |
| App down | Any | - |
| Response time | > 3s | > 10s |
| Container restarts | > 3/hour | > 10/hour |

## Integration Points

- **Kraliki Swarm Dashboard**: Real-time widget showing app health
- **n8n Workflows**: Trigger alerts on degraded/down status
- **Weekly Reports**: Include in stats summary
- **Blackboard**: Post status changes

## Collection Configuration

Edit `/kraliki/integrations/revenue_metrics.py`:
- `COLLECT_INTERVAL`: How often to collect (default: 60s)
- `REVENUE_APPS`: Add/remove tracked apps

## File Locations

| File | Purpose |
|------|---------|
| `/kraliki/data/revenue-metrics.json` | Latest metrics snapshot |
| `/kraliki/logs/daily/YYYY-MM-DD.json` | Daily stats (includes revenue metrics) |
| `/kraliki/integrations/revenue_metrics.py` | Collection script |
| `/kraliki/integrations/n8n_api.py` | API server (includes /revenue/metrics) |

---
*Created by darwin-claude-integrator | Dec 22, 2025*
