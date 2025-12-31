# Password Reset Token Implementation - Migration Guide

## Overview
This document describes the implementation of dedicated password reset token fields to separate them from email verification tokens.

## Changes Made

### 1. Updated User Model (`backend/app/models/user.py`)
Added dedicated password reset token fields:
- `password_reset_token`: Column for storing password reset token
- `password_reset_token_expires`: Column for token expiration datetime

This separates password reset functionality from email verification, preventing conflicts.

### 2. Created Migration (`backend/migrations/versions/20251224_1735_add_password_reset_token_fields.py`)
New migration adds password reset token fields to the users table.

### 3. Updated Password Reset Routes (`backend/app/auth/database_routes.py`)
Modified two functions:
- `forgot_password()`: Now uses `password_reset_token` and `password_reset_token_expires`
- `reset_password()`: Validates against `password_reset_token` and clears it after successful reset

### 4. Created Comprehensive Tests (`backend/tests/test_password_reset.py`)
New test file covers:
- Password reset email sending with new token fields
- Password reset with valid token
- Password reset with expired token
- No conflicts between email verification and password reset tokens
- Reset clears failed login attempts and account locks

### 5. Updated Existing Tests (`backend/tests/test_email_verification.py`)
Modified `test_reset_password_with_valid_token` to use new password reset token fields.

## Applying the Migration

### Option 1: Using Alembic CLI
```bash
cd /home/adminmatej/github/applications/cc-lite-2026/backend
uv venv .venv
source .venv/bin/activate
uv pip install -r requirements.txt
alembic upgrade head
```

### Option 2: Using uv
```bash
cd /home/adminmatej/github/applications/cc-lite-2026/backend
uv venv .venv
uv pip install -r requirements.txt
uv run alembic upgrade head
```

### Option 3: Using Python Directly
```bash
cd /home/adminmatej/github/applications/cc-lite-2026/backend
python -m alembic upgrade head
```

## Verification

### Check Migration Status
```bash
alembic current
```
Should show: `20251224_1735`

### Run Tests
```bash
pytest tests/test_password_reset.py -v
pytest tests/test_email_verification.py::test_reset_password_with_valid_token -v
```

### Manual Verification
1. Create a user and verify email
2. Request password reset via `/api/v1/auth/forgot-password`
3. Check database: `password_reset_token` and `password_reset_token_expires` should be set
4. Verify email was sent with reset token
5. Reset password via `/api/v1/auth/reset-password`
6. Verify `password_reset_token` fields are cleared

## Benefits

1. **Separation of Concerns**: Email verification and password reset are now truly independent
2. **No Token Conflicts**: Users can verify email and reset password simultaneously
3. **Clearer Semantics**: Field names match their actual purpose
4. **Better Testing**: Easier to test each flow independently
5. **Security**: Clearer audit trail for password resets

## Database Schema Changes

### Before
```sql
users table:
  - email_verification_token
  - email_verification_token_expires
  (Used for BOTH email verification AND password reset)
```

### After
```sql
users table:
  - email_verification_token
  - email_verification_token_expires
  - password_reset_token
  - password_reset_token_expires
  (Separate fields for each purpose)
```

## Rollback

If needed, rollback the migration:
```bash
alembic downgrade -1
```

This will remove the password reset token fields (but won't break existing functionality if you revert the code changes).
