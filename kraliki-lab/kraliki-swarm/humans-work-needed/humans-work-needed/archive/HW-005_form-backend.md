# HW-005: Configure Form Backend for Contact Forms

**Created:** 2025-12-09
**Priority:** Medium
**Status:** Pending
**Blocks:** Contact form submissions on landing pages

## Context

Contact forms have been added to landing pages (main, business, consulting, family). They currently use a placeholder Formspree endpoint that needs to be replaced with a working backend.

## Options

### Option A: Formspree (Recommended for simplicity)
1. Sign up at https://formspree.io/
2. Create a form for each site or one unified form
3. Get the form endpoint (e.g., `https://formspree.io/f/xyzabc123`)
4. Replace placeholder in HTML files

**Pros:** No server maintenance, instant setup, free tier available (50 submissions/month)
**Cons:** Limited customization, requires paid plan for more volume

### Option B: EspoCRM Web-to-Lead
1. Configure EspoCRM to accept lead submissions (see HW-004)
2. Set up CORS for form origins
3. Point forms to EspoCRM endpoint

**Pros:** Leads go directly to CRM, no third party
**Cons:** Requires EspoCRM setup (HW-004)

### Option C: Custom API Endpoint
1. Create a simple endpoint in existing backend
2. Store submissions in database
3. Send email notifications

**Pros:** Full control
**Cons:** Requires development and maintenance

## Files to Update

After choosing a backend, update the form action in:

- `/github/websites/main/index.html` - Contact section (line ~246)
- `/github/websites/business/index.html` - Footer contact (if form added)
- `/github/websites/consulting/index.html` - Booking section
- `/github/websites/family/index.html` - Registration section

## Example Update (Formspree)

```html
<!-- Before -->
<form action="https://formspree.io/f/placeholder" method="POST">

<!-- After -->
<form action="https://formspree.io/f/your-actual-id" method="POST">
```

## Verification

1. Submit a test form
2. Verify you receive the submission in chosen backend
3. Check email notifications work
4. Test from different pages

## Notes

- Main landing page has a full contact form with name, email, message
- Other pages have Cal.com placeholders for booking (separate issue - HW-002)
- Consider honeypot fields for spam protection
