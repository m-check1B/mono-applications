# Test 009: Audit Booking (B2B)

**Feature:** /audit command - The Reality Check professional audit
**Priority:** P0 (Critical - Revenue Feature)
**Type:** Telegram Bot
**Estimated Time:** 3 minutes

## Objective

Verify the B2B audit booking feature displays correct information and links to the payment/booking system.

## Business Context

"The Reality Check" is a professional sensitivity audit service:
- **Price:** EUR 500 per 1-hour session
- **Target:** B2B clients, HR professionals, teams
- **Delivery:** 60-minute Zoom consultation
- **Includes:** Personalized analysis + action plan

## Preconditions

- Bot is running
- AUDIT_PRICE_EUR configured in settings
- AUDIT_PAYMENT_LINK configured (Stripe/Cal.com link)

## Test Steps

### Test 9.1: View Audit Information

1. Send `/audit`
2. **Expected:** Detailed audit description:

```
The Reality Check: Professional Sensitivity Audit

Unlock a deeper understanding of your sensitivity with
'The Reality Check'—our premier B2B consulting service...

What's included in this 1-hour session:
- In-depth analysis of your birth chart and biorhythms
- Review of your dream patterns and subconscious signals
- Environmental assessment (location, workspace, EMF)
- Personalized coping strategies and performance optimization plan
- Direct Q&A with a Sense by Kraliki expert

Price: EUR 500
Duration: 60 minutes via Zoom

[Book Your Reality Check Now](payment_link)
```

### Test 9.2: Payment Link Present

1. Send `/audit`
2. **Expected:** Clickable link to booking/payment
3. Link format: Markdown or inline button

### Test 9.3: Link Opens Correctly

1. Click the booking link
2. **Expected:** Opens payment page (Stripe or Cal.com)
3. Page shows correct price and service details

### Test 9.4: Analytics Tracking

1. Send `/audit`
2. **Expected:** Command tracked in analytics
3. Can verify via `/stats` (admin only)

### Test 9.5: Audit vs Subscribe Distinction

1. Compare `/audit` and `/subscribe` outputs
2. **Expected:**
   - `/subscribe`: Telegram Stars, self-service
   - `/audit`: EUR 500, human consultation

### Test 9.6: Target Audience Language

1. Review audit description text
2. **Expected:** B2B-focused language:
   - "Professionals and teams"
   - "Performance optimization"
   - "Consulting service"

## Success Criteria

- [ ] /audit shows complete service description
- [ ] Price displayed as EUR 500
- [ ] Duration shown as 60 minutes
- [ ] Session format indicated (Zoom)
- [ ] All included features listed
- [ ] Booking link is present and clickable
- [ ] Link leads to correct payment/booking page
- [ ] Command tracked in analytics

## Audit Service Components

### What's Included

1. **Birth Chart Analysis**
   - Full natal chart review
   - Key planetary aspects
   - Life themes and patterns

2. **Biorhythm Assessment**
   - Current cycle positions
   - Upcoming critical periods
   - Optimization strategies

3. **Dream Pattern Review**
   - Analysis of reported dreams
   - Subconscious signal interpretation
   - Jungian framework application

4. **Environmental Assessment**
   - Location impact analysis
   - Workspace recommendations
   - EMF and sensitivity factors

5. **Action Plan**
   - Personalized coping strategies
   - Performance optimization steps
   - Follow-up recommendations

### Delivery

- Platform: Zoom
- Duration: 60 minutes
- Recording: Optional (client choice)
- Follow-up: Summary document via email

## Configuration

```bash
# In .env
AUDIT_PRICE_EUR=500
AUDIT_PAYMENT_LINK=https://pay.stripe.com/... or https://cal.com/...
```

## Notes

- This is the primary revenue feature (EUR 500/session)
- Target: 1-2 audits per month = EUR 500-1000 MRR
- Analytics should track audit command usage for sales funnel
- Future: Team packages, recurring clients
