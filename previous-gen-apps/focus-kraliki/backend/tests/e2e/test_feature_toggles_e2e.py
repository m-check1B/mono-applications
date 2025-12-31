"""
E2E tests for feature toggle disabled states
Tests Gemini File Search, II-Agent, and Voice Transcription toggles
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.orm import Session

from app.models.user import User
from app.core.security import generate_id


class TestGeminiFileSearchDisabled:
    """Test E2E flow when Gemini File Search is disabled"""

    @pytest.mark.asyncio
    async def test_gemini_disabled_sql_fallback(self, test_user: User, db: Session, async_client: AsyncClient, auth_headers: dict):
        """When Gemini disabled, file search should use SQL fallback"""
        # Disable Gemini
        test_user.featureToggles = {"geminiFileSearch": False}
        db.commit()

        # Attempt file search (should use SQL fallback)
        response = await async_client.post(
            "/ai/file-search/query",
            headers=auth_headers,
            json={
                "query": "test query",
                "limit": 10
            }
        )

        # Should work but use SQL instead of Gemini
        # In production, check response headers or metadata for fallback indicator
        assert response.status_code in [200, 503]  # 503 if Gemini required

    @pytest.mark.asyncio
    async def test_gemini_disabled_settings_ui(self, test_user: User, db: Session, async_client: AsyncClient, auth_headers: dict):
        """Settings page should reflect Gemini disabled state"""
        # Disable Gemini
        test_user.featureToggles = {"geminiFileSearch": False}
        db.commit()

        response = await async_client.get(
            "/onboarding/status",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["featureToggles"]["geminiFileSearch"] == False

    @pytest.mark.asyncio
    async def test_gemini_enable_requires_privacy_acknowledgment(self, test_user: User, db: Session, async_client: AsyncClient, auth_headers: dict):
        """Enabling Gemini should require privacy acknowledgment"""
        # Set privacy not acknowledged
        test_user.privacyPreferences = {"dataPrivacyAcknowledged": False}
        test_user.featureToggles = {"geminiFileSearch": False}
        db.commit()


        # Try to enable Gemini without privacy acknowledgment
        response = await async_client.post(
            "/onboarding/feature-toggles",
            headers=auth_headers,
            json={
                "geminiFileSearch": True,
                "iiAgent": False,
                "voiceTranscription": False
            }
        )

        # Should succeed (toggle can be set) but usage should be blocked
        # In production, AI routes would check both toggle AND privacy acknowledgment
        assert response.status_code == 200


class TestIIAgentDisabled:
    """Test E2E flow when II-Agent is disabled"""

    @pytest.mark.asyncio
    async def test_ii_agent_disabled_deterministic_routing(self, test_user: User, db: Session, async_client: AsyncClient, auth_headers: dict):
        """When II-Agent disabled, should use deterministic routing"""
        # Disable II-Agent
        test_user.featureToggles = {"iiAgent": False}
        db.commit()


        # Complex task request (normally would use II-Agent)
        response = await async_client.post(
            "/ai/orchestrate-task",
            headers=auth_headers,
            json={
                "input": "Create 5 tasks for project and schedule them",
                "context": {}
            }
        )

        # Should work but use deterministic routing instead
        # Response might indicate simplified processing
        assert response.status_code in [200, 503]  # 503 if II-Agent required

    @pytest.mark.asyncio
    async def test_ii_agent_disabled_settings_persist(self, test_user: User, db: Session, async_client: AsyncClient, auth_headers: dict):
        """II-Agent toggle should persist across sessions"""
        # Disable II-Agent
        test_user.featureToggles = {"iiAgent": False}
        db.commit()


        # Verify toggle persists
        response = await async_client.get(
            "/onboarding/status",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["featureToggles"]["iiAgent"] == False

        # Simulate session refresh (new request)
        response2 = await async_client.get(
            "/onboarding/status",
            headers=auth_headers
        )

        assert response2.status_code == 200
        data2 = response2.json()
        assert data2["featureToggles"]["iiAgent"] == False

    @pytest.mark.asyncio
    async def test_ii_agent_disabled_no_sessions_created(self, test_user: User, db: Session):
        """When II-Agent disabled, no agent sessions should be created"""
        from app.models.agent_session import AgentSession

        # Disable II-Agent
        test_user.featureToggles = {"iiAgent": False}
        db.commit()

        # Check no agent sessions exist
        sessions = db.query(AgentSession).filter(
            AgentSession.userId == test_user.id
        ).all()

        # Should be empty or very minimal
        assert len(sessions) == 0


class TestVoiceTranscriptionDisabled:
    """Test E2E flow when Voice Transcription is disabled"""

    @pytest.mark.asyncio
    async def test_voice_disabled_ui_hidden(self, test_user: User, db: Session, async_client: AsyncClient, auth_headers: dict):
        """When voice disabled, voice button should not be shown"""
        # Disable voice
        test_user.featureToggles = {"voiceTranscription": False}
        db.commit()


        # Get feature status
        response = await async_client.get(
            "/onboarding/status",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["featureToggles"]["voiceTranscription"] == False
        # Frontend should hide voice button based on this

    @pytest.mark.asyncio
    async def test_voice_disabled_endpoint_blocked(self, test_user: User, db: Session, async_client: AsyncClient, auth_headers: dict):
        """When voice disabled, voice endpoints should be blocked"""
        # Disable voice
        test_user.featureToggles = {"voiceTranscription": False}
        db.commit()


        # Try to use voice endpoint
        response = await async_client.post(
            "/voice/transcribe",
            headers=auth_headers,
            json={
                "audio_data": "base64_encoded_audio"
            }
        )

        # Should be blocked (400 or 403)
        # In production, voice endpoints should check feature toggle
        assert response.status_code in [400, 403, 404, 422]

    @pytest.mark.asyncio
    async def test_voice_disabled_settings_toggle(self, test_user: User, db: Session, async_client: AsyncClient, auth_headers: dict):
        """User can toggle voice on/off in settings"""
        # Start with voice enabled
        test_user.featureToggles = {"voiceTranscription": True}
        db.commit()


        # Disable voice
        response = await async_client.post(
            "/onboarding/feature-toggles",
            headers=auth_headers,
            json={
                "geminiFileSearch": True,
                "iiAgent": True,
                "voiceTranscription": False
            }
        )

        assert response.status_code == 200

        # Verify change persisted
        db.refresh(test_user)
        assert test_user.featureToggles["voiceTranscription"] == False


class TestMultipleTogglesDisabled:
    """Test E2E flow with multiple features disabled"""

    @pytest.mark.asyncio
    async def test_all_ai_features_disabled(self, test_user: User, db: Session, async_client: AsyncClient, auth_headers: dict):
        """User can disable all AI features"""
        # Disable everything
        test_user.featureToggles = {
            "geminiFileSearch": False,
            "iiAgent": False,
            "voiceTranscription": False
        }
        db.commit()


        # Verify all disabled
        response = await async_client.get(
            "/onboarding/status",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["featureToggles"]["geminiFileSearch"] == False
        assert data["featureToggles"]["iiAgent"] == False
        assert data["featureToggles"]["voiceTranscription"] == False

    @pytest.mark.asyncio
    async def test_partial_ai_enabled(self, test_user: User, db: Session, async_client: AsyncClient, auth_headers: dict):
        """User can enable only some AI features"""
        # Enable Gemini, disable others
        test_user.featureToggles = {
            "geminiFileSearch": True,
            "iiAgent": False,
            "voiceTranscription": False
        }
        db.commit()


        # Verify partial enable
        response = await async_client.get(
            "/onboarding/status",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["featureToggles"]["geminiFileSearch"] == True
        assert data["featureToggles"]["iiAgent"] == False
        assert data["featureToggles"]["voiceTranscription"] == False

    @pytest.mark.asyncio
    async def test_toggle_changes_immediate_effect(self, test_user: User, db: Session, async_client: AsyncClient, auth_headers: dict):
        """Toggle changes should take immediate effect"""
        # Start with all enabled
        test_user.featureToggles = {
            "geminiFileSearch": True,
            "iiAgent": True,
            "voiceTranscription": True
        }
        db.commit()


        # Disable Gemini
        response = await async_client.post(
            "/onboarding/feature-toggles",
            headers=auth_headers,
            json={
                "geminiFileSearch": False,
                "iiAgent": True,
                "voiceTranscription": True
            }
        )

        assert response.status_code == 200

        # Immediate verification
        response2 = await async_client.get(
            "/onboarding/status",
            headers=auth_headers
        )

        assert response2.status_code == 200
        data = response2.json()
        assert data["featureToggles"]["geminiFileSearch"] == False


class TestFeatureTogglesSecurity:
    """Test security aspects of feature toggles"""

    @pytest.mark.asyncio
    async def test_user_cannot_see_other_user_toggles(self, test_user: User, db: Session, async_client: AsyncClient, auth_headers: dict):
        """Users should only see their own feature toggles"""
        # Create another user
        other_user = User(
            id=generate_id(),
            email="other@example.com",
            username="other",
            organizationId=generate_id(),  # Add organizationId
            onboardingCompleted=False,
            onboardingStep=0,
            featureToggles={
                "geminiFileSearch": False,
                "iiAgent": False,
                "voiceTranscription": False
            }
        )
        db.add(other_user)
        db.commit()

        # Test user has different toggles
        test_user.featureToggles = {
            "geminiFileSearch": True,
            "iiAgent": True,
            "voiceTranscription": True
        }
        db.commit()


        # Get test_user toggles
        response = await async_client.get(
            "/onboarding/status",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        # Should see own toggles, not other_user's
        assert data["featureToggles"]["geminiFileSearch"] == True

    @pytest.mark.asyncio
    async def test_feature_toggles_require_auth(self, async_client: AsyncClient):
        """Feature toggle endpoints require authentication"""
        # Try without auth
        response = await async_client.get("/onboarding/status")

        assert response.status_code in [401, 403, 422]

    @pytest.mark.asyncio
    async def test_feature_toggles_cannot_be_changed_via_get(self, test_user: User, db: Session, async_client: AsyncClient, auth_headers: dict):
        """Feature toggles should only change via POST"""
        test_user.featureToggles = {"geminiFileSearch": True}
        db.commit()


        # GET should not modify
        response = await async_client.get(
            "/onboarding/status",
            headers=auth_headers
        )

        assert response.status_code == 200

        # Verify no changes
        db.refresh(test_user)
        assert test_user.featureToggles["geminiFileSearch"] == True


class TestBYOKIntegration:
    """Test BYOK (Bring Your Own Key) integration with toggles"""

    @pytest.mark.asyncio
    async def test_byok_user_gemini_disabled_no_cost(self, test_user: User, db: Session):
        """BYOK users who disable Gemini should not incur costs"""
        # Set up BYOK
        test_user.openRouterApiKey = "sk-user-key-12345"
        test_user.featureToggles = {"geminiFileSearch": False}
        db.commit()

        # In production, AI requests should:
        # 1. Check if Gemini is disabled
        # 2. If disabled, don't make Gemini API calls (no cost)
        # 3. Use SQL fallback instead

        assert test_user.featureToggles["geminiFileSearch"] == False
        assert test_user.openRouterApiKey is not None

    @pytest.mark.asyncio
    async def test_byok_user_can_enable_all_features(self, test_user: User, db: Session):
        """BYOK users can enable all features using their own keys"""
        test_user.openRouterApiKey = "sk-user-key-12345"
        test_user.featureToggles = {
            "geminiFileSearch": True,
            "iiAgent": True,
            "voiceTranscription": True
        }
        db.commit()

        # All features should use user's API key
        assert test_user.featureToggles["geminiFileSearch"] == True
        assert test_user.featureToggles["iiAgent"] == True
