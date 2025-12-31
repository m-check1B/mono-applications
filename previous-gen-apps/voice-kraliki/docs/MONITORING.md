# CC-Lite Monitoring & Alerting Setup

This document describes the complete monitoring and alerting setup for CC-Lite / Voice by Kraliki.

## Overview

The monitoring stack consists of:
- **Prometheus**: Metrics collection and storage
- **Alertmanager**: Alert routing and notification
- **Grafana**: Visualization dashboards
- **Node Exporter**: System metrics (CPU, memory, disk)

## Quick Start

### Start Monitoring Stack

```bash
cd /home/adminmatej/github/applications/cc-lite-2026/infra/monitoring
docker compose -f docker-compose.monitoring.yml up -d
```

### Access Services (via SSH tunnel)

Since all services bind to `127.0.0.1` for security, access them via VS Code port forwarding or SSH tunnels:

| Service | Port | URL |
|---------|------|-----|
| Prometheus | 9090 | http://localhost:9090 |
| Alertmanager | 9093 | http://localhost:9093 |
| Grafana | 3001 | http://localhost:3001 |
| Node Exporter | 9100 | http://localhost:9100/metrics |

Default Grafana credentials: `admin` / `admin`

## Health Check Endpoints

The backend provides comprehensive health check endpoints:

### `/api/v1/monitoring/health`
Full system health check with all components.

```bash
curl http://localhost:8000/api/v1/monitoring/health
```

Response:
```json
{
  "status": "healthy",
  "version": "2.0.0",
  "environment": "development",
  "uptime_seconds": 3600.5,
  "components": [
    {"name": "database", "status": "healthy", "latency_ms": 5.2},
    {"name": "redis", "status": "healthy", "latency_ms": 1.1},
    {"name": "disk", "status": "healthy", "latency_ms": 0.3},
    {"name": "memory", "status": "healthy", "latency_ms": 0.1}
  ],
  "checked_at": "2025-12-26T00:10:00Z"
}
```

With external provider checks:
```bash
curl "http://localhost:8000/api/v1/monitoring/health?include_external=true"
```

### `/api/v1/monitoring/health/ready`
Kubernetes-style readiness probe. Checks critical dependencies only.

```bash
curl http://localhost:8000/api/v1/monitoring/health/ready
```

Response:
```json
{
  "ready": true,
  "checks": {
    "database": "healthy"
  }
}
```

### `/api/v1/monitoring/health/live`
Kubernetes-style liveness probe. Lightweight check.

```bash
curl http://localhost:8000/api/v1/monitoring/health/live
```

Response:
```json
{
  "alive": true,
  "uptime_seconds": 3600.5
}
```

### `/api/v1/monitoring/metrics`
Prometheus metrics endpoint.

```bash
curl http://localhost:8000/api/v1/monitoring/metrics
```

## Prometheus Metrics

### HTTP Metrics
- `http_requests_total{method, endpoint, status}` - Request count
- `http_request_duration_seconds{method, endpoint}` - Request latency histogram

### Database Metrics
- `db_connections_total` - Total pool connections
- `db_connections_checked_out` - Currently in-use connections
- `db_connections_overflow` - Overflow connections
- `db_query_duration_seconds{operation}` - Query latency

### AI Provider Metrics
- `ai_provider_requests_total{provider, status}` - Provider request count
- `ai_provider_latency_seconds{provider}` - Provider latency histogram
- `ai_provider_errors_total{provider, error_type}` - Provider errors
- `ai_provider_active_sessions{provider}` - Active provider sessions

### Telephony Metrics
- `telephony_calls_total{provider, status, direction}` - Call count
- `telephony_call_duration_seconds{provider, direction}` - Call duration
- `telephony_active_calls{provider}` - Active calls

### Session Metrics
- `sessions_active{provider_type}` - Active sessions
- `sessions_total{provider_type, status}` - Total sessions created
- `session_duration_seconds{provider_type}` - Session duration

### WebSocket Metrics
- `websocket_connections_active` - Active WebSocket connections
- `websocket_messages_total{direction, message_type}` - Message count

## Alert Rules

Alerts are defined in `/infra/monitoring/rules/alerts.yml`:

### Critical Alerts (Immediate Action)
- **BackendDown**: Backend API is unreachable
- **DatabaseDown**: PostgreSQL is unreachable
- **TraefikDown**: Reverse proxy is unreachable
- **DiskSpaceLow**: Disk usage > 90%
- **AllProvidersDown**: All AI providers circuit breakers open

### Warning Alerts (Investigation Needed)
- **HighErrorRate**: Error rate > 10%
- **HighResponseTime**: P95 latency > 1s
- **HighCPUUsage**: CPU > 80% for 5 minutes
- **HighMemoryUsage**: Memory > 85% for 5 minutes
- **RedisDown**: Redis is unreachable
- **HighProviderLatency**: AI provider P95 > 2s

## Grafana Dashboards

Pre-configured dashboard: **CC-Lite / Voice by Kraliki Overview**

Panels include:
1. **System Overview**: Backend status, P95 latency, error rate, request rate
2. **HTTP Traffic**: Request rate by method, response time percentiles
3. **AI Providers**: Request rate, latency, errors by provider
4. **Telephony**: Active calls, call duration, status distribution
5. **Database & Resources**: Connection pool, WebSocket connections

Dashboard file: `/infra/monitoring/grafana-dashboards/cc-lite-overview.json`

## Alert Notification Configuration

Edit `/infra/monitoring/alertmanager.yml` to configure notifications:

### Email (Default)
```yaml
receivers:
  - name: 'critical-alerts'
    email_configs:
      - to: 'admin@operator-demo-2026.com'
```

### Slack
```yaml
receivers:
  - name: 'slack-alerts'
    slack_configs:
      - api_url: 'https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK'
        channel: '#alerts'
```

### PagerDuty
```yaml
receivers:
  - name: 'pagerduty'
    pagerduty_configs:
      - service_key: 'YOUR_PAGERDUTY_KEY'
```

## Kubernetes Integration

For Kubernetes deployments, use these probe configurations:

```yaml
livenessProbe:
  httpGet:
    path: /api/v1/monitoring/health/live
    port: 8000
  initialDelaySeconds: 10
  periodSeconds: 10

readinessProbe:
  httpGet:
    path: /api/v1/monitoring/health/ready
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 5
```

## Troubleshooting

### Prometheus not scraping backend
1. Check if backend is running: `curl http://localhost:8000/health`
2. Verify Prometheus config: `docker exec cc-lite-prometheus cat /etc/prometheus/prometheus.yml`
3. Check Prometheus targets: http://localhost:9090/targets

### Alerts not firing
1. Check Alertmanager config: `docker exec cc-lite-alertmanager amtool check-config /etc/alertmanager/alertmanager.yml`
2. View active alerts: http://localhost:9093/#/alerts
3. Check Prometheus alerts: http://localhost:9090/alerts

### Grafana dashboard not loading
1. Check datasource: Grafana > Settings > Data Sources > Prometheus
2. Verify Prometheus URL: `http://prometheus:9090`
3. Check provisioning logs: `docker logs cc-lite-grafana`

## Security Notes

All monitoring services bind to `127.0.0.1` only - they are NOT accessible from the internet. Access requires:
- SSH tunnel to the dev server
- VS Code Remote port forwarding

Never bind services to `0.0.0.0` on this internet-connected server!
