# VD-528: Enable Stripe Payments for Lab by Kraliki

## Status: Integration Infrastructure READY (Human Action Required)

## What Was Completed

### 1. Added Placeholder Stripe Links to Landing Pages
Updated the following files with Stripe placeholder links:
- `/home/adminmatej/github/infra/compose/lab/index.html`
- `/home/adminmatej/github/applications/lab-kraliki/docs/landing-page.html`

**Links Added:**
- `placeholder_lab_by_kraliki_starter` (€299/month subscription)
- `placeholder_lab_by_kraliki_pro` (€499/month subscription)

**Total occurrences:** 10 placeholder links across both files

### 2. Verified Configuration Script
- Script: `/home/adminmatej/github/scripts/configure_stripe_links.py`
- Tested and verified to work correctly
- Automatically replaces placeholders when actual Stripe links provided in `.env`

### 3. Integration Flow
```
1. Human creates Stripe products in Stripe Dashboard
2. Human adds links to .env:
   STRIPE_LINK_LAB_STARTER=https://buy.stripe.com/...
   STRIPE_LINK_LAB_PRO=https://buy.stripe.com/...
3. Run: python3 scripts/configure_stripe_links.py
4. Script replaces placeholders across all files
5. Deploy to production
```

## Pricing Tiers (from VD-315)

### Starter (€299/month)
- Pre-configured Hetzner VM
- CLIProxyAPI (unified gateway)
- Claude Code + Gemini + Codex
- mgrep semantic search
- Prompt library access
- Basic documentation
- Community support

### Pro (€499/month)
- Everything in Starter
- Custom domain configuration
- Pattern library (proven workflows)
- Priority email support
- Monthly pattern updates
- Onboarding documentation
- Upgrade path to Enterprise

## Blocker (Human Task)

**Time Required:** ~5 minutes

**Action Required:**
1. Log in to [Stripe Dashboard](https://dashboard.stripe.com)
2. Create two subscription products:
   - Lab by Kraliki Starter (€299/month)
   - Lab by Kraliki Pro (€499/month)
3. Generate payment links for each
4. Add to `/home/adminmatej/github/.env`:
   ```
   STRIPE_LINK_LAB_STARTER=https://buy.stripe.com/[link]
   STRIPE_LINK_LAB_PRO=https://buy.stripe.com/[link]
   ```
5. Run: `python3 scripts/configure_stripe_links.py`

## Related Tasks
- VD-523: Configure Stripe Payment Links (In Review - created config script)
- VD-529: Enable Stripe Payments for Reality Check Audit (Backlog)
- VD-530: Enable Stripe Payments for Academy L1 (In Progress)

## Documentation
- Product pricing: `marketing-2026/content/sites/VD-315_lab-kraliki-billing-pricing.md`
- Stripe needs: `marketing-2026/campaigns/STRIPE-LINKS-NEEDED.md`

---
**Completed by:** darwin-opencode-integrator
**Date:** 2025-12-29
**Points Earned:** 150
