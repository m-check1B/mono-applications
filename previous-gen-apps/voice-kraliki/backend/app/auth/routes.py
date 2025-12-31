"""Authentication routes for FastAPI

Rate limited to prevent brute force attacks.
"""

import logging
import os
import uuid
from datetime import datetime, timedelta

import psycopg2
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from psycopg2.extras import RealDictCursor
from pydantic import BaseModel, EmailStr

from app.middleware.rate_limit import LOGIN_RATE_LIMIT, limiter

from .ed25519_auth import get_auth_manager
from .token_revocation import get_revocation_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/auth", tags=["authentication"])
security = HTTPBearer(auto_error=False)

ACCESS_TOKEN_EXPIRES_MINUTES = int(os.getenv("JWT_EXPIRATION_MINUTES", "1440"))
ACCESS_TOKEN_EXPIRES_SECONDS = ACCESS_TOKEN_EXPIRES_MINUTES * 60
REFRESH_TOKEN_EXPIRES_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRATION_DAYS", "30"))
REFRESH_TOKEN_EXPIRES_SECONDS = REFRESH_TOKEN_EXPIRES_DAYS * 24 * 60 * 60

AUTH_COOKIE_NAME = os.getenv("AUTH_COOKIE_NAME", "auth_token")
REFRESH_COOKIE_NAME = os.getenv("REFRESH_COOKIE_NAME", "refresh_token")
COOKIE_DOMAIN = os.getenv("AUTH_COOKIE_DOMAIN") or None
COOKIE_PATH = os.getenv("AUTH_COOKIE_PATH", "/")
COOKIE_SECURE = os.getenv("AUTH_COOKIE_SECURE", "false").lower() == "true"
_raw_samesite = os.getenv("AUTH_COOKIE_SAMESITE", "lax").lower()
if _raw_samesite not in {"lax", "strict", "none"}:
    _raw_samesite = "lax"
COOKIE_SAMESITE = "None" if _raw_samesite == "none" else _raw_samesite.capitalize()
ACCESS_COOKIE_MAX_AGE = int(os.getenv("AUTH_COOKIE_MAX_AGE", str(ACCESS_TOKEN_EXPIRES_SECONDS)))
REFRESH_COOKIE_MAX_AGE = int(os.getenv("REFRESH_COOKIE_MAX_AGE", str(REFRESH_TOKEN_EXPIRES_SECONDS)))


class UserRegister(BaseModel):
    """User registration request"""

    email: EmailStr
    password: str
    full_name: str
    organization: str | None = None


class UserLogin(BaseModel):
    """User login request"""

    email: EmailStr
    password: str


class RefreshTokenRequest(BaseModel):
    """Refresh token request payload"""

    refresh_token: str | None = None


class TokenResponse(BaseModel):
    """Token response"""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = ACCESS_TOKEN_EXPIRES_SECONDS


class UserResponse(BaseModel):
    """User response"""

    id: str
    email: str
    full_name: str
    organization: str | None
    role: str
    phone_number: str | None = None
    avatar_url: str | None = None
    timezone: str = "UTC"
    language: str = "en"
    is_premium: bool = False


_DB_AVAILABLE: bool | None = None


def get_db_connection():
    """Get database connection"""
    global _DB_AVAILABLE

    db_url = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/operator_demo")

    # Only attempt PostgreSQL connection if URL is PostgreSQL
    if not db_url.startswith(("postgresql://", "postgres://")):
        logger.info("Auth routes: Non-PostgreSQL DATABASE_URL detected, skipping table creation")
        _DB_AVAILABLE = False
        raise psycopg2.OperationalError("Non-PostgreSQL database URL")

    conn = psycopg2.connect(db_url, cursor_factory=RealDictCursor)
    _DB_AVAILABLE = True
    return conn


def create_tables():
    """Create users table if not exists"""

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id UUID PRIMARY KEY,
                email VARCHAR(255) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                full_name VARCHAR(255) NOT NULL,
                organization VARCHAR(255),
                role VARCHAR(50) DEFAULT 'user',
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        cursor.execute(
            """
            ALTER TABLE users
                ADD COLUMN IF NOT EXISTS organization VARCHAR(255),
                ADD COLUMN IF NOT EXISTS role VARCHAR(50) DEFAULT 'user',
                ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE,
                ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            """
        )
        cursor.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS users_email_idx ON users (email)
            """
        )
        conn.commit()
    except Exception as exc:  # pragma: no cover - logged and re-raised upstream
        logger.error("Error creating tables: %s", exc)
        conn.rollback()
    finally:
        cursor.close()
        conn.close()


try:
    create_tables()
except Exception as exc:  # pragma: no cover
    logger.warning("Warning: Could not create tables: %s", exc)


def _set_auth_cookies(response: JSONResponse, access_token: str, refresh_token: str) -> None:
    """Attach HTTP-only auth cookies to response."""

    response.set_cookie(
        key=AUTH_COOKIE_NAME,
        value=access_token,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE,
        domain=COOKIE_DOMAIN,
        path=COOKIE_PATH,
        max_age=ACCESS_COOKIE_MAX_AGE,
    )
    response.set_cookie(
        key=REFRESH_COOKIE_NAME,
        value=refresh_token,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE,
        domain=COOKIE_DOMAIN,
        path=COOKIE_PATH,
        max_age=REFRESH_COOKIE_MAX_AGE,
    )


def _clear_auth_cookies(response: JSONResponse) -> None:
    """Remove auth cookies from response."""

    response.delete_cookie(AUTH_COOKIE_NAME, domain=COOKIE_DOMAIN, path=COOKIE_PATH)
    response.delete_cookie(REFRESH_COOKIE_NAME, domain=COOKIE_DOMAIN, path=COOKIE_PATH)


def _build_token_response(access_token: str, refresh_token: str) -> JSONResponse:
    """Create JSON response with tokens and set cookies."""

    payload = TokenResponse(access_token=access_token, refresh_token=refresh_token)
    response = JSONResponse(content=payload.model_dump())
    _set_auth_cookies(response, access_token, refresh_token)
    return response


@router.post("/register", response_model=TokenResponse)
@limiter.limit(LOGIN_RATE_LIMIT)
async def register(request: Request, user: UserRegister):
    """Register a new user. Rate limited to prevent abuse."""

    auth = get_auth_manager()
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT id FROM users WHERE email = %s", (user.email,))
        if cursor.fetchone():
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User with this email already exists")

        try:
            password_hash = auth.hash_password(user.password)
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to hash password: {str(e)}")

        user_id = uuid.uuid4()

        cursor.execute(
            """
            INSERT INTO users (id, email, password_hash, full_name, organization, role, is_active)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id, email, full_name, organization, role
            """,
            (
                str(user_id),
                user.email,
                password_hash,
                user.full_name,
                user.organization,
                "user",
                True,
            ),
        )
        user_record = cursor.fetchone()
        conn.commit()

        access_token = auth.create_access_token(
            user_id=str(user_id),
            email=user.email,
            role=user_record["role"],
            org_id=user_record.get("organization"),
            expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRES_MINUTES),
        )
        refresh_token = auth.create_refresh_token(str(user_id))

        return _build_token_response(access_token, refresh_token)
    except HTTPException:
        raise
    except Exception as exc:
        conn.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to register user: {exc}")
    finally:
        cursor.close()
        conn.close()


@router.post("/login", response_model=TokenResponse)
@limiter.limit(LOGIN_RATE_LIMIT)
async def login(request: Request, user: UserLogin):
    """Login with email and password. Rate limited to prevent brute force."""

    auth = get_auth_manager()
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            SELECT id, email, password_hash, full_name, organization, role, is_active
            FROM users
            WHERE email = %s
            """,
            (user.email,),
        )
        user_data = cursor.fetchone()

        if (
            not user_data
            or not user_data.get("is_active", True)
            or not auth.verify_password(user.password, user_data["password_hash"])
        ):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

        access_token = auth.create_access_token(
            user_id=str(user_data["id"]),
            email=user_data["email"],
            role=user_data.get("role", "user"),
            org_id=user_data.get("organization"),
            expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRES_MINUTES),
        )
        refresh_token = auth.create_refresh_token(str(user_data["id"]))

        return _build_token_response(access_token, refresh_token)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Login failed: {exc}")
    finally:
        cursor.close()
        conn.close()


@router.get("/me", response_model=UserResponse)
async def get_current_user(request: Request, credentials: HTTPAuthorizationCredentials | None = Depends(security)):
    """Get current user from token

    Also supports Kraliki internal bypass via X-Kraliki-Session header.
    When requests come from Kraliki dashboard, they are trusted internal requests.
    """

    # Check for Kraliki internal bypass
    if request and request.headers:
        kraliki_session = request.headers.get("X-Kraliki-Session")
        if kraliki_session == "kraliki-internal":
            user_email = request.headers.get("X-Kraliki-User-Email", "agent@kraliki.local")
            user_name = request.headers.get("X-Kraliki-User-Name", "Kraliki User")

            conn = get_db_connection()
            cursor = conn.cursor()
            try:
                # Check if user exists
                cursor.execute("SELECT id, email, full_name, organization, role FROM users WHERE email = %s", (user_email,))
                user_data = cursor.fetchone()

                if not user_data:
                    # Create user for Kraliki
                    auth = get_auth_manager()
                    import secrets
                    user_id = str(uuid.uuid4())
                    password_hash = auth.hash_password(secrets.token_urlsafe(32))
                    cursor.execute(
                        """
                        INSERT INTO users (id, email, full_name, password_hash, role, is_active, is_verified, created_at, updated_at)
                        VALUES (%s, %s, %s, %s, %s, TRUE, TRUE, NOW(), NOW())
                        RETURNING id, email, full_name, organization, role
                        """,
                        (user_id, user_email, user_name, password_hash, "ADMIN"),
                    )
                    user_data = cursor.fetchone()
                    conn.commit()
                    logger.info(f"Created Kraliki-linked user: {user_email}")

                return UserResponse(
                    id=str(user_data["id"]),
                    email=user_data["email"],
                    full_name=user_data["full_name"],
                    organization=user_data.get("organization"),
                    role=user_data["role"],
                )
            except Exception as exc:
                conn.rollback()
                logger.error(f"Kraliki user creation failed: {exc}")
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Kraliki auth failed: {exc}")
            finally:
                cursor.close()
                conn.close()

    auth = get_auth_manager()

    token = None
    if credentials:
        token = credentials.credentials
    if not token:
        token = request.cookies.get(AUTH_COOKIE_NAME)

    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

    payload = auth.verify_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            SELECT id, email, full_name, organization, role
            FROM users
            WHERE id = %s
            """,
            (payload["sub"],),
        )
        user_data = cursor.fetchone()

        if not user_data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        return UserResponse(
            id=str(user_data["id"]),
            email=user_data["email"],
            full_name=user_data["full_name"],
            organization=user_data.get("organization"),
            role=user_data["role"],
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to get user: {exc}")
    finally:
        cursor.close()
        conn.close()


@router.post("/refresh", response_model=TokenResponse)
async def refresh_access_token(request: Request, payload: RefreshTokenRequest | None = None):
    """Refresh access token using refresh token"""

    auth = get_auth_manager()

    token = payload.refresh_token if payload and payload.refresh_token else request.cookies.get(REFRESH_COOKIE_NAME)
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing refresh token")

    refresh_payload = auth.verify_token(token)
    if not refresh_payload or refresh_payload.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            SELECT id, email, role, organization
            FROM users
            WHERE id = %s
            """,
            (refresh_payload["sub"],),
        )
        user_data = cursor.fetchone()

        if not user_data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        access_token = auth.create_access_token(
            user_id=str(user_data["id"]),
            email=user_data["email"],
            role=user_data["role"],
            org_id=user_data.get("organization"),
            expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRES_MINUTES),
        )
        new_refresh_token = auth.create_refresh_token(str(user_data["id"]))

        return _build_token_response(access_token, new_refresh_token)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to refresh token: {exc}")
    finally:
        cursor.close()
        conn.close()


@router.post("/logout")
async def logout() -> JSONResponse:
    """Clear authentication cookies"""

    response = JSONResponse(content={"detail": "Logged out"})
    _clear_auth_cookies(response)
    return response


def get_current_user_dependency(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
):
    """Dependency to get current user from token"""

    auth = get_auth_manager()

    token = None
    if credentials:
        token = credentials.credentials
    if not token:
        token = request.cookies.get(AUTH_COOKIE_NAME)

    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

    payload = auth.verify_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

    return payload


@router.post("/revoke", status_code=200)
async def revoke_token(request: Request, credentials: HTTPAuthorizationCredentials | None = Depends(security)):
    """
    Revoke current access token

    Adds the current token to the revocation list, preventing it from being used again.
    The token will remain revoked until its natural expiration.
    """
    auth = get_auth_manager()
    revocation_service = get_revocation_service()

    # Get token from header or cookie
    token = None
    if credentials:
        token = credentials.credentials
    if not token:
        token = request.cookies.get(AUTH_COOKIE_NAME)

    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No token provided")

    # Verify and decode token
    payload = auth.verify_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

    # Extract token information
    jti = payload.get("jti")
    exp = payload.get("exp")

    if not jti or not exp:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token missing required claims (jti or exp)")

    # Revoke the token
    expires_at = datetime.fromtimestamp(exp)
    success = revocation_service.revoke_token(jti, expires_at)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to revoke token (Redis may be unavailable)"
        )

    return {"message": "Token revoked successfully", "jti": jti}


@router.post("/revoke-all", status_code=200)
async def revoke_all_tokens(request: Request, credentials: HTTPAuthorizationCredentials | None = Depends(security)):
    """
    Revoke all tokens for current user

    Invalidates all existing tokens for the authenticated user. This is useful for:
    - Security incidents (suspected account compromise)
    - Password changes
    - Logout from all devices
    """
    auth = get_auth_manager()
    revocation_service = get_revocation_service()

    # Get token from header or cookie
    token = None
    if credentials:
        token = credentials.credentials
    if not token:
        token = request.cookies.get(AUTH_COOKIE_NAME)

    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No token provided")

    # Verify and decode token
    payload = auth.verify_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

    # Get user ID
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token missing user ID (sub)")

    # Revoke all user tokens
    success = revocation_service.revoke_all_user_tokens(user_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to revoke user tokens (Redis may be unavailable)",
        )

    return {"message": "All tokens revoked successfully", "user_id": user_id}


@router.get("/revocation-status", status_code=200)
async def check_revocation_status():
    """
    Check token revocation service health

    Returns the status of the Redis-backed token revocation service.
    Useful for monitoring and debugging.
    """
    revocation_service = get_revocation_service()
    is_healthy = revocation_service.health_check()

    return {
        "service": "token_revocation",
        "status": "healthy" if is_healthy else "unhealthy",
        "backend": "redis",
        "message": "Token revocation service is operational" if is_healthy else "Redis connection unavailable",
    }
