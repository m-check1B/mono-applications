"""
Targeted tests to improve coverage for Zitadel Auth
"""
import pytest
from unittest.mock import MagicMock, patch
from fastapi import HTTPException

# Mock auth_core before importing service
mock_auth_core = MagicMock()
mock_zitadel = MagicMock()
mock_auth_core.zitadel = mock_zitadel

with patch.dict("sys.modules", {"auth_core": mock_auth_core, "auth_core.zitadel": mock_zitadel, "auth_core.fastapi_zitadel": MagicMock()}):
    from app.core import zitadel_auth as service

def test_is_zitadel_enabled():
    """Test is_zitadel_enabled logic"""
    with patch("os.getenv", return_value="zitadel"):
        assert service.is_zitadel_enabled() is True
    with patch("os.getenv", return_value="ed25519"):
        assert service.is_zitadel_enabled() is False

def test_get_auth_mode():
    """Test get_auth_mode logic"""
    with patch("os.getenv", return_value="test_mode"):
        assert service.get_auth_mode() == "test_mode"

def test_create_auth_exception():
    """Test create_auth_exception logic"""
    exc = service.create_auth_exception("Error message")
    assert exc.status_code == 401
    assert exc.detail == "Error message"
    assert "WWW-Authenticate" in exc.headers

@pytest.mark.asyncio
async def test_get_current_user_optional_zitadel_none():
    """Test get_current_user_optional_zitadel with no credentials"""
    result = await service.get_current_user_optional_zitadel(None)
    assert result is None

@pytest.mark.asyncio
async def test_get_current_user_zitadel_none():
    """Test get_current_user_zitadel with no credentials raises 401"""
    with pytest.raises(HTTPException) as exc:
        await service.get_current_user_zitadel(None)
    assert exc.value.status_code == 401
