# Magic Box Billing Strategy

**Version**: 1.0.0
**Last Updated**: 2025-12-28
**Status**: Planning

---

## Executive Summary

Magic Box is a self-hosted multi-AI orchestration platform. This document outlines the billing strategy that balances:

1. **Privacy-first**: All metering happens locally on customer VMs
2. **Fair pricing**: Customers pay for what they use
3. **Transparency**: Clear cost breakdown visible to customers
4. **Easy implementation**: Leverage existing usage-metering infrastructure

---

## Table of Contents

1. [Pricing Model Analysis](#pricing-model-analysis)
2. [Recommended Pricing Structure](#recommended-pricing-structure)
3. [Integration Options](#integration-options)
4. [Technical Implementation](#technical-implementation)
5. [Usage Metering Specification](#usage-metering-specification)
6. [Billing Dashboard](#billing-dashboard)
7. [Customer Portal Requirements](#customer-portal-requirements)
8. [Early Adopter Migration](#early-adopter-migration)

---

## Pricing Model Analysis

### Option 1: Fixed Subscription

| Tier | Monthly Price | Included Features |
|------|---------------|-------------------|
| Starter | EUR 99/month | 1 VM, basic prompts, email support |
| Pro | EUR 199/month | 2 VMs, all prompts, priority support, custom patterns |
| Enterprise | EUR 499/month | Unlimited VMs, dedicated support, SLA, custom integrations |

**Pros:**
- Predictable revenue
- Simple billing operations
- Easy customer budgeting

**Cons:**
- Not fair for low-usage customers
- May deter experimentation
- Undercharges heavy users

**Verdict**: Good for base platform access, but does not account for actual AI API consumption.

---

### Option 2: Pure Usage-Based

| Metric | Price |
|--------|-------|
| API tokens (input) | Pass-through + 20% margin |
| API tokens (output) | Pass-through + 20% margin |
| Compute hours | EUR 0.05/hour |
| Pattern executions | EUR 0.01/execution |

**Pros:**
- Perfectly fair
- Scales with usage
- Encourages experimentation (low barrier)

**Cons:**
- Unpredictable costs for customers
- Complex billing operations
- Revenue volatility

**Verdict**: Fair but creates budget anxiety for customers.

---

### Option 3: Hybrid (RECOMMENDED)

Combines base subscription with usage-based overage:

| Tier | Base Price | Included Compute | Included API Credits | Overage |
|------|------------|------------------|---------------------|---------|
| Starter | EUR 99/mo | 100 hours | EUR 50 API credits | Pay-as-you-go |
| Pro | EUR 199/mo | 300 hours | EUR 150 API credits | Pay-as-you-go |
| Enterprise | EUR 499/mo | Unlimited | EUR 500 API credits | Discounted rates |

**Overage Pricing:**
- Compute: EUR 0.05/hour beyond included
- API: Pass-through cost + 15% margin

**Pros:**
- Predictable base cost
- Fair overage billing
- Encourages upgrade to higher tiers
- Reduces billing complexity for typical usage

**Cons:**
- Slightly more complex than pure subscription
- Requires usage tracking

**Verdict**: Best balance of predictability and fairness.

---

## Recommended Pricing Structure

### Primary Recommendation: Hybrid Model

Based on analysis, the **Hybrid Model** is recommended for the following reasons:

1. **Customer-friendly**: Base subscription covers typical usage
2. **Fair**: Overage ensures heavy users pay proportionally
3. **Revenue optimization**: Captures value from both steady and variable usage
4. **Privacy-aligned**: All metering happens locally, only summary data synced for billing

### Detailed Tier Structure

#### Starter Tier - EUR 99/month
- **Target**: Solo developers, small teams
- **Included**:
  - 1 Magic Box VM license
  - 100 compute hours/month
  - EUR 50 in API credits (Claude, Gemini, OpenAI)
  - Basic prompt library (12 prompts)
  - Community support (Discord/forum)
  - Usage dashboard access
- **Overage**:
  - Compute: EUR 0.05/hour
  - API: Pass-through + 20% margin

#### Pro Tier - EUR 199/month
- **Target**: Growing teams, agencies
- **Included**:
  - Up to 3 Magic Box VM licenses
  - 300 compute hours/month
  - EUR 150 in API credits
  - Full prompt library (22+ prompts)
  - Custom pattern creation tools
  - Priority email support
  - Team usage dashboard
- **Overage**:
  - Compute: EUR 0.04/hour
  - API: Pass-through + 15% margin

#### Enterprise Tier - EUR 499/month
- **Target**: Large teams, enterprises
- **Included**:
  - Unlimited VM licenses
  - Unlimited compute hours
  - EUR 500 in API credits
  - Full prompt library + custom development
  - Dedicated Slack channel
  - SLA (99.9% uptime)
  - Central dashboard for all VMs
  - Custom integrations
- **Overage**:
  - API: Pass-through + 10% margin

### Annual Discounts
- **Starter Annual**: EUR 990/year (17% discount)
- **Pro Annual**: EUR 1,990/year (17% discount)
- **Enterprise Annual**: EUR 4,990/year (17% discount)

---

## Integration Options

### Option A: Stripe Billing (RECOMMENDED)

**Why Stripe:**
- Industry standard for SaaS billing
- Excellent metered billing support
- Built-in customer portal
- Handles invoicing, taxes, and compliance
- Existing landing page integration ready

**Architecture:**
```
[Customer VM] ---> [Local Usage DB] ---> [Monthly Sync] ---> [Stripe]
                                              |
                                    Usage Record API
                                              |
                                    [Stripe Subscription Item]
```

**Implementation:**
1. Create Stripe Products for each tier
2. Create metered Price for overage
3. Monthly cron syncs usage to Stripe
4. Stripe generates invoices automatically

**Existing Code**: `usage-metering/stripe_sync.py` already implements basic sync.

**Effort**: Low (2-3 days)

---

### Option B: LemonSqueezy

**Why Consider:**
- Simpler setup than Stripe
- Built for digital products
- Good for EU/VAT handling
- Merchant of Record (handles taxes)

**Limitations:**
- Less flexible metered billing
- Would need custom webhook for usage sync
- No existing integration code

**Effort**: Medium (5-7 days)

---

### Option C: Self-Hosted Billing

**Why Consider:**
- Full control
- No payment processor fees
- Privacy-first (no external data)

**Limitations:**
- Must handle invoicing manually
- No payment collection (bank transfer only)
- No customer portal
- Significant development effort

**Effort**: High (2-3 weeks)

---

### Recommendation: Stripe Billing

Stripe is the clear winner because:
1. Existing `stripe_sync.py` provides foundation
2. Landing page already has Stripe payment links
3. Handles compliance (PSD2, VAT, invoicing)
4. Customer portal included
5. Best metered billing support

---

## Technical Implementation

### Phase 1: Stripe Setup (Day 1)

1. **Create Stripe Products:**
   - `magic-box-starter` - EUR 99/month
   - `magic-box-pro` - EUR 199/month
   - `magic-box-enterprise` - EUR 499/month

2. **Create Metered Prices:**
   - `magic-box-compute-overage` - EUR 0.05/unit (1 unit = 1 hour)
   - `magic-box-api-overage` - EUR 0.01/unit (1 unit = 1 cent of API cost)

3. **Configure Payment Links:**
   - Update `docs/landing-page.html` with real Stripe links
   - Run `scripts/configure_stripe_links.sh`

### Phase 2: Usage Sync Automation (Day 2)

1. **Enhance stripe_sync.py:**
   - Add compute hours reporting
   - Add API credits tracking
   - Add multi-subscription-item support

2. **Create Monthly Sync Cron:**
   ```bash
   # /etc/cron.d/magic-box-billing
   0 0 1 * * root /opt/magic-box-usage/sync-to-stripe.sh
   ```

3. **Sync Script:**
   ```bash
   #!/bin/bash
   MONTH=$(date -d "last month" +%Y-%m)
   python3 /opt/magic-box-usage/stripe_sync.py \
     --month $MONTH \
     --commit
   ```

### Phase 3: Customer Portal (Day 3)

1. **Stripe Customer Portal:**
   - Enable in Stripe Dashboard
   - Configure allowed actions (cancel, upgrade, payment method)

2. **Integration:**
   - Add "Manage Subscription" button to usage dashboard
   - Link to Stripe Customer Portal session

### Phase 4: Testing & Launch

1. **Test Flow:**
   - Create test subscription
   - Generate test usage data
   - Run sync in dry-run mode
   - Verify Stripe records
   - Run sync with --commit
   - Check invoice preview

2. **Launch Checklist:**
   - [ ] Stripe Products created
   - [ ] Payment links tested
   - [ ] Sync script deployed
   - [ ] Customer portal enabled
   - [ ] Early adopters migrated
   - [ ] Documentation updated

---

## Usage Metering Specification

### Metrics Collected

| Metric | Collection Interval | Storage | Sync to Stripe |
|--------|---------------------|---------|----------------|
| API tokens (input) | Per request | SQLite | Monthly (aggregated) |
| API tokens (output) | Per request | SQLite | Monthly (aggregated) |
| Compute hours | Every 5 minutes | SQLite | Monthly (aggregated) |
| Command executions | Per command | SQLite | Not synced (analytics only) |
| Pattern usage | Per execution | SQLite | Not synced (analytics only) |

### Local Storage Schema

See `usage-metering/schema.sql` for complete schema.

Key tables:
- `api_usage`: Token counts per request
- `resource_usage`: CPU/memory snapshots
- `billing_reports`: Monthly aggregates

### Billing Aggregation

Monthly billing report calculation:

```python
def calculate_monthly_bill(customer_id, month):
    # Get tier and included amounts
    tier = get_customer_tier(customer_id)
    included_compute = tier.included_compute_hours
    included_api_credits = tier.included_api_credits

    # Calculate actual usage
    compute_hours = calculate_compute_hours(customer_id, month)
    api_cost = calculate_api_cost(customer_id, month)

    # Calculate overage
    compute_overage = max(0, compute_hours - included_compute)
    api_overage = max(0, api_cost - included_api_credits)

    # Calculate overage charges
    compute_charge = compute_overage * tier.compute_overage_rate
    api_charge = api_overage * (1 + tier.api_margin)

    return {
        "base_subscription": tier.price,
        "compute_hours": compute_hours,
        "compute_overage": compute_overage,
        "compute_charge": compute_charge,
        "api_cost": api_cost,
        "api_overage": api_overage,
        "api_charge": api_charge,
        "total": tier.price + compute_charge + api_charge
    }
```

### Privacy Considerations

**Local Data (never leaves VM):**
- Raw token counts per request
- Resource snapshots every 5 minutes
- Command history
- Pattern usage logs

**Synced to Stripe (monthly aggregate only):**
- Total compute hours
- Total API cost (in cents)
- Customer ID and email

**No synced data:**
- Actual prompts or responses
- File contents
- Detailed command arguments
- Individual API request logs

---

## Billing Dashboard

### Customer-Facing Dashboard

The existing dashboard at `usage-metering/dashboard.html` provides:

1. **Usage Overview:**
   - Current month API costs
   - Compute hours used
   - Remaining included credits
   - Projected end-of-month total

2. **Cost Breakdown:**
   - By AI provider (Claude, OpenAI, Gemini)
   - By model
   - By day/week

3. **Resource Utilization:**
   - CPU usage graph
   - Memory usage graph
   - Disk usage

4. **Export Functions:**
   - Download JSON usage data
   - Download CSV for accounting

### Required Enhancements

1. **Subscription Status Widget:**
   - Current tier
   - Renewal date
   - "Upgrade" button
   - "Manage Subscription" link (Stripe Portal)

2. **Overage Warning:**
   - Alert when approaching included limits
   - Estimated overage cost
   - Upgrade recommendation

3. **Invoice History:**
   - Link to Stripe invoices
   - Payment status

### Mockup Description

```
+--------------------------------------------------+
|  Magic Box Usage Dashboard                       |
|  Tier: Pro | Renewal: Feb 1, 2025               |
+--------------------------------------------------+
|                                                  |
|  [Current Month: January 2025]                   |
|                                                  |
|  +---------------+  +---------------+            |
|  | Compute Hours |  | API Credits   |            |
|  |     245/300   |  |  EUR 120/150  |            |
|  |  [====80%====]|  |  [===80%====] |            |
|  +---------------+  +---------------+            |
|                                                  |
|  Estimated Total: EUR 199 (no overage)           |
|                                                  |
|  +------------------------------------------+    |
|  |  API Usage by Provider                   |    |
|  |  [Chart: Claude 65%, Gemini 25%, GPT 10%]|    |
|  +------------------------------------------+    |
|                                                  |
|  +------------------------------------------+    |
|  |  Daily Usage Trend                        |   |
|  |  [Line chart showing 30-day trend]        |   |
|  +------------------------------------------+    |
|                                                  |
|  [Export JSON]  [Export CSV]  [Manage Sub]       |
+--------------------------------------------------+
```

---

## Customer Portal Requirements

### Self-Service Capabilities

1. **Subscription Management:**
   - View current plan
   - Upgrade/downgrade tier
   - Cancel subscription
   - Update billing cycle (monthly/annual)

2. **Payment Management:**
   - Update credit card
   - View payment history
   - Download invoices
   - Update billing email

3. **Usage & Billing:**
   - View current usage
   - View past billing reports
   - Download usage data
   - Set spending alerts

4. **Account Settings:**
   - Update contact info
   - Manage VM licenses
   - Generate API keys
   - View documentation

### Implementation via Stripe

Stripe Customer Portal handles most requirements:
- Payment method management
- Invoice downloads
- Subscription changes
- Billing email updates

Custom dashboard handles:
- Usage visualization
- VM management
- Documentation access
- Spending alerts

### Portal Access Flow

```
User clicks "Manage Subscription" in dashboard
    |
    v
Backend generates Stripe Portal Session
    |
    v
User redirected to Stripe Customer Portal
    |
    v
User makes changes (payment, plan, cancel)
    |
    v
Stripe sends webhook to update local state
    |
    v
User returned to dashboard with updated info
```

---

## Early Adopter Migration

### Migration Strategy

For customers who signed up before billing launch:

#### Phase 1: Grace Period (First Month)

1. **Notification:**
   - Email all early adopters about upcoming billing
   - Explain new pricing structure
   - Offer loyalty discount

2. **Grandfather Offer:**
   - 30% lifetime discount on Pro tier
   - Locked rate: EUR 139/month (vs EUR 199)
   - Must convert by deadline

3. **Usage Tracking:**
   - Start tracking usage immediately
   - Provide usage reports for transparency
   - Help customers choose appropriate tier

#### Phase 2: Conversion (Month 2)

1. **Tier Assignment:**
   - Based on actual usage data from grace period
   - Recommend appropriate tier
   - Offer trial of higher tier

2. **Payment Collection:**
   - Create Stripe subscriptions
   - Send payment links
   - Follow up on failed payments

3. **Support:**
   - Dedicated migration support
   - Q&A sessions
   - Individual consultations

#### Phase 3: Stabilization (Month 3+)

1. **Monitoring:**
   - Watch for tier mismatches
   - Proactive upgrade suggestions
   - Identify churn risks

2. **Feedback:**
   - Collect pricing feedback
   - Adjust if needed
   - Document learnings

### Migration Timeline

| Week | Action |
|------|--------|
| Week 1 | Enable usage tracking on all VMs |
| Week 2 | Send announcement email |
| Week 3 | Individual outreach to high-value customers |
| Week 4 | End of grace period warning |
| Month 2 | Begin billing, offer 1-week extension for stragglers |
| Month 3 | Full billing active, migration complete |

### Migration Script

```bash
#!/bin/bash
# migrate-early-adopter.sh
# Migrates an early adopter to paid billing

CUSTOMER_ID=$1
TIER=$2  # starter, pro, enterprise
DISCOUNT=$3  # e.g., 30 for 30% off

echo "Migrating $CUSTOMER_ID to $TIER tier with ${DISCOUNT}% discount"

# 1. Create Stripe customer if not exists
stripe customers create \
  --email $(get_customer_email $CUSTOMER_ID) \
  --name $(get_customer_name $CUSTOMER_ID) \
  --metadata[magic_box_customer_id]=$CUSTOMER_ID

# 2. Create subscription with coupon
stripe subscriptions create \
  --customer $(get_stripe_customer_id $CUSTOMER_ID) \
  --items[0][price]=$(get_price_id $TIER) \
  --coupon=EARLYBIRD$DISCOUNT

# 3. Update local database
update_customer_billing_status $CUSTOMER_ID "active" $TIER

echo "Migration complete for $CUSTOMER_ID"
```

---

## Files in This Directory

| File | Purpose |
|------|---------|
| `README.md` | This document - billing strategy overview |
| `PRICING.md` | Detailed pricing tiers and calculations |
| `INTEGRATION.md` | Stripe integration guide |
| `IMPLEMENTATION.md` | Technical implementation plan |
| `METERING.md` | Usage metering specification |
| `DASHBOARD.md` | Billing dashboard requirements |
| `PORTAL.md` | Customer portal requirements |
| `MIGRATION.md` | Early adopter migration plan |

---

## Next Steps

1. **Immediate**: Review and approve pricing structure
2. **Week 1**: Set up Stripe Products and Prices
3. **Week 2**: Enhance stripe_sync.py for full billing
4. **Week 3**: Deploy to early adopter VMs
5. **Week 4**: Launch billing with migration program

---

## Contact

For questions about Magic Box billing:
- Email: billing@verduona.com
- Slack: #magic-box-billing
