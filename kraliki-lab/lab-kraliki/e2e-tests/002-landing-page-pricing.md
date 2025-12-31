# E2E Test: 002 - Landing Page Pricing Section

## Test Information

| Field | Value |
|-------|-------|
| Priority | HIGH |
| Estimated Duration | 8 minutes |
| Prerequisites | Access to Lab by Kraliki landing page |
| URL | https://lab.kraliki.com or http://127.0.0.1:3000 |

## Objective

Verify that the pricing section accurately displays all tiers, features, and CTAs for Lab by Kraliki subscription plans.

## Pre-conditions

1. Landing page accessible
2. Pricing section exists on page

## Pricing Tiers (Reference)

| Tier | Price | Target |
|------|-------|--------|
| Starter | 299 EUR/mo | Freelancers |
| Pro | 499 EUR/mo | Agencies |
| Enterprise | 10K+ EUR/yr | Large orgs |
| Setup + Training | 2,500 EUR | One-time |

## Test Steps

### Step 1: Navigate to Pricing

| Action | Scroll to or click pricing navigation |
|--------|---------------------------------------|
| Expected | Pricing section visible |
| Verification | Section header says "Pricing" or similar |

### Step 2: Starter Tier Display

| Action | Verify Starter tier card |
|--------|--------------------------|
| Expected | - Tier name: "Starter" |
| | - Price: 299 EUR/month displayed |
| | - Target audience mentioned (freelancers) |
| | - Feature list visible |
| | - CTA button present |
| Verification | Visual inspection |

### Step 3: Pro Tier Display

| Action | Verify Pro tier card |
|--------|---------------------|
| Expected | - Tier name: "Pro" |
| | - Price: 499 EUR/month displayed |
| | - Target audience mentioned (agencies) |
| | - Feature list visible |
| | - CTA button present |
| | - May be highlighted as "Most Popular" |
| Verification | Visual inspection |

### Step 4: Enterprise Tier Display

| Action | Verify Enterprise tier card |
|--------|----------------------------|
| Expected | - Tier name: "Enterprise" |
| | - Price: "Custom" or "Contact Us" |
| | - Feature list for enterprise |
| | - Contact CTA instead of signup |
| Verification | Visual inspection |

### Step 5: Feature Comparison

| Action | Check feature differentiation |
|--------|------------------------------|
| Expected | - Each tier shows different features |
| | - Higher tiers include lower tier features |
| | - Clear visual hierarchy |
| Verification | Compare feature lists across tiers |

### Step 6: Pricing CTA Functionality

| Action | Click each tier's CTA button |
|--------|------------------------------|
| Expected | - Starter: Leads to signup or demo |
| | - Pro: Leads to signup or demo |
| | - Enterprise: Leads to contact form |
| Verification | Click and verify destination |

### Step 7: Currency Display

| Action | Verify currency handling |
|--------|--------------------------|
| Expected | - Prices in EUR clearly marked |
| | - Currency symbol visible |
| | - Monthly/yearly toggle (if applicable) |
| Verification | Visual inspection |

### Step 8: Value Propositions

| Action | Check value messaging near pricing |
|--------|-----------------------------------|
| Expected | - ROI messaging (e.g., "80%+ margin") |
| | - Cost comparison to alternatives |
| | - Risk reduction messaging (trial/guarantee) |
| Verification | Visual inspection |

## Pass Criteria

- All three tiers displayed correctly
- Prices match documented pricing
- All CTAs functional
- No broken layouts or overlapping elements

## Edge Cases to Check

| Scenario | Expected Behavior |
|----------|-------------------|
| Very long feature list | Properly contained, no overflow |
| Currency symbol display | Euro sign renders correctly |
| Mobile view | Tiers stack vertically |

## Related Tests

- 001-landing-page-core.md
- 003-responsive-design.md
