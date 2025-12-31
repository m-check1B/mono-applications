"""Authenticated AI Service API Routes.

This module provides REST API endpoints for the authenticated AI service,
enabling secure access to AI capabilities with proper authentication and authorization.
"""

import logging
from typing import Any

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from app.auth.jwt_auth import get_current_user
from app.middleware.rate_limit import AI_SERVICE_RATE_LIMIT, API_RATE_LIMIT, limiter
from app.models.user import User
from app.services.authenticated_ai_service import (
    AIServicePermission,
    AuthenticatedAIService,
    authenticated_ai_service,
)

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v1/ai", tags=["authenticated-ai"])


# Request/Response Models
class ConversationAnalysisRequest(BaseModel):
    """Request for conversation analysis."""

    conversation_data: dict[str, Any] = Field(description="Conversation data to analyze")
    real_time: bool = Field(default=False, description="Real-time analysis")


class SentimentAnalysisRequest(BaseModel):
    """Request for sentiment analysis."""

    text: str = Field(description="Text to analyze")
    context: dict[str, Any] | None = Field(default=None, description="Additional context")


class SummarizationRequest(BaseModel):
    """Request for conversation summarization."""

    conversation_data: dict[str, Any] = Field(description="Conversation data to summarize")
    summary_type: str = Field(default="brief", description="Type of summary")


class AgentAssistanceRequest(BaseModel):
    """Request for agent assistance."""

    current_situation: dict[str, Any] = Field(description="Current conversation situation")
    assistance_type: str = Field(default="suggestions", description="Type of assistance")


class WorkflowAutomationRequest(BaseModel):
    """Request for workflow automation."""

    workflow_data: dict[str, Any] = Field(description="Workflow data")
    workflow_type: str = Field(description="Type of workflow to automate")


class ComplianceCheckRequest(BaseModel):
    """Request for compliance checking."""

    interaction_data: dict[str, Any] = Field(description="Interaction data to check")
    compliance_rules: list[str] | None = Field(
        default=None, description="Specific rules to check"
    )


class ContextSharingRequest(BaseModel):
    """Request for context sharing."""

    context_data: dict[str, Any] = Field(description="Context data to share")
    target_users: list[str] | None = Field(default=None, description="Target users")


class AudioOptimizationRequest(BaseModel):
    """Request for audio optimization."""

    optimization_type: str = Field(default="quality", description="Type of optimization")


class AnalyticsRequest(BaseModel):
    """Request for analytics."""

    filters: dict[str, Any] | None = Field(default=None, description="Analytics filters")
    time_range: dict[str, Any] | None = Field(default=None, description="Time range")


# AI Insights Endpoints
@router.post("/insights", response_model=dict[str, Any])
@limiter.limit(AI_SERVICE_RATE_LIMIT)
async def get_ai_insights(
    request_obj: Request,
    request: ConversationAnalysisRequest,
    current_user: User = Depends(get_current_user),
    ai_service: AuthenticatedAIService = Depends(lambda: authenticated_ai_service),
):
    """Get AI-powered conversation insights."""
    try:
        insights = await ai_service.get_ai_insights(
            user=current_user,
            conversation_data=request.conversation_data,
            real_time=request.real_time,
        )
        return {"success": True, "data": insights}
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        logger.error(f"AI insights error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to get AI insights"
        )


# Sentiment Analysis Endpoints
@router.post("/sentiment", response_model=dict[str, Any])
@limiter.limit(AI_SERVICE_RATE_LIMIT)
async def analyze_sentiment(
    request_obj: Request,
    request: SentimentAnalysisRequest,
    current_user: User = Depends(get_current_user),
    ai_service: AuthenticatedAIService = Depends(lambda: authenticated_ai_service),
):
    """Analyze sentiment of text."""
    try:
        sentiment = await ai_service.analyze_sentiment(
            user=current_user,
            text=request.text,
            context=request.context,
        )
        return {"success": True, "data": sentiment}
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        logger.error(f"Sentiment analysis error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to analyze sentiment"
        )


# Transcription Endpoints
@router.post("/transcribe", response_model=dict[str, Any])
@limiter.limit(AI_SERVICE_RATE_LIMIT)
async def transcribe_audio(
    request_obj: Request,
    audio_file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    ai_service: AuthenticatedAIService = Depends(lambda: authenticated_ai_service),
):
    """Transcribe audio file."""
    try:
        # Read audio data
        audio_data = await file.read()
        audio_format = file.filename.split(".")[-1] if file.filename else "wav"

        transcription = await ai_service.transcribe_audio(
            user=current_user,
            audio_data=audio_data,
            format=audio_format,
            real_time=real_time,
        )
        return {"success": True, "data": transcription}
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        logger.error(f"Transcription error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to transcribe audio"
        )


# Text-to-Speech Endpoints
@router.post("/tts", response_class=StreamingResponse)
@limiter.limit(AI_SERVICE_RATE_LIMIT)
async def generate_speech(
    request_obj: Request,
    text: str = File(...),
    voice: str = File(default="default"),
    current_user: User = Depends(get_current_user),
    ai_service: AuthenticatedAIService = Depends(lambda: authenticated_ai_service),
):
    """Generate speech from text."""
    try:
        text = request.get("text", "")
        voice = request.get("voice", "default")
        real_time = request.get("real_time", False)

        audio = await ai_service.generate_speech(
            user=current_user,
            text=text,
            voice=voice,
            real_time=real_time,
        )

        return StreamingResponse(
            iter([audio]),
            media_type="audio/mpeg",
            headers={"Content-Disposition": "attachment; filename=speech.mp3"},
        )
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        logger.error(f"TTS error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to generate speech"
        )


# Summarization Endpoints
@router.post("/summarize", response_model=dict[str, Any])
@limiter.limit(AI_SERVICE_RATE_LIMIT)
async def summarize_conversation(
    request_obj: Request,
    request: SummarizationRequest,
    current_user: User = Depends(get_current_user),
    ai_service: AuthenticatedAIService = Depends(lambda: authenticated_ai_service),
):
    """Summarize conversation."""
    try:
        summary = await ai_service.summarize_conversation(
            user=current_user,
            conversation_data=request.conversation_data,
            summary_type=request.summary_type,
        )
        return {"success": True, "data": summary}
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        logger.error(f"Summarization error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to summarize conversation",
        )


# Agent Assistance Endpoints
@router.post("/agent-assistance", response_model=dict[str, Any])
@limiter.limit(AI_SERVICE_RATE_LIMIT)
async def get_agent_assistance(
    request_obj: Request,
    request: AgentAssistanceRequest,
    current_user: User = Depends(get_current_user),
    ai_service: AuthenticatedAIService = Depends(lambda: authenticated_ai_service),
):
    """Get AI-powered agent assistance."""
    try:
        assistance = await ai_service.get_agent_assistance(
            user=current_user,
            current_situation=request.current_situation,
            assistance_type=request.assistance_type,
        )
        return {"success": True, "data": assistance}
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        logger.error(f"Agent assistance error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get agent assistance",
        )


# Analytics Endpoints
@router.post("/analytics", response_model=dict[str, Any])
@limiter.limit(AI_SERVICE_RATE_LIMIT)
async def get_analytics(
    request_obj: Request,
    request: AnalyticsRequest,
    current_user: User = Depends(get_current_user),
    ai_service: AuthenticatedAIService = Depends(lambda: authenticated_ai_service),
):
    """Get AI-powered analytics."""
    try:
        analytics = await ai_service.get_analytics(
            user=current_user,
            filters=request.filters,
            time_range=request.time_range,
        )
        return {"success": True, "data": analytics}
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        logger.error(f"Analytics error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to get analytics"
        )


# Workflow Automation Endpoints
@router.post("/workflow-automation", response_model=dict[str, Any])
@limiter.limit(AI_SERVICE_RATE_LIMIT)
async def automate_workflow(
    request_obj: Request,
    request: WorkflowAutomationRequest,
    current_user: User = Depends(get_current_user),
    ai_service: AuthenticatedAIService = Depends(lambda: authenticated_ai_service),
):
    """Automate workflow using AI."""
    try:
        result = await ai_service.automate_workflow(
            user=current_user,
            workflow_data=request.workflow_data,
            workflow_type=request.workflow_type,
        )
        return {"success": True, "data": result}
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        logger.error(f"Workflow automation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to automate workflow"
        )


# Compliance Check Endpoints
@router.post("/compliance", response_model=dict[str, Any])
@limiter.limit(AI_SERVICE_RATE_LIMIT)
async def check_compliance(
    request_obj: Request,
    request: ComplianceCheckRequest,
    current_user: User = Depends(get_current_user),
    ai_service: AuthenticatedAIService = Depends(lambda: authenticated_ai_service),
):
    """Check compliance using AI."""
    try:
        compliance = await ai_service.check_compliance(
            user=current_user,
            interaction_data=request.interaction_data,
            compliance_rules=request.compliance_rules,
        )
        return {"success": True, "data": compliance}
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        logger.error(f"Compliance check error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to check compliance"
        )


# Context Sharing Endpoints
@router.post("/context-sharing", response_model=dict[str, Any])
@limiter.limit(AI_SERVICE_RATE_LIMIT)
async def share_context(
    request_obj: Request,
    request: ContextSharingRequest,
    current_user: User = Depends(get_current_user),
    ai_service: AuthenticatedAIService = Depends(lambda: authenticated_ai_service),
):
    """Share context using AI."""
    try:
        result = await ai_service.share_context(
            user=current_user,
            context_data=request.context_data,
            target_users=request.target_users,
        )
        return {"success": True, "data": result}
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        logger.error(f"Context sharing error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to share context"
        )


# Audio Optimization Endpoints
@router.post("/audio-optimize", response_class=StreamingResponse)
@limiter.limit(AI_SERVICE_RATE_LIMIT)
async def optimize_audio(
    request_obj: Request,
    audio_file: UploadFile = File(...),
    optimization_type: str = File(default="quality"),
    current_user: User = Depends(get_current_user),
    ai_service: AuthenticatedAIService = Depends(lambda: authenticated_ai_service),
):
    """Optimize audio using AI."""
    try:
        # Read audio data
        audio_data = await file.read()

        optimized = await ai_service.optimize_audio(
            user=current_user,
            audio_data=audio_data,
            optimization_type=optimization_type,
        )

        return StreamingResponse(
            iter([optimized]),
            media_type="audio/mpeg",
            headers={"Content-Disposition": "attachment; filename=optimized_audio.mp3"},
        )
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        logger.error(f"Audio optimization error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to optimize audio"
        )


# Health Monitoring Endpoints
@router.get("/health", response_model=dict[str, Any])
@limiter.limit(API_RATE_LIMIT)
async def get_health_status(
    request_obj: Request,
    current_user: User = Depends(get_current_user),
    ai_service: AuthenticatedAIService = Depends(lambda: authenticated_ai_service),
):
    """Get AI provider health status."""
    try:
        from app.services.ai_service_manager import ProviderType

        provider_enum = None
        if provider_type:
            try:
                provider_enum = ProviderType(provider_type)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid provider type: {provider_type}",
                )

        health = await ai_service.get_health_status(
            user=current_user,
            provider_type=provider_enum,
        )
        return {"success": True, "data": health}
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        logger.error(f"Health monitoring error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to get health status"
        )


# Usage Statistics Endpoints
@router.get("/usage", response_model=dict[str, Any])
@limiter.limit(API_RATE_LIMIT)
async def get_usage_stats(
    request_obj: Request,
    current_user: User = Depends(get_current_user),
    ai_service: AuthenticatedAIService = Depends(lambda: authenticated_ai_service),
):
    """Get usage statistics for current user."""
    try:
        stats = ai_service.get_usage_stats(current_user.id)
        return {"success": True, "data": stats}
    except Exception as e:
        logger.error(f"Usage stats error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get usage statistics",
        )


@router.get("/usage/all", response_model=dict[str, Any])
@limiter.limit(API_RATE_LIMIT)
async def get_all_usage_stats(
    request_obj: Request,
    current_user: User = Depends(get_current_user),
    ai_service: AuthenticatedAIService = Depends(lambda: authenticated_ai_service),
):
    """Get usage statistics for all users (admin only)."""
    try:
        stats = ai_service.get_all_usage_stats()
        return {"success": True, "data": stats}
    except Exception as e:
        logger.error(f"All usage stats error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get all usage statistics",
        )


# Available Services Endpoint
@router.get("/services", response_model=dict[str, Any])
@limiter.limit(API_RATE_LIMIT)
async def get_available_services(
    request_obj: Request,
    current_user: User = Depends(get_current_user),
    ai_service: AuthenticatedAIService = Depends(lambda: authenticated_ai_service),
):
    """Get list of available AI services for current user."""
    try:
        # Check which services the user has access to
        available_services = []

        service_permissions = {
            "ai_insights": AIServicePermission.INSIGHTS_READ,
            "sentiment_analysis": AIServicePermission.SENTIMENT_ANALYSIS,
            "transcription": AIServicePermission.TRANSCRIPTION,
            "tts": AIServicePermission.TTS,
            "summarization": AIServicePermission.SUMMARIZATION,
            "agent_assistance": AIServicePermission.AGENT_ASSISTANCE,
            "analytics": AIServicePermission.ANALYTICS,
            "workflow_automation": AIServicePermission.WORKFLOW_AUTOMATION,
            "compliance": AIServicePermission.COMPLIANCE_CHECK,
            "context_sharing": AIServicePermission.CONTEXT_SHARING,
            "audio_optimization": AIServicePermission.AUDIO_OPTIMIZATION,
            "health_monitoring": AIServicePermission.HEALTH_MONITORING,
        }

        for service, permission in service_permissions.items():
            if ai_service._check_permission(current_user, permission):
                available_services.append(service)

        return {
            "success": True,
            "data": {
                "available_services": available_services,
                "total_services": len(available_services),
                "user_role": current_user.role,
            },
        }
    except Exception as e:
        logger.error(f"Available services error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get available services",
        )
