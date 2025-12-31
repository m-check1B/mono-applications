# Voice by Kraliki Production Deployment Guide

> **Complete Step-by-Step Production Deployment with Docker**

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Deployment (Docker)](#quick-deployment-docker)
3. [Environment Configuration](#environment-configuration)
4. [Database Setup](#database-setup)
5. [SSL/TLS Configuration](#ssltls-configuration)
6. [Production Deployment](#production-deployment)
7. [Monitoring Setup](#monitoring-setup)
8. [Backup & Recovery](#backup--recovery)
9. [Scaling & Load Balancing](#scaling--load-balancing)
10. [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements

**Minimum Configuration:**
- **CPU**: 2 vCPU
- **RAM**: 4GB
- **Storage**: 50GB SSD
- **Network**: 100 Mbps
- **OS**: Ubuntu 20.04 LTS or CentOS 8

**Recommended for Production:**
- **CPU**: 4 vCPU
- **RAM**: 8GB
- **Storage**: 100GB SSD
- **Network**: 1 Gbps
- **OS**: Ubuntu 22.04 LTS

### Required Software

```bash
# Install Docker and Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker compose
sudo chmod +x /usr/local/bin/docker compose

# Install Node.js (for local development)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install pnpm
npm install -g pnpm
```

### Domain & SSL Requirements

- **Domain Name**: Point to your server IP
- **SSL Certificate**: Let's Encrypt or commercial certificate
- **Firewall**: Configure ports 80, 443, and custom application ports

## Quick Deployment (Docker)

### 1. Clone Repository

```bash
# Clone the repository
git clone https://github.com/your-org/cc-lite.git
cd cc-lite

# Switch to production branch if applicable
git checkout main
```

### 2. Environment Setup

```bash
# Copy environment template
cp .env.template .env.production

# Generate secure secrets
./scripts/generate-secrets.sh

# Edit environment file
nano .env.production
```

### 3. One-Command Deployment

```bash
# Deploy with Docker Compose
docker compose -f infra/docker/production.yml up -d

# Check deployment status
docker compose -f infra/docker/production.yml ps
```

### 4. Verify Deployment

```bash
# Check application health
curl http://localhost:3010/health

# Check logs
docker compose -f infra/docker/production.yml logs -f app
```

## Environment Configuration

### Production Environment File

Create `.env.production` with the following configuration:

```bash
# ===== CORE CONFIGURATION =====
NODE_ENV=production
PORT=3010
HOST=0.0.0.0

# ===== DATABASE CONFIGURATION =====
DATABASE_URL=postgresql://cc_lite_user:CHANGE_ME_DB_PASSWORD@postgres:5432/cc_lite_production
DB_HOST=postgres
DB_PORT=5432
DB_NAME=cc_lite_production
DB_USER=cc_lite_user
DB_PASSWORD=CHANGE_ME_DB_PASSWORD

# ===== AUTHENTICATION SECRETS =====
JWT_SECRET=CHANGE_ME_JWT_SECRET_64_CHARS_MINIMUM
COOKIE_SECRET=CHANGE_ME_COOKIE_SECRET_32_CHARS_MINIMUM
AUTH_ENCRYPTION_KEY=CHANGE_ME_ENCRYPTION_KEY_32_CHARS

# ===== REDIS CONFIGURATION =====
REDIS_URL=redis://redis:6379
REDIS_HOST=redis
REDIS_PORT=6379

# ===== TELEPHONY CONFIGURATION =====
TELEPHONY_PROVIDER=twilio
TELEPHONY_ENABLED=true

# Twilio Configuration
TWILIO_ACCOUNT_SID=CHANGE_ME_TWILIO_ACCOUNT_SID
TWILIO_AUTH_TOKEN=CHANGE_ME_TWILIO_AUTH_TOKEN
TWILIO_PHONE_NUMBER=CHANGE_ME_TWILIO_PHONE_NUMBER

# Telnyx Configuration (Alternative)
TELNYX_API_KEY=CHANGE_ME_TELNYX_API_KEY
TELNYX_PHONE_NUMBER=CHANGE_ME_TELNYX_PHONE_NUMBER

# ===== AI SERVICES =====
OPENAI_API_KEY=CHANGE_ME_OPENAI_API_KEY
DEEPGRAM_API_KEY=CHANGE_ME_DEEPGRAM_API_KEY
ELEVENLABS_API_KEY=CHANGE_ME_ELEVENLABS_API_KEY

# ===== PRODUCTION SETTINGS =====
SEED_DEMO_USERS=false
ENABLE_DEBUG_LOGGING=false
LOG_LEVEL=info
METRICS_ENABLED=true
TRACING_ENABLED=true

# ===== FRONTEND CONFIGURATION =====
FRONTEND_URL=https://your-domain.com
BACKEND_URL=https://api.your-domain.com

# ===== EMAIL CONFIGURATION =====
SMTP_HOST=CHANGE_ME_SMTP_HOST
SMTP_PORT=587
SMTP_USER=CHANGE_ME_SMTP_USER
SMTP_PASSWORD=CHANGE_ME_SMTP_PASSWORD
FROM_EMAIL=noreply@your-domain.com

# ===== MONITORING =====
SENTRY_DSN=CHANGE_ME_SENTRY_DSN
PROMETHEUS_ENABLED=true
GRAFANA_ENABLED=true

# ===== SECURITY =====
ALLOWED_ORIGINS=https://your-domain.com,https://app.your-domain.com
CORS_ENABLED=true
RATE_LIMIT_ENABLED=true
WEBHOOK_SECRET=CHANGE_ME_WEBHOOK_SECRET
```

### Secret Generation Script

Create `scripts/generate-secrets.sh`:

```bash
#!/bin/bash

echo "Generating secure secrets for Voice by Kraliki production..."

# Generate JWT secret (64 characters)
JWT_SECRET=$(openssl rand -base64 48)

# Generate cookie secret (32 characters)
COOKIE_SECRET=$(openssl rand -base64 24)

# Generate encryption key (32 characters)
ENCRYPTION_KEY=$(openssl rand -hex 32)

# Generate database password
DB_PASSWORD=$(openssl rand -base64 24 | tr -d "=+/" | cut -c1-20)

# Generate webhook secret
WEBHOOK_SECRET=$(openssl rand -base64 32)

echo "Generated secrets:"
echo "JWT_SECRET=$JWT_SECRET"
echo "COOKIE_SECRET=$COOKIE_SECRET"
echo "AUTH_ENCRYPTION_KEY=$ENCRYPTION_KEY"
echo "DB_PASSWORD=$DB_PASSWORD"
echo "WEBHOOK_SECRET=$WEBHOOK_SECRET"

echo ""
echo "Copy these values to your .env.production file"
```

## Database Setup

### PostgreSQL Configuration

Create `config/postgres.conf`:

```conf
# PostgreSQL configuration for Voice by Kraliki production

# Connection settings
listen_addresses = '*'
port = 5432
max_connections = 200

# Memory settings
shared_buffers = 256MB
effective_cache_size = 1GB
work_mem = 4MB
maintenance_work_mem = 64MB

# Checkpoint settings
checkpoint_completion_target = 0.7
wal_buffers = 16MB

# Logging
log_statement = 'mod'
log_min_duration_statement = 1000
log_line_prefix = '%t [%p]: [%l-1] user=%u,db=%d,app=%a,client=%h '

# Performance
random_page_cost = 1.1
effective_io_concurrency = 200
```

### Database Initialization

```sql
-- Create production database and user
CREATE USER cc_lite_user WITH PASSWORD 'your_secure_password';
CREATE DATABASE cc_lite_production OWNER cc_lite_user;

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE cc_lite_production TO cc_lite_user;

-- Enable extensions
\c cc_lite_production;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- Performance indexes
CREATE INDEX CONCURRENTLY idx_calls_status_created ON calls(status, created_at);
CREATE INDEX CONCURRENTLY idx_agents_status_active ON agents(status) WHERE status != 'OFFLINE';
CREATE INDEX CONCURRENTLY idx_transcripts_call_timestamp ON transcripts(call_id, timestamp DESC);
```

### Database Migration

```bash
# Run database migrations
docker compose -f infra/docker/production.yml exec app pnpm prisma migrate deploy

# Seed initial data (production-safe)
docker compose -f infra/docker/production.yml exec app pnpm prisma db seed
```

## SSL/TLS Configuration

### Let's Encrypt with Certbot

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com -d api.your-domain.com

# Auto-renewal setup
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

### Nginx Configuration

Create `nginx/production.conf`:

```nginx
# Voice by Kraliki Production Nginx Configuration

upstream cc_lite_backend {
    server app:3010 max_fails=3 fail_timeout=30s;
    keepalive 32;
}

# HTTP to HTTPS redirect
server {
    listen 80;
    server_name your-domain.com api.your-domain.com;
    return 301 https://$server_name$request_uri;
}

# Main application server
server {
    listen 443 ssl http2;
    server_name your-domain.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    # Frontend static files
    location / {
        try_files $uri $uri/ /index.html;
        root /var/www/cc-lite/dist;
        expires 1d;
        add_header Cache-Control "public, immutable";
    }

    # API proxy
    location /api/ {
        proxy_pass http://cc_lite_backend/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        proxy_read_timeout 86400;
    }

    # tRPC endpoint
    location /trpc/ {
        proxy_pass http://cc_lite_backend/trpc/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }

    # WebSocket support
    location /socket.io/ {
        proxy_pass http://cc_lite_backend/socket.io/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Health check
    location /health {
        proxy_pass http://cc_lite_backend/health;
        access_log off;
    }
}
```

## Production Deployment

### Docker Compose Production

Create `infra/docker/production.yml`:

```yaml
version: '3.8'

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile.production
    restart: unless-stopped
    environment:
      - NODE_ENV=production
    env_file:
      - .env.production
    ports:
      - "3010:3010"
    depends_on:
      - postgres
      - redis
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3010/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s
    volumes:
      - ./uploads:/app/uploads
      - ./logs:/app/logs
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
        reservations:
          cpus: '0.5'
          memory: 512M

  postgres:
    image: postgres:15-alpine
    restart: unless-stopped
    environment:
      - POSTGRES_DB=cc_lite_production
      - POSTGRES_USER=cc_lite_user
      - POSTGRES_PASSWORD=${DB_PASSWORD}
      - POSTGRES_INITDB_ARGS="--encoding=UTF-8 --lc-collate=C --lc-ctype=C"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./config/postgres.conf:/etc/postgresql/postgresql.conf
      - ./backups:/backups
    ports:
      - "127.0.0.1:5432:5432"
    command: postgres -c config_file=/etc/postgresql/postgresql.conf
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U cc_lite_user -d cc_lite_production"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    restart: unless-stopped
    command: redis-server --appendonly yes --maxmemory 256mb --maxmemory-policy allkeys-lru
    volumes:
      - redis_data:/data
    ports:
      - "127.0.0.1:6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 3

  nginx:
    image: nginx:alpine
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/production.conf:/etc/nginx/conf.d/default.conf
      - ./dist:/var/www/cc-lite/dist:ro
      - /etc/letsencrypt:/etc/letsencrypt:ro
    depends_on:
      - app
    healthcheck:
      test: ["CMD", "wget", "--quiet", "--tries=1", "--spider", "http://localhost/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  prometheus:
    image: prom/prometheus:latest
    restart: unless-stopped
    ports:
      - "127.0.0.1:9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--web.enable-lifecycle'

  grafana:
    image: grafana/grafana:latest
    restart: unless-stopped
    ports:
      - "127.0.0.1:3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD:-admin}
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/grafana:/etc/grafana/provisioning

volumes:
  postgres_data:
  redis_data:
  prometheus_data:
  grafana_data:

networks:
  default:
    driver: bridge
```

### Production Dockerfile

Create `Dockerfile.production`:

```dockerfile
# Multi-stage production build

# Stage 1: Build frontend
FROM node:18-alpine AS frontend-builder
WORKDIR /app
COPY package.json pnpm-lock.yaml ./
RUN npm install -g pnpm
RUN pnpm install --frozen-lockfile
COPY . .
RUN pnpm build

# Stage 2: Build backend
FROM node:18-alpine AS backend-builder
WORKDIR /app
COPY package.json pnpm-lock.yaml ./
RUN npm install -g pnpm
RUN pnpm install --frozen-lockfile --prod

# Stage 3: Production runtime
FROM node:18-alpine AS production

# Install system dependencies
RUN apk add --no-cache \
    curl \
    postgresql-client \
    redis \
    pm2

# Create app user
RUN addgroup -g 1001 -S nodejs
RUN adduser -S cc-lite -u 1001

WORKDIR /app

# Copy built applications
COPY --from=frontend-builder --chown=cc-lite:nodejs /app/dist ./dist
COPY --from=backend-builder --chown=cc-lite:nodejs /app/node_modules ./node_modules
COPY --from=backend-builder --chown=cc-lite:nodejs /app/server ./server
COPY --from=backend-builder --chown=cc-lite:nodejs /app/prisma ./prisma

# Copy configuration files
COPY --chown=cc-lite:nodejs ecosystem.config.js ./
COPY --chown=cc-lite:nodejs package.json ./

# Create necessary directories
RUN mkdir -p uploads logs
RUN chown -R cc-lite:nodejs uploads logs

# Switch to non-root user
USER cc-lite

# Expose port
EXPOSE 3010

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:3010/health || exit 1

# Start application with PM2
CMD ["pm2-runtime", "start", "ecosystem.config.js"]
```

### PM2 Ecosystem Configuration

Create `ecosystem.config.js`:

```javascript
module.exports = {
  apps: [
    {
      name: 'cc-lite-production',
      script: 'server/index.js',
      instances: 'max',
      exec_mode: 'cluster',
      env: {
        NODE_ENV: 'production',
        PORT: 3010
      },
      error_file: './logs/pm2-error.log',
      out_file: './logs/pm2-out.log',
      log_file: './logs/pm2-combined.log',
      time: true,
      max_memory_restart: '1G',
      node_args: '--max-old-space-size=1024',
      kill_timeout: 3000,
      wait_ready: true,
      listen_timeout: 10000,
      restart_delay: 4000,
      max_restarts: 10,
      min_uptime: '10s'
    }
  ]
};
```

## Monitoring Setup

### Prometheus Configuration

Create `monitoring/prometheus.yml`:

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "alert_rules.yml"

scrape_configs:
  - job_name: 'cc-lite'
    static_configs:
      - targets: ['app:3010']
    metrics_path: '/metrics'
    scrape_interval: 15s

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres:5432']

  - job_name: 'redis'
    static_configs:
      - targets: ['redis:6379']

  - job_name: 'nginx'
    static_configs:
      - targets: ['nginx:80']
```

### Grafana Dashboard

Create `monitoring/grafana/dashboards/cc-lite.json`:

```json
{
  "dashboard": {
    "id": null,
    "title": "Voice by Kraliki Production Dashboard",
    "tags": ["cc-lite"],
    "timezone": "browser",
    "panels": [
      {
        "title": "Active Calls",
        "type": "stat",
        "targets": [
          {
            "expr": "cc_lite_active_calls_total",
            "legendFormat": "Active Calls"
          }
        ]
      },
      {
        "title": "Call Volume",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(cc_lite_calls_total[5m])",
            "legendFormat": "Calls/sec"
          }
        ]
      }
    ]
  }
}
```

## Backup & Recovery

### Automated Backup Script

Create `scripts/backup.sh`:

```bash
#!/bin/bash

BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="cc_lite_production"
DB_USER="cc_lite_user"

# Create backup directory
mkdir -p $BACKUP_DIR

# Database backup
docker compose exec -T postgres pg_dump -U $DB_USER -d $DB_NAME | gzip > $BACKUP_DIR/db_backup_$DATE.sql.gz

# Application files backup
tar -czf $BACKUP_DIR/uploads_backup_$DATE.tar.gz uploads/

# Configuration backup
tar -czf $BACKUP_DIR/config_backup_$DATE.tar.gz \
  .env.production \
  infra/docker/production.yml \
  nginx/ \
  monitoring/

# Clean old backups (keep 30 days)
find $BACKUP_DIR -name "*.gz" -mtime +30 -delete

echo "Backup completed: $DATE"
```

### Recovery Script

Create `scripts/restore.sh`:

```bash
#!/bin/bash

BACKUP_FILE=$1
if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: $0 <backup_file>"
    exit 1
fi

# Stop application
docker compose -f infra/docker/production.yml down

# Restore database
gunzip -c $BACKUP_FILE | docker compose exec -T postgres psql -U cc_lite_user -d cc_lite_production

# Restart application
docker compose -f infra/docker/production.yml up -d

echo "Restore completed"
```

### Backup Cron Job

```bash
# Add to crontab
0 2 * * * /path/to/cc-lite/scripts/backup.sh
```

## Scaling & Load Balancing

### Multiple App Instances

Update `infra/docker/production.yml`:

```yaml
services:
  app1:
    <<: *app-common
    container_name: cc-lite-app-1

  app2:
    <<: *app-common
    container_name: cc-lite-app-2

  app3:
    <<: *app-common
    container_name: cc-lite-app-3

  nginx:
    # Update upstream configuration
    volumes:
      - ./nginx/load-balancer.conf:/etc/nginx/conf.d/default.conf
```

### Load Balancer Configuration

Create `nginx/load-balancer.conf`:

```nginx
upstream cc_lite_cluster {
    least_conn;
    server app1:3010 max_fails=3 fail_timeout=30s;
    server app2:3010 max_fails=3 fail_timeout=30s;
    server app3:3010 max_fails=3 fail_timeout=30s;
    keepalive 32;
}

# Sticky sessions for WebSocket
map $http_upgrade $connection_upgrade {
    default upgrade;
    '' close;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    # WebSocket with sticky sessions
    location /socket.io/ {
        proxy_pass http://cc_lite_cluster;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection $connection_upgrade;
        ip_hash; # Ensure sticky sessions
    }

    # API load balancing
    location /api/ {
        proxy_pass http://cc_lite_cluster;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Troubleshooting

### Common Issues

**Issue: Application won't start**
```bash
# Check logs
docker compose -f infra/docker/production.yml logs app

# Check environment variables
docker compose -f infra/docker/production.yml exec app env | grep -E "(DATABASE|JWT|TWILIO)"

# Verify database connection
docker compose -f infra/docker/production.yml exec app npx prisma db push --preview-feature
```

**Issue: Database connection failed**
```bash
# Check PostgreSQL status
docker compose -f infra/docker/production.yml exec postgres pg_isready

# Test connection
docker compose -f infra/docker/production.yml exec postgres psql -U cc_lite_user -d cc_lite_production -c "SELECT 1;"

# Check network connectivity
docker compose -f infra/docker/production.yml exec app nc -zv postgres 5432
```

**Issue: SSL certificate problems**
```bash
# Check certificate validity
openssl x509 -in /etc/letsencrypt/live/your-domain.com/fullchain.pem -text -noout

# Renew certificate
sudo certbot renew --force-renewal

# Test SSL configuration
curl -I https://your-domain.com
```

### Health Checks

```bash
# Application health
curl -f http://localhost:3010/health

# Database health
docker compose -f infra/docker/production.yml exec postgres pg_isready

# Redis health
docker compose -f infra/docker/production.yml exec redis redis-cli ping

# Full system check
./scripts/health-check.sh
```

### Log Analysis

```bash
# Application logs
docker compose -f infra/docker/production.yml logs -f app

# Error logs only
docker compose -f infra/docker/production.yml logs app | grep ERROR

# Performance logs
docker compose -f infra/docker/production.yml exec app pm2 logs

# System logs
journalctl -u docker -f
```

This deployment guide ensures a production-ready Voice by Kraliki installation with proper security, monitoring, and scalability considerations.