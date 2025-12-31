"""
Ed25519 JWT Integration Examples
Demo file showing how to integrate the new authentication into Voice by Kraliki routes
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Dict, Any

# Import the new security module
from app.core.security import (
    jwt_manager,
    get_current_user,
    hash_password,
    verify_password
)

router = APIRouter(prefix="/api/auth", tags=["authentication"])


# Request/Response Models
class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 900  # 15 minutes in seconds


class RefreshRequest(BaseModel):
    refresh_token: str


# Example 1: Login Endpoint with Ed25519 JWT
@router.post("/login", response_model=TokenResponse)
async def login(credentials: LoginRequest):
    """
    Authenticate user and return Ed25519-signed JWT tokens

    This replaces any existing login logic with the new Ed25519 implementation
    """
    # TODO: Replace this with actual database lookup
    # from app.services.auth_service import authenticate_user
    # user = await authenticate_user(credentials.email, credentials.password)

    # Mock user lookup (replace with real DB query)
    if credentials.email == "admin@cc-lite.local":
        user_data = {
            "id": "user_123",
            "email": credentials.email,
            "role": "ADMIN"
        }
    else:
        raise HTTPException(401, "Invalid credentials")

    # Create Ed25519-signed tokens
    access_token = jwt_manager.create_access_token({
        "sub": user_data["id"],
        "email": user_data["email"],
        "role": user_data["role"]
    })

    refresh_token = jwt_manager.create_refresh_token({
        "sub": user_data["id"],
        "email": user_data["email"]
    })

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token
    )


# Example 2: Protected Route using get_current_user dependency
@router.get("/me")
async def get_current_user_info(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Protected route - requires valid Ed25519 JWT token

    Usage from frontend:
    fetch('/api/auth/me', {
        headers: {
            'Authorization': 'Bearer <access_token>'
        }
    })
    """
    return {
        "user_id": current_user["sub"],
        "email": current_user["email"],
        "role": current_user.get("role"),
        "token_type": current_user.get("type")
    }


# Example 3: Refresh Token Endpoint
@router.post("/refresh", response_model=TokenResponse)
async def refresh_access_token(request: RefreshRequest):
    """
    Exchange refresh token for new access token

    Security: Refresh tokens should be rotated on use (implement token blacklist)
    """
    try:
        # Verify refresh token
        payload = jwt_manager.verify_token(request.refresh_token)

        # Verify it's actually a refresh token
        if payload.get("type") != "refresh":
            raise HTTPException(401, "Invalid token type")

        # Create new access token
        access_token = jwt_manager.create_access_token({
            "sub": payload["sub"],
            "email": payload["email"],
            "role": payload.get("role")
        })

        # Optional: Rotate refresh token (best practice)
        new_refresh_token = jwt_manager.create_refresh_token({
            "sub": payload["sub"],
            "email": payload["email"]
        })

        return TokenResponse(
            access_token=access_token,
            refresh_token=new_refresh_token
        )

    except ValueError as e:
        raise HTTPException(401, str(e))


# Example 4: Role-based access control
def require_role(required_role: str):
    """
    Dependency factory for role-based access control

    Usage:
        @router.get("/admin-only", dependencies=[Depends(require_role("ADMIN"))])
    """
    async def role_checker(
        current_user: Dict[str, Any] = Depends(get_current_user)
    ):
        user_role = current_user.get("role")
        if user_role != required_role:
            raise HTTPException(
                403,
                f"Insufficient permissions. Required: {required_role}, Got: {user_role}"
            )
        return current_user

    return role_checker


# Example 5: Admin-only route
@router.get("/admin/stats")
async def admin_statistics(
    current_user: Dict[str, Any] = Depends(require_role("ADMIN"))
):
    """
    Admin-only endpoint using role-based access control
    """
    return {
        "message": "Admin access granted",
        "admin_email": current_user["email"],
        "stats": {
            "total_users": 42,
            "active_calls": 7
        }
    }


# Example 6: Logout (with token blacklist - TODO)
@router.post("/logout")
async def logout(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Logout endpoint

    TODO: Implement token blacklist/revocation
    - Store token JTI in Redis with TTL matching token expiration
    - Check blacklist in get_current_user dependency
    """
    # TODO: Add token to blacklist
    # await redis.setex(f"blacklist:{token_jti}", ttl, "1")

    return {
        "message": "Logged out successfully",
        "user_id": current_user["sub"]
    }


# Integration Notes:
"""
To integrate this into existing Voice by Kraliki routes:

1. Update app/routers/auth.py:
   - Replace existing login logic with the login() function above
   - Add refresh token endpoint
   - Add logout with token blacklist

2. Update protected routes (app/routers/calls.py, agents.py, etc):
   - Add `current_user: dict = Depends(get_current_user)` to route signatures
   - Use `current_user["sub"]` to get user ID
   - Use `current_user["role"]` for role checks

3. Frontend updates (SvelteKit):
   - Store tokens in localStorage or httpOnly cookies
   - Add Authorization header to all API requests
   - Implement token refresh on 401 errors
   - Clear tokens on logout

4. Testing:
   - Update existing auth tests to use Ed25519 tokens
   - Test token expiration handling
   - Test role-based access control
   - Load test with realistic token volumes

Example Frontend Integration (SvelteKit):

```typescript
// src/lib/api/client.ts
const API_BASE = 'http://localhost:8000';

async function apiFetch(endpoint: string, options: RequestInit = {}) {
    const token = localStorage.getItem('access_token');

    const response = await fetch(`${API_BASE}${endpoint}`, {
        ...options,
        headers: {
            'Content-Type': 'application/json',
            'Authorization': token ? `Bearer ${token}` : '',
            ...options.headers
        }
    });

    // Handle token expiration
    if (response.status === 401) {
        // Try to refresh token
        const refreshed = await refreshAccessToken();
        if (refreshed) {
            // Retry original request
            return apiFetch(endpoint, options);
        } else {
            // Redirect to login
            window.location.href = '/login';
        }
    }

    return response;
}

async function refreshAccessToken() {
    const refresh_token = localStorage.getItem('refresh_token');
    if (!refresh_token) return false;

    const response = await fetch(`${API_BASE}/api/auth/refresh`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh_token })
    });

    if (response.ok) {
        const { access_token, refresh_token: new_refresh } = await response.json();
        localStorage.setItem('access_token', access_token);
        localStorage.setItem('refresh_token', new_refresh);
        return true;
    }

    return false;
}
```
"""
