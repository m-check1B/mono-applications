# Docker Security Policy

**Effective Date:** October 15, 2025
**Last Updated:** October 15, 2025

---

## 🐳 Docker Security Requirements

### Container Configuration

#### Port Binding (CRITICAL)
✅ **REQUIRED:** All services MUST bind to `127.0.0.1` only

```yaml
# ✅ CORRECT
ports:
  - "127.0.0.1:6379:6379"
  - "127.0.0.1:5432:5432"
  - "127.0.0.1:8000:8000"

# ❌ WRONG - Exposes to Internet
ports:
  - "6379:6379"
  - "5432:5432"
  - "8000:8000"

# ❌ WRONG - Explicitly exposes to all interfaces
ports:
  - "0.0.0.0:6379:6379"
```

**Exception:** Only HTTP/HTTPS proxies (nginx, traefik) may bind to `0.0.0.0:80` and `0.0.0.0:443`

---

### Authentication

✅ **REQUIRED:** All database services MUST require authentication

```yaml
# Redis
redis:
  image: redis:7-alpine
  command: >
    redis-server
    --requirepass ${REDIS_PASSWORD}
    --protected-mode yes
  environment:
    - REDIS_PASSWORD=${REDIS_PASSWORD}
  ports:
    - "127.0.0.1:6379:6379"

# PostgreSQL
postgres:
  image: postgres:16-alpine
  environment:
    - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
    - POSTGRES_USER=${POSTGRES_USER}
  ports:
    - "127.0.0.1:5432:5432"
```

---

### Network Isolation

✅ **REQUIRED:** Use internal Docker networks

```yaml
services:
  backend:
    networks:
      - internal
      - frontend

  redis:
    networks:
      - internal  # Only accessible by backend

  postgres:
    networks:
      - internal  # Only accessible by backend

networks:
  internal:
    driver: bridge
    internal: true  # Not connected to outside world

  frontend:
    driver: bridge  # Can access Internet if needed
```

---

### User Permissions

✅ **REQUIRED:** Run containers as non-root when possible

```yaml
redis:
  image: redis:7-alpine
  user: "999:999"  # Non-root user

# Or in Dockerfile:
FROM redis:7-alpine
USER redis
```

❌ **AVOID:** Privileged mode

```yaml
# ❌ Only use if absolutely necessary
privileged: true
```

---

### Resource Limits

✅ **REQUIRED:** Set resource limits for all containers

```yaml
redis:
  image: redis:7-alpine
  deploy:
    resources:
      limits:
        cpus: '0.50'
        memory: 512M
      reservations:
        cpus: '0.25'
        memory: 256M
```

---

### Health Checks

✅ **REQUIRED:** Implement health checks

```yaml
redis:
  image: redis:7-alpine
  healthcheck:
    test: ["CMD", "redis-cli", "-a", "${REDIS_PASSWORD}", "ping"]
    interval: 10s
    timeout: 5s
    retries: 3
    start_period: 10s
```

---

### Security Options

✅ **RECOMMENDED:** Use security options

```yaml
services:
  backend:
    security_opt:
      - no-new-privileges:true
    cap_drop:
      - ALL
    cap_add:
      - NET_BIND_SERVICE  # Only if needed
    read_only: true  # If applicable
```

---

## 🔒 Secure Docker Compose Template

```yaml
version: '3.8'

services:
  # Frontend/Proxy (only service exposed)
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    networks:
      - frontend
    restart: unless-stopped
    security_opt:
      - no-new-privileges:true

  # Backend (internal only)
  backend:
    build: ./backend
    ports:
      - "127.0.0.1:8000:8000"  # Localhost only
    environment:
      - DATABASE_URL=postgresql://${DB_USER}:${DB_PASSWORD}@postgres:5432/${DB_NAME}
      - REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379/0
    networks:
      - internal
      - frontend
    restart: unless-stopped
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G

  # Redis (internal only, no host ports)
  redis:
    image: redis:7-alpine
    command: >
      redis-server
      --requirepass ${REDIS_PASSWORD}
      --protected-mode yes
      --rename-command FLUSHDB ""
      --rename-command FLUSHALL ""
      --rename-command CONFIG ""
    networks:
      - internal
    volumes:
      - redis-data:/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "-a", "${REDIS_PASSWORD}", "ping"]
      interval: 10s
      timeout: 5s
      retries: 3
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M

  # PostgreSQL (internal only, no host ports)
  postgres:
    image: postgres:16-alpine
    environment:
      - POSTGRES_USER=${DB_USER}
      - POSTGRES_PASSWORD=${DB_PASSWORD}
      - POSTGRES_DB=${DB_NAME}
    networks:
      - internal
    volumes:
      - postgres-data:/var/lib/postgresql/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER}"]
      interval: 10s
      timeout: 5s
      retries: 3
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G

networks:
  frontend:
    driver: bridge
  internal:
    driver: bridge
    internal: true  # Critical: Not connected to Internet

volumes:
  redis-data:
  postgres-data:
```

---

## 🛡️ Security Verification Checklist

### Before Deployment
- [ ] All port bindings use `127.0.0.1` or no host port
- [ ] All databases require authentication
- [ ] Strong passwords configured (32+ characters)
- [ ] Internal network configured
- [ ] Health checks implemented
- [ ] Resource limits set
- [ ] Non-root user where possible
- [ ] Security options configured
- [ ] No privileged mode (unless justified)
- [ ] Restart policy set

### After Deployment
- [ ] Verify port bindings: `docker ps | grep -E "6379|5432|27017"`
- [ ] Test authentication required
- [ ] Check containers running as non-root: `docker exec <container> whoami`
- [ ] Verify health checks: `docker inspect <container> | grep Health`
- [ ] Test Internet accessibility (should fail)
- [ ] Review logs for errors

---

## 🚫 Common Mistakes

### ❌ Exposing Database to Internet
```yaml
# WRONG
redis:
  ports:
    - "6379:6379"  # Exposed to 0.0.0.0
```

### ❌ No Authentication
```yaml
# WRONG
redis:
  image: redis:7-alpine
  # No password configured!
```

### ❌ No Network Isolation
```yaml
# WRONG - All services on default bridge
services:
  redis:
    # No networks specified
```

### ❌ Running as Root
```yaml
# WRONG
backend:
  user: root  # Unnecessary
```

---

## 🔍 Security Auditing

### Regular Checks

**Weekly:**
```bash
# Check port bindings
docker ps --format "table {{.Names}}\t{{.Ports}}"

# Check for containers running as root
docker ps -q | xargs docker inspect --format '{{.Name}} {{.Config.User}}'

# Check for privileged containers
docker ps -q | xargs docker inspect --format '{{.Name}} {{.HostConfig.Privileged}}'
```

**Monthly:**
```bash
# Scan images for vulnerabilities
docker scan <image>

# Or use Trivy
trivy image <image>

# Check for outdated images
docker images --format "{{.Repository}}:{{.Tag}}" | xargs -I {} docker pull {}
```

---

## 📋 Incident: Redis Exposure

### What Happened (October 15, 2025)
- Container `operator-demo-redis` exposed to `0.0.0.0:6379`
- No authentication configured
- Detected by BSI security scan
- **Severity:** P0 - Critical

### Resolution
- Stopped insecure container
- Created new container with:
  - Port binding: `127.0.0.1:6379:6379`
  - Authentication: 32-character password
  - Protected mode: Enabled
- Verified security
- Updated documentation

### Prevention
- This policy document created
- Verification scripts implemented
- All future containers must follow this policy

---

## 🛠️ Tools & Scripts

### Verification Script
```bash
#!/bin/bash
# Check Docker security

echo "=== Port Bindings ==="
docker ps --format "{{.Names}}: {{.Ports}}" | grep -E "6379|5432|27017|3306"

echo -e "\n=== Privileged Containers ==="
docker ps -q | xargs docker inspect --format '{{.Name}} {{.HostConfig.Privileged}}' | grep true || echo "None (good!)"

echo -e "\n=== Containers Running as Root ==="
docker ps -q | xargs docker inspect --format '{{.Name}} {{.Config.User}}' | grep -E "root|^$" || echo "None running as root (good!)"

echo -e "\n=== Network Configuration ==="
docker network ls
```

---

## 📚 References

- [Docker Security Best Practices](https://docs.docker.com/engine/security/)
- [CIS Docker Benchmark](https://www.cisecurity.org/benchmark/docker)
- [OWASP Docker Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Docker_Security_Cheat_Sheet.html)

---

**Policy Owner:** Infrastructure Team
**Approved:** October 15, 2025
**Next Review:** January 15, 2026
