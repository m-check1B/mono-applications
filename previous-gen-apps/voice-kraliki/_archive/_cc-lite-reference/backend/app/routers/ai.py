"""AI router - AI agent interactions and features"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional, List
from app.core.database import get_db
from app.dependencies import get_current_user
from app.core.logger import get_logger
from app.models.user import User
from app.services.ai_service import get_ai_service

router = APIRouter(prefix="/api/ai", tags=["ai"])
logger = get_logger(__name__)


class ChatRequest(BaseModel):
    """Chat with AI agent"""
    message: str
    context: Optional[dict] = None
    call_id: Optional[str] = None


class SummarizeRequest(BaseModel):
    """Summarize text"""
    text: str
    max_length: Optional[int] = 150


class TranscribeRequest(BaseModel):
    """Transcribe audio"""
    audio_url: str
    language: Optional[str] = "en"


@router.post("/chat", response_model=dict)
async def chat_with_ai(
    request: ChatRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Chat with AI agent

    **Protected**: Requires authentication
    """
    try:
        ai_service = get_ai_service()

        response = await ai_service.chat(
            message=request.message,
            context=request.context or {},
            user_id=current_user.id
        )

        return {
            'success': True,
            'response': response,
            'model': 'claude-3-5-sonnet-20241022'
        }

    except Exception as e:
        logger.error(f"Error in AI chat: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI chat failed: {str(e)}"
        )


@router.post("/summarize", response_model=dict)
async def summarize_text(
    request: SummarizeRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Summarize text using AI

    **Protected**: Requires authentication
    """
    try:
        ai_service = get_ai_service()

        summary = await ai_service.summarize(
            text=request.text,
            max_length=request.max_length
        )

        return {
            'success': True,
            'summary': summary,
            'original_length': len(request.text),
            'summary_length': len(summary)
        }

    except Exception as e:
        logger.error(f"Error summarizing text: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Summarization failed: {str(e)}"
        )


@router.post("/transcribe", response_model=dict)
async def transcribe_audio(
    request: TranscribeRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Transcribe audio using AI

    **Protected**: Requires authentication
    """
    try:
        ai_service = get_ai_service()

        transcription = await ai_service.transcribe_audio(
            audio_url=request.audio_url,
            language=request.language
        )

        return {
            'success': True,
            'transcription': transcription,
            'language': request.language
        }

    except Exception as e:
        logger.error(f"Error transcribing audio: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Transcription failed: {str(e)}"
        )


@router.get("/models", response_model=dict)
async def get_ai_models(current_user: User = Depends(get_current_user)):
    """
    Get available AI models

    **Protected**: Requires authentication
    """
    return {
        'models': [
            {
                'id': 'claude-3-5-sonnet-20241022',
                'name': 'Claude 3.5 Sonnet',
                'provider': 'Anthropic',
                'capabilities': ['chat', 'summarization', 'analysis']
            },
            {
                'id': 'claude-3-opus-20240229',
                'name': 'Claude 3 Opus',
                'provider': 'Anthropic',
                'capabilities': ['chat', 'summarization', 'analysis', 'complex-reasoning']
            }
        ]
    }


@router.get("/usage", response_model=dict)
async def get_ai_usage(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get AI usage statistics

    **Protected**: Requires authentication
    """
    # Mock implementation - would track actual usage
    return {
        'organization_id': current_user.organization_id,
        'current_month': {
            'requests': 1250,
            'tokens_used': 125000,
            'cost_usd': 12.50
        },
        'limits': {
            'max_requests_per_month': 10000,
            'max_tokens_per_month': 1000000
        }
    }
