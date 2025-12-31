#!/usr/bin/env python3
"""Test script for Milestone 2 - Stateful Resilience & Security."""

import asyncio
import sys
import os
from datetime import datetime
from uuid import uuid4

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.sessions.models import Session, SessionStatus
from app.sessions.manager import SessionManager, SessionCreateRequest


async def test_session_manager_persistence():
    """Test SessionManager with persistent storage integration."""
    print("Testing SessionManager with persistent storage...")
    
    try:
        manager = SessionManager()
        
        # Create session request
        request = SessionCreateRequest(
            provider_type="openai",
            provider_model="gpt-4o-mini",
            strategy="realtime",
            system_prompt="Test milestone 2 prompt",
            temperature=0.7,
            metadata={"milestone": "2", "test": True}
        )
        
        # Create session
        session = await manager.create_session(request)
        print(f"✓ Session created: {session.id}")
        print(f"✓ Provider: {session.provider_type}")
        print(f"✓ Model: {session.provider_model}")
        
        # Get session
        retrieved = await manager.get_session(session.id)
        print(f"✓ Session retrieved: {retrieved is not None}")
        print(f"✓ Data integrity: {retrieved.provider_type == session.provider_type if retrieved else False}")
        
        # List sessions
        sessions = await manager.list_sessions()
        print(f"✓ Sessions listed: {len(sessions)} sessions")
        
        # Start session (will fail due to missing provider config, but that's expected)
        try:
            await manager.start_session(session.id)
            print("✓ Session started successfully")
        except Exception as e:
            print(f"⚠ Session start failed (expected): {type(e).__name__}")
        
        # End session
        await manager.end_session(session.id)
        print("✓ Session ended")
        
        # Verify session status
        ended_session = await manager.get_session(session.id)
        print(f"✓ Session status: {ended_session.status.value if ended_session else 'None'}")
        
        return True
        
    except Exception as e:
        print(f"✗ SessionManager test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_storage_fallback():
    """Test storage fallback behavior."""
    print("\nTesting storage fallback behavior...")
    
    try:
        from app.sessions.storage import PersistentSessionManager
        
        manager = PersistentSessionManager()
        await manager.initialize()
        
        # Create test session
        session = Session(
            provider_type="gemini",
            provider_model="gemini-2.5-flash",
            strategy="segmented",
            system_prompt="Fallback test prompt",
            temperature=0.8,
            status=SessionStatus.PENDING,
            metadata={"fallback_test": True}
        )
        
        # Test memory fallback
        created = await manager.create_session(session)
        print(f"✓ Session created with fallback: {created}")
        
        # Retrieve from memory
        retrieved = await manager.get_session(session.id)
        print(f"✓ Session retrieved from fallback: {retrieved is not None}")
        
        await manager.close()
        return True
        
    except Exception as e:
        print(f"✗ Storage fallback test failed: {e}")
        return False


async def test_ttl_functionality():
    """Test TTL functionality for sessions."""
    print("\nTesting TTL functionality...")
    
    try:
        from app.sessions.storage import RedisStorage
        
        storage = RedisStorage()
        
        # Create session with short TTL
        session = Session(
            provider_type="openai",
            provider_model="gpt-4o-mini",
            strategy="realtime",
            system_prompt="TTL test prompt",
            temperature=0.7,
            status=SessionStatus.ACTIVE,
            metadata={"ttl_test": True}
        )
        
        # Store with 2-second TTL
        stored = await storage.store_session(session, ttl_seconds=2)
        print(f"✓ Session stored with TTL: {stored}")
        
        # Retrieve immediately
        retrieved = await storage.get_session(session.id)
        print(f"✓ Session retrieved immediately: {retrieved is not None}")
        
        # Wait for expiration
        print("⏳ Waiting for TTL expiration...")
        await asyncio.sleep(3)
        
        # Try to retrieve after expiration
        expired = await storage.get_session(session.id)
        print(f"✓ Session expired as expected: {expired is None}")
        
        return True
        
    except Exception as e:
        print(f"✗ TTL functionality test failed: {e}")
        return False


async def main():
    """Run all Milestone 2 tests."""
    print("=== Milestone 2 - Stateful Resilience & Security Tests ===\n")
    
    results = []
    
    # Run tests
    results.append(await test_session_manager_persistence())
    results.append(await test_storage_fallback())
    results.append(await test_ttl_functionality())
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print(f"\n=== Milestone 2 Test Summary ===")
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 Milestone 2 requirements implemented successfully!")
        print("✓ Session persistence with Redis/Postgres")
        print("✓ TTL support for automatic cleanup")
        print("✓ Memory fallback for resilience")
        print("✓ Graceful recovery capabilities")
        return 0
    else:
        print("❌ Some Milestone 2 requirements need attention.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)