import pytest
from unittest.mock import MagicMock, patch
from datetime import timedelta
from fastapi import HTTPException, Request
from app.core.security import (
    verify_password, 
    get_password_hash, 
    create_access_token, 
    create_agent_token,
    decode_token,
    get_current_user,
    get_optional_user,
    generate_id
)
from app.models.user import User

def test_password_hashing():
    pwd = "secret-password"
    hashed = get_password_hash(pwd)
    assert verify_password(pwd, hashed) is True
    assert verify_password("wrong", hashed) is False

def test_create_access_token():
    token = create_access_token({"sub": "user1"})
    assert isinstance(token, str)
    payload = decode_token(token)
    assert payload["sub"] == "user1"

def test_create_agent_token():
    token = create_agent_token(user_id="user1", data={"org": "org1"})
    payload = decode_token(token)
    assert payload["sub"] == "user1"
    assert payload["scope"] == "agent"
    assert payload["org"] == "org1"
    
    with pytest.raises(ValueError):
        create_agent_token(user_id=None)

@pytest.mark.asyncio
async def test_get_current_user_bypass():
    mock_request = MagicMock()
    mock_request.headers = {
        "X-Kraliki-Session": "kraliki-internal",
        "X-Kraliki-User-Email": "agent@kraliki.local",
        "X-Kraliki-User-Name": "Kraliki User",
        "X-Kraliki-User-Id": "unknown"
    }
    
    mock_db = MagicMock()
    mock_user = MagicMock(spec=User)
    mock_db.query.return_value.filter.return_value.first.return_value = mock_user
    
    user = await get_current_user(mock_request, credentials=None, db=mock_db)
    assert user == mock_user

@pytest.mark.asyncio
async def test_get_current_user_no_credentials():
    mock_request = MagicMock()
    mock_request.headers = {}  # No Kraliki headers
    mock_request.state = MagicMock()
    mock_request.state.user_id = None  # No platform user

    with pytest.raises(HTTPException) as exc:
        await get_current_user(mock_request, credentials=None)
    assert exc.value.status_code == 401

@pytest.mark.asyncio
async def test_get_optional_user():
    # Success case
    with patch("app.core.security.get_current_user", return_value="user"):
        result = await get_optional_user(None)
        assert result == "user"
    
    # Unauthorized case
    with patch("app.core.security.get_current_user", side_effect=HTTPException(status_code=401)):
        result = await get_optional_user(None)
        assert result is None

def test_generate_id():
    id1 = generate_id()
    id2 = generate_id()
    assert len(id1) > 10
    assert id1 != id2
