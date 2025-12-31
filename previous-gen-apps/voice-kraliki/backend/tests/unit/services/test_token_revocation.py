"""
Test Token Revocation Service
Simple integration test for JWT token revocation functionality
"""

import asyncio
from datetime import datetime, timedelta, timezone
from app.auth.token_revocation import get_revocation_service
from app.auth.ed25519_auth import get_auth_manager


def test_individual_token_revocation():
    """Test revoking a single token by JTI"""
    print("\n=== Testing Individual Token Revocation ===")

    revocation_service = get_revocation_service()

    # Test token data
    jti = "test-token-123"
    expires_at = datetime.now(timezone.utc) + timedelta(hours=1)

    # Check health
    if not revocation_service.health_check():
        print("❌ Redis is not available. Please start Redis server.")
        print("   Run: redis-server")
        return False

    print("✓ Redis connection healthy")

    # Revoke token
    success = revocation_service.revoke_token(jti, expires_at)
    if success:
        print(f"✓ Token revoked: {jti}")
    else:
        print(f"❌ Failed to revoke token: {jti}")
        return False

    # Check if revoked
    is_revoked = revocation_service.is_token_revoked(jti)
    if is_revoked:
        print(f"✓ Token correctly identified as revoked")
    else:
        print(f"❌ Token not found in revocation list")
        return False

    # Check that a different token is not revoked
    different_jti = "different-token-456"
    is_different_revoked = revocation_service.is_token_revoked(different_jti)
    if not is_different_revoked:
        print(f"✓ Different token correctly identified as not revoked")
    else:
        print(f"❌ Different token incorrectly marked as revoked")
        return False

    print("✓ Individual token revocation test passed!")
    return True


def test_user_level_revocation():
    """Test revoking all tokens for a user"""
    print("\n=== Testing User-Level Revocation ===")

    revocation_service = get_revocation_service()

    # Test user data
    user_id = "test-user-789"

    # Revoke all user tokens
    success = revocation_service.revoke_all_user_tokens(user_id)
    if success:
        print(f"✓ All tokens revoked for user: {user_id}")
    else:
        print(f"❌ Failed to revoke user tokens")
        return False

    # Check that old tokens are revoked
    old_token_issued_at = datetime.now(timezone.utc) - timedelta(hours=2)
    is_old_revoked = revocation_service.is_token_revoked_for_user(user_id, old_token_issued_at)
    if is_old_revoked:
        print(f"✓ Old token correctly identified as revoked")
    else:
        print(f"❌ Old token not revoked")
        return False

    # Check that new tokens are not revoked
    new_token_issued_at = datetime.now(timezone.utc) + timedelta(seconds=10)
    is_new_revoked = revocation_service.is_token_revoked_for_user(user_id, new_token_issued_at)
    if not is_new_revoked:
        print(f"✓ New token correctly identified as not revoked")
    else:
        print(f"❌ New token incorrectly marked as revoked")
        return False

    # Clean up
    revocation_service.clear_user_revocation(user_id)
    print(f"✓ User revocation cleared")

    print("✓ User-level revocation test passed!")
    return True


def test_jwt_integration():
    """Test token revocation with actual JWT tokens"""
    print("\n=== Testing JWT Integration ===")

    auth_manager = get_auth_manager()
    revocation_service = get_revocation_service()

    # Create a test token
    import uuid

    test_user_id = "integration-test-user"
    test_email = f"test-{uuid.uuid4()}@example.com"

    token = auth_manager.create_access_token(
        user_id=test_user_id, email=test_email, role="user", expires_delta=timedelta(hours=1)
    )
    print(f"✓ Created test token")

    # Verify token works
    payload = auth_manager.verify_token(token)
    if payload and payload.get("sub") == test_user_id:
        print(f"✓ Token verified successfully")
    else:
        print(f"❌ Token verification failed")
        return False

    # Extract JTI and expiration
    jti = payload.get("jti")
    exp = payload.get("exp")

    if not jti:
        print(f"❌ Token missing JTI claim")
        return False

    print(f"✓ Token has JTI: {jti}")

    # Revoke the token
    expires_at = datetime.fromtimestamp(exp)
    success = revocation_service.revoke_token(jti, expires_at)

    if not success:
        print(f"❌ Failed to revoke token")
        return False

    print(f"✓ Token revoked in Redis")

    # Try to verify revoked token (should fail)
    # Note: This requires the JWT authentication to check revocation
    # which is implemented in jwt_auth.py
    from app.auth.jwt_auth import get_jwt_auth_manager

    jwt_auth = get_jwt_auth_manager()
    revoked_payload = jwt_auth.verify_token(token)

    if revoked_payload is None:
        print(f"✓ Revoked token correctly rejected")
    else:
        print(f"❌ Revoked token still accepted")
        return False

    print("✓ JWT integration test passed!")
    return True


def test_expiration_handling():
    """Test handling of expired tokens"""
    print("\n=== Testing Expiration Handling ===")

    revocation_service = get_revocation_service()

    # Try to revoke an already expired token
    jti = "expired-token-123"
    expires_at = datetime.now(timezone.utc) - timedelta(hours=1)  # Already expired

    success = revocation_service.revoke_token(jti, expires_at)
    if not success:
        print(f"✓ Expired token revocation correctly rejected")
    else:
        print(f"❌ Expired token should not be added to revocation list")
        return False

    print("✓ Expiration handling test passed!")
    return True


def run_all_tests():
    """Run all token revocation tests"""
    print("\n" + "=" * 60)
    print("TOKEN REVOCATION TEST SUITE")
    print("=" * 60)

    tests = [
        test_individual_token_revocation,
        test_user_level_revocation,
        test_expiration_handling,
        test_jwt_integration,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            result = test()
            if result:
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            import traceback

            traceback.print_exc()
            failed += 1

    print("\n" + "=" * 60)
    print(f"TEST RESULTS: {passed} passed, {failed} failed")
    print("=" * 60)

    if failed == 0:
        print("✅ All tests passed!")
        return 0
    else:
        print(f"❌ {failed} test(s) failed")
        return 1


if __name__ == "__main__":
    import sys

    exit_code = run_all_tests()
    sys.exit(exit_code)
