# Human Task: Configure DNS for crm.verduona.com

**Priority:** Required for CRM SSL access
**Estimated time:** 5 minutes

## What's Needed

Add DNS record for `crm.verduona.com` pointing to the dev server so Traefik can issue SSL certificate.

## Steps

### 1. Add DNS Record

In your DNS provider (Cloudflare, etc.):

| Type | Name | Value | TTL |
|------|------|-------|-----|
| A | crm | 5.9.38.218 | Auto |

Or if using CNAME to existing record:

| Type | Name | Value | TTL |
|------|------|-------|-----|
| CNAME | crm | verduona.com | Auto |

### 2. Restart CRM with New Network

```bash
cd /home/adminmatej/github/crm
docker compose down
docker compose up -d
```

### 3. Verify SSL Certificate

Wait 1-2 minutes for Let's Encrypt, then:

```bash
# Check Traefik routing
curl -I https://crm.verduona.com

# Should see:
# HTTP/2 200
# or HTTP/2 302 (redirect to login)
```

### 4. Update EspoCRM Site URL

In EspoCRM admin:
1. Go to Administration > Settings
2. Update "Site URL" to `https://crm.verduona.com`
3. Save

## Verification

1. Access https://crm.verduona.com
2. Should see EspoCRM login with valid SSL certificate
3. Check certificate shows `crm.verduona.com`

## Notes

- CRM docker-compose already updated with Traefik labels
- Health checks added to all CRM containers
- Fallback local access still works at `127.0.0.1:8080`

---

*Created: 2025-12-09*
