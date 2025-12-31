# JWT Token Revocation Implementation

## Overview

This document describes the JWT token revocation mechanism implemented to prevent compromised tokens from being used. The system uses Redis as a distributed cache for fast token blacklisting and supports both individual token revocation and bulk user token revocation.

## Architecture

### Components

1. **Token Revocation Service** (`app/auth/token_revocation.py`)
   - Redis-backed token blacklist
   - Automatic expiration based on JWT expiration time
   - User-level token revocation support
   - Health check endpoint

2. **JWT Authentication Updates** (`app/auth/jwt_auth.py`)
   - Integrated revocation checking in token verification
   - Checks both individual token JTI and user-level revocation
   - Transparent integration with existing authentication flow

3. **API Endpoints** (`app/auth/routes.py`)
   - `POST /api/v1/auth/revoke` - Revoke current token
   - `POST /api/v1/auth/revoke-all` - Revoke all user tokens
   - `GET /api/v1/auth/revocation-status` - Health check

4. **Configuration** (`app/config/settings.py`)
   - Redis connection settings
   - Environment variable support

## Features

### 1. Individual Token Revocation

Revoke a specific JWT token by its JTI (JWT ID):

```python
# Automatically stores in Redis with TTL = token expiration time
revocation_service.revoke_token(jti, expires_at)
```

**Use Cases:**
- User logs out
- Suspicious activity detected
- Token compromise suspected

### 2. User-Level Token Revocation

Revoke all tokens for a specific user:

```python
# Stores revocation timestamp for user
revocation_service.revoke_all_user_tokens(user_id)
```

**Use Cases:**
- Password change
- Security incident
- Logout from all devices
- Account suspension

### 3. Automatic Expiration

Tokens are automatically removed from the revocation list when they expire naturally, minimizing Redis storage requirements.

### 4. Graceful Degradation

If Redis is unavailable:
- Token revocation fails safely (returns error to client)
- Token verification fails open (allows tokens) to prevent service disruption
- All Redis operations have error handling and logging

## API Usage

### Revoke Current Token

```bash
POST /api/v1/auth/revoke
Authorization: Bearer <token>

Response:
{
  "message": "Token revoked successfully",
  "jti": "abc123def456"
}
```

### Revoke All User Tokens

```bash
POST /api/v1/auth/revoke-all
Authorization: Bearer <token>

Response:
{
  "message": "All tokens revoked successfully",
  "user_id": "user-uuid-here"
}
```

### Check Revocation Service Health

```bash
GET /api/v1/auth/revocation-status

Response:
{
  "service": "token_revocation",
  "status": "healthy",
  "backend": "redis",
  "message": "Token revocation service is operational"
}
```

## Configuration

### Environment Variables

Add to your `.env` file:

```env
# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=  # Optional, leave empty if no password
```

### Settings

All Redis configuration is managed through `app/config/settings.py`:

```python
redis_host: str = "localhost"      # Redis server host
redis_port: int = 6379             # Redis server port
redis_db: int = 0                  # Redis database number (0-15)
redis_password: str | None = None  # Redis password (optional)
```

## Redis Data Structure

### Individual Token Revocation

```
Key:   revoked_token:{jti}
Value: "revoked"
TTL:   Token expiration time
```

Example:
```
Key: revoked_token:abc123def456
Value: "revoked"
TTL: 86400 seconds (24 hours)
```

### User Token Revocation

```
Key:   user_tokens:{user_id}
Value: ISO timestamp of revocation
TTL:   None (manual cleanup)
```

Example:
```
Key: user_tokens:550e8400-e29b-41d4-a716-446655440000
Value: "2025-10-14T10:30:00.000000"
TTL: -1 (no expiration)
```

## Security Considerations

### 1. Token Compromise Response

When a token is compromised:

1. **Immediate Action**: Call `/api/v1/auth/revoke` to blacklist the token
2. **User-Wide Action**: If multiple tokens may be compromised, use `/api/v1/auth/revoke-all`
3. **Monitoring**: Check logs for any usage of revoked tokens

### 2. Password Change Flow

Recommended flow when user changes password:

```python
# 1. Update password in database
update_user_password(user_id, new_password_hash)

# 2. Revoke all existing tokens
revocation_service.revoke_all_user_tokens(user_id)

# 3. Issue new token
new_token = auth.create_access_token(user_id, ...)
```

### 3. Account Suspension

When suspending a user account:

```python
# 1. Mark user as inactive in database
user.is_active = False

# 2. Revoke all tokens
revocation_service.revoke_all_user_tokens(user_id)
```

### 4. Rate Limiting

Consider adding rate limiting to revocation endpoints to prevent abuse:

```python
# Using slowapi or similar
@limiter.limit("5/minute")
@router.post("/revoke-all")
async def revoke_all_tokens(...):
    ...
```

## Performance Considerations

### Redis Connection Pool

The current implementation uses a single Redis connection. For production with high traffic, consider using a connection pool:

```python
self.redis_pool = redis.ConnectionPool(
    host=settings.redis_host,
    port=settings.redis_port,
    db=settings.redis_db,
    max_connections=10
)
self.redis_client = redis.Redis(connection_pool=self.redis_pool)
```

### Memory Usage

- Each revoked token uses approximately 50-100 bytes in Redis
- With 1 million revoked tokens: ~50-100 MB memory
- Automatic expiration prevents unbounded growth

### Lookup Performance

- Redis GET operations: O(1) complexity
- Typical latency: < 1ms for local Redis, < 5ms for remote Redis
- Minimal impact on authentication performance

## Monitoring and Operations

### Key Metrics to Monitor

1. **Revocation Service Health**
   - Redis connection status
   - Redis memory usage
   - Token revocation rate

2. **Token Usage**
   - Revoked tokens in Redis
   - Failed authentication attempts (may indicate compromised tokens)
   - Revocation endpoint usage patterns

3. **Performance**
   - Authentication latency (with revocation checks)
   - Redis response time
   - Redis connection errors

### Logging

The implementation includes comprehensive logging:

```python
# Token revoked
logger.info(f"Token revoked: {jti} (expires in {ttl}s)")

# Token check failed
logger.warning(f"Token with JTI {jti} has been revoked")

# User tokens revoked
logger.info(f"All tokens revoked for user: {user_id}")

# Redis errors
logger.error(f"Failed to connect to Redis: {e}")
```

### Health Checks

Use the health check endpoint in your monitoring:

```bash
# Example: Prometheus blackbox exporter or similar
curl http://localhost:8000/api/v1/auth/revocation-status
```

## Testing

### Manual Testing

1. **Test Single Token Revocation**:
```bash
# Login and get token
TOKEN=$(curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password"}' \
  | jq -r '.access_token')

# Verify token works
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/auth/me

# Revoke token
curl -X POST http://localhost:8000/api/v1/auth/revoke \
  -H "Authorization: Bearer $TOKEN"

# Verify token no longer works
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/auth/me
# Should return 401 Unauthorized
```

2. **Test User-Level Revocation**:
```bash
# Get multiple tokens for same user
TOKEN1=$(curl -X POST http://localhost:8000/api/v1/auth/login ...)
TOKEN2=$(curl -X POST http://localhost:8000/api/v1/auth/login ...)

# Revoke all with one token
curl -X POST http://localhost:8000/api/v1/auth/revoke-all \
  -H "Authorization: Bearer $TOKEN1"

# Both tokens should now be invalid
curl -H "Authorization: Bearer $TOKEN1" .../me  # Should fail
curl -H "Authorization: Bearer $TOKEN2" .../me  # Should fail
```

### Integration Tests

Example pytest test:

```python
import pytest
from datetime import datetime, timedelta
from app.auth.token_revocation import get_revocation_service

def test_token_revocation():
    service = get_revocation_service()
    jti = "test-jti-123"
    expires_at = datetime.utcnow() + timedelta(hours=1)

    # Revoke token
    assert service.revoke_token(jti, expires_at)

    # Check revocation
    assert service.is_token_revoked(jti)

    # Different token should not be revoked
    assert not service.is_token_revoked("different-jti")

def test_user_token_revocation():
    service = get_revocation_service()
    user_id = "test-user-123"

    # Revoke all user tokens
    assert service.revoke_all_user_tokens(user_id)

    # Check old token is revoked
    old_token_iat = datetime.utcnow() - timedelta(hours=1)
    assert service.is_token_revoked_for_user(user_id, old_token_iat)

    # New token should not be revoked
    new_token_iat = datetime.utcnow() + timedelta(seconds=5)
    assert not service.is_token_revoked_for_user(user_id, new_token_iat)
```

## Deployment Checklist

- [ ] Redis server is running and accessible
- [ ] Redis configuration is set in environment variables
- [ ] Redis has sufficient memory allocated
- [ ] Redis persistence is configured (optional, for audit trail)
- [ ] Monitoring is set up for Redis health
- [ ] Logging is configured and centralized
- [ ] Rate limiting is configured on revocation endpoints
- [ ] Documentation is updated for operations team
- [ ] Alert rules are configured for Redis failures
- [ ] Backup and recovery procedures are documented

## Troubleshooting

### Issue: "Redis not available, cannot revoke token"

**Cause**: Redis connection failed

**Solution**:
1. Verify Redis is running: `redis-cli ping`
2. Check Redis configuration in `.env`
3. Verify network connectivity
4. Check Redis logs for errors

### Issue: Token still works after revocation

**Possible Causes**:
1. Token doesn't have JTI claim (old tokens)
2. Redis connection failed during revocation
3. Multiple backend instances with separate Redis databases

**Solution**:
1. Ensure all new tokens include JTI (already implemented in `ed25519_auth.py`)
2. Check Redis health endpoint
3. Verify all backend instances use same Redis instance

### Issue: High Redis memory usage

**Cause**: Many revoked tokens in Redis

**Solution**:
1. Tokens auto-expire, so this is temporary
2. Monitor revocation rate - high rate may indicate attack
3. Consider shorter token expiration times
4. Check for tokens with very long TTL

## Future Enhancements

### 1. Distributed Revocation

For multi-region deployments, consider:
- Redis Cluster for horizontal scaling
- Redis Sentinel for high availability
- Cross-region replication

### 2. Audit Trail

Store revocation events in database:

```python
# Track who revoked what and when
RevocationAudit(
    jti=jti,
    user_id=user_id,
    revoked_by=admin_id,
    revoked_at=datetime.utcnow(),
    reason="Security incident"
)
```

### 3. Token Refresh Integration

Automatically revoke refresh tokens when access token is revoked:

```python
def revoke_token_with_refresh(access_jti, refresh_jti, expires_at):
    revoke_token(access_jti, expires_at)
    revoke_token(refresh_jti, refresh_expires_at)
```

### 4. Revocation Webhooks

Notify other services when tokens are revoked:

```python
# After revocation
await notify_webhook({
    "event": "token_revoked",
    "user_id": user_id,
    "timestamp": datetime.utcnow()
})
```

## References

- [RFC 7009: OAuth 2.0 Token Revocation](https://tools.ietf.org/html/rfc7009)
- [JWT Best Practices](https://tools.ietf.org/html/rfc8725)
- [Redis Documentation](https://redis.io/documentation)
- [OWASP JWT Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/JSON_Web_Token_for_Java_Cheat_Sheet.html)

## Support

For issues or questions:
1. Check this documentation
2. Review logs for error messages
3. Check Redis health endpoint
4. Contact the security team for security-related issues
