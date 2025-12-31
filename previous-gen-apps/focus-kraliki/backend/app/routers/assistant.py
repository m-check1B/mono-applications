from __future__ import annotations

import base64
from datetime import datetime
from typing import Dict

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from anthropic import Anthropic

from app.core.security import get_current_user
from app.core.config import settings
from app.core.database import get_db
from app.models.user import User
from app.schemas.voice import (
    InitVoiceSessionRequest,
    InitVoiceSessionResponse,
    ProcessVoiceInputRequest,
    ProcessVoiceInputResponse,
    SynthesizeSpeechRequest,
    SynthesizeSpeechResponse,
    VoiceSessionStatusResponse,
    ChatWithAssistantRequest,
    ChatWithAssistantResponse,
    VoiceProvidersResponse,
    VoiceProviderEnum,
    VoiceTransportConfig,
)
from app.schemas.command_history import (
    LogCommandRequest,
    UpdateCommandStatusRequest,
    CommandHistoryQueryRequest,
    CommandHistoryResponse,
    CommandHistoryListResponse,
    CommandSourcesResponse,
    CommandSourceInfo,
    CommandStatusesResponse,
    CommandStatusInfo,
)
from app.services.voice import VoiceService, VoiceServiceConfig, VoiceProvider, VoiceProviderUnavailable, VoiceSessionNotFound
from app.services.command_history import log_command, update_command_status, get_command_history
from app.models.command_history import CommandSource, CommandStatus

router = APIRouter(prefix="/assistant", tags=["assistant"])

# Lazy initialization for Anthropic client (to avoid test import errors)
_anthropic_client = None


def get_anthropic_client():
    global _anthropic_client
    if _anthropic_client is None:
        _anthropic_client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    return _anthropic_client

voice_service = VoiceService(
    VoiceServiceConfig(
        gemini_api_key=settings.GEMINI_API_KEY,
        gemini_model=settings.GEMINI_AUDIO_MODEL,
        openai_api_key=settings.OPENAI_REALTIME_API_KEY or settings.OPENAI_API_KEY,
        openai_model=settings.OPENAI_REALTIME_MODEL,
        openai_tts_model=settings.OPENAI_TTS_MODEL,
        deepgram_api_key=settings.DEEPGRAM_API_KEY or None,
        deepgram_model=settings.DEEPGRAM_MODEL,
    )
)


_PROVIDER_MAP: Dict[VoiceProviderEnum, VoiceProvider] = {
    VoiceProviderEnum.GEMINI_NATIVE: VoiceProvider.GEMINI_NATIVE,
    VoiceProviderEnum.OPENAI_REALTIME: VoiceProvider.OPENAI_REALTIME,
    VoiceProviderEnum.DEEPGRAM_TRANSCRIPTION: VoiceProvider.DEEPGRAM_TRANSCRIPTION,
}


def _map_provider(provider: VoiceProviderEnum) -> VoiceProvider:
    return _PROVIDER_MAP[provider]


@router.get("/voice/providers", response_model=VoiceProvidersResponse)
async def get_voice_providers() -> VoiceProvidersResponse:
    return VoiceProvidersResponse(providers=voice_service.available_providers())


@router.post("/voice/init", response_model=InitVoiceSessionResponse)
async def init_voice_session(
    request: InitVoiceSessionRequest,
    current_user: User = Depends(get_current_user),
):
    provider = _map_provider(request.provider)

    if provider == VoiceProvider.DEEPGRAM_TRANSCRIPTION:
        raise HTTPException(status_code=400, detail="Deepgram is available for transcription only")

    try:
        session = voice_service.create_session(
            provider,
            language=request.language,
            voice=request.voice,
            metadata={**request.metadata, "user_id": current_user.id},
        )
    except VoiceProviderUnavailable as exc:  # pragma: no cover - runtime path
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    transport = VoiceTransportConfig(**session.transport)

    return InitVoiceSessionResponse(
        success=True,
        provider=request.provider,
        sessionId=session.session_id,
        expiresAt=session.expires_at,
        transport=transport,
        metadata=session.metadata,
        availableProviders=voice_service.available_providers(),
    )


@router.post("/voice/process", response_model=ProcessVoiceInputResponse)
async def process_voice_input(
    request: ProcessVoiceInputRequest,
    current_user: User = Depends(get_current_user),
):
    audio_buffer = base64.b64decode(request.audioData)
    provider_enum = request.provider or VoiceProviderEnum.DEEPGRAM_TRANSCRIPTION
    provider = _map_provider(provider_enum)

    try:
        transcription = await voice_service.transcribe(
            audio_buffer,
            mimetype=request.mimetype,
            language=request.language,
            provider=provider,
        )
    except VoiceProviderUnavailable as exc:  # pragma: no cover
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    prompt = f"""User (voice input, {request.language}) said: "{transcription.transcript}"\n\nRespond with a concise, actionable reply fit for voice assistants."""

    response = get_anthropic_client().messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=200,
        messages=[{"role": "user", "content": prompt}],
    )

    ai_response = response.content[0].text if response.content else ""

    return ProcessVoiceInputResponse(
        success=True,
        transcript=transcription.transcript,
        response=ai_response,
        confidence=transcription.confidence,
        language=request.language,
        provider=provider_enum,
    )


@router.post("/tts", response_model=SynthesizeSpeechResponse)
async def synthesize_speech(
    request: SynthesizeSpeechRequest,
    current_user: User = Depends(get_current_user),
):
    provider = _map_provider(request.provider)

    try:
        audio_bytes = await voice_service.synthesise(
            text=request.text,
            provider=provider,
            voice=request.voice,
            format=request.format,
            language=request.language,
        )
    except VoiceProviderUnavailable as exc:  # pragma: no cover
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    audio_data = base64.b64encode(audio_bytes).decode("utf-8")
    words = max(1, len(request.text.split()))
    duration_seconds = max(1.0, (words / 150.0) * 60.0)

    return SynthesizeSpeechResponse(
        success=True,
        audioData=audio_data,
        format=request.format,
        duration=duration_seconds,
        provider=request.provider,
    )


@router.get("/voice/status/{session_id}", response_model=VoiceSessionStatusResponse)
async def get_voice_session_status(session_id: str, current_user: User = Depends(get_current_user)):
    try:
        session = voice_service.get_session(session_id)
    except VoiceSessionNotFound as exc:
        raise HTTPException(status_code=404, detail="Voice session not found") from exc

    transport = VoiceTransportConfig(**session.transport)

    return VoiceSessionStatusResponse(
        sessionId=session.session_id,
        provider=VoiceProviderEnum(session.provider.value),
        status="active" if not session.is_expired() else "expired",
        createdAt=session.created_at,
        expiresAt=session.expires_at,
        transport=transport,
    )


@router.post("/chat", response_model=ChatWithAssistantResponse)
async def chat_with_assistant(
    request: ChatWithAssistantRequest,
    current_user: User = Depends(get_current_user),
):
    try:
        conversation_id = request.conversationId or f"conv_{int(datetime.utcnow().timestamp())}"
        context_info = ""
        if request.context:
            context_info = f"\n\nContext: {request.context}"

        prompt = f"{request.message}{context_info}"

        response = get_anthropic_client().messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}],
        )

        return ChatWithAssistantResponse(
            success=True,
            response=response.content[0].text if response.content else "",
            conversationId=conversation_id,
            confidence=0.95,
            reasoning="Processed with Claude 3.5 Sonnet",
        )

    except Exception as exc:  # pragma: no cover - defensive path
        raise HTTPException(status_code=500, detail=str(exc)) from exc


# ========== Command History Endpoints ==========

@router.get("/commands", response_model=CommandHistoryListResponse)
async def get_commands(
    source: CommandSource = Query(None, description="Filter by command source"),
    intent: str = Query(None, description="Filter by intent"),
    status: CommandStatus = Query(None, description="Filter by status"),
    since: datetime = Query(None, description="Start date filter (ISO 8601)"),
    until: datetime = Query(None, description="End date filter (ISO 8601)"),
    limit: int = Query(50, ge=1, le=200, description="Maximum results"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get command history for the current user.

    This endpoint returns a paginated list of commands executed by the user,
    optionally filtered by source, intent, status, and date range.

    Query Parameters:
    - source: Filter by command source (voice, api, agent, etc.)
    - intent: Filter by parsed intent (create_task, update_task, etc.)
    - status: Filter by execution status
    - since: Start date (ISO 8601 format)
    - until: End date (ISO 8601 format)
    - limit: Maximum number of results (1-200, default 50)
    - offset: Pagination offset (default 0)

    Returns:
        List of command history records with pagination metadata
    """
    commands, total = get_command_history(
        db,
        user_id=current_user.id,
        source=source,
        intent=intent,
        status=status,
        since=since,
        until=until,
        limit=limit,
        offset=offset,
    )

    return CommandHistoryListResponse(
        commands=[CommandHistoryResponse.model_validate(cmd) for cmd in commands],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.post("/commands", response_model=CommandHistoryResponse)
async def create_command(
    request: LogCommandRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Log a new command to the history.

    This endpoint allows clients to manually log commands to the history.
    Typically used by the frontend to track user actions that don't go through
    other tracked endpoints.

    Body:
    - source: Command source (assistant_voice, assistant_text, etc.)
    - command: Command text/description
    - intent: Parsed intent (optional)
    - context: Additional context (optional)
    - telemetryId: Link to routing telemetry (optional)
    - agentSessionId: II-Agent session UUID (optional)
    - conversationId: AI conversation ID (optional)
    - model: AI model used (optional)
    - confidence: Confidence score (optional)
    - metadata: Additional metadata (optional)

    Returns:
        Created command history record
    """
    cmd = log_command(
        db,
        user_id=current_user.id,
        source=request.source,
        command=request.command,
        intent=request.intent,
        context=request.context,
        telemetry_id=request.telemetryId,
        agent_session_id=request.agentSessionId,
        conversation_id=request.conversationId,
        model=request.model,
        confidence=request.confidence,
        metadata=request.metadata,
    )

    return CommandHistoryResponse.model_validate(cmd)


@router.patch("/commands/{command_id}", response_model=CommandHistoryResponse)
async def update_command(
    command_id: str,
    request: UpdateCommandStatusRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update command status and results.

    This endpoint allows updating the status of a command execution,
    typically to mark it as completed, failed, or to add result data.

    Path Parameters:
    - command_id: ID of the command to update

    Body:
    - status: New command status
    - result: Execution result (optional)
    - error: Error details (optional)

    Returns:
        Updated command history record
    """
    cmd = update_command_status(
        db,
        command_id=command_id,
        status=request.status,
        result=request.result,
        error=request.error,
    )

    if not cmd:
        raise HTTPException(status_code=404, detail="Command not found")

    # Verify ownership
    if cmd.userId != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this command")

    return CommandHistoryResponse.model_validate(cmd)


@router.get("/commands/sources", response_model=CommandSourcesResponse)
async def get_command_sources():
    """
    Get list of available command sources.

    Returns:
        List of command source types with descriptions
    """
    sources = [
        CommandSourceInfo(
            value=CommandSource.ASSISTANT_VOICE.value,
            description="Voice commands via assistant"
        ),
        CommandSourceInfo(
            value=CommandSource.ASSISTANT_TEXT.value,
            description="Text commands via assistant"
        ),
        CommandSourceInfo(
            value=CommandSource.DETERMINISTIC_API.value,
            description="Direct API calls (tasks, projects, etc.)"
        ),
        CommandSourceInfo(
            value=CommandSource.II_AGENT.value,
            description="II-Agent orchestrated executions"
        ),
        CommandSourceInfo(
            value=CommandSource.WORKFLOW.value,
            description="Workflow template executions"
        ),
        CommandSourceInfo(
            value=CommandSource.DIRECT_API.value,
            description="Other direct API operations"
        ),
    ]

    return CommandSourcesResponse(sources=sources)


@router.get("/commands/statuses", response_model=CommandStatusesResponse)
async def get_command_statuses():
    """
    Get list of available command statuses.

    Returns:
        List of command status types with descriptions
    """
    statuses = [
        CommandStatusInfo(
            value=CommandStatus.PENDING.value,
            description="Command is waiting to be executed"
        ),
        CommandStatusInfo(
            value=CommandStatus.IN_PROGRESS.value,
            description="Command is currently executing"
        ),
        CommandStatusInfo(
            value=CommandStatus.COMPLETED.value,
            description="Command executed successfully"
        ),
        CommandStatusInfo(
            value=CommandStatus.FAILED.value,
            description="Command execution failed"
        ),
        CommandStatusInfo(
            value=CommandStatus.CANCELLED.value,
            description="Command was cancelled"
        ),
    ]

    return CommandStatusesResponse(statuses=statuses)
