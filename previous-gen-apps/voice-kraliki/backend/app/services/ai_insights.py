"""
AI Insights Service

Provides real-time analysis of conversation data including:
- Intent detection and classification
- Sentiment analysis with emotion detection
- AI-powered suggestions for agents
- Conversation analytics and metrics
"""

import asyncio
import logging
import re
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)

class IntentCategory(Enum):
    INQUIRY = "inquiry"
    COMPLAINT = "complaint"
    PURCHASE = "purchase"
    SUPPORT = "support"
    GENERAL = "general"

class Sentiment(Enum):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"

class SuggestionType(Enum):
    RESPONSE = "response"
    ACTION = "action"
    ESCALATION = "escalation"

class SuggestionPriority(Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

@dataclass
class IntentAnalysis:
    intent: str
    confidence: float
    category: IntentCategory
    keywords: list[str]

@dataclass
class SentimentAnalysis:
    sentiment: Sentiment
    score: float  # -1 to 1
    confidence: float  # 0 to 1
    emotions: dict[str, float]

@dataclass
class Suggestion:
    id: str
    type: SuggestionType
    title: str
    description: str
    priority: SuggestionPriority
    confidence: float
    timestamp: datetime

class AIInsightsService:
    """Service for generating AI insights from conversation data"""

    def __init__(self):
        self.intent_patterns = self._load_intent_patterns()
        self.sentiment_keywords = self._load_sentiment_keywords()
        self.suggestion_templates = self._load_suggestion_templates()

    def _load_intent_patterns(self) -> dict[IntentCategory, list[dict[str, Any]]]:
        """Load intent detection patterns"""
        return {
            IntentCategory.INQUIRY: [
                {"keywords": ["what", "how", "when", "where", "why", "tell me", "explain"], "weight": 0.8},
                {"keywords": ["information", "details", "specification", "features"], "weight": 0.7},
                {"keywords": ["question", "ask", "wondering", "curious"], "weight": 0.9}
            ],
            IntentCategory.COMPLAINT: [
                {"keywords": ["problem", "issue", "wrong", "broken", "not working", "failed"], "weight": 0.9},
                {"keywords": ["unhappy", "dissatisfied", "disappointed", "frustrated"], "weight": 0.8},
                {"keywords": ["complaint", "grievance", "concern", "worried"], "weight": 0.9}
            ],
            IntentCategory.PURCHASE: [
                {"keywords": ["buy", "purchase", "order", "cost", "price", "pay"], "weight": 0.9},
                {"keywords": ["interested", "want", "need", "looking for"], "weight": 0.7},
                {"keywords": ["deal", "offer", "discount", "promotion"], "weight": 0.6}
            ],
            IntentCategory.SUPPORT: [
                {"keywords": ["help", "support", "assist", "guidance", "troubleshoot"], "weight": 0.9},
                {"keywords": ["fix", "resolve", "solution", "workaround"], "weight": 0.8},
                {"keywords": ["technical", "error", "bug", "issue"], "weight": 0.7}
            ]
        }

    def _load_sentiment_keywords(self) -> dict[str, float]:
        """Load sentiment keyword weights"""
        return {
            # Positive words
            "good": 0.8, "great": 0.9, "excellent": 1.0, "amazing": 1.0, "wonderful": 0.9,
            "happy": 0.8, "satisfied": 0.7, "pleased": 0.8, "perfect": 0.9, "love": 1.0,
            "thank": 0.7, "thanks": 0.6, "appreciate": 0.8, "helpful": 0.7, "fantastic": 0.9,

            # Negative words
            "bad": -0.8, "terrible": -1.0, "awful": -0.9, "horrible": -1.0, "worst": -1.0,
            "angry": -0.8, "frustrated": -0.7, "disappointed": -0.6, "unhappy": -0.7, "sad": -0.6,
            "hate": -1.0, "useless": -0.8, "waste": -0.7, "problem": -0.5, "issue": -0.4,

            # Neutral words
            "okay": 0.1, "fine": 0.1, "alright": 0.1, "neutral": 0.0, "maybe": 0.0
        }

    def _load_suggestion_templates(self) -> dict[str, list[dict[str, Any]]]:
        """Load suggestion templates based on context"""
        return {
            "complaint": [
                {
                    "type": SuggestionType.RESPONSE,
                    "title": "Acknowledge and Empathize",
                    "description": "Start by acknowledging the customer's frustration and showing empathy for their situation.",
                    "priority": SuggestionPriority.HIGH
                },
                {
                    "type": SuggestionType.ACTION,
                    "title": "Offer Immediate Solution",
                    "description": "Propose a concrete solution or next step to address their concern.",
                    "priority": SuggestionPriority.HIGH
                }
            ],
            "inquiry": [
                {
                    "type": SuggestionType.RESPONSE,
                    "title": "Provide Clear Information",
                    "description": "Give detailed, accurate information to answer their question thoroughly.",
                    "priority": SuggestionPriority.MEDIUM
                },
                {
                    "type": SuggestionType.RESPONSE,
                    "title": "Offer Additional Resources",
                    "description": "Suggest relevant documentation, tutorials, or support channels.",
                    "priority": SuggestionPriority.LOW
                }
            ],
            "purchase": [
                {
                    "type": SuggestionType.RESPONSE,
                    "title": "Highlight Key Benefits",
                    "description": "Emphasize the main benefits and value proposition of the product/service.",
                    "priority": SuggestionPriority.HIGH
                },
                {
                    "type": SuggestionType.ACTION,
                    "title": "Create Urgency",
                    "description": "Mention limited-time offers or exclusive deals to encourage action.",
                    "priority": SuggestionPriority.MEDIUM
                }
            ]
        }

    async def analyze_intent(self, text: str, conversation_history: list[dict[str, Any]] | None = None) -> IntentAnalysis:
        """Analyze user intent from text"""
        text_lower = text.lower()
        scores = {}

        # Calculate intent scores based on patterns
        for category, patterns in self.intent_patterns.items():
            score = 0.0
            matched_keywords = []

            for pattern in patterns:
                keyword_matches = sum(1 for keyword in pattern["keywords"] if keyword in text_lower)
                if keyword_matches > 0:
                    pattern_score = (keyword_matches / len(pattern["keywords"])) * pattern["weight"]
                    score += pattern_score
                    matched_keywords.extend([kw for kw in pattern["keywords"] if kw in text_lower])

            scores[category] = score

        # Determine the best intent
        if not scores or max(scores.values()) == 0:
            return IntentAnalysis(
                intent="general",
                confidence=0.5,
                category=IntentCategory.GENERAL,
                keywords=[]
            )

        best_category = max(scores.keys(), key=lambda k: scores[k])
        confidence = min(scores[best_category] * 2, 1.0)  # Boost confidence

        # Extract matched keywords
        matched_keywords = []
        for pattern in self.intent_patterns[best_category]:
            matched_keywords.extend([kw for kw in pattern["keywords"] if kw in text_lower])

        # Generate intent label
        intent_labels = {
            IntentCategory.INQUIRY: "information_request",
            IntentCategory.COMPLAINT: "complaint_or_issue",
            IntentCategory.PURCHASE: "purchase_interest",
            IntentCategory.SUPPORT: "support_request",
            IntentCategory.GENERAL: "general_conversation"
        }

        return IntentAnalysis(
            intent=intent_labels[best_category],
            confidence=confidence,
            category=best_category,
            keywords=list(set(matched_keywords))
        )

    async def analyze_sentiment(self, text: str) -> SentimentAnalysis:
        """Analyze sentiment from text"""
        text_lower = text.lower()
        words = re.findall(r'\b\w+\b', text_lower)

        # Calculate sentiment score
        sentiment_score = 0.0
        word_count = 0

        for word in words:
            if word in self.sentiment_keywords:
                sentiment_score += self.sentiment_keywords[word]
                word_count += 1

        # Normalize score
        if word_count > 0:
            sentiment_score = sentiment_score / word_count
        else:
            sentiment_score = 0.0

        # Clamp to [-1, 1]
        sentiment_score = max(-1.0, min(1.0, sentiment_score))

        # Determine sentiment category
        if sentiment_score > 0.2:
            sentiment = Sentiment.POSITIVE
        elif sentiment_score < -0.2:
            sentiment = Sentiment.NEGATIVE
        else:
            sentiment = Sentiment.NEUTRAL

        # Calculate confidence based on word count and score magnitude
        confidence = min(word_count / 5.0, 1.0) * abs(sentiment_score)
        confidence = max(0.2, confidence)  # Minimum confidence

        # Analyze emotions (simplified)
        emotions = {}
        emotion_keywords = {
            "joy": ["happy", "excited", "pleased", "delighted", "thrilled"],
            "anger": ["angry", "furious", "mad", "irritated", "enraged"],
            "fear": ["scared", "afraid", "worried", "anxious", "concerned"],
            "sadness": ["sad", "upset", "disappointed", "depressed", "hurt"]
        }

        for emotion, keywords in emotion_keywords.items():
            emotion_score = sum(1 for kw in keywords if kw in text_lower)
            if emotion_score > 0:
                emotions[emotion] = min(emotion_score / len(keywords), 1.0)

        return SentimentAnalysis(
            sentiment=sentiment,
            score=sentiment_score,
            confidence=confidence,
            emotions=emotions
        )

    async def generate_suggestions(
        self,
        intent: IntentAnalysis,
        sentiment: SentimentAnalysis,
        conversation_context: list[dict[str, Any]] | None = None
    ) -> list[Suggestion]:
        """Generate AI suggestions based on intent and sentiment"""
        suggestions = []

        # Get templates based on intent category
        templates = self.suggestion_templates.get(intent.category.value, [])

        for template in templates:
            # Adjust priority based on sentiment
            priority = template["priority"]
            if sentiment.sentiment == Sentiment.NEGATIVE and priority == SuggestionPriority.MEDIUM:
                priority = SuggestionPriority.HIGH
            elif sentiment.sentiment == Sentiment.POSITIVE and priority == SuggestionPriority.HIGH:
                priority = SuggestionPriority.MEDIUM

            # Calculate confidence based on intent confidence and sentiment
            confidence = (intent.confidence + sentiment.confidence) / 2

            suggestion = Suggestion(
                id=f"suggestion_{datetime.now().timestamp()}_{len(suggestions)}",
                type=template["type"],
                title=template["title"],
                description=template["description"],
                priority=priority,
                confidence=confidence,
                timestamp=datetime.now()
            )
            suggestions.append(suggestion)

        # Add escalation suggestions for negative sentiment
        if sentiment.sentiment == Sentiment.NEGATIVE and sentiment.score < -0.6:
            escalation = Suggestion(
                id=f"escalation_{datetime.now().timestamp()}",
                type=SuggestionType.ESCALATION,
                title="Consider Escalation",
                description="Customer is highly dissatisfied. Consider escalating to a supervisor or offering compensation.",
                priority=SuggestionPriority.HIGH,
                confidence=0.9,
                timestamp=datetime.now()
            )
            suggestions.append(escalation)

        return suggestions

    async def process_message(
        self,
        message: str,
        role: str,
        conversation_history: list[dict[str, Any]] | None = None
    ) -> dict[str, Any]:
        """Process a message and generate insights"""
        if role != 'user':
            return {}

        # Run analyses in parallel
        intent_task = asyncio.create_task(self.analyze_intent(message, conversation_history))
        sentiment_task = asyncio.create_task(self.analyze_sentiment(message))

        intent, sentiment = await asyncio.gather(intent_task, sentiment_task)

        # Generate suggestions
        suggestions = await self.generate_suggestions(intent, sentiment, conversation_history)

        return {
            "intent": asdict(intent),
            "sentiment": asdict(sentiment),
            "suggestions": [asdict(s) for s in suggestions]
        }

    def create_insight_events(self, insights: dict[str, Any]) -> list[dict[str, Any]]:
        """Create WebSocket events for insights"""
        events = []

        if "intent" in insights:
            events.append({
                "type": "intent-analysis",
                "data": insights["intent"]
            })

        if "sentiment" in insights:
            events.append({
                "type": "sentiment-analysis",
                "data": insights["sentiment"]
            })

        if "suggestions" in insights:
            for suggestion in insights["suggestions"]:
                events.append({
                    "type": "suggestion",
                    "data": suggestion
                })

        return events

# Global instance
ai_insights_service = AIInsightsService()
