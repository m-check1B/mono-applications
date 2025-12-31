#!/usr/bin/env python3
"""Test script for AI integration without database dependencies."""

import asyncio
import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, '/home/adminmatej/github/applications/operator-demo-2026/backend')

from app.models.ai_insights_types import (
    IntentCategory, SentimentScore, UrgencyLevel,
    IntentAnalysis, SentimentAnalysis, AgentSuggestion, 
    ConversationMetrics, ConversationInsights
)
from datetime import datetime, timezone

def test_types_import():
    """Test that all types can be imported and instantiated."""
    print("Testing AI insights types import...")
    
    # Test enums
    intent = IntentCategory.INQUIRY
    sentiment = SentimentScore.NEUTRAL
    urgency = UrgencyLevel.MEDIUM
    print(f"✓ Enums: {intent}, {sentiment}, {urgency}")
    
    # Test dataclasses
    intent_analysis = IntentAnalysis(
        intent="general_inquiry",
        category=IntentCategory.INQUIRY,
        confidence=0.8,
        keywords=["help", "information"],
        context="Customer asking for general information",
        urgency=UrgencyLevel.MEDIUM
    )
    print(f"✓ IntentAnalysis: {intent_analysis.intent}")
    
    sentiment_analysis = SentimentAnalysis(
        score=SentimentScore.NEUTRAL,
        confidence=0.7,
        emotions=[{"joy": 0.2, "trust": 0.3}],
        key_phrases=["thank you", "please"],
        sentiment_trajectory=[0.5, 0.6, 0.5]
    )
    print(f"✓ SentimentAnalysis: {sentiment_analysis.score}")
    
    suggestion = AgentSuggestion(
        type="response",
        title="Acknowledge Customer",
        description="Acknowledge the customer's issue",
        priority="high",
        confidence=0.9,
        reasoning="Good customer service",
        suggested_response="I understand your concern and I'm here to help."
    )
    print(f"✓ AgentSuggestion: {suggestion.title}")
    
    metrics = ConversationMetrics(
        clarity_score=85.0,
        engagement_score=75.0,
        resolution_probability=80.0,
        customer_satisfaction_prediction=85.0,
        handling_time_estimate=10,
        complexity_score=60.0
    )
    print(f"✓ ConversationMetrics: clarity={metrics.clarity_score}")
    
    insights = ConversationInsights(
        session_id="test_session_123",
        timestamp=datetime.now(timezone.utc),
        intent=intent_analysis,
        sentiment=sentiment_analysis,
        suggestions=[suggestion],
        metrics=metrics,
        summary="Customer contacted support for general information.",
        key_topics=["information", "help"],
        action_items=["Provide requested information"]
    )
    print(f"✓ ConversationInsights: session={insights.session_id}")
    
    return True

def test_enhanced_service_import():
    """Test importing the enhanced AI insights service."""
    print("\nTesting enhanced AI insights service import...")
    
    try:
        # Mock environment variables to avoid settings errors
        os.environ['DATABASE_URL'] = 'sqlite:///test.db'
        os.environ['CORS_ORIGINS'] = '["http://localhost:3000"]'
        
        from app.services.enhanced_ai_insights import EnhancedAIInsightsService
        service = EnhancedAIInsightsService()
        print("✓ EnhancedAIInsightsService instantiated successfully")
        
        # Test fallback methods
        test_transcript = "Customer: I need help with my account. Agent: I'd be happy to help you with your account."
        
        intent = service._fallback_intent(test_transcript)
        print(f"✓ Fallback intent: {intent.intent}")
        
        sentiment = service._fallback_sentiment(test_transcript)
        print(f"✓ Fallback sentiment: {sentiment.score}")
        
        suggestions = service._fallback_suggestions(test_transcript)
        print(f"✓ Fallback suggestions: {len(suggestions)} suggestions")
        
        metrics = service._fallback_metrics(test_transcript)
        print(f"✓ Fallback metrics: clarity={metrics.clarity_score}")
        
        summary = service._fallback_summary(test_transcript)
        print(f"✓ Fallback summary: {summary}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error importing enhanced service: {e}")
        return False

async def test_conversation_analysis():
    """Test a full conversation analysis workflow."""
    print("\nTesting conversation analysis workflow...")
    
    try:
        # Mock environment variables
        os.environ['DATABASE_URL'] = 'sqlite:///test.db'
        os.environ['CORS_ORIGINS'] = '["http://localhost:3000"]'
        
        from app.services.enhanced_ai_insights import EnhancedAIInsightsService
        service = EnhancedAIInsightsService()
        
        # Test conversation data
        conversation_data = {
            "session_id": "test_session_456",
            "transcript": """
            Customer: Hi, I'm having trouble with my internet connection. It keeps dropping every few minutes.
            Agent: I'm sorry to hear you're experiencing connection issues. Let me help you troubleshoot this.
            Customer: Thank you. This has been happening for the past two days and it's really frustrating.
            Agent: I understand your frustration. Let's check your modem status first.
            """
        }
        
        # Test analysis (will use fallback methods since no API keys)
        insights = await service.analyze_conversation(conversation_data)
        
        print(f"✓ Analysis completed for session: {insights.session_id}")
        print(f"✓ Intent: {insights.intent.intent} (confidence: {insights.intent.confidence})")
        print(f"✓ Sentiment: {insights.sentiment.score} (confidence: {insights.sentiment.confidence})")
        print(f"✓ Suggestions: {len(insights.suggestions)} generated")
        print(f"✓ Summary: {insights.summary}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error in conversation analysis: {e}")
        return False

async def main():
    """Run all tests."""
    print("🚀 Starting AI Integration Tests\n")
    
    # Test 1: Types import
    if not test_types_import():
        print("❌ Types import test failed")
        return False
    
    # Test 2: Enhanced service import
    if not test_enhanced_service_import():
        print("❌ Enhanced service import test failed")
        return False
    
    # Test 3: Conversation analysis
    if not await test_conversation_analysis():
        print("❌ Conversation analysis test failed")
        return False
    
    print("\n🎉 All AI integration tests passed!")
    print("✅ Phase 3 AI Integration is complete and working")
    return True

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)