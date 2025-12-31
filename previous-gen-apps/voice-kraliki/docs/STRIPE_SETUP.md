# Stripe Subscription Setup Guide

This guide explains how to set up Stripe subscriptions for Voice by Kraliki, supporting both **CC-Lite (B2B)** and **Voice of People (B2C)** products.

---

## Overview

### CC-Lite (B2B) - Contact Center Platform
- **Starter**: $1,500/month - Up to 5 agents, 1,000 AI minutes
- **Professional**: $3,500/month - Up to 15 agents, 3,000 AI minutes

### Voice of People (B2C) - AI Voice Companion
- **Free**: $0/month - 10 AI voice minutes (no subscription needed)
- **Personal**: $9.99/month - 100 AI voice minutes
- **Premium**: $29.99/month - 500 AI voice minutes
- **Pro**: $99.99/month - 2,000 AI voice minutes, API access

---

## Step 1: Install Stripe CLI (Optional)

For testing webhooks locally:

```bash
# macOS
brew install stripe/stripe-cli/stripe

# Linux
curl -s https://packages.stripe.com/api/security/assertions/ip-only.json | jq '.ip_prefixes' | xargs
```

---

## Step 2: Get Stripe API Keys

1. Go to [Stripe Dashboard](https://dashboard.stripe.com/)
2. Navigate to **Developers** > **API keys**
3. Copy your:
   - **Publishable key** (pk_live_... or pk_test_...)
   - **Secret key** (sk_live_... or sk_test_...)
   - **Webhook signing secret** (after creating webhook)

---

## Step 3: Create Products and Prices

### Option A: Use the Automated Script (Recommended)

Run the setup script to create all products and prices:

```bash
cd /home/adminmatej/github/applications/voice-kraliki

# Create in test mode first
python3 scripts/setup_stripe_products.py --test

# If successful, create in production
python3 scripts/setup_stripe_products.py
```

The script will:
1. Create all products (CC-Lite + Voice of People)
2. Create monthly prices for each plan
3. Display Price IDs to add to your `.env` file

### Option B: Manual Setup in Stripe Dashboard

#### For CC-Lite (B2B):

1. Go to **Products** > **Add product**
2. **Product: CC-Lite Starter**
   - Name: `CC-Lite Starter`
   - Description: `Up to 5 agents, 1,000 AI minutes/month`
   - Pricing:
     - Price: $1,500.00
     - Billing period: `Monthly`
   - Click **Save product**
   - Copy the **Price ID** (starts with `price_...`)

3. **Product: CC-Lite Professional**
   - Name: `CC-Lite Professional`
   - Description: `Up to 15 agents, 3,000 AI minutes/month`
   - Pricing:
     - Price: $3,500.00
     - Billing period: `Monthly`
   - Click **Save product**
   - Copy the **Price ID**

#### For Voice of People (B2C):

Repeat for each plan:

| Plan | Name | Price | Features |
|------|------|-------|----------|
| Personal | Voice of People - Personal | $9.99 | 100 AI voice minutes/month |
| Premium | Voice of People - Premium | $29.99 | 500 AI voice minutes/month, priority support |
| Pro | Voice of People - Pro | $99.99 | 2,000 AI voice minutes/month, API access |

---

## Step 4: Configure Environment Variables

Add the Price IDs to your `.env` file:

```bash
# Stripe Configuration
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...

# CC-Lite (B2B) Price IDs
STRIPE_PRICE_ID_CCLITE_STARTER=price_...
STRIPE_PRICE_ID_CCLITE_PROFESSIONAL=price_...

# Voice of People (B2C) Price IDs
STRIPE_PRICE_ID_VOP_PERSONAL=price_...
STRIPE_PRICE_ID_VOP_PREMIUM=price_...
STRIPE_PRICE_ID_VOP_PRO=price_...
```

**Note:** Use test keys (`sk_test_...`) for development.

---

## Step 5: Set Up Webhook

### For Development (Stripe CLI):

```bash
# Forward webhook events to your local server
stripe listen --forward-to localhost:8000/api/v1/billing/webhook

# Copy the webhook signing secret (starts with whsec_...)
# Add it to STRIPE_WEBHOOK_SECRET in .env
```

### For Production:

1. In Stripe Dashboard, go to **Developers** > **Webhooks**
2. Click **Add endpoint**
3. URL: `https://yourdomain.com/api/v1/billing/webhook`
4. Select events to send:
   - `checkout.session.completed`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
   - `invoice.payment_succeeded`
   - `invoice.payment_failed`
5. Click **Add endpoint**
6. Copy the **Webhook signing secret** to `.env`

---

## Step 6: Test the Integration

### Test in Stripe Test Mode:

1. Ensure you're using test keys (`sk_test_...`)
2. Use the API endpoint to create a checkout session:
   ```bash
   curl -X POST http://localhost:8000/api/v1/billing/checkout-session \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     -d '{"product": "vop", "plan": "personal"}'
   ```
3. You'll receive a `url` - open it to see the Stripe checkout
4. Complete payment with test card: `4242 4242 4242 4242` (any future date, any CVC)
5. Verify webhook is received and user is marked as premium

### Expected Webhook Events:

- `checkout.session.completed`: User successfully subscribed
- `customer.subscription.updated`: Subscription changed (upgrade/downgrade)
- `customer.subscription.deleted`: Subscription cancelled

---

## Step 7: Monitor Subscriptions

### View in Stripe Dashboard:

1. Go to **Billing** > **Subscriptions**
2. View all active subscriptions
3. Filter by product (CC-Lite vs Voice of People)

### View in Application:

The billing API provides endpoints:
- `GET /api/v1/billing/plans` - List available plans
- `POST /api/v1/billing/checkout-session` - Create checkout session
- `GET /api/v1/billing/portal-session` - Customer portal (manage subscription)

---

## Usage Tracking

Voice minutes are tracked in the `usage_records` table:

```python
from app.models.usage import UsageRecord

# Record usage
usage = UsageRecord(
    user_id=user.id,
    service_type="voice_minutes",
    quantity=60,  # duration in seconds
    reference_id="session_123",
    timestamp=datetime.now(timezone.utc)
)
db.add(usage)
await db.commit()
```

---

## Billing API Usage Examples

### Get Available Plans:

```bash
curl http://localhost:8000/api/v1/billing/plans
```

Response:
```json
{
  "cc_lite": [
    {
      "id": "starter",
      "name": "Starter",
      "product": "cc_lite",
      "price": 1500.00,
      "currency": "USD",
      "interval": "month",
      "features": [...],
      "recommended": false
    },
    ...
  ],
  "vop": [
    {
      "id": "personal",
      "name": "Personal",
      "product": "vop",
      "price": 9.99,
      "currency": "USD",
      "interval": "month",
      "voice_minutes_included": 100,
      "features": [...],
      "recommended": false
    },
    ...
  ]
}
```

### Create Checkout Session (Voice of People - Premium):

```bash
curl -X POST http://localhost:8000/api/v1/billing/checkout-session \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "product": "vop",
    "plan": "premium",
    "success_url": "https://voice.kraliki.com/settings/billing?payment=success",
    "cancel_url": "https://voice.kraliki.com/settings/billing?payment=cancelled"
  }'
```

Response:
```json
{
  "sessionId": "cs_test_...",
  "url": "https://checkout.stripe.com/c/pay/..."
}
```

### Create Customer Portal Session:

```bash
curl -X GET "http://localhost:8000/api/v1/billing/portal-session?return_url=/settings/billing" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

Response:
```json
{
  "url": "https://billing.stripe.com/session/..."
}
```

---

## Troubleshooting

### Webhook Not Received:

1. Check webhook URL is publicly accessible
2. Verify webhook secret in `.env` matches Stripe dashboard
3. Check server logs for webhook processing errors

### Price Not Found:

1. Verify price IDs in `.env` are correct
2. Ensure prices exist in Stripe dashboard (use `--list` flag)
3. Check you're using the correct Stripe account (test vs live)

### Checkout Session Fails:

1. Verify JWT token is valid
2. Check user exists in database
3. Ensure Stripe customer ID is set or can be created

---

## Security Notes

1. **Never commit `.env` to git** - it contains Stripe secret keys
2. **Use separate API keys** for test and production
3. **Verify webhook signatures** in your handler (implemented in `billing.py`)
4. **Restrict webhook events** to only those needed
5. **Monitor Stripe dashboard** for suspicious activity

---

## Support

- Stripe Documentation: https://stripe.com/docs
- Stripe API Reference: https://stripe.com/docs/api
- Voice of Strategy Document: `verduona-business/01-ACTIVE-STRATEGY/VOICE_APP_MONETIZATION_STRATEGY.md`

---

## Next Steps

After setup is complete:
1. Test checkout flow end-to-end
2. Implement usage tracking (voice minutes)
3. Set up usage-based billing (optional)
4. Create billing UI in frontend
5. Monitor revenue metrics in Stripe dashboard
