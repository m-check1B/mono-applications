# HW-011: Setup Redis Server on Port 6380

**Created:** 2025-12-20
**Blocks:** W2-001 (TL;DR bot), W2-002 (SenseIt bot), W2-003, W2-004
**Priority:** HIGH

## Problem
Both Telegram bots (TL;DR and SenseIt) require Redis for user session management and caching. Redis is not currently installed or running on this server.

The bots expect Redis at `localhost:6380`.

## What's Needed

### Option A: Install Redis via apt (Recommended)
```bash
# Install Redis
sudo apt update && sudo apt install -y redis-server

# Configure to listen on port 6380
sudo sed -i 's/port 6379/port 6380/' /etc/redis/redis.conf

# Bind to localhost only (security)
sudo sed -i 's/bind 127.0.0.1 ::1/bind 127.0.0.1/' /etc/redis/redis.conf

# Enable and start
sudo systemctl enable redis-server
sudo systemctl start redis-server

# Verify
redis-cli -p 6380 PING
```

### Option B: Run Redis in Docker
```bash
# Create compose file or add to existing
docker run -d \
  --name redis-bots \
  --restart unless-stopped \
  -p 127.0.0.1:6380:6379 \
  redis:alpine
```

## Verification
```bash
redis-cli -p 6380 PING
# Should return: PONG
```

## Time Estimate
5-10 minutes

---
**Status:** DONE

## Resolution
Redis was started via Docker on 2025-12-20:
```bash
docker run -d --name redis-bots --restart unless-stopped -p 127.0.0.1:6380:6379 redis:alpine
```
Verified with `docker exec redis-bots redis-cli PING` → PONG
