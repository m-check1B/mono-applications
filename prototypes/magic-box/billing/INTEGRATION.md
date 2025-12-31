# Stripe Billing Integration Guide

**Version**: 1.0.0
**Last Updated**: 2025-12-28

---

## Overview

This document details the Stripe integration for Magic Box billing.

---

## Why Stripe

1. **Proven Platform**: Industry standard for SaaS billing
2. **Metered Billing**: Native support for usage-based pricing
3. **Customer Portal**: Built-in self-service portal
4. **Global Payments**: Handles multi-currency, taxes
5. **Existing Foundation**: `stripe_sync.py` already implemented

---

## Stripe Product Structure

### Products

| Product ID | Name | Description |
|------------|------|-------------|
| `prod_magicbox_starter` | Magic Box Starter | Solo developer tier |
| `prod_magicbox_pro` | Magic Box Pro | Growing team tier |
| `prod_magicbox_enterprise` | Magic Box Enterprise | Large team tier |

### Prices

**Base Subscription Prices:**

| Price ID | Product | Amount | Interval |
|----------|---------|--------|----------|
| `price_starter_monthly` | Starter | EUR 99 | Monthly |
| `price_starter_annual` | Starter | EUR 990 | Yearly |
| `price_pro_monthly` | Pro | EUR 199 | Monthly |
| `price_pro_annual` | Pro | EUR 1,990 | Yearly |
| `price_enterprise_monthly` | Enterprise | EUR 499 | Monthly |
| `price_enterprise_annual` | Enterprise | EUR 4,990 | Yearly |

**Metered Overage Prices:**

| Price ID | Description | Unit Amount | Usage Type |
|----------|-------------|-------------|------------|
| `price_compute_overage_starter` | Compute overage (Starter) | EUR 0.05 | Metered |
| `price_compute_overage_pro` | Compute overage (Pro) | EUR 0.04 | Metered |
| `price_api_overage` | API overage | EUR 0.01 | Metered |

---

## Subscription Structure

Each customer subscription includes:

1. **Base Price**: Fixed monthly/annual fee
2. **Compute Overage**: Metered price for excess compute hours
3. **API Overage**: Metered price for excess API credits

Example subscription items:

```json
{
  "subscription": "sub_123",
  "items": [
    {
      "id": "si_base",
      "price": "price_pro_monthly",
      "quantity": 1
    },
    {
      "id": "si_compute",
      "price": "price_compute_overage_pro",
      "quantity": 0
    },
    {
      "id": "si_api",
      "price": "price_api_overage",
      "quantity": 0
    }
  ]
}
```

---

## Usage Record Flow

### Local Collection

```
[VM] --> usage_tracker.py --> usage.db (SQLite)
                                  |
                                  v
                        [Monthly aggregation]
                                  |
                                  v
                        [stripe_sync.py]
                                  |
                                  v
                        [Stripe Usage Record API]
```

### Sync Process

1. **Monthly Cron** (1st of each month at 00:00):
   ```bash
   python3 stripe_sync.py --month $(date -d "last month" +%Y-%m) --commit
   ```

2. **Usage Record Created**:
   ```python
   stripe.UsageRecord.create(
       subscription_item="si_compute",
       quantity=compute_overage_hours,
       timestamp=month_end_timestamp,
       action="set"
   )
   ```

3. **Stripe Invoice**:
   - Base subscription billed at cycle start
   - Overage added to invoice at cycle end
   - Invoice finalized and sent

---

## API Integration

### Environment Variables

```bash
# Required
STRIPE_API_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Per-customer (stored in usage.db)
STRIPE_CUSTOMER_ID=cus_...
STRIPE_SUBSCRIPTION_ID=sub_...
STRIPE_SUBSCRIPTION_ITEM_COMPUTE=si_...
STRIPE_SUBSCRIPTION_ITEM_API=si_...
```

### Customer Creation

```python
import stripe

def create_stripe_customer(customer):
    """Create Stripe customer from Magic Box customer"""
    stripe_customer = stripe.Customer.create(
        email=customer.email,
        name=customer.name,
        metadata={
            "magic_box_customer_id": customer.id,
            "magic_box_vm_id": customer.vm_id
        }
    )
    return stripe_customer.id
```

### Subscription Creation

```python
def create_subscription(customer_id, tier):
    """Create subscription for customer"""
    prices = {
        "starter": {
            "base": "price_starter_monthly",
            "compute": "price_compute_overage_starter",
            "api": "price_api_overage"
        },
        "pro": {
            "base": "price_pro_monthly",
            "compute": "price_compute_overage_pro",
            "api": "price_api_overage"
        },
        "enterprise": {
            "base": "price_enterprise_monthly",
            "compute": None,  # Unlimited
            "api": "price_api_overage"
        }
    }

    tier_prices = prices[tier]
    items = [{"price": tier_prices["base"]}]

    if tier_prices["compute"]:
        items.append({"price": tier_prices["compute"]})

    items.append({"price": tier_prices["api"]})

    subscription = stripe.Subscription.create(
        customer=customer_id,
        items=items,
        payment_behavior="default_incomplete",
        expand=["latest_invoice.payment_intent"]
    )

    return subscription
```

### Usage Reporting

```python
def report_usage(subscription_item_id, quantity, timestamp):
    """Report usage to Stripe"""
    usage_record = stripe.UsageRecord.create(
        subscription_item=subscription_item_id,
        quantity=quantity,
        timestamp=int(timestamp.timestamp()),
        action="set"  # Replace previous value for this period
    )
    return usage_record
```

---

## Webhook Handling

### Required Webhooks

| Event | Action |
|-------|--------|
| `customer.subscription.created` | Store subscription IDs locally |
| `customer.subscription.updated` | Update tier in local DB |
| `customer.subscription.deleted` | Mark customer as inactive |
| `invoice.paid` | Log successful payment |
| `invoice.payment_failed` | Send alert, pause if needed |
| `customer.updated` | Sync customer details |

### Webhook Endpoint

```python
from flask import Flask, request
import stripe

app = Flask(__name__)

@app.route("/webhooks/stripe", methods=["POST"])
def stripe_webhook():
    payload = request.data
    sig_header = request.headers.get("Stripe-Signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        return "Invalid payload", 400
    except stripe.error.SignatureVerificationError:
        return "Invalid signature", 400

    if event["type"] == "customer.subscription.created":
        handle_subscription_created(event["data"]["object"])
    elif event["type"] == "customer.subscription.updated":
        handle_subscription_updated(event["data"]["object"])
    elif event["type"] == "invoice.paid":
        handle_invoice_paid(event["data"]["object"])
    elif event["type"] == "invoice.payment_failed":
        handle_payment_failed(event["data"]["object"])

    return "OK", 200
```

---

## Customer Portal Integration

### Enable Customer Portal

In Stripe Dashboard:
1. Go to Settings > Billing > Customer portal
2. Enable portal
3. Configure allowed actions:
   - Update payment method: Yes
   - Cancel subscription: Yes
   - Switch plans: Yes
   - View invoices: Yes
   - Update billing address: Yes

### Portal Session Creation

```python
def create_portal_session(customer_id, return_url):
    """Create Stripe Customer Portal session"""
    session = stripe.billing_portal.Session.create(
        customer=customer_id,
        return_url=return_url
    )
    return session.url
```

### Dashboard Integration

Add button to usage dashboard:

```html
<button onclick="openBillingPortal()">Manage Subscription</button>

<script>
async function openBillingPortal() {
    const response = await fetch('/api/billing/portal-session', {
        method: 'POST'
    });
    const data = await response.json();
    window.location.href = data.url;
}
</script>
```

---

## Coupons and Discounts

### Early Adopter Coupon

```python
stripe.Coupon.create(
    id="EARLYBIRD30",
    percent_off=30,
    duration="forever",
    metadata={"description": "Early adopter 30% lifetime discount"}
)
```

### Annual Discount

Built into annual pricing (17% off).

### Promotional Coupon

```python
stripe.Coupon.create(
    id="LAUNCH2025",
    percent_off=20,
    duration="once",
    redeem_by=1735689600,  # Dec 31, 2025
    max_redemptions=100
)
```

---

## Testing

### Test Mode Setup

1. Use Stripe test API keys (`sk_test_...`)
2. Use test card numbers:
   - Success: `4242 4242 4242 4242`
   - Decline: `4000 0000 0000 0002`
   - 3D Secure: `4000 0025 0000 3155`

### Test Workflow

```bash
# 1. Create test customer
python3 -c "
import stripe
stripe.api_key = 'sk_test_...'
customer = stripe.Customer.create(email='test@example.com')
print(customer.id)
"

# 2. Create test subscription
python3 -c "
import stripe
stripe.api_key = 'sk_test_...'
subscription = stripe.Subscription.create(
    customer='cus_test123',
    items=[{'price': 'price_starter_monthly'}],
    payment_behavior='default_incomplete'
)
print(subscription.id)
"

# 3. Simulate usage sync
python3 stripe_sync.py --month 2025-01 --subscription-item si_test123

# 4. Preview invoice
python3 -c "
import stripe
stripe.api_key = 'sk_test_...'
invoice = stripe.Invoice.upcoming(customer='cus_test123')
print(invoice.amount_due / 100)
"
```

---

## Error Handling

### Common Errors

| Error | Cause | Resolution |
|-------|-------|------------|
| `card_declined` | Payment failed | Email customer, retry in 3 days |
| `expired_card` | Card expired | Prompt card update via portal |
| `insufficient_funds` | NSF | Email customer, retry in 7 days |
| `rate_limit` | Too many API calls | Implement exponential backoff |
| `resource_missing` | Invalid subscription | Re-sync customer data |

### Retry Logic

```python
import time
from functools import wraps

def retry_on_failure(max_retries=3, delay=1):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except stripe.error.RateLimitError:
                    if attempt < max_retries - 1:
                        time.sleep(delay * (2 ** attempt))
                    else:
                        raise
                except stripe.error.APIConnectionError:
                    if attempt < max_retries - 1:
                        time.sleep(delay)
                    else:
                        raise
            return None
        return wrapper
    return decorator

@retry_on_failure(max_retries=3)
def sync_usage_to_stripe(customer_id, usage):
    # Sync logic here
    pass
```

---

## Security Considerations

1. **API Keys**: Store in environment variables, never in code
2. **Webhook Verification**: Always verify webhook signatures
3. **Idempotency**: Use idempotency keys for all create operations
4. **Audit Log**: Log all billing operations locally
5. **PCI Compliance**: Never handle raw card data (use Stripe.js)

---

## Monitoring

### Key Metrics

| Metric | Description | Alert Threshold |
|--------|-------------|-----------------|
| Sync Success Rate | % of usage syncs that succeed | < 95% |
| Payment Success Rate | % of payments that succeed | < 90% |
| Webhook Response Time | Time to process webhooks | > 5 seconds |
| Failed Invoices | Count of unpaid invoices | > 5 |

### Health Check

```python
def check_stripe_health():
    """Check Stripe API connectivity"""
    try:
        stripe.Balance.retrieve()
        return {"status": "healthy"}
    except stripe.error.StripeError as e:
        return {"status": "unhealthy", "error": str(e)}
```

---

## LemonSqueezy Alternative

If Stripe is not suitable, LemonSqueezy can be used:

### Advantages
- Merchant of Record (handles taxes globally)
- Simpler setup
- Built for digital products

### Limitations
- Less flexible metered billing
- Would need custom usage sync webhook
- No existing integration code

### Implementation Effort
- Additional 5-7 days vs Stripe
- Custom webhook development required
- New SDK to integrate

**Recommendation**: Stick with Stripe unless MoR is required.
