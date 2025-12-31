# Focus Lite Deployment Checklist

**Implementation Status:** ✅ **100% CODE COMPLETE**
**Database Status:** ⏳ **Requires PostgreSQL Setup**
**Deployment Ready:** ✅ **YES** (after DB configuration)

---

## Pre-Deployment Requirements

### 1. Database Setup (PostgreSQL)

**Current Status:** ⚠️ Not configured
**Required Actions:**

```bash
# Option A: Use existing PostgreSQL server
export DATABASE_URL="postgresql://user:password@localhost:5432/focus_lite"

# Option B: Start PostgreSQL with Docker
docker run --name focus-lite-postgres \
  -e POSTGRES_PASSWORD=your_password \
  -e POSTGRES_DB=focus_lite \
  -p 5432:5432 \
  -d postgres:15

# Option C: Install PostgreSQL locally
sudo apt-get install postgresql postgresql-contrib
sudo -u postgres createdb focus_lite
sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'your_password';"
```

**Update Backend Configuration:**
```bash
# backend/.env
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/focus_lite
```

### 2. Apply Database Migrations

**Migrations Ready:** ✅ 2 migrations created
- Migration 007: Add AI billing fields to user
- Migration 008: Rename metadata → item_metadata

```bash
cd /home/adminmatej/github/applications/focus-lite/backend

# Check current migration status
alembic current

# Apply all migrations
alembic upgrade head

# Verify migrations applied
alembic current  # Should show: 008 (head)
```

### 3. Environment Variables

**Backend** (`backend/.env`):
```env
# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/focus_lite

# JWT Secret
SECRET_KEY=your-secret-key-here-min-32-chars

# OpenRouter (System Key)
OPENROUTER_API_KEY=sk-or-v1-your-system-key

# CORS
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000

# Server
PORT=3017
HOST=127.0.0.1
```

**II-Agent** (`ii-agent/.env`):
```env
# Focus Lite Integration
FOCUS_API_BASE_URL=http://127.0.0.1:3017

# Anthropic API
ANTHROPIC_API_KEY=your-anthropic-key

# Database (PostgreSQL required)
DATABASE_URL=postgresql://postgres:password@localhost:5433/ii_agent

# Server
PORT=8765
HOST=127.0.0.1
```

**Frontend** (`frontend/.env`):
```env
# API Base URL
VITE_API_BASE_URL=http://localhost:3017
VITE_WS_BASE_URL=ws://localhost:8765
```

---

## Deployment Steps

### Step 1: Database Migration
```bash
cd /home/adminmatej/github/applications/focus-lite/backend
alembic upgrade head
```

**Expected Output:**
```
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade  -> 007, add ai billing fields to user
INFO  [alembic.runtime.migration] Running upgrade 007 -> 008, rename metadata to item_metadata
```

### Step 2: Start Backend Server
```bash
cd /home/adminmatej/github/applications/focus-lite/backend
uvicorn app.main:app --reload --host 127.0.0.1 --port 3017
```

**Health Check:**
```bash
curl http://localhost:3017/health
# Expected: {"status": "healthy"}

curl http://localhost:3017/docs
# Should load Swagger UI
```

### Step 3: Start II-Agent Server
```bash
cd /home/adminmatej/github/applications/focus-lite/ii-agent
python ws_server.py
```

**Health Check:**
```bash
# WebSocket connection test
wscat -c ws://localhost:8765/ws
# Should connect successfully
```

### Step 4: Start Frontend Server
```bash
cd /home/adminmatej/github/applications/focus-lite/frontend
npm run dev
```

**Health Check:**
```bash
curl http://localhost:5173
# Should return HTML
```

### Step 5: Verify All Services
```bash
# Backend
curl http://localhost:3017/health

# Frontend
curl http://localhost:5173

# II-Agent (requires wscat)
# npm install -g wscat
wscat -c ws://localhost:8765/ws
```

---

## Post-Deployment Verification

### 1. User Registration & Default Types
```bash
# Register a new user
curl -X POST http://localhost:3017/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "test123456",
    "name": "Test User"
  }'

# Login
curl -X POST http://localhost:3017/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "test123456"
  }'

# Get user profile (with JWT token)
curl -X GET http://localhost:3017/users/me \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Verify default knowledge types created
curl -X GET http://localhost:3017/knowledge/item-types \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Expected: 4 types (Ideas, Notes, Tasks, Plans)
```

### 2. Knowledge Hub

**Test via Browser:**
1. Navigate to `http://localhost:5173`
2. Login with test account
3. Go to `/dashboard/knowledge`
4. Verify:
   - Knowledge grid displays
   - Can create knowledge item
   - Can edit/delete items
   - AI chat is visible
   - Search works
   - Filter by type works

### 3. Agent Workbench

**Test via Browser:**
1. Navigate to `/dashboard/agent`
2. Click "Connect"
3. Should see: "Connection failed: 404" (backend endpoint)
4. Click "Initialize Agent"
5. Enter query: "Create a task called 'Test Integration'"
6. Verify:
   - WebSocket connects
   - Agent responds
   - Tool calls execute
   - Task created

### 4. Settings & BYOK

**Test via Browser:**
1. Navigate to `/dashboard/settings`
2. Click "API Keys" tab
3. Verify:
   - Usage stats display
   - Can enter OpenRouter key
   - Test button works
   - Save button works
   - Remove button works

### 5. Agent Tools API

```bash
# Get agent session token
TOKEN=$(curl -X POST http://localhost:3017/agent/sessions \
  -H "Authorization: Bearer YOUR_USER_JWT" \
  -s | jq -r '.agentToken')

# Test knowledge create
curl -X POST http://localhost:3017/agent-tools/knowledge/create \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "typeId": "IDEAS_TYPE_ID",
    "title": "Test Idea",
    "content": "This is a test"
  }'

# Test task create
curl -X POST http://localhost:3017/agent-tools/tasks \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Task",
    "description": "Test description"
  }'
```

---

## Troubleshooting

### Database Connection Failed
**Error:** `password authentication failed for user "postgres"`

**Solutions:**
1. Check PostgreSQL is running: `sudo systemctl status postgresql`
2. Verify DATABASE_URL in backend/.env
3. Test connection: `psql -U postgres -d focus_lite`
4. Reset password: `sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'newpass';"`

### Migration Failed
**Error:** `Target database is not up to date`

**Solutions:**
```bash
# Check current version
alembic current

# Stamp to specific version if needed
alembic stamp head

# Retry upgrade
alembic upgrade head
```

### Backend Won't Start
**Error:** `ModuleNotFoundError`

**Solutions:**
```bash
# Install dependencies
cd backend
pip install -r requirements.txt

# Verify imports
python -c "from app.main import app; print('OK')"
```

### Frontend Build Errors
**Error:** `Module not found`

**Solutions:**
```bash
# Install dependencies
cd frontend
npm install

# Clear cache
rm -rf node_modules .svelte-kit
npm install
npm run dev
```

### II-Agent WebSocket Won't Connect
**Error:** `Connection refused`

**Solutions:**
1. Check II-Agent is running on port 8765
2. Verify FOCUS_API_BASE_URL in ii-agent/.env
3. Check no firewall blocking port 8765

---

## Production Deployment

### Database Backup
```bash
# Before migration
pg_dump focus_lite > focus_lite_backup_$(date +%Y%m%d).sql

# Restore if needed
psql focus_lite < focus_lite_backup_YYYYMMDD.sql
```

### Nginx Configuration
```nginx
# /etc/nginx/sites-available/focus-lite

upstream backend {
    server 127.0.0.1:3017;
}

upstream ii_agent {
    server 127.0.0.1:8765;
}

server {
    listen 80;
    server_name focus-lite.example.com;

    # Frontend (SvelteKit build)
    location / {
        root /var/www/focus-lite/frontend/build;
        try_files $uri $uri/ /index.html;
    }

    # Backend API
    location /api {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # II-Agent WebSocket (internal only, don't expose)
    location /ws {
        deny all;  # Block public access
        proxy_pass http://ii_agent;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### Systemd Service Files

**Backend** (`/etc/systemd/system/focus-lite-backend.service`):
```ini
[Unit]
Description=Focus Lite Backend
After=network.target postgresql.service

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/focus-lite/backend
Environment="PATH=/var/www/focus-lite/backend/venv/bin"
ExecStart=/var/www/focus-lite/backend/venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 3017
Restart=always

[Install]
WantedBy=multi-user.target
```

**II-Agent** (`/etc/systemd/system/focus-lite-ii-agent.service`):
```ini
[Unit]
Description=Focus Lite II-Agent
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/focus-lite/ii-agent
Environment="PATH=/var/www/focus-lite/ii-agent/venv/bin"
ExecStart=/var/www/focus-lite/ii-agent/venv/bin/python ws_server.py
Restart=always

[Install]
WantedBy=multi-user.target
```

**Enable Services:**
```bash
sudo systemctl enable focus-lite-backend
sudo systemctl enable focus-lite-ii-agent
sudo systemctl start focus-lite-backend
sudo systemctl start focus-lite-ii-agent
```

---

## Monitoring & Logs

### Application Logs
```bash
# Backend logs
tail -f backend/logs/app.log

# II-Agent logs
tail -f ii-agent/logs/ii_agent.log

# Systemd logs
sudo journalctl -u focus-lite-backend -f
sudo journalctl -u focus-lite-ii-agent -f
```

### Health Monitoring
```bash
# Create health check script
cat > /usr/local/bin/focus-lite-health.sh << 'EOF'
#!/bin/bash
curl -f http://localhost:3017/health || exit 1
curl -f http://localhost:5173 || exit 1
EOF

chmod +x /usr/local/bin/focus-lite-health.sh

# Add to cron
echo "*/5 * * * * /usr/local/bin/focus-lite-health.sh" | crontab -
```

---

## Rollback Plan

### If Migration Fails
```bash
# Rollback to previous version
cd backend
alembic downgrade -1

# Or specific version
alembic downgrade 007
```

### If Deployment Fails
```bash
# Stop services
sudo systemctl stop focus-lite-backend
sudo systemctl stop focus-lite-ii-agent

# Restore database
psql focus_lite < focus_lite_backup_YYYYMMDD.sql

# Revert code
git checkout previous-working-commit

# Restart
sudo systemctl start focus-lite-backend
sudo systemctl start focus-lite-ii-agent
```

---

## Success Criteria

### All Green Checklist
- [ ] PostgreSQL running and accessible
- [ ] Migrations 007 and 008 applied successfully
- [ ] Backend starts without errors
- [ ] II-Agent starts without errors
- [ ] Frontend builds successfully
- [ ] User registration creates 4 default knowledge types
- [ ] Knowledge Hub UI loads and works
- [ ] Agent Workbench connects to II-Agent
- [ ] Settings & BYOK UI functional
- [ ] Agent Tools API returns 200 OK
- [ ] End-to-end: Create knowledge item via AI agent works

---

**Deployment Status:** ✅ **CODE COMPLETE - READY WHEN DATABASE CONFIGURED**

**Next Action:** Set up PostgreSQL and run migrations

**Support:** See TROUBLESHOOTING section or check logs
