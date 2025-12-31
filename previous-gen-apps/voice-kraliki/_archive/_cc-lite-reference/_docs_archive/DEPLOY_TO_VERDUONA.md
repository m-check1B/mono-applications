# 🚀 Deploy Voice by Kraliki to verduona.dev

## Quick Deploy (Recommended)

**One command to deploy everything:**

```bash
cd /home/adminmatej/github/apps/cc-lite
bash deploy/QUICK_DEPLOY.sh
```

This script will:
1. ✅ Install/verify Nginx on host
2. ✅ Get SSL certificate for cc-lite.verduona.dev
3. ✅ Configure Nginx reverse proxy
4. ✅ Create .env.production (if needed)
5. ✅ Create data directories
6. ✅ Build and start Docker containers
7. ✅ Run database migrations
8. ✅ Verify deployment

**Time**: ~5 minutes
**Result**: https://cc-lite.verduona.dev

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│ Internet (AI Agents - OpenAI, Claude, etc)          │
└─────────────────────┬───────────────────────────────┘
                      │
                      │ HTTPS (443)
                      ↓
┌─────────────────────────────────────────────────────┐
│ Host Nginx (verduona.dev server)                    │
│ - SSL Termination (Let's Encrypt)                   │
│ - Reverse Proxy                                      │
│ - Rate Limiting                                      │
│ - Security Headers                                   │
└─────────────────────┬───────────────────────────────┘
                      │
        ┌─────────────┼─────────────┐
        │             │             │
        ↓             ↓             ↓
  127.0.0.1:3007  127.0.0.1:3010  127.0.0.1:5432
     Frontend        Backend       Database
        │             │             │
┌───────┴─────────────┴─────────────┴─────────────────┐
│ Docker Containers                                    │
│ ├─ cc-lite-app (Frontend + Backend)                 │
│ ├─ cc-lite-postgres (Database)                      │
│ └─ cc-lite-redis (Cache)                            │
└─────────────────────────────────────────────────────┘
```

---

## Manual Deployment (Step-by-Step)

### Step 1: Prepare Environment

```bash
cd /home/adminmatej/github/apps/cc-lite

# Copy environment template
cp .env.production.template .env.production

# Edit with your credentials (tomorrow)
nano .env.production
```

**Required credentials:**
- Database password
- Redis password
- JWT secrets (auto-generated)
- Twilio credentials (for calls)
- OpenAI API key (for AI)
- Deepgram API key (for transcription)

### Step 2: Install Host Nginx

```bash
sudo apt-get update
sudo apt-get install -y nginx certbot python3-certbot-nginx
```

### Step 3: Get SSL Certificate

```bash
sudo certbot certonly --nginx -d cc-lite.verduona.dev
```

**Certificate location:**
- `/etc/letsencrypt/live/verduona.dev/fullchain.pem`
- `/etc/letsencrypt/live/verduona.dev/privkey.pem`

### Step 4: Configure Nginx

```bash
# Copy config
sudo cp deploy/host-nginx/cc-lite.verduona.dev.conf /etc/nginx/sites-available/cc-lite.verduona.dev

# Enable site
sudo ln -s /etc/nginx/sites-available/cc-lite.verduona.dev /etc/nginx/sites-enabled/

# Test config
sudo nginx -t

# Reload
sudo systemctl reload nginx
```

### Step 5: Create Data Directories

```bash
sudo mkdir -p /opt/cc-lite/{data,logs,backups,uploads}/{postgres,redis,app}
sudo chown -R $USER:$USER /opt/cc-lite
```

### Step 6: Build Application

```bash
pnpm install --frozen-lockfile
pnpm prisma generate
pnpm build
```

### Step 7: Start Docker Containers

```bash
# Start services
docker compose -f docker compose.simple.yml up -d --build

# Check status
docker compose -f docker compose.simple.yml ps

# View logs
docker compose -f docker compose.simple.yml logs -f app
```

### Step 8: Run Database Migrations

```bash
# Wait for database to be ready
sleep 10

# Run migrations
pnpm prisma migrate deploy

# Seed demo users (optional)
pnpm run db:seed
```

### Step 9: Verify Deployment

```bash
# Check health
curl http://localhost:3010/health
curl https://cc-lite.verduona.dev/health

# Check frontend
curl -I https://cc-lite.verduona.dev

# Check logs
docker compose -f docker compose.simple.yml logs app
```

---

## For AI Agent Testing

### Why This Setup is Perfect for AI Agents:

1. **Public HTTPS URL**: `https://cc-lite.verduona.dev`
   - OpenAI assistants can access it
   - Claude can browse and interact
   - No CORS issues
   - Valid SSL certificate

2. **Stable Domain**:
   - Persistent URL (not ngrok temporary)
   - Proper DNS resolution
   - Production-like environment

3. **Full Features**:
   - Real authentication
   - Database persistence
   - WebSocket support
   - File uploads work

4. **Monitoring**:
   - Access logs: `/var/log/nginx/cc-lite-access.log`
   - Error logs: `/var/log/nginx/cc-lite-error.log`
   - Application logs: `docker compose logs -f`

### Testing with OpenAI Assistants

```python
# Example: OpenAI assistant with browsing
from openai import OpenAI

client = OpenAI(api_key="your-key")

assistant = client.beta.assistants.create(
    name="Voice by Kraliki Tester",
    instructions="""You are a QA tester for Voice by Kraliki call center app.

    Test these features:
    1. Login at https://cc-lite.verduona.dev
    2. Navigate dashboards
    3. Try creating campaigns
    4. Test all buttons and forms
    5. Report any bugs or issues

    Credentials:
    - Email: test.assistant@stack2025.com
    - Password: Stack2025!Test@Assistant#Secure$2024
    """,
    tools=[{"type": "code_interpreter"}],
    model="gpt-4-turbo-preview"
)

# The assistant can now browse and interact with your app
```

### Testing with Claude

```bash
# Give Claude this prompt:
"Please test the Voice by Kraliki application at https://cc-lite.verduona.dev

Login with:
- Email: test.assistant@stack2025.com
- Password: Stack2025!Test@Assistant#Secure$2024

Test all features and report:
1. What works well
2. What's broken
3. UI/UX issues
4. Performance problems
5. Suggestions for improvement"
```

---

## Useful Commands

### Docker Management

```bash
# View all containers
docker compose -f docker compose.simple.yml ps

# View logs (all services)
docker compose -f docker compose.simple.yml logs -f

# View logs (specific service)
docker compose -f docker compose.simple.yml logs -f app

# Restart services
docker compose -f docker compose.simple.yml restart

# Stop services
docker compose -f docker compose.simple.yml down

# Rebuild and restart
docker compose -f docker compose.simple.yml up -d --build
```

### Database Management

```bash
# Access PostgreSQL
docker exec -it cc-lite-postgres psql -U cc_lite_user -d cc_light

# Run migrations
pnpm prisma migrate deploy

# View migration status
pnpm prisma migrate status

# Reset database (WARNING: deletes all data)
pnpm prisma migrate reset

# Backup database
docker exec cc-lite-postgres pg_dump -U cc_lite_user cc_light > backup.sql

# Restore database
docker exec -i cc-lite-postgres psql -U cc_lite_user cc_light < backup.sql
```

### Nginx Management

```bash
# Test config
sudo nginx -t

# Reload config
sudo systemctl reload nginx

# Restart Nginx
sudo systemctl restart nginx

# View access logs
sudo tail -f /var/log/nginx/cc-lite-access.log

# View error logs
sudo tail -f /var/log/nginx/cc-lite-error.log
```

### SSL Certificate Renewal

```bash
# Test renewal (dry run)
sudo certbot renew --dry-run

# Renew certificates
sudo certbot renew

# Auto-renew is configured via cron
sudo systemctl status certbot.timer
```

---

## Troubleshooting

### App Not Accessible

```bash
# Check containers running
docker compose -f docker compose.simple.yml ps

# Check app logs
docker compose -f docker compose.simple.yml logs app

# Check health endpoint
curl http://localhost:3010/health

# Check Nginx
sudo systemctl status nginx
sudo nginx -t
```

### Database Connection Issues

```bash
# Check PostgreSQL is running
docker ps | grep postgres

# Test connection
docker exec cc-lite-postgres pg_isready

# Check logs
docker logs cc-lite-postgres

# Verify DATABASE_URL in .env.production
grep DATABASE_URL .env.production
```

### SSL Certificate Issues

```bash
# Check certificate validity
sudo certbot certificates

# Test SSL connection
openssl s_client -connect cc-lite.verduona.dev:443

# Renew certificate
sudo certbot renew --force-renewal
```

### 502 Bad Gateway

This usually means the app container isn't running or healthy:

```bash
# Check container status
docker ps

# Check app logs
docker logs cc-lite-app

# Restart app
docker compose -f docker compose.simple.yml restart app

# Check health
curl http://localhost:3010/health
```

---

## Updating the Application

### Quick Update

```bash
cd /home/adminmatej/github/apps/cc-lite

# Pull latest changes
git pull

# Rebuild and restart
docker compose -f docker compose.simple.yml up -d --build

# Run migrations if needed
pnpm prisma migrate deploy

# Verify
curl https://cc-lite.verduona.dev/health
```

### Zero-Downtime Update

```bash
# Build new version
docker compose -f docker compose.simple.yml build

# Start new container
docker compose -f docker compose.simple.yml up -d --no-deps --build app

# Old container stops, new one starts
# Nginx automatically routes to new container
```

---

## Monitoring

### Health Checks

```bash
# Application health
curl https://cc-lite.verduona.dev/health

# Expected response
{"status":"ok","timestamp":"2025-01-29T20:00:00.000Z"}
```

### Metrics

```bash
# View app metrics
curl http://localhost:3010/metrics

# Container stats
docker stats cc-lite-app cc-lite-postgres cc-lite-redis
```

### Logs

```bash
# Application logs
docker compose -f docker compose.simple.yml logs -f app

# Nginx access logs
sudo tail -f /var/log/nginx/cc-lite-access.log

# All logs together
sudo tail -f /var/log/nginx/cc-lite-*.log & \
docker compose -f docker compose.simple.yml logs -f
```

---

## Security Checklist

Before going live:

- [ ] SSL certificate installed and valid
- [ ] Strong passwords in .env.production
- [ ] SEED_DEMO_USERS=false
- [ ] Firewall configured (only 80, 443 open)
- [ ] Database not exposed to internet
- [ ] Redis password protected
- [ ] Regular backups configured
- [ ] Monitoring alerts set up

---

## Cost & Performance

**Server Requirements:**
- CPU: 2+ cores
- RAM: 4GB minimum
- Disk: 20GB
- Bandwidth: 1TB/month

**Expected Performance:**
- Response time: <100ms (p95)
- Concurrent users: 50-100
- API requests: 10,000/day
- Database size: <1GB (first 6 months)

---

## Next Steps

1. **Deploy**: Run `bash deploy/QUICK_DEPLOY.sh`
2. **Test manually**: Visit https://cc-lite.verduona.dev
3. **Test with AI agents**: Point OpenAI/Claude to URL
4. **Monitor**: Watch logs and metrics
5. **Iterate**: Based on feedback

---

**Questions?** Check logs first:
```bash
docker compose -f docker compose.simple.yml logs -f app
```

**Ready to deploy?**
```bash
bash deploy/QUICK_DEPLOY.sh
```

🚀 **Let's go live!**