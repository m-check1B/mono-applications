# HW-007: Create Stripe Payment Link for TL;DR Bot Pro

**Status:** PENDING
**Priority:** HIGH
**Blocks:** W2-006 (Connect Stripe to landing)
**Estimated Time:** 10 minutes
**Created:** 2025-12-12

---

## What Needs to Be Done

Create a Stripe Payment Link for the TL;DR Bot Pro subscription ($5/month).

---

## Step-by-Step Instructions

### 1. Log into Stripe Dashboard
- Go to: https://dashboard.stripe.com
- Use your Stripe account (or create one if needed)

### 2. Create a Product
- Go to: **Products** > **Add product**
- Product name: `TL;DR Bot Pro`
- Description: `Unlimited Telegram chat summaries, extended lookback, priority processing`
- Price: `$5.00 USD` / month (recurring)
- Click **Save product**

### 3. Create a Payment Link
- Go to: **Payment Links** > **New**
- Select the product you just created
- Settings:
  - Allow customers to adjust quantity: **No**
  - Collect customer email: **Yes**
  - After payment: Redirect to `https://t.me/sumarium_bot?start=paid`
- Click **Create link**

### 4. Copy the Payment Link URL
It will look like: `https://buy.stripe.com/xxx`

### 5. Update the Landing Page
Edit `/github/websites/tldr/index.html`:
- Find line ~442: `const STRIPE_PAYMENT_LINK = window.STRIPE_PAYMENT_LINK || 'STRIPE_PAYMENT_LINK_PLACEHOLDER';`
- Replace `STRIPE_PAYMENT_LINK_PLACEHOLDER` with your actual payment link

The landing page currently reads the link from this constant, so updating the HTML is the expected path.

---

## Test Mode First

You can do all this in **Stripe Test Mode** first:
1. Toggle to "Test mode" in Stripe dashboard (top right)
2. Create test product and payment link
3. Test with card number: `4242 4242 4242 4242`
4. Verify the redirect works

---

## Verification Criteria

- [ ] Product exists in Stripe dashboard
- [ ] Payment Link URL is active
- [ ] Test payment completes successfully
- [ ] Landing page button opens Stripe checkout
- [ ] After payment, user is redirected to Telegram bot

---

## When Complete

1. Change **Status** above to: **DONE**
2. Save this file

---

## Notes

- The landing page is already updated with the Stripe button
- Current behavior: Shows "Payment coming soon" alert until real link is added
- Both card and Telegram Stars payment options are displayed
