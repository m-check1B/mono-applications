# HW-013: Point verduona.dev DNS to Dev Server

**Status:** DONE
**Created:** 2025-12-20
**Priority:** HIGH
**Blocks:** BETA-EXPOSURE feature (beta app testing)

## What's Needed

Point the `verduona.dev` domain (and wildcard subdomains) to the dev server.

## DNS Records to Add

In your domain registrar (Namecheap/Cloudflare):

| Type | Host | Value | TTL |
|------|------|-------|-----|
| A | @ | 5.9.38.218 | 300 |
| A | * | 5.9.38.218 | 300 |

**Important:** If using Cloudflare, set proxy to **OFF** (gray cloud) for Let's Encrypt to work.

## Subdomains That Will Work

Once DNS is pointed:
- `vop.verduona.dev` - Voice of People
- `cc.verduona.dev` - CC-Lite 2026
- `focus.verduona.dev` - Focus-Lite
- `skola.verduona.dev` - Skola Pilot

## Verification

After DNS propagation (~5-15 min):
```bash
dig vop.verduona.dev
# Should return: 5.9.38.218
```

## Why verduona.dev?

- `.dev` = beta/development testing
- `.com` = production (customer-facing)
- Separate domains allow testing without affecting production
