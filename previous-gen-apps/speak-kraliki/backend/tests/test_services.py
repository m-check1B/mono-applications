"""
Speak by Kraliki - Service Tests
"""

import pytest
from unittest.mock import patch, MagicMock

from app.services.ai_conversation import AIConversationService, DEFAULT_QUESTIONS, FILLER_SOUNDS
from app.services.analysis import AnalysisService
from app.services.email import EmailService


class TestAIConversationService:
    """Tests for AI Conversation Service."""

    def test_get_filler_sound(self):
        """Test getting random filler sound."""
        service = AIConversationService()
        filler = service.get_filler_sound()
        assert filler in FILLER_SOUNDS

    def test_get_greeting(self):
        """Test greeting generation."""
        service = AIConversationService()
        greeting = service.get_greeting("Jan")
        assert "Jan" in greeting
        assert "Ahoj" in greeting

    def test_get_farewell(self):
        """Test farewell generation."""
        service = AIConversationService()
        farewell = service.get_farewell()
        assert any(word in farewell.lower() for word in ["diky", "dekuji", "moc"])

    def test_default_questions_structure(self):
        """Test default questions have correct structure."""
        for q in DEFAULT_QUESTIONS:
            assert "id" in q
            assert "question" in q
            assert "follow_up_count" in q
            assert isinstance(q["follow_up_count"], int)

    def test_format_history_empty(self):
        """Test formatting empty conversation history."""
        service = AIConversationService()
        result = service._format_history([])
        assert result == "Zadne"

    def test_format_history_with_content(self):
        """Test formatting conversation history."""
        service = AIConversationService()
        history = [
            {"role": "ai", "content": "Hello"},
            {"role": "user", "content": "Hi there"},
        ]
        result = service._format_history(history)
        assert "AI: Hello" in result
        assert "Zamestnanec: Hi there" in result

    def test_fallback_response(self):
        """Test fallback response generation."""
        service = AIConversationService()
        response = service._generate_fallback_response("test message", "test question")
        assert len(response) > 0

    @pytest.mark.asyncio
    async def test_generate_response_without_api_key(self):
        """Test response generation without API key uses fallback."""
        service = AIConversationService()
        service.api_key = None

        response = await service.generate_response(
            employee_name="Test",
            company_name="Test Co",
            department_name="Engineering",
            current_question="How are you?",
            user_message="I'm fine",
            conversation_history=[],
        )

        assert len(response) > 0

    @pytest.mark.asyncio
    async def test_stream_response(self):
        """Test streaming response."""
        service = AIConversationService()
        service.api_key = None  # Use fallback

        chunks = []
        async for chunk in service.stream_response(
            employee_name="Test",
            company_name="Test Co",
            department_name="",
            current_question="Test?",
            user_message="Test",
            conversation_history=[],
        ):
            chunks.append(chunk)

        assert len(chunks) > 0


class TestAnalysisService:
    """Tests for Analysis Service."""

    def test_analyze_transcript_positive(self):
        """Test analyzing positive transcript."""
        service = AnalysisService()
        transcript = [
            {"role": "ai", "content": "How are you doing?"},
            {"role": "user", "content": "I'm doing great! Love my job and team."},
            {"role": "ai", "content": "That's wonderful!"},
            {"role": "user", "content": "Yes, very happy here."},
        ]

        result = service.analyze_transcript(transcript)

        assert "sentiment_score" in result
        assert "topics" in result
        assert "flags" in result
        assert "summary" in result

    def test_analyze_transcript_negative(self):
        """Test analyzing negative transcript."""
        service = AnalysisService()
        transcript = [
            {"role": "ai", "content": "How are you doing?"},
            {"role": "user", "content": "I'm frustrated with management."},
            {"role": "ai", "content": "Tell me more."},
            {"role": "user", "content": "There's too much work and no recognition."},
        ]

        result = service.analyze_transcript(transcript)

        assert result["sentiment_score"] is not None

    def test_generate_alerts(self):
        """Test alert generation from flags."""
        service = AnalysisService()

        alerts = service.generate_alerts(
            conversation_id="conv-123",
            company_id="company-456",
            department_id="dept-789",
            flags=["flight_risk"],
            transcript=[
                {"role": "user", "content": "I'm looking at other opportunities"}
            ],
        )

        assert isinstance(alerts, list)

    def test_empty_transcript_analysis(self):
        """Test analyzing empty transcript."""
        service = AnalysisService()
        result = service.analyze_transcript([])

        assert result["sentiment_score"] is not None
        assert isinstance(result["topics"], list)


class TestEmailService:
    """Tests for Email Service."""

    def test_email_service_init_without_key(self):
        """Test email service initialization without API key."""
        service = EmailService()
        service.api_key = None
        assert service.client is None

    @pytest.mark.asyncio
    async def test_send_email_dev_mode(self):
        """Test sending email in dev mode (no API key)."""
        service = EmailService()
        service._client = None
        service.api_key = None

        result = await service._send_email(
            to="test@test.com",
            subject="Test Subject",
            html="<p>Test content</p>"
        )

        assert result is True  # Returns True in dev mode

    @pytest.mark.asyncio
    async def test_send_survey_invitation(self):
        """Test survey invitation email generation."""
        service = EmailService()
        service._client = None
        service.api_key = None

        result = await service.send_survey_invitation(
            to_email="employee@test.com",
            employee_name="Jan",
            company_name="Test Company",
            magic_link="https://example.com/v/token123",
            survey_name="Monthly Check-in",
        )

        assert result is True

    @pytest.mark.asyncio
    async def test_send_alert_notification(self):
        """Test alert notification email."""
        service = EmailService()
        service._client = None
        service.api_key = None

        result = await service.send_alert_notification(
            to_email="hr@test.com",
            user_name="HR Manager",
            alert_type="flight_risk",
            alert_description="Potential departure detected",
            department_name="Engineering",
            dashboard_link="https://example.com/dashboard",
        )

        assert result is True

    @pytest.mark.asyncio
    async def test_send_welcome_email(self):
        """Test welcome email."""
        service = EmailService()
        service._client = None
        service.api_key = None

        result = await service.send_welcome_email(
            to_email="newuser@test.com",
            user_name="New User",
            company_name="New Company",
            login_link="https://example.com/login",
        )

        assert result is True
