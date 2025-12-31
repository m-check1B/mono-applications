
import pytest
import asyncio
from app.services.context_sharing import context_sharing_service, ChannelType, ContextEventType, ContextEvent
from app.services.authenticated_ai_service import get_authenticated_ai_service, User, UserRole

@pytest.mark.asyncio
async def test_context_sharing_singleton():
    """Test that context_sharing_service is indeed shared."""
    auth_service = get_authenticated_ai_service()
    
    # Both should point to the same global instance
    assert auth_service.context_sharing is context_sharing_service

@pytest.mark.asyncio
async def test_share_context_method():
    """Test the newly added share_context method."""
    auth_service = get_authenticated_ai_service()
    user = User(id="user_1", username="test", role=UserRole.ADMIN, company_id="comp_1")
    
    context_data = {
        "session_id": "test_session_123",
        "customer_info": {"name": "John Doe", "email": "john@example.com"}
    }
    
    result = await auth_service.share_context(user, context_data, target_users=["user_2"])
    
    assert result["status"] == "success"
    assert result["session_id"] == "test_session_123"
    
    # Verify it's in the service
    context = context_sharing_service.get_context("test_session_123")
    assert context is not None
    assert context.customer_info["name"] == "John Doe"
    
    # Verify event was added
    assert len(context.events) > 0
    last_event = context.events[-1]
    assert last_event.event_type == ContextEventType.CUSTOMER_INFO_UPDATED
    assert last_event.data["shared_with"] == ["user_2"]

@pytest.mark.asyncio
async def test_channel_linking():
    """Test channel linking in context sharing service."""
    session_id = "shared_123"
    browser_cid = "browser_456"
    voice_cid = "voice_789"
    
    # 1. Create browser context
    context_sharing_service.create_shared_context(
        session_id=session_id,
        channel=ChannelType.BROWSER,
        channel_session_id=browser_cid,
        customer_info={"initial": "data"}
    )
    
    # 2. Link voice channel
    context_sharing_service.link_channels(
        shared_session_id=session_id,
        channel=ChannelType.VOICE,
        channel_session_id=voice_cid
    )
    
    # 3. Retrieve by voice channel ID
    context = context_sharing_service.get_context_by_channel(voice_cid)
    assert context is not None
    assert context.session_id == session_id
    assert context.browser_session_id == browser_cid
    assert context.voice_session_id == voice_cid
    assert context.customer_info["initial"] == "data"
