"""
Tests for Permissions module - RBAC decorators and dependencies.

Tests cover:
- require_permissions decorator
- require_role decorator
- require_min_role decorator
- require_resource_access decorator
- FastAPI permission dependencies
"""

import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from uuid import uuid4

from fastapi import HTTPException

from app.auth.permissions import (
    require_permissions,
    require_role,
    require_min_role,
    require_resource_access,
    require_admin_user,
    require_supervisor_or_admin,
    require_user_management_permission,
    require_analytics_access,
    require_campaign_management,
    require_provider_management,
    require_system_admin,
)
from app.models.user import User, UserRole, Permission


@pytest.fixture
def mock_user():
    """Create a mock agent user."""
    user = MagicMock(spec=User)
    user.id = str(uuid4())
    user.email = f"agent-{uuid4()}@example.com"
    user.role = UserRole.AGENT
    user.is_active = True
    user.permissions = []
    return user


@pytest.fixture
def mock_admin_user():
    """Create a mock admin user."""
    user = MagicMock(spec=User)
    user.id = str(uuid4())
    user.email = f"admin-{uuid4()}@example.com"
    user.role = UserRole.ADMIN
    user.is_active = True
    user.permissions = [p.value for p in Permission]
    return user


@pytest.fixture
def mock_supervisor_user():
    """Create a mock supervisor user."""
    user = MagicMock(spec=User)
    user.id = str(uuid4())
    user.email = f"supervisor-{uuid4()}@example.com"
    user.role = UserRole.SUPERVISOR
    user.is_active = True
    user.permissions = [Permission.CAMPAIGN_READ.value, Permission.ANALYTICS_READ.value]
    return user


@pytest.fixture
def mock_rbac_service():
    """Create a mock RBAC service."""
    mock = MagicMock()
    mock.has_any_permission.return_value = True
    mock.has_permission.return_value = True
    mock.can_manage_role.return_value = True
    mock.can_access_resource.return_value = True
    return mock


class TestRequirePermissionsDecorator:
    """Tests for require_permissions decorator."""

    @pytest.mark.asyncio
    async def test_require_permissions_success(self, mock_admin_user, mock_rbac_service):
        """Test decorator passes with correct permissions."""
        with patch("app.auth.permissions.get_rbac_service", return_value=mock_rbac_service):

            @require_permissions(Permission.CAMPAIGN_READ)
            async def protected_endpoint(current_user):
                return "success"

            result = await protected_endpoint(current_user=mock_admin_user)
            assert result == "success"

    @pytest.mark.asyncio
    async def test_require_permissions_list(self, mock_admin_user, mock_rbac_service):
        """Test decorator with list of permissions."""
        with patch("app.auth.permissions.get_rbac_service", return_value=mock_rbac_service):

            @require_permissions([Permission.CAMPAIGN_READ, Permission.ANALYTICS_READ])
            async def protected_endpoint(current_user):
                return "success"

            result = await protected_endpoint(current_user=mock_admin_user)
            assert result == "success"

    @pytest.mark.asyncio
    async def test_require_permissions_no_user(self):
        """Test decorator fails without user."""

        @require_permissions(Permission.CAMPAIGN_READ)
        async def protected_endpoint(current_user=None):
            return "success"

        with pytest.raises(HTTPException) as exc_info:
            await protected_endpoint()

        assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_require_permissions_denied(self, mock_user):
        """Test decorator denies access without permission."""
        mock_rbac = MagicMock()
        mock_rbac.has_any_permission.return_value = False

        with patch("app.auth.permissions.get_rbac_service", return_value=mock_rbac):

            @require_permissions(Permission.SYSTEM_ADMIN)
            async def protected_endpoint(current_user):
                return "success"

            with pytest.raises(HTTPException) as exc_info:
                await protected_endpoint(current_user=mock_user)

            assert exc_info.value.status_code == 403


class TestRequireRoleDecorator:
    """Tests for require_role decorator."""

    @pytest.mark.asyncio
    async def test_require_role_success(self, mock_admin_user):
        """Test decorator passes with correct role."""

        @require_role(UserRole.ADMIN)
        async def protected_endpoint(current_user):
            return "success"

        result = await protected_endpoint(current_user=mock_admin_user)
        assert result == "success"

    @pytest.mark.asyncio
    async def test_require_role_list(self, mock_supervisor_user):
        """Test decorator with list of roles."""

        @require_role([UserRole.SUPERVISOR, UserRole.ADMIN])
        async def protected_endpoint(current_user):
            return "success"

        result = await protected_endpoint(current_user=mock_supervisor_user)
        assert result == "success"

    @pytest.mark.asyncio
    async def test_require_role_no_user(self):
        """Test decorator fails without user."""

        @require_role(UserRole.ADMIN)
        async def protected_endpoint(current_user=None):
            return "success"

        with pytest.raises(HTTPException) as exc_info:
            await protected_endpoint()

        assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_require_role_denied(self, mock_user):
        """Test decorator denies access without role."""

        @require_role(UserRole.ADMIN)
        async def protected_endpoint(current_user):
            return "success"

        with pytest.raises(HTTPException) as exc_info:
            await protected_endpoint(current_user=mock_user)

        assert exc_info.value.status_code == 403


class TestRequireMinRoleDecorator:
    """Tests for require_min_role decorator."""

    @pytest.mark.asyncio
    async def test_require_min_role_success(self, mock_admin_user, mock_rbac_service):
        """Test decorator passes with higher role."""
        with patch("app.auth.permissions.get_rbac_service", return_value=mock_rbac_service):

            @require_min_role(UserRole.SUPERVISOR)
            async def protected_endpoint(current_user):
                return "success"

            result = await protected_endpoint(current_user=mock_admin_user)
            assert result == "success"

    @pytest.mark.asyncio
    async def test_require_min_role_no_user(self):
        """Test decorator fails without user."""

        @require_min_role(UserRole.SUPERVISOR)
        async def protected_endpoint(current_user=None):
            return "success"

        with pytest.raises(HTTPException) as exc_info:
            await protected_endpoint()

        assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_require_min_role_denied(self, mock_user):
        """Test decorator denies access with lower role."""
        mock_rbac = MagicMock()
        mock_rbac.can_manage_role.return_value = False

        with patch("app.auth.permissions.get_rbac_service", return_value=mock_rbac):

            @require_min_role(UserRole.SUPERVISOR)
            async def protected_endpoint(current_user):
                return "success"

            with pytest.raises(HTTPException) as exc_info:
                await protected_endpoint(current_user=mock_user)

            assert exc_info.value.status_code == 403


class TestRequireResourceAccessDecorator:
    """Tests for require_resource_access decorator."""

    @pytest.mark.asyncio
    async def test_require_resource_access_success(self, mock_admin_user, mock_rbac_service):
        """Test decorator passes with resource access."""
        with patch("app.auth.permissions.get_rbac_service", return_value=mock_rbac_service):

            @require_resource_access("campaign", "write")
            async def protected_endpoint(current_user):
                return "success"

            result = await protected_endpoint(current_user=mock_admin_user)
            assert result == "success"

    @pytest.mark.asyncio
    async def test_require_resource_access_no_user(self):
        """Test decorator fails without user."""

        @require_resource_access("campaign", "write")
        async def protected_endpoint(current_user=None):
            return "success"

        with pytest.raises(HTTPException) as exc_info:
            await protected_endpoint()

        assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_require_resource_access_denied(self, mock_user):
        """Test decorator denies access without resource permission."""
        mock_rbac = MagicMock()
        mock_rbac.can_access_resource.return_value = False

        with patch("app.auth.permissions.get_rbac_service", return_value=mock_rbac):

            @require_resource_access("user", "delete")
            async def protected_endpoint(current_user):
                return "success"

            with pytest.raises(HTTPException) as exc_info:
                await protected_endpoint(current_user=mock_user)

            assert exc_info.value.status_code == 403


class TestFastAPIDependencies:
    """Tests for FastAPI permission dependencies."""

    def test_require_admin_user_success(self, mock_admin_user):
        """Test require_admin_user passes for admin."""
        result = require_admin_user(current_user=mock_admin_user)
        assert result == mock_admin_user

    def test_require_admin_user_denied(self, mock_user):
        """Test require_admin_user fails for non-admin."""
        with pytest.raises(HTTPException) as exc_info:
            require_admin_user(current_user=mock_user)

        assert exc_info.value.status_code == 403

    def test_require_supervisor_or_admin_with_supervisor(self, mock_supervisor_user):
        """Test require_supervisor_or_admin passes for supervisor."""
        result = require_supervisor_or_admin(current_user=mock_supervisor_user)
        assert result == mock_supervisor_user

    def test_require_supervisor_or_admin_with_admin(self, mock_admin_user):
        """Test require_supervisor_or_admin passes for admin."""
        result = require_supervisor_or_admin(current_user=mock_admin_user)
        assert result == mock_admin_user

    def test_require_supervisor_or_admin_denied(self, mock_user):
        """Test require_supervisor_or_admin fails for agent."""
        with pytest.raises(HTTPException) as exc_info:
            require_supervisor_or_admin(current_user=mock_user)

        assert exc_info.value.status_code == 403


class TestPermissionDependencies:
    """Tests for specific permission dependencies."""

    def test_require_user_management_permission_success(self, mock_admin_user, mock_rbac_service):
        """Test user management permission passes for admin."""
        mock_db = MagicMock()

        with patch("app.auth.permissions.get_rbac_service", return_value=mock_rbac_service):
            result = require_user_management_permission(current_user=mock_admin_user, db=mock_db)
            assert result == mock_admin_user

    def test_require_user_management_permission_denied(self, mock_user):
        """Test user management permission fails without permission."""
        mock_db = MagicMock()
        mock_rbac = MagicMock()
        mock_rbac.has_permission.return_value = False

        with patch("app.auth.permissions.get_rbac_service", return_value=mock_rbac):
            with pytest.raises(HTTPException) as exc_info:
                require_user_management_permission(current_user=mock_user, db=mock_db)
            assert exc_info.value.status_code == 403

    def test_require_analytics_access_success(self, mock_supervisor_user, mock_rbac_service):
        """Test analytics access passes for supervisor."""
        mock_db = MagicMock()

        with patch("app.auth.permissions.get_rbac_service", return_value=mock_rbac_service):
            result = require_analytics_access(current_user=mock_supervisor_user, db=mock_db)
            assert result == mock_supervisor_user

    def test_require_analytics_access_denied(self, mock_user):
        """Test analytics access fails without permission."""
        mock_db = MagicMock()
        mock_rbac = MagicMock()
        mock_rbac.has_permission.return_value = False

        with patch("app.auth.permissions.get_rbac_service", return_value=mock_rbac):
            with pytest.raises(HTTPException) as exc_info:
                require_analytics_access(current_user=mock_user, db=mock_db)
            assert exc_info.value.status_code == 403

    def test_require_campaign_management_success(self, mock_admin_user, mock_rbac_service):
        """Test campaign management passes for admin."""
        mock_db = MagicMock()

        with patch("app.auth.permissions.get_rbac_service", return_value=mock_rbac_service):
            result = require_campaign_management(current_user=mock_admin_user, db=mock_db)
            assert result == mock_admin_user

    def test_require_provider_management_success(self, mock_admin_user, mock_rbac_service):
        """Test provider management passes for admin."""
        mock_db = MagicMock()

        with patch("app.auth.permissions.get_rbac_service", return_value=mock_rbac_service):
            result = require_provider_management(current_user=mock_admin_user, db=mock_db)
            assert result == mock_admin_user

    def test_require_system_admin_success(self, mock_admin_user, mock_rbac_service):
        """Test system admin passes for admin."""
        mock_db = MagicMock()

        with patch("app.auth.permissions.get_rbac_service", return_value=mock_rbac_service):
            result = require_system_admin(current_user=mock_admin_user, db=mock_db)
            assert result == mock_admin_user

    def test_require_system_admin_denied(self, mock_user):
        """Test system admin fails for non-admin."""
        mock_db = MagicMock()
        mock_rbac = MagicMock()
        mock_rbac.has_permission.return_value = False

        with patch("app.auth.permissions.get_rbac_service", return_value=mock_rbac):
            with pytest.raises(HTTPException) as exc_info:
                require_system_admin(current_user=mock_user, db=mock_db)
            assert exc_info.value.status_code == 403


class TestUserRoleEnum:
    """Tests for UserRole enum values."""

    def test_user_role_values(self):
        """Test that all expected roles are defined."""
        expected_roles = ["USER", "ADMIN", "AGENT", "SUPERVISOR", "ANALYST"]
        for role in expected_roles:
            assert hasattr(UserRole, role)

    def test_user_role_string_conversion(self):
        """Test role string conversion."""
        assert UserRole.ADMIN.value == "ADMIN"
        assert UserRole.AGENT.value == "AGENT"


class TestPermissionEnum:
    """Tests for Permission enum values."""

    def test_permission_values_format(self):
        """Test that permissions follow resource:action format."""
        for perm in Permission:
            assert ":" in perm.value

    def test_core_permissions_exist(self):
        """Test that core permissions are defined."""
        expected = [
            "USER_READ",
            "USER_WRITE",
            "USER_DELETE",
            "SESSION_READ",
            "SESSION_WRITE",
            "SESSION_DELETE",
            "CAMPAIGN_READ",
            "CAMPAIGN_WRITE",
            "CAMPAIGN_DELETE",
            "ANALYTICS_READ",
            "SYSTEM_ADMIN",
        ]
        for perm in expected:
            assert hasattr(Permission, perm)
