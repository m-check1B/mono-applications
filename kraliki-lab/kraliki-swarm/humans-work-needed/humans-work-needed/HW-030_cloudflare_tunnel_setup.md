# HW-030: Setup Cloudflare Zero Trust Tunnel

**Created:** 2025-12-22
**Priority:** HIGH
**Blocking:** VD-254, VD-256 (n8n production, secure service exposure)
**Time Estimate:** 30-45 minutes

## Context

The dev server has multiple services running on localhost (n8n, Zitadel, etc.) that need secure production access. Cloudflare Tunnel (Zero Trust) provides:
- No open inbound ports required
- Automatic SSL/TLS
- Access policies (authentication before reaching service)
- DDoS protection included

## Steps

### 1. Create Cloudflare Account (if not exists)
- Go to: https://dash.cloudflare.com/
- Sign up or log in

### 2. Add Domain (if not done)
- Add `verduona.dev` to Cloudflare
- Update nameservers at registrar
- Wait for propagation (~5 min)

### 3. Install cloudflared on Server

```bash
# SSH to server, then:
cd /home/adminmatej/github/infra/cloudflare-tunnel
./install.sh
```

### 4. Authenticate + Create Tunnel + DNS (scripted)

```bash
# This opens a browser for Cloudflare OAuth
cd /home/adminmatej/github/infra/cloudflare-tunnel
./setup.sh
```

This script creates the `verduona-dev-server` tunnel, writes
`/home/adminmatej/.cloudflared/verduona-dev-server.json`, and sets DNS records
for these hostnames:

- `zt-mgrep.verduona.dev`
- `zt-qdrant.verduona.dev`
- `zt-n8n.verduona.dev`
- `zt-windmill.verduona.dev`
- `zt-traefik.verduona.dev`
- `zt-crm.verduona.dev`

### 5. Run as a service (PM2)

```bash
cd /home/adminmatej/github/infra/cloudflare-tunnel
pm2 start ecosystem.config.js
pm2 save
```

### 6. Add Zero Trust Access Policies (Dashboard)

1. Go to: Cloudflare Dashboard > Zero Trust > Access > Applications
2. Add Application > Self-hosted
3. Name: "Kraliki Internal Tools"
4. Domain: `zt-*.verduona.dev`
5. Add Policy: "Allow specific emails" (your email)

## Verification

```bash
# Check tunnel status
~/bin/cloudflared tunnel list
~/bin/cloudflared tunnel info verduona-dev-server

# Test access
curl -I https://zt-n8n.verduona.dev/healthz
```

## After Completion

1. Update `/github/secrets/` with any new credentials if needed
2. Notify agents: `python3 applications/kraliki-swarm/arena/blackboard.py post "darwin-claude-integrator" "HW-030 RESOLVED: Cloudflare Tunnel configured" -t status`
3. Mark VD-254 and VD-256 as unblocked in Linear

## Related

- VD-254: Setup Cloudflare Zero Trust tunnel
- VD-256: Deploy n8n to production server
- PORT_REGISTRY.md: Current localhost bindings
