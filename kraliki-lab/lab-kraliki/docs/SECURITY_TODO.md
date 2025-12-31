# Lab by Kraliki - Security Implementation TODO

**Created:** 2025-12-28
**Status:** Prototype - NOT for production use without implementing these controls
**Linear Issue:** VD-521

---

## Summary

The admin dashboard (`scripts/admin_dashboard.py`) currently lacks production security controls. This document outlines the specific implementation steps required before any production or public-facing deployment.

**Current security measures:**
- Binds to `127.0.0.1` only (localhost) - good default
- No hardcoded credentials in code - good

**Missing security controls:**
- No authentication on any endpoint
- No authorization/RBAC
- No rate limiting
- HTTPS enforcement delegated to Traefik (not enforced at app level)
- No CSRF protection on form endpoints
- No audit logging for administrative actions

---

## Priority 1: JWT Authentication Middleware (CRITICAL)

### Overview

All endpoints in `admin_dashboard.py` are currently open. Before exposing via Traefik or any reverse proxy, JWT authentication must be implemented.

### Implementation Steps

#### Step 1: Add Dependencies

```bash
pip install PyJWT flask-limiter
```

Add to `requirements.txt`:
```
Flask>=2.0
PyJWT>=2.8.0
flask-limiter>=3.5.0
```

#### Step 2: Create JWT Middleware

Create `/home/adminmatej/github/applications/kraliki-lab/lab-kraliki/scripts/auth.py`:

```python
"""JWT Authentication Middleware for Lab by Kraliki Admin Dashboard."""

import os
import jwt
import functools
from datetime import datetime, timedelta
from flask import request, jsonify, g

# Configuration - MUST be set via environment variables
JWT_SECRET = os.environ.get('LAB_KRALIKI_JWT_SECRET')
JWT_ALGORITHM = 'HS256'
JWT_EXPIRY_HOURS = 24

if not JWT_SECRET:
    raise ValueError("LAB_KRALIKI_JWT_SECRET environment variable is required")


def generate_token(user_id: str, role: str = 'admin') -> str:
    """Generate a JWT token for a user."""
    payload = {
        'user_id': user_id,
        'role': role,
        'exp': datetime.utcnow() + timedelta(hours=JWT_EXPIRY_HOURS),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    """Decode and validate a JWT token."""
    return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])


def require_auth(f):
    """Decorator to require JWT authentication on an endpoint."""
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')

        if not auth_header:
            return jsonify({'error': 'Missing Authorization header'}), 401

        if not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Invalid Authorization header format'}), 401

        token = auth_header.split(' ')[1]

        try:
            payload = decode_token(token)
            g.current_user = payload
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401

        return f(*args, **kwargs)
    return decorated


def require_role(role: str):
    """Decorator to require a specific role."""
    def decorator(f):
        @functools.wraps(f)
        @require_auth
        def decorated(*args, **kwargs):
            if g.current_user.get('role') != role:
                return jsonify({'error': 'Insufficient permissions'}), 403
            return f(*args, **kwargs)
        return decorated
    return decorator
```

#### Step 3: Apply to Protected Routes

Modify `admin_dashboard.py` to apply authentication:

```python
from auth import require_auth, require_role

# Dashboard pages - require basic auth
@app.route("/")
@require_auth
def dashboard():
    ...

# API endpoints - require auth
@app.route("/api/metrics")
@require_auth
def api_metrics():
    ...

# Dangerous actions - require admin role
@app.route("/api/vms/<vm_id>/restart", methods=["POST"])
@require_role('admin')
def restart_vm(vm_id: str):
    ...

@app.route("/api/vms/<vm_id>/rebuild", methods=["POST"])
@require_role('admin')
def rebuild_vm(vm_id: str):
    ...
```

#### Step 4: Environment Configuration

Create `.env.example`:
```bash
# JWT Secret - MUST be a strong random string (32+ characters)
# Generate with: python -c "import secrets; print(secrets.token_hex(32))"
LAB_KRALIKI_JWT_SECRET=your-secret-here-minimum-32-characters

# Optional: Override default expiry (hours)
LAB_KRALIKI_JWT_EXPIRY_HOURS=24
```

---

## Priority 2: Rate Limiting (HIGH)

### Overview

API endpoints, especially `/api/vms/<vm_id>/restart` and `/api/vms/<vm_id>/rebuild`, must be rate-limited to prevent abuse.

### Implementation Steps

Add rate limiting to `admin_dashboard.py`:

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"  # Use Redis in production
)

# Apply stricter limits to dangerous endpoints
@app.route("/api/vms/<vm_id>/restart", methods=["POST"])
@limiter.limit("5 per hour")
@require_role('admin')
def restart_vm(vm_id: str):
    ...

@app.route("/api/vms/<vm_id>/rebuild", methods=["POST"])
@limiter.limit("2 per hour")
@require_role('admin')
def rebuild_vm(vm_id: str):
    ...
```

---

## Priority 3: HTTPS Enforcement (HIGH)

### Option A: Traefik-Level (Recommended)

Configure in Traefik:
```yaml
# /github/infra/traefik/dynamic/lab-kraliki.yml
http:
  routers:
    lab-kraliki:
      rule: "Host(`lab.verduona.dev`)"
      entrypoints:
        - websecure
      tls:
        certResolver: letsencrypt
      service: lab-kraliki
      middlewares:
        - lab-auth  # Add auth middleware if using Traefik auth
```

### Option B: Application-Level (Fallback)

Add to `admin_dashboard.py`:

```python
@app.before_request
def enforce_https():
    """Redirect HTTP to HTTPS in production."""
    if not request.is_secure and not app.debug:
        if request.headers.get('X-Forwarded-Proto', 'http') != 'https':
            url = request.url.replace('http://', 'https://', 1)
            return redirect(url, code=301)
```

---

## Priority 4: CSRF Protection (MEDIUM)

### Overview

Form endpoints (`/tickets/new`, `/alerts/<id>/resolve`) need CSRF protection.

### Implementation Steps

```python
from flask_wtf.csrf import CSRFProtect

csrf = CSRFProtect(app)

# Add CSRF token to templates:
# <input type="hidden" name="csrf_token" value="{{ csrf_token() }}"/>
```

---

## Priority 5: Audit Logging (MEDIUM)

### Overview

Administrative actions (restart VM, rebuild VM, resolve alert) should be logged with user identity.

### Implementation Steps

Add to `admin_dashboard.py`:

```python
import logging

audit_logger = logging.getLogger('audit')
audit_handler = logging.FileHandler('/var/log/lab-kraliki/audit.log')
audit_handler.setFormatter(
    logging.Formatter('%(asctime)s - %(message)s')
)
audit_logger.addHandler(audit_handler)
audit_logger.setLevel(logging.INFO)

def log_audit(action: str, resource: str, user: str, details: str = ''):
    """Log an administrative action."""
    audit_logger.info(f"ACTION={action} RESOURCE={resource} USER={user} DETAILS={details}")

# Example usage in restart_vm:
@app.route("/api/vms/<vm_id>/restart", methods=["POST"])
@require_role('admin')
def restart_vm(vm_id: str):
    log_audit('restart', f'vm:{vm_id}', g.current_user['user_id'])
    # ... rest of implementation
```

---

## Priority 6: Zitadel Integration (FUTURE)

### Overview

For production, integrate with the Zitadel identity server running at `zitadel.verduona.dev` instead of custom JWT.

### Implementation Steps

See: `/github/applications/speak-kraliki/backend/platform-packages/auth-core/` for reference implementation.

Key steps:
1. Register Lab by Kraliki as OIDC client in Zitadel
2. Use Zitadel JWT validation instead of custom JWT
3. Map Zitadel roles to Lab by Kraliki permissions

---

## Endpoints to Protect

| Endpoint | Current Auth | Required Auth | Priority |
|----------|--------------|---------------|----------|
| `GET /` | None | require_auth | Critical |
| `GET /vms` | None | require_auth | Critical |
| `GET /vms/<vm_id>` | None | require_auth | Critical |
| `GET /customers` | None | require_auth | Critical |
| `GET /alerts` | None | require_auth | Critical |
| `GET /tickets` | None | require_auth | Critical |
| `GET /tickets/new` | None | require_auth | Critical |
| `POST /tickets/new` | None | require_auth + CSRF | Critical |
| `POST /alerts/<id>/resolve` | None | require_auth + CSRF | Critical |
| `GET /api/metrics` | None | require_auth | Critical |
| `GET /api/vms` | None | require_auth | Critical |
| `GET /api/alerts` | None | require_auth | Critical |
| `POST /api/vms/<vm_id>/restart` | None | require_role('admin') + rate limit | Critical |
| `POST /api/vms/<vm_id>/rebuild` | None | require_role('admin') + rate limit | Critical |

---

## Security Checklist Before Production

- [ ] JWT_SECRET set as environment variable (min 32 chars)
- [ ] All routes decorated with `@require_auth` or `@require_role`
- [ ] Rate limiting configured and tested
- [ ] HTTPS enforced (Traefik or app-level)
- [ ] CSRF tokens on all forms
- [ ] Audit logging enabled
- [ ] `.env` added to `.gitignore`
- [ ] No hardcoded credentials
- [ ] Error messages don't leak sensitive info
- [ ] Session handling tested for security
- [ ] Input validation on all user inputs

---

## Current Mitigations

While these security controls are not implemented, the following mitigations are in place:

1. **Localhost binding only** - Dashboard binds to `127.0.0.1:8002`, not accessible from network
2. **No Traefik route yet** - Dashboard not exposed to internet
3. **Prototype status** - No real customer data in system

**WARNING:** Do NOT expose this dashboard via Traefik or any reverse proxy until Priority 1-3 items are implemented.

---

## References

- Flask-JWT documentation: https://pyjwt.readthedocs.io/
- Flask-Limiter: https://flask-limiter.readthedocs.io/
- OWASP Flask Security: https://cheatsheetseries.owasp.org/cheatsheets/Flask_Cheat_Sheet.html
- Zitadel OIDC: https://zitadel.com/docs/guides/integrate/login/oidc

---

*Document created by Claude Code for VD-521*
*Review required before implementation*
