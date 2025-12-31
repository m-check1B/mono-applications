#!/usr/bin/env python3
"""Test script for persistent storage functionality."""

import asyncio
import sys
import os
from datetime import datetime, timezone
from uuid import uuid4

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.sessions.models import Session, SessionStatus
from app.sessions.storage import RedisStorage, PersistentSessionManager


async def test_redis_storage():
    """Test Redis storage functionality."""
    print("Testing Redis storage...")
    
    try:
        storage = RedisStorage()
        await storage.get_redis()  # Test connection
        print("✓ Redis connection successful")
        
        # Create test session
        session = Session(
            provider_type="openai",
            provider_model="gpt-4o-mini",
            strategy="realtime",
            system_prompt="Test prompt",
            temperature=0.7,
            status=SessionStatus.ACTIVE,
            metadata={"test": True}
        )
        
        # Store session
        success = await storage.store_session(session, ttl_seconds=60)
        print(f"✓ Session storage: {success}")
        
        # Retrieve session
        retrieved = await storage.get_session(session.id)
        print(f"✓ Session retrieval: {retrieved is not None}")
        print(f"✓ Session ID match: {retrieved.id == session.id if retrieved else False}")
        
        # List sessions
        sessions = await storage.list_sessions()
        print(f"✓ Session listing: {len(sessions)} sessions")
        
        # Delete session
        deleted = await storage.delete_session(session.id)
        print(f"✓ Session deletion: {deleted}")
        
        return True
        
    except Exception as e:
        print(f"✗ Redis storage test failed: {e}")
        return False


async def test_persistent_manager():
    """Test PersistentSessionManager functionality."""
    print("\nTesting PersistentSessionManager...")
    
    try:
        manager = PersistentSessionManager()
        await manager.initialize()
        print("✓ PersistentSessionManager initialization successful")
        
        # Create test session
        session = Session(
            provider_type="gemini",
            provider_model="gemini-2.5-flash",
            strategy="segmented",
            system_prompt="Test manager prompt",
            temperature=0.8,
            status=SessionStatus.PENDING,
            metadata={"manager_test": True}
        )
        
        # Create session
        created = await manager.create_session(session, ttl_seconds=60)
        print(f"✓ Session creation: {created}")
        
        # Get session
        retrieved = await manager.get_session(session.id)
        print(f"✓ Session retrieval: {retrieved is not None}")
        print(f"✓ Session data match: {retrieved.provider_type == session.provider_type if retrieved else False}")
        
        # Update session
        session.status = SessionStatus.ACTIVE
        session.updated_at = datetime.now(timezone.utc)
        updated = await manager.update_session(session, ttl_seconds=60)
        print(f"✓ Session update: {updated}")
        
        # List sessions
        sessions = await manager.list_sessions()
        print(f"✓ Session listing: {len(sessions)} sessions")
        
        # Delete session
        deleted = await manager.delete_session(session.id)
        print(f"✓ Session deletion: {deleted}")
        
        await manager.close()
        return True
        
    except Exception as e:
        print(f"✗ PersistentSessionManager test failed: {e}")
        return False


async def test_call_mapping():
    """Test call mapping functionality."""
    print("\nTesting call mapping...")
    
    try:
        storage = RedisStorage()
        session_id = uuid4()
        call_sid = "test_call_123"
        
        # Store call map
        success = await storage.store_call_map(call_sid, session_id, ttl_seconds=60)
        print(f"✓ Call map storage: {success}")
        
        # Get session by call
        retrieved_id = await storage.get_session_by_call(call_sid)
        print(f"✓ Session retrieval by call: {retrieved_id == session_id}")
        
        # Delete call map
        deleted = await storage.delete_call_map(call_sid)
        print(f"✓ Call map deletion: {deleted}")
        
        return True
        
    except Exception as e:
        print(f"✗ Call mapping test failed: {e}")
        return False


async def test_transcript_storage():
    """Test transcript storage functionality."""
    print("\nTesting transcript storage...")
    
    try:
        storage = RedisStorage()
        session_id = uuid4()
        
        # Store transcript entries
        for i in range(3):
            success = await storage.store_transcript(
                session_id=session_id,
                sequence_number=i,
                speaker="user" if i % 2 == 0 else "assistant",
                content=f"Test message {i}",
                confidence=0.95,
                ttl_seconds=60
            )
            print(f"✓ Transcript {i} storage: {success}")
        
        # Get transcripts
        transcripts = await storage.get_transcripts(session_id)
        print(f"✓ Transcript retrieval: {len(transcripts)} entries")
        print(f"✓ Transcript ordering: {all(t.sequence_number == i for i, t in enumerate(transcripts))}")
        
        return True
        
    except Exception as e:
        print(f"✗ Transcript storage test failed: {e}")
        return False


async def main():
    """Run all tests."""
    print("=== Persistent Storage Tests ===\n")
    
    results = []
    
    # Run tests
    results.append(await test_redis_storage())
    results.append(await test_persistent_manager())
    results.append(await test_call_mapping())
    results.append(await test_transcript_storage())
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print(f"\n=== Test Summary ===")
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! Persistent storage is working correctly.")
        return 0
    else:
        print("❌ Some tests failed. Check Redis configuration and dependencies.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)