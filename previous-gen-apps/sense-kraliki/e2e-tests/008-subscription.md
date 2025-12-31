# Test 008: Subscription and Payments

**Feature:** /subscribe, /status commands - Telegram Stars payments
**Priority:** P0 (Critical)
**Type:** Telegram Bot
**Estimated Time:** 5 minutes

## Objective

Verify the subscription system works correctly including plan display, payment processing, and premium status management.

## Preconditions

- Bot is running
- Telegram Stars payments configured
- Test account with Telegram Stars (for payment testing)

## Test Steps

### Test 8.1: View Subscription Options

1. Send `/subscribe`
2. **Expected:** Two plan options displayed:

```
Sense by Kraliki Premium Plans

1. Sensitive Plan - 150 Stars (~$3/mo)
- Unlimited dream analyses
- Full sensitivity breakdowns
- 6-month forecasts
- Basic remedies

2. Empath Plan - 350 Stars (~$7/mo)
- Everything in Sensitive
- Full 12-month forecasts
- Advanced pattern tracking
- Personalized remedy plans
- Priority support

To subscribe:
/subscribe sensitive or /subscribe 1
/subscribe empath or /subscribe 2
```

### Test 8.2: Select Sensitive Plan

1. Send `/subscribe sensitive` or `/subscribe 1`
2. **Expected:** Telegram Stars payment invoice appears
3. Invoice shows:
   - Title: "Sense by Kraliki Sensitive Plan"
   - Price: 150 Stars
   - Description includes features

### Test 8.3: Select Empath Plan

1. Send `/subscribe empath` or `/subscribe 2`
2. **Expected:** Telegram Stars payment invoice appears
3. Invoice shows:
   - Title: "Sense by Kraliki Empath Plan"
   - Price: 350 Stars

### Test 8.4: Free User Status

1. As free user, send `/status`
2. **Expected:** Free tier status:
   - "Subscription Status: Free"
   - Shows free tier limits (3 dreams/month)
   - Suggests upgrade

### Test 8.5: Payment Flow (if testable)

1. Complete payment for Sensitive plan
2. **Expected:** Confirmation message:
   - "Thank you for your support!"
   - "Your Sensitive plan is now active for 1 month"
   - Suggests /sense, /dream, /forecast

### Test 8.6: Premium User Status

1. As premium user, send `/status`
2. **Expected:** Premium status:
   - "Subscription Status: Sensitive/Empath Plan"
   - Expiration date
   - Days remaining
   - List of benefits

### Test 8.7: Already Premium

1. As premium user, send `/subscribe`
2. **Expected:** Message indicating already premium:
   - "You're already on the Premium plan!"
   - Shows expiration date
   - Suggests /status for benefits

### Test 8.8: Pre-Checkout Validation

During payment:
1. Payment payload validated
2. **Expected:** Correct user ID in payload
3. **Expected:** Correct amount for plan

### Test 8.9: Payment Mismatch

If payment amount differs from expected:
1. **Expected:** Pre-checkout rejected
2. Error message shown

### Test 8.10: Premium Benefits Work

After subscribing:
1. `/dream` - Unlimited analyses (no limit message)
2. `/forecast` - Full 12-month forecast (Empath)
3. `/sense` - Full breakdowns
4. `/remedies` - Personalized plans (Empath)

## Success Criteria

- [ ] /subscribe shows both plans with prices
- [ ] /subscribe sensitive sends invoice for 150 Stars
- [ ] /subscribe empath sends invoice for 350 Stars
- [ ] /status shows free tier for free users
- [ ] /status shows premium details for subscribers
- [ ] Payment triggers confirmation message
- [ ] Premium status persists after payment
- [ ] Premium benefits are unlocked
- [ ] Already premium users cannot double-subscribe

## Pricing Configuration

| Plan | Price (Stars) | Price (USD) | Duration |
|------|---------------|-------------|----------|
| Sensitive | 150 | ~$3 | 1 month |
| Empath | 350 | ~$7 | 1 month |

## Premium Features

| Feature | Free | Sensitive | Empath |
|---------|------|-----------|--------|
| Sensitivity score | Basic | Full | Full |
| Dream analyses | 3/month | Unlimited | Unlimited |
| Forecast | 3 months | 6 months | 12 months |
| Remedies | Basic | Basic | Personalized |
| Pattern tracking | No | No | Yes |
| Priority support | No | No | Yes |

## Payment Payload Format

```
{plan}:{user_id}
```

Example: `sensitive:12345` or `empath:67890`

## Notes

- Telegram Stars (XTR) is the payment currency
- Payment goes to bot owner's Telegram account
- Subscription is for 1 month from payment date
- User data stored in Redis with premium_until timestamp
- Analytics track subscriptions for business metrics
