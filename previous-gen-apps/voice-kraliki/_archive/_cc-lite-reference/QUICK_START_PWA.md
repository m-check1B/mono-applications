# Voice by Kraliki PWA Quick Start Guide

## Verification (30 seconds)

```bash
cd /home/adminmatej/github/applications/cc-lite/frontend
./verify-pwa.sh
```

**Expected**: 23/23 checks passed ✅

## Development Testing (2 minutes)

```bash
# 1. Start server
pnpm dev

# 2. Open browser
# http://localhost:5173

# 3. Test offline
# DevTools > Network > Offline > Reload
# Should show offline page

# 4. Test installation
# Chrome > Address bar > Install icon
```

## Lighthouse Audit (1 minute)

```bash
lighthouse http://localhost:5173 \
  --view \
  --only-categories=pwa
```

**Target**: 100/100 PWA Score

## Mobile Components Usage

```svelte
<script>
  import {
    BottomNavigation,
    FloatingActionButton,
    MobileCard,
    CallQueueMobile
  } from '$lib/components/mobile';

  const calls = [
    {
      id: '1',
      customer: 'John Doe',
      phone: '+1234567890',
      status: 'waiting',
      wait_time: '2m 30s'
    }
  ];
</script>

<!-- Mobile call queue with FAB -->
<CallQueueMobile {calls} />

<!-- Or use individual components -->
<MobileCard
  title="Customer Name"
  subtitle="+1234567890"
  onclick={() => console.log('clicked')}
/>

<FloatingActionButton
  icon="📞"
  label="New Call"
  onclick={() => console.log('new call')}
/>

<!-- Bottom navigation (add to layout) -->
<BottomNavigation />
```

## File Structure

```
cc-lite/
├── PWA_IMPLEMENTATION.md       ← Complete guide
├── WEEK3-4_PWA_SUMMARY.md      ← Task summary
├── QUICK_START_PWA.md          ← This file
│
└── frontend/
    ├── verify-pwa.sh           ← Run this first!
    │
    ├── static/
    │   ├── manifest.json       ← PWA manifest
    │   ├── service-worker.js   ← Offline support
    │   ├── offline.html        ← Fallback page
    │   └── icons/              ← 8 icon sizes
    │
    └── src/
        ├── routes/
        │   ├── +layout.svelte  ← PWA meta tags
        │   └── offline/
        │       └── +page.svelte ← Offline route
        │
        └── lib/components/mobile/
            ├── BottomNavigation.svelte
            ├── FloatingActionButton.svelte
            ├── MobileCard.svelte
            ├── CallQueueMobile.svelte
            └── index.ts
```

## Key Features

- ✅ Installable on mobile + desktop
- ✅ Works offline
- ✅ 48px touch targets
- ✅ Bottom navigation
- ✅ Floating action button
- ✅ Card-based layouts
- ✅ Safe area insets

## Production Deployment

1. Generate real icons (replace SVG):
   ```bash
   convert source.svg -resize 192x192 icon-192.png
   ```

2. Enable HTTPS (required for PWA)

3. Run Lighthouse on production URL

4. Test on real devices:
   - iOS Safari: Share > Add to Home Screen
   - Android Chrome: Install prompt

## Troubleshooting

**Service worker not registering?**
- Check DevTools > Application > Service Workers
- Force update: Check "Update on reload"

**App not installing?**
- Verify HTTPS (required in production)
- Check manifest.json is accessible
- Verify icons are valid

**Offline not working?**
- Check service worker is active
- Verify cache entries in DevTools

## Resources

- Full docs: `/PWA_IMPLEMENTATION.md`
- Summary: `/WEEK3-4_PWA_SUMMARY.md`
- Verify script: `./frontend/verify-pwa.sh`

---

**Quick Win**: Run `./verify-pwa.sh` - Should see 23/23 passed ✅
