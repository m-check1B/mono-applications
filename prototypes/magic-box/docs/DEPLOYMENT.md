# Magic Box Landing Page - Deployment Guide

## Overview

Production-ready landing page for Magic Box with Stripe checkout integration and contact form.

## Features

- ✅ Hero section with 16× productivity value proposition
- ✅ Pricing tiers display (Starter €299/mo, Pro €499/mo, Enterprise €10K/yr)
- ✅ Feature comparison table (Traditional vs Magic Box)
- ✅ Proof section with December 2, 2025 production run results
- ✅ Stripe checkout integration (Payment Links)
- ✅ FAQ section
- ✅ Contact/Support form (FormSubmit.io)
- ✅ Mobile responsive design
- ✅ Dark terminal theme with brutalist styling

## Files

- `docs/landing-page.html` - Main landing page (production-ready)
- `docs/landing-page-copy.md` - Copy content (English + Czech versions)
- `DEPLOYMENT.md` - This deployment guide

## Quick Deploy

### Option 1: Static Hosting (Netlify, Vercel, GitHub Pages)

1. **Create repository for landing page** (optional)
   ```bash
   git init
   git add docs/landing-page.html
   git commit -m "Add Magic Box landing page"
   ```

2. **Deploy to Netlify**
   - Go to [netlify.com](https://netlify.com)
   - Drag and drop the `docs` folder
   - Rename to `magic-box` or your preferred domain

3. **Deploy to Vercel**
   ```bash
   npm install -g vercel
   cd docs
   vercel deploy
   ```

4. **Deploy to GitHub Pages**
   - Push to GitHub repository
   - Settings → Pages → Source: `docs` folder
   - URL: `https://yourusername.github.io/magic-box/`

### Option 2: Serve Locally

```bash
cd applications/magic-box/docs
python3 -m http.server 8000
# Visit http://localhost:8000/landing-page.html
```

### Option 3: Deploy to Existing Domain

If deploying to `verduona.com/magic-box`:

1. Copy `landing-page.html` to your web server:
   ```bash
   scp docs/landing-page.html user@server:/var/www/verduona.com/public/magic-box/index.html
   ```

2. Configure nginx (if needed):
   ```nginx
   location /magic-box {
       alias /var/www/verduona.com/public/magic-box;
       index index.html;
   }
   ```

## Stripe Integration Setup

The landing page uses Stripe Payment Links for checkout (no backend required).

### Step 1: Create Stripe Products & Prices

1. Log in to [Stripe Dashboard](https://dashboard.stripe.com)
2. Go to **Products** → **Add product**
3. Create 3 products:

   **Product 1: Magic Box Starter**
   - Name: `Magic Box Starter`
   - Description: `Pre-configured Hetzner VM with full AI orchestration stack`
   - Price: `€299` EUR/month
   - Set up recurring subscription

   **Product 2: Magic Box Pro**
   - Name: `Magic Box Pro`
   - Description: `Custom setup, priority support, pattern library`
   - Price: `€499` EUR/month
   - Set up recurring subscription

   **Product 3: Magic Box Enterprise**
   - Name: `Magic Box Enterprise`
   - Description: `Full customization, dedicated support, SLA`
   - Price: `€10,000` EUR/year
   - Set up recurring subscription

### Step 2: Create Payment Links

For each product, create a Payment Link:

1. Go to **Products** → Select product → **Create payment link**
2. Copy the generated URL (e.g., `https://buy.stripe.com/xyz123`)

### Step 3: Update Landing Page

#### Option A: Automated (Recommended)

Use the configuration script:

```bash
# Add Stripe links to .env
echo "STRIPE_PAYMENT_LINK_STARTER=https://buy.stripe.com/..." >> .env
echo "STRIPE_PAYMENT_LINK_PRO=https://buy.stripe.com/..." >> .env

# Run configuration script
./scripts/configure_stripe_links.sh
```

The script will:
- Backup current landing page
- Replace all placeholder Stripe URLs with real links
- Show summary of configured links

#### Option B: Manual Update

Replace placeholder Stripe URLs in `landing-page.html`:

```html
<!-- Line 782 - Header Subscribe button -->
<a href="https://buy.stripe.com/YOUR_STARTER_URL" class="brutal-btn brutal-btn-primary">Subscribe</a>

<!-- Line 792 - Hero Pro CTA -->
<a href="https://buy.stripe.com/YOUR_PRO_URL" class="brutal-btn brutal-btn-primary pulse-glow">Subscribe via Stripe</a>

<!-- Line 993 - Starter pricing -->
<a href="https://buy.stripe.com/YOUR_STARTER_URL" class="brutal-btn">Subscribe via Stripe</a>

<!-- Line 1012 - Pro pricing -->
<a href="https://buy.stripe.com/YOUR_PRO_URL" class="brutal-btn brutal-btn-primary pulse-glow">Subscribe via Stripe</a>

<!-- Line 1194 - CTA section -->
<a href="https://buy.stripe.com/YOUR_PRO_URL" class="brutal-btn brutal-btn-primary pulse-glow">Subscribe via Stripe</a>
```

### Step 4: Configure Success/Cancel Pages

In Stripe Payment Link settings:
- **After payment**: Redirect to `https://yourdomain.com/magic-box/thank-you`
- **After cancel**: Redirect to `https://yourdomain.com/magic-box`

## Contact Form Setup

The contact form uses [FormSubmit.io](https://formsubmit.io) - no backend required.

### Current Configuration

```html
<form action="https://formsubmit.co/hello@verduona.com" method="POST">
  <input type="hidden" name="_subject" value="Magic Box Inquiry from Landing Page">
  <input type="hidden" name="_captcha" value="false">
  <input type="hidden" name="_next" value="https://verduona.com/magic-box/thank-you">
```

### Customize for Your Domain

Update the `_next` parameter in the form (line 1017):

```html
<input type="hidden" name="_next" value="https://YOUR-DOMAIN.com/magic-box/thank-you">
```

### FormSubmit Verification

First email from FormSubmit will require you to verify your email address:
1. Submit the form once
2. Check your inbox (hello@verduona.com)
3. Click verification link
4. Form will start working

## Customization

### Update Company Details

Find and replace in `landing-page.html`:

```html
<!-- Email addresses -->
hello@verduona.com → your-contact@yourcompany.com
support@verduona.com → your-support@yourcompany.com
sales@verduona.com → your-sales@yourcompany.com

<!-- Company name -->
Verduona → Your Company Name

<!-- Domain -->
verduona.com → yourdomain.com
```

### Update Pricing

Modify pricing section (lines 861-917):

```html
<div class="pricing-price">
    <span class="setup">€299</span><br>
    <span class="monthly">/month</span>
</div>
```

### Update Colors

Edit CSS variables (lines 13-21):

```css
:root {
    --color-void: #050505;
    --color-concrete: #F0F0F0;
    --color-terminal-green: #33FF00;
    --color-system-red: #FF3333;
    --color-cyan-data: #00FFFF;
}
```

## Testing

### Test Stripe Integration

1. **Test Mode**: Use Stripe test mode first
   - Dashboard → Settings → Payment links → Test mode
   - Use test card: `4242 4242 4242 4242`

2. **Test Flow**:
   - Click "Subscribe via Stripe" button
   - Complete checkout in test mode
   - Verify redirection to success page

### Test Contact Form

1. Submit test form
2. Verify email arrives at `hello@verduona.com`
3. Check FormSubmit confirmation

### Test Mobile Responsiveness

1. Open Chrome DevTools (F12)
2. Toggle device toolbar (Ctrl+Shift+M)
3. Test at: 320px, 375px, 768px, 1024px

## SEO Optimization

### Meta Tags (Already Included)

```html
<meta name="description" content="Magic Box - Pre-configured multi-AI orchestration stack. 16× productivity. €299-499/month. Instant Stripe checkout.">
<meta name="keywords" content="AI orchestration, multi-AI, productivity, automation, Claude, Gemini, AI consultancy">
```

### Additional SEO

1. **Sitemap**: Add to `sitemap.xml`
   ```xml
   <url>
       <loc>https://yourdomain.com/magic-box/</loc>
       <lastmod>2025-12-26</lastmod>
       <changefreq>weekly</changefreq>
       <priority>0.9</priority>
   </url>
   ```

2. **Google Analytics**: Add tracking script before `</head>`:
   ```html
   <script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
   <script>
     window.dataLayer = window.dataLayer || [];
     function gtag(){dataLayer.push(arguments);}
     gtag('js', new Date());
     gtag('config', 'G-XXXXXXXXXX');
   </script>
   ```

## Analytics

### Recommended Tools

1. **Google Analytics 4** - Traffic, conversions
2. **Stripe Analytics** - Revenue, subscription metrics
3. **Hotjar** - User behavior, heatmaps (optional)

### Track Conversions

Add event tracking to Stripe buttons:

```html
<a href="https://buy.stripe.com/YOUR_URL"
   onclick="gtag('event', 'conversion', {'send_to': 'AW-CONVERSION_ID'});"
   class="brutal-btn brutal-btn-primary">Subscribe</a>
```

## Maintenance

### Update Content

- **Pricing**: Update if rates change
- **FAQ**: Add new common questions
- **Proof**: Add new success stories

### Monitor

- **Stripe**: Check subscriptions, churn, revenue
- **FormSubmit**: Verify form submissions working
- **Analytics**: Traffic sources, conversion rates

## Troubleshooting

### Form Not Submitting

- Verify FormSubmit email verified
- Check spam folder for verification email
- Ensure correct `_next` redirect URL

### Stripe Not Redirecting

- Check Stripe Payment Link settings
- Verify success/cancel URLs configured
- Ensure domain added to Stripe settings

### Mobile Layout Issues

- Check viewport meta tag (included in template)
- Test on actual devices, not just DevTools
- Verify CSS media queries loaded

## Support

For issues with:
- **FormSubmit**: https://formsubmit.io/support
- **Stripe**: https://support.stripe.com
- **Deployment**: Check hosting provider docs

---

**Status**: Production Ready ✅

**Last Updated**: 2025-12-26

**Next Steps**:
1. Deploy to your domain
2. Create Stripe Payment Links
3. Test checkout flow
4. Launch and monitor
