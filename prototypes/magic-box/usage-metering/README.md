# Magic Box Usage Metering System

**Track API usage, system resources, and billing for Magic Box customers.**

## Features

- **API Usage Tracking**: Claude, OpenAI, Gemini token usage with cost calculation
- **Resource Monitoring**: CPU, memory, and disk usage (collected every 5 minutes)
- **Command Tracking**: Log all commands run on the VM
- **Pattern Usage**: Track which prompt patterns are used
- **Billing Reports**: Generate monthly cost breakdowns
- **REST API**: Query all usage data via HTTP
- **Dashboard**: Web-based interface for customers to view usage
- **Export Functionality**: Download data as JSON or CSV

## Quick Start

### Installation

```bash
# From Magic Box VM
cd /opt/magic-box
./usage-metering/install.sh
```

The installer will:
1. Copy service files to `/opt/magic-box-usage/`
2. Initialize SQLite database at `/opt/magic-box/usage.db`
3. Register customer (prompted on first run)
4. Create systemd services for API and collector
5. Configure Traefik routing (if available)

### Manual Setup

```bash
# Initialize database
python3 usage_tracker.py --init

# Register customer
python3 usage_tracker.py --register CUSTOMER_ID "Company Name" "contact@example.com"

# Start API server
python3 api.py --port 8585

# Collect system resources (run every 5 minutes via cron)
python3 usage_tracker.py --collect
```

## Usage

### CLI

```bash
# Show usage summary (last 30 days)
python3 usage_tracker.py --summary

# Generate monthly billing report
python3 usage_tracker.py --report 2025-01

# Export usage data
python3 usage_tracker.py --export json > usage.json
python3 usage_tracker.py --export csv > usage.csv

# Collect system resources now
python3 usage_tracker.py --collect
```

### REST API

**Base URL**: `http://localhost:8585`

#### Endpoints

**Health Check**
```bash
GET /health
```

```bash
GET /api/health
```

**Usage Summary**
```bash
GET /api/usage/summary?start=2025-01-01&end=2025-01-31
```

Returns:
```json
{
  "period": {"start": "2025-01-01", "end": "2025-01-31"},
  "api_usage": [
    {"provider": "claude", "model": "claude-3-5-sonnet", "input_tokens": 1000000, "output_tokens": 500000, "total_cost": 10.5}
  ],
  "resources": {"avg_cpu": 15.2, "avg_memory": 45.3, "max_memory": 72.1},
  "totals": {
    "input_tokens": 1000000,
    "output_tokens": 500000,
    "cost": 10.5,
    "commands": 234,
    "compute_hours": 128.5
  }
}
```

**Resource History**
```bash
GET /api/usage/resources?hours=24&limit=100
```

**API Usage History**
```bash
GET /api/usage/api?hours=24&limit=50
```

**Command History**
```bash
GET /api/usage/commands?hours=24&limit=50
```

**Billing Report**
```bash
GET /api/billing/report?month=2025-01
```

### Dashboard

Access the web dashboard:
- Local: `http://localhost:8585/dashboard.html`
- Traefik: `http://usage.magicbox.local`

The dashboard shows:
- Total costs and token counts
- API usage by provider/model
- Resource utilization (CPU, memory, disk)
- Recent command usage
- Data export buttons

## Database Schema

The SQLite database (`usage.db`) contains:

### Tables

**customers**
- Customer information (ID, name, email, VM ID, billing plan)

**ai_providers**
- AI provider pricing (Claude, OpenAI, Gemini)

**api_usage**
- API call tracking (tokens, costs, timestamps)

**resource_usage**
- System resource snapshots (CPU, memory, disk)

**command_usage**
- Command execution log

**pattern_usage**
- Prompt pattern usage tracking

**billing_reports**
- Monthly billing reports

### Views

Run `schema.sql` to initialize the database.

## Cost Calculation

API costs are calculated based on token usage and provider pricing:

| Provider | Model | Input (per 1M) | Output (per 1M) |
|----------|--------|------------------|-------------------|
| Claude   | claude-3-5-sonnet | $3.00  | $15.00 |
| Claude   | claude-3-opus      | $15.00 | $75.00 |
| OpenAI   | gpt-4              | $30.00 | $60.00 |
| OpenAI   | gpt-4-turbo        | $10.00 | $30.00 |
| Gemini   | gemini-1.5-pro     | $1.25  | $5.00  |
| Gemini   | gemini-1.5-flash    | $0.075 | $0.30  |

Pricing can be updated in the `ai_providers` table.

## Billing Reports

Monthly billing reports include:

1. **API Costs**: Token usage × pricing
2. **Compute Hours**: Resource samples × 5 minutes / 60
3. **Total Cost**: API costs + compute hours

Generate via:
```bash
python3 usage_tracker.py --report 2025-01
```

Or via API:
```bash
curl http://localhost:8585/api/billing/report?month=2025-01
```

## Integration

### Tracking API Calls

To track API usage programmatically:

```python
from usage_tracker import UsageMeteringService

service = UsageMeteringService()

# Track Claude usage
service.track_api_usage(
    provider="claude",
    model="claude-3-5-sonnet",
    input_tokens=1000,
    output_tokens=500,
    endpoint="/v1/messages"
)
```

### Tracking Commands

Use the shell wrapper to track commands:

```bash
# In .bashrc or .profile
magic_box_track() {
    python3 /opt/magic-box-usage/usage_tracker.py \
        --track-command "$1" \
        --args "${@:2}" \
        --db /opt/magic-box/usage.db &
    "$@"
}
```

### Docker Deployment

```bash
cd usage-metering
docker-compose up -d
```

Services:
- `usage-metering`: API server (port 8585)
- `usage-collector`: Resource collector (every 5 minutes)

### Stripe Usage Sync (Draft)

Use the usage report to post metered usage into Stripe (quantity in cents):

```bash
export STRIPE_SUBSCRIPTION_ITEM_ID=si_123
export STRIPE_API_KEY=sk_live_...
python3 stripe_sync.py --month 2025-01 --commit
```

Dry-run (default) prints the Stripe payload without sending:

```bash
python3 stripe_sync.py --month 2025-01
```

Set `STRIPE_FX_RATE` if usage costs are stored in USD and billing is in EUR.

## Monitoring

### Service Status

```bash
# Check API service
sudo systemctl status magic-box-usage.service

# Check collector service
sudo systemctl status magic-box-usage-collector.service

# View logs
sudo journalctl -u magic-box-usage -f
```

### Health Checks

```bash
# API health
curl http://localhost:8585/health
curl http://localhost:8585/api/health

# Dashboard accessible
curl -I http://localhost:8585/dashboard.html
```

## Troubleshooting

### Database Issues

```bash
# Recreate database
sudo rm /opt/magic-box/usage.db
python3 usage_tracker.py --init
```

### Service Not Starting

```bash
# Check logs
sudo journalctl -u magic-box-usage -n 50

# Restart service
sudo systemctl restart magic-box-usage.service
```

### Port Already in Use

```bash
# Change port
python3 api.py --port 8586
```

## Security

- API accessible only from localhost by default
- Database file permissions: 600 (root only)
- No customer data leaves the VM (self-contained)
- Traefik routing can be configured for HTTPS

## Future Enhancements

- [ ] Stripe integration for automatic billing
- [ ] Email alerts for cost thresholds
- [ ] Multi-VM aggregation (central dashboard)
- [ ] Real-time cost estimation
- [ ] Custom pricing tiers
- [ ] Usage-based auto-scaling suggestions

## Support

For issues or feature requests, contact Magic Box support.
