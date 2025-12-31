# Manual Redis Security Fix Instructions

**Status:** Redis is running as LXD user - requires manual configuration

---

## Step 1: Locate Redis Installation

Redis is running under the `lxd` user, which means it's likely in a container. Run these commands to locate it:

```bash
# Check if Redis is in a Docker container
sudo docker ps | grep redis

# Check if Redis is in an LXD container
sudo lxc list | grep -i redis

# Check if Redis is a snap package
snap list | grep redis

# Find Redis process details
sudo ps aux | grep redis-server

# Find Redis config file
sudo find /etc -name "redis*.conf" 2>/dev/null
sudo find /var -name "redis*.conf" 2>/dev/null
sudo find /snap -name "redis*.conf" 2>/dev/null
```

---

## Step 2a: If Redis is in Docker Container

If you found Redis in Docker, secure it via docker-compose or docker run:

### Update docker-compose.yml
```yaml
services:
  redis:
    image: redis:7.4-alpine
    command: >
      redis-server
      --requirepass CHANGE_THIS_TO_STRONG_PASSWORD
      --bind 127.0.0.1
      --protected-mode yes
    ports:
      - "127.0.0.1:6379:6379"  # CRITICAL: Bind to localhost only
    volumes:
      - redis-data:/data
    restart: unless-stopped

volumes:
  redis-data:
```

### Or update Docker run command
```bash
# Stop current Redis
sudo docker stop <redis-container-id>

# Start with security
sudo docker run -d \
  --name redis-secure \
  -p 127.0.0.1:6379:6379 \
  -v redis-data:/data \
  redis:7.4-alpine \
  redis-server \
  --requirepass "YOUR_STRONG_PASSWORD_HERE" \
  --bind 127.0.0.1 \
  --protected-mode yes
```

---

## Step 2b: If Redis is in LXD Container

If Redis is in an LXD container:

```bash
# List containers
sudo lxc list

# Enter the container (replace 'container-name' with actual name)
sudo lxc exec <container-name> -- bash

# Once inside, find Redis config
find /etc -name "redis*.conf"

# Edit the config
nano /etc/redis/redis.conf  # or wherever you found it

# Make these changes:
# 1. Find and change: bind 0.0.0.0
#    Replace with:    bind 127.0.0.1 ::1

# 2. Find and uncomment: # requirepass foobared
#    Replace with:       requirepass YOUR_STRONG_PASSWORD_HERE

# 3. Add if not present:
#    protected-mode yes

# 4. Restart Redis inside container
systemctl restart redis-server
# OR
/etc/init.d/redis-server restart

# Exit container
exit
```

---

## Step 2c: If Redis is Installed Directly (System Service)

If Redis is a system service:

```bash
# Find config
sudo find / -name "redis.conf" -type f 2>/dev/null

# Common locations:
# /etc/redis/redis.conf
# /etc/redis.conf
# /usr/local/etc/redis.conf

# Edit config (replace path with your actual path)
sudo nano /etc/redis/redis.conf

# Make these critical changes:

# 1. BIND TO LOCALHOST ONLY
#    Find: bind 0.0.0.0
#    Change to: bind 127.0.0.1 ::1

# 2. REQUIRE PASSWORD
#    Find: # requirepass foobared
#    Change to: requirepass YOUR_STRONG_32_CHAR_PASSWORD

# 3. ENABLE PROTECTED MODE
#    Find: protected-mode no
#    Change to: protected-mode yes

# 4. DISABLE DANGEROUS COMMANDS (add at end of file)
rename-command FLUSHDB ""
rename-command FLUSHALL ""
rename-command CONFIG ""
rename-command SHUTDOWN ""
rename-command BGREWRITEAOF ""
rename-command BGSAVE ""
rename-command SAVE ""
rename-command DEBUG ""

# Save and exit (Ctrl+X, Y, Enter)

# Restart Redis
sudo systemctl restart redis-server
# OR
sudo systemctl restart redis
# OR
sudo service redis-server restart
```

---

## Step 3: Generate Strong Password

```bash
# Generate a strong 32-character password
openssl rand -base64 32 | tr -d "=+/" | cut -c1-32

# Save this password! You'll need it for:
# 1. Redis config (requirepass)
# 2. Application .env file (REDIS_PASSWORD)
```

---

## Step 4: Configure Firewall

Block Redis port from external access:

```bash
# Enable firewall
sudo ufw enable

# Block Redis port explicitly
sudo ufw deny 6379/tcp

# Allow only necessary ports
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS

# Verify
sudo ufw status verbose

# Should show:
# 6379/tcp       DENY IN     Anywhere
```

---

## Step 5: Verify Security Fix

```bash
# Check Redis binding
ss -tulpn | grep 6379

# Expected OUTPUT: 127.0.0.1:6379 (GOOD)
# Bad OUTPUT: 0.0.0.0:6379 (STILL VULNERABLE)

# Test authentication (should fail without password)
redis-cli -h 127.0.0.1 ping
# Expected: (error) NOAUTH Authentication required.

# Test with password (should work)
redis-cli -h 127.0.0.1 -a YOUR_PASSWORD ping
# Expected: PONG

# Run verification script
cd /home/adminmatej/github/applications/operator-demo-2026
bash scripts/verify-redis-security.sh
```

---

## Step 6: Update Application

Add Redis password to your application:

```bash
# Add to backend .env file
cd /home/adminmatej/github/applications/operator-demo-2026/backend
echo 'REDIS_PASSWORD=your_generated_password_here' >> .env

# Update application code to use:
# redis://:PASSWORD@localhost:6379/0
# OR
# redis://:PASSWORD@127.0.0.1:6379/0
```

In your application code (Python example):
```python
import os
import redis

redis_password = os.getenv('REDIS_PASSWORD')
redis_client = redis.Redis(
    host='127.0.0.1',
    port=6379,
    password=redis_password,
    decode_responses=True
)
```

---

## Step 7: Test Application

```bash
# Start your application
cd /home/adminmatej/github/applications/operator-demo-2026/backend
# Run your application and verify Redis connectivity

# Check logs for Redis connection errors
# If you see "NOAUTH" errors, check your password configuration
```

---

## Quick Reference Commands

### Check Current Status
```bash
# Is Redis running?
ps aux | grep redis

# What ports is it listening on?
ss -tulpn | grep 6379

# Can I connect without password? (should fail)
redis-cli ping
```

### Test Security
```bash
# From another machine (should fail)
nc -zv YOUR_SERVER_IP 6379

# From same machine (should require password)
redis-cli ping
```

---

## Verification Checklist

- [ ] Redis config file located and edited
- [ ] Redis bound to 127.0.0.1 only (not 0.0.0.0)
- [ ] Strong password (32+ chars) configured
- [ ] Protected mode enabled
- [ ] Dangerous commands disabled
- [ ] Redis service restarted
- [ ] Firewall blocks port 6379 from external
- [ ] Verification script passes all checks
- [ ] Application updated with password
- [ ] Application tested and working

---

## If You Get Stuck

### Common Issues

**1. Can't find Redis config**
```bash
# Check if Redis is using default config
redis-cli CONFIG GET dir
redis-cli CONFIG GET dbfilename

# Find Redis binary
which redis-server
ls -la $(which redis-server)
```

**2. Redis won't restart**
```bash
# Check logs
sudo journalctl -u redis-server -n 50
# OR
sudo tail -50 /var/log/redis/redis-server.log
```

**3. Application can't connect**
```bash
# Test connection manually
redis-cli -h 127.0.0.1 -a YOUR_PASSWORD ping

# Check .env file has correct password
cat backend/.env | grep REDIS_PASSWORD
```

**4. Still accessible from Internet**
```bash
# Check firewall
sudo ufw status verbose

# Check Redis binding again
ss -tulpn | grep 6379

# May need to restart Redis again
sudo systemctl restart redis-server
```

---

## Emergency Contact

If Redis is still exposed after following these steps:

1. **Immediate action:** Stop Redis entirely
   ```bash
   sudo systemctl stop redis-server
   # OR
   sudo docker stop <redis-container>
   ```

2. **Investigate:** Check what's accessing Redis
   ```bash
   sudo lsof -i :6379
   ```

3. **Get help:** The BSI notification will be sent again if the issue persists

---

## Next Steps After Fix

1. Review Redis logs for unauthorized access:
   ```bash
   sudo tail -100 /var/log/redis/redis-server.log
   ```

2. Consider rotating any secrets that may have been in Redis:
   - Session tokens (force logout all users)
   - API keys
   - OAuth tokens

3. Set up monitoring:
   ```bash
   # Add to crontab to check security hourly
   crontab -e
   # Add line:
   0 * * * * /home/adminmatej/github/applications/operator-demo-2026/scripts/verify-redis-security.sh
   ```

---

**IMPORTANT:** The vulnerability is that Redis is binding to `0.0.0.0:6379` (all interfaces) without authentication. The fix MUST change this to `127.0.0.1:6379` (localhost only) AND add a password.

---

*For automated fix (when Redis is in standard location), use:*
```bash
sudo bash scripts/fix-redis-security.sh
```
