# E2E Test: 001 - Landing Page Core Elements

## Test Information

| Field | Value |
|-------|-------|
| Priority | HIGH |
| Estimated Duration | 10 minutes |
| Prerequisites | Browser access to Lab by Kraliki landing page |
| URL | https://lab.kraliki.com or http://127.0.0.1:3000 |

## Objective

Verify that the Lab by Kraliki landing page loads correctly and displays all essential elements for converting visitors into demo requests or signups.

## Pre-conditions

1. Landing page is deployed and accessible
2. Browser with JavaScript enabled
3. Stable internet connection (for production testing)

## Test Steps

### Step 1: Page Load

| Action | Navigate to the landing page URL |
|--------|----------------------------------|
| Expected | Page loads within 3 seconds, no console errors |
| Verification | Check browser console for errors |

### Step 2: Hero Section

| Action | Verify hero section content |
|--------|----------------------------|
| Expected | - Headline visible and readable |
| | - Subheadline explains value proposition |
| | - Primary CTA button (e.g., "Start Free Trial" or "Book Demo") |
| | - Secondary CTA button visible |
| Verification | Visual inspection |

### Step 3: Navigation

| Action | Check navigation elements |
|--------|--------------------------|
| Expected | - Logo visible and clickable |
| | - Navigation links: Features, Pricing, About |
| | - Navigation is accessible |
| Verification | Click each nav link, verify scroll or navigation |

### Step 4: Features Section

| Action | Verify features section |
|--------|------------------------|
| Expected | - Section header visible |
| | - 3 feature cards displayed |
| | - Each card has icon, title, and description |
| Verification | Visual inspection |

### Step 5: Social Proof Section

| Action | Check social proof elements |
|--------|----------------------------|
| Expected | - Statistics displayed (e.g., "16x productivity") |
| | - Customer testimonial visible |
| | - Credibility indicators present |
| Verification | Visual inspection |

### Step 6: CTA Section

| Action | Verify call-to-action section |
|--------|------------------------------|
| Expected | - Strong headline |
| | - Clear CTA button |
| | - CTA is above the fold on scroll |
| Verification | Scroll to section, verify CTA visibility |

### Step 7: Footer

| Action | Check footer content |
|--------|---------------------|
| Expected | - Company information |
| | - Resource links (Documentation, API, Community) |
| | - Legal links (Privacy, Terms) |
| | - Contact information |
| Verification | Visual inspection, click links |

### Step 8: SEO Elements

| Action | Verify SEO meta tags |
|--------|---------------------|
| Expected | - Page title contains "Lab by Kraliki" |
| | - Meta description present and meaningful |
| | - Open Graph tags for social sharing |
| Verification | View page source or use SEO extension |

### Step 9: Accessibility

| Action | Basic accessibility check |
|--------|--------------------------|
| Expected | - Only one H1 tag on page |
| | - Proper heading hierarchy (H1 > H2 > H3) |
| | - Alt text on images |
| | - Keyboard navigation works |
| Verification | Tab through page, check heading structure |

## Pass Criteria

- All steps pass without critical issues
- Page loads in under 3 seconds
- No JavaScript errors in console
- All CTAs are clickable and visible

## Common Issues

| Issue | Resolution |
|-------|------------|
| Slow page load | Check image optimization, CDN |
| Broken CTA links | Verify href attributes |
| Missing sections | Check HTML structure |
| Console errors | Debug JavaScript issues |

## Related Tests

- 002-landing-page-pricing.md
- 003-responsive-design.md
