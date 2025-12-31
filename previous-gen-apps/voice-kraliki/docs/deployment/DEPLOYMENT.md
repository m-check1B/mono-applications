# CC-Lite 2026 - Deployment Guide

**Version:** 2.0.0
**Last Updated:** November 11, 2025
**Target Environments:** Development, Staging, Production

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Configuration](#environment-configuration)
3. [Development Deployment](#development-deployment)
4. [Docker Deployment](#docker-deployment)
5. [Production Deployment](#production-deployment)
6. [SSL/TLS Configuration](#ssltls-configuration)
7. [Database Setup](#database-setup)
8. [Monitoring Setup](#monitoring-setup)
9. [Backup & Recovery](#backup--recovery)
10. [Troubleshooting](#troubleshooting)

## Prerequisites

### Required Software
- **Docker:** 20.10+ with Docker Compose v2
- **Node.js:** 20+ (for local frontend development)
- **Python:** 3.11+ (for local backend development)
- **PostgreSQL:** 14+ (if not using Docker)
- **Redis:** 7+ (for caching, optional)
- **Qdrant:** 1.7+ (for vector search)

### System Requirements

#### Minimum (Development)
- CPU: 2 cores
- RAM: 4GB
- Disk: 20GB

#### Recommended (Production)
- CPU: 4+ cores
- RAM: 8GB+
- Disk: 100GB+ (SSD recommended)
- Network: 100Mbps+

## Environment Configuration

### Environment Variables

Create `.env` file in the project root:

```bash
# Database Configuration
DATABASE_URL=postgresql://postgres:password@localhost:5432/operator_demo
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_secure_password_here
POSTGRES_DB=operator_demo

# Redis Configuration (Optional)
REDIS_URL=redis://localhost:6379/0

# Qdrant Vector Database
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=  # Optional, for production

# JWT & Security
JWT_SECRET=your_jwt_secret_key_minimum_32_characters
SECRET_KEY=your_secret_key_minimum_32_characters
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# API Keys - Voice AI Providers
OPENAI_API_KEY=sk-proj-...
GEMINI_API_KEY=AIzaSy...
DEEPGRAM_API_KEY=...

# Telephony Providers
TWILIO_ACCOUNT_SID=ACa75fdadde...
TWILIO_AUTH_TOKEN=...
TWILIO_PHONE_NUMBER_US=+1...
TELNYX_API_KEY=...
TELNYX_PUBLIC_KEY=...

# Application Settings
DEBUG=false
LOG_LEVEL=info
ALLOWED_ORIGINS=http://localhost:3000,https://yourdomain.com

# CORS Settings
CORS_ALLOW_CREDENTIALS=true
CORS_ALLOW_METHODS=GET,POST,PUT,DELETE,OPTIONS
CORS_ALLOW_HEADERS=*

# File Upload
MAX_UPLOAD_SIZE=10485760  # 10MB in bytes
UPLOAD_DIR=/app/uploads

# Email Configuration (Optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password
SMTP_FROM=noreply@yourdomain.com
```

### Environment-Specific Configurations

#### Development (.env.development)
```bash
DEBUG=true
LOG_LEVEL=debug
DATABASE_URL=postgresql://postgres:password@localhost:5432/operator_demo
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
```

#### Staging (.env.staging)
```bash
DEBUG=false
LOG_LEVEL=info
DATABASE_URL=postgresql://user:password@staging-db:5432/cc_lite_staging
ALLOWED_ORIGINS=https://staging.yourdomain.com
```

#### Production (.env.production)
```bash
DEBUG=false
LOG_LEVEL=warning
DATABASE_URL=postgresql://user:secure_password@prod-db:5432/cc_lite_prod
ALLOWED_ORIGINS=https://yourdomain.com
JWT_SECRET=<64-character-random-string>
SECRET_KEY=<64-character-random-string>
```

## Development Deployment

### Option 1: Local Development (Without Docker)

#### Backend Setup
```bash
# 1. Navigate to backend directory
cd backend

# 2. Install dependencies using uv
uv sync

# 3. Setup database
# Make sure PostgreSQL is running
createdb operator_demo

# 4. Run migrations
uv run alembic upgrade head

# 5. Create initial user (optional)
uv run python -m app.scripts.create_admin

# 6. Start development server
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Backend will be available at http://localhost:8000
# API docs at http://localhost:8000/docs
```

#### Frontend Setup
```bash
# 1. Navigate to frontend directory
cd frontend

# 2. Install dependencies
pnpm install

# 3. Start development server
pnpm dev

# Frontend will be available at http://localhost:3000
```

### Option 2: Docker Development

```bash
# 1. Start all services with docker-compose
docker compose up -d

# 2. Check service status
docker compose ps

# 3. View logs
docker compose logs -f

# 4. Stop services
docker compose down

# Services:
# - Backend: http://localhost:8000
# - Frontend: http://localhost:3000
# - PostgreSQL: localhost:5432
# - Redis: localhost:6379
# - Qdrant: http://localhost:6333
```

## Docker Deployment

### Production Docker Setup

#### 1. Prepare Environment
```bash
# Copy and configure environment file
cp .env.example .env
nano .env  # Edit with production values
```

#### 2. Build Images
```bash
# Build production images
docker compose -f docker-compose.prod.yml build

# Or build specific service
docker compose -f docker-compose.prod.yml build backend
```

#### 3. Database Initialization
```bash
# Run migrations
docker compose -f docker-compose.prod.yml run --rm backend \
  alembic upgrade head

# Create admin user
docker compose -f docker-compose.prod.yml run --rm backend \
  python -m app.scripts.create_admin
```

#### 4. Start Services
```bash
# Start all services
docker compose -f docker-compose.prod.yml up -d

# Check health
docker compose -f docker-compose.prod.yml ps

# View logs
docker compose -f docker-compose.prod.yml logs -f backend
```

### Docker Compose Configuration

**docker-compose.prod.yml** (example):
```yaml
version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.prod
    container_name: cc-lite-backend
    restart: unless-stopped
    env_file: .env
    ports:
      - "8000:8000"
    depends_on:
      - db
      - redis
      - qdrant
    volumes:
      - ./backend/uploads:/app/uploads
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.prod
    container_name: cc-lite-frontend
    restart: unless-stopped
    ports:
      - "3000:3000"
    depends_on:
      - backend
    environment:
      - PUBLIC_API_URL=http://backend:8000
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 1G

  db:
    image: postgres:15-alpine
    container_name: cc-lite-db
    restart: unless-stopped
    env_file: .env
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U $POSTGRES_USER"]
      interval: 10s
      timeout: 5s
      retries: 5
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G

  redis:
    image: redis:7-alpine
    container_name: cc-lite-redis
    restart: unless-stopped
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 5

  qdrant:
    image: qdrant/qdrant:v1.7.0
    container_name: cc-lite-qdrant
    restart: unless-stopped
    ports:
      - "6333:6333"
      - "6334:6334"
    volumes:
      - qdrant_data:/qdrant/storage
    environment:
      - QDRANT__SERVICE__GRPC_PORT=6334

volumes:
  postgres_data:
  redis_data:
  qdrant_data:
```

## Production Deployment

### Deployment with Traefik Reverse Proxy

#### 1. Install Traefik
```bash
# Create Traefik network
docker network create traefik

# Deploy Traefik
docker compose -f traefik-docker-compose.yml up -d
```

#### 2. Configure Domain & SSL
```yaml
# Add to docker-compose.prod.yml
labels:
  - "traefik.enable=true"
  - "traefik.http.routers.backend.rule=Host(`api.yourdomain.com`)"
  - "traefik.http.routers.backend.entrypoints=websecure"
  - "traefik.http.routers.backend.tls.certresolver=letsencrypt"
  - "traefik.http.services.backend.loadbalancer.server.port=8000"
```

#### 3. Deploy Application
```bash
# Deploy with Traefik labels
docker compose -f docker-compose.prod.yml -f docker-compose.traefik.yml up -d

# Verify SSL certificates
curl https://api.yourdomain.com/health
```

### Manual Server Deployment

#### 1. Server Preparation
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y python3.11 python3.11-venv postgresql-14 nginx redis-server

# Install Node.js 20
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# Install Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
```

#### 2. Application Setup
```bash
# Clone repository
git clone <repository-url> /opt/cc-lite-2026
cd /opt/cc-lite-2026

# Setup environment
cp .env.example .env
nano .env  # Configure production settings

# Build and start services
docker compose -f docker-compose.prod.yml up -d
```

#### 3. Nginx Configuration
```nginx
# /etc/nginx/sites-available/cc-lite

upstream backend {
    server localhost:8000;
}

upstream frontend {
    server localhost:3000;
}

server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # Frontend
    location / {
        proxy_pass http://frontend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # Backend API
    location /api {
        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket support
    location /ws {
        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}

server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/api.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.yourdomain.com/privkey.pem;

    location / {
        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/cc-lite /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## SSL/TLS Configuration

### Let's Encrypt with Certbot

```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d yourdomain.com -d api.yourdomain.com

# Test renewal
sudo certbot renew --dry-run

# Auto-renewal (already configured by certbot)
sudo systemctl status certbot.timer
```

### SSL with Traefik (Automatic)

Traefik automatically handles SSL certificates with Let's Encrypt:

```yaml
# traefik.yml
certificatesResolvers:
  letsencrypt:
    acme:
      email: admin@yourdomain.com
      storage: /letsencrypt/acme.json
      tlsChallenge: {}
```

## Database Setup

### PostgreSQL Production Setup

#### 1. Configuration
```bash
# Edit PostgreSQL config
sudo nano /etc/postgresql/14/main/postgresql.conf

# Recommended settings
shared_buffers = 2GB
effective_cache_size = 6GB
maintenance_work_mem = 512MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
work_mem = 10MB
min_wal_size = 1GB
max_wal_size = 4GB
max_worker_processes = 4
max_parallel_workers_per_gather = 2
max_parallel_workers = 4
max_parallel_maintenance_workers = 2
```

#### 2. Create Database and User
```sql
-- Connect as postgres user
sudo -u postgres psql

-- Create database and user
CREATE DATABASE cc_lite_prod;
CREATE USER cc_lite_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE cc_lite_prod TO cc_lite_user;

-- Enable extensions
\c cc_lite_prod
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

\q
```

#### 3. Run Migrations
```bash
cd /opt/cc-lite-2026/backend
uv run alembic upgrade head
```

### Database Optimization

```sql
-- Create essential indexes
CREATE INDEX CONCURRENTLY idx_campaigns_status ON campaigns(status);
CREATE INDEX CONCURRENTLY idx_campaigns_created_by ON campaigns(created_by_id);
CREATE INDEX CONCURRENTLY idx_contacts_campaign ON contacts(campaign_id);
CREATE INDEX CONCURRENTLY idx_metrics_timestamp ON metrics(timestamp);
CREATE INDEX CONCURRENTLY idx_metrics_type_name ON metrics(metric_type, metric_name);

-- Analyze tables
ANALYZE campaigns;
ANALYZE contacts;
ANALYZE metrics;
ANALYZE agents;
```

## Monitoring Setup

### Application Monitoring

#### Health Check Endpoints
```bash
# Backend health
curl http://localhost:8000/health

# Database health
curl http://localhost:8000/health/db

# Response format
{
  "status": "healthy",
  "version": "2.0.0",
  "timestamp": "2025-11-11T12:00:00Z"
}
```

#### Prometheus Metrics (Optional)
```python
# Add to backend/app/main.py
from prometheus_fastapi_instrumentator import Instrumentator

Instrumentator().instrument(app).expose(app, endpoint="/metrics")
```

### Log Management

#### Application Logs
```bash
# View backend logs
docker compose logs -f backend --tail=100

# View frontend logs
docker compose logs -f frontend --tail=100

# Export logs to file
docker compose logs backend > backend_logs_$(date +%Y%m%d).log
```

#### Log Rotation
```bash
# /etc/logrotate.d/cc-lite
/var/log/cc-lite/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
    sharedscripts
    postrotate
        docker compose restart backend
    endscript
}
```

### Uptime Monitoring

#### Simple Health Check Script
```bash
#!/bin/bash
# /usr/local/bin/cc-lite-health-check.sh

BACKEND_URL="http://localhost:8000/health"
FRONTEND_URL="http://localhost:3000"
ALERT_EMAIL="admin@yourdomain.com"

check_service() {
    local url=$1
    local name=$2

    if ! curl -f -s -o /dev/null "$url"; then
        echo "❌ $name is down!" | mail -s "CC-Lite Alert: $name Down" "$ALERT_EMAIL"
        return 1
    fi
    return 0
}

check_service "$BACKEND_URL" "Backend"
check_service "$FRONTEND_URL" "Frontend"
```

```bash
# Add to crontab
crontab -e
*/5 * * * * /usr/local/bin/cc-lite-health-check.sh
```

## Backup & Recovery

### Automated Database Backups

```bash
#!/bin/bash
# /usr/local/bin/backup-cc-lite-db.sh

BACKUP_DIR="/backups/cc-lite"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/cc_lite_backup_$DATE.sql"
RETENTION_DAYS=30

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Backup database
docker exec cc-lite-db pg_dump -U postgres operator_demo > "$BACKUP_FILE"

# Compress backup
gzip "$BACKUP_FILE"

# Remove old backups
find "$BACKUP_DIR" -name "*.sql.gz" -mtime +$RETENTION_DAYS -delete

echo "Backup completed: ${BACKUP_FILE}.gz"
```

```bash
# Make script executable
chmod +x /usr/local/bin/backup-cc-lite-db.sh

# Schedule daily backups at 2 AM
crontab -e
0 2 * * * /usr/local/bin/backup-cc-lite-db.sh
```

### Database Restore

```bash
# Restore from backup
gunzip < /backups/cc-lite/cc_lite_backup_20251111_020000.sql.gz | \
  docker exec -i cc-lite-db psql -U postgres operator_demo

# Or restore specific backup
docker exec -i cc-lite-db psql -U postgres operator_demo < backup.sql
```

### Application State Backup

```bash
#!/bin/bash
# Backup volumes and configuration

BACKUP_DIR="/backups/cc-lite"
DATE=$(date +%Y%m%d_%H%M%S)

# Backup Docker volumes
docker run --rm \
  -v cc-lite-2026_postgres_data:/data \
  -v $BACKUP_DIR:/backup \
  alpine tar czf /backup/postgres_volume_$DATE.tar.gz /data

# Backup .env and configuration
tar czf "$BACKUP_DIR/config_$DATE.tar.gz" .env docker-compose.prod.yml

echo "Application state backed up"
```

## Troubleshooting

### Common Deployment Issues

#### Port Already in Use
```bash
# Find process using port 8000
lsof -i :8000
# or
netstat -tulpn | grep 8000

# Kill process
kill -9 <PID>
```

#### Database Connection Failures
```bash
# Check if PostgreSQL is running
docker compose ps db

# Test connection
docker exec -it cc-lite-db psql -U postgres -d operator_demo

# Check connection string
echo $DATABASE_URL

# Verify network
docker network ls
docker network inspect <network-name>
```

#### Permission Denied Errors
```bash
# Fix file permissions
sudo chown -R $USER:$USER /opt/cc-lite-2026

# Fix Docker socket permissions
sudo chmod 666 /var/run/docker.sock

# Fix upload directory
sudo chown -R 1000:1000 backend/uploads
```

#### SSL Certificate Issues
```bash
# Check certificate expiry
openssl x509 -in /etc/letsencrypt/live/yourdomain.com/cert.pem -noout -dates

# Renew certificate
sudo certbot renew

# Test SSL configuration
openssl s_client -connect yourdomain.com:443 -servername yourdomain.com
```

#### High Memory Usage
```bash
# Check container resource usage
docker stats

# Limit container memory
# Add to docker-compose.prod.yml
services:
  backend:
    mem_limit: 1g
    memswap_limit: 2g
```

### Performance Tuning

#### Database Optimization
```sql
-- Vacuum and analyze
VACUUM ANALYZE;

-- Check table bloat
SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Rebuild indexes
REINDEX TABLE campaigns;
REINDEX TABLE contacts;
```

#### Application Tuning
```bash
# Increase worker processes (Uvicorn)
uvicorn app.main:app --workers 4 --host 0.0.0.0 --port 8000

# Adjust Gunicorn workers (alternative)
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

## Production Checklist

Before going live, verify:

- [ ] All environment variables are configured securely
- [ ] Database is properly initialized with migrations
- [ ] SSL/TLS certificates are installed and valid
- [ ] CORS origins are properly configured
- [ ] API keys for third-party services are valid
- [ ] Backup system is operational and tested
- [ ] Monitoring and alerting are configured
- [ ] Log rotation is configured
- [ ] Firewall rules are properly set
- [ ] Health checks are passing
- [ ] Load testing completed
- [ ] Security headers are configured
- [ ] Rate limiting is enabled
- [ ] Documentation is up to date
- [ ] Rollback plan is prepared

## Support

For deployment issues:
- Check logs: `docker compose logs -f`
- Review [README.md](./README.md) for architecture details
- Check API documentation: http://localhost:8000/docs
- Review [TROUBLESHOOTING.md](./docs/TROUBLESHOOTING.md)

---

**Last Updated:** November 11, 2025
**Maintained By:** CC-Lite 2026 Team
**Version:** 2.0.0
