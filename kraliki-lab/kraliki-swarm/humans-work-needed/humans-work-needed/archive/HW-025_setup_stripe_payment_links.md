# HW-025: Setup Stripe Payment Links

**Created:** 2025-12-21
**Priority:** HIGH
**Status:** DONE (2025-12-22)
**Blocks:** Magic Box Sales & Consulting Revenue

## Context
While Telegram bots use Stars, "Magic Box" and high-ticket Consulting/Workshops require standard Stripe payment links. The Master Plan identified this as a critical blocker (HW-007 in legacy planning).

## Action Required

1.  **Log in to Stripe Dashboard.**
2.  **Create Payment Links for:**
    *   **Magic Box Subscription:**
        *   Product Name: "Magic Box Pro"
        *   Price: €299/month (or as defined in Pricing Strategy)
        *   Type: Recurring
    *   **Workshop Ticket:**
        *   Product Name: "AI Competence Workshop"
        *   Price: €149 (Early Bird) / €249 (Standard)
        *   Type: One-time
    *   **Consulting Diagnostic:**
        *   Product Name: "AI Readiness Diagnostic"
        *   Price: [Custom or Fixed, e.g., €999]
        *   Type: One-time

3.  **Copy the Links.**
4.  **Save the Links:**
    *   Update `content/operations/pricing_config.md` (or similar) with the URLs.
    *   Or provide them in `QUEUE_STATUS.md` comments for the dev team to integrate into the landing pages.

## Verification
*   Open each link in an Incognito window to ensure it loads the checkout page correctly.

## Notes
*   Ensure tax settings (VAT) are correctly configured in Stripe for EU customers.
