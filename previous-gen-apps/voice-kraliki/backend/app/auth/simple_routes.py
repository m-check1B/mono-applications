"""Simple authentication routes for frontend compatibility"""

import os
import sys

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

# Add the parent directory to the path to import from routes
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ..database import get_db
from ..middleware.rate_limit import LOGIN_RATE_LIMIT, limiter
from ..models.user import User
from .routes import (
    UserLogin,
    UserRegister,
    get_auth_manager,
)

router = APIRouter(prefix="/auth", tags=["authentication"])


class Credentials(BaseModel):
    """Login credentials"""

    email: str
    password: str


class RegisterPayload(Credentials):
    """Registration payload"""

    name: str | None = None


class AuthResponse(BaseModel):
    """Authentication response"""

    access_token: str
    refresh_token: str
    expires_at: int | None = None
    user: dict | None = None


def _extract_token_data(response: JSONResponse) -> dict:
    """Extract token data from JSONResponse"""
    if hasattr(response, "body"):
        import json

        body = response.body
        if isinstance(body, bytes):
            return json.loads(body.decode())
        elif isinstance(body, memoryview):
            return json.loads(body.tobytes().decode())
        else:
            return {"access_token": "", "refresh_token": "", "expires_in": 0}
    else:
        return {"access_token": "", "refresh_token": "", "expires_in": 0}


def _convert_to_frontend_response(token_data: dict, user_data: dict) -> AuthResponse:
    """Convert backend token response to frontend format"""
    # Ensure 'name' is present for backward compatibility (renamed from full_name)
    if "full_name" in user_data and "name" not in user_data:
        user_data["name"] = user_data["full_name"]

    return AuthResponse(
        access_token=token_data.get("access_token", ""),
        refresh_token=token_data.get("refresh_token", ""),
        expires_at=token_data.get("expires_in"),
        user=user_data,
    )


def _build_user_info(db: Session, token_payload: dict | None, fallback_email: str, fallback_name: str) -> dict:
    """Fetch user info from database with token-aware fallbacks."""
    user_id = token_payload.get("sub") if token_payload else None
    email = token_payload.get("email") if token_payload else None
    role = token_payload.get("role") if token_payload else None

    user = None
    if user_id:
        # User.id is now a UUID string, no conversion needed
        stmt = select(User).where(User.id == str(user_id))
        user = db.execute(stmt).scalar_one_or_none()

    if user is None and email:
        stmt = select(User).where(User.email == email)
        user = db.execute(stmt).scalar_one_or_none()

    if user:
        role_value = user.role.value if hasattr(user.role, "value") else str(user.role)
        return {
            "id": str(user.id),
            "email": user.email,
            "full_name": user.full_name,
            "name": user.full_name,
            "role": role_value,
            "organization": user.organization,
            "phone_number": user.phone_number,
            "avatar_url": user.avatar_url,
            "timezone": user.timezone,
            "language": user.language,
            "permissions": user.permissions,
            "is_premium": getattr(user, "is_premium", False),
            "is_verified": getattr(user, "is_verified", False),
            "is_active": getattr(user, "is_active", True),
            "stripe_customer_id": getattr(user, "stripe_customer_id", None),
        }

    return {
        "id": str(user_id or ""),
        "email": email or fallback_email,
        "full_name": fallback_name,
        "name": fallback_name,
        "role": role or "agent",
    }


@router.post("/login", response_model=AuthResponse)
@limiter.limit(LOGIN_RATE_LIMIT)
async def login(credentials: Credentials, request: Request, db: Session = Depends(get_db)):
    """Login endpoint - redirects to real authentication. Rate limited to prevent brute force."""
    # Import here to avoid circular imports
    from .routes import login as real_login

    # Convert to backend format
    user_login = UserLogin(email=credentials.email, password=credentials.password)

    # Call real authentication and get the JSONResponse
    response = await real_login(request, user_login)

    # Extract token data from the response
    token_data = _extract_token_data(response)

    # Get user info from the database
    auth = get_auth_manager()
    token = token_data.get("access_token")
    user_info = {"id": "", "email": credentials.email, "full_name": "User", "role": "agent"}

    if token:
        try:
            payload = auth.verify_token(token)
            if payload:
                user_info = _build_user_info(db, payload, credentials.email, "User")
        except Exception as e:
            import logging

            logging.getLogger(__name__).error(f"Error fetching user data: {e}")
            pass  # Use fallback user info

    return _convert_to_frontend_response(token_data, user_info)


@router.post("/register", response_model=AuthResponse)
@limiter.limit(LOGIN_RATE_LIMIT)
async def register(payload: RegisterPayload, request: Request, db: Session = Depends(get_db)):
    """Registration endpoint - redirects to real authentication. Rate limited to prevent abuse."""
    # Import here to avoid circular imports
    from .routes import register as real_register

    # Convert to backend format
    user_register = UserRegister(
        email=payload.email,
        password=payload.password,
        full_name=payload.name or "New User",
        organization=None,
    )

    # Call real authentication
    response = await real_register(request, user_register)

    # Extract token data from the response
    token_data = _extract_token_data(response)

    # Get user info from the database
    user_info = {
        "id": "new_user_id",
        "email": payload.email,
        "full_name": payload.name or "New User",
        "role": "agent",
    }

    token = token_data.get("access_token")
    if token:
        try:
            auth = get_auth_manager()
            token_payload = auth.verify_token(token)
            if token_payload:
                user_info = _build_user_info(db, token_payload, payload.email, payload.name or "New User")
        except Exception as e:
            import logging

            logging.getLogger(__name__).error(f"Error fetching user data: {e}")
            pass  # Use fallback user info

    return _convert_to_frontend_response(token_data, user_info)


@router.post("/logout")
async def logout():
    """Logout endpoint - redirects to real authentication"""
    # Import here to avoid circular imports
    from .routes import logout as real_logout

    return await real_logout()
