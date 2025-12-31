# Voice Kraliki - APM & Production Monitoring Guide

## Overview

Voice Kraliki includes comprehensive production monitoring with:

- **Sentry** - Error tracking, performance monitoring, and profiling
- **Prometheus** - Metrics collection and alerting
- **Structured Logging** - Log aggregation and analysis
- **Health Checks** - Liveness and readiness probes

## Table of Contents

1. [Quick Setup](#quick-setup)
2. [Sentry Configuration](#sentry-configuration)
3. [Prometheus Metrics](#prometheus-metrics)
4. [Health Checks](#health-checks)
5. [Performance Monitoring](#performance-monitoring)
6. [Alerting](#alerting)
7. [Production Deployment](#production-deployment)

---

## Quick Setup

### 1. Set Environment Variables

Add these to your `.env` file:

```bash
# Sentry
SENTRY_DSN="https://your-sentry-dsn@sentry.io/project-id"
SENTRY_TRACES_SAMPLE_RATE=0.1
SENTRY_PROFILES_SAMPLE_RATE=0.1
RELEASE_VERSION="2.0.0"

# Prometheus
ENABLE_METRICS="true"

# APM
APM_ENABLED="true"
APM_ENVIRONMENT="production"
```

### 2. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 3. Verify Setup

```bash
# Start the application
python main.py

# Check health endpoint
curl http://localhost:8000/health

# Check metrics endpoint
curl http://localhost:8000/metrics
```

---

## Sentry Configuration

### Getting Started with Sentry

1. **Create a Sentry Account**: https://sentry.io/signup/

2. **Create a New Project**:
   - Go to Settings → Projects → Create Project
   - Select "FastAPI" as the platform
   - Choose "Python" as the language

3. **Get Your DSN**:
   - Project Settings → Client Keys (DSN)
   - Copy the DSN URL

### Sentry Features

#### Error Tracking

All unhandled exceptions are automatically captured:

```python
# Manual error capture
from app.config.sentry import capture_exception

try:
    risky_operation()
except Exception as e:
    capture_exception(e, context={
        "user": {"id": user.id, "email": user.email},
        "tags": {"feature": "voice-api"},
        "extra": {"input_data": request_data}
    })
```

#### Performance Monitoring

Automatically tracks:
- Request latency (all API endpoints)
- Database query performance
- External API calls (OpenAI, Deepgram, etc.)
- Custom transactions

```python
# Custom transaction
import sentry_sdk

with sentry_sdk.start_transaction(op="voice_processing", name="call_analysis"):
    process_call_audio()
    analyze_sentiment()
    generate_response()
```

#### Profiling

CPU profiling to identify performance bottlenecks:

```bash
# Enable profiling in .env
SENTRY_PROFILES_SAMPLE_RATE=0.5  # Sample 50% of transactions
```

### Sentry Dashboard Access

- **Errors**: https://sentry.io/organizations/[org]/issues/
- **Performance**: https://sentry.io/organizations/[org]/performance/
- **Profiles**: https://sentry.io/organizations/[org]/profiling/

---

## Prometheus Metrics

### Available Metrics

All metrics are exposed at `/metrics`:

```bash
curl http://localhost:8000/metrics
```

#### HTTP Metrics

- `http_requests_total` - Total HTTP requests
- `http_request_duration_seconds` - Request latency histogram
- `http_requests_inprogress` - Currently in-flight requests

#### Endpoint Breakdown

Metrics are labeled by:
- `method` - HTTP method (GET, POST, etc.)
- `endpoint` - API endpoint path
- `status` - HTTP status code
- `path` - Request path template

### Example Queries

```promql
# Error rate by endpoint
rate(http_requests_total{status=~"5.."}[5m])

# P95 latency
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

# Requests per second
rate(http_requests_total[1m])
```

### Prometheus Setup

#### Local Development

```bash
# Install prometheus
docker run -d \
  -p 9090:9090 \
  -v $(pwd)/monitoring/prometheus.yml:/etc/prometheus/prometheus.yml \
  prom/prometheus

# Access dashboard at http://localhost:9090
```

#### Production with Grafana

1. **Deploy Prometheus**:
   ```bash
   # Using Docker
   docker run -d \
     --name prometheus \
     -p 9090:9090 \
     -v prometheus.yml:/etc/prometheus/prometheus.yml \
     -v prometheus_data:/prometheus \
     prom/prometheus
   ```

2. **Deploy Grafana**:
   ```bash
   docker run -d \
     --name grafana \
     -p 3000:3000 \
     grafana/grafana
   ```

3. **Import Dashboard**:
   - Go to Grafana → Dashboards → Import
   - Use ID: 10826 (FastAPI dashboard)

---

## Health Checks

### Endpoints

#### `/health` - Liveness Probe

```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "version": "2.0.0",
  "python": "3.12+",
  "environment": "production"
}
```

#### `/ready` - Readiness Probe

```bash
curl http://localhost:8000/ready
```

Response:
```json
{
  "status": "ready"
}
```

### Kubernetes Configuration

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: voice-kraliki
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: backend
        image: voice-kraliki:latest
        ports:
        - containerPort: 8000
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
```

---

## Performance Monitoring

### Custom Metrics

Create custom metrics in your endpoints:

```python
from prometheus_client import Counter, Histogram, Gauge

# Define metrics
voice_calls_total = Counter(
    'voice_calls_total',
    'Total voice calls processed',
    ['provider', 'status']
)

call_duration_seconds = Histogram(
    'call_duration_seconds',
    'Voice call duration',
    ['provider']
)

active_calls = Gauge(
    'active_calls',
    'Currently active voice calls',
    ['provider']
)

# Use in code
@router.post("/calls")
async def create_call(call_data: CallRequest):
    active_calls.labels(provider=call_data.provider).inc()
    
    try:
        start_time = time.time()
        result = process_call(call_data)
        duration = time.time() - start_time
        
        call_duration_seconds.labels(provider=call_data.provider).observe(duration)
        voice_calls_total.labels(provider=call_data.provider, status='success').inc()
        
        return result
    except Exception as e:
        voice_calls_total.labels(provider=call_data.provider, status='error').inc()
        raise
    finally:
        active_calls.labels(provider=call_data.provider).dec()
```

### Database Performance Monitoring

Sentry automatically tracks SQLAlchemy queries:

```python
# Enable query logging in .env
LOG_LEVEL="DEBUG"
```

### External API Monitoring

Track API calls to providers:

```python
import sentry_sdk

with sentry_sdk.start_transaction(op="http.client", name="openai_chat") as transaction:
    response = openai.ChatCompletion.create(...)
    transaction.set_data("response_tokens", response.usage.total_tokens)
```

---

## Alerting

### Prometheus Alerts

Configure alerts in `monitoring/prometheus-alerts.yml`:

```yaml
groups:
  - name: voice_kraliki_alerts
    interval: 30s
    rules:
      # High error rate
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
          
      # High latency
      - alert: HighLatency
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "P95 latency exceeds 1s"
          
      # Service down
      - alert: ServiceDown
        expr: up{job="voice-kraliki"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Voice Kraliki service is down"
```

### Sentry Alerts

1. **Create Alert Rule**:
   - Go to Settings → Alerts → New Alert Rule
   - Set conditions (error rate, latency, etc.)
   - Configure notifications (Email, Slack, PagerDuty)

2. **Example Alert Rules**:
   - Error rate > 5% for 5 minutes
   - P95 latency > 2 seconds
   - New errors in production

---

## Production Deployment

### Environment Variables

Production setup:

```bash
# Enable full monitoring
SENTRY_DSN="https://production-dsn@sentry.io/123"
SENTRY_TRACES_SAMPLE_RATE=0.1
SENTRY_PROFILES_SAMPLE_RATE=0.05
RELEASE_VERSION="2.0.0"

ENABLE_METRICS="true"
APM_ENABLED="true"
APM_ENVIRONMENT="production"

# Performance tuning
WORKERS=4
LOG_LEVEL="INFO"
```

### Docker Deployment

```yaml
# docker-compose.yml
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - SENTRY_DSN=${SENTRY_DSN}
      - ENABLE_METRICS=true
      - ENVIRONMENT=production
    depends_on:
      - prometheus
      - grafana

  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - ./monitoring/prometheus-alerts.yml:/etc/prometheus/alerts.yml

  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    volumes:
      - grafana_data:/var/lib/grafana

volumes:
  grafana_data:
```

### PM2 Deployment

```javascript
// ecosystem.config.js
module.exports = {
  apps: [{
    name: 'voice-kraliki',
    script: 'main.py',
    interpreter: 'python3',
    instances: 4,
    exec_mode: 'cluster',
    env: {
      ENVIRONMENT: 'production',
      SENTRY_DSN: process.env.SENTRY_DSN,
      ENABLE_METRICS: 'true'
    },
    error_file: './logs/error.log',
    out_file: './logs/out.log',
    log_date_format: 'YYYY-MM-DD HH:mm:ss'
  }]
};
```

---

## Monitoring Checklist

- [ ] Configure Sentry DSN
- [ ] Set trace sampling rates
- [ ] Enable profiling (optional)
- [ ] Configure Prometheus
- [ ] Set up Grafana dashboards
- [ ] Configure alert rules
- [ ] Test health endpoints
- [ ] Deploy to production
- [ ] Verify metrics are being collected
- [ ] Configure log aggregation (if using ELK, etc.)
- [ ] Set up on-call rotation

---

## Troubleshooting

### Metrics not showing

```bash
# Check if metrics endpoint is accessible
curl http://localhost:8000/metrics

# Check ENABLE_METRICS environment variable
echo $ENABLE_METRICS

# Check application logs for monitoring errors
tail -f logs/app.log | grep -i metrics
```

### Sentry not capturing errors

```bash
# Verify Sentry DSN is set
echo $SENTRY_DSN

# Check application logs
tail -f logs/app.log | grep -i sentry

# Test manual capture
python -c "from app.config.sentry import capture_exception; import sentry_sdk; sentry_sdk.capture_exception(Exception('test'))"
```

### High latency alerts

1. Check Sentry performance dashboard
2. Identify slow endpoints
3. Review database query performance
4. Check external API response times
5. Consider caching strategies

---

## Resources

- [Sentry Documentation](https://docs.sentry.io/)
- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Dashboards](https://grafana.com/grafana/dashboards/)
- [FastAPI Instrumentation](https://github.com/trallnag/prometheus-fastapi-instrumentator)
