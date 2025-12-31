"""
FastAPI Integration for Auth Core

Provides FastAPI-specific utilities:
- HTTPException-raising token verification
- OAuth2 password bearer dependency
- Current user dependency factory
"""

from typing import Optional, Callable, Awaitable, TypeVar, Generic
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer

from auth_core.jwt import (
    Ed25519Auth,
    TokenPayload,
    TokenType,
    TokenError,
    TokenExpiredError,
    TokenInvalidError,
    TokenTypeMismatchError,
)
from auth_core.revocation import TokenBlacklist


T = TypeVar("T")  # User model type


def create_auth_exception(detail: str) -> HTTPException:
    """Create standard 401 Unauthorized exception."""
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


class FastAPIAuth(Generic[T]):
    """
    FastAPI integration for Ed25519Auth.

    Usage:
        auth = Ed25519Auth(keys_dir="keys")
        blacklist = TokenBlacklist(redis_url="redis://localhost")
        fastapi_auth = FastAPIAuth(auth, blacklist, get_user_func)

        @app.get("/protected")
        async def protected(user: User = Depends(fastapi_auth.get_current_user)):
            return {"user": user.id}
    """

    def __init__(
        self,
        auth: Ed25519Auth,
        blacklist: Optional[TokenBlacklist] = None,
        get_user: Optional[Callable[[str], Awaitable[Optional[T]]]] = None,
        token_url: str = "/api/auth/login",
    ):
        """
        Initialize FastAPI auth integration.

        Args:
            auth: Ed25519Auth instance
            blacklist: Optional TokenBlacklist for revocation checks
            get_user: Async function to get user by ID
            token_url: URL for OAuth2 token endpoint
        """
        self.auth = auth
        self.blacklist = blacklist
        self.get_user = get_user
        self.oauth2_scheme = OAuth2PasswordBearer(tokenUrl=token_url)

    def verify_token_or_raise(
        self,
        token: str,
        expected_type: TokenType = TokenType.ACCESS,
    ) -> TokenPayload:
        """
        Verify token and raise HTTPException on failure.

        Args:
            token: JWT token string
            expected_type: Expected token type

        Returns:
            TokenPayload if valid

        Raises:
            HTTPException: 401 Unauthorized on any error
        """
        try:
            return self.auth.verify_token(token, expected_type)
        except TokenExpiredError:
            raise create_auth_exception("Token has expired")
        except TokenTypeMismatchError as e:
            raise create_auth_exception(
                f"Invalid token type. Expected '{e.expected}', got '{e.got}'"
            )
        except TokenInvalidError as e:
            raise create_auth_exception(str(e))
        except TokenError as e:
            raise create_auth_exception(f"Token verification failed: {e}")

    async def verify_token_with_revocation(
        self,
        token: str,
        expected_type: TokenType = TokenType.ACCESS,
    ) -> TokenPayload:
        """
        Verify token and check revocation status.

        Args:
            token: JWT token string
            expected_type: Expected token type

        Returns:
            TokenPayload if valid and not revoked

        Raises:
            HTTPException: 401 Unauthorized if invalid or revoked
        """
        payload = self.verify_token_or_raise(token, expected_type)

        if self.blacklist:
            # Check both token and user revocation
            is_revoked = await self.blacklist.is_token_or_user_revoked(
                token, payload.sub
            )
            if is_revoked:
                raise create_auth_exception("Token has been revoked")

        return payload

    async def get_current_user_id(
        self,
        token: str = Depends(OAuth2PasswordBearer(tokenUrl="/api/auth/login")),
    ) -> str:
        """
        FastAPI dependency to get current user ID from token.

        Usage:
            @app.get("/me")
            async def me(user_id: str = Depends(auth.get_current_user_id)):
                return {"user_id": user_id}
        """
        payload = await self.verify_token_with_revocation(token)
        return payload.sub

    def create_get_current_user(self) -> Callable:
        """
        Create a FastAPI dependency for getting the current user.

        Returns:
            Async dependency function

        Usage:
            get_current_user = fastapi_auth.create_get_current_user()

            @app.get("/me")
            async def me(user: User = Depends(get_current_user)):
                return user
        """
        oauth2_scheme = self.oauth2_scheme

        async def get_current_user(
            token: str = Depends(oauth2_scheme),
        ) -> T:
            payload = await self.verify_token_with_revocation(token)

            if not self.get_user:
                raise ValueError("get_user function not configured")

            user = await self.get_user(payload.sub)
            if not user:
                raise create_auth_exception("User not found")

            return user

        return get_current_user

    def create_get_current_user_optional(self) -> Callable:
        """
        Create a FastAPI dependency for optional user authentication.

        Returns None if no token provided, raises if token is invalid.

        Usage:
            get_current_user_optional = auth.create_get_current_user_optional()

            @app.get("/items")
            async def items(user: Optional[User] = Depends(get_current_user_optional)):
                if user:
                    return user_items(user)
                return public_items()
        """
        oauth2_scheme = OAuth2PasswordBearer(
            tokenUrl=self.oauth2_scheme.model.flows.password.tokenUrl,
            auto_error=False,
        )

        async def get_current_user_optional(
            token: Optional[str] = Depends(oauth2_scheme),
        ) -> Optional[T]:
            if not token:
                return None

            payload = await self.verify_token_with_revocation(token)

            if not self.get_user:
                return None

            return await self.get_user(payload.sub)

        return get_current_user_optional


# Convenience function for simple setups
def create_token_dependency(
    auth: Ed25519Auth,
    blacklist: Optional[TokenBlacklist] = None,
    token_url: str = "/api/auth/login",
) -> Callable:
    """
    Create a simple token verification dependency.

    Usage:
        verify_token = create_token_dependency(auth, blacklist)

        @app.get("/protected")
        async def protected(payload: TokenPayload = Depends(verify_token)):
            return {"user_id": payload.sub}
    """
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl=token_url)
    fastapi_auth = FastAPIAuth(auth, blacklist)

    async def verify_token(token: str = Depends(oauth2_scheme)) -> TokenPayload:
        return await fastapi_auth.verify_token_with_revocation(token)

    return verify_token
