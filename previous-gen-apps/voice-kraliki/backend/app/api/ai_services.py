"""AI Services API endpoints.

Exposes transcription, summarization, agent assistance, and sentiment analysis
services via REST and WebSocket endpoints.
"""

import logging
from uuid import UUID

from fastapi import APIRouter, HTTPException, Request, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

from app.middleware.rate_limit import AI_SERVICE_RATE_LIMIT, limiter
from app.services.agent_assistance_service import (
    AssistanceConfig,
    AssistanceSuggestion,
    get_agent_assistance_service,
)
from app.services.sentiment_service import (
    SentimentAnalysis,
    SentimentConfig,
    SentimentTrend,
    get_sentiment_service,
)
from app.services.summarization_service import (
    CallSummary,
    SummarizationConfig,
    get_summarization_service,
)
from app.services.transcription_service import (
    SpeakerRole,
    TranscriptionConfig,
    TranscriptionSegment,
    get_transcription_service,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ai", tags=["AI Services"])


# Request/Response Models
class StartTranscriptionRequest(BaseModel):
    session_id: UUID
    config: TranscriptionConfig


class AddTranscriptionRequest(BaseModel):
    session_id: UUID
    text: str
    speaker: SpeakerRole
    confidence: float = 1.0
    is_final: bool = True


class GenerateSummaryRequest(BaseModel):
    session_id: UUID
    transcript: str
    config: SummarizationConfig


class AnalyzeSentimentRequest(BaseModel):
    session_id: UUID
    text: str
    speaker: str


class GetAssistanceRequest(BaseModel):
    session_id: UUID
    transcript: str
    context: dict = {}


# Transcription Endpoints
@router.post("/transcription/start")
@limiter.limit(AI_SERVICE_RATE_LIMIT)
async def start_transcription(http_request: Request, request: StartTranscriptionRequest):
    """Start transcription for a session. Rate limited (AI operation)."""
    try:
        service = get_transcription_service()
        await service.start_transcription(request.session_id, request.config)
        return {
            "status": "success",
            "message": f"Transcription started for session {request.session_id}"
        }
    except Exception as e:
        logger.error(f"Failed to start transcription: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/transcription/stop")
@limiter.limit(AI_SERVICE_RATE_LIMIT)
async def stop_transcription(request: Request, session_id: UUID):
    """Stop transcription for a session. Rate limited (AI operation)."""
    try:
        service = get_transcription_service()
        await service.stop_transcription(session_id)
        return {
            "status": "success",
            "message": f"Transcription stopped for session {session_id}"
        }
    except Exception as e:
        logger.error(f"Failed to stop transcription: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/transcription/add")
@limiter.limit(AI_SERVICE_RATE_LIMIT)
async def add_transcription(http_request: Request, request: AddTranscriptionRequest) -> TranscriptionSegment:
    """Add a transcription segment. Rate limited (AI operation)."""
    try:
        service = get_transcription_service()
        segment = await service.add_transcription(
            request.session_id,
            request.text,
            request.speaker,
            request.confidence,
            request.is_final
        )
        return segment
    except Exception as e:
        logger.error(f"Failed to add transcription: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/transcription/history/{session_id}")
async def get_transcription_history(
    session_id: UUID,
    limit: int | None = None
) -> list[TranscriptionSegment]:
    """Get transcription history for a session."""
    try:
        service = get_transcription_service()
        return service.get_transcription_history(session_id, limit)
    except Exception as e:
        logger.error(f"Failed to get transcription history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/transcription/full/{session_id}")
async def get_full_transcript(
    session_id: UUID,
    include_interim: bool = False
) -> dict:
    """Get full transcript as formatted text."""
    try:
        service = get_transcription_service()
        transcript = service.get_full_transcript(session_id, include_interim)
        return {"session_id": str(session_id), "transcript": transcript}
    except Exception as e:
        logger.error(f"Failed to get full transcript: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/transcription/stats/{session_id}")
async def get_transcription_stats(session_id: UUID) -> dict:
    """Get transcription statistics."""
    try:
        service = get_transcription_service()
        return await service.get_session_stats(session_id)
    except Exception as e:
        logger.error(f"Failed to get transcription stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Summarization Endpoints
@router.post("/summarization/generate")
@limiter.limit(AI_SERVICE_RATE_LIMIT)
async def generate_summary(http_request: Request, request: GenerateSummaryRequest) -> CallSummary:
    """Generate AI-powered call summary. Rate limited (AI operation)."""
    try:
        service = get_summarization_service()
        summary = await service.generate_summary(
            request.session_id,
            request.transcript,
            request.config
        )
        return summary
    except Exception as e:
        logger.error(f"Failed to generate summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/summarization/{session_id}")
async def get_summary(session_id: UUID) -> CallSummary | None:
    """Get cached summary for a session."""
    try:
        service = get_summarization_service()
        summary = await service.get_summary(session_id)
        if not summary:
            raise HTTPException(status_code=404, detail="Summary not found")
        return summary
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Agent Assistance Endpoints
@router.post("/assistance/start")
@limiter.limit(AI_SERVICE_RATE_LIMIT)
async def start_assistance(request: Request, session_id: UUID, config: AssistanceConfig):
    """Start agent assistance for a session. Rate limited (AI operation)."""
    try:
        service = get_agent_assistance_service()
        await service.start_assistance(session_id, config)
        return {
            "status": "success",
            "message": f"Agent assistance started for session {session_id}"
        }
    except Exception as e:
        logger.error(f"Failed to start assistance: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/assistance/stop")
@limiter.limit(AI_SERVICE_RATE_LIMIT)
async def stop_assistance(request: Request, session_id: UUID):
    """Stop agent assistance for a session. Rate limited (AI operation)."""
    try:
        service = get_agent_assistance_service()
        await service.stop_assistance(session_id)
        return {
            "status": "success",
            "message": f"Agent assistance stopped for session {session_id}"
        }
    except Exception as e:
        logger.error(f"Failed to stop assistance: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/assistance/analyze")
@limiter.limit(AI_SERVICE_RATE_LIMIT)
async def get_assistance(http_request: Request, request: GetAssistanceRequest) -> list[AssistanceSuggestion]:
    """Get assistance suggestions for current conversation. Rate limited (AI operation)."""
    try:
        service = get_agent_assistance_service()
        suggestions = await service.analyze_conversation(
            request.session_id,
            request.transcript,
            request.context
        )
        return suggestions
    except Exception as e:
        logger.error(f"Failed to get assistance: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/assistance/history/{session_id}")
async def get_assistance_history(
    session_id: UUID,
    limit: int | None = None
) -> list[AssistanceSuggestion]:
    """Get assistance suggestion history."""
    try:
        service = get_agent_assistance_service()
        return service.get_suggestion_history(session_id, limit)
    except Exception as e:
        logger.error(f"Failed to get assistance history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Sentiment Analysis Endpoints
@router.post("/sentiment/start")
@limiter.limit(AI_SERVICE_RATE_LIMIT)
async def start_sentiment_analysis(request: Request, session_id: UUID, config: SentimentConfig):
    """Start sentiment analysis for a session. Rate limited (AI operation)."""
    try:
        service = get_sentiment_service()
        await service.start_analysis(session_id, config)
        return {
            "status": "success",
            "message": f"Sentiment analysis started for session {session_id}"
        }
    except Exception as e:
        logger.error(f"Failed to start sentiment analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sentiment/stop")
@limiter.limit(AI_SERVICE_RATE_LIMIT)
async def stop_sentiment_analysis(request: Request, session_id: UUID):
    """Stop sentiment analysis for a session. Rate limited (AI operation)."""
    try:
        service = get_sentiment_service()
        await service.stop_analysis(session_id)
        return {
            "status": "success",
            "message": f"Sentiment analysis stopped for session {session_id}"
        }
    except Exception as e:
        logger.error(f"Failed to stop sentiment analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sentiment/analyze")
@limiter.limit(AI_SERVICE_RATE_LIMIT)
async def analyze_sentiment(http_request: Request, request: AnalyzeSentimentRequest) -> SentimentAnalysis | None:
    """Analyze sentiment of text. Rate limited (AI operation)."""
    try:
        service = get_sentiment_service()
        analysis = await service.analyze_text(
            request.session_id,
            request.text,
            request.speaker
        )
        return analysis
    except Exception as e:
        logger.error(f"Failed to analyze sentiment: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sentiment/trend/{session_id}")
async def get_sentiment_trend(session_id: UUID) -> SentimentTrend | None:
    """Get sentiment trend for a session."""
    try:
        service = get_sentiment_service()
        trend = await service.get_sentiment_trend(session_id)
        if not trend:
            raise HTTPException(status_code=404, detail="No sentiment data found")
        return trend
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get sentiment trend: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sentiment/history/{session_id}")
async def get_sentiment_history(
    session_id: UUID,
    limit: int | None = None
) -> list[SentimentAnalysis]:
    """Get sentiment history for a session."""
    try:
        service = get_sentiment_service()
        return service.get_sentiment_history(session_id, limit)
    except Exception as e:
        logger.error(f"Failed to get sentiment history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sentiment/alerts/{session_id}")
async def get_sentiment_alerts(session_id: UUID) -> list[dict]:
    """Get sentiment alerts for a session."""
    try:
        service = get_sentiment_service()
        return service.get_alerts(session_id)
    except Exception as e:
        logger.error(f"Failed to get sentiment alerts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# WebSocket endpoint for real-time AI data
@router.websocket("/ws/{session_id}")
async def ai_websocket(websocket: WebSocket, session_id: UUID):
    """WebSocket endpoint for real-time AI service updates."""
    await websocket.accept()
    logger.info(f"AI WebSocket connected for session {session_id}")

    try:
        while True:
            # Receive messages from client
            data = await websocket.receive_json()
            message_type = data.get("type")

            if message_type == "transcription":
                # Add transcription
                service = get_transcription_service()
                segment = await service.add_transcription(
                    session_id,
                    data.get("text", ""),
                    SpeakerRole(data.get("speaker", "agent")),
                    data.get("confidence", 1.0),
                    data.get("is_final", True)
                )
                await websocket.send_json({
                    "type": "transcription",
                    "data": segment.dict()
                })

            elif message_type == "sentiment":
                # Analyze sentiment
                sentiment_service = get_sentiment_service()
                analysis = await sentiment_service.analyze_text(
                    session_id,
                    data.get("text", ""),
                    data.get("speaker", "customer")
                )
                if analysis:
                    await websocket.send_json({
                        "type": "sentiment",
                        "data": analysis.dict()
                    })

            elif message_type == "assistance":
                # Get assistance
                assistance_service = get_agent_assistance_service()
                suggestions = await assistance_service.analyze_conversation(
                    session_id,
                    data.get("transcript", ""),
                    data.get("context", {})
                )
                await websocket.send_json({
                    "type": "assistance",
                    "data": [s.dict() for s in suggestions]
                })

    except WebSocketDisconnect:
        logger.info(f"AI WebSocket disconnected for session {session_id}")
    except Exception as e:
        logger.error(f"AI WebSocket error for session {session_id}: {e}")
        await websocket.close()
