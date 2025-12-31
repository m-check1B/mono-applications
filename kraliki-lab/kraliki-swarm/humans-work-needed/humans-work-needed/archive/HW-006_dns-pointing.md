# HW-006: DNS Setup - verduona.com & verduona.dev

**Created:** 2025-12-09
**Updated:** 2025-12-20
**Priority:** HIGH
**Status:** COMPLETED (2025-12-20)
**Blocks:** Public website access, staging environment

## Server Details

- **IP:** 5.9.38.218
- **Provider:** Hetzner (dev server)
- **Traefik:** Running on ports 80/443 with Let's Encrypt

---

## PART 1: verduona.com (Marketing Websites - DO NOW)

### Cloudflare/Namecheap Settings

**CRITICAL: Cloudflare proxy MUST be OFF (grey cloud, DNS only)**
Traefik handles SSL via Let's Encrypt. If proxy is ON, HTTP challenge fails.

### DNS Records

| Type | Name | Value | TTL | Proxy |
|------|------|-------|-----|-------|
| A | @ | 5.9.38.218 | 300 | OFF |
| A | www | 5.9.38.218 | 300 | OFF |
| A | business | 5.9.38.218 | 300 | OFF |
| A | family | 5.9.38.218 | 300 | OFF |
| A | consulting | 5.9.38.218 | 300 | OFF |
| A | company | 5.9.38.218 | 300 | OFF |
| A | demos | 5.9.38.218 | 300 | OFF |
| A | tldr | 5.9.38.218 | 300 | OFF |
| A | magicbox | 5.9.38.218 | 300 | OFF |
| A | inzenyring | 5.9.38.218 | 300 | OFF |
| A | crm | 5.9.38.218 | 300 | OFF |

---

## PART 2: verduona.dev (Staging/Dev - DO NOW)

Set up for future staging apps. Wildcard covers all subdomains.

| Type | Name | Value | TTL | Proxy |
|------|------|-------|-----|-------|
| A | @ | 5.9.38.218 | 300 | OFF |
| A | * | 5.9.38.218 | 300 | OFF |

Future subdomains: `focus.verduona.dev`, `cc.verduona.dev`, `api.verduona.dev`

---

## Domain Strategy Summary

| Domain | Purpose | Server |
|--------|---------|--------|
| verduona.com | Marketing websites | Dev server (5.9.38.218) |
| *.verduona.com | Marketing subdomains | Dev server (5.9.38.218) |
| verduona.dev | Staging/dev apps | Dev server (5.9.38.218) |
| *.verduona.dev | Staging subdomains | Dev server (5.9.38.218) |

**LATER (not now):** Production apps will move to separate production server with different IP.

---

## Verification Steps

After DNS changes, wait ~5 minutes for propagation (TTL 300).

### 1. Check DNS Propagation

```bash
dig verduona.com +short
# Expected: 5.9.38.218

dig business.verduona.com +short
# Expected: 5.9.38.218

dig verduona.dev +short
# Expected: 5.9.38.218
```

### 2. Test HTTPS (after propagation)

```bash
curl -I https://verduona.com
# Expected: HTTP/2 200

curl -I https://business.verduona.com
# Expected: HTTP/2 200
```

### 3. Check SSL Certificate

```bash
echo | openssl s_client -connect verduona.com:443 2>/dev/null | openssl x509 -noout -issuer -dates
# Expected: Let's Encrypt issuer, valid dates
```

---

## Troubleshooting

### SSL Not Working?

1. Ensure Cloudflare proxy is OFF (grey cloud)
2. Check Traefik logs: `docker compose -f /github/infra/compose/websites.yml logs traefik`
3. Let's Encrypt may rate-limit if too many attempts

### Site Not Loading?

1. Verify DNS propagation: `dig verduona.com +short`
2. Check Traefik is running: `docker ps | grep traefik`
3. Check site container: `docker ps | grep websites`

---

## Rollback

If issues occur, point DNS back to previous provider or set TTL to 3600 and wait.

---

## Notes

- SSL certificates auto-generate on first request (may take 30s)
- Traefik dashboard: `http://localhost:8089` (SSH tunnel required)
- All services bind to localhost except ports 80/443
