# E2E Test: 003 - Responsive Design

## Test Information

| Field | Value |
|-------|-------|
| Priority | MEDIUM |
| Estimated Duration | 15 minutes |
| Prerequisites | Access to landing page, browser dev tools |
| URL | https://lab.kraliki.com or http://127.0.0.1:3000 |

## Objective

Verify that the Lab by Kraliki landing page displays correctly and remains functional across different screen sizes and devices.

## Pre-conditions

1. Browser with responsive design mode (DevTools)
2. Or access to actual mobile/tablet devices

## Viewport Sizes to Test

| Device Type | Width | Height |
|-------------|-------|--------|
| Mobile (iPhone SE) | 375px | 667px |
| Mobile (iPhone 12) | 390px | 844px |
| Tablet (iPad) | 768px | 1024px |
| Laptop | 1366px | 768px |
| Desktop | 1920px | 1080px |

## Test Steps

### Step 1: Mobile Viewport (375px)

| Action | Set viewport to 375x667, load page |
|--------|-----------------------------------|
| Expected | - Mobile-optimized layout |
| | - Navigation collapses to hamburger menu |
| | - Hero text readable without horizontal scroll |
| | - CTAs are tap-friendly (min 44px touch target) |
| | - Images scale properly |
| Verification | Visual inspection, no horizontal scroll |

### Step 2: Mobile Navigation

| Action | Test mobile navigation menu |
|--------|----------------------------|
| Expected | - Hamburger icon visible |
| | - Menu opens on tap |
| | - Links are accessible |
| | - Menu closes after selection |
| Verification | Tap hamburger, navigate |

### Step 3: Mobile Hero Section

| Action | Check hero on mobile |
|--------|---------------------|
| Expected | - Headline fully visible |
| | - CTAs stack vertically if needed |
| | - No text overflow or truncation |
| Verification | Visual inspection |

### Step 4: Mobile Features Section

| Action | Check features on mobile |
|--------|-------------------------|
| Expected | - Feature cards stack vertically |
| | - Full content visible |
| | - Icons/images scale |
| Verification | Scroll through features |

### Step 5: Mobile Pricing Section

| Action | Check pricing on mobile |
|--------|------------------------|
| Expected | - Pricing cards stack vertically |
| | - All tiers visible on scroll |
| | - Prices readable |
| | - CTAs full-width and tappable |
| Verification | Scroll through pricing |

### Step 6: Mobile Footer

| Action | Check footer on mobile |
|--------|----------------------|
| Expected | - Links accessible |
| | - Copyright visible |
| | - No overlapping elements |
| Verification | Scroll to footer |

### Step 7: Tablet Viewport (768px)

| Action | Set viewport to 768x1024, reload |
|--------|----------------------------------|
| Expected | - Two-column layouts where appropriate |
| | - Navigation may be visible or hamburger |
| | - Adequate spacing between elements |
| Verification | Visual inspection |

### Step 8: Desktop Viewport (1920px)

| Action | Set viewport to 1920x1080, reload |
|--------|-----------------------------------|
| Expected | - Full desktop layout |
| | - Navigation fully visible |
| | - Content centered, not stretched |
| | - Max-width constraints applied |
| Verification | Visual inspection |

### Step 9: Orientation Change (Mobile)

| Action | Rotate from portrait to landscape |
|--------|-----------------------------------|
| Expected | - Layout adapts smoothly |
| | - No content hidden |
| | - Scroll works correctly |
| Verification | Rotate device/viewport |

### Step 10: Touch Targets

| Action | Verify all interactive elements |
|--------|--------------------------------|
| Expected | - Buttons minimum 44x44px |
| | - Links have adequate spacing |
| | - No accidental tap issues |
| Verification | Tap each interactive element |

## Pass Criteria

- No horizontal scrollbar on any viewport
- All content readable without zoom
- Navigation functional on all sizes
- CTAs accessible and tappable
- Images scale without distortion

## Common Issues

| Issue | Resolution |
|-------|------------|
| Horizontal scroll on mobile | Check fixed-width elements |
| Text too small | Use responsive font sizes |
| Overlapping elements | Check z-index and positioning |
| Hamburger menu not working | Check JavaScript event handlers |

## Browser Testing

Also test on:
- [ ] Chrome
- [ ] Safari
- [ ] Firefox
- [ ] Edge (if applicable)

## Related Tests

- 001-landing-page-core.md
- 002-landing-page-pricing.md
