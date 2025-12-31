# HW-XXX Setup Stripe Payment Links for AI Academy

## Context

Payment links are needed for Q1 2026 Revenue Plan per `marketing-2026/campaigns/STRIPE-LINKS-NEEDED.md`

## Payment Links Required

### 1. Reality Check: 1-Hour AI Workflow Audit
- **Price:** €500.00
- **Type:** One-time
- **Product Name:** Strategic AI Reality Check (1-Hour Audit)
- **Description:** A 1-hour deep-dive into your business workflows. Includes a recorded Loom walkthrough of recommended orchestrated AI solutions.
- **Success Page:** "Thank you for booking your Reality Check. You will receive an email within 2 hours with a link to book your session on my calendar."
- **Current Placeholder:** `https://buy.stripe.com/placeholder_reality_check`
- **Action Needed:** Create real Stripe payment link and update placeholder in STRIPE-LINKS-NEEDED.md

### 2. AI Academy: Level 1 (Student) - Early Bird
- **Price:** €49.00
- **Type:** One-time
- **Product Name:** AI Automation Academy: Level 1 (Student)
- **Description:** Early access to Level 1 course. Launch date: Jan 1, 2026.
- **Current Placeholder:** `https://buy.stripe.com/placeholder_academy_l1_early`
- **Action Needed:** Create real Stripe payment link and update placeholder in STRIPE-LINKS-NEEDED.md

## Steps to Complete

1. **Log into Stripe Dashboard**
   - Navigate to https://dashboard.stripe.com
   - Ensure test/live mode matches environment

2. **Create Payment Links**

   ### Reality Check Payment Link
   - Product Name: "Strategic AI Reality Check (1-Hour Audit)"
   - Price: €500.00 EUR
   - Type: One-time payment
   - Success URL: `https://verduona.com/reality-check-success` (or create custom success page)
   - Cancel URL: `https://verduona.com/` (homepage)
   - Shipping address: Not applicable (service)
   - Billing details: Collect name, email for follow-up

   ### Academy Level 1 Payment Link
   - Product Name: "AI Automation Academy: Level 1 (Student)"
   - Price: €49.00 EUR
   - Type: One-time payment
   - Success URL: `https://verduona.com/academy-success` (or create custom success page)
   - Cancel URL: `https://verduona.com/academy` (course page)
   - Shipping address: Not applicable (digital product)
   - Allow promo codes: No (early bird fixed price)

3. **Update STRIPE-LINKS-NEEDED.md**
   Replace placeholder URLs with actual Stripe payment links
   Change status from 🔴 PENDING to ✅ COMPLETE for each link

4. **Update Features**
   - Mark LIN-VD-313 as `blocked_by: "HW-XXX"`
   - Add note that human work is in progress

## Additional Notes

- Test payment links in test mode before going live
- Ensure webhooks are configured for Stripe events (payment.success, payment.failed, etc.)
- Update pricing on website to reflect payment link availability
- Consider creating Stripe checkout session instead of payment link for better UX (optional future improvement)

## Blocker

This task requires access to:
- Stripe Dashboard (production keys)
- Ability to create products/prices in Stripe
- Business owner approval for pricing and payment flow
