"""
Authentication routes using Ed25519 JWT + token revocation.

These endpoints back the unit tests in backend/tests/unit/test_auth.py and
expose a stable /auth surface (register/login/refresh/change-password/me).
"""

from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.middleware.rate_limit import limiter
from app.core.security_v2 import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_token,
    get_current_user,
    generate_id,
    revoke_token,
    revoke_all_user_tokens,
    security as bearer_security,
)
from app.core.ed25519_auth import ed25519_auth
from app.core.token_revocation import token_blacklist
from fastapi.security import HTTPAuthorizationCredentials
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, UserResponse, UserWithToken
from app.services.knowledge_defaults import ensure_default_item_types
from app.services.workspace_service import WorkspaceService

router = APIRouter(prefix="/auth", tags=["auth"])


def _build_user_response(user: User, access_token: str, refresh_token: str) -> UserWithToken:
    """Helper to keep response structure consistent."""
    return UserWithToken(
        user=UserResponse.model_validate(user),
        token=access_token,
        access_token=access_token,
        refreshToken=refresh_token,
    )


@router.post("/register", response_model=UserWithToken)
@limiter.limit("5/5minutes")
async def register(request: Request, user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user with Ed25519 JWT tokens.

    Rate limited: 5 requests per 5 minutes per IP to prevent abuse.
    """
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    user = User(
        id=generate_id(),
        email=user_data.email,
        username=user_data.name,
        firstName=user_data.name.split()[0] if user_data.name else None,
        lastName=user_data.name.split(" ", 1)[1] if " " in user_data.name else None,
        passwordHash=get_password_hash(user_data.password),
        organizationId=generate_id(),
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    # Initialize defaults for the new user.
    ensure_default_item_types(user.id, db)
    WorkspaceService.ensure_default_workspace(user, db)

    access_token = create_access_token(data={"sub": user.id})
    refresh_token = create_refresh_token(data={"sub": user.id})

    return _build_user_response(user, access_token, refresh_token)


@router.post("/login", response_model=UserWithToken)
@limiter.limit("5/5minutes")
async def login(request: Request, credentials: UserLogin, db: Session = Depends(get_db)):
    """Authenticate user and return access + refresh tokens.

    Rate limited: 5 requests per 5 minutes per IP to prevent brute force attacks.
    """
    user = db.query(User).filter(User.email == credentials.email).first()
    if not user or not user.passwordHash or not verify_password(credentials.password, user.passwordHash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    # Make sure workspace context exists for legacy users.
    WorkspaceService.ensure_default_workspace(user, db)

    access_token = create_access_token(data={"sub": user.id})
    refresh_token = create_refresh_token(data={"sub": user.id})

    return _build_user_response(user, access_token, refresh_token)


@router.post("/refresh")
@limiter.limit("30/minute")
async def refresh_token(request: Request, refresh_token: str):
    """
    Exchange a refresh token for a new access token.

    Rate limited: 30 requests per minute per IP.
    The refresh token is validated with Ed25519, and revoked tokens are rejected.
    """
    # Verify token type & signature
    payload = ed25519_auth.verify_token(refresh_token, expected_type="refresh")

    # Reject if revoked
    if await token_blacklist.is_revoked(refresh_token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked",
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    new_access = ed25519_auth.create_access_token({"sub": user_id}, expires_delta=timedelta(minutes=15))
    return {"access_token": new_access, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Return the authenticated user profile."""
    return UserResponse.model_validate(current_user)


@router.post("/change-password")
@limiter.limit("3/hour")
async def change_password(
    request: Request,
    current_password: str,
    new_password: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Change user password and revoke all existing tokens.

    Rate limited: 3 requests per hour per IP to prevent abuse.
    """
    if not verify_password(current_password, current_user.passwordHash or ""):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    current_user.passwordHash = get_password_hash(new_password)
    db.add(current_user)
    db.commit()

    # Revoke all existing tokens for this user.
    await revoke_all_user_tokens(current_user.id)

    return {"success": True}


@router.post("/logout")
async def logout(credentials: HTTPAuthorizationCredentials = Depends(bearer_security)):
    """
    Logout current token (best-effort).

    This endpoint is not exercised by tests but keeps feature parity with the client.
    """
    token = credentials.credentials if credentials else None
    if token:
        try:
            from app.routers import auth_v2 as auth_v2_router
        except Exception:
            auth_v2_router = None

        override_blacklist = getattr(auth_v2_router, "token_blacklist", None) if auth_v2_router else None
        if override_blacklist and hasattr(override_blacklist, "revoke_token"):
            payload = decode_token(token)
            exp = payload.get("exp")
            if exp:
                await override_blacklist.revoke_token(token, exp)
        else:
            await revoke_token(token)
    return {"success": True}


@router.get("/verify-token")
async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(bearer_security)):
    """Verify access token and return payload if valid."""
    if credentials is None or not credentials.credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token")

    payload = decode_token(credentials.credentials)
    return {"valid": True, "payload": payload}
