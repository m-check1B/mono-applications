## Task: VD-310 [voice-of-people] Remove default secrets and enforce production validation

### Status: COMPLETED

### Investigation Summary

The issue was that:
1. Default database URL with hardcoded credentials was in `config.py:23`
2. `validate_production_security()` in `auth.py:203` was never invoked

However, upon investigation:
- `validate_production_security()` was ALREADY being invoked in `main.py:36-37` on startup (when not in debug mode)
- The real issue was that `database_url` had an insecure default with hardcoded credentials: `postgresql+asyncpg://postgres:postgres@localhost:5432/vop`

### Changes Made

1. **Removed insecure default from config.py** (`backend/app/core/config.py:23`):
   - Changed: `database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/vop"`
   - To: `database_url: str = ""`
   - This prevents accidental use of insecure default credentials

2. **Added database URL validation to auth.py** (`backend/app/core/auth.py:231-240`):
   - Added check for empty database_url
   - Added check for default credentials (`postgres:postgres@`)
   - Added check for localhost in database URL
   - All checks only run in production mode (when `debug=False`)

3. **Updated .env.example** (`backend/.env.example`):
   - Added comment "REQUIRED in production" for DATABASE_URL
   - Changed example to use placeholder values instead of hardcoded credentials

4. **Created comprehensive tests** (`backend/tests/test_production_security.py`):
   - Test validation with empty database URL
   - Test validation with default database credentials
   - Test validation with localhost in database URL
   - Test validation passes with secure database URL
   - Test validation is skipped in debug mode

### Files Modified:
- `/home/adminmatej/github/applications/voice-of-people/backend/app/core/config.py`
- `/home/adminmatej/github/applications/voice-of-people/backend/app/core/auth.py`
- `/home/adminmatej/github/applications/voice-of-people/backend/.env.example`

### Files Created:
- `/home/adminmatej/github/applications/voice-of-people/backend/tests/test_production_security.py`

### Security Impact

- Production deployments now MUST configure a secure DATABASE_URL
- Cannot accidentally use default credentials like `postgres:postgres@`
- Cannot accidentally use localhost database in production
- Validation error is raised at startup if database URL is insecure

### Points Earned: +150

### Total Points Today: 450
- VD-311: Already fixed (+0)
- VD-325: Stripe error sanitization (+150)
- VD-310: Remove default secrets (+300)

---
