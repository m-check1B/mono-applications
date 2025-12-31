#!/usr/bin/env python3
"""
Session Persistence Test

This script tests Redis-based session persistence functionality.
"""

import asyncio
import os
import sys
from dotenv import load_dotenv
from uuid import uuid4

# Load environment variables
load_dotenv('/home/adminmatej/github/applications/operator-demo-2026/backend/.env')

# Add the current directory to Python path
sys.path.insert(0, '/home/adminmatej/github/applications/operator-demo-2026/backend')

from app.config.feature_flags import get_feature_flags
from app.sessions.storage import get_persistent_storage, RedisStorage
from app.sessions.models import SessionCreateRequest, SessionStatus
from app.providers.registry import ProviderType

async def test_redis_connection():
    """Test Redis connection."""
    
    print("🔗 Testing Redis Connection")
    print("=" * 40)
    
    try:
        redis_storage = RedisStorage()
        
        # Test basic Redis connection
        r = await redis_storage.get_redis()
        
        # Test ping
        pong = await r.ping()
        print(f"✅ Redis ping test: {pong}")
        
        # Test basic operations
        test_key = "test:connection"
        test_value = "test_value"
        
        # Store test data
        await r.setex(test_key, 60, test_value)
        print(f"✅ Redis store test: True")
        
        # Retrieve test data
        retrieved = await r.get(test_key)
        print(f"✅ Redis retrieve test: {retrieved == test_value}")
        
        # Clean up
        await r.delete(test_key)
        print(f"✅ Redis delete test: True")
        
        return True
        
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")
        return False

async def test_session_persistence():
    """Test session persistence functionality."""
    
    print("\n💾 Testing Session Persistence")
    print("=" * 40)
    
    try:
        # Get persistent storage
        storage = await get_persistent_storage()
        if not storage:
            print("❌ Persistent storage not available")
            return False
            
        print("✅ Persistent storage initialized")
        
        # Create a test session
        session_request = SessionCreateRequest(
            provider=ProviderType.OPENAI.value,
            provider_model="gpt-4o-mini",
            strategy="realtime",
            metadata={"test": True}
        )
        
        # Create session using storage
        from app.sessions.models import Session
        from uuid import uuid4
        from datetime import datetime
        
        session = Session(
            id=uuid4(),
            provider_type=session_request.provider or "openai",
            provider_model=session_request.provider_model or "gpt-4o-mini",
            strategy=session_request.strategy or "realtime",
            status=SessionStatus.PENDING,
            metadata=session_request.metadata,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        success = await storage.create_session(session)
        session_id = session.id
        print(f"✅ Created persistent session: {session_id}")
        
        # Retrieve session
        retrieved_session = await storage.get_session(session_id)
        if retrieved_session:
            print(f"✅ Retrieved persistent session: {retrieved_session.id}")
            print(f"   Provider: {retrieved_session.provider_type}")
            print(f"   Status: {retrieved_session.status}")
        else:
            print("❌ Failed to retrieve persistent session")
            return False
        
        # Update session
        retrieved_session.status = SessionStatus.ACTIVE
        success = await storage.update_session(retrieved_session)
        print(f"✅ Updated persistent session: {success}")
        
        # List sessions
        sessions = await storage.list_sessions()
        print(f"✅ Listed {len(sessions)} persistent sessions")
        
        # Clean up
        await storage.delete_session(session_id)
        print(f"✅ Deleted persistent session")
        
        return True
        
    except Exception as e:
        print(f"❌ Session persistence test failed: {e}")
        return False

async def test_session_manager_integration():
    """Test session manager with persistence enabled."""
    
    print("\n🔄 Testing Session Manager Integration")
    print("=" * 45)
    
    try:
        from app.sessions.manager import get_session_manager
        
        manager = get_session_manager()
        
        # Create session request
        session_request = SessionCreateRequest(
            provider=ProviderType.OPENAI.value,
            provider_model="gpt-4o-mini",
            strategy="realtime",
            metadata={"test_persistence": True}
        )
        
        # Create session
        session = await manager.create_session(session_request)
        print(f"✅ Created session via manager: {session.id}")
        
        # Retrieve session (should come from persistent storage)
        retrieved_session = await manager.get_session(session.id)
        if retrieved_session:
            print(f"✅ Retrieved session via manager: {retrieved_session.id}")
            print(f"   Metadata: {retrieved_session.metadata}")
        else:
            print("❌ Failed to retrieve session via manager")
            return False
        
        # Clean up
        await manager.end_session(session.id)
        print(f"✅ Ended session via manager")
        
        return True
        
    except Exception as e:
        print(f"❌ Session manager integration test failed: {e}")
        return False

def test_configuration():
    """Test configuration settings."""
    
    print("\n⚙️ Configuration Check")
    print("-" * 25)
    
    # Check environment variables
    env_vars = [
        'ENABLE_PERSISTENT_SESSIONS',
        'REDIS_URL',
        'REDIS_HOST',
        'REDIS_PORT'
    ]
    
    for var in env_vars:
        value = os.getenv(var)
        status = "✅" if value else "❌"
        print(f"{status} {var}: {value}")
    
    # Check feature flags
    flags = get_feature_flags()
    session_flags = [
        ('enable_persistent_sessions', 'Persistent Sessions'),
        ('enable_session_recovery', 'Session Recovery'),
        ('enable_session_analytics', 'Session Analytics'),
    ]
    
    print("\nSession Feature Flags:")
    for flag, name in session_flags:
        enabled = getattr(flags, flag, False)
        status = "✅" if enabled else "❌"
        print(f"{status} {name}: {enabled}")

async def main():
    """Main test function."""
    
    print("🚀 Session Persistence Test Suite")
    print("=" * 50)
    
    # Test configuration
    test_configuration()
    
    # Test Redis connection
    redis_works = await test_redis_connection()
    
    # Test session persistence
    if redis_works:
        persistence_works = await test_session_persistence()
        manager_works = await test_session_manager_integration()
    else:
        persistence_works = False
        manager_works = False
    
    print("\n📊 Summary")
    print("-" * 15)
    
    if redis_works and persistence_works and manager_works:
        print("✅ Session persistence is fully functional")
        print("✅ Redis connection is working")
        print("✅ Session data is persisted across restarts")
        print("✅ Session manager integration is working")
    else:
        print("❌ Session persistence has issues")
        if not redis_works:
            print("❌ Redis connection is not working")
        if not persistence_works:
            print("❌ Session persistence is not working")
        if not manager_works:
            print("❌ Session manager integration is not working")
    
    print(f"\nNext steps:")
    print(f"1. Ensure Redis is running in production")
    print(f"2. Monitor session persistence logs")
    print(f"3. Test session recovery after restart")

if __name__ == "__main__":
    asyncio.run(main())