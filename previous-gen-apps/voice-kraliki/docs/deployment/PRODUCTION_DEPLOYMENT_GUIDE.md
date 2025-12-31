# Production Deployment Guide
## Operator Demo 2026

This guide covers the complete production deployment of the Operator Demo 2026 application with Traefik reverse proxy, monitoring, and automated backups.

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Prerequisites](#prerequisites)
4. [Environment Configuration](#environment-configuration)
5. [Deployment Steps](#deployment-steps)
6. [Monitoring & Observability](#monitoring--observability)
7. [Backup & Recovery](#backup--recovery)
8. [Security Configuration](#security-configuration)
9. [Troubleshooting](#troubleshooting)
10. [Maintenance](#maintenance)

---

## 🎯 Overview

The Operator Demo 2026 production deployment includes:

- **Frontend**: SvelteKit application with Node.js adapter
- **Backend**: FastAPI Python application with PostgreSQL
- **Reverse Proxy**: Traefik v3 with SSL/TLS termination
- **Monitoring**: Prometheus, Grafana, AlertManager
- **Caching**: Redis for sessions and caching
- **Vector Database**: Qdrant for AI operations
- **Backups**: Automated PostgreSQL and Redis backups

---

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Internet      │    │   Traefik       │    │   Applications  │
│                 │    │   (Port 80/443) │    │                 │
│ ┌─────────────┐ │    │ ┌─────────────┐ │    │ ┌─────────────┐ │
│ │ HTTPS/SSL   │ │───▶│ │ Router      │ │───▶│ │ Frontend    │ │
│ │ Termination │ │    │ │ Middleware  │ │    │ │ (Port 3000) │ │
│ └─────────────┘ │    │ │ Load Balance│ │    │ └─────────────┘ │
│                 │    │ │ Rate Limit  │ │    │                 │
│ ┌─────────────┐ │    │ └─────────────┘ │    │ ┌─────────────┐ │
│ │ Domain      │ │    │                 │    │ │ Backend     │ │
│ │ Management  │ │    │ ┌─────────────┐ │    │ │ (Port 8000) │ │
│ └─────────────┘ │    │ │ SSL Certs   │ │    │ └─────────────┘ │
└─────────────────┘    │ │ Let's Encrypt│ │    └─────────────────┘
                       │ └─────────────┘ │
                       └─────────────────┘
                                │
                       ┌─────────────────┐
                       │   Monitoring    │
                       │                 │
                       │ ┌─────────────┐ │
                       │ │ Prometheus  │ │
                       │ │ (Port 9090) │ │
                       │ └─────────────┘ │
                       │                 │
                       │ ┌─────────────┐ │
                       │ │ Grafana     │ │
                       │ │ (Port 3001) │ │
                       │ └─────────────┘ │
                       │                 │
                       │ ┌─────────────┐ │
                       │ │ AlertManager│ │
                       │ │ (Port 9093) │ │
                       │ └─────────────┘ │
                       └─────────────────┘
```

---

## ✅ Prerequisites

### System Requirements
- **OS**: Linux (Ubuntu 20.04+ recommended)
- **RAM**: Minimum 4GB, Recommended 8GB+
- **Storage**: Minimum 20GB, Recommended 50GB+
- **CPU**: Minimum 2 cores, Recommended 4+ cores

### Software Requirements
- **Docker**: 20.10+
- **Docker Compose**: 2.0+
- **Git**: 2.30+
- **OpenSSL**: For certificate generation

### Network Requirements
- **Ports**: 80, 443, 8080 (Traefik dashboard)
- **Domains**: Configured with DNS A records
- **Firewall**: Allow HTTP/HTTPS traffic

---

## ⚙️ Environment Configuration

### 1. Production Environment File

Create `.env.production`:

```bash
# Application Settings
APP_NAME=Operator Demo Backend
VERSION=2.0.0
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO

# Server Configuration
HOST=0.0.0.0
PORT=8000

# Production URLs
FRONTEND_URL=https://app.operator-demo-2026.com
PRODUCTION_URL=https://api.operator-demo-2026.com
PUBLIC_URL=https://operator-demo-2026.com
API_BASE_URL=https://api.operator-demo-2026.com
PUBLIC_API_BASE_URL=https://api.operator-demo-2026.com
PRIVATE_API_BASE_URL=http://backend:8000

# Security - GENERATE NEW VALUES FOR PRODUCTION!
SECRET_KEY=prod-sk-$(openssl rand -hex 32)
JWT_SECRET=prod-jwt-$(openssl rand -hex 32)
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=1440
JWT_KEYS_DIR=/app/keys
AUTH_COOKIE_NAME=auth_token
REFRESH_COOKIE_NAME=refresh_token
AUTH_COOKIE_DOMAIN=.operator-demo-2026.com
AUTH_COOKIE_SECURE=true
AUTH_COOKIE_SAMESITE=strict
AUTH_COOKIE_PATH=/
CORS_ORIGINS=https://app.operator-demo-2026.com,https://operator-demo-2026.com

# Database Configuration
DATABASE_URL=postgresql://postgres:${POSTGRES_PASSWORD}@postgres:5432/operator_demo
POSTGRES_PASSWORD=prod-db-$(openssl rand -hex 16)

# AI Provider API Keys
OPENAI_API_KEY=your-openai-api-key
GEMINI_API_KEY=your-gemini-api-key
DEEPGRAM_API_KEY=your-deepgram-api-key

# Telephony Provider Credentials
TWILIO_ACCOUNT_SID=your-twilio-account-sid
TWILIO_AUTH_TOKEN=your-twilio-auth-token
TELNYX_API_KEY=your-telnyx-api-key
TELNYX_PUBLIC_KEY=your-telnyx-public-key

# Redis Configuration
REDIS_URL=redis://redis:6379/0

# Monitoring & Observability
SENTRY_DSN=${SENTRY_DSN}
SENTRY_TRACES_SAMPLE_RATE=0.1
SENTRY_PROFILES_SAMPLE_RATE=0.1
ENABLE_METRICS=true
RELEASE_VERSION=2.0.0

# AWS Configuration (for backups)
AWS_S3_BUCKET=${AWS_S3_BUCKET}
AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
AWS_DEFAULT_REGION=us-east-1

# Backup Configuration
BACKUP_DIR=/backups
RETENTION_DAYS=30
```

### 2. Traefik Environment

Create `.env.traefik`:

```bash
# Cloudflare API credentials (for Let's Encrypt DNS challenge)
CF_API_EMAIL=your-email@example.com
CF_DNS_API_TOKEN=your-cloudflare-dns-token
CF_API_KEY=your-cloudflare-api-key

# Traefik Environment
TRAEFIK_ENV=production

# Grafana Credentials
GRAFANA_USER=admin
GRAFANA_PASSWORD=your-grafana-password
```

---

## 🚀 Deployment Steps

### 1. Clone Repository

```bash
git clone <repository-url>
cd operator-demo-2026
```

### 2. Generate SSL Certificates (Development)

```bash
# For development/testing only
./scripts/generate-ssl-certs.sh
```

### 3. Deploy Production Stack

```bash
# Deploy full production stack with monitoring
docker compose -f docker-compose.yml \
  -f docker-compose.traefik.yml \
  -f docker-compose.prod.yml \
  -f docker-compose.monitoring.yml \
  up -d
```

### 4. Verify Deployment

```bash
# Check all services
docker compose -f docker-compose.yml \
  -f docker-compose.traefik.yml \
  -f docker-compose.prod.yml \
  -f docker-compose.monitoring.yml \
  ps

# Test services
curl -f http://localhost:8000/health  # Backend
curl -f http://localhost:3000/        # Frontend
curl -f http://localhost:9090/api/v1/status/config  # Prometheus
```

---

## 📊 Monitoring & Observability

### Prometheus Metrics

Access: http://localhost:9090

**Key Metrics:**
- `http_requests_total` - HTTP request count
- `http_request_duration_seconds` - Request latency
- `up` - Service availability
- `process_cpu_seconds_total` - CPU usage
- `process_resident_memory_bytes` - Memory usage

### Grafana Dashboards

Access: http://localhost:3001 (admin/admin)

**Default Dashboards:**
- System Overview
- Application Performance
- Database Metrics
- Infrastructure Health

### AlertManager

Access: http://localhost:9093

**Alert Types:**
- **Critical**: Service down, high error rates
- **Warning**: High response times, resource usage
- **Info**: High request rates, system events

### Sentry Integration

Configure in `.env.production`:

```bash
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
SENTRY_TRACES_SAMPLE_RATE=0.1
SENTRY_PROFILES_SAMPLE_RATE=0.1
```

---

## 💾 Backup & Recovery

### Automated Backups

The backup script runs automatically and includes:

- **PostgreSQL**: Full database dumps
- **Redis**: RDB snapshots
- **Compression**: Gzip compression
- **Retention**: 30-day retention policy
- **Cloud Storage**: Optional S3 upload

### Manual Backup

```bash
# Run backup manually
./scripts/backup-production.sh

# Custom backup directory
BACKUP_DIR=/custom/backups ./scripts/backup-production.sh
```

### Recovery Procedures

#### PostgreSQL Recovery

```bash
# Stop application
docker compose stop backend

# Restore database
docker exec -i operator-demo-postgres psql -U postgres operator_demo < backup.sql

# Restart application
docker compose start backend
```

#### Redis Recovery

```bash
# Stop Redis
docker compose stop redis

# Copy backup file
docker cp redis_backup.rdb operator-demo-redis:/data/dump.rdb

# Restart Redis
docker compose start redis
```

---

## 🔒 Security Configuration

### SSL/TLS Configuration

Traefik automatically handles SSL certificates:

```yaml
# traefik/traefik.yml
certificatesResolvers:
  letsencrypt:
    acme:
      email: ${CF_API_EMAIL}
      storage: /letsencrypt/acme.json
      dnsChallenge:
        provider: cloudflare
```

### Security Headers

Configured in Traefik middleware:

```yaml
# traefik/config/middlewares.yml
security-headers:
  headers:
    customResponseHeaders:
      X-Content-Type-Options: "nosniff"
      X-Frame-Options: "DENY"
      X-XSS-Protection: "1; mode=block"
      Strict-Transport-Security: "max-age=31536000; includeSubDomains"
```

### Rate Limiting

```yaml
rate-limit-api:
  rateLimit:
    average: 100
    period: "1m"
    burst: 200
```

### CORS Configuration

```yaml
cors-headers:
  headers:
    accessControlAllowOriginList:
      - "https://operator-demo-2026.com"
      - "https://api.operator-demo-2026.com"
```

---

## 🔧 Troubleshooting

### Common Issues

#### 1. Frontend Health Check Fails

**Problem**: Frontend container unhealthy
**Solution**: Check SvelteKit adapter configuration

```bash
# Check logs
docker logs operator-demo-frontend

# Verify adapter-node configuration
cat frontend/svelte.config.js
```

#### 2. Database Connection Issues

**Problem**: Backend can't connect to PostgreSQL
**Solution**: Verify database URL and credentials

```bash
# Check database status
docker exec operator-demo-postgres pg_isready -U postgres

# Test connection from backend
docker exec operator-demo-backend python -c "
import psycopg2
conn = psycopg2.connect('postgresql://postgres:password@postgres:5432/operator_demo')
print('Database connection successful')
"
```

#### 3. SSL Certificate Issues

**Problem**: Let's Encrypt certificate renewal fails
**Solution**: Check Cloudflare API credentials

```bash
# Check Traefik logs
docker logs operator-traefik | grep -i acme

# Verify Cloudflare token
curl -X GET "https://api.cloudflare.com/client/v4/user/tokens/verify" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### 4. Monitoring Services Down

**Problem**: Prometheus/Grafana not accessible
**Solution**: Check network configuration

```bash
# Check network
docker network ls
docker network inspect operator-demo-2026_operator-network

# Restart monitoring stack
docker compose -f docker-compose.monitoring.yml restart
```

### Health Check Commands

```bash
# Backend health
curl -f http://localhost:8000/health

# Frontend health
curl -f http://localhost:3000/

# Database health
docker exec operator-demo-postgres pg_isready -U postgres

# Redis health
docker exec operator-demo-redis redis-cli ping

# Traefik health
curl -f http://localhost:8080/ping
```

### Log Analysis

```bash
# Application logs
docker logs operator-demo-backend --tail 100
docker logs operator-demo-frontend --tail 100

# Infrastructure logs
docker logs operator-traefik --tail 100
docker logs operator-prometheus --tail 100

# Database logs
docker logs operator-demo-postgres --tail 100
```

---

## 🔄 Maintenance

### Regular Tasks

#### Daily
- Monitor service health
- Check backup completion
- Review error logs

#### Weekly
- Update security patches
- Review resource usage
- Check SSL certificate expiry

#### Monthly
- Database maintenance
- Log rotation
- Performance tuning

### Update Procedures

#### Application Updates

```bash
# Pull latest code
git pull origin main

# Rebuild and redeploy
docker compose -f docker-compose.yml \
  -f docker-compose.traefik.yml \
  -f docker-compose.prod.yml \
  -f docker-compose.monitoring.yml \
  up -d --build
```

#### System Updates

```bash
# Update Docker images
docker compose pull

# Restart with new images
docker compose -f docker-compose.yml \
  -f docker-compose.traefik.yml \
  -f docker-compose.prod.yml \
  -f docker-compose.monitoring.yml \
  up -d
```

### Performance Monitoring

Key metrics to monitor:

- **Response Time**: < 500ms (95th percentile)
- **Error Rate**: < 1%
- **CPU Usage**: < 80%
- **Memory Usage**: < 85%
- **Disk Usage**: < 90%

### Scaling Considerations

#### Horizontal Scaling

```yaml
# docker-compose.prod.yml
backend:
  deploy:
    replicas: 3
  # ... other config
```

#### Resource Limits

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
```

---

## 📞 Support

### Emergency Contacts

- **Infrastructure**: infrastructure@operator-demo-2026.com
- **Application**: development@operator-demo-2026.com
- **Security**: security@operator-demo-2026.com

### Documentation

- **API Documentation**: http://localhost:8000/docs
- **Traefik Dashboard**: http://localhost:8080
- **Grafana Dashboards**: http://localhost:3001

### Monitoring Alerts

Configure alert notifications in `monitoring/alertmanager.yml`:

```yaml
receivers:
  - name: 'critical-alerts'
    email_configs:
      - to: 'admin@operator-demo-2026.com'
```

---

## 📝 Change Log

### v2.0.0 (2025-10-12)
- ✅ Production deployment with Traefik
- ✅ Comprehensive monitoring setup
- ✅ Automated backup system
- ✅ Security hardening
- ✅ SSL/TLS configuration
- ✅ Health checks for all services

---

**Last Updated**: October 12, 2025  
**Version**: 2.0.0  
**Environment**: Production