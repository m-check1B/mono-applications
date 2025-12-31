# Focus by Kraliki - Hetzner Deployment Guide

Complete guide for deploying Focus by Kraliki to a Hetzner VPS with Docker, automatic HTTPS, and production best practices.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Server Setup](#server-setup)
- [Initial Configuration](#initial-configuration)
- [Deployment](#deployment)
- [Post-Deployment](#post-deployment)
- [Maintenance](#maintenance)
- [Troubleshooting](#troubleshooting)

## Prerequisites

### Hetzner Account

1. **Sign up**: https://accounts.hetzner.com/signUp
2. **Add SSH key** in Hetzner Console → Security → SSH Keys

### Recommended Server Specs

| Usage | Server | CPU | RAM | Storage | Price/mo |
|-------|--------|-----|-----|---------|----------|
| **Dev/Testing** | CX21 | 2 vCPU | 4 GB | 40 GB | ~€5 |
| **Small Production** | CX31 | 2 vCPU | 8 GB | 80 GB | ~€9 |
| **Production** | CX41 | 4 vCPU | 16 GB | 160 GB | ~€16 |

### Domain Requirements

You need two subdomains pointing to your server IP:
- `app.yourdomain.com` → Frontend
- `api.yourdomain.com` → Backend API

## Server Setup

### 1. Create Server

```bash
# Via Hetzner Console
1. Go to Cloud → Create Server
2. Location: Choose nearest to your users
3. Image: Ubuntu 22.04 LTS
4. Type: CX21 or higher
5. SSH Key: Select your key
6. Name: focus-kraliki-prod
7. Click "Create & Buy Now"
```

### 2. Initial Server Configuration

SSH into your server:

```bash
ssh root@YOUR_SERVER_IP
```

Update system and install essentials:

```bash
# Update system
apt update && apt upgrade -y

# Install essentials
apt install -y curl git ufw fail2ban htop

# Set timezone
timedatectl set-timezone Europe/Berlin  # Or your timezone

# Set hostname
hostnamectl set-hostname focus-kraliki-prod
```

### 3. Security Setup

```bash
# Configure firewall
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable

# Configure fail2ban
systemctl enable fail2ban
systemctl start fail2ban

# Create non-root user
adduser deploy
usermod -aG sudo deploy
mkdir -p /home/deploy/.ssh
cp ~/.ssh/authorized_keys /home/deploy/.ssh/
chown -R deploy:deploy /home/deploy/.ssh
chmod 700 /home/deploy/.ssh
chmod 600 /home/deploy/.ssh/authorized_keys

# Test new user (open new terminal)
ssh deploy@YOUR_SERVER_IP

# If successful, disable root login
sed -i 's/PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
systemctl restart sshd
```

### 4. Install Docker

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Add user to docker group
usermod -aG docker deploy

# Log out and back in for group to take effect
exit
ssh deploy@YOUR_SERVER_IP

# Verify Docker installation
docker --version
docker compose version

# Enable Docker to start on boot
sudo systemctl enable docker
```

## Initial Configuration

### 1. Clone Repository

```bash
# Clone as deploy user
cd ~
git clone https://github.com/your-org/focus-kraliki.git
cd focus-kraliki

# Checkout production branch
git checkout main  # or your production branch
```

### 2. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit environment file
nano .env
```

**Required `.env` configuration:**

```bash
# Database
DB_USER=postgres
DB_PASSWORD=<generate with: openssl rand -base64 32>

# Redis
REDIS_PASSWORD=<generate with: openssl rand -base64 32>

# Security - Generate strong secrets
JWT_SECRET=<generate with: openssl rand -hex 32>
SESSION_SECRET=<generate with: openssl rand -hex 32>

# AI Services (required)
ANTHROPIC_API_KEY=sk-ant-api03-...
OPENAI_API_KEY=sk-...

# AI Services (optional)
DEEPGRAM_API_KEY=...
GEMINI_API_KEY=...
OPENAI_REALTIME_API_KEY=...

# Domains
DOMAIN=app.yourdomain.com
API_DOMAIN=api.yourdomain.com

# CORS - Update with your domain
ALLOWED_ORIGINS=https://app.yourdomain.com

# API URL for frontend
PUBLIC_API_URL=https://api.yourdomain.com

# Webhook Configuration
II_AGENT_WEBHOOK_SECRET=<generate with: openssl rand -hex 32>
GOOGLE_CALENDAR_WEBHOOK_TOKEN=<generate with: openssl rand -hex 32>

# Static Files (optional)
STATIC_FILE_BASE_URL=https://cdn.example.com  # If using external CDN for static assets
```

**Generate secure secrets:**

```bash
# Generate DB password
openssl rand -base64 32

# Generate Redis password
openssl rand -base64 32

# Generate JWT secret
openssl rand -hex 32

# Generate Session secret
openssl rand -hex 32

# Generate II-Agent webhook secret
openssl rand -hex 32

# Generate Google Calendar webhook token
openssl rand -hex 32
```

### 3. DNS Configuration

Point your domains to the server IP:

```
Type    Name    Value           TTL
A       app     YOUR_SERVER_IP  300
A       api     YOUR_SERVER_IP  300
```

Wait for DNS propagation (check with `nslookup app.yourdomain.com`).

## Deployment

### Automated Deployment (Recommended)

```bash
cd ~/focus-kraliki
./scripts/deploy-hetzner.sh
```

The script will:
1. ✅ Validate environment variables
2. ✅ Backup existing database
3. ✅ Build Docker images
4. ✅ Start all services
5. ✅ Run database migrations
6. ✅ Perform health checks
7. ✅ Ensure Traefik routing/TLS is active (shared reverse proxy)

### Manual Deployment

If you prefer manual control:

```bash
# Build images
docker compose -f docker-compose.prod.yml build

# Start services
docker compose -f docker-compose.prod.yml up -d

# Check status
docker compose -f docker-compose.prod.yml ps

# View logs
docker compose -f docker-compose.prod.yml logs -f

# Run migrations
docker compose -f docker-compose.prod.yml exec backend alembic upgrade head
```

## Post-Deployment

### 1. Verify Services

```bash
# Check all containers are running
docker compose -f docker-compose.prod.yml ps

# Check logs
docker compose -f docker-compose.prod.yml logs --tail=100

# Test health endpoints
curl https://api.yourdomain.com/health
curl https://app.yourdomain.com
```

### 2. Access Application

- **Frontend**: https://app.yourdomain.com
- **API**: https://api.yourdomain.com
- **API Docs**: https://api.yourdomain.com/docs

### 3. Create First User

Register at: https://app.yourdomain.com/register

### 4. Setup Monitoring

```bash
# Install monitoring script
./scripts/monitor.sh

# View container stats
docker stats

# Check disk space
df -h

# Check memory
free -h
```

### 5. Setup Automated Backups

```bash
# Test backup
./scripts/backup.sh

# Setup daily backups with cron
crontab -e

# Add this line (daily at 2 AM)
0 2 * * * cd /home/deploy/focus-kraliki && ./scripts/backup.sh >> /home/deploy/backup.log 2>&1
```

## Maintenance

### Viewing Logs

```bash
# All services
docker compose -f docker-compose.prod.yml logs -f

# Specific service
docker compose -f docker-compose.prod.yml logs -f backend
docker compose -f docker-compose.prod.yml logs -f frontend
docker compose -f docker-compose.prod.yml logs -f postgres
docker compose -f docker-compose.prod.yml logs -f redis

# Last 100 lines
docker compose -f docker-compose.prod.yml logs --tail=100
```

### Updating Application

```bash
cd ~/focus-kraliki

# Pull latest code
git pull origin main

# Redeploy
./scripts/deploy-hetzner.sh
```

### Database Management

```bash
# Backup database
./scripts/backup.sh

# Restore database
./scripts/restore.sh backups/focus_kraliki_backup_20251113_120000.sql.gz

# Connect to database
docker compose -f docker-compose.prod.yml exec postgres psql -U postgres focus_kraliki

# Run migrations
docker compose -f docker-compose.prod.yml exec backend alembic upgrade head

# Rollback migration
docker compose -f docker-compose.prod.yml exec backend alembic downgrade -1
```

### Container Management

```bash
# Restart all services
docker compose -f docker-compose.prod.yml restart

# Restart specific service
docker compose -f docker-compose.prod.yml restart backend

# Stop all services
docker compose -f docker-compose.prod.yml down

# Stop and remove volumes (DANGER - deletes data)
docker compose -f docker-compose.prod.yml down -v

# Rebuild service
docker compose -f docker-compose.prod.yml up -d --build backend
```

### SSL Certificate Management

Traefik handles SSL automatically. Check Traefik status/logs via the shared stack:

```bash
cd /home/adminmatej/github/websites
docker compose logs -f traefik
```

## Troubleshooting

### Service Not Starting

```bash
# Check logs
docker compose -f docker-compose.prod.yml logs [service-name]

# Check container status
docker compose -f docker-compose.prod.yml ps

# Restart service
docker compose -f docker-compose.prod.yml restart [service-name]
```

### Database Connection Issues

```bash
# Check PostgreSQL is running
docker compose -f docker-compose.prod.yml ps postgres

# Check PostgreSQL logs
docker compose -f docker-compose.prod.yml logs postgres

# Test connection
docker compose -f docker-compose.prod.yml exec postgres pg_isready -U postgres

# Connect to PostgreSQL
docker compose -f docker-compose.prod.yml exec postgres psql -U postgres focus_kraliki
```

### Redis Connection Issues

```bash
# Check Redis is running
docker compose -f docker-compose.prod.yml ps redis

# Check Redis logs
docker compose -f docker-compose.prod.yml logs redis

# Test connection (replace PASSWORD with your REDIS_PASSWORD)
docker compose -f docker-compose.prod.yml exec redis redis-cli -a PASSWORD ping
```

### SSL/HTTPS Issues

```bash
# Check Traefik logs
cd /home/adminmatej/github/websites
docker compose logs traefik

# Verify DNS is pointing to server
nslookup app.yourdomain.com
nslookup api.yourdomain.com

# Check firewall allows ports 80 and 443
sudo ufw status

# Restart Traefik
docker compose restart traefik
```

### High Memory Usage

```bash
# Check memory usage
free -h
docker stats

# Restart services to clear memory
docker compose -f docker-compose.prod.yml restart

# If Redis is using too much memory, clear cache
docker compose -f docker-compose.prod.yml exec redis redis-cli -a PASSWORD FLUSHDB
```

### Disk Space Issues

```bash
# Check disk usage
df -h

# Clean Docker resources
docker system prune -a

# Remove old backups (keep last 7 days)
find backups/ -name "*.sql.gz" -mtime +7 -delete

# Check Docker volumes
docker system df
```

### Application Errors

```bash
# Check backend logs for errors
docker compose -f docker-compose.prod.yml logs backend --tail=200

# Check if environment variables are set correctly
docker compose -f docker-compose.prod.yml exec backend env | grep -E "DATABASE_URL|ANTHROPIC|OPENAI"

# Restart backend
docker compose -f docker-compose.prod.yml restart backend
```

### Performance Issues

```bash
# Check resource usage
htop
docker stats

# Check slow database queries
docker compose -f docker-compose.prod.yml exec postgres psql -U postgres focus_kraliki -c "SELECT * FROM pg_stat_activity WHERE state = 'active';"

# Clear Redis cache if needed
docker compose -f docker-compose.prod.yml exec redis redis-cli -a PASSWORD FLUSHDB
```

## Security Best Practices

### Regular Updates

```bash
# Update system packages monthly
sudo apt update && sudo apt upgrade -y

# Update Docker images
docker compose -f docker-compose.prod.yml pull
./scripts/deploy-hetzner.sh
```

### Backup Strategy

- **Daily automated backups** to local disk
- **Weekly offsite backups** to Hetzner Storage Box or S3
- **Test restores** monthly to verify backups work

### Monitoring

Set up monitoring for:
- ✅ Service uptime (UptimeRobot or similar)
- ✅ SSL certificate expiration (automatic with Traefik)
- ✅ Disk space usage
- ✅ Memory usage
- ✅ Application errors in logs

### Access Control

- ✅ Use SSH keys only (no password auth)
- ✅ Regularly rotate API keys and secrets
- ✅ Use strong database passwords
- ✅ Enable 2FA on critical accounts
- ✅ Regular security audits

## Performance Optimization

### Database

```bash
# Analyze and optimize tables
docker compose -f docker-compose.prod.yml exec postgres psql -U postgres focus_kraliki -c "ANALYZE;"

# Vacuum database
docker compose -f docker-compose.prod.yml exec postgres psql -U postgres focus_kraliki -c "VACUUM ANALYZE;"
```

### Redis Cache

Configured with:
- LRU eviction policy
- 256MB memory limit
- Persistence enabled

### Scaling

For high traffic, consider:
1. Upgrade server (CX41 → CX51)
2. Use managed PostgreSQL (Hetzner Managed Database)
3. Add Redis cluster
4. Load balancer with multiple backend instances

## Cost Estimation

### Monthly Costs (EUR)

| Component | Cost |
|-----------|------|
| CX21 Server | €5 |
| CX31 Server | €9 |
| CX41 Server | €16 |
| Bandwidth (20TB included) | €0 |
| Backups (optional) | ~€1 |
| Storage Box 100GB (optional) | €3 |

**Total for small production**: ~€10-20/month

## Support & Resources

- **Hetzner Docs**: https://docs.hetzner.com
- **Docker Docs**: https://docs.docker.com
- **Traefik Docs**: https://doc.traefik.io/traefik/
- **Focus by Kraliki Issues**: https://github.com/your-org/focus-kraliki/issues

## Quick Reference

```bash
# Deploy/Update
./scripts/deploy-hetzner.sh

# View logs
docker compose -f docker-compose.prod.yml logs -f

# Backup
./scripts/backup.sh

# Restore
./scripts/restore.sh <backup-file>

# Restart
docker compose -f docker-compose.prod.yml restart

# Stop
docker compose -f docker-compose.prod.yml down

# Status
docker compose -f docker-compose.prod.yml ps
```

---

**Focus by Kraliki on Hetzner** - Production-ready deployment with automatic HTTPS, backups, and monitoring.
