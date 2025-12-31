from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from app.core.database import get_db
from app.core.security import generate_id, create_access_token, get_current_user
from app.core.config import settings
from app.middleware.rate_limit import limiter
from app.models.user import User
from app.schemas.user import (
    GoogleAuthUrlRequest, GoogleAuthUrlResponse,
    GoogleLoginRequest, GoogleLinkRequest,
    UserWithToken, UserResponse
)
from datetime import datetime, timedelta
import secrets

router = APIRouter(prefix="/auth/google", tags=["google-oauth"])

# In-memory CSRF token storage (replace with Redis in production)
csrf_tokens = {}


def _verify_google_token(id_token_str: str) -> dict:
    """Verify Google ID token using configured client ID."""
    if not settings.GOOGLE_OAUTH_CLIENT_ID:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google OAuth is not configured"
        )

    try:
        return id_token.verify_oauth2_token(
            id_token_str,
            google_requests.Request(),
            settings.GOOGLE_OAUTH_CLIENT_ID
        )
    except ValueError as exc:  # Invalid token
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Google ID token"
        ) from exc

@router.post("/url", response_model=GoogleAuthUrlResponse)
@limiter.limit("10/minute")  # Rate limit OAuth URL generation - prevents CSRF token exhaustion
async def get_google_auth_url(request: Request, auth_request: GoogleAuthUrlRequest):
    """Generate Google OAuth URL with CSRF protection"""
    # Generate CSRF token
    csrf_token = secrets.token_urlsafe(32)
    csrf_tokens[auth_request.state] = csrf_token

    # Ensure OAuth client ID configured
    if not settings.GOOGLE_OAUTH_CLIENT_ID:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google OAuth is not configured"
        )
    google_client_id = settings.GOOGLE_OAUTH_CLIENT_ID
    redirect_uri = settings.GOOGLE_OAUTH_REDIRECT_URI

    # Include calendar scopes for calendar sync
    scopes = [
        "openid",
        "email",
        "profile",
        "https://www.googleapis.com/auth/calendar.readonly",
        "https://www.googleapis.com/auth/calendar.events"
    ]
    scope_string = "%20".join(scopes)

    oauth_url = (
        f"https://accounts.google.com/o/oauth2/v2/auth?"
        f"client_id={google_client_id}&"
        f"redirect_uri={redirect_uri}&"
        f"response_type=code&"
        f"scope={scope_string}&"
        f"access_type=offline&"
        f"prompt=consent&"
        f"state={auth_request.state}"
    )

    return GoogleAuthUrlResponse(
        url=oauth_url,
        csrfToken=csrf_token
    )

@router.post("/login", response_model=UserWithToken)
@limiter.limit("5/5minutes")  # Rate limit OAuth login - prevents brute force
async def google_login(
    request: Request,
    code: str,
    redirect_uri: str,
    db: Session = Depends(get_db)
):
    """Login or register user with Google OAuth code"""
    import httpx

    if not settings.GOOGLE_OAUTH_CLIENT_ID or not settings.GOOGLE_OAUTH_CLIENT_SECRET:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google OAuth is not configured"
        )

    # Exchange authorization code for tokens
    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "code": code,
                "client_id": settings.GOOGLE_OAUTH_CLIENT_ID,
                "client_secret": settings.GOOGLE_OAUTH_CLIENT_SECRET,
                "redirect_uri": redirect_uri,
                "grant_type": "authorization_code"
            }
        )

        if token_response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to exchange authorization code"
            )

        token_data = token_response.json()
        id_token_str = token_data.get("id_token")

    # Verify ID token
    token_payload = _verify_google_token(id_token_str)

    google_email = token_payload.get("email")
    google_name = token_payload.get("name") or token_payload.get("email")
    google_id = token_payload.get("sub")

    if not google_email or not google_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google token is missing required fields"
        )

    # Check if user exists
    user = db.query(User).filter(User.email == google_email).first()

    if not user:
        # Create new user
        user = User(
            id=generate_id(),
            email=google_email,
            username=google_name,
            firstName=google_name.split()[0] if google_name else None,
            lastName=google_name.split()[-1] if len(google_name.split()) > 1 else None,
            organizationId=generate_id(),  # Create default org
            passwordHash=None  # OAuth users don't have passwords
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    # Store Google Calendar tokens in user preferences
    prefs = user.preferences or {}
    prefs["calendar_sync"] = {
        "enabled": True,
        "access_token": token_data.get("access_token"),
        "refresh_token": token_data.get("refresh_token"),
        "expires_at": (datetime.utcnow() + timedelta(seconds=token_data.get("expires_in", 3600))).isoformat(),
        "sync_direction": "two-way",
        "last_sync": None
    }
    user.preferences = prefs
    db.commit()
    db.refresh(user)

    # Create access token
    access_token = create_access_token(data={"sub": user.id})

    return UserWithToken(
        user=UserResponse.model_validate(user),
        token=access_token
    )

@router.post("/link")
@limiter.limit("5/minute")  # Rate limit account linking - sensitive operation
async def link_google_account(
    request: Request,
    link_request: GoogleLinkRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Link Google account to existing user"""
    # Validate CSRF
    if csrf_tokens.get(link_request.state) != link_request.csrfToken:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid CSRF token"
        )

    csrf_tokens.pop(link_request.state, None)

    # Verify Google token and link account
    token_payload = _verify_google_token(link_request.idToken)
    google_email = token_payload.get("email")
    google_id = token_payload.get("sub")

    if not google_email or not google_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google token is missing required fields"
        )

    prefs = current_user.preferences or {}
    prefs["googleLinked"] = True
    prefs["googleEmail"] = google_email
    prefs["googleId"] = google_id
    current_user.preferences = prefs
    db.commit()

    return {
        "success": True,
        "message": "Google account linked successfully"
    }

@router.post("/unlink")
@limiter.limit("5/minute")  # Rate limit account unlinking - sensitive operation
async def unlink_google_account(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Unlink Google account from user"""
    prefs = current_user.preferences or {}
    prefs["googleLinked"] = False
    current_user.preferences = prefs
    db.commit()

    return {
        "success": True,
        "message": "Google account unlinked successfully"
    }
