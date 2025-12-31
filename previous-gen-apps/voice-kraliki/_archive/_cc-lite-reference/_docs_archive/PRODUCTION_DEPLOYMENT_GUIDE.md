# Voice by Kraliki Production Deployment Guide

## 🚀 Consolidated Docker Configuration - Production Ready

This guide covers the deployment of Voice by Kraliki using the consolidated, security-hardened Docker configuration that implements 100% production readiness.

## 📋 Prerequisites

### System Requirements
- **OS**: Linux (Ubuntu 20.04+ recommended)
- **RAM**: Minimum 8GB, Recommended 16GB
- **CPU**: Minimum 4 cores, Recommended 8 cores
- **Storage**: Minimum 100GB SSD, Recommended 500GB SSD
- **Network**: Static IP address, Domain name configured

### Software Requirements
- **Docker**: Version 24.0+
- **Docker Compose**: Version 2.20+
- **Git**: For code deployment
- **curl**: For health checks

### Security Requirements
- **Firewall**: UFW or iptables configured
- **SSL Certificate**: Valid TLS certificate for domain
- **Secrets Management**: Docker secrets or external vault

## 🔧 Installation Steps

### 1. Initial Server Setup

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
newgrp docker

# Install Docker Compose (if not included)
sudo apt install docker compose-plugin

# Verify installation
docker --version
docker compose version
```

### 2. Clone and Setup Application

```bash
# Clone the repository
git clone <your-cc-lite-repo-url> /opt/cc-lite
cd /opt/cc-lite

# Create required directories
sudo mkdir -p /opt/cc-lite/{data,logs,backups,cache,uploads}/{postgres,redis,app,nginx,prometheus,grafana,loki}
sudo chown -R $USER:$USER /opt/cc-lite
```

### 3. Configure Docker Secrets

```bash
# Run the secrets setup script
./deploy/scripts/setup-secrets.sh

# This will create all required Docker secrets:
# - cc_lite_jwt_secret
# - cc_lite_jwt_refresh_secret
# - cc_lite_db_password
# - cc_lite_redis_password
# - cc_lite_session_secret
# - cc_lite_cookie_secret
# - cc_lite_twilio_auth_token
# - cc_lite_openai_api_key
# - cc_lite_deepgram_api_key
```

### 4. Configure SSL Certificates

```bash
# Create SSL directory
mkdir -p /opt/cc-lite/deploy/ssl

# Copy your SSL certificates
sudo cp your-domain.crt /opt/cc-lite/deploy/ssl/cc-lite.crt
sudo cp your-domain.key /opt/cc-lite/deploy/ssl/cc-lite.key

# Set proper permissions
sudo chmod 600 /opt/cc-lite/deploy/ssl/*
```

### 5. Environment Configuration

```bash
# Copy the production environment template
cp /tmp/cc-lite-secrets/production.env.template .env.production

# Edit the environment file
nano .env.production

# Update the following variables:
# - CORS_ORIGIN=https://your-domain.com
# - WEBHOOK_BASE_URL=https://your-domain.com
# - TWILIO_ACCOUNT_SID=your_twilio_sid
# - TWILIO_PHONE_NUMBER=your_twilio_number
# - LINEAR_API_KEY=your_linear_key
# - LINEAR_TEAM_ID=your_linear_team
# - GRAFANA_DOMAIN=your-domain.com
```

### 6. Validate Configuration

```bash
# Run configuration validation
./deploy/scripts/validate-docker-config.sh

# This checks:
# ✅ Docker Compose syntax
# ✅ Security hardening
# ✅ Network configuration
# ✅ Health checks
# ✅ Resource limits
# ✅ Secrets management
# ✅ Supporting files
```

## 🚀 Deployment

### Option 1: Standard Deployment

```bash
# Build and start all services
docker compose -f docker compose.production.yml up -d

# Monitor deployment
docker compose -f docker compose.production.yml logs -f
```

### Option 2: Zero-Downtime Deployment

```bash
# For production updates with zero downtime
./deploy/scripts/zero-downtime-deploy.sh rolling

# Or blue-green deployment
./deploy/scripts/zero-downtime-deploy.sh blue-green
```

## 🔍 Service Architecture

### Services Included

1. **PostgreSQL Database** (postgres:15-alpine)
   - Production-optimized configuration
   - SCRAM-SHA-256 authentication
   - Health checks and monitoring

2. **Redis Cache** (redis:7-alpine)
   - Password-protected
   - AOF persistence enabled
   - Memory-optimized configuration

3. **Voice by Kraliki Application** (custom build)
   - Non-root user execution
   - Read-only container
   - Comprehensive health checks

4. **Nginx Reverse Proxy** (nginx:1.25-alpine)
   - SSL/TLS termination
   - Rate limiting and security headers
   - Static file serving

5. **Prometheus Monitoring** (prom/prometheus:latest)
   - Metrics collection from all services
   - Alert rules configured
   - 30-day retention

6. **Grafana Dashboards** (grafana/grafana:latest)
   - Pre-configured dashboards
   - Prometheus data source
   - Security hardened

7. **Loki Log Aggregation** (grafana/loki:latest)
   - Structured log collection
   - Log retention policies
   - Integration with Grafana

8. **Backup Service** (postgres:15-alpine)
   - Automated database backups
   - Configurable retention
   - Health monitoring

## 🔐 Security Features

### Network Security
- **Internal Networks**: Backend services isolated
- **Localhost Binding**: External services bound to 127.0.0.1
- **No Direct Exposure**: Database and cache not exposed externally

### Container Security
- **Non-root Users**: All services run as non-root
- **Capability Dropping**: ALL capabilities dropped by default
- **Read-only Containers**: Where applicable
- **Security Options**: no-new-privileges enabled

### Secrets Management
- **Docker Secrets**: All sensitive data in Docker secrets
- **No Hardcoded Values**: Passwords loaded from secrets files
- **External References**: API keys loaded from external sources

### SSL/TLS Configuration
- **Modern Protocols**: TLS 1.2 and 1.3 only
- **Strong Ciphers**: ECDHE ciphers preferred
- **HSTS Headers**: HTTP Strict Transport Security
- **Security Headers**: Comprehensive security headers

## 📊 Monitoring & Observability

### Health Checks
- **Application**: HTTP health endpoint
- **Database**: PostgreSQL connection check
- **Cache**: Redis ping command
- **Proxy**: Nginx status endpoint

### Metrics Collection
- **Application Metrics**: Custom business metrics
- **Infrastructure Metrics**: CPU, memory, disk, network
- **Database Metrics**: Connection count, query performance
- **Web Metrics**: Response times, error rates

### Log Aggregation
- **Structured Logging**: JSON format logs
- **Log Rotation**: Size and time-based rotation
- **Centralized Collection**: Loki aggregation
- **Search and Analysis**: Grafana integration

### Alerting Rules
- **Service Health**: Down services, failed health checks
- **Performance**: High response times, error rates
- **Resource Usage**: High CPU, memory, disk usage
- **Security**: Failed logins, rate limit hits

## 🔄 Backup Strategy

### Automated Backups
- **Database**: Daily PostgreSQL dumps
- **Redis**: Periodic RDB snapshots
- **Application Data**: File uploads and logs
- **Configuration**: Docker volumes and configs

### Backup Retention
- **Daily Backups**: Kept for 30 days
- **Weekly Backups**: Kept for 12 weeks
- **Monthly Backups**: Kept for 12 months
- **Cleanup**: Automated old backup removal

### Disaster Recovery
- **Point-in-time Recovery**: Transaction log shipping
- **Cross-region Replication**: Optional setup
- **Backup Validation**: Regular restore testing
- **Documentation**: Recovery procedures

## 🚨 Troubleshooting

### Common Issues

#### Services Not Starting
```bash
# Check service status
docker compose -f docker compose.production.yml ps

# Check service logs
docker compose -f docker compose.production.yml logs <service-name>

# Check resource usage
docker stats
```

#### Health Check Failures
```bash
# Test application health
curl http://127.0.0.1:3010/health

# Check dependencies
docker compose -f docker compose.production.yml exec app ping postgres
docker compose -f docker compose.production.yml exec app ping redis
```

#### Secret Access Issues
```bash
# List Docker secrets
docker secret ls

# Verify secret content (be careful!)
docker secret inspect <secret-name>

# Recreate secrets if needed
docker secret rm <secret-name>
echo "new_value" | docker secret create <secret-name> -
```

#### Network Connectivity Issues
```bash
# Check network configuration
docker network ls
docker network inspect cc_lite_internal

# Test inter-service communication
docker compose -f docker compose.production.yml exec app nslookup postgres
```

### Log Locations

- **Application Logs**: `/opt/cc-lite/logs/app/`
- **Nginx Logs**: `/opt/cc-lite/logs/nginx/`
- **Database Logs**: Docker container logs
- **System Logs**: `/var/log/docker/`

### Performance Tuning

#### Database Optimization
```bash
# Check database performance
docker compose -f docker compose.production.yml exec postgres psql -U cc_lite_user -d cc_light_prod -c "SELECT * FROM pg_stat_activity;"

# Analyze query performance
docker compose -f docker compose.production.yml exec postgres psql -U cc_lite_user -d cc_light_prod -c "SELECT query, mean_time, calls FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 10;"
```

#### Resource Monitoring
```bash
# Check resource usage
docker compose -f docker compose.production.yml exec app ps aux
docker compose -f docker compose.production.yml exec app free -h
docker compose -f docker compose.production.yml exec app df -h
```

## 🔄 Maintenance

### Regular Tasks

#### Weekly
- Review monitoring dashboards
- Check backup integrity
- Update system packages
- Rotate log files

#### Monthly
- Update Docker images
- Review security logs
- Test disaster recovery
- Performance optimization

#### Quarterly
- Security audit
- Dependency updates
- Configuration review
- Capacity planning

### Update Procedures

#### Application Updates
```bash
# Zero-downtime rolling update
./deploy/scripts/zero-downtime-deploy.sh rolling

# Blue-green deployment
./deploy/scripts/zero-downtime-deploy.sh blue-green
```

#### Infrastructure Updates
```bash
# Update Docker images
docker compose -f docker compose.production.yml pull

# Restart services one by one
docker compose -f docker compose.production.yml restart <service-name>
```

## 📈 Scaling

### Horizontal Scaling
- Add more application instances
- Load balancer configuration
- Database read replicas
- Redis clustering

### Vertical Scaling
- Increase resource limits
- Optimize database configuration
- Tune application parameters
- Monitor performance metrics

## 🛡️ Security Maintenance

### Regular Security Tasks
- Update security patches
- Rotate secrets and certificates
- Review access logs
- Update firewall rules

### Security Monitoring
- Failed authentication attempts
- Unusual traffic patterns
- Resource exhaustion attacks
- Data access anomalies

## 📞 Support

### Documentation
- [API Documentation](./docs/api/)
- [Architecture Guide](./docs/architecture/)
- [Security Policy](./docs/security/)

### Monitoring URLs
- **Application**: https://your-domain.com
- **Grafana**: http://127.0.0.1:3000
- **Prometheus**: http://127.0.0.1:9090

### Emergency Contacts
- **System Administrator**: your-admin@company.com
- **Development Team**: dev-team@company.com
- **Security Team**: security@company.com

---

## ✅ Production Readiness Checklist

- [ ] Docker secrets configured
- [ ] SSL certificates installed
- [ ] Environment variables set
- [ ] Firewall configured
- [ ] Monitoring enabled
- [ ] Backups tested
- [ ] Health checks passing
- [ ] Security headers enabled
- [ ] Log aggregation working
- [ ] Alert rules configured
- [ ] Disaster recovery tested
- [ ] Documentation updated

**🎉 Congratulations! Your Voice by Kraliki production deployment is ready.**