# Technical Implementation Plan

**Version**: 1.0.0
**Last Updated**: 2025-12-28

---

## Implementation Overview

This document provides a detailed technical implementation plan for Magic Box billing.

---

## Prerequisites

### Existing Infrastructure

| Component | Status | Location |
|-----------|--------|----------|
| Usage Tracking | Ready | `usage-metering/usage_tracker.py` |
| Usage API | Ready | `usage-metering/api.py` |
| Usage Dashboard | Ready | `usage-metering/dashboard.html` |
| Stripe Sync (Basic) | Ready | `usage-metering/stripe_sync.py` |
| Database Schema | Ready | `usage-metering/schema.sql` |
| Landing Page | Ready | `docs/landing-page.html` |

### Required Accounts

| Service | Purpose | Status |
|---------|---------|--------|
| Stripe Account | Payment processing | Needs setup |
| Stripe Test Mode | Testing | Needs setup |
| SendGrid/SES | Billing emails | Optional |

---

## Phase 1: Stripe Setup (Day 1)

### Task 1.1: Create Stripe Products

```bash
# Login to Stripe Dashboard
# Navigate to Products > Create Product

# Product 1: Starter
Name: Magic Box Starter
Description: Solo developer tier - 1 VM, 100 compute hours, EUR 50 API credits
Metadata:
  tier: starter
  included_compute_hours: 100
  included_api_credits: 50

# Product 2: Pro
Name: Magic Box Pro
Description: Growing team tier - 3 VMs, 300 compute hours, EUR 150 API credits
Metadata:
  tier: pro
  included_compute_hours: 300
  included_api_credits: 150

# Product 3: Enterprise
Name: Magic Box Enterprise
Description: Large team tier - Unlimited VMs, Unlimited compute, EUR 500 API credits
Metadata:
  tier: enterprise
  included_compute_hours: -1
  included_api_credits: 500
```

### Task 1.2: Create Prices

```python
import stripe
stripe.api_key = "sk_live_..."

# Starter Monthly
stripe.Price.create(
    product="prod_magicbox_starter",
    unit_amount=9900,  # EUR 99.00
    currency="eur",
    recurring={"interval": "month"},
    metadata={"tier": "starter", "billing_cycle": "monthly"}
)

# Starter Annual
stripe.Price.create(
    product="prod_magicbox_starter",
    unit_amount=99000,  # EUR 990.00
    currency="eur",
    recurring={"interval": "year"},
    metadata={"tier": "starter", "billing_cycle": "annual"}
)

# Pro Monthly
stripe.Price.create(
    product="prod_magicbox_pro",
    unit_amount=19900,  # EUR 199.00
    currency="eur",
    recurring={"interval": "month"},
    metadata={"tier": "pro", "billing_cycle": "monthly"}
)

# Pro Annual
stripe.Price.create(
    product="prod_magicbox_pro",
    unit_amount=199000,  # EUR 1990.00
    currency="eur",
    recurring={"interval": "year"},
    metadata={"tier": "pro", "billing_cycle": "annual"}
)

# Enterprise Monthly
stripe.Price.create(
    product="prod_magicbox_enterprise",
    unit_amount=49900,  # EUR 499.00
    currency="eur",
    recurring={"interval": "month"},
    metadata={"tier": "enterprise", "billing_cycle": "monthly"}
)

# Enterprise Annual
stripe.Price.create(
    product="prod_magicbox_enterprise",
    unit_amount=499000,  # EUR 4990.00
    currency="eur",
    recurring={"interval": "year"},
    metadata={"tier": "enterprise", "billing_cycle": "annual"}
)

# Compute Overage (Starter)
stripe.Price.create(
    product="prod_magicbox_starter",
    unit_amount=5,  # EUR 0.05
    currency="eur",
    recurring={
        "interval": "month",
        "usage_type": "metered",
        "aggregate_usage": "sum"
    },
    metadata={"type": "compute_overage", "tier": "starter"}
)

# Compute Overage (Pro)
stripe.Price.create(
    product="prod_magicbox_pro",
    unit_amount=4,  # EUR 0.04
    currency="eur",
    recurring={
        "interval": "month",
        "usage_type": "metered",
        "aggregate_usage": "sum"
    },
    metadata={"type": "compute_overage", "tier": "pro"}
)

# API Overage (all tiers)
stripe.Price.create(
    product="prod_magicbox_starter",  # Can be separate product
    unit_amount=1,  # EUR 0.01 per cent of API cost
    currency="eur",
    recurring={
        "interval": "month",
        "usage_type": "metered",
        "aggregate_usage": "sum"
    },
    metadata={"type": "api_overage"}
)
```

### Task 1.3: Create Payment Links

```bash
# In Stripe Dashboard > Payment Links

# Starter Link
Product: Magic Box Starter (Monthly)
After Payment: Redirect to /welcome?tier=starter
Collect: Email, Billing Address
Allow Promotion Codes: Yes

# Pro Link
Product: Magic Box Pro (Monthly)
After Payment: Redirect to /welcome?tier=pro
Collect: Email, Billing Address
Allow Promotion Codes: Yes

# Enterprise Link
Product: Magic Box Enterprise (Monthly)
After Payment: Redirect to /welcome?tier=enterprise
Collect: Email, Billing Address, Company Name
Allow Promotion Codes: Yes
```

### Task 1.4: Update Landing Page

```bash
# Store payment links in .env
echo "STRIPE_PAYMENT_LINK_STARTER=https://buy.stripe.com/..." >> .env
echo "STRIPE_PAYMENT_LINK_PRO=https://buy.stripe.com/..." >> .env
echo "STRIPE_PAYMENT_LINK_ENTERPRISE=https://buy.stripe.com/..." >> .env

# Run configuration script
./scripts/configure_stripe_links.sh
```

---

## Phase 2: Enhanced Usage Sync (Day 2)

### Task 2.1: Extend stripe_sync.py

Create enhanced version at `usage-metering/stripe_sync_v2.py`:

```python
#!/usr/bin/env python3
"""
Enhanced Stripe Usage Sync
==========================

Syncs Magic Box usage to Stripe with support for:
- Compute hour overage
- API credit overage
- Tier-aware included amounts
- Multi-subscription item support
"""

import argparse
import json
import os
import sqlite3
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from usage_tracker import UsageMeteringService


# Tier configuration
TIERS = {
    "starter": {
        "included_compute_hours": 100,
        "included_api_credits": 50.0,
        "compute_overage_rate": 0.05,
        "api_margin": 0.20
    },
    "pro": {
        "included_compute_hours": 300,
        "included_api_credits": 150.0,
        "compute_overage_rate": 0.04,
        "api_margin": 0.15
    },
    "enterprise": {
        "included_compute_hours": float('inf'),
        "included_api_credits": 500.0,
        "compute_overage_rate": 0.0,
        "api_margin": 0.10
    }
}


class StripeUsageSync:
    """Sync usage data to Stripe"""

    def __init__(self, db_path: str, api_key: Optional[str] = None):
        self.db_path = db_path
        self.api_key = api_key or os.getenv("STRIPE_API_KEY", "")
        self.service = UsageMeteringService(db_path=db_path)

    def get_customer_tier(self) -> str:
        """Get customer billing tier from database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT billing_plan FROM customers LIMIT 1"
            )
            row = cursor.fetchone()
            return row[0] if row else "starter"

    def get_stripe_subscription_items(self) -> Dict[str, str]:
        """Get Stripe subscription item IDs from environment"""
        return {
            "compute": os.getenv("STRIPE_SUBSCRIPTION_ITEM_COMPUTE", ""),
            "api": os.getenv("STRIPE_SUBSCRIPTION_ITEM_API", "")
        }

    def calculate_overage(self, month: str) -> Dict[str, Any]:
        """Calculate overage for a billing month"""
        report = self.service.generate_billing_report(month)
        if not report:
            return None

        tier = self.get_customer_tier()
        tier_config = TIERS.get(tier, TIERS["starter"])

        # Compute overage
        compute_hours = float(report["total_compute_hours"])
        included_compute = tier_config["included_compute_hours"]

        if included_compute == float('inf'):
            compute_overage_hours = 0
        else:
            compute_overage_hours = max(0, compute_hours - included_compute)

        compute_overage_charge = compute_overage_hours * tier_config["compute_overage_rate"]

        # API overage
        api_cost = float(report["total_api_cost"])
        included_api = tier_config["included_api_credits"]
        api_overage = max(0, api_cost - included_api)
        api_margin = tier_config["api_margin"]
        api_overage_charge = api_overage * (1 + api_margin)

        return {
            "month": month,
            "tier": tier,
            "compute": {
                "total_hours": compute_hours,
                "included_hours": included_compute,
                "overage_hours": compute_overage_hours,
                "overage_charge": round(compute_overage_charge, 2)
            },
            "api": {
                "total_cost": api_cost,
                "included_credits": included_api,
                "overage_cost": api_overage,
                "margin": api_margin,
                "overage_charge": round(api_overage_charge, 2)
            },
            "total_overage_charge": round(compute_overage_charge + api_overage_charge, 2)
        }

    def month_end_timestamp(self, month: str) -> int:
        """Get unix timestamp for end of month"""
        year, month_num = map(int, month.split("-"))
        start = datetime(year, month_num, 1, tzinfo=timezone.utc)
        if month_num == 12:
            next_month = datetime(year + 1, 1, 1, tzinfo=timezone.utc)
        else:
            next_month = datetime(year, month_num + 1, 1, tzinfo=timezone.utc)
        end = next_month - timedelta(seconds=1)
        return int(end.timestamp())

    def stripe_post(self, endpoint: str, payload: dict) -> dict:
        """Make POST request to Stripe API"""
        if not self.api_key:
            raise ValueError("STRIPE_API_KEY not set")

        body = urlencode(payload).encode("utf-8")
        req = Request(f"https://api.stripe.com/v1/{endpoint}", data=body)
        req.add_header("Authorization", f"Bearer {self.api_key}")
        req.add_header("Content-Type", "application/x-www-form-urlencoded")

        with urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))

    def sync_to_stripe(self, month: str, commit: bool = False) -> Dict[str, Any]:
        """Sync usage to Stripe"""
        overage = self.calculate_overage(month)
        if not overage:
            return {"error": "No customer registered"}

        subscription_items = self.get_stripe_subscription_items()
        timestamp = self.month_end_timestamp(month)

        result = {
            "month": month,
            "overage": overage,
            "dry_run": not commit,
            "stripe_records": []
        }

        # Sync compute overage
        if overage["compute"]["overage_hours"] > 0:
            compute_payload = {
                "subscription_item": subscription_items["compute"],
                "quantity": int(overage["compute"]["overage_hours"]),
                "timestamp": timestamp,
                "action": "set"
            }

            if commit and subscription_items["compute"]:
                response = self.stripe_post("usage_records", compute_payload)
                result["stripe_records"].append({
                    "type": "compute",
                    "payload": compute_payload,
                    "response": response
                })
            else:
                result["stripe_records"].append({
                    "type": "compute",
                    "payload": compute_payload,
                    "response": None
                })

        # Sync API overage
        if overage["api"]["overage_cost"] > 0:
            # Convert to cents for Stripe
            api_overage_cents = int(overage["api"]["overage_charge"] * 100)

            api_payload = {
                "subscription_item": subscription_items["api"],
                "quantity": api_overage_cents,
                "timestamp": timestamp,
                "action": "set"
            }

            if commit and subscription_items["api"]:
                response = self.stripe_post("usage_records", api_payload)
                result["stripe_records"].append({
                    "type": "api",
                    "payload": api_payload,
                    "response": response
                })
            else:
                result["stripe_records"].append({
                    "type": "api",
                    "payload": api_payload,
                    "response": None
                })

        return result


def main():
    parser = argparse.ArgumentParser(description="Enhanced Stripe Usage Sync")
    parser.add_argument(
        "--month",
        default=datetime.now(timezone.utc).strftime("%Y-%m"),
        help="Billing month (YYYY-MM)"
    )
    parser.add_argument(
        "--db",
        default=os.getenv("MAGIC_BOX_USAGE_DB", "/opt/magic-box/usage.db"),
        help="Path to usage.db"
    )
    parser.add_argument(
        "--commit",
        action="store_true",
        help="Send to Stripe (default: dry-run)"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON"
    )

    args = parser.parse_args()

    sync = StripeUsageSync(db_path=args.db)
    result = sync.sync_to_stripe(args.month, commit=args.commit)

    if args.json:
        print(json.dumps(result, indent=2, default=str))
    else:
        print(f"Month: {result['month']}")
        print(f"Mode: {'COMMIT' if not result['dry_run'] else 'DRY RUN'}")
        print(f"\nOverage Summary:")
        print(f"  Compute: {result['overage']['compute']['overage_hours']:.1f} hours "
              f"= EUR {result['overage']['compute']['overage_charge']:.2f}")
        print(f"  API: EUR {result['overage']['api']['overage_charge']:.2f}")
        print(f"  Total: EUR {result['overage']['total_overage_charge']:.2f}")

        if result['stripe_records']:
            print(f"\nStripe Records:")
            for record in result['stripe_records']:
                status = "SENT" if record['response'] else "PENDING"
                print(f"  {record['type']}: {status}")


if __name__ == "__main__":
    main()
```

### Task 2.2: Create Monthly Sync Script

Create `usage-metering/sync-monthly.sh`:

```bash
#!/bin/bash
# Monthly Stripe Usage Sync
# Run via cron on 1st of each month

set -e

SCRIPT_DIR=$(dirname "$0")
MONTH=$(date -d "last month" +%Y-%m)
LOG_FILE="/var/log/magic-box/billing-sync.log"

echo "[$(date)] Starting monthly sync for $MONTH" >> "$LOG_FILE"

# Run sync
python3 "$SCRIPT_DIR/stripe_sync_v2.py" \
    --month "$MONTH" \
    --commit \
    --json >> "$LOG_FILE" 2>&1

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo "[$(date)] Sync completed successfully" >> "$LOG_FILE"
else
    echo "[$(date)] Sync failed with exit code $EXIT_CODE" >> "$LOG_FILE"
    # Send alert (optional)
    # curl -X POST "https://hooks.slack.com/..." -d '{"text": "Magic Box billing sync failed"}'
fi

exit $EXIT_CODE
```

### Task 2.3: Set Up Cron Job

```bash
# Add to /etc/cron.d/magic-box-billing
# Run at 00:05 on 1st of each month
5 0 1 * * root /opt/magic-box-usage/sync-monthly.sh
```

---

## Phase 3: Customer Portal Integration (Day 3)

### Task 3.1: Add Portal Endpoint to API

Update `usage-metering/api.py`:

```python
@app.route("/api/billing/portal-session", methods=["POST"])
def create_portal_session():
    """Create Stripe Customer Portal session"""
    import stripe
    stripe.api_key = os.getenv("STRIPE_API_KEY")

    customer_id = get_stripe_customer_id()
    if not customer_id:
        return jsonify({"error": "No billing account"}), 400

    return_url = request.json.get("return_url", request.host_url + "dashboard.html")

    session = stripe.billing_portal.Session.create(
        customer=customer_id,
        return_url=return_url
    )

    return jsonify({"url": session.url})


@app.route("/api/billing/subscription", methods=["GET"])
def get_subscription():
    """Get current subscription details"""
    import stripe
    stripe.api_key = os.getenv("STRIPE_API_KEY")

    subscription_id = os.getenv("STRIPE_SUBSCRIPTION_ID")
    if not subscription_id:
        return jsonify({"subscription": None})

    subscription = stripe.Subscription.retrieve(subscription_id)

    return jsonify({
        "subscription": {
            "id": subscription.id,
            "status": subscription.status,
            "current_period_end": subscription.current_period_end,
            "cancel_at_period_end": subscription.cancel_at_period_end,
            "plan": subscription.items.data[0].price.metadata.get("tier", "unknown")
        }
    })
```

### Task 3.2: Update Dashboard

Add billing section to `usage-metering/dashboard.html`:

```html
<!-- Add after usage cards -->
<div class="billing-section" id="billing-section">
    <h2>Subscription</h2>
    <div class="subscription-card">
        <div class="tier-badge" id="tier-badge">Loading...</div>
        <div class="subscription-details">
            <p>Status: <span id="sub-status">-</span></p>
            <p>Renews: <span id="sub-renewal">-</span></p>
        </div>
        <div class="subscription-actions">
            <button onclick="openBillingPortal()" class="btn-primary">
                Manage Subscription
            </button>
            <button onclick="viewInvoices()" class="btn-secondary">
                View Invoices
            </button>
        </div>
    </div>
</div>

<script>
async function loadSubscription() {
    try {
        const response = await fetch('/api/billing/subscription');
        const data = await response.json();

        if (data.subscription) {
            document.getElementById('tier-badge').textContent =
                data.subscription.plan.toUpperCase();
            document.getElementById('sub-status').textContent =
                data.subscription.status;
            document.getElementById('sub-renewal').textContent =
                new Date(data.subscription.current_period_end * 1000)
                    .toLocaleDateString();
        } else {
            document.getElementById('billing-section').innerHTML =
                '<p>No active subscription. <a href="/pricing">Get started</a></p>';
        }
    } catch (error) {
        console.error('Failed to load subscription:', error);
    }
}

async function openBillingPortal() {
    try {
        const response = await fetch('/api/billing/portal-session', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({return_url: window.location.href})
        });
        const data = await response.json();

        if (data.url) {
            window.location.href = data.url;
        } else {
            alert('Failed to open billing portal');
        }
    } catch (error) {
        console.error('Failed to create portal session:', error);
        alert('Failed to open billing portal');
    }
}

async function viewInvoices() {
    openBillingPortal();  // Portal has invoice section
}

// Load on page load
document.addEventListener('DOMContentLoaded', loadSubscription);
</script>

<style>
.billing-section {
    margin-top: 2rem;
    padding: 1.5rem;
    background: #f8f9fa;
    border-radius: 8px;
}

.subscription-card {
    display: flex;
    align-items: center;
    gap: 2rem;
}

.tier-badge {
    background: #4f46e5;
    color: white;
    padding: 0.5rem 1rem;
    border-radius: 4px;
    font-weight: bold;
}

.subscription-actions {
    margin-left: auto;
    display: flex;
    gap: 0.5rem;
}

.btn-primary {
    background: #4f46e5;
    color: white;
    border: none;
    padding: 0.5rem 1rem;
    border-radius: 4px;
    cursor: pointer;
}

.btn-secondary {
    background: white;
    border: 1px solid #4f46e5;
    color: #4f46e5;
    padding: 0.5rem 1rem;
    border-radius: 4px;
    cursor: pointer;
}
</style>
```

---

## Phase 4: Webhook Handler (Day 4)

### Task 4.1: Create Webhook Endpoint

Create `usage-metering/webhooks.py`:

```python
#!/usr/bin/env python3
"""
Stripe Webhook Handler
======================

Handles Stripe webhook events for Magic Box billing.
"""

import json
import os
import sqlite3
from datetime import datetime
from flask import Flask, request

import stripe

app = Flask(__name__)
stripe.api_key = os.getenv("STRIPE_API_KEY")
WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")
DB_PATH = os.getenv("MAGIC_BOX_USAGE_DB", "/opt/magic-box/usage.db")


def log_event(event_type: str, event_id: str, data: dict):
    """Log webhook event to database"""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS stripe_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL,
                event_id TEXT UNIQUE NOT NULL,
                data TEXT,
                processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute(
            "INSERT OR IGNORE INTO stripe_events (event_type, event_id, data) VALUES (?, ?, ?)",
            (event_type, event_id, json.dumps(data))
        )
        conn.commit()


def update_customer_subscription(subscription: dict):
    """Update local customer record with subscription info"""
    customer_id = subscription.get("customer")
    status = subscription.get("status")
    tier = "starter"

    # Extract tier from subscription items
    for item in subscription.get("items", {}).get("data", []):
        price = item.get("price", {})
        if price.get("metadata", {}).get("tier"):
            tier = price["metadata"]["tier"]
            break

    with sqlite3.connect(DB_PATH) as conn:
        # Update or create billing info
        conn.execute("""
            CREATE TABLE IF NOT EXISTS billing_info (
                customer_id TEXT PRIMARY KEY,
                stripe_customer_id TEXT,
                stripe_subscription_id TEXT,
                subscription_status TEXT,
                tier TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            INSERT OR REPLACE INTO billing_info
            (customer_id, stripe_customer_id, stripe_subscription_id, subscription_status, tier)
            VALUES (
                (SELECT id FROM customers LIMIT 1),
                ?, ?, ?, ?
            )
        """, (customer_id, subscription["id"], status, tier))
        conn.commit()


@app.route("/webhooks/stripe", methods=["POST"])
def handle_webhook():
    payload = request.data
    sig_header = request.headers.get("Stripe-Signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, WEBHOOK_SECRET
        )
    except ValueError as e:
        return f"Invalid payload: {e}", 400
    except stripe.error.SignatureVerificationError as e:
        return f"Invalid signature: {e}", 400

    event_type = event["type"]
    event_id = event["id"]
    data = event["data"]["object"]

    # Log all events
    log_event(event_type, event_id, data)

    # Handle specific events
    if event_type == "customer.subscription.created":
        update_customer_subscription(data)
        print(f"Subscription created: {data['id']}")

    elif event_type == "customer.subscription.updated":
        update_customer_subscription(data)
        print(f"Subscription updated: {data['id']}")

    elif event_type == "customer.subscription.deleted":
        update_customer_subscription(data)
        print(f"Subscription deleted: {data['id']}")

    elif event_type == "invoice.paid":
        print(f"Invoice paid: {data['id']} for {data['amount_paid'] / 100} {data['currency']}")

    elif event_type == "invoice.payment_failed":
        print(f"Payment failed for invoice: {data['id']}")
        # TODO: Send alert or pause service

    return "OK", 200


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8586)
```

### Task 4.2: Configure Webhook in Stripe

1. Go to Stripe Dashboard > Developers > Webhooks
2. Add endpoint: `https://your-domain/webhooks/stripe`
3. Select events:
   - `customer.subscription.created`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
   - `invoice.paid`
   - `invoice.payment_failed`
   - `customer.updated`

---

## Phase 5: Testing (Day 5)

### Test Checklist

| Test | Command/Action | Expected Result |
|------|---------------|-----------------|
| Create customer | Stripe Dashboard | Customer created |
| Create subscription | Payment link | Subscription active |
| Generate usage | `usage_tracker.py --collect` | Data in SQLite |
| Calculate overage | `stripe_sync_v2.py --month 2025-01` | Overage calculated |
| Sync to Stripe | `stripe_sync_v2.py --commit` | Usage record created |
| Preview invoice | Stripe Dashboard | Overage shown |
| Customer portal | Click "Manage" button | Portal opens |
| Webhook | Create subscription | Local DB updated |

### Test Script

```bash
#!/bin/bash
# test-billing.sh - Test billing integration

set -e

echo "=== Testing Magic Box Billing ==="

# 1. Test usage tracking
echo "1. Testing usage tracking..."
python3 usage_tracker.py --collect --db /tmp/test-usage.db
python3 usage_tracker.py --summary --db /tmp/test-usage.db

# 2. Test overage calculation
echo "2. Testing overage calculation..."
python3 stripe_sync_v2.py --db /tmp/test-usage.db --month 2025-01 --json

# 3. Test API health
echo "3. Testing API..."
curl -s http://localhost:8585/health | jq

# 4. Test subscription endpoint
echo "4. Testing subscription endpoint..."
curl -s http://localhost:8585/api/billing/subscription | jq

echo "=== All tests passed ==="
```

---

## Deployment Checklist

### Pre-Launch

- [ ] Stripe Products created
- [ ] Stripe Prices created
- [ ] Payment links configured
- [ ] Landing page updated
- [ ] Webhook endpoint deployed
- [ ] Webhook secret configured
- [ ] Customer portal enabled
- [ ] Test subscription created
- [ ] Usage sync tested
- [ ] Overage calculation verified

### Launch

- [ ] Enable live mode in Stripe
- [ ] Update API keys to production
- [ ] Deploy webhook handler
- [ ] Enable cron job
- [ ] Announce to early adopters
- [ ] Monitor first invoices

### Post-Launch

- [ ] Verify first invoice generation
- [ ] Check payment success
- [ ] Monitor webhook logs
- [ ] Collect customer feedback
- [ ] Adjust pricing if needed

---

## Rollback Plan

If issues occur:

1. **Disable cron job**: `crontab -e` and comment out sync
2. **Pause subscriptions**: Stripe Dashboard > Subscriptions > Pause
3. **Revert code**: `git revert HEAD`
4. **Communicate**: Email customers about delay
5. **Debug**: Check logs at `/var/log/magic-box/billing-sync.log`
