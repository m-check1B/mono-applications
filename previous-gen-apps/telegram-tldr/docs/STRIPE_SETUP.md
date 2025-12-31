# Stripe Setup for TL;DR Bot Premium Tier

This guide configures card payments (Stripe) for the TL;DR Bot premium tier.

## Prerequisites

- Stripe account (test mode is fine for validation)
- Public HTTPS base URL for the bot (same as `TELEGRAM_WEBHOOK_URL` or a dedicated domain)

## 1. Create Products and Prices

Create products and recurring prices in Stripe:

- Pro Monthly: EUR 4.99 / month
- Pro Yearly: EUR 47.99 / year
- Content Pro Monthly: EUR 7.99 / month
- Content Pro Yearly: EUR 79.99 / year

Copy the price IDs and set them in `.env`:

```
STRIPE_PRICE_PRO_MONTHLY=price_...
STRIPE_PRICE_PRO_YEARLY=price_...
STRIPE_PRICE_CONTENT_MONTHLY=price_...
STRIPE_PRICE_CONTENT_YEARLY=price_...
```

## 2. Configure Webhook Endpoint

Set the webhook endpoint to:

```
https://<public-base-url>/stripe/webhook
```

Required events:

- `checkout.session.completed`
- `customer.subscription.created`
- `customer.subscription.updated`
- `customer.subscription.deleted`
- `invoice.payment_succeeded`
- `invoice.payment_failed`

Copy the webhook signing secret and set it in `.env`:

```
STRIPE_WEBHOOK_SECRET=whsec_...
```

## 3. Set Base URL for Stripe Callbacks

Use one of the following (Stripe will redirect users after checkout):

- Preferred: `STRIPE_WEBHOOK_URL=https://bot.example.com`
- Fallback: `TELEGRAM_WEBHOOK_URL=https://bot.example.com`

The app will use `STRIPE_WEBHOOK_URL` if set, otherwise it falls back to `TELEGRAM_WEBHOOK_URL`.

## 4. Enable Stripe API Key

```
STRIPE_API_KEY=sk_test_...
```

## 5. Validate

- Start the bot with `docker compose up -d`
- Run `/subscribe_stripe` in Telegram
- Complete a test checkout
- Confirm Stripe sends webhook events and subscription status updates

## Troubleshooting

- Missing base URL: set `STRIPE_WEBHOOK_URL` or `TELEGRAM_WEBHOOK_URL`
- Invalid signature: verify `STRIPE_WEBHOOK_SECRET`
- Stripe checkout not working: confirm price IDs exist and are active
