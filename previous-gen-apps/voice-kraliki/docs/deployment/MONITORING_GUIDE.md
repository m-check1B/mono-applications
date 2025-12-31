# Monitoring Guide
## Operator Demo 2026 Production

This guide covers the complete monitoring and observability setup for the Operator Demo 2026 production environment.

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Monitoring Stack](#monitoring-stack)
3. [Metrics Collection](#metrics-collection)
4. [Alerting](#alerting)
5. [Dashboards](#dashboards)
6. [Troubleshooting](#troubleshooting)
7. [Maintenance](#maintenance)

---

## 🎯 Overview

The monitoring stack provides comprehensive observability for:

- **Application Performance**: Response times, error rates, throughput
- **Infrastructure Health**: CPU, memory, disk, network
- **Business Metrics**: User activity, feature usage
- **Security Events**: Authentication failures, rate limits

---

## 🏗️ Monitoring Stack

### Components

| Component | Purpose | Access | Port |
|-----------|---------|--------|------|
| **Prometheus** | Metrics collection & storage | http://localhost:9090 | 9090 |
| **Grafana** | Visualization & dashboards | http://localhost:3001 | 3001 |
| **AlertManager** | Alert routing & notification | http://localhost:9093 | 9093 |
| **Node Exporter** | System metrics | http://localhost:9100/metrics | 9100 |

### Architecture

```
Applications → Prometheus → AlertManager → Notifications
     ↓              ↓
   Metrics      Grafana ← Dashboards
     ↓
   Node Exporter (System Metrics)
```

---

## 📊 Metrics Collection

### Application Metrics

#### HTTP Metrics
```promql
# Request rate
rate(http_requests_total[5m])

# Error rate
rate(http_requests_total{status=~"5.."}[5m])

# Response time (95th percentile)
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))
```

#### Business Metrics
```promql
# Active users
rate(user_sessions_total[5m])

# API calls per feature
rate(api_calls_total{feature="campaigns"}[5m])

# Conversion rate
rate(signups_total[5m]) / rate(page_views_total{page="/signup"}[5m])
```

### Infrastructure Metrics

#### System Resources
```promql
# CPU usage
100 - (avg by(instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)

# Memory usage
(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100

# Disk usage
(1 - (node_filesystem_avail_bytes / node_filesystem_size_bytes)) * 100

# Network I/O
rate(node_network_receive_bytes_total[5m])
rate(node_network_transmit_bytes_total[5m])
```

#### Database Metrics
```promql
# PostgreSQL connections
pg_stat_activity_count

# Query performance
rate(pg_stat_statements_mean_time_seconds[5m])

# Database size
pg_database_size_bytes
```

### Custom Metrics

#### Application-Specific
```python
# In FastAPI application
from prometheus_client import Counter, Histogram, Gauge

# Business metrics
user_registrations = Counter('user_registrations_total', 'Total user registrations')
campaigns_created = Counter('campaigns_created_total', 'Total campaigns created')

# Performance metrics
request_duration = Histogram('api_request_duration_seconds', 'API request duration')
active_sessions = Gauge('active_sessions_total', 'Number of active sessions')

# Usage in endpoints
@app.post("/users/register")
async def register_user():
    user_registrations.inc()
    # ... registration logic
```

---

## 🚨 Alerting

### Alert Rules

#### Critical Alerts
```yaml
# monitoring/rules/alerts.yml
- alert: BackendDown
  expr: up{job="operator-backend"} == 0
  for: 1m
  labels:
    severity: critical
    service: backend
  annotations:
    summary: "Backend API is down"
    description: "Backend API has been down for more than 1 minute"

- alert: HighErrorRate
  expr: rate(http_requests_total{job="operator-backend",status=~"5.."}[5m]) > 0.1
  for: 2m
  labels:
    severity: critical
    service: backend
  annotations:
    summary: "High error rate on backend API"
    description: "Backend API error rate is {{ $value }} errors per second"
```

#### Warning Alerts
```yaml
- alert: HighResponseTime
  expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket{job="operator-backend"}[5m])) > 1
  for: 5m
  labels:
    severity: warning
    service: backend
  annotations:
    summary: "High response time on backend API"
    description: "95th percentile response time is {{ $value }} seconds"

- alert: HighCPUUsage
  expr: 100 - (avg by(instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80
  for: 5m
  labels:
    severity: warning
    service: system
  annotations:
    summary: "High CPU usage"
    description: "CPU usage is {{ $value }}% on {{ $labels.instance }}"
```

### Notification Channels

#### Email Configuration
```yaml
# monitoring/alertmanager.yml
receivers:
  - name: 'critical-alerts'
    email_configs:
      - to: 'admin@operator-demo-2026.com'
        headers:
          subject: '[CRITICAL] Operator Demo Alert: {{ .GroupLabels.alertname }}'
        html: |
          <h2>🚨 Critical Alert</h2>
          {{ range .Alerts }}
          <p><strong>{{ .Annotations.summary }}</strong></p>
          <p>{{ .Annotations.description }}</p>
          <p><strong>Labels:</strong> {{ range .Labels.SortedPairs }}{{ .Name }}={{ .Value }} {{ end }}</p>
          {{ end }}
```

#### Webhook Configuration
```yaml
- name: 'web.hook'
  webhook_configs:
    - url: 'http://backend:8000/webhooks/alerts'
        send_resolved: true
        http_config:
          bearer_token: 'your-webhook-token'
```

#### Slack Integration
```yaml
- name: 'slack-alerts'
  slack_configs:
    - api_url: 'https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK'
        channel: '#alerts'
        title: 'Operator Demo Alert'
        text: '{{ range .Alerts }}{{ .Annotations.summary }}{{ end }}'
```

---

## 📈 Dashboards

### Grafana Setup

#### Data Sources
1. **Prometheus**: http://prometheus:9090
2. **Loki**: (optional) for logs
3. **Tempo**: (optional) for traces

#### Dashboard Templates

##### 1. Application Overview
```json
{
  "dashboard": {
    "title": "Application Overview",
    "panels": [
      {
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])",
            "legendFormat": "{{method}} {{status}}"
          }
        ]
      },
      {
        "title": "Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "95th percentile"
          },
          {
            "expr": "histogram_quantile(0.50, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "50th percentile"
          }
        ]
      },
      {
        "title": "Error Rate",
        "type": "singlestat",
        "targets": [
          {
            "expr": "rate(http_requests_total{status=~\"5..\"}[5m]) / rate(http_requests_total[5m])",
            "legendFormat": "Error Rate"
          }
        ]
      }
    ]
  }
}
```

##### 2. Infrastructure Health
```json
{
  "dashboard": {
    "title": "Infrastructure Health",
    "panels": [
      {
        "title": "CPU Usage",
        "type": "graph",
        "targets": [
          {
            "expr": "100 - (avg by(instance) (rate(node_cpu_seconds_total{mode=\"idle\"}[5m])) * 100)",
            "legendFormat": "{{instance}}"
          }
        ]
      },
      {
        "title": "Memory Usage",
        "type": "graph",
        "targets": [
          {
            "expr": "(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100",
            "legendFormat": "{{instance}}"
          }
        ]
      },
      {
        "title": "Disk Usage",
        "type": "graph",
        "targets": [
          {
            "expr": "(1 - (node_filesystem_avail_bytes / node_filesystem_size_bytes)) * 100",
            "legendFormat": "{{instance}}:{{mountpoint}}"
          }
        ]
      }
    ]
  }
}
```

### Custom Dashboards

#### Business Metrics Dashboard
- User registrations over time
- Campaign creation rate
- API usage by feature
- Revenue metrics (if applicable)

#### Security Dashboard
- Authentication failures
- Rate limit violations
- Suspicious activity patterns
- SSL certificate expiry

---

## 🔧 Troubleshooting

### Common Issues

#### 1. Prometheus Not Scraping Metrics

**Symptoms**: No data in Prometheus
**Diagnostics**:
```bash
# Check Prometheus targets
curl http://localhost:9090/api/v1/targets

# Check specific target
curl http://localhost:8000/metrics

# Check network connectivity
docker exec operator-prometheus ping backend
```

**Solutions**:
- Verify service discovery configuration
- Check network connectivity
- Ensure metrics endpoint is accessible

#### 2. Grafana Data Source Issues

**Symptoms**: No data in Grafana dashboards
**Diagnostics**:
```bash
# Test Prometheus from Grafana container
docker exec operator-grafana curl http://prometheus:9090/api/v1/query?query=up

# Check Grafana logs
docker logs operator-grafana
```

**Solutions**:
- Verify data source configuration
- Check network connectivity
- Validate Prometheus query syntax

#### 3. AlertManager Not Sending Notifications

**Symptoms**: Alerts firing but no notifications
**Diagnostics**:
```bash
# Check AlertManager configuration
curl http://localhost:9093/api/v1/status

# Test webhook endpoint
curl -X POST http://backend:8000/webhooks/alerts -H "Content-Type: application/json" -d '{"test": true}'
```

**Solutions**:
- Verify notification configuration
- Test webhook endpoints
- Check SMTP settings for email

### Performance Issues

#### High Memory Usage in Prometheus
```yaml
# prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s
  # Reduce retention if needed
  # external_labels:
  #   retention: 15d
```

#### Slow Grafana Queries
- Optimize PromQL queries
- Use recording rules for complex queries
- Implement query caching

---

## 🔄 Maintenance

### Daily Tasks

#### Health Checks
```bash
# Check all monitoring services
docker compose -f docker-compose.monitoring.yml ps

# Verify Prometheus targets
curl -s http://localhost:9090/api/v1/targets | jq '.data.activeTargets[] | select(.health=="up") | .labels.job'

# Check alert status
curl -s http://localhost:9093/api/v1/alerts | jq '.data.alerts[] | select(.state=="firing")'
```

#### Log Review
```bash
# Check for errors
docker logs operator-prometheus --tail 100 | grep -i error
docker logs operator-grafana --tail 100 | grep -i error
docker logs operator-alertmanager --tail 100 | grep -i error
```

### Weekly Tasks

#### Performance Review
- Check query performance in Grafana
- Review alert effectiveness
- Monitor resource usage

#### Configuration Updates
- Update alert thresholds
- Add new metrics
- Refresh dashboards

### Monthly Tasks

#### Capacity Planning
- Review storage usage
- Plan for scaling
- Update retention policies

#### Backup Configuration
```bash
# Backup Prometheus data
docker exec operator-prometheus tar czf /tmp/prometheus-backup.tar.gz /prometheus

# Backup Grafana dashboards
curl -u admin:admin http://localhost:3001/api/dashboards/home > grafana-dashboards.json
```

---

## 📚 Additional Resources

### Documentation
- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [AlertManager Documentation](https://prometheus.io/docs/alerting/latest/alertmanager/)

### Query Examples

#### Application Performance
```promql
# Top 10 slowest endpoints
topk(10, histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])))

# Error rate by endpoint
rate(http_requests_total{status=~"5.."}[5m]) by (endpoint)

# Request rate by method
rate(http_requests_total[5m]) by (method)
```

#### System Performance
```promql
# Load average
node_load1

# Disk I/O
rate(node_disk_io_time_seconds_total[5m])

# Network errors
rate(node_network_receive_errs_total[5m])
```

### Best Practices

1. **Labeling**: Use consistent labeling strategy
2. **Retention**: Set appropriate data retention policies
3. **Alerting**: Avoid alert fatigue with proper thresholds
4. **Security**: Secure monitoring endpoints
5. **Documentation**: Document custom metrics and alerts

---

**Last Updated**: October 12, 2025  
**Version**: 2.0.0  
**Environment**: Production