# Webhook Security Configuration

This document describes the security measures implemented for webhook endpoints in the Operator Demo 2026 application.

## Overview

Webhook endpoints receive callbacks from external telephony providers (Twilio and Telnyx). These endpoints require robust security to prevent:
- Unauthorized webhook injection
- Replay attacks
- Denial of Service (DoS) attacks
- Data tampering

## Security Layers

The webhook security implementation uses four layers of defense (applied in order):

### 1. Rate Limiting
- **Limit**: 100 requests per minute per IP address
- **Purpose**: Prevent DoS attacks and abuse
- **Implementation**: Applied via `@limiter.limit(WEBHOOK_RATE_LIMIT)` decorator
- **Configuration**: `WEBHOOK_RATE_LIMIT` in `/backend/app/middleware/rate_limit.py`
- **Backend**: Redis-based rate limiting using slowapi

### 2. IP Whitelisting
- **Purpose**: Only allow webhooks from verified provider IP addresses
- **Validation**: Checks source IP against provider-specific whitelists
- **Configuration**: See `settings.py` (lines 173-199)
- **Supports**: Both single IPs and CIDR notation (e.g., `185.125.138.0/24`)

### 3. Signature Validation
- **Purpose**: Cryptographic verification of webhook authenticity
- **Twilio**: Uses HMAC-SHA256 with `X-Twilio-Signature` header
- **Telnyx**: Uses Ed25519 with `Telnyx-Signature-Ed25519` header
- **Implementation**: `_validate_webhook_signature()` in `telephony/routes.py`

### 4. Timestamp Validation
- **Purpose**: Prevent replay attacks
- **Timeout**: Webhooks older than 5 minutes (300 seconds) are rejected
- **Implementation**: Part of `_validate_webhook_signature()` function
- **Headers**: Checks `X-Twilio-Timestamp` or `Telnyx-Timestamp`

## Configuration

### IP Whitelist Settings

Located in `/backend/app/config/settings.py`:

```python
# Enable/disable IP whitelisting (set to False for development)
enable_webhook_ip_whitelist: bool = True

# Twilio IP whitelist
twilio_webhook_ips: list[str] = [
    "54.172.60.0",
    "54.244.51.0",
    "54.171.127.192",
    "35.156.191.128",
    "54.65.63.192",
    "54.169.127.128",
    "54.252.254.64",
    "177.71.206.192",
]

# Telnyx IP whitelist (supports CIDR notation)
telnyx_webhook_ips: list[str] = [
    "185.125.138.0/24",
    "185.125.139.0/24",
]
```

### Environment Variables

Add to your `.env` file:

```bash
# Disable IP whitelisting for local development
ENABLE_WEBHOOK_IP_WHITELIST=false

# Redis configuration for rate limiting
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Twilio credentials (required for signature validation)
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token

# Telnyx credentials (required for signature validation)
TELNYX_API_KEY=your_api_key
TELNYX_PUBLIC_KEY=your_ed25519_public_key
```

## Provider IP Addresses

### Twilio

Official documentation: https://www.twilio.com/docs/usage/webhooks/ip-addresses

The current whitelist includes IPs from:
- US East (Virginia)
- US West (Oregon)
- EU (Ireland)
- EU (Frankfurt)
- Asia Pacific (Singapore)
- Asia Pacific (Tokyo)
- Asia Pacific (Sydney)
- South America (São Paulo)

**Note**: Twilio periodically updates their IP ranges. Check their documentation regularly.

### Telnyx

Official documentation: https://developers.telnyx.com/docs/v2/development/webhook-security

Current IP ranges:
- `185.125.138.0/24` - Primary range
- `185.125.139.0/24` - Secondary range

**Note**: Telnyx uses CIDR notation for their IP ranges.

## Disabling Security for Development

For local development, you may need to disable IP whitelisting:

```python
# In .env
ENABLE_WEBHOOK_IP_WHITELIST=false
```

Alternatively, add your development IP or use a service like ngrok and add its IP range.

## Testing Webhook Security

### 1. Test IP Whitelisting

```bash
# This should be rejected (non-whitelisted IP)
curl -X POST http://localhost:8000/api/v1/telephony/webhooks/twilio \
  -H "Content-Type: application/json" \
  -d '{"test": "data"}'

# Response: 403 Forbidden - "Webhook rejected: IP not whitelisted"
```

### 2. Test Rate Limiting

```bash
# Send 101 requests in quick succession
for i in {1..101}; do
  curl -X POST http://localhost:8000/api/v1/telephony/webhooks/twilio \
    -H "Content-Type: application/json" \
    -d '{"test": "data"}'
done

# The 101st request should return:
# Response: 429 Too Many Requests
```

### 3. Test Signature Validation

Enable webhook validation in feature flags, then:

```bash
# Without signature - should be rejected
curl -X POST http://localhost:8000/api/v1/telephony/webhooks/twilio \
  -H "Content-Type: application/json" \
  -d '{"CallSid": "test"}'

# Response: 403 Forbidden - "Invalid webhook signature"
```

### 4. Test Timestamp Validation

The timestamp validation is part of signature validation. Webhooks with timestamps older than 5 minutes are automatically rejected.

## Security Best Practices

### 1. Keep IP Whitelists Updated
- Review provider documentation monthly
- Subscribe to provider security bulletins
- Use monitoring to detect rejected webhooks from new IPs

### 2. Monitor Failed Attempts
Check logs for patterns:
```bash
grep "Webhook rejected" /var/log/app.log
grep "Invalid webhook signature" /var/log/app.log
```

### 3. Use Environment-Specific Configuration
- **Development**: Disable IP whitelisting
- **Staging**: Enable all security features
- **Production**: Enable all security features + additional monitoring

### 4. Rate Limiting Tuning
Current limit: 100 requests/minute per IP

Adjust if needed in `rate_limit.py`:
```python
WEBHOOK_RATE_LIMIT = "200/minute"  # For high-volume scenarios
```

### 5. Emergency Access
If legitimate webhooks are being blocked:

1. Check logs for the source IP
2. Verify it's from the provider's documented ranges
3. Add to whitelist in `settings.py`
4. Restart the application

### 6. Signature Key Rotation
- Rotate Twilio auth tokens quarterly
- Rotate Telnyx public keys quarterly
- Update environment variables immediately after rotation
- Test webhook delivery after rotation

## Troubleshooting

### Issue: Webhooks Rejected from Legitimate IPs

**Symptoms**: 403 errors, logs show "IP not whitelisted"

**Solutions**:
1. Verify the IP in logs matches provider documentation
2. Add IP to whitelist in `settings.py`
3. Check if using CIDR notation correctly for Telnyx
4. Ensure `enable_webhook_ip_whitelist` is True

### Issue: Rate Limit Exceeded

**Symptoms**: 429 errors, "rate_limit_exceeded" in response

**Solutions**:
1. Check if provider is sending duplicate webhooks
2. Increase `WEBHOOK_RATE_LIMIT` if traffic is legitimate
3. Verify Redis is running and accessible
4. Check rate limit headers in response

### Issue: Signature Validation Failures

**Symptoms**: 403 errors, "Invalid webhook signature"

**Solutions**:
1. Verify credentials in `.env` match provider dashboard
2. Check webhook URL matches what's configured in provider
3. For Telnyx, ensure public key is in PEM format
4. Enable debug logging to see signature details

### Issue: Timestamp Too Old

**Symptoms**: Webhooks rejected with "timestamp too old"

**Solutions**:
1. Check server clock synchronization (NTP)
2. Verify provider timestamp format
3. Adjust timeout threshold if needed (currently 300 seconds)
4. Check network latency to webhook endpoint

## Architecture

```
Incoming Webhook Request
         |
         v
    [Rate Limiter]  ← Layer 1: 100/min per IP
         |
         v
   [IP Whitelist]   ← Layer 2: Provider IP verification
         |
         v
 [Signature Check]  ← Layer 3: HMAC/Ed25519 validation
         |
         v
 [Timestamp Check]  ← Layer 4: Replay attack prevention
         |
         v
   [Process Webhook]
```

## File Locations

- Configuration: `/backend/app/config/settings.py` (lines 173-199)
- IP Validation: `/backend/app/telephony/routes.py` (function `_validate_webhook_ip`)
- Signature Validation: `/backend/app/telephony/routes.py` (function `_validate_webhook_signature`)
- Rate Limiting: `/backend/app/middleware/rate_limit.py`
- Webhook Handler: `/backend/app/telephony/routes.py` (endpoint `/webhooks/{provider}`)

## Monitoring Recommendations

### Metrics to Track
1. Webhook request volume per provider
2. Rate limit hit count
3. IP whitelist rejection count
4. Signature validation failure count
5. Timestamp validation failure count

### Alerts to Configure
1. Spike in webhook rejections (possible attack)
2. New IPs attempting webhook delivery
3. Rate limit exceeded for extended period
4. Signature validation failures > 5% of traffic
5. Timestamp drift > 60 seconds

## Compliance Notes

- **PCI DSS**: IP whitelisting and signature validation help with network security requirements
- **SOC 2**: Comprehensive logging supports audit trail requirements
- **GDPR**: Webhook validation prevents unauthorized data access
- **HIPAA**: Defense-in-depth approach meets technical safeguard requirements

## Support

For issues related to:
- **Twilio webhooks**: https://support.twilio.com
- **Telnyx webhooks**: https://support.telnyx.com
- **Application security**: Contact your security team

## Changelog

- **2026-10-14**: Initial implementation with 4-layer security model
  - Added IP whitelisting for Twilio and Telnyx
  - Implemented rate limiting (100/min per IP)
  - Enhanced signature validation
  - Added timestamp replay protection
