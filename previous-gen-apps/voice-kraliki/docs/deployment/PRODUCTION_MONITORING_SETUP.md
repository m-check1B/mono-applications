# Production Deployment with Full Monitoring Stack
# ==============================================

This guide explains how to deploy Voice Kraliki with complete APM and monitoring infrastructure.

## Overview

The monitoring stack includes:

| Component | Purpose | Access URL |
|-----------|---------|------------|
| **Prometheus** | Metrics collection and storage | http://localhost:9090 |
| **Grafana** | Visualization dashboards | http://localhost:3001 |
| **Alertmanager** | Alert routing and notifications | http://localhost:9093 |
| **Node Exporter** | System metrics (CPU, memory, disk) | http://localhost:9100/metrics |
| **Sentry** | Error tracking and performance monitoring | Configure SENTRY_DSN |

## Prerequisites

1. **Docker and Docker Compose** installed
2. **Environment variables** configured in `.env`
3. **Sentry DSN** (optional but recommended for production)

## Quick Start

### 1. Configure Environment Variables

Create or update `.env` file with monitoring configuration:

```bash
# Sentry Error Tracking (optional but recommended)
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
SENTRY_TRACES_SAMPLE_RATE=0.1
SENTRY_PROFILES_SAMPLE_RATE=0.1

# Grafana Admin Credentials
GRAFANA_ADMIN_USER=admin
GRAFANA_ADMIN_PASSWORD=your-secure-password

# Grafana Root URL (update for production)
GRAFANA_ROOT_URL=http://localhost:3001
```

### 2. Deploy Application with Monitoring

Deploy both application and monitoring stack:

```bash
# Deploy application services
docker compose -f docker-compose.yml up -d

# Deploy monitoring stack
docker compose -f docker-compose.monitoring.prod.yml up -d
```

Or use the provided monitoring deployment script:

```bash
./scripts/deploy-with-monitoring.sh
```

### 3. Verify Deployment

Check that all services are running:

```bash
# Check application health
curl http://localhost:8000/health

# Check Prometheus is scraping metrics
curl http://localhost:9090/api/v1/targets

# Check Grafana is accessible
curl http://localhost:3001/api/health

# Check metrics endpoint
curl http://localhost:8000/metrics
```

## Monitoring Services

### Prometheus

Prometheus scrapes metrics from all services and stores them for 15 days.

- **Web UI**: http://localhost:9090 (via SSH tunnel or port forwarding)
- **Configuration**: `infra/monitoring/prometheus.yml`
- **Alert Rules**: `backend/monitoring/prometheus-alerts.yml`
- **Retention**: 15 days

**Key metrics collected:**
- HTTP requests and latency (backend)
- Database connection pool
- AI provider requests and errors
- Telephony calls and duration
- Session counts and duration
- WebSocket connections
- System metrics (CPU, memory, disk)

### Grafana

Grafana provides visualization dashboards with real-time metrics.

- **Web UI**: http://localhost:3001
- **Default credentials**: `admin` / `admin` (change in production!)
- **Dashboards**: Auto-provisioned from `infra/monitoring/grafana-dashboards/`

**Available Dashboards:**
1. **CC-Lite / Voice by Kraliki Overview** - Main production dashboard
   - System health status
   - API performance metrics
   - AI provider health
   - Telephony call statistics
   - Database and resource usage

### Alertmanager

Alertmanager receives alerts from Prometheus and routes them to notification channels.

- **Web UI**: http://localhost:9093
- **Configuration**: `infra/monitoring/alertmanager.yml`
- **Default receivers**:
  - Webhook: `http://backend:8000/webhooks/alerts` (for logging)
  - Email: `admin@operator-demo-2026.com` (update for production)

**Alert Severities:**
- **Critical**: Immediate action required (e.g., backend down, all providers offline)
- **Warning**: Investigation needed (e.g., high error rate, degraded performance)

### Sentry

Sentry captures errors and exceptions with stack traces, and provides performance monitoring.

- **Setup**: Configure `SENTRY_DSN` environment variable
- **Features**:
  - Error tracking with stack traces
  - Performance monitoring (traces)
  - User context and breadcrumbs
  - Release tracking
  - Issue grouping and filtering

**Sample rate configuration:**
- `SENTRY_TRACES_SAMPLE_RATE=0.1`: 10% of transactions traced
- `SENTRY_PROFILES_SAMPLE_RATE=0.1`: 10% of requests profiled

## Alert Rules

### Critical Alerts

Alerts that require immediate action:

| Alert | Trigger | For |
|-------|----------|------|
| `CircuitBreakerOpen` | Circuit breaker OPEN for provider | 1 min |
| `AllProvidersDown` | All 3 voice providers offline | 1 min |
| `BackendDown` | Backend API unreachable | 1 min |
| `DatabaseDown` | PostgreSQL unreachable | 1 min |
| `HighProviderErrorRate` | Error rate > 5% | 5 min |
| `CriticalProviderLatency` | P95 latency > 5s | 5 min |
| `DatabaseConnectionPoolExhausted` | < 2 connections available | 5 min |
| `RedisDown` | Redis unreachable | 1 min |

### Warning Alerts

Alerts for investigation:

| Alert | Trigger | For |
|-------|----------|------|
| `HighAPILatency` | P95 latency > 1s | 10 min |
| `ModerateProviderErrorRate` | Error rate > 1% | 10 min |
| `HighErrorLogRate` | > 10 errors/sec | 5 min |
| `CriticalErrorLogRate` | > 50 errors/sec | 2 min |

Full alert rules in: `backend/monitoring/prometheus-alerts.yml`

## Production Security Notes

### Localhost Access Only

All monitoring services bind to `127.0.0.1` only - NOT accessible from internet.

Access via:
- **SSH tunnel**: `ssh -L 9090:localhost:9090 user@server`
- **VS Code port forwarding**: Configure in Remote SSH settings
- **Reverse proxy** (not recommended for production monitoring)

### Secure Configuration

1. **Change Grafana admin password** in `.env`
2. **Configure real Sentry DSN** for error tracking
3. **Update Alertmanager email** in `infra/monitoring/alertmanager.yml`
4. **Set up real notification channels** (Slack, PagerDuty, etc.)

### Traefik Integration

For production with Traefik reverse proxy, add monitoring services to Traefik network
and configure HTTPS access (if needed for external dashboards).

## Troubleshooting

### Prometheus not scraping backend

1. Check backend metrics endpoint:
   ```bash
   curl http://localhost:8000/metrics
   ```

2. Verify Prometheus targets:
   - Go to http://localhost:9090/targets
   - Check if `operator-backend` job is UP

3. Check Prometheus logs:
   ```bash
   docker logs cc-lite-prometheus
   ```

### Alerts not firing

1. Check Alertmanager status:
   ```bash
   curl http://localhost:9093/api/v1/status
   ```

2. View active alerts in Prometheus:
   - Go to http://localhost:9090/alerts

3. Verify webhook endpoint:
   ```bash
   curl http://localhost:8000/webhooks/alerts
   ```

### Grafana dashboard not loading

1. Check datasource connection:
   - Grafana > Settings > Data Sources > Prometheus
   - Verify URL: `http://prometheus:9090`

2. Check Grafana logs:
   ```bash
   docker logs cc-lite-grafana
   ```

### Sentry errors not appearing

1. Verify SENTRY_DSN is set:
   ```bash
   echo $SENTRY_DSN
   ```

2. Check Sentry initialization in logs:
   ```bash
   docker logs cc-lite-backend | grep Sentry
   ```

3. Look for warning "SENTRY_DSN not configured"

## Monitoring Health Check

Verify entire monitoring stack is operational:

```bash
#!/bin/bash

echo "Checking monitoring stack..."

# Application
curl -s http://localhost:8000/health && echo "✅ Backend healthy" || echo "❌ Backend down"
curl -s http://localhost:8000/metrics > /dev/null && echo "✅ Metrics endpoint available" || echo "❌ Metrics endpoint down"

# Prometheus
curl -s http://localhost:9090/-/healthy > /dev/null && echo "✅ Prometheus healthy" || echo "❌ Prometheus down"

# Alertmanager
curl -s http://localhost:9093/-/healthy > /dev/null && echo "✅ Alertmanager healthy" || echo "❌ Alertmanager down"

# Grafana
curl -s http://localhost:3001/api/health > /dev/null && echo "✅ Grafana healthy" || echo "❌ Grafana down"

# Node Exporter
curl -s http://localhost:9100/metrics > /dev/null && echo "✅ Node exporter healthy" || echo "❌ Node exporter down"

echo "Monitoring check complete!"
```

## Scaling and Maintenance

### Increase Prometheus Retention

Edit `docker-compose.monitoring.prod.yml`:

```yaml
command:
  - "--storage.tsdb.retention.time=30d"  # 30 days instead of 15
```

### Backup Monitoring Data

```bash
# Backup Prometheus data
docker run --rm -v cc-lite-prometheus_data:/data -v $(pwd):/backup alpine tar czf /backup/prometheus-$(date +%Y%m%d).tar.gz -C /data .

# Backup Grafana dashboards
docker exec cc-lite-grafana tar czf - /var/lib/grafana/dashboards | gzip > grafana-dashboards-$(date +%Y%m%d).tar.gz
```

### Update Alert Rules

Edit `backend/monitoring/prometheus-alerts.yml`, then reload Prometheus:

```bash
curl -X POST http://localhost:9090/-/reload
```

## Documentation

- **Monitoring guide**: `docs/MONITORING.md`
- **Alert rules**: `backend/monitoring/prometheus-alerts.yml`
- **Prometheus config**: `infra/monitoring/prometheus.yml`
- **Grafana dashboards**: `infra/monitoring/grafana-dashboards/`

## Support

For issues with monitoring setup:
1. Check logs: `docker logs cc-lite-<service>`
2. Review `docs/MONITORING.md` for detailed troubleshooting
3. Consult Prometheus/Grafana/Sentry documentation
