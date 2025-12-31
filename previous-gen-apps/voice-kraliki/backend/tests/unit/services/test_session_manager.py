"""
Comprehensive Unit Tests for Session Manager

Tests cover:
- Session creation and initialization
- Session lifecycle management (start, end)
- Session cleanup on completion
- Concurrent session handling
- Session state persistence
- Session retrieval and updates
- Provider instantiation
- Model resolution
- Error handling
"""

import pytest
from datetime import datetime, timezone
from unittest.mock import Mock, MagicMock, patch, AsyncMock
from uuid import UUID, uuid4

from app.sessions.manager import SessionManager, get_session_manager
from app.sessions.models import Session, SessionCreateRequest, SessionStatus
from app.providers.registry import ProviderType, TelephonyType


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def session_manager():
    """Create a fresh session manager instance."""
    manager = SessionManager()
    manager._sessions = {}
    manager._providers = {}
    return manager


@pytest.fixture
def mock_provider_registry():
    """Create a mock provider registry."""
    mock_registry = Mock()

    # Mock provider info
    mock_provider_info = Mock()
    mock_provider_info.available_models = ["gemini-2.5-flash", "gemini-2.0-flash"]
    mock_provider_info.is_configured = True

    mock_registry.get_provider_info = Mock(return_value=mock_provider_info)
    mock_registry.create_provider = Mock(return_value=Mock())

    # Mock telephony info
    mock_telephony_info = Mock()
    mock_telephony_info.id = "twilio"
    mock_telephony_info.is_configured = True
    mock_telephony_info.is_primary = True

    mock_registry.get_telephony_info = Mock(return_value=mock_telephony_info)
    mock_registry.list_telephony_adapters = Mock(return_value=[mock_telephony_info])

    return mock_registry


@pytest.fixture
def basic_session_request():
    """Create a basic session creation request."""
    return SessionCreateRequest(
        provider_type="gemini",
        system_prompt="You are a helpful assistant.",
        temperature=0.7
    )


@pytest.fixture
def mock_provider():
    """Create a mock provider instance."""
    provider = Mock()
    provider.connect = AsyncMock()
    provider.disconnect = AsyncMock()
    return provider


# ============================================================================
# 1. SESSION CREATION TESTS
# ============================================================================

@pytest.mark.unit
class TestSessionCreation:
    """Test session creation and initialization."""

    @pytest.mark.asyncio
    async def test_create_session_returns_session_object(self, session_manager, basic_session_request, mock_provider_registry):
        """Test that creating a session returns a Session object."""
        with patch.object(session_manager, 'registry', mock_provider_registry):
            session = await session_manager.create_session(basic_session_request)

        assert isinstance(session, Session)
        assert session.id is not None
        assert isinstance(session.id, UUID)

    @pytest.mark.asyncio
    async def test_create_session_sets_pending_status(self, session_manager, basic_session_request, mock_provider_registry):
        """Test that new sessions are created with PENDING status."""
        with patch.object(session_manager, 'registry', mock_provider_registry):
            session = await session_manager.create_session(basic_session_request)

        assert session.status == SessionStatus.PENDING

    @pytest.mark.asyncio
    async def test_create_session_sets_provider_type(self, session_manager, basic_session_request, mock_provider_registry):
        """Test that session has correct provider type."""
        with patch.object(session_manager, 'registry', mock_provider_registry):
            session = await session_manager.create_session(basic_session_request)

        assert session.provider_type == "gemini"

    @pytest.mark.asyncio
    async def test_create_session_sets_timestamps(self, session_manager, basic_session_request, mock_provider_registry):
        """Test that session has created and updated timestamps."""
        before_create = datetime.now(timezone.utc)

        with patch.object(session_manager, 'registry', mock_provider_registry):
            session = await session_manager.create_session(basic_session_request)

        after_create = datetime.now(timezone.utc)

        assert session.created_at is not None
        assert session.updated_at is not None
        assert before_create <= session.created_at <= after_create
        assert before_create <= session.updated_at <= after_create

    @pytest.mark.asyncio
    async def test_create_session_caches_in_memory(self, session_manager, basic_session_request, mock_provider_registry):
        """Test that created session is cached in memory."""
        with patch.object(session_manager, 'registry', mock_provider_registry):
            session = await session_manager.create_session(basic_session_request)

        assert session.id in session_manager._sessions
        assert session_manager._sessions[session.id] == session

    @pytest.mark.asyncio
    async def test_create_session_resolves_model(self, session_manager, mock_provider_registry):
        """Test that session creation resolves provider model."""
        request = SessionCreateRequest(
            provider_type="gemini",
            provider_model="gemini-2.5-flash"
        )

        with patch.object(session_manager, 'registry', mock_provider_registry):
            session = await session_manager.create_session(request)

        assert session.provider_model == "gemini-2.5-flash"

    @pytest.mark.asyncio
    async def test_create_session_with_metadata(self, session_manager, mock_provider_registry):
        """Test session creation with custom metadata."""
        request = SessionCreateRequest(
            provider_type="gemini",
            metadata={"custom_field": "custom_value"}
        )

        with patch.object(session_manager, 'registry', mock_provider_registry):
            session = await session_manager.create_session(request)

        assert session.metadata is not None
        assert "custom_field" in session.metadata
        assert session.metadata["custom_field"] == "custom_value"

    @pytest.mark.asyncio
    async def test_create_session_invalid_provider_raises_error(self, session_manager):
        """Test that invalid provider type raises ValueError."""
        request = SessionCreateRequest(
            provider_type="invalid_provider"
        )

        with pytest.raises(ValueError, match="Unsupported provider"):
            await session_manager.create_session(request)


# ============================================================================
# 2. SESSION LIFECYCLE TESTS
# ============================================================================

@pytest.mark.unit
class TestSessionLifecycle:
    """Test session lifecycle management."""

    @pytest.mark.asyncio
    async def test_start_session_changes_status_to_active(self, session_manager, basic_session_request, mock_provider_registry, mock_provider):
        """Test that starting a session changes status to ACTIVE."""
        with patch.object(session_manager, 'registry', mock_provider_registry):
            with patch.object(session_manager, '_create_provider', return_value=mock_provider):
                session = await session_manager.create_session(basic_session_request)
                await session_manager.start_session(session.id)

        assert session.status == SessionStatus.ACTIVE

    @pytest.mark.asyncio
    async def test_start_session_connects_provider(self, session_manager, basic_session_request, mock_provider_registry, mock_provider):
        """Test that starting a session connects the provider."""
        with patch.object(session_manager, 'registry', mock_provider_registry):
            with patch.object(session_manager, '_create_provider', return_value=mock_provider):
                session = await session_manager.create_session(basic_session_request)
                await session_manager.start_session(session.id)

        mock_provider.connect.assert_called_once()

    @pytest.mark.asyncio
    async def test_start_session_stores_provider_instance(self, session_manager, basic_session_request, mock_provider_registry, mock_provider):
        """Test that starting a session stores provider instance."""
        with patch.object(session_manager, 'registry', mock_provider_registry):
            with patch.object(session_manager, '_create_provider', return_value=mock_provider):
                session = await session_manager.create_session(basic_session_request)
                await session_manager.start_session(session.id)

        assert session.id in session_manager._providers
        assert session_manager._providers[session.id] == mock_provider

    @pytest.mark.asyncio
    async def test_start_nonexistent_session_raises_error(self, session_manager):
        """Test that starting non-existent session raises ValueError."""
        fake_session_id = uuid4()

        with pytest.raises(ValueError, match="not found"):
            await session_manager.start_session(fake_session_id)

    @pytest.mark.asyncio
    async def test_end_session_changes_status_to_completed(self, session_manager, basic_session_request, mock_provider_registry, mock_provider):
        """Test that ending a session changes status to COMPLETED."""
        with patch.object(session_manager, 'registry', mock_provider_registry):
            with patch.object(session_manager, '_create_provider', return_value=mock_provider):
                session = await session_manager.create_session(basic_session_request)
                await session_manager.start_session(session.id)
                await session_manager.end_session(session.id)

        assert session.status == SessionStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_end_session_disconnects_provider(self, session_manager, basic_session_request, mock_provider_registry, mock_provider):
        """Test that ending a session disconnects the provider."""
        with patch.object(session_manager, 'registry', mock_provider_registry):
            with patch.object(session_manager, '_create_provider', return_value=mock_provider):
                session = await session_manager.create_session(basic_session_request)
                await session_manager.start_session(session.id)
                await session_manager.end_session(session.id)

        mock_provider.disconnect.assert_called_once()

    @pytest.mark.asyncio
    async def test_end_session_removes_provider_instance(self, session_manager, basic_session_request, mock_provider_registry, mock_provider):
        """Test that ending a session removes provider instance."""
        with patch.object(session_manager, 'registry', mock_provider_registry):
            with patch.object(session_manager, '_create_provider', return_value=mock_provider):
                session = await session_manager.create_session(basic_session_request)
                await session_manager.start_session(session.id)
                await session_manager.end_session(session.id)

        assert session.id not in session_manager._providers

    @pytest.mark.asyncio
    async def test_end_session_sets_ended_timestamp(self, session_manager, basic_session_request, mock_provider_registry, mock_provider):
        """Test that ending a session sets ended_at timestamp."""
        with patch.object(session_manager, 'registry', mock_provider_registry):
            with patch.object(session_manager, '_create_provider', return_value=mock_provider):
                session = await session_manager.create_session(basic_session_request)
                await session_manager.start_session(session.id)

                before_end = datetime.now(timezone.utc)
                await session_manager.end_session(session.id)
                after_end = datetime.now(timezone.utc)

        assert session.ended_at is not None
        assert before_end <= session.ended_at <= after_end

    @pytest.mark.asyncio
    async def test_end_nonexistent_session_handled_gracefully(self, session_manager):
        """Test that ending non-existent session is handled gracefully."""
        fake_session_id = uuid4()

        # Should not raise an exception
        await session_manager.end_session(fake_session_id)


# ============================================================================
# 3. SESSION RETRIEVAL TESTS
# ============================================================================

@pytest.mark.unit
class TestSessionRetrieval:
    """Test session retrieval operations."""

    @pytest.mark.asyncio
    async def test_get_session_returns_session(self, session_manager, basic_session_request, mock_provider_registry):
        """Test that get_session returns the correct session."""
        with patch.object(session_manager, 'registry', mock_provider_registry):
            session = await session_manager.create_session(basic_session_request)

        retrieved = await session_manager.get_session(session.id)

        assert retrieved is not None
        assert retrieved.id == session.id

    @pytest.mark.asyncio
    async def test_get_session_returns_none_for_nonexistent(self, session_manager):
        """Test that get_session returns None for non-existent session."""
        fake_id = uuid4()

        result = await session_manager.get_session(fake_id)

        assert result is None

    def test_get_provider_returns_provider_instance(self, session_manager, mock_provider):
        """Test that get_provider returns provider instance."""
        session_id = uuid4()
        session_manager._providers[session_id] = mock_provider

        provider = session_manager.get_provider(session_id)

        assert provider == mock_provider

    def test_get_provider_returns_none_for_nonexistent(self, session_manager):
        """Test that get_provider returns None for non-existent session."""
        fake_id = uuid4()

        provider = session_manager.get_provider(fake_id)

        assert provider is None

    @pytest.mark.asyncio
    async def test_list_sessions_returns_all_sessions(self, session_manager, mock_provider_registry):
        """Test that list_sessions returns all sessions."""
        with patch.object(session_manager, 'registry', mock_provider_registry):
            request1 = SessionCreateRequest(provider_type="gemini")
            request2 = SessionCreateRequest(provider_type="openai")

            await session_manager.create_session(request1)
            await session_manager.create_session(request2)

        sessions = await session_manager.list_sessions()

        assert len(sessions) >= 2

    @pytest.mark.asyncio
    async def test_list_sessions_filters_by_status(self, session_manager, basic_session_request, mock_provider_registry, mock_provider):
        """Test that list_sessions filters by status."""
        with patch.object(session_manager, 'registry', mock_provider_registry):
            with patch.object(session_manager, '_create_provider', return_value=mock_provider):
                # Create pending session
                pending_session = await session_manager.create_session(basic_session_request)

                # Create and start active session
                active_request = SessionCreateRequest(provider_type="openai")
                active_session = await session_manager.create_session(active_request)
                await session_manager.start_session(active_session.id)

        pending_sessions = await session_manager.list_sessions(status=SessionStatus.PENDING)
        active_sessions = await session_manager.list_sessions(status=SessionStatus.ACTIVE)

        # Check that filtering works
        assert any(s.id == pending_session.id for s in pending_sessions)
        assert any(s.id == active_session.id for s in active_sessions)


# ============================================================================
# 4. PROVIDER INSTANTIATION TESTS
# ============================================================================

@pytest.mark.unit
class TestProviderInstantiation:
    """Test provider creation and configuration."""

    def test_create_provider_instantiates_correct_type(self, session_manager, mock_provider_registry):
        """Test that _create_provider instantiates correct provider type."""
        session = Session(
            provider_type="gemini",
            provider_model="gemini-2.5-flash"
        )

        with patch.object(session_manager, 'registry', mock_provider_registry):
            provider = session_manager._create_provider(session)

        mock_provider_registry.create_provider.assert_called_once()

    def test_create_provider_invalid_type_raises_error(self, session_manager):
        """Test that invalid provider type raises ValueError."""
        session = Session(
            provider_type="invalid_provider",
            provider_model="some-model"
        )

        with pytest.raises(ValueError, match="Unsupported provider type"):
            session_manager._create_provider(session)


# ============================================================================
# 5. MODEL RESOLUTION TESTS
# ============================================================================

@pytest.mark.unit
class TestModelResolution:
    """Test model resolution logic."""

    @pytest.mark.asyncio
    async def test_resolve_model_uses_preferred_when_available(self, session_manager, mock_provider_registry):
        """Test that preferred model is used when available."""
        request = SessionCreateRequest(
            provider_type="gemini",
            provider_model="gemini-2.5-flash"
        )

        with patch.object(session_manager, 'registry', mock_provider_registry):
            session = await session_manager.create_session(request)

        assert session.provider_model == "gemini-2.5-flash"

    @pytest.mark.asyncio
    async def test_resolve_model_falls_back_to_default(self, session_manager, mock_provider_registry):
        """Test that model falls back to default when not specified."""
        request = SessionCreateRequest(
            provider_type="gemini"
        )

        with patch.object(session_manager, 'registry', mock_provider_registry):
            session = await session_manager.create_session(request)

        # Should use first available model
        assert session.provider_model in mock_provider_registry.get_provider_info().available_models

    @pytest.mark.asyncio
    async def test_resolve_model_premium_selection(self, session_manager, mock_provider_registry):
        """Test that premium flag selects non-mini model."""
        mock_provider_info = mock_provider_registry.get_provider_info()
        mock_provider_info.available_models = ["gemini-2.0-flash-mini", "gemini-2.5-flash"]

        request = SessionCreateRequest(
            provider_type="gemini",
            use_premium=True
        )

        with patch.object(session_manager, 'registry', mock_provider_registry):
            session = await session_manager.create_session(request)

        # Should select non-mini model
        assert "mini" not in session.provider_model


# ============================================================================
# 6. ERROR HANDLING TESTS
# ============================================================================

@pytest.mark.unit
class TestErrorHandling:
    """Test error handling in session management."""

    @pytest.mark.asyncio
    async def test_start_session_connection_error_sets_error_status(self, session_manager, basic_session_request, mock_provider_registry):
        """Test that connection error sets session status to ERROR."""
        mock_provider = Mock()
        mock_provider.connect = AsyncMock(side_effect=ConnectionError("Connection failed"))

        with patch.object(session_manager, 'registry', mock_provider_registry):
            with patch.object(session_manager, '_create_provider', return_value=mock_provider):
                session = await session_manager.create_session(basic_session_request)

                with pytest.raises(ConnectionError):
                    await session_manager.start_session(session.id)

        assert session.status == SessionStatus.ERROR

    @pytest.mark.asyncio
    async def test_end_session_disconnect_error_handled_gracefully(self, session_manager, basic_session_request, mock_provider_registry):
        """Test that disconnect error during end_session is handled gracefully."""
        mock_provider = Mock()
        mock_provider.connect = AsyncMock()
        mock_provider.disconnect = AsyncMock(side_effect=Exception("Disconnect failed"))

        with patch.object(session_manager, 'registry', mock_provider_registry):
            with patch.object(session_manager, '_create_provider', return_value=mock_provider):
                session = await session_manager.create_session(basic_session_request)
                await session_manager.start_session(session.id)

                # Should not raise exception
                await session_manager.end_session(session.id)

        # Provider should still be removed
        assert session.id not in session_manager._providers


# ============================================================================
# 7. CONCURRENT SESSION TESTS
# ============================================================================

@pytest.mark.unit
class TestConcurrentSessions:
    """Test concurrent session handling."""

    @pytest.mark.asyncio
    async def test_multiple_concurrent_sessions(self, session_manager, mock_provider_registry, mock_provider):
        """Test that multiple sessions can be managed concurrently."""
        with patch.object(session_manager, 'registry', mock_provider_registry):
            with patch.object(session_manager, '_create_provider', return_value=mock_provider):
                # Create multiple sessions
                sessions = []
                for i in range(5):
                    request = SessionCreateRequest(
                        provider_type="gemini",
                        metadata={"index": i}
                    )
                    session = await session_manager.create_session(request)
                    sessions.append(session)

        # All sessions should be tracked
        assert len(session_manager._sessions) >= 5

        # Each session should be retrievable
        for session in sessions:
            retrieved = await session_manager.get_session(session.id)
            assert retrieved is not None
            assert retrieved.id == session.id

    @pytest.mark.asyncio
    async def test_concurrent_session_independence(self, session_manager, mock_provider_registry, mock_provider):
        """Test that concurrent sessions are independent."""
        with patch.object(session_manager, 'registry', mock_provider_registry):
            with patch.object(session_manager, '_create_provider', return_value=mock_provider):
                # Create two sessions
                request1 = SessionCreateRequest(provider_type="gemini")
                request2 = SessionCreateRequest(provider_type="openai")

                session1 = await session_manager.create_session(request1)
                session2 = await session_manager.create_session(request2)

                # Start one session
                await session_manager.start_session(session1.id)

        # Sessions should have independent states
        assert session1.status == SessionStatus.ACTIVE
        assert session2.status == SessionStatus.PENDING


# ============================================================================
# 8. SINGLETON PATTERN TESTS
# ============================================================================

@pytest.mark.unit
class TestSingletonPattern:
    """Test singleton pattern implementation."""

    def test_get_session_manager_returns_same_instance(self):
        """Test that get_session_manager returns same instance."""
        manager1 = get_session_manager()
        manager2 = get_session_manager()

        assert manager1 is manager2


# ============================================================================
# 9. TELEPHONY INTEGRATION TESTS
# ============================================================================

@pytest.mark.unit
class TestTelephonyIntegration:
    """Test telephony provider integration."""

    @pytest.mark.asyncio
    async def test_create_session_with_telephony_provider(self, session_manager, mock_provider_registry):
        """Test creating session with telephony provider."""
        request = SessionCreateRequest(
            provider_type="gemini",
            telephony="twilio"
        )

        with patch.object(session_manager, 'registry', mock_provider_registry):
            session = await session_manager.create_session(request)

        assert session.telephony_provider == "twilio"

    @pytest.mark.asyncio
    async def test_create_session_with_phone_number(self, session_manager, mock_provider_registry):
        """Test creating session with phone number metadata."""
        request = SessionCreateRequest(
            provider_type="gemini",
            phone_number="+1234567890"
        )

        with patch.object(session_manager, 'registry', mock_provider_registry):
            session = await session_manager.create_session(request)

        assert "phone_number" in session.metadata
        assert session.metadata["phone_number"] == "+1234567890"
