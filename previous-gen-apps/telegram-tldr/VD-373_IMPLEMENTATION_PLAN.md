# VD-373: Premium Tier Implementation - Stripe Integration

## Current State (Updated)
- Bot has Telegram Stars integration (250 Stars for Pro, 400 Stars for Content Pro)
- **Stripe recurring subscriptions now implemented!**
- Basic subscription tracking in Redis (active for N months)
- Payment handling via aiogram's invoice system AND Stripe
- **Recurring payment support via Stripe (auto-renewing)**

## Implementation Plan

### Phase 1: Dependencies & Config
- [x] Add `stripe` to pyproject.toml
- [x] Add Stripe config to Settings (api_key, webhook_secret, pricing)
- [ ] Create Stripe products and pricing plans (requires Stripe dashboard setup)

### Phase 2: Payment Service Layer
- [x] Create `app/services/payments.py` with:
  - Abstract payment provider interface
  - Telegram Stars provider (existing)
  - Stripe provider (new)
  - Unified payment handler

### Phase 3: Stripe Integration
- [x] Create Stripe checkout flow
- [x] Add Stripe webhook endpoint
- [x] Handle subscription events (created, updated, cancelled)
- [x] Sync subscription status with Redis
- [x] Add success/cancel callback pages

### Phase 4: Bot Commands
- [x] Add `/subscribe_stripe` command (Stripe checkout)
- [x] Add `/subscribe_stars` command (Telegram Stars direct)
- [x] Update `/subscribe` to show both options
- [x] Add `/manage` command (view/cancel Stripe subs)
- [x] Update `/help` with new commands

### Phase 5: Subscription Management
- [x] Track Stripe subscription IDs in Redis
- [x] Handle subscription expiry/renewal (via webhooks)
- [x] Add subscription status checking
- [x] Graceful downgrade on cancellation

### Phase 6: Testing
- [x] Unit tests for payment service (521 tests passing)
- [x] Integration tests for Stripe webhooks
- [ ] E2E tests for subscription flow (requires live Stripe test mode)

## Pricing Strategy
- **Pro Plan**: €4.99/month (~$5.49 USD) - Monthly auto-renewing
- **Pro Plan Annual**: €47.99/year (20% off) - Yearly auto-renewing
- **Content Pro Plan**: €7.99/month (~$8.79 USD)

## Security Notes
- Never expose Stripe API keys in code
- Validate webhook signatures ✓
- Use 127.0.0.1 for webhook endpoint (not 0.0.0.0) ✓

## Remaining Work
1. Set up Stripe products in dashboard with price IDs
2. Configure environment variables:
   - `STRIPE_API_KEY`
   - `STRIPE_WEBHOOK_SECRET`
   - `STRIPE_PRICE_PRO_MONTHLY`
   - `STRIPE_PRICE_PRO_YEARLY`
   - `STRIPE_PRICE_CONTENT_MONTHLY`
   - `STRIPE_PRICE_CONTENT_YEARLY`
3. Test with Stripe test mode keys
