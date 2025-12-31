"""
FastAPI Integration for Zitadel Authentication

Provides FastAPI-specific utilities for Zitadel JWT validation:
- HTTPException-raising token verification
- OAuth2 bearer dependency
- Current user dependency factory
- Role-based access control

Usage:
    from auth_core.fastapi_zitadel import FastAPIZitadelAuth

    auth = FastAPIZitadelAuth(
        issuer="https://identity.verduona.dev",
        client_id="your-client-id"
    )

    @app.get("/protected")
    async def protected(user: ZitadelTokenPayload = Depends(auth.get_current_user)):
        return {"user_id": user.sub, "email": user.email}
"""

from typing import Optional, Callable, Awaitable, TypeVar, Generic, List, Set
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer, HTTPBearer, HTTPAuthorizationCredentials

from auth_core.zitadel import (
    ZitadelAuth,
    ZitadelTokenPayload,
    ZitadelTokenError,
    ZitadelTokenExpiredError,
    ZitadelTokenInvalidError,
)


T = TypeVar("T")  # User model type


def create_auth_exception(detail: str) -> HTTPException:
    """Create standard 401 Unauthorized exception."""
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


def create_forbidden_exception(detail: str) -> HTTPException:
    """Create standard 403 Forbidden exception."""
    return HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=detail,
    )


class FastAPIZitadelAuth(Generic[T]):
    """
    FastAPI integration for Zitadel authentication.

    Provides dependency injection for protected routes with support for:
    - Token validation via JWKS
    - User lookup
    - Role-based access control

    Usage:
        auth = FastAPIZitadelAuth(
            issuer="https://identity.verduona.dev",
            client_id="your-client-id"
        )

        # Simple protection - returns token payload
        @app.get("/me")
        async def me(payload: ZitadelTokenPayload = Depends(auth.get_current_user)):
            return {"user_id": payload.sub}

        # With user lookup
        auth_with_users = FastAPIZitadelAuth(
            issuer="...",
            client_id="...",
            get_user=get_user_from_db
        )

        @app.get("/profile")
        async def profile(user: User = Depends(auth_with_users.get_current_user_entity)):
            return user

        # Role-based access
        @app.get("/admin")
        async def admin(user = Depends(auth.require_roles(["admin"]))):
            return {"admin": True}
    """

    def __init__(
        self,
        issuer: str,
        client_id: Optional[str] = None,
        audiences: Optional[List[str]] = None,
        get_user: Optional[Callable[[str], Awaitable[Optional[T]]]] = None,
        use_http_bearer: bool = True,
    ):
        """
        Initialize FastAPI Zitadel auth integration.

        Args:
            issuer: Zitadel instance URL
            client_id: Client ID for audience validation
            audiences: List of allowed audiences (client IDs)
            get_user: Async function to get user entity by Zitadel user ID
            use_http_bearer: Use HTTPBearer (recommended) instead of OAuth2PasswordBearer
        """
        self.zitadel = ZitadelAuth(
            issuer=issuer,
            audience=client_id,
            audiences=audiences,
        )
        self.get_user_fn = get_user
        self.use_http_bearer = use_http_bearer

        if use_http_bearer:
            self._bearer = HTTPBearer(auto_error=False)
        else:
            self._oauth2_scheme = OAuth2PasswordBearer(
                tokenUrl=f"{issuer}/oauth/v2/token",
                auto_error=False,
            )

    def verify_token_or_raise(self, token: str) -> ZitadelTokenPayload:
        """
        Verify token and raise HTTPException on failure.

        Args:
            token: JWT token string

        Returns:
            ZitadelTokenPayload if valid

        Raises:
            HTTPException: 401 Unauthorized on any error
        """
        try:
            return self.zitadel.verify_token(token)
        except ZitadelTokenExpiredError:
            raise create_auth_exception("Token has expired")
        except ZitadelTokenInvalidError as e:
            raise create_auth_exception(str(e))
        except ZitadelTokenError as e:
            raise create_auth_exception(f"Token verification failed: {e}")

    async def _get_token_from_request(
        self,
        credentials: Optional[HTTPAuthorizationCredentials] = None,
        token: Optional[str] = None,
    ) -> str:
        """Extract token from request credentials."""
        if self.use_http_bearer:
            if not credentials:
                raise create_auth_exception("Not authenticated")
            return credentials.credentials
        else:
            if not token:
                raise create_auth_exception("Not authenticated")
            return token

    def get_current_user(self) -> Callable:
        """
        Create dependency for getting current user token payload.

        Returns ZitadelTokenPayload with user info from token.

        Usage:
            @app.get("/me")
            async def me(user: ZitadelTokenPayload = Depends(auth.get_current_user())):
                return {"sub": user.sub, "email": user.email}
        """
        if self.use_http_bearer:
            bearer = self._bearer

            async def get_current_user_dep(
                credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer),
            ) -> ZitadelTokenPayload:
                token = await self._get_token_from_request(credentials=credentials)
                return self.verify_token_or_raise(token)
        else:
            oauth2 = self._oauth2_scheme

            async def get_current_user_dep(
                token: Optional[str] = Depends(oauth2),
            ) -> ZitadelTokenPayload:
                token = await self._get_token_from_request(token=token)
                return self.verify_token_or_raise(token)

        return get_current_user_dep

    def get_current_user_optional(self) -> Callable:
        """
        Create dependency for optional authentication.

        Returns None if no token, ZitadelTokenPayload if valid token.
        Raises HTTPException if token is present but invalid.

        Usage:
            @app.get("/items")
            async def items(user: Optional[ZitadelTokenPayload] = Depends(auth.get_current_user_optional())):
                if user:
                    return private_items(user)
                return public_items()
        """
        if self.use_http_bearer:
            bearer = self._bearer

            async def get_current_user_optional_dep(
                credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer),
            ) -> Optional[ZitadelTokenPayload]:
                if not credentials:
                    return None
                return self.verify_token_or_raise(credentials.credentials)
        else:
            oauth2 = self._oauth2_scheme

            async def get_current_user_optional_dep(
                token: Optional[str] = Depends(oauth2),
            ) -> Optional[ZitadelTokenPayload]:
                if not token:
                    return None
                return self.verify_token_or_raise(token)

        return get_current_user_optional_dep

    def get_current_user_entity(self) -> Callable:
        """
        Create dependency for getting user entity from database.

        Requires get_user function to be configured.

        Usage:
            async def get_user_from_db(zitadel_id: str) -> Optional[User]:
                return await db.users.find_one({"zitadel_id": zitadel_id})

            auth = FastAPIZitadelAuth(..., get_user=get_user_from_db)

            @app.get("/profile")
            async def profile(user: User = Depends(auth.get_current_user_entity())):
                return user
        """
        if not self.get_user_fn:
            raise ValueError("get_user function not configured")

        get_payload = self.get_current_user()
        get_user = self.get_user_fn

        async def get_current_user_entity_dep(
            payload: ZitadelTokenPayload = Depends(get_payload),
        ) -> T:
            user = await get_user(payload.sub)
            if not user:
                raise create_auth_exception("User not found")
            return user

        return get_current_user_entity_dep

    def require_roles(self, roles: List[str], require_all: bool = False) -> Callable:
        """
        Create dependency that requires specific roles.

        Checks roles from Zitadel's project roles claim.

        Args:
            roles: Required roles
            require_all: If True, user must have ALL roles. If False, ANY role.

        Usage:
            @app.get("/admin")
            async def admin_only(user = Depends(auth.require_roles(["admin"]))):
                return {"admin": True}

            @app.get("/super")
            async def super_admin(user = Depends(auth.require_roles(["admin", "super"], require_all=True))):
                return {"super_admin": True}
        """
        get_payload = self.get_current_user()
        required_roles = set(roles)

        async def require_roles_dep(
            payload: ZitadelTokenPayload = Depends(get_payload),
        ) -> ZitadelTokenPayload:
            # Extract user's roles from payload
            user_roles: Set[str] = set()
            for role_data in payload.roles.values():
                user_roles.update(role_data.keys())

            if require_all:
                # Must have all required roles
                if not required_roles.issubset(user_roles):
                    missing = required_roles - user_roles
                    raise create_forbidden_exception(
                        f"Missing required roles: {', '.join(missing)}"
                    )
            else:
                # Must have at least one required role
                if not required_roles.intersection(user_roles):
                    raise create_forbidden_exception(
                        f"Requires one of: {', '.join(required_roles)}"
                    )

            return payload

        return require_roles_dep

    def require_org(self, org_id: Optional[str] = None, org_name: Optional[str] = None) -> Callable:
        """
        Create dependency that requires specific organization.

        Args:
            org_id: Required organization ID
            org_name: Required organization name

        Usage:
            @app.get("/org-resource")
            async def org_only(user = Depends(auth.require_org(org_id="..."))):
                return {"allowed": True}
        """
        get_payload = self.get_current_user()

        async def require_org_dep(
            payload: ZitadelTokenPayload = Depends(get_payload),
        ) -> ZitadelTokenPayload:
            if org_id and payload.org_id != org_id:
                raise create_forbidden_exception("Organization access denied")
            if org_name and payload.org_name != org_name:
                raise create_forbidden_exception("Organization access denied")
            return payload

        return require_org_dep


# Convenience function for simple setups
def create_zitadel_dependency(
    issuer: str = "https://identity.verduona.dev",
    client_id: Optional[str] = None,
) -> Callable:
    """
    Create a simple Zitadel token verification dependency.

    Usage:
        verify_user = create_zitadel_dependency(client_id="my-app")

        @app.get("/protected")
        async def protected(user: ZitadelTokenPayload = Depends(verify_user)):
            return {"user_id": user.sub}
    """
    auth = FastAPIZitadelAuth(issuer=issuer, client_id=client_id)
    return auth.get_current_user()
