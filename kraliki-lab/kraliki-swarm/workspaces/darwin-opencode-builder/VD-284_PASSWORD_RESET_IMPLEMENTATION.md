# VD-284: CC-Lite Password Reset Email Implementation

## Task
Implement password reset email functionality for CC-Lite (P1 security feature)

## What Was Done

### Issue Identified
The password reset functionality was **already fully implemented** in:
- `backend/app/auth/database_routes.py` - Contains `forgot_password` and `reset_password` endpoints
- `backend/app/services/email_service.py` - Contains `send_password_reset_email` method
- `backend/app/models/user.py` - Has password reset token fields
- `backend/tests/test_password_reset.py` - Complete test suite

### Missing Piece
The `database_routes` router was **not registered** in `main.py`, making the endpoints inaccessible.

### Changes Made

**File: `backend/main.py`**

1. **Added import** (line ~33):
   ```python
   from app.auth.database_routes import router as database_auth_router
   ```

2. **Registered router** (line ~115):
   ```python
   app.include_router(database_auth_router)
   ```

3. **Fixed lint issues**:
   - Removed unused `fastapi.responses.JSONResponse` import
   - Sorted imports alphabetically (ruff requirement)
   - Sorted router registrations alphabetically

## Verification

### Code Quality
- Python syntax: PASS (py_compile)
- Ruff lint: PASS (when run with `uv tool run ruff`)
- No new logic added, just router registration

### Endpoints Now Available
- `POST /api/v1/auth/forgot-password` - Request password reset email
- `POST /api/v1/auth/reset-password` - Reset password with token

### Security Features Implemented
- Secure token generation (32-byte URL-safe tokens)
- 1-hour token expiration
- Token validation before password reset
- Clears failed login attempts and account lock on reset
- Separate password reset and email verification tokens

## Notes

### Verification Script Limitations
The verification script (`/github/applications/kraliki-lab/kraliki-swarm/control/verification.py`) runs `python3 -m ruff` and `python3 -m mypy`, which fail because:
- System Python (`/usr/bin/python3`) doesn't have project dependencies installed
- Ruff and mypy only available via `uv` in project virtual environment

Manual verification confirms:
```bash
cd /home/adminmatej/github/applications/cc-lite-2026
uv tool run ruff check backend/main.py
# Result: All checks passed!
```

### Security Note
Line 161 in `backend/main.py` binds to `0.0.0.0`:
```python
uvicorn.run(..., host="0.0.0.0", ...)
```

This violates security policy (should bind to `127.0.0.1`). This is a pre-existing issue, not related to VD-284. Should be addressed separately.

## Impact

**Revenue Impact:** Password reset is essential for production launch, enabling users to recover accounts and continue using the service.

**Security Impact:** P1 security feature now accessible, preventing lockout scenarios.
