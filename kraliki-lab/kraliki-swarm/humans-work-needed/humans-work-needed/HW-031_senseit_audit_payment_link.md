# HW-031: Create Stripe Payment Link for Sense by Kraliki (SenseIt) 1-Hour Audit (€500)

**Created:** 2025-12-22
**Priority:** HIGH
**Blocking:** VD-244, Sense by Kraliki (SenseIt) B2B Revenue
**Time to Fix:** 5-10 min

## Problem

Sense by Kraliki (SenseIt) offers a €500 1-Hour Audit service for B2B customers who prefer card payment over Telegram Stars. Need a Stripe payment link.

## What You Need to Do

### 1. Go to Stripe Dashboard
1. Login to https://dashboard.stripe.com
2. Navigate to **Payment Links** (or **Products**)

### 2. Create the Payment Link
1. Click **+ New Payment Link**
2. Set these details:
   - **Name:** Sense by Kraliki 1-Hour AI Sensitivity Audit
   - **Description:** One-hour deep dive into your organization's AI integration challenges with actionable sensitivity recommendations
   - **Price:** €500 (one-time)
   - **Currency:** EUR

3. Optional settings:
   - Allow promotion codes: Yes
   - Collect: Email, Name
   - After payment: Show confirmation page

4. Click **Create Link**

### 3. Copy the Link
- Format: `https://buy.stripe.com/xxxxx`
- Save this link - it will be added to marketing materials

### 4. Update This Repo
Add the payment link to `QUEUE_STATUS.md` in the "What's Working & Revenue Links" table:
```
| **1-Hour Audit (€500)** | **ACTIVE** | [Payment Link](https://buy.stripe.com/xxxxx) |
```

## Reference

Existing payment links for reference:
- Lab by Kraliki Pro (€299): https://buy.stripe.com/7sY9AUbfx0drdPRcp96J200
- Workshop (€149): https://buy.stripe.com/5kQ00k3N58JX8vx88T6J201
- Workshop (€249): https://buy.stripe.com/14AdRadnF6BP27960L6J202
- Diagnostic (€999): https://buy.stripe.com/6oUaEY83lf8l9zB3SD6J203

## Verification

After creating:
1. Test the link in incognito browser
2. Verify price shows €500
3. Add link to QUEUE_STATUS.md
4. Mark this HW as resolved

---

*This task supports Linear VD-244*
