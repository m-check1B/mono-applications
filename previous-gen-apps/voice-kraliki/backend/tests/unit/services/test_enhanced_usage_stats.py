"""
Tests for Enhanced Usage Service Stats
"""

import pytest
from unittest.mock import MagicMock, patch
from uuid import uuid4

from app.services.usage_service import UsageService

@pytest.fixture
def usage_service():
    """Create a UsageService instance."""
    return UsageService()

@pytest.fixture
def mock_db():
    """Create a mock database session."""
    return MagicMock()

@pytest.fixture
def mock_user():
    """Create a mock user."""
    user = MagicMock()
    user.id = str(uuid4())
    user.preferences = {"subscription": {"plan": "starter"}}
    return user

def test_get_usage_stats_includes_breakdown(usage_service, mock_db, mock_user):
    """Test that get_usage_stats includes provider breakdown."""
    mock_user_result = MagicMock()
    mock_user_result.scalar_one_or_none.return_value = mock_user
    
    # Mock monthly usage for different service types
    # total: 1000s (16.67m), gemini: 600s (10m), openai: 300s (5m)
    def side_effect(query):
        # This is a bit simplified, but enough to mock different calls
        query_str = str(query).lower()
        mock_res = MagicMock()
        if "voice_gemini" in query_str:
            mock_res.scalar.return_value = 600
        elif "voice_openai" in query_str:
            mock_res.scalar.return_value = 300
        elif "voice_minutes" in query_str:
            mock_res.scalar.return_value = 1000
        else:
            mock_res.scalar.return_value = 0
        return mock_res

    # First call is for User, subsequent for UsageRecord sums
    mock_db.execute.side_effect = [mock_user_result, 
                                   side_effect("voice_minutes"),
                                   side_effect("voice_gemini"),
                                   side_effect("voice_openai")]
    
    stats = usage_service.get_usage_stats(mock_db, mock_user.id)
    
    assert "breakdown" in stats
    assert stats["breakdown"]["gemini_minutes"] == 10.0
    assert stats["breakdown"]["openai_minutes"] == 5.0
    assert stats["breakdown"]["other_minutes"] == round(16.67 - 10.0 - 5.0, 2)
    assert stats["used_minutes"] == 16.67
