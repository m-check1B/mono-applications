# Deployment Guide - Operator Demo 2026

**Version:** 1.0.0
**Stack:** Python/FastAPI + SvelteKit
**Status:** Production Ready

## Quick Start

```bash
# Clone repository
git clone https://github.com/m-check1B/operator-demo-2026.git
cd operator-demo-2026

# Deploy with PM2 (recommended)
./deploy.sh pm2

# OR Deploy with Docker
./deploy.sh docker
```

## Prerequisites

- **Node.js:** 20+ and npm
- **Python:** 3.11+
- **PostgreSQL:** 15+ (for production)
- **PM2:** (will be installed automatically)
- **Docker:** (optional, for container deployment)

## Environment Setup

### 1. Configure Environment Variables

```bash
# For production, copy and edit the production template
cp .env.production .env
nano .env  # Edit with your values
```

**Critical variables to change:**
- `SECRET_KEY` - Generate random 64-char string
- `JWT_SECRET` - Generate random JWT secret
- `DATABASE_URL` - Your PostgreSQL connection string
- All API keys (OpenAI, Gemini, Twilio, etc.)

### 2. Frontend Environment

```bash
# Edit frontend environment
nano frontend/.env

# Key variables:
PUBLIC_BACKEND_URL=https://api.your-domain.com
PUBLIC_WS_URL=wss://api.your-domain.com
```

## Database Setup

### PostgreSQL Installation

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install postgresql postgresql-contrib

# Start PostgreSQL
sudo systemctl start postgresql
```

### Create Database

```bash
# Run setup script
sudo -u postgres psql -f backend/setup_database.sql

# OR manually:
sudo -u postgres psql
CREATE DATABASE operator_demo;
CREATE USER operator_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE operator_demo TO operator_user;
\q
```

## Deployment Methods

### Method 1: PM2 Deployment (Recommended)

```bash
# Install dependencies
cd backend && pip3 install -r requirements.txt && cd ..
cd frontend && npm install && npm run build && cd ..

# Start with PM2
pm2 start ecosystem.config.js --env production

# Save PM2 configuration
pm2 save
pm2 startup  # Follow instructions to enable auto-start
```

**PM2 Commands:**
```bash
pm2 status          # Check status
pm2 logs            # View logs
pm2 monit           # Real-time monitoring
pm2 restart all     # Restart services
pm2 stop all        # Stop services
pm2 delete all      # Remove from PM2
```

### Method 2: Docker Deployment

```bash
# Build and start
docker-compose -f docker-compose.prod.yml up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Method 3: Manual Deployment

```bash
# Backend (Terminal 1)
cd backend
pip3 install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Frontend (Terminal 2)
cd frontend
npm install
npm run build
npm run preview -- --port 3000 --host 0.0.0.0
```

## Production Checklist

### Security

- [ ] Change all default secrets in `.env`
- [ ] Use HTTPS (configure reverse proxy)
- [ ] Enable CORS for your domain only
- [ ] Set `DEBUG=false` in production
- [ ] Use strong database password
- [ ] Configure firewall rules

### Database

- [ ] PostgreSQL installed and configured
- [ ] Database created and initialized
- [ ] Regular backup strategy in place
- [ ] Connection pooling configured

### Monitoring

- [ ] PM2 logs configured
- [ ] Health endpoints tested (`/health`)
- [ ] Error tracking setup (Sentry optional)
- [ ] Resource monitoring (CPU/Memory)

### Performance

- [ ] Frontend built in production mode
- [ ] API rate limiting configured
- [ ] Static assets cached
- [ ] Database indexes created

## Reverse Proxy Setup (Nginx)

```nginx
# /etc/nginx/sites-available/operator-demo

# Backend API
server {
    listen 80;
    server_name api.your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}

# Frontend
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

Enable sites:
```bash
sudo ln -s /etc/nginx/sites-available/operator-demo /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## SSL/TLS with Let's Encrypt

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get certificates
sudo certbot --nginx -d your-domain.com -d api.your-domain.com

# Auto-renewal
sudo certbot renew --dry-run
```

## Troubleshooting

### Backend won't start

```bash
# Check Python version
python3 --version  # Should be 3.11+

# Check dependencies
pip3 install -r backend/requirements.txt

# Check logs
pm2 logs operator-demo-backend
```

### Frontend build fails

```bash
# Clear cache
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run build
```

### Database connection issues

```bash
# Test connection
psql -U operator_user -d operator_demo -h localhost

# Check PostgreSQL status
sudo systemctl status postgresql

# View PostgreSQL logs
sudo tail -f /var/log/postgresql/*.log
```

### Port conflicts

```bash
# Check what's using ports
sudo lsof -i :8000  # Backend
sudo lsof -i :3000  # Frontend

# Kill process using port
sudo kill -9 $(sudo lsof -t -i:8000)
```

## Health Checks

```bash
# Backend health
curl http://localhost:8000/health

# Frontend health
curl http://localhost:3000

# Full system check
./scripts/test-backend.sh
./scripts/test-frontend.sh
```

## Backup Strategy

### Database Backup

```bash
# Create backup
pg_dump -U operator_user operator_demo > backup_$(date +%Y%m%d).sql

# Restore backup
psql -U operator_user operator_demo < backup_20251012.sql
```

### Application Backup

```bash
# Backup entire application
tar -czf operator-demo-backup-$(date +%Y%m%d).tar.gz \
  --exclude=node_modules \
  --exclude=__pycache__ \
  --exclude=.git \
  .
```

## Monitoring with PM2

```bash
# Install PM2 web monitoring (optional)
pm2 install pm2-logrotate
pm2 set pm2-logrotate:max_size 10M
pm2 set pm2-logrotate:retain 7

# Enable web dashboard
pm2 web
```

## Updates and Maintenance

```bash
# Pull latest changes
git pull origin develop

# Update dependencies
cd backend && pip3 install -r requirements.txt && cd ..
cd frontend && npm install && npm run build && cd ..

# Restart services
pm2 restart all

# Zero-downtime reload
pm2 reload all
```

## Support

For issues or questions:
- Check logs: `pm2 logs`
- Backend logs: `logs/backend-*.log`
- Frontend logs: `logs/frontend-*.log`
- GitHub Issues: https://github.com/m-check1B/operator-demo-2026/issues

---

*Deployment guide for operator-demo-2026 - Production Ready Application*