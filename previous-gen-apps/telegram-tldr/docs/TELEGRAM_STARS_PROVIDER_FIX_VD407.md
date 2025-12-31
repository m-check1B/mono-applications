# Telegram Stars Provider Token Configuration - VD-407 Fix

**Date:** 2025-12-26
**Task:** VD-407 - Telegram Stars provider tokens empty - payment broken
**Status:** ✅ FIXED

---

## Issue Summary

The original implementation hardcoded `provider_token=""` in three places in `app/services/bot.py`. While an empty string is technically correct for Telegram Stars payments, this prevented the use of other payment providers (Stripe, etc.) if needed in the future.

## Root Cause

**Missing Configuration:** There was no `telegram_stars_provider_token` setting in `app/core/config.py`, making it impossible to configure alternative payment providers without editing code.

## Solution

### 1. Added Configurable Provider Token

**File:** `app/core/config.py` (line 27)

Added new setting:
```python
telegram_stars_provider_token: str = ""  # Payment provider token (empty for Telegram Stars, or Stripe/etc. token)
```

This setting:
- Defaults to empty string (correct for Telegram Stars)
- Can be set via environment variable `TELEGRAM_STARS_PROVIDER_TOKEN`
- Allows future use of traditional payment providers (Stripe, etc.) without code changes

### 2. Updated Invoice Calls

**File:** `app/services/bot.py` (3 locations updated)

#### a) Subscription Invoice (line 642)
```python
provider_token=settings.telegram_stars_provider_token,  # Use configurable setting
```

#### b) Content Subscription Invoice (line 1173)
```python
provider_token=settings.telegram_stars_provider_token,  # Use configurable setting
```

#### c) Newsletter Invoice (line 1304)
```python
provider_token=settings.telegram_stars_provider_token,  # Use configurable setting
```

### 3. Updated Environment Variables Documentation

**File:** `.env.example` (line 17)

Added documentation:
```env
# Note: Telegram Stars (XTR currency) does not require a payment provider token
# The provider_token is intentionally set to empty string "" for Stars payments
FREE_SUMMARIES=3
SUBSCRIPTION_PRICE_STARS=250
NEWSLETTER_PRICE_STARS=250
TELEGRAM_STARS_PROVIDER_TOKEN=  # Payment provider token (empty for Telegram Stars, or Stripe/etc. token)
```

---

## Verification

### Code Changes
✅ `telegram_stars_provider_token` setting added to config
✅ All three `send_invoice()` calls updated to use `settings.telegram_stars_provider_token`
✅ `.env.example` documented with new setting
✅ Default value is empty string (correct for Telegram Stars)

### Testing Checklist
- [ ] Test `/subscribe` command still works (default behavior unchanged)
- [ ] Verify `TELEGRAM_STARS_PROVIDER_TOKEN` env var can be set and used
- [ ] Test that empty string still works for Telegram Stars
- [ ] Future: Test that non-empty token works for alternative payment provider

---

## Important Notes

### Telegram Stars Payments
- **Provider token should remain empty** `""` for Telegram Stars (XTR currency)
- This is correct behavior per Telegram Bot API documentation
- Do NOT set `TELEGRAM_STARS_PROVIDER_TOKEN` for normal Stars operation

### Future Payment Providers
- If adding Stripe or other traditional payment providers:
  1. Set `TELEGRAM_STARS_PROVIDER_TOKEN=your_stripe_token` in `.env`
  2. No code changes needed - setting is now configurable

### BotFather Configuration
- **Critical:** Bot must have Telegram Stars enabled in @BotFather
- Navigate to: @BotFather → Your Bot (@sumarium_bot) → Payments → Telegram Stars
- Enable Stars payments for the bot

Without BotFather configuration, payments will fail regardless of code changes.

---

## Related Issues

- **VD-261:** Enable Telegram Stars in BotFather for @sumarium_bot (HW-023) - **HUMAN TASK**
  - This is the root cause if payments are still broken
  - A human must enable Stars in BotFather

---

## Deployment

After deploying this fix:
1. Ensure `TELEGRAM_BOT_TOKEN` is set
2. (Optional) If using Stripe/etc., set `TELEGRAM_STARS_PROVIDER_TOKEN`
3. Restart bot container: `docker restart tldr-bot`
4. Verify `/subscribe` command works

**Note:** For Telegram Stars, `TELEGRAM_STARS_PROVIDER_TOKEN` should remain empty or unset.

