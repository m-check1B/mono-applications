# Security Documentation

## Overview

Speak by Kraliki handles sensitive employee feedback data. This document outlines security measures and best practices.

## Authentication

### User Authentication (HR/CEO)

| Mechanism | Details |
|-----------|---------|
| Password hashing | bcrypt with cost factor 12 |
| Access tokens | JWT, HS256 signed, 15-minute expiry |
| Refresh tokens | JWT, HS256 signed, 7-day expiry |
| Session management | Stateless (token-based) |

**Token structure:**
```json
{
  "sub": "user-uuid",
  "company_id": "company-uuid",
  "role": "owner",
  "exp": 1704067200,
  "iat": 1704066300
}
```

### Employee Authentication

| Mechanism | Details |
|-----------|---------|
| Magic links | Cryptographically random tokens |
| Token length | 32 characters (URL-safe base64) |
| Token expiry | 7 days from generation |
| Single use | Token valid until conversation complete |

**Magic link format:**
```
https://app.example.com/v/{token}
```

## Authorization

### Role-Based Access Control

| Role | Permissions |
|------|-------------|
| `owner` | Full company access, user management |
| `manager` | Department-filtered access |
| `employee` | Own data only (via magic link) |

### Endpoint Protection

```python
# Owner/Manager only
@router.get("/surveys")
async def list_surveys(
    user: User = Depends(get_current_user)  # Validates JWT
):
    # Automatically filtered by company_id from token
    pass

# Employee only (magic link)
@router.get("/employee/transcript")
async def get_transcript(
    token: str = Query(...)
):
    employee = await validate_magic_link(token)
    # Access limited to own conversation
    pass
```

## Data Protection

### Encryption

| Data | At Rest | In Transit |
|------|---------|------------|
| Passwords | bcrypt hash | TLS 1.3 |
| Transcripts | Database encryption | TLS 1.3 |
| API traffic | N/A | TLS 1.3 |
| WebSocket | N/A | WSS (TLS) |

### Anonymization

Employee responses are anonymized for management:

```
Real: john.doe@company.com
Anonymous: EMP-A1B2C3D4
```

Anonymous IDs are:
- Generated per conversation
- Not linkable to employee identity
- Consistent within single survey cycle

### Data Minimization

- Only collect necessary information
- Transcripts can be redacted by employees
- Personal data deleted on request (GDPR)

## Privacy Features

### Trust Layer

1. **Consent Screen**
   - Shown before conversation starts
   - Explains data usage
   - Employee must explicitly consent

2. **Transcript Review**
   - Employees can review before submission
   - Can redact specific messages
   - Final approval before analysis

3. **Data Deletion**
   - One-click delete all personal data
   - Includes transcripts, responses, metadata
   - Immediate and permanent

### Anonymity Guarantees

- Managers never see individual responses
- Only aggregated sentiment and topics
- Department-level is minimum granularity
- Minimum 5 responses before showing department data

## API Security

### Rate Limiting

```python
# Per-endpoint limits
POST /auth/login:     5/minute per IP
POST /auth/register:  3/minute per IP
GET /surveys:         60/minute per user
WebSocket:            1 connection per token
```

### Input Validation

All inputs validated with Pydantic:

```python
class SurveyCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: str | None = Field(None, max_length=2000)
    frequency: Literal["weekly", "monthly", "quarterly"]
```

### CORS Configuration

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://app.example.com"],  # Specific origins
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["*"],
)
```

### Security Headers

```python
@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000"
    return response
```

## Infrastructure Security

### Environment Variables

**Never commit to source control:**
- `SECRET_KEY`
- `DATABASE_URL` (with credentials)
- `GEMINI_API_KEY`
- `RESEND_API_KEY`
- `STRIPE_SECRET_KEY`

**Use:**
- `.env` files (gitignored)
- Docker secrets
- Cloud secret managers (AWS SSM, GCP Secret Manager)

### Database Security

```sql
-- Separate application user with minimal privileges
CREATE USER vop_app WITH PASSWORD 'secure_password';
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO vop_app;

-- No direct database access from internet
-- Database only accessible from application container
```

### Network Security

```
Internet → WAF/CDN → Load Balancer → Application
                                          │
                                    Private Network
                                          │
                                      Database
```

- Database not exposed to public internet
- All traffic over TLS
- WebSocket upgraded from HTTPS only

## Compliance

### GDPR Compliance

| Right | Implementation |
|-------|----------------|
| Right to access | `/employee/transcript` endpoint |
| Right to rectification | Transcript redaction |
| Right to erasure | `/employee/data` DELETE endpoint |
| Right to portability | Export transcript as JSON |

### Data Processing

- Only process data with explicit consent
- Purpose limitation (employee feedback only)
- Storage limitation (retention policies)
- Integrity (audit logs)

### Audit Logging

```python
# Log security events
logger.info(f"User {user_id} accessed survey {survey_id}")
logger.warning(f"Failed login attempt for {email}")
logger.error(f"Unauthorized access attempt: {details}")
```

## Incident Response

### Security Event Detection

Monitor for:
- Multiple failed login attempts
- Unusual API patterns
- Unauthorized data access
- Token abuse

### Response Procedure

1. **Detect** - Automated alerts or manual discovery
2. **Contain** - Revoke tokens, block IPs if needed
3. **Investigate** - Review logs, identify scope
4. **Remediate** - Fix vulnerability, update secrets
5. **Notify** - Inform affected users if data breach

### Secret Rotation

Rotate periodically:
- `SECRET_KEY`: Quarterly (invalidates all tokens)
- `GEMINI_API_KEY`: On suspicion of compromise
- Database passwords: Quarterly

## Security Checklist

### Development

- [ ] No secrets in code or git history
- [ ] Dependencies scanned for vulnerabilities
- [ ] Input validation on all endpoints
- [ ] SQL injection prevention (parameterized queries)
- [ ] XSS prevention (output encoding)

### Deployment

- [ ] TLS enabled everywhere
- [ ] Security headers configured
- [ ] Rate limiting enabled
- [ ] CORS properly restricted
- [ ] Database not publicly accessible
- [ ] Logging enabled
- [ ] Secrets in secure storage

### Operations

- [ ] Regular backups tested
- [ ] Audit logs reviewed
- [ ] Dependencies updated
- [ ] Security patches applied
- [ ] Access reviewed quarterly

## Vulnerability Reporting

Report security vulnerabilities to:
- Email: security@example.com
- Do not disclose publicly until fixed
- Response within 48 hours

## Dependencies

Keep dependencies updated and scan regularly:

```bash
# Python
pip-audit

# Node.js
npm audit
```

## References

- OWASP Top 10: https://owasp.org/Top10/
- GDPR: https://gdpr.eu/
- FastAPI Security: https://fastapi.tiangolo.com/tutorial/security/
