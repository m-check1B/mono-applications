# CC-Light Subdomain Deployment Configuration

This directory contains all the configuration files needed for deploying CC-Light with a subdomain architecture.

## Architecture Overview

### Subdomain Setup
- **API Service**: `api.cc-lite` → `localhost:3010`
- **Frontend App**: `app.cc-lite` → `localhost:3007`

### Services
- **cc-lite-api**: Backend API server (port 3010)
- **cc-lite-frontend**: Frontend Vite preview server (port 3007)
- **cc-lite-campaign-worker**: Background worker for autonomous campaigns
- **cc-lite-backup**: Daily database and configuration backup
- **cc-lite-monitor**: Health monitoring for all services

## Configuration Files

### 1. PM2 Ecosystem (`ecosystem.config.js`)
```bash
# Start all services in production
pm2 start config/ecosystem.config.js --env production

# Start all services in development
pm2 start config/ecosystem.config.js --env development

# Manage services
./scripts/pm2-manage.sh start production
./scripts/pm2-manage.sh status
./scripts/pm2-manage.sh logs
```

### 2. Nginx Configuration (`nginx-subdomains.conf`)
```bash
# Install configuration
sudo cp config/nginx-subdomains.conf /etc/nginx/sites-available/cc-lite-subdomains
sudo ln -s /etc/nginx/sites-available/cc-lite-subdomains /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

**Requirements:**
- SSL certificates for `*.cc-lite` domain
- DNS records pointing `api.cc-lite` and `app.cc-lite` to your server

### 3. Environment Configuration

#### Production (`.env.subdomains`)
- Optimized for subdomain deployment
- Production-ready settings
- Multi-language support enabled
- Security hardening

#### Development (`.env.development`)
- Local development settings
- Debug logging enabled
- Relaxed security for development
- Local database configuration

## Deployment

### Automated Deployment
```bash
# Deploy to production
./scripts/deploy-subdomains.sh production

# Deploy to development
./scripts/deploy-subdomains.sh development

# Force rebuild dependencies
./scripts/deploy-subdomains.sh production true
```

### Manual Deployment Steps
```bash
# 1. Install dependencies
cd /home/adminmatej/github/apps/cc-lite
pnpm install --frozen-lockfile
pnpm run build

# 2. Setup environment
cp config/.env.subdomains .env
# Edit .env with your specific values

# 3. Configure nginx
sudo cp config/nginx-subdomains.conf /etc/nginx/sites-available/cc-lite-subdomains
sudo ln -s /etc/nginx/sites-available/cc-lite-subdomains /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx

# 4. Start services with PM2
pm2 start config/ecosystem.config.js --env production
pm2 save
pm2 startup
```

## Service Management

### PM2 Management Script
```bash
# Service control
./scripts/pm2-manage.sh start [production|development]
./scripts/pm2-manage.sh stop
./scripts/pm2-manage.sh restart [production|development]
./scripts/pm2-manage.sh reload [production|development]
./scripts/pm2-manage.sh delete

# Monitoring
./scripts/pm2-manage.sh status
./scripts/pm2-manage.sh logs [service] [lines]
./scripts/pm2-manage.sh follow [service]
./scripts/pm2-manage.sh monitor
./scripts/pm2-manage.sh health

# Maintenance
./scripts/pm2-manage.sh backup
./scripts/pm2-manage.sh startup
./scripts/pm2-manage.sh update [production|development]
```

### Health Monitoring
```bash
# Run single health check
node scripts/health-check.js check

# Start continuous monitoring (PM2 handles this automatically)
node scripts/health-check.js monitor
```

### Backup Management
```bash
# Run backup manually
./scripts/backup.sh

# Database only
./scripts/backup.sh --database-only

# Configuration only
./scripts/backup.sh --config-only
```

## Environment Variables

### Required Variables
```bash
# Database
DATABASE_URL="postgresql://cc_user:cc_password@localhost:5432/cc_light"

# API Keys
OPENAI_API_KEY="your_openai_api_key"
DEEPGRAM_API_KEY="your_deepgram_api_key"
ELEVENLABS_API_KEY="your_elevenlabs_api_key"

# JWT Secrets (generate new ones for production)
JWT_SECRET="your_jwt_secret_here"
JWT_REFRESH_SECRET="your_jwt_refresh_secret_here"

# Subdomain URLs
API_BASE_URL="https://api.cc-lite"
APP_BASE_URL="https://app.cc-lite"
FRONTEND_URL="https://app.cc-lite"
WEBHOOK_BASE_URL="https://api.cc-lite"

# Vite Frontend Variables
VITE_API_BASE_URL="https://api.cc-lite"
VITE_APP_BASE_URL="https://app.cc-lite"
```

### Optional Variables
```bash
# Twilio (for telephony features)
TWILIO_ACCOUNT_SID="your_account_sid"
TWILIO_AUTH_TOKEN="your_auth_token"
TWILIO_PHONE_NUMBER="+1234567890"

# Redis (for session storage)
REDIS_URL="redis://localhost:6379"

# Monitoring & Alerts
ALERT_EMAIL="admin@yourdomain.com"
SLACK_WEBHOOK="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"

# Multi-language settings
ENABLE_LANGUAGE_DETECTION=true
SUPPORTED_LANGUAGES="en,es,cs"
DEFAULT_LANGUAGE="en"
```

## SSL Certificate Setup

### Using Let's Encrypt
```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Get wildcard certificate
sudo certbot certonly --manual --preferred-challenges dns -d "*.cc-lite" -d "cc-lite"

# Verify certificate paths in nginx config match:
# /etc/letsencrypt/live/cc-lite/fullchain.pem
# /etc/letsencrypt/live/cc-lite/privkey.pem
```

### Certificate Renewal
```bash
# Test renewal
sudo certbot renew --dry-run

# Auto-renewal (add to crontab)
0 12 * * * /usr/bin/certbot renew --quiet
```

## DNS Configuration

Point these domains to your server IP:
- `api.cc-lite` → `YOUR_SERVER_IP`
- `app.cc-lite` → `YOUR_SERVER_IP`

Example DNS records:
```
api.cc-lite.    IN    A    YOUR_SERVER_IP
app.cc-lite.    IN    A    YOUR_SERVER_IP
```

## Security Considerations

### Firewall Rules
```bash
# Allow HTTP and HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Block direct access to application ports (optional)
sudo ufw deny 3010/tcp
sudo ufw deny 3007/tcp
```

### PM2 Security
- Services bind to `127.0.0.1` only (localhost)
- Nginx handles external requests and SSL termination
- Rate limiting enabled at nginx level
- Metrics endpoint restricted to localhost

### Application Security
- JWT tokens with separate refresh tokens
- Rate limiting on API endpoints
- Input validation and sanitization
- Security headers configured in nginx
- Regular security updates

## Monitoring & Maintenance

### Log Files
```bash
# PM2 logs
pm2 logs

# Application logs
tail -f /var/log/cc-lite/*.log

# Nginx logs
tail -f /var/log/nginx/api.cc-lite.*.log
tail -f /var/log/nginx/app.cc-lite.*.log
```

### Performance Monitoring
- PM2 built-in monitoring: `pm2 monit`
- Health check endpoint: `https://api.cc-lite/health`
- Application metrics: `https://api.cc-lite/metrics` (localhost only)

### Backup Schedule
- **Database**: Daily at 2 AM (automated via PM2 cron)
- **Configuration**: Daily with database backup
- **Uploads**: Daily if upload directory exists
- **Retention**: 30 days (configurable)

## Troubleshooting

### Common Issues

#### Services Not Starting
```bash
# Check PM2 status
pm2 list
pm2 logs

# Check application dependencies
cd /home/adminmatej/github/apps/cc-lite
pnpm install
pnpm run build

# Check environment configuration
cat .env
```

#### Nginx Configuration Issues
```bash
# Test nginx configuration
sudo nginx -t

# Check nginx error logs
sudo tail -f /var/log/nginx/error.log

# Reload nginx configuration
sudo systemctl reload nginx
```

#### SSL Certificate Issues
```bash
# Check certificate validity
sudo certbot certificates

# Test SSL configuration
openssl s_client -connect api.cc-lite:443 -servername api.cc-lite
openssl s_client -connect app.cc-lite:443 -servername app.cc-lite
```

#### Database Connection Issues
```bash
# Test database connection
psql -h localhost -U cc_user -d cc_light -c "SELECT 1;"

# Check database logs
sudo tail -f /var/log/postgresql/postgresql-*.log
```

### Performance Issues
```bash
# Check system resources
htop
df -h
free -m

# Check PM2 memory usage
pm2 list
pm2 describe cc-lite-api

# Restart services if needed
pm2 restart all
```

## Support

For issues and support:
1. Check application logs: `pm2 logs`
2. Check nginx logs: `sudo tail -f /var/log/nginx/*.log`
3. Run health checks: `node scripts/health-check.js check`
4. Check PM2 status: `pm2 list`

## Version Information

- **PM2 Configuration**: v2.0 (Subdomain Architecture)
- **Nginx Configuration**: v1.0 (SSL + Subdomains)
- **Health Monitoring**: v1.0
- **Backup System**: v1.0
- **Deployment Scripts**: v1.0