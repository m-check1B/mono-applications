# Lab by Kraliki Usage Metering System

Comprehensive usage tracking and billing support for Lab by Kraliki VM rental service.

---

## Overview

The usage metering system tracks three key categories of metrics:

1. **API Usage**: Tokens and costs for Claude, OpenAI, and Gemini API calls
2. **Resource Usage**: CPU, memory, disk, and network metrics
3. **User Activity**: Commands run, patterns used, and operations performed

These metrics support:
- Cost attribution per customer VM
- Usage-based billing (beyond fixed monthly fee)
- Customer dashboards for self-service monitoring
- Export for Stripe billing integration

---

## Components

### 1. usage_metering.py

Core database and collection engine for all usage metrics.

**Features:**
- SQLite database for persistent storage
- API usage records with cost calculation
- Resource usage tracking (CPU, memory, disk, network)
- Activity logging (commands, patterns, operations)
- Time-based reporting (daily, weekly, monthly)
- CSV export for billing integration

**Database Schema:**

```sql
-- API usage (tokens, costs)
api_usage (
    id, timestamp, customer_id, vm_id,
    provider, model, tokens_in, tokens_out, cost_usd
)

-- Resource usage (VM metrics)
resource_usage (
    id, timestamp, customer_id, vm_id,
    cpu_percent, memory_percent, disk_gb,
    network_in_mb, network_out_mb
)

-- Activity log (user actions)
activity_log (
    id, timestamp, customer_id, vm_id,
    activity_type, pattern_name, command, duration_seconds
)

-- Customer registry
customers (
    id, vm_id, tier, created_at, status
)
```

**Usage:**

```bash
# Add customer
python3 /opt/magic-box/scripts/usage_metering.py \
    --customer-id acme-corp \
    --vm-id magicbox-acme-corp \
    --tier pro

# Collect current metrics
python3 /opt/magic-box/scripts/usage_metering.py \
    --customer-id acme-corp \
    --vm-id magicbox-acme-corp \
    --collect

# Generate report
python3 /opt/magic-box/scripts/usage_metering.py \
    --customer-id acme-corp \
    --period month \
    --report \
    --export-csv /tmp/usage-report.csv
```

---

### 2. parse_cliproxy_logs.py

Parses CLIProxyAPI access logs to extract API usage metrics.

**Features:**
- Supports common log format and JSON logs
- Detects Anthropic, OpenAI, and Google API calls
- Extracts token counts (input/output)
- Calculates costs using current pricing
- Stores directly to usage database

**Supported Log Formats:**

Common Log Format:
```
10.0.0.1 - - [25/Dec/2025:10:30:00 +0000] "POST /v1/messages HTTP/1.1" 200 1234 "-" "anthropic-sdk/0.1.0"
```

JSON Format:
```json
{
  "timestamp": "2025-12-25T10:30:00Z",
  "path": "/v1/messages",
  "status": 200,
  "model": "claude-3-sonnet-20240229",
  "input_tokens": 1500,
  "output_tokens": 500
}
```

**Pricing (as of Dec 2025):**

| Provider | Model | Input | Output |
|----------|--------|--------|---------|
| Anthropic | claude-3-opus | $0.015/1K | $0.075/1K |
| Anthropic | claude-3-sonnet | $0.003/1K | $0.015/1K |
| Anthropic | claude-3-haiku | $0.00025/1K | $0.00125/1K |
| OpenAI | gpt-4-turbo | $0.01/1K | $0.03/1K |
| OpenAI | gpt-4 | $0.03/1K | $0.06/1K |
| OpenAI | gpt-3.5-turbo | $0.0005/1K | $0.0015/1K |
| Google | gemini-1.5-pro | $0.000125/1K | $0.0005/1K |
| Google | gemini-1.5-flash | $0.000075/1K | $0.0003/1K |
| Google | gemini-1.0-pro | $0.00025/1K | $0.0005/1K |

**Usage:**

```bash
# Parse and display summary
python3 /opt/magic-box/scripts/parse_cliproxy_logs.py \
    --log-file /var/log/cliproxy/access.log \
    --customer-id acme-corp \
    --vm-id magicbox-acme-corp

# Parse and store to database
python3 /opt/magic-box/scripts/parse_cliproxy_logs.py \
    --log-file /var/log/cliproxy/access.log \
    --customer-id acme-corp \
    --vm-id magicbox-acme-corp \
    --store
```

---

### 3. usage_dashboard.py

Web-based dashboard for customers to view their usage.

**Features:**
- Real-time metrics display
- Customer selection
- Period filtering (day, week, month)
- API usage breakdown by provider and model
- Resource usage trends
- Activity summary
- Self-service access

**Security:**
- Binds to 127.0.0.1 by default (not exposed to internet)
- Use Traefik reverse proxy for public access
- Auth protection recommended

**Usage:**

```bash
# Start dashboard (localhost only)
python3 /opt/magic-box/scripts/usage_dashboard.py \
    --port 8080 \
    --host 127.0.0.1

# Access at http://127.0.0.1:8080
```

---

## Integration Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   Lab by Kraliki VM                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  CLIProxyAPI (Port 3000)                                   │
│  ├── Logs to /var/log/cliproxy/access.log                    │
│  └── parse_cliproxy_logs.py extracts API usage              │
│         ↓                                                    │
│  usage_metering.py stores metrics in SQLite                     │
│         ↓                                                    │
│  Cron jobs collect metrics every 5 minutes                     │
│         ↓                                                    │
│  usage_dashboard.py serves web interface (Port 8080)           │
│         ↓                                                    │
│  Customer views usage at lab.kraliki.com                       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Deployment

### 1. Install Components

```bash
# Ensure scripts are executable
chmod +x /opt/magic-box/scripts/*.py

# Create database directory
mkdir -p /var/lib/magic-box
touch /var/lib/magic-box/usage.db
chmod 600 /var/lib/magic-box/usage.db
```

### 2. Set Up Cron Jobs

Add to `/etc/cron.d/magic-box-usage`:

```cron
# Collect resource usage every 5 minutes
*/5 * * * * root cd /opt/magic-box/scripts && /usr/bin/python3 usage_metering.py --customer-id CUSTOMER_ID --vm-id VM_ID --collect

# Parse API logs every hour
0 * * * * root cd /opt/magic-box/scripts && /usr/bin/python3 parse_cliproxy_logs.py --log-file /var/log/cliproxy/access.log --customer-id CUSTOMER_ID --vm-id VM_ID --store

# Start dashboard on boot
@reboot root cd /opt/magic-box/scripts && /usr/bin/python3 usage_dashboard.py --port 8080 --host 127.0.0.1 >> /var/log/magic-box/dashboard.log 2>&1
```

### 3. Configure Traefik (Optional)

Add Traefik labels for public dashboard access:

```yaml
services:
  usage-dashboard:
    image: magic-box-dashboard
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.usage.rule=Host(`lab.kraliki.com`)"
      - "traefik.http.routers.usage.tls=true"
      - "traefik.http.routers.usage.tls.certresolver=letsencrypt"
      - "traefik.http.services.usage.loadbalancer.server.port=8080"
```

---

## Billing Integration

### Export Format for Stripe

The system generates CSV exports compatible with billing integration:

```csv
Provider,Model,Tokens In,Tokens Out,Total Tokens,Cost USD
anthropic,claude-3-sonnet,10000,5000,15000,0.1050
openai,gpt-4-turbo,5000,2000,7000,0.1100
google,gemini-1.5-pro,8000,4000,12000,0.0029
```

### Cost Calculation

**Fixed Monthly Fee (Subscription):**
- Starter: €299/mo
- Pro: €499/mo
- Enterprise: €833/mo

**Usage-Based Add-on (Optional):**
- Metered if >1M tokens/month
- Charged at cost + 20% markup
- Example: $10 API cost → $12 customer charge

### Automated Billing Flow

1. Cron job collects metrics daily
2. Monthly report generated on 1st of each month
3. CSV exported to billing service
4. Stripe invoice created with:
   - Base subscription amount
   - Usage overage charges (if any)
5. Customer receives invoice via email

---

## API Reference

### usage_metering.py CLI

| Argument | Required | Description |
|----------|-----------|-------------|
| `--customer-id` | Yes | Customer identifier |
| `--vm-id` | Yes | VM identifier |
| `--tier` | No | Customer tier (starter/pro/enterprise) |
| `--collect` | No | Collect and store current resource metrics |
| `--report` | No | Generate usage report |
| `--period` | No | Report period (day/week/month, default: month) |
| `--export-csv` | No | Export report to CSV file |
| `--output` | No | Output format (json/text, default: text) |

### parse_cliproxy_logs.py CLI

| Argument | Required | Description |
|----------|-----------|-------------|
| `--log-file` | Yes | Path to CLIProxyAPI log file |
| `--customer-id` | Yes | Customer identifier |
| `--vm-id` | Yes | VM identifier |
| `--output` | No | Output format (json/summary, default: summary) |
| `--store` | No | Store to usage_metering database |

### usage_dashboard.py CLI

| Argument | Required | Description |
|----------|-----------|-------------|
| `--port` | No | HTTP port (default: 8080) |
| `--host` | No | Host to bind (default: 127.0.0.1) |
| `--db-path` | No | Path to usage database (default: /var/lib/magic-box/usage.db) |

---

## Troubleshooting

### Database Locked

If you see "database is locked" errors:

```bash
# Check for running processes
ps aux | grep usage_metering

# Kill stuck processes
killall -9 usage_metering.py
```

### Missing Metrics

If dashboard shows no data:

1. Check cron jobs are running:
   ```bash
   tail -f /var/log/syslog | grep CRON
   ```

2. Verify log file exists:
   ```bash
   ls -la /var/log/cliproxy/access.log
   ```

3. Check database contents:
   ```bash
   sqlite3 /var/lib/magic-box/usage.db "SELECT COUNT(*) FROM api_usage;"
   ```

### High CPU Usage

If collection scripts consume too much CPU:

1. Reduce collection frequency in cron
2. Add rate limiting to parse_cliproxy_logs.py
3. Archive old log files

---

## Future Enhancements

- [ ] Real-time WebSocket updates in dashboard
- [ ] Usage alerts (email/Slack)
- [ ] Predictive cost forecasting
- [ ] Multi-tenant dashboard (all customers viewable by admin)
- [ ] Integration with Prometheus/Grafana for advanced metrics
- [ ] Automated cleanup of old data (retention policy)
- [ ] Usage anomalies detection (spikes, unusual patterns)

---

*Last Updated: December 25, 2025*
