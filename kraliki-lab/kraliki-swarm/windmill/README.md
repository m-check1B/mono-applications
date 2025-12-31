# Kraliki Windmill Workflows

Automated workflows for the Kraliki AI swarm system, powered by Windmill.

## Access

- **Windmill UI**: http://127.0.0.1:8100 (localhost only)
- **Workspace**: `kraliki`
- **API Token**: `kraliki-windmill-secret-2026`

## Workflows

### 1. User Sync (`f/automation/user_sync`)

Syncs new users from Zitadel to all Kraliki apps.

**Trigger**: Webhook (POST)
**Endpoint**: `/api/r/user-sync`

**Input**:
```json
{
  "user_id": "zitadel-user-id",
  "email": "user@example.com",
  "name": "User Name",
  "event_type": "user.created"
}
```

**Configure in Zitadel**:
1. Go to Zitadel Console > Actions
2. Create action that calls: `http://127.0.0.1:8100/api/r/user-sync`
3. Trigger on: User Created

---

### 2. Lead Capture (`f/automation/lead_capture`)

Processes lead form submissions, validates, deduplicates, and creates in EspoCRM.

**Trigger**: Webhook (POST)
**Endpoint**: `/api/r/lead-capture`

**Input**:
```json
{
  "email": "lead@example.com",
  "name": "Lead Name",
  "company": "Company (optional)",
  "phone": "+1234567890 (optional)",
  "source": "website",
  "message": "Optional message"
}
```

**Configure**:
1. Set `ESPOCRM_API_KEY` variable in Windmill
2. Point website forms to webhook endpoint

---

### 3. Customer Onboarding (`f/automation/customer_onboarding`)

Processes successful Stripe payments and provisions customer accounts.

**Trigger**: Webhook (POST)
**Endpoint**: `/api/r/stripe-webhook`

**Input** (from Stripe webhook):
```json
{
  "customer_id": "cus_xxx",
  "customer_email": "customer@example.com",
  "customer_name": "Customer Name",
  "subscription_id": "sub_xxx (optional)",
  "product_name": "Focus by Kraliki",
  "amount_paid": 9900,
  "currency": "eur"
}
```

**Steps**:
1. Create customer account in the relevant app
2. Send welcome email via kraliki-notify
3. Create Linear task for sales follow-up

**Configure**:
1. Set `INTERNAL_SECRET` variable in Windmill
2. Set `LINEAR_API_KEY` variable in Windmill
3. Set `TEAM_ID` variable for Linear team
4. Configure Stripe webhook to call this endpoint

---

### 4. Weekly Metrics (`f/automation/weekly_metrics`)

Collects weekly metrics from all apps and sends summary to Telegram.

**Trigger**: Cron Schedule
**Schedule**: Every Sunday at 18:00 (Europe/Prague)
**Cron**: `0 0 18 * * 7`

**Output**: Posts summary to Telegram with:
- Stripe revenue (total charges, EUR amount)
- User counts per app (active, new)
- Overall totals

**Configure**:
1. Set `STRIPE_SECRET_KEY` variable in Windmill
2. Set `TELEGRAM_BOT_TOKEN` variable in Windmill
3. Set `TELEGRAM_CHAT_ID` variable in Windmill

---

## API Usage

### Authentication

All API calls require the superadmin token:
```bash
curl -H "Authorization: Bearer kraliki-windmill-secret-2026" ...
```

### Run a Script

```bash
# Run user_sync with test data
curl -X POST "http://127.0.0.1:8100/api/w/kraliki/jobs/run/p/f/automation/user_sync" \
  -H "Authorization: Bearer kraliki-windmill-secret-2026" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test", "email": "test@example.com", "name": "Test"}'
```

### List Jobs

```bash
# List completed jobs
curl "http://127.0.0.1:8100/api/w/kraliki/jobs/completed/list" \
  -H "Authorization: Bearer kraliki-windmill-secret-2026"
```

### Get Job Result

```bash
curl "http://127.0.0.1:8100/api/w/kraliki/jobs/completed/get_result/{job_id}" \
  -H "Authorization: Bearer kraliki-windmill-secret-2026"
```

---

## Required Variables

Set these in Windmill UI (Settings > Variables):

| Variable | Description |
|----------|-------------|
| `INTERNAL_SECRET` | Secret for internal API calls between apps |
| `ESPOCRM_API_KEY` | EspoCRM API key for lead creation |
| `LINEAR_API_KEY` | Linear API key for task creation |
| `TEAM_ID` | Linear team ID for new tasks |
| `STRIPE_SECRET_KEY` | Stripe secret key for metrics |
| `TELEGRAM_BOT_TOKEN` | Telegram bot token for notifications |
| `TELEGRAM_CHAT_ID` | Telegram chat ID for metrics reports |

---

## Docker Compose

Windmill runs via Docker Compose:

```bash
# Start
docker compose -f /home/adminmatej/github/infra/compose/windmill.yml up -d

# Stop
docker compose -f /home/adminmatej/github/infra/compose/windmill.yml down

# Logs
docker logs windmill-server -f
docker logs windmill-worker -f
```

---

## Extending

To add new workflows:

1. Create script via API:
```bash
curl -X POST "http://127.0.0.1:8100/api/w/kraliki/scripts/create" \
  -H "Authorization: Bearer kraliki-windmill-secret-2026" \
  -H "Content-Type: application/json" \
  -d '{
    "path": "f/automation/my_script",
    "summary": "My Script",
    "description": "Description",
    "content": "def main():\n    return {\"ok\": True}",
    "language": "python3",
    "is_template": false,
    "kind": "script"
  }'
```

2. Add trigger (webhook or schedule) as needed

---

*Part of Kraliki AI Swarm - Verduona*
