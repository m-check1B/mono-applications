# Hetzner Cloud Deployment Guide

**Operator Demo 2026** - Complete deployment guide for Hetzner Cloud servers

**Version:** 2.0.0
**Last Updated:** November 13, 2025
**Target:** Production deployment on Hetzner Cloud

---

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Server Setup](#server-setup)
4. [Quick Start](#quick-start)
5. [Detailed Deployment Steps](#detailed-deployment-steps)
6. [Configuration](#configuration)
7. [Security Setup](#security-setup)
8. [Monitoring & Maintenance](#monitoring--maintenance)
9. [Troubleshooting](#troubleshooting)
10. [Backup & Recovery](#backup--recovery)

---

## Overview

This guide provides step-by-step instructions for deploying the Operator Demo 2026 application on Hetzner Cloud servers. The deployment uses Docker Compose for container orchestration and includes all necessary services:

- **Backend API** (FastAPI/Python)
- **Frontend** (SvelteKit)
- **PostgreSQL** (Database)
- **Redis** (Cache & Pub/Sub)
- **Qdrant** (Vector Database)

### Recommended Hetzner Server Specs

#### Minimum (Testing)
- **Type:** CX21 or CPX21
- **CPU:** 2 vCPU
- **RAM:** 4 GB
- **Storage:** 40 GB SSD
- **Cost:** ~€5-8/month

#### Recommended (Production)
- **Type:** CX31 or CPX31
- **CPU:** 4 vCPU
- **RAM:** 8 GB
- **Storage:** 80 GB SSD
- **Cost:** ~€12-18/month

#### High Traffic (Enterprise)
- **Type:** CX41 or CPX41
- **CPU:** 8 vCPU
- **RAM:** 16 GB
- **Storage:** 160 GB SSD
- **Cost:** ~€24-36/month

---

## Prerequisites

### Required Software

- **SSH Client** (for connecting to your Hetzner server)
- **Git** (version control)
- **Domain name** (optional, but recommended for production)

### Required Accounts

- Hetzner Cloud account with active server
- GitHub account (for repository access)
- Domain registrar (if using custom domain)

---

## Server Setup

### 1. Create Hetzner Cloud Server

1. Log in to [Hetzner Cloud Console](https://console.hetzner.cloud/)
2. Create a new project (e.g., "operator-demo-prod")
3. Click **"Add Server"**
4. Choose:
   - **Location:** Choose closest to your users (e.g., Nuremberg, Helsinki, Ashburn)
   - **Image:** Ubuntu 22.04 LTS
   - **Type:** CX31 or higher (see recommendations above)
   - **SSH Key:** Add your SSH public key
   - **Volumes:** Optional - add for extra storage if needed
   - **Networking:**
     - Enable IPv4 & IPv6
     - Consider adding to private network for extra security
   - **Firewall:** Create firewall (see Security Setup below)
   - **Backups:** Enable automatic backups (recommended)

5. Click **"Create & Buy now"**

6. Note down your server's IP address once it's created

### 2. Initial Server Configuration

Connect to your server:

```bash
ssh root@YOUR_SERVER_IP
```

Update system packages:

```bash
apt update && apt upgrade -y
```

Install required software:

```bash
# Install Docker
curl -fsSL https://get.docker.com | sh

# Start and enable Docker
systemctl start docker
systemctl enable docker

# Install Docker Compose (latest version)
mkdir -p /usr/local/lib/docker/cli-plugins
curl -SL https://github.com/docker/compose/releases/latest/download/docker-compose-linux-x86_64 \
  -o /usr/local/lib/docker/cli-plugins/docker-compose
chmod +x /usr/local/lib/docker/cli-plugins/docker-compose

# Install other utilities
apt install -y git curl wget htop nano ufw fail2ban
```

Verify installations:

```bash
docker --version
docker compose version
git --version
```

### 3. Create Deployment User (Security Best Practice)

Instead of running everything as root, create a dedicated user:

```bash
# Create user
adduser operator
usermod -aG sudo operator
usermod -aG docker operator

# Set up SSH for new user
mkdir -p /home/operator/.ssh
cp ~/.ssh/authorized_keys /home/operator/.ssh/
chown -R operator:operator /home/operator/.ssh
chmod 700 /home/operator/.ssh
chmod 600 /home/operator/.ssh/authorized_keys
```

From now on, use the `operator` user for deployment:

```bash
su - operator
```

---

## Quick Start

### One-Command Deployment

If you already have your `.env.production` file configured:

```bash
# Clone repository
cd /opt
sudo mkdir -p operator-demo && sudo chown operator:operator operator-demo
cd operator-demo
git clone https://github.com/m-check1B/cc-lite-2026.git .
git checkout develop

# Configure environment
cp .env.production.template .env.production
nano .env.production  # Edit with your settings

# Deploy
./scripts/deploy-hetzner.sh init
```

That's it! Your application should now be running.

---

## Detailed Deployment Steps

### Step 1: Clone Repository

```bash
# Create deployment directory
sudo mkdir -p /opt/operator-demo
sudo chown operator:operator /opt/operator-demo
cd /opt/operator-demo

# Clone repository
git clone https://github.com/m-check1B/cc-lite-2026.git .

# Switch to develop branch
git checkout develop
```

### Step 2: Configure Environment

```bash
# Copy environment template
cp .env.production.template .env.production

# Generate secure secrets
./scripts/deploy-hetzner.sh init

# When prompted, generate secrets and add them to .env.production
nano .env.production
```

**Required environment variables to configure:**

```bash
# Generate these secrets (will be shown by the script)
POSTGRES_PASSWORD=<32-char-random-string>
REDIS_PASSWORD=<32-char-random-string>
SECRET_KEY=<64-char-random-string>

# Update with your domain (or use IP temporarily)
PUBLIC_URL=https://yourdomain.com
PUBLIC_API_BASE_URL=https://api.yourdomain.com
PUBLIC_EXTERNAL_API_BASE_URL=https://api.yourdomain.com

# Add API keys if using these services
OPENAI_API_KEY=sk-proj-...
GEMINI_API_KEY=AIzaSy...
DEEPGRAM_API_KEY=...
TWILIO_ACCOUNT_SID=...
TWILIO_AUTH_TOKEN=...
```

**Security note:** Set proper file permissions:

```bash
chmod 600 .env.production
```

### Step 3: Initial Deployment

Run the deployment script:

```bash
./scripts/deploy-hetzner.sh init
```

This will:
1. Check all requirements
2. Create necessary directories
3. Pull and build Docker images
4. Start all services
5. Run database migrations
6. Optionally create an admin user

### Step 4: Verify Deployment

Check service status:

```bash
./scripts/deploy-hetzner.sh status
```

You should see all services running and healthy.

Test endpoints:

```bash
# Backend health check
curl http://localhost:8000/health

# Frontend
curl http://localhost:3000
```

### Step 5: Configure Domain and SSL (Production)

#### Option A: Using Nginx (Simpler)

1. Install Nginx:

```bash
sudo apt install -y nginx certbot python3-certbot-nginx
```

2. Create Nginx configuration:

```bash
sudo nano /etc/nginx/sites-available/operator-demo
```

Add this configuration:

```nginx
# HTTP - Redirect to HTTPS
server {
    listen 80;
    listen [::]:80;
    server_name yourdomain.com api.yourdomain.com;

    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }

    location / {
        return 301 https://$host$request_uri;
    }
}

# HTTPS - Frontend
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name yourdomain.com;

    # SSL certificates (will be configured by certbot)
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
}

# HTTPS - Backend API
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name api.yourdomain.com;

    # SSL certificates
    ssl_certificate /etc/letsencrypt/live/api.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.yourdomain.com/privkey.pem;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;

    # Backend API
    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket support
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

3. Enable site and obtain SSL certificates:

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/operator-demo /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Obtain SSL certificates
sudo certbot --nginx -d yourdomain.com -d api.yourdomain.com

# Reload Nginx
sudo systemctl reload nginx
```

#### Option B: Using Traefik (Advanced)

Use the provided Traefik configuration:

```bash
docker compose -f docker-compose.hetzner.yml -f docker-compose.traefik.yml up -d
```

Update `docker-compose.traefik.yml` with your domain names before deploying.

---

## Configuration

### Firewall Setup (UFW)

Configure firewall rules:

```bash
# Reset firewall (if needed)
sudo ufw --force reset

# Default policies
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Allow SSH (IMPORTANT - do this first!)
sudo ufw allow 22/tcp

# Allow HTTP and HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Enable firewall
sudo ufw enable

# Check status
sudo ufw status verbose
```

### Hetzner Cloud Firewall (Recommended)

In addition to UFW, configure Hetzner Cloud Firewall:

1. Go to Hetzner Cloud Console
2. Navigate to **Firewalls**
3. Create new firewall with rules:

**Inbound Rules:**
- SSH (22) - Your IP only (for security)
- HTTP (80) - 0.0.0.0/0
- HTTPS (443) - 0.0.0.0/0

**Outbound Rules:**
- Allow all

4. Apply firewall to your server

---

## Security Setup

### 1. SSH Hardening

Edit SSH configuration:

```bash
sudo nano /etc/ssh/sshd_config
```

Recommended settings:

```bash
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes
X11Forwarding no
MaxAuthTries 3
```

Restart SSH:

```bash
sudo systemctl restart sshd
```

### 2. Install Fail2Ban

Protect against brute force attacks:

```bash
sudo apt install -y fail2ban

# Configure
sudo nano /etc/fail2ban/jail.local
```

Add:

```ini
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5

[sshd]
enabled = true
port = 22
```

Start Fail2Ban:

```bash
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

### 3. Regular Security Updates

Set up automatic security updates:

```bash
sudo apt install -y unattended-upgrades
sudo dpkg-reconfigure --priority=low unattended-upgrades
```

---

## Monitoring & Maintenance

### View Logs

```bash
# All services
./scripts/deploy-hetzner.sh logs

# Specific service
./scripts/deploy-hetzner.sh logs backend
./scripts/deploy-hetzner.sh logs frontend
```

### Check Service Status

```bash
./scripts/deploy-hetzner.sh status
```

### Update Application

```bash
# Pull latest code and deploy
./scripts/deploy-hetzner.sh deploy
```

### Restart Services

```bash
./scripts/deploy-hetzner.sh restart
```

### Database Backups

```bash
# Create manual backup
./scripts/deploy-hetzner.sh backup

# Backups are stored in ./backups/ directory
# Automatic cleanup keeps last 30 days
```

### Set Up Automated Backups

Add to crontab:

```bash
crontab -e
```

Add these lines:

```bash
# Daily backup at 2 AM
0 2 * * * cd /opt/operator-demo && ./scripts/deploy-hetzner.sh backup

# Weekly cleanup at 3 AM Sunday
0 3 * * 0 cd /opt/operator-demo && ./scripts/deploy-hetzner.sh cleanup
```

### Resource Monitoring

Check Docker resource usage:

```bash
docker stats
```

Check server resources:

```bash
htop
```

Check disk space:

```bash
df -h
```

---

## Troubleshooting

### Services Won't Start

```bash
# Check Docker status
sudo systemctl status docker

# Check logs for specific service
docker compose -f docker-compose.hetzner.yml logs backend

# Try restarting
./scripts/deploy-hetzner.sh restart
```

### Database Connection Issues

```bash
# Check PostgreSQL logs
docker compose -f docker-compose.hetzner.yml logs postgres

# Verify database is accessible
docker compose -f docker-compose.hetzner.yml exec postgres psql -U postgres -d operator_demo

# Check DATABASE_URL in .env.production
```

### Port Already in Use

```bash
# Find process using port
sudo lsof -i :8000

# Kill process if needed
sudo kill -9 <PID>
```

### Out of Disk Space

```bash
# Check disk usage
df -h

# Clean up Docker
./scripts/deploy-hetzner.sh cleanup

# Remove old logs
sudo journalctl --vacuum-time=7d
```

### SSL Certificate Issues

```bash
# Test certificate renewal
sudo certbot renew --dry-run

# Force renewal
sudo certbot renew --force-renewal

# Check certificate expiry
openssl x509 -in /etc/letsencrypt/live/yourdomain.com/cert.pem -noout -dates
```

---

## Backup & Recovery

### Manual Backup

```bash
./scripts/deploy-hetzner.sh backup
```

### Restore from Backup

```bash
# List available backups
ls -lh backups/

# Restore specific backup
gunzip < backups/backup_20251113_020000.sql.gz | \
  docker compose -f docker-compose.hetzner.yml exec -T postgres \
  psql -U postgres -d operator_demo
```

### Full Server Backup

Use Hetzner's backup feature or create a snapshot:

```bash
# Install Hetzner CLI (optional)
wget https://github.com/hetznercloud/cli/releases/latest/download/hcloud-linux-amd64.tar.gz
tar -xvf hcloud-linux-amd64.tar.gz
sudo mv hcloud /usr/local/bin/

# Create snapshot
hcloud server create-image --type snapshot --description "operator-demo-backup-$(date +%Y%m%d)" <server-id>
```

---

## Performance Optimization

### Docker Resource Limits

The `docker-compose.hetzner.yml` file already includes resource limits optimized for Hetzner servers. Adjust if needed based on your server size.

### PostgreSQL Tuning

The configuration includes optimized PostgreSQL settings for the recommended server specs. For larger servers, you may want to increase:

- `shared_buffers`
- `effective_cache_size`
- `max_connections`

### Enable Monitoring (Optional)

Consider adding Prometheus and Grafana for detailed monitoring. The project includes monitoring configuration:

```bash
docker compose -f docker-compose.hetzner.yml -f docker-compose.monitoring.yml up -d
```

---

## Cost Optimization

### Hetzner Cost Estimates

**Monthly costs:**
- CX31 Server: €12.60
- 80 GB SSD: Included
- Backups (optional): +20% = €2.52
- Traffic: Unlimited (20TB included)
- **Total: ~€15/month**

### Reducing Costs

1. **Use Snapshots instead of Backups:** One-time cost vs monthly
2. **Shared resources:** Host multiple projects on one server
3. **Auto-scaling:** Start small, scale up as needed
4. **Use Hetzner Volumes:** Separate storage for cost-effective scaling

---

## Support & Resources

### Documentation

- [Main README](./README.md)
- [General Deployment Guide](./DEPLOYMENT.md)
- [API Documentation](./API_DOCUMENTATION.md)
- [Security Documentation](./SECURITY_DOCUMENTATION_COMPLETE.md)

### Getting Help

- Check logs: `./scripts/deploy-hetzner.sh logs`
- Review status: `./scripts/deploy-hetzner.sh status`
- GitHub Issues: https://github.com/m-check1B/cc-lite-2026/issues

### Useful Commands Reference

```bash
# Deployment
./scripts/deploy-hetzner.sh init      # Initial setup
./scripts/deploy-hetzner.sh deploy    # Update deployment
./scripts/deploy-hetzner.sh restart   # Restart services
./scripts/deploy-hetzner.sh status    # Check status

# Maintenance
./scripts/deploy-hetzner.sh backup    # Create backup
./scripts/deploy-hetzner.sh logs      # View logs
./scripts/deploy-hetzner.sh cleanup   # Clean up resources

# Docker
docker compose -f docker-compose.hetzner.yml ps              # List services
docker compose -f docker-compose.hetzner.yml exec backend sh # Access backend shell
docker compose -f docker-compose.hetzner.yml down            # Stop all services
```

---

## Production Checklist

Before going live, verify:

- [ ] Server is properly configured with adequate resources
- [ ] Firewall rules are set up correctly
- [ ] SSL certificates are installed and auto-renewal is configured
- [ ] All environment variables in `.env.production` are set
- [ ] Strong passwords generated for POSTGRES_PASSWORD, REDIS_PASSWORD, SECRET_KEY
- [ ] Database migrations have run successfully
- [ ] Initial admin user is created
- [ ] Automated backups are configured
- [ ] Monitoring is set up (optional but recommended)
- [ ] Domain DNS is pointing to server IP
- [ ] Health checks are passing
- [ ] Security updates are enabled
- [ ] Fail2Ban is configured
- [ ] SSH is hardened (no root login, key-based auth only)
- [ ] API keys for required services are added
- [ ] Test deployment with small load
- [ ] Rollback plan is documented

---

**Deployment Guide Version:** 1.0.0
**Last Updated:** November 13, 2025
**Maintained By:** Operator Demo 2026 Team

For questions or issues, please open a GitHub issue or consult the main documentation.
