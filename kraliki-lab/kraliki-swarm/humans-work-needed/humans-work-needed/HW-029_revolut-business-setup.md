# HW-029: Set Up Revolut Business Account (Czech s.r.o.)

**Created:** 2025-12-22
**Priority:** HIGH
**Blocking:** Financial security isolation, API payment safety
**Estimated Time:** 1-2 hours (plus verification wait)

## Why This Matters

Currently, API keys for payment services (Stripe, Hetzner, OpenAI, etc.) are connected to main bank account. If any API key leaks or gets misconfigured, attackers could drain the entire account.

Revolut Business provides:
- **Virtual cards with per-card limits** — damage capped even if compromised
- **Instant freeze** — lock cards immediately via app
- **Transaction alerts** — real-time notifications
- **Isolated wallet** — main bank never exposed

## Required Documents (Czech s.r.o.)

- [ ] Company registration extract (Výpis z obchodního rejstříku)
- [ ] Articles of association (Zakladatelská listina / Společenská smlouva)
- [ ] Proof of director's identity (passport/ID)
- [ ] Proof of director's address
- [ ] Company tax ID (IČO, DIČ)

## Steps

1. Go to https://www.revolut.com/business/
2. Select "Open account" → Czech Republic → Limited company
3. Upload company documents
4. Complete identity verification (video call or app verification)
5. Wait for approval (usually 1-3 business days)

## After Approval — Virtual Card Setup

Create these virtual cards with limits:

| Card Name | Monthly Limit | Purpose |
|-----------|---------------|---------|
| `hetzner-servers` | €200 | Server hosting costs |
| `api-services` | €100 | OpenAI, Anthropic, etc. |
| `ads-marketing` | €500 | Google Ads, Meta Ads |
| `stripe-reserve` | €50 | Stripe fees buffer |

## After Cards Created

1. Update Hetzner payment method to `hetzner-servers` card
2. Update API service payments to `api-services` card
3. Connect Stripe payouts to Revolut IBAN (revenue in)
4. Set up weekly auto-sweep to main bank (keep exposure low)
5. Store card details in `/github/secrets/revolut/` (gitignored)

## Completion Criteria

- [ ] Revolut Business account active
- [ ] 4 virtual cards created with limits
- [ ] Hetzner billing switched to Revolut card
- [ ] Stripe payouts connected to Revolut
- [ ] Card details stored in secrets

---

*This is a human-only task requiring identity verification and legal documents.*
