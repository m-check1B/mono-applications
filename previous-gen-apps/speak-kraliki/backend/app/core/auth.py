"""
Speak by Kraliki - Authentication
Stack 2026 Standard: Ed25519 JWT with 15min access, 7day refresh
Supports both HS256 (dev) and Ed25519 (production)

Uses auth-core for Ed25519 operations when available.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID
import secrets
import logging

import jwt
import bcrypt
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db

# Try to use auth-core for Ed25519 operations
try:
    from auth_core import (
        Ed25519Auth,
        TokenConfig,
        TokenType,
        TokenExpiredError,
        TokenInvalidError,
        TokenTypeMismatchError,
    )

    AUTH_CORE_AVAILABLE = True
except ImportError:
    AUTH_CORE_AVAILABLE = False

logger = logging.getLogger(__name__)
security = HTTPBearer(auto_error=False)  # Allow Kraliki bypass without token


def hash_password(password: str) -> str:
    """Hash password with bcrypt."""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash."""
    return bcrypt.checkpw(password.encode(), hashed.encode())


def _get_signing_key():
    """Get appropriate signing key based on config."""
    if settings.use_ed25519 and settings.ed25519_private_key:
        from cryptography.hazmat.primitives.serialization import load_pem_private_key

        return load_pem_private_key(
            settings.ed25519_private_key.encode(), password=None
        )
    if settings.jwt_secret_key:
        return settings.jwt_secret_key
    raise ValueError(
        "No signing key configured: set JWT_SECRET_KEY or ED25519_PRIVATE_KEY"
    )


def _get_verify_key():
    """Get appropriate verification key based on config."""
    if settings.use_ed25519 and settings.ed25519_public_key:
        from cryptography.hazmat.primitives.serialization import load_pem_public_key

        return load_pem_public_key(settings.ed25519_public_key.encode())
    if settings.jwt_secret_key:
        return settings.jwt_secret_key
    raise ValueError(
        "No verification key configured: set JWT_SECRET_KEY or ED25519_PUBLIC_KEY"
    )


def _get_algorithm() -> str:
    """Get JWT algorithm based on config."""
    if settings.use_ed25519 and settings.ed25519_private_key:
        return "EdDSA"
    return settings.jwt_algorithm


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    )
    to_encode.update({"exp": expire, "iat": datetime.utcnow(), "type": "access"})

    algorithm = _get_algorithm()
    key = _get_signing_key()

    return jwt.encode(to_encode, key, algorithm=algorithm)


def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT refresh token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta or timedelta(days=settings.refresh_token_expire_days)
    )
    to_encode.update({"exp": expire, "iat": datetime.utcnow(), "type": "refresh"})

    algorithm = _get_algorithm()
    key = _get_signing_key()

    return jwt.encode(to_encode, key, algorithm=algorithm)


def verify_token(token: str, token_type: str = "access") -> dict:
    """Verify and decode JWT token."""
    try:
        algorithm = _get_algorithm()
        key = _get_verify_key()

        payload = jwt.decode(token, key, algorithms=[algorithm])

        if payload.get("type") != token_type:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type"
            )

        return payload

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired"
        )
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid token: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )


def generate_magic_link_token() -> tuple[str, str]:
    """Generate secure magic link token for employee access.

    Returns:
        tuple[str, str]: (plaintext_token, hashed_token)
        - plaintext_token: Send this to the user via email
        - hashed_token: Store this in the database
    """
    plaintext_token = secrets.token_urlsafe(32)
    hashed_token = hash_magic_link_token(plaintext_token)
    return plaintext_token, hashed_token


def hash_magic_link_token(token: str) -> str:
    """Hash a magic link token for secure storage.

    Uses SHA-256 for fast, constant-time comparison.
    Magic links are single-use and time-limited, so bcrypt is overkill.
    """
    import hashlib

    return hashlib.sha256(token.encode()).hexdigest()


def verify_magic_link_token(plaintext_token: str, stored_hash: str) -> bool:
    """Verify a magic link token against its stored hash.

    Uses constant-time comparison to prevent timing attacks.
    """
    import hashlib
    import hmac

    token_hash = hashlib.sha256(plaintext_token.encode()).hexdigest()
    return hmac.compare_digest(token_hash, stored_hash)


async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Get current authenticated user from token.
    Returns payload with: sub (user_id), company_id, role, email

    Also supports Kraliki internal bypass via X-Kraliki-Session header.
    When requests come from Kraliki dashboard, they are trusted internal requests.
    Creates real DB user on first access (Strategy A).
    """
    # Check for Kraliki internal bypass
    if request and request.headers:
        kraliki_session = request.headers.get("X-Kraliki-Session")
        if kraliki_session == "kraliki-internal":
            # Get user info from Kraliki headers
            user_email = request.headers.get("X-Kraliki-User-Email", "agent@kraliki.local")
            user_name = request.headers.get("X-Kraliki-User-Name", "Kraliki User")

            # Parse name into first/last
            name_parts = user_name.split(" ", 1)
            first_name = name_parts[0] if name_parts else "Kraliki"
            last_name = name_parts[1] if len(name_parts) > 1 else "User"

            return await _handle_kraliki_bypass(db, user_email, first_name, last_name, user_name)

    # Standard JWT auth flow - requires credentials
    if credentials is None or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    payload = verify_token(credentials.credentials)
    return payload


async def _handle_kraliki_bypass(db: AsyncSession, user_email: str, first_name: str, last_name: str, user_name: str) -> dict:
    """Helper to handle Kraliki bypass logic with a given database session."""
    from app.models.user import User
    from app.models.company import Company
    from sqlalchemy import select
    import secrets

    # Check if user exists by email
    result = await db.execute(
        select(User).where(User.email == user_email)
    )
    kraliki_user = result.scalar_one_or_none()

    if not kraliki_user:
        # Need to create user - first ensure company exists
        company_slug = "kraliki-internal"
        result = await db.execute(
            select(Company).where(Company.slug == company_slug)
        )
        company = result.scalar_one_or_none()

        if not company:
            company = Company(
                name="Kraliki Internal",
                slug=company_slug,
                plan="premium",
                is_active=True
            )
            db.add(company)
            await db.flush()
            logger.info(f"Created Kraliki company: {company.id}")

        # Create user with random password (won't be used - SSO only)
        kraliki_user = User(
            company_id=company.id,
            email=user_email,
            password_hash=hash_password(secrets.token_urlsafe(32)),
            first_name=first_name,
            last_name=last_name,
            role="owner",
            is_active=True,
            is_verified=True
        )
        db.add(kraliki_user)
        await db.commit()
        await db.refresh(kraliki_user)
        logger.info(f"Created Kraliki-linked user: {user_email}")
    else:
        # User exists - just update last login
        kraliki_user.last_login = datetime.utcnow()
        await db.commit()

    # Get company name for response
    result = await db.execute(
        select(Company).where(Company.id == kraliki_user.company_id)
    )
    company = result.scalar_one_or_none()
    company_name = company.name if company else "Kraliki Internal"

    logger.info(f"Kraliki bypass for user: {user_email}")
    return {
        "sub": str(kraliki_user.id),
        "company_id": str(kraliki_user.company_id),
        "email": kraliki_user.email,
        "role": kraliki_user.role,
        "first_name": kraliki_user.first_name,
        "last_name": kraliki_user.last_name,
        "company_name": company_name,
        "department_id": str(kraliki_user.department_id) if kraliki_user.department_id else None,
    }


    # Standard JWT auth flow - requires credentials
    if credentials is None or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    payload = verify_token(credentials.credentials)
    return payload


async def get_current_user_optional(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> Optional[dict]:
    """Get current user if authenticated, None otherwise.

    Also supports Kraliki internal bypass via X-Kraliki-Session header.
    """
    # Check for Kraliki internal bypass
    if request and request.headers:
        kraliki_session = request.headers.get("X-Kraliki-Session")
        if kraliki_session == "kraliki-internal":
            user_email = request.headers.get("X-Kraliki-User-Email", "agent@kraliki.local")
            user_name = request.headers.get("X-Kraliki-User-Name", "Kraliki User")
            name_parts = user_name.split(" ", 1)
            first_name = name_parts[0] if name_parts else "Kraliki"
            last_name = name_parts[1] if len(name_parts) > 1 else "User"

            synthetic_user_id = uuid.uuid5(uuid.NAMESPACE_DNS, user_email)
            synthetic_company_id = uuid.uuid5(uuid.NAMESPACE_DNS, "kraliki-internal")
            return {
                "sub": str(synthetic_user_id),
                "company_id": str(synthetic_company_id),
                "email": user_email,
                "role": "owner",
                "first_name": first_name,
                "last_name": last_name,
                "company_name": "Kraliki Internal",
                "department_id": None,
            }

    if not credentials:
        return None
    try:
        return verify_token(credentials.credentials)
    except HTTPException:
        return None


def create_user_token_payload(
    user_id: UUID,
    company_id: UUID,
    email: str,
    role: str,
    first_name: str,
    last_name: str,
    company_name: str,
    department_id: Optional[UUID] = None,
) -> dict:
    """
    Create standardized token payload.
    Includes all data needed for tenant isolation.
    """
    return {
        "sub": str(user_id),
        "company_id": str(company_id),
        "email": email,
        "role": role,
        "first_name": first_name,
        "last_name": last_name,
        "company_name": company_name,
        "department_id": str(department_id) if department_id else None,
    }


# Helper to validate production security
def validate_production_security():
    """
    Check that production has secure JWT configuration.
    Call on startup in production mode.

    Raises RuntimeError if:
    - JWT_SECRET_KEY is empty, too short, or a known placeholder
    - Ed25519 is enabled but keys are missing
    - Stripe keys are placeholders
    """
    errors = []

    if not settings.debug:
        # Use Settings.validate_secrets() for basic configuration checks
        config_errors = settings.validate_secrets()
        errors.extend(config_errors)

        # Check JWT secret - empty string or known insecure defaults
        insecure_secrets = {
            "",
            "your-secret-key-change-in-production",
            "your-super-secret-key-change-in-production",
            "change_me_generate_secure_secret",
            "changeme",
            "secret",
            "password",
            "12345678",
            "replace_me",
        }
        if (
            settings.jwt_secret_key
            and settings.jwt_secret_key.lower() in insecure_secrets
        ):
            errors.append("JWT_SECRET_KEY is a known insecure default")
        elif settings.jwt_secret_key and len(settings.jwt_secret_key) < 32:
            errors.append("JWT_SECRET_KEY is too short (minimum 32 characters)")

        # Check Stripe keys if any are set (indicating Stripe integration is active)
        if settings.stripe_secret_key:
            if settings.stripe_secret_key.startswith("sk_test_"):
                logger.warning("SECURITY: Using Stripe TEST key in production!")
            if not settings.stripe_webhook_secret:
                errors.append("STRIPE_WEBHOOK_SECRET required when using Stripe")

            # Check for placeholder price IDs
            placeholder_prices = [
                settings.stripe_price_personal,
                settings.stripe_price_premium,
                settings.stripe_price_pro,
            ]
            if any("placeholder" in p.lower() for p in placeholder_prices):
                errors.append(
                    "Stripe price IDs contain placeholders - configure real price IDs"
                )

        # Check other critical secrets
        if settings.gemini_api_key == "" and settings.use_ed25519:
            logger.warning(
                "SECURITY: GEMINI_API_KEY not configured (AI features disabled)"
            )

        if errors:
            for error in errors:
                logger.error(f"SECURITY: {error}")
            raise RuntimeError(
                f"Production security validation failed:\n"
                + "\n".join(f"  - {e}" for e in errors)
            )
