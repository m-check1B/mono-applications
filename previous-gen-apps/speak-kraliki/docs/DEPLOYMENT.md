# Deployment Guide

## Prerequisites

- Docker 24+ and Docker Compose v2
- PostgreSQL 17+
- Domain with SSL certificate
- Google Cloud account (Gemini API)
- Resend account (email delivery)

## Environment Variables

Create `.env` file with:

```bash
# Database
POSTGRES_USER=vop
POSTGRES_PASSWORD=your-db-password
POSTGRES_DB=vop
DATABASE_URL=postgresql+asyncpg://vop:your-db-password@db:5432/vop

# Security
SECRET_KEY=your-256-bit-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# AI
GEMINI_API_KEY=your-gemini-api-key

# Email
RESEND_API_KEY=your-resend-api-key
RESEND_FROM_EMAIL=noreply@yourdomain.com

# URLs
FRONTEND_URL=https://yourdomain.com
BACKEND_URL=https://api.yourdomain.com

# Optional
STRIPE_SECRET_KEY=sk_live_xxx
STRIPE_WEBHOOK_SECRET=whsec_xxx
```

## Docker Deployment (Traefik)

Use the repo `docker-compose.yml` which already includes Traefik labels and the
`websites_default` network.

```bash
docker compose up -d --build
```

Update the `traefik.http.routers.*.rule` hostnames in `docker-compose.yml` if
you are using custom domains.

### Backend Dockerfile

```dockerfile
FROM python:3.13-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"]
```

### Frontend Dockerfile

```dockerfile
FROM node:22-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:22-alpine
WORKDIR /app
COPY --from=builder /app/build ./build
COPY --from=builder /app/package*.json ./
RUN npm ci --omit=dev
EXPOSE 3000
CMD ["node", "build"]
```

### Traefik Routing

Routing is handled by Traefik (see `/github/infra/traefik/`). Do not use nginx
here. The compose file already defines routers for `/api`, `/docs`,
`/openapi.json`, and `/health` for both production and beta domains.

## Deployment Steps

### 1. Initial Setup

```bash
# Clone repository
git clone https://github.com/yourorg/speak-kraliki.git
cd speak-kraliki

# Create environment file
cp .env.example .env
# Edit .env with your values
```

### 2. Database Migration

```bash
# Start database
docker compose up -d db

# Run migrations
docker compose run --rm backend \
    alembic upgrade head
```

### 3. Deploy Services

```bash
# Build and start all services
docker compose up -d --build

# Check status
docker compose ps

# View logs
docker compose logs -f
```

### 4. SSL Setup (Traefik)

TLS is handled by Traefik via the `letsencrypt` certresolver. Make sure Traefik
is running and the `traefik.http.routers.*.tls.certresolver=letsencrypt` labels
are set in `docker-compose.yml`. No certbot or nginx required.

## Scaling

### Horizontal Scaling

```yaml
# docker-compose.yml
services:
  backend:
    deploy:
      replicas: 3
```

### Database Connection Pooling

Use PgBouncer for high traffic:

```yaml
pgbouncer:
  image: edoburu/pgbouncer
  environment:
    DATABASE_URL: postgresql://vop:pass@db:5432/vop
    POOL_MODE: transaction
    MAX_CLIENT_CONN: 1000
```

## Monitoring

### Health Checks

- Backend: `GET /health`
- Database: PostgreSQL health check in compose

### Logging

```bash
# View all logs
docker compose logs -f

# Export to file
docker compose logs > logs.txt
```

### Metrics (Optional)

Add Prometheus + Grafana for metrics:

```yaml
prometheus:
  image: prom/prometheus
  volumes:
    - ./prometheus.yml:/etc/prometheus/prometheus.yml

grafana:
  image: grafana/grafana
  ports:
    - "127.0.0.1:3001:3000"
```

## Backup Strategy

### Database Backup

```bash
# Manual backup
docker compose exec db pg_dump -U vop vop > backup.sql

# Automated (cron)
0 2 * * * docker compose exec -T db pg_dump -U vop vop | gzip > /backups/vop_$(date +\%Y\%m\%d).sql.gz
```

### Restore

```bash
docker compose exec -T db psql -U vop vop < backup.sql
```

## Troubleshooting

### Container won't start

```bash
# Check logs
docker compose logs backend

# Verify environment
docker compose config
```

### Database connection issues

```bash
# Test connection
docker compose exec backend python -c "
from app.core.database import engine
import asyncio
async def test():
    async with engine.connect() as conn:
        print('Connected!')
asyncio.run(test())
"
```

### WebSocket issues

- Verify Traefik WebSocket configuration
- Check firewall allows WSS (port 443)
- Verify `proxy_read_timeout` is sufficient

## Security Checklist

- [ ] SSL/TLS enabled
- [ ] Strong SECRET_KEY (32+ chars)
- [ ] Database not exposed publicly
- [ ] Environment variables secured
- [ ] Rate limiting configured
- [ ] CORS properly restricted
- [ ] Regular backups configured
- [ ] Logs rotated
