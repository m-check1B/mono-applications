#!/usr/bin/env python3
"""
Milestone 4 Test: AI-First Experience & Automation - AI Insights

Tests real-time transcript, intent, sentiment panels and AI suggestions.
"""

import asyncio
import logging
import sys
from datetime import datetime
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.ai_insights import (
    AIInsightsService,
    IntentCategory,
    Sentiment,
    SuggestionType,
    SuggestionPriority
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TestAIInsights:
    """Test suite for AI Insights functionality"""
    
    def __init__(self):
        self.ai_service = AIInsightsService()
        self.test_results = []
    
    def log_test(self, test_name: str, passed: bool, details: str = ""):
        """Log test result"""
        status = "✓ PASS" if passed else "✗ FAIL"
        logger.info(f"{status}: {test_name}")
        if details:
            logger.info(f"  Details: {details}")
        self.test_results.append((test_name, passed, details))
    
    async def test_intent_analysis(self):
        """Test intent detection and classification"""
        logger.info("=== Testing Intent Analysis ===")
        
        test_cases = [
            {
                "text": "I want to buy a new insurance policy",
                "expected_category": IntentCategory.PURCHASE,
                "expected_intent_keywords": ["buy", "purchase"]
            },
            {
                "text": "I have a problem with my claim, it's not working",
                "expected_category": IntentCategory.COMPLAINT,
                "expected_intent_keywords": ["problem", "issue", "not working"]
            },
            {
                "text": "Can you tell me more about your coverage options?",
                "expected_category": IntentCategory.INQUIRY,
                "expected_intent_keywords": ["tell me", "information"]
            },
            {
                "text": "I need help with the online portal",
                "expected_category": IntentCategory.SUPPORT,
                "expected_intent_keywords": ["help", "support"]
            }
        ]
        
        for i, case in enumerate(test_cases):
            try:
                result = await self.ai_service.analyze_intent(case["text"])
                
                # Check category
                category_match = result.category == case["expected_category"]
                
                # Check for expected keywords
                has_expected_keywords = any(
                    kw in case["text"].lower() for kw in case["expected_intent_keywords"]
                )
                
                # Check confidence
                confidence_ok = result.confidence > 0.2
                
                passed = category_match and has_expected_keywords and confidence_ok
                details = f"Category: {result.category.value}, Confidence: {result.confidence:.2f}, Keywords: {result.keywords}"
                
                self.log_test(f"Intent Analysis Test {i+1}", passed, details)
                
            except Exception as e:
                self.log_test(f"Intent Analysis Test {i+1}", False, f"Error: {e}")
    
    async def test_sentiment_analysis(self):
        """Test sentiment analysis with emotion detection"""
        logger.info("=== Testing Sentiment Analysis ===")
        
        test_cases = [
            {
                "text": "I'm very happy with your service, it's absolutely amazing!",
                "expected_sentiment": Sentiment.POSITIVE,
                "expected_score_range": (0.3, 1.0)
            },
            {
                "text": "This is terrible, I'm angry and frustrated with the experience",
                "expected_sentiment": Sentiment.NEGATIVE,
                "expected_score_range": (-1.0, -0.3)
            },
            {
                "text": "The service is okay, nothing special but it works fine",
                "expected_sentiment": Sentiment.NEUTRAL,
                "expected_score_range": (-0.3, 0.3)
            }
        ]
        
        for i, case in enumerate(test_cases):
            try:
                result = await self.ai_service.analyze_sentiment(case["text"])
                
                # Check sentiment
                sentiment_match = result.sentiment == case["expected_sentiment"]
                
                # Check score range
                min_score, max_score = case["expected_score_range"]
                score_in_range = min_score <= result.score <= max_score
                
                # Check confidence
                confidence_ok = result.confidence > 0.2
                
                passed = sentiment_match and score_in_range and confidence_ok
                details = f"Sentiment: {result.sentiment.value}, Score: {result.score:.2f}, Confidence: {result.confidence:.2f}"
                
                self.log_test(f"Sentiment Analysis Test {i+1}", passed, details)
                
            except Exception as e:
                self.log_test(f"Sentiment Analysis Test {i+1}", False, f"Error: {e}")
    
    async def test_suggestion_generation(self):
        """Test AI suggestion generation"""
        logger.info("=== Testing Suggestion Generation ===")
        
        # Create mock intent and sentiment
        from app.services.ai_insights import IntentAnalysis, SentimentAnalysis
        
        test_cases = [
            {
                "intent": IntentAnalysis(
                    intent="complaint_or_issue",
                    confidence=0.8,
                    category=IntentCategory.COMPLAINT,
                    keywords=["problem", "issue"]
                ),
                "sentiment": SentimentAnalysis(
                    sentiment=Sentiment.NEGATIVE,
                    score=-0.7,
                    confidence=0.8,
                    emotions={"anger": 0.8, "frustration": 0.6}
                ),
                "expected_suggestion_types": [SuggestionType.RESPONSE, SuggestionType.ACTION, SuggestionType.ESCALATION]
            },
            {
                "intent": IntentAnalysis(
                    intent="information_request",
                    confidence=0.7,
                    category=IntentCategory.INQUIRY,
                    keywords=["information", "details"]
                ),
                "sentiment": SentimentAnalysis(
                    sentiment=Sentiment.NEUTRAL,
                    score=0.1,
                    confidence=0.5,
                    emotions={}
                ),
                "expected_suggestion_types": [SuggestionType.RESPONSE]
            }
        ]
        
        for i, case in enumerate(test_cases):
            try:
                suggestions = await self.ai_service.generate_suggestions(
                    case["intent"],
                    case["sentiment"]
                )
                
                # Check that we got suggestions
                has_suggestions = len(suggestions) > 0
                
                # Check suggestion types
                suggestion_types = [s.type for s in suggestions]
                has_expected_types = any(
                    exp_type in suggestion_types for exp_type in case["expected_suggestion_types"]
                )
                
                # Check confidence scores
                confidences_ok = all(s.confidence > 0 for s in suggestions)
                
                passed = has_suggestions and has_expected_types and confidences_ok
                details = f"Suggestions: {len(suggestions)}, Types: {[t.value for t in suggestion_types]}"
                
                self.log_test(f"Suggestion Generation Test {i+1}", passed, details)
                
            except Exception as e:
                self.log_test(f"Suggestion Generation Test {i+1}", False, f"Error: {e}")
    
    async def test_end_to_end_processing(self):
        """Test end-to-end message processing"""
        logger.info("=== Testing End-to-End Processing ===")
        
        test_messages = [
            "I'm really frustrated with my recent claim experience, nothing is working properly",
            "Can you help me understand the coverage details?",
            "I want to purchase a new policy for my car"
        ]
        
        for i, message in enumerate(test_messages):
            try:
                # Process the message
                insights = await self.ai_service.process_message(
                    message=message,
                    role="user",
                    conversation_history=[]
                )
                
                # Check that we got all expected components
                has_intent = "intent" in insights
                has_sentiment = "sentiment" in insights
                has_suggestions = "suggestions" in insights
                
                # Check intent structure
                if has_intent:
                    intent = insights["intent"]
                    intent_valid = all(key in intent for key in ["intent", "confidence", "category", "keywords"])
                else:
                    intent_valid = False
                
                # Check sentiment structure
                if has_sentiment:
                    sentiment = insights["sentiment"]
                    sentiment_valid = all(key in sentiment for key in ["sentiment", "score", "confidence", "emotions"])
                else:
                    sentiment_valid = False
                
                # Check suggestions structure
                if has_suggestions:
                    suggestions = insights["suggestions"]
                    suggestions_valid = len(suggestions) > 0 and all(
                        all(key in s for key in ["id", "type", "title", "description", "priority", "confidence"])
                        for s in suggestions
                    )
                else:
                    suggestions_valid = False
                
                passed = has_intent and has_sentiment and has_suggestions and intent_valid and sentiment_valid and suggestions_valid
                details = f"Intent: {has_intent}, Sentiment: {has_sentiment}, Suggestions: {len(insights.get('suggestions', []))}"
                
                self.log_test(f"End-to-End Processing Test {i+1}", passed, details)
                
            except Exception as e:
                self.log_test(f"End-to-End Processing Test {i+1}", False, f"Error: {e}")
    
    async def test_insight_events_creation(self):
        """Test creation of WebSocket events from insights"""
        logger.info("=== Testing Insight Events Creation ===")
        
        try:
            # Create mock insights
            insights = {
                "intent": {
                    "intent": "complaint_or_issue",
                    "confidence": 0.8,
                    "category": "complaint",
                    "keywords": ["problem", "issue"]
                },
                "sentiment": {
                    "sentiment": "negative",
                    "score": -0.7,
                    "confidence": 0.8,
                    "emotions": {"anger": 0.8}
                },
                "suggestions": [
                    {
                        "id": "suggestion_1",
                        "type": "response",
                        "title": "Acknowledge and Empathize",
                        "description": "Show empathy for customer frustration",
                        "priority": "high",
                        "confidence": 0.9
                    }
                ]
            }
            
            # Create events
            events = self.ai_service.create_insight_events(insights)
            
            # Check event structure
            has_intent_event = any(e["type"] == "intent-analysis" for e in events)
            has_sentiment_event = any(e["type"] == "sentiment-analysis" for e in events)
            has_suggestion_events = any(e["type"] == "suggestion" for e in events)
            
            # Check event data structure
            events_valid = True
            for event in events:
                if "type" not in event or "data" not in event:
                    events_valid = False
                    break
            
            passed = has_intent_event and has_sentiment_event and has_suggestion_events and events_valid
            details = f"Events: {len(events)}, Types: {[e['type'] for e in events]}"
            
            self.log_test("Insight Events Creation", passed, details)
            
        except Exception as e:
            self.log_test("Insight Events Creation", False, f"Error: {e}")
    
    async def run_all_tests(self):
        """Run all test suites"""
        logger.info("=== Milestone 4 AI Insights Test Suite ===")
        
        await self.test_intent_analysis()
        await self.test_sentiment_analysis()
        await self.test_suggestion_generation()
        await self.test_end_to_end_processing()
        await self.test_insight_events_creation()
        
        # Calculate results
        total_tests = len(self.test_results)
        passed_tests = sum(1 for _, passed, _ in self.test_results if passed)
        failed_tests = total_tests - passed_tests
        
        logger.info("\n=== Test Summary ===")
        logger.info(f"Total tests: {total_tests}")
        logger.info(f"Passed: {passed_tests}")
        logger.info(f"Failed: {failed_tests}")
        logger.info(f"Success rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            logger.info("\nFailed Tests:")
            for test_name, passed, details in self.test_results:
                if not passed:
                    logger.info(f"  - {test_name}: {details}")
        
        return passed_tests == total_tests

async def main():
    """Main test runner"""
    tester = TestAIInsights()
    success = await tester.run_all_tests()
    
    if success:
        logger.info("\n🎉 All AI insights tests passed!")
        logger.info("✓ Intent detection and classification working")
        logger.info("✓ Sentiment analysis with emotion detection working")
        logger.info("✓ AI suggestion generation working")
        logger.info("✓ End-to-end message processing working")
        logger.info("✓ WebSocket event creation working")
    else:
        logger.info("\n❌ Some tests failed. Check the logs above.")
    
    return success

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)