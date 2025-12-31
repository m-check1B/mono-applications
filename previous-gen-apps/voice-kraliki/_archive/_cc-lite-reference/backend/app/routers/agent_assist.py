"""Agent assist router - Real-time agent assistance and suggestions"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import List, Optional
from app.core.database import get_db
from app.dependencies import get_current_user
from app.core.logger import get_logger
from app.models.user import User
from app.services.ai_service import get_ai_service

router = APIRouter(prefix="/api/agent-assist", tags=["agent-assist"])
logger = get_logger(__name__)


class SuggestionRequest(BaseModel):
    """Request for AI suggestions"""
    call_id: str
    transcript: str
    context: Optional[dict] = None


class ResponseTemplateRequest(BaseModel):
    """Request for response template"""
    category: str
    situation: str


@router.post("/suggestions", response_model=dict)
async def get_suggestions(
    request: SuggestionRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Get AI-powered suggestions for agent

    **Protected**: Requires authentication
    """
    try:
        ai_service = get_ai_service()

        # Generate suggestions based on transcript
        suggestions = await ai_service.generate_agent_suggestions(
            transcript=request.transcript,
            context=request.context or {}
        )

        return {
            'success': True,
            'call_id': request.call_id,
            'suggestions': suggestions,
            'timestamp': datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Error generating suggestions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate suggestions"
        )


@router.get("/templates", response_model=dict)
async def get_response_templates(
    category: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """
    Get response templates for common scenarios

    **Protected**: Requires authentication
    """
    templates = {
        'greeting': [
            'Thank you for calling. How may I assist you today?',
            'Good morning/afternoon. This is {agent_name}. How can I help you?'
        ],
        'hold': [
            'May I place you on hold for a moment while I check that information?',
            'I need to verify this with my supervisor. Can you hold for just a moment?'
        ],
        'closing': [
            'Is there anything else I can help you with today?',
            'Thank you for your call. Have a great day!'
        ],
        'escalation': [
            'I understand your concern. Let me connect you with my supervisor who can better assist you.',
            'I\'d like to transfer you to a specialist who can help resolve this issue.'
        ]
    }

    if category and category in templates:
        return {
            'category': category,
            'templates': templates[category]
        }

    return {
        'categories': list(templates.keys()),
        'templates': templates
    }


@router.post("/analyze-sentiment", response_model=dict)
async def analyze_call_sentiment(
    call_id: str,
    transcript: str,
    current_user: User = Depends(get_current_user)
):
    """
    Analyze call sentiment in real-time

    **Protected**: Requires authentication
    """
    try:
        from app.services.sentiment_service import get_sentiment_service

        sentiment_service = get_sentiment_service()

        # Quick sentiment analysis
        prompt = f"""Analyze the sentiment of this call transcript and provide immediate feedback for the agent.

Transcript: "{transcript}"

Provide:
1. Overall sentiment (positive/neutral/negative)
2. Customer emotion
3. Recommended action for agent
4. Urgency level

Respond with JSON only."""

        # Mock for now - would use actual AI
        result = {
            'call_id': call_id,
            'sentiment': 'neutral',
            'customer_emotion': 'concerned',
            'recommended_action': 'Empathize and provide clear solution',
            'urgency': 'medium'
        }

        return {
            'success': True,
            **result
        }

    except Exception as e:
        logger.error(f"Error analyzing sentiment: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to analyze sentiment"
        )


@router.get("/knowledge-base", response_model=dict)
async def search_knowledge_base(
    query: str,
    limit: int = 5,
    current_user: User = Depends(get_current_user)
):
    """
    Search knowledge base for relevant articles

    **Protected**: Requires authentication
    """
    # Mock knowledge base search
    articles = [
        {
            'id': 'kb-001',
            'title': 'How to handle billing inquiries',
            'summary': 'Step-by-step guide for processing billing questions',
            'relevance': 0.95
        },
        {
            'id': 'kb-002',
            'title': 'Troubleshooting common issues',
            'summary': 'Quick fixes for frequent customer problems',
            'relevance': 0.87
        }
    ]

    return {
        'query': query,
        'articles': articles[:limit],
        'total': len(articles)
    }


@router.post("/feedback", response_model=dict)
async def submit_suggestion_feedback(
    suggestion_id: str,
    helpful: bool,
    current_user: User = Depends(get_current_user)
):
    """
    Submit feedback on AI suggestion

    **Protected**: Requires authentication
    """
    # Would store feedback for training
    return {
        'success': True,
        'message': 'Feedback recorded',
        'suggestion_id': suggestion_id,
        'helpful': helpful
    }


from datetime import datetime
