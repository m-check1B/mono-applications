# VD-315 Magic Box Billing Integration Plan

## Goal
Deliver Stripe-ready billing for Magic Box VM rentals (EUR 299-499/mo) with optional usage overage based on the existing usage-metering service.

## Current Assets
- Usage metering service (API + billing report):
  - Canonical: `/home/adminmatej/github/applications/prototypes/magic-box/usage-metering/`
  - Archive mirror: `/home/adminmatej/github/_archive/applications-duplicates-20251227/magic-box/usage-metering/`
- REST API includes `/api/health` (added `/health` alias for simple probes).
- Monthly billing report includes API cost + compute hours:
  `usage_tracker.py -> generate_billing_report(month)`.
- Stripe usage sync script (draft):
  `/home/adminmatej/github/applications/prototypes/magic-box/usage-metering/stripe_sync.py`.
- Billing strategy docs:
  - `/home/adminmatej/github/applications/prototypes/magic-box/billing/README.md`
  - `/home/adminmatej/github/applications/prototypes/magic-box/billing/IMPLEMENTATION.md`

## Billing Model
### Base Subscription (fixed)
- Starter: EUR 299/mo
- Pro: EUR 499/mo
- Enterprise: EUR 10K/yr (manual invoicing)

### Variable Usage (optional, metered)
- Use a Stripe metered price with unit amount = 1 cent.
- Quantity = total usage cost in cents (API usage + compute cost).
- Usage data source = usage-metering billing report.

### Compute Cost (CPX31)
- CPX31 monthly cost -> hourly rate:
  `hourly_cost = monthly_cost_eur / (30 * 24)`
- Update `usage_tracker.py` compute pricing to match actual CPX31 cost once final.

## Stripe Setup
1. Create Stripe Product: “Magic Box Base”
2. Create Prices:
   - Starter (EUR 299/mo)
   - Pro (EUR 499/mo)
3. Create Stripe Product: “Magic Box Usage”
4. Create Metered Price:
   - `usage_type=metered`, `aggregate_usage=sum`
   - Unit amount = 1 cent
5. For each customer VM:
   - Create customer
   - Create subscription with base price + usage price
   - Store `subscription_item_id` for usage price

## Deployment Notes
- Install usage-metering on each customer VM:
  - `cd /home/adminmatej/github/applications/prototypes/magic-box/usage-metering`
  - `./install.sh` (creates `/opt/magic-box-usage` + systemd services)
- Services created by installer:
  - `magic-box-usage.service` (API on port 8585)
  - `magic-box-usage-collector.service` (usage collection)
- Database path on VM: `/opt/magic-box/usage.db`

## Sync Workflow
- Daily or monthly cron job runs on VM:
  - Generates billing report for current month
  - Sends Stripe usage record with total cents
- Script: `stripe_sync.py`
  - Uses `STRIPE_SUBSCRIPTION_ITEM_ID`
  - Uses `STRIPE_API_KEY`
  - Supports `STRIPE_FX_RATE` for USD->EUR conversion

## Required Environment
- `STRIPE_API_KEY` (Stripe secret key for usage records)
- `STRIPE_SUBSCRIPTION_ITEM_ID` (metered price subscription item ID)
- `STRIPE_FX_RATE` (optional, defaults to 1.0)
- `MAGIC_BOX_USAGE_DB` (optional, default `/opt/magic-box/usage.db`)

## Operational Steps
1. Ensure usage-metering service is running and recording usage.
2. Register customer in usage DB (customer ID should align with Stripe customer).
3. Run sync in dry-run mode to validate payload.
4. Enable `--commit` when Stripe IDs are confirmed.

## Testing
- Health check for usage-metering API:
  `curl -v http://localhost:8585/health`
- Billing report:
  `curl http://localhost:8585/api/billing/report?month=YYYY-MM`

## Risks / Open Questions
- Confirm currency of usage costs (USD vs EUR) and set FX rate accordingly.
- Decide if usage overage is billed immediately (daily) or at month end.
- Confirm CPX31 pricing and update compute cost formula.
- If Magic Box is moved out of _archive, update paths and deployment docs.
