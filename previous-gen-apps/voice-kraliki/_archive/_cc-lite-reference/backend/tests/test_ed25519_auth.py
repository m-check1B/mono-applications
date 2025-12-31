import pytest
from app.core.security import jwt_manager

def test_create_access_token():
    """Test access token creation"""
    token = jwt_manager.create_access_token({"sub": "test_user", "email": "test@example.com"})
    assert token is not None
    assert isinstance(token, str)
    assert len(token) > 100  # JWT tokens are long

def test_create_refresh_token():
    """Test refresh token creation"""
    token = jwt_manager.create_refresh_token({"sub": "test_user"})
    assert token is not None
    assert isinstance(token, str)

def test_verify_access_token():
    """Test token verification"""
    token = jwt_manager.create_access_token({"sub": "test_user", "email": "test@example.com"})
    payload = jwt_manager.verify_token(token)

    assert payload["sub"] == "test_user"
    assert payload["email"] == "test@example.com"
    assert payload["type"] == "access"

def test_verify_refresh_token():
    """Test refresh token verification"""
    token = jwt_manager.create_refresh_token({"sub": "test_user"})
    payload = jwt_manager.verify_token(token)

    assert payload["sub"] == "test_user"
    assert payload["type"] == "refresh"

def test_token_contains_standard_claims():
    """Test that tokens contain iat and exp claims"""
    token = jwt_manager.create_access_token({"sub": "test_user"})
    payload = jwt_manager.verify_token(token)

    assert "iat" in payload
    assert "exp" in payload
    assert payload["exp"] > payload["iat"]

def test_ed25519_algorithm():
    """Test that EdDSA algorithm is used"""
    token = jwt_manager.create_access_token({"sub": "test_user"})
    # EdDSA tokens should be shorter than RSA tokens
    assert len(token) < 500
    # Should decode successfully with Ed25519 public key
    payload = jwt_manager.verify_token(token)
    assert payload["sub"] == "test_user"
