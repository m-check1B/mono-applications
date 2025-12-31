# Voice by Kraliki Python Backend - Deployment Guide

**Stack**: Python 3.11+ + FastAPI + SQLAlchemy + PostgreSQL
**Last Updated**: October 1, 2025

---

## 🚀 Quick Deployment Options

### Option 1: Docker Compose (Recommended for Development)

```bash
cd backend-python
docker compose up --build
```

**Includes**:
- Python backend (port 3010)
- PostgreSQL database (port 5432)
- Redis cache (port 6379)

### Option 2: Production with PM2 + Docker

```bash
# Build Docker image
docker build -t cc-lite-backend:latest .

# Run with PM2
pm2 start ecosystem.config.js
```

### Option 3: Direct Python (Development)

```bash
# Install dependencies
pip install -r requirements.txt

# Setup database
alembic upgrade head

# Run server
uvicorn app.main:app --host 0.0.0.0 --port 3010
```

---

## 📋 Prerequisites

### System Requirements
- Python 3.11+
- PostgreSQL 15+
- Redis 7+ (optional)
- 2GB RAM minimum
- 10GB disk space

### External Services
- Twilio account (for telephony)
- OpenAI API key (for AI features)
- Deepgram API key (for transcription)

---

## 🔧 Configuration

### 1. Environment Variables

Copy and edit `.env.example`:

```bash
cp .env.example .env
```

**Required Variables**:
```bash
# Application
CC_LITE_SECRET_KEY=<generate-with-openssl-rand-hex-32>
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/cc_lite

# Auth
JWT_SECRET=<generate-with-openssl-rand-hex-32>

# Telephony (if using)
TWILIO_ACCOUNT_SID=<your-twilio-sid>
TWILIO_AUTH_TOKEN=<your-twilio-token>
TWILIO_PHONE_NUMBER=<your-twilio-number>

# AI Services (if using)
OPENAI_API_KEY=<your-openai-key>
DEEPGRAM_API_KEY=<your-deepgram-key>
```

**Generate Secrets**:
```bash
# Generate SECRET_KEY
openssl rand -hex 32

# Generate JWT_SECRET
openssl rand -hex 32
```

### 2. Database Setup

**Create Database**:
```bash
createdb cc_lite
```

**Run Migrations**:
```bash
cd backend-python
alembic upgrade head
```

**Seed Data** (optional):
```python
# Create seed script: scripts/seed.py
python scripts/seed.py
```

---

## 🐳 Docker Deployment

### Development (docker compose.yml)

```yaml
services:
  backend:
    build: .
    ports:
      - "3010:3010"
    environment:
      - DATABASE_URL=postgresql+asyncpg://cc_lite:cc_lite_dev@postgres:5432/cc_lite
      - CC_LITE_DEBUG=true
    depends_on:
      - postgres
      - redis

  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_USER=cc_lite
      - POSTGRES_PASSWORD=cc_lite_dev
      - POSTGRES_DB=cc_lite
    volumes:
      - postgres-data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
```

**Start**:
```bash
docker compose up -d
```

### Production (docker compose.production.yml)

```yaml
services:
  backend:
    build: .
    restart: always
    ports:
      - "3010:3010"
    environment:
      - CC_LITE_DEBUG=false
      - HOST=0.0.0.0
    env_file:
      - .env.production
    depends_on:
      - postgres
      - redis
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3010/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

**Deploy**:
```bash
docker compose -f docker compose.production.yml up -d
```

---

## 🔄 Database Migrations

### Create Migration

```bash
# Auto-generate migration from model changes
alembic revision --autogenerate -m "Description of changes"

# Create empty migration
alembic revision -m "Description"
```

### Apply Migrations

```bash
# Upgrade to latest
alembic upgrade head

# Upgrade one version
alembic upgrade +1

# Downgrade one version
alembic downgrade -1

# Show current version
alembic current

# Show migration history
alembic history
```

---

## 🌐 Nginx Reverse Proxy

### Configuration

```nginx
server {
    listen 80;
    server_name api.cc-lite.example.com;

    location / {
        proxy_pass http://127.0.0.1:3010;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket support
    location /ws {
        proxy_pass http://127.0.0.1:3010;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "Upgrade";
    }
}
```

### SSL with Let's Encrypt

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d api.cc-lite.example.com

# Auto-renewal (already configured)
sudo systemctl status certbot.timer
```

---

## 📊 Monitoring & Logging

### Health Checks

```bash
# Application health
curl http://localhost:3010/health

# Detailed metrics
curl http://localhost:3010/metrics
```

### Logs

```bash
# View logs (Docker)
docker compose logs -f backend

# View logs (systemd)
journalctl -u cc-lite-backend -f

# View logs (PM2)
pm2 logs cc-lite-backend
```

### Monitoring Setup

**Prometheus + Grafana** (optional):
```yaml
# monitoring/docker compose.yml
services:
  prometheus:
    image: prom/prometheus
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"

  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
```

---

## 🧪 Testing Deployment

### Smoke Tests

```bash
# Test health endpoint
curl http://localhost:3010/health

# Test API docs
curl http://localhost:3010/docs

# Test auth endpoint
curl -X POST http://localhost:3010/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password"}'
```

### Load Testing

```bash
# Install k6
brew install k6  # or apt install k6

# Run load test
k6 run tests/load/basic.js
```

---

## 🔐 Security Checklist

- [ ] Change all default passwords
- [ ] Set strong SECRET_KEY and JWT_SECRET
- [ ] Enable HTTPS with valid SSL certificate
- [ ] Configure firewall (allow only 80, 443, 22)
- [ ] Set CC_LITE_DEBUG=false in production
- [ ] Use environment variables for secrets (not .env files)
- [ ] Enable rate limiting
- [ ] Configure CORS properly
- [ ] Regular security updates (`apt update && apt upgrade`)
- [ ] Database backups configured
- [ ] Monitor logs for suspicious activity

---

## 📦 Backup & Recovery

### Database Backup

```bash
# Backup
pg_dump -h localhost -U cc_lite cc_lite > backup_$(date +%Y%m%d).sql

# Restore
psql -h localhost -U cc_lite cc_lite < backup_20251001.sql
```

### Automated Backups

```bash
# Add to crontab
0 2 * * * /usr/bin/pg_dump -h localhost -U cc_lite cc_lite > /backups/cc_lite_$(date +\%Y\%m\%d).sql
```

---

## 🚨 Troubleshooting

### Common Issues

**Cannot connect to database**:
```bash
# Check PostgreSQL is running
systemctl status postgresql

# Check connection
psql -h localhost -U cc_lite -d cc_lite
```

**Import errors**:
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

**Port already in use**:
```bash
# Find process using port 3010
lsof -i :3010

# Kill process
kill -9 <PID>
```

**Alembic migration fails**:
```bash
# Check current version
alembic current

# Stamp database with current version
alembic stamp head
```

---

## 📚 Additional Resources

- [API Documentation](http://localhost:3010/docs)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [SQLAlchemy Docs](https://docs.sqlalchemy.org/)
- [Alembic Docs](https://alembic.sqlalchemy.org/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)

---

**Support**: Create an issue in the repository or contact the development team.
