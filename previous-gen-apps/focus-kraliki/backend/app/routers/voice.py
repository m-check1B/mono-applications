from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from sqlalchemy.orm import Session
from app.core.database import get_db, SessionLocal
from app.core.security import get_current_user, generate_id
from app.core.config import settings
from app.models.user import User
from app.models.voice_recording import VoiceRecording
from app.models.task import Task, TaskStatus
from app.services.voice import VoiceService, VoiceServiceConfig, VoiceProvider
from app.schemas.voice import (
    VoiceTranscribeRequest,
    VoiceTranscribeResponse,
    VoiceProcessRequest,
    VoiceProcessResponse,
    VoiceToTaskRequest,
    VoiceToTaskResponse
)
from anthropic import Anthropic
from datetime import datetime
from typing import Optional
import json
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/voice", tags=["voice"])

# ========== Background Tasks for File Search Integration ==========

async def import_voice_transcript_background(user_id: str, recording_id: str):
    """
    Background task to import voice transcript to Gemini File Search.

    This runs asynchronously after transcription to enable voice-based knowledge search.
    Gracefully handles Gemini unavailability.
    """
    db: Session = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        recording = db.query(VoiceRecording).filter(
            VoiceRecording.id == recording_id,
            VoiceRecording.userId == user_id
        ).first()

        if not user or not recording:
            logger.warning("Skipping voice transcript import - user or recording not found")
            return

        from app.services.gemini_file_search import import_voice_transcript
        result = await import_voice_transcript(db, user, recording)
        if result:
            logger.info(f"Successfully imported voice transcript {recording.id} to File Search")
        else:
            logger.warning(f"Failed to import voice transcript {recording.id} - Gemini unavailable or error occurred")
    except ImportError:
        logger.debug("Gemini File Search service not available - skipping voice transcript import")
    except Exception as e:
        logger.error(f"Error importing voice transcript {recording_id} to File Search: {e}", exc_info=True)
    finally:
        db.close()

# Initialize voice service
voice_service = VoiceService(VoiceServiceConfig(
    gemini_api_key=settings.GEMINI_API_KEY,
    gemini_model=settings.GEMINI_AUDIO_MODEL,
    openai_api_key=settings.OPENAI_API_KEY,
    openai_model=settings.OPENAI_REALTIME_MODEL,
    openai_tts_model=settings.OPENAI_TTS_MODEL,
    deepgram_api_key=settings.DEEPGRAM_API_KEY,
    deepgram_model=settings.DEEPGRAM_MODEL
))

# Lazy initialization for Anthropic client
_anthropic_client = None

def get_anthropic_client():
    global _anthropic_client
    if _anthropic_client is None:
        _anthropic_client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    return _anthropic_client


@router.get("/providers")
async def get_available_providers(
    current_user: User = Depends(get_current_user)
):
    """Get list of available voice providers"""
    return {
        "providers": voice_service.available_providers(),
        "default": "deepgram" if voice_service.available_providers().get("deepgram") else "gemini"
    }


@router.post("/transcribe", response_model=VoiceTranscribeResponse)
async def transcribe_audio(
    audio: UploadFile = File(...),
    language: str = Form("en"),
    provider: Optional[str] = Form(None),
    background_tasks: BackgroundTasks = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Transcribe audio file to text"""
    try:
        # Read audio data
        audio_data = await audio.read()

        # Determine provider
        voice_provider = None
        if provider:
            try:
                voice_provider = VoiceProvider(provider)
            except ValueError:
                logger.warning(f"Invalid voice provider '{provider}', using default")

        # Transcribe
        result = await voice_service.transcribe(
            audio_data,
            mimetype=audio.content_type or "audio/wav",
            language=language,
            provider=voice_provider
        )

        # Save recording
        recording = VoiceRecording(
            id=generate_id(),
            userId=current_user.id,
            transcript=result.text,
            language=language,
            confidence=result.confidence,
            duration=result.duration,
            mimetype=audio.content_type or "audio/wav",
            provider=provider or "auto",
            createdAt=datetime.utcnow()
        )
        db.add(recording)
        db.commit()
        db.refresh(recording)

        # Schedule background import to File Search
        if background_tasks:
            logger.debug(f"Scheduling File Search import for voice transcript {recording.id}")
            background_tasks.add_task(
                import_voice_transcript_background,
                current_user.id,
                recording.id
            )

        return VoiceTranscribeResponse(
            id=recording.id,
            transcript=result.text,
            confidence=result.confidence,
            language=language,
            duration=result.duration
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")


@router.post("/process", response_model=VoiceProcessResponse)
async def process_voice_input(
    request: VoiceProcessRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Process voice transcript with AI to detect intent and extract structured data"""
    try:
        prompt = f"""Analyze this voice input and return a compact JSON with intent and entities.

Voice Input: "{request.transcript}"

Intents to choose from:
- "create_task"
- "update_task"
- "schedule_event" (calendar events/meetings/reminders)
- "start_timer" (begin time tracking)
- "stop_timer" (stop/finish a running timer)
- "run_workflow" (execute predefined workflow/template)
- "question" (general question)
- "command" (generic instruction)
- "other"

JSON format ONLY:
{{
  "intent": "<one of the above>",
  "confidence": 0.92,
  "entities": {{
    "title": "title or subject",
    "description": "optional detail",
    "priority": 1-5,
    "dueDate": "ISO date if mentioned",
    "start_time": "ISO datetime for events/timers",
    "end_time": "ISO datetime for events",
    "durationMinutes": 30,
    "workflowName": "if workflow requested"
  }},
  "naturalLanguageResponse": "brief confirmation"
}}

Only return valid JSON."""

        response = get_anthropic_client().messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )

        result = json.loads(response.content[0].text)

        # Update voice recording if exists
        if request.recordingId:
            recording = db.query(VoiceRecording).filter(
                VoiceRecording.id == request.recordingId,
                VoiceRecording.userId == current_user.id
            ).first()

            if recording:
                recording.processedResult = result
                recording.intent = result.get("intent")
                db.commit()

        return VoiceProcessResponse(
            intent=result.get("intent", "other"),
            confidence=result.get("confidence", 0.5),
            entities=result.get("entities", {}),
            response=result.get("naturalLanguageResponse", "I understood your input")
        )
    except Exception as e:
        # Fallback processing - log the error for debugging
        logger.warning(f"Voice processing failed, using fallback: {e}")
        return VoiceProcessResponse(
            intent="other",
            confidence=0.3,
            entities={},
            response=f"I heard: {request.transcript}"
        )


@router.post("/to-task", response_model=VoiceToTaskResponse)
async def voice_to_task(
    request: VoiceToTaskRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Convert voice input directly to a task"""
    try:
        # First process the voice input
        process_request = VoiceProcessRequest(
            transcript=request.transcript,
            recordingId=request.recordingId
        )
        processed = await process_voice_input(process_request, current_user, db)

        # If intent is not create_task, return error
        if processed.intent != "create_task" and not request.forceCreate:
            return VoiceToTaskResponse(
                success=False,
                message=f"Input doesn't seem to be a task creation request. Intent detected: {processed.intent}",
                task=None,
                confidence=processed.confidence
            )

        # Create task from entities
        entities = processed.entities

        task = Task(
            id=generate_id(),
            userId=current_user.id,
            title=entities.get("title", request.transcript[:100]),
            description=entities.get("description"),
            priority=entities.get("priority", 2),
            status=TaskStatus.PENDING,
            tags=entities.get("tags", []),
            estimatedMinutes=entities.get("estimatedMinutes"),
            createdAt=datetime.utcnow()
        )

        # Parse due date if provided
        if entities.get("dueDate"):
            try:
                task.dueDate = datetime.fromisoformat(entities["dueDate"].replace("Z", "+00:00"))
            except (ValueError, TypeError) as e:
                # Log parse error but continue with task creation
                logger.warning(f"Failed to parse due date '{entities.get('dueDate')}': {e}")

        db.add(task)
        db.commit()
        db.refresh(task)

        return VoiceToTaskResponse(
            success=True,
            message=processed.response,
            task={
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "priority": task.priority,
                "status": task.status.value,
                "tags": task.tags,
                "estimatedMinutes": task.estimatedMinutes
            },
            confidence=processed.confidence
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Task creation failed: {str(e)}")


@router.get("/recordings")
async def get_voice_recordings(
    limit: int = 20,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's voice recordings"""
    recordings = db.query(VoiceRecording).filter(
        VoiceRecording.userId == current_user.id
    ).order_by(VoiceRecording.createdAt.desc()).limit(limit).offset(offset).all()

    total = db.query(VoiceRecording).filter(
        VoiceRecording.userId == current_user.id
    ).count()

    return {
        "recordings": [
            {
                "id": r.id,
                "transcript": r.transcript,
                "language": r.language,
                "confidence": r.confidence,
                "duration": r.duration,
                "intent": r.intent,
                "createdAt": r.createdAt.isoformat()
            }
            for r in recordings
        ],
        "total": total,
        "limit": limit,
        "offset": offset
    }


@router.delete("/recordings/{recording_id}")
async def delete_voice_recording(
    recording_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a voice recording"""
    recording = db.query(VoiceRecording).filter(
        VoiceRecording.id == recording_id,
        VoiceRecording.userId == current_user.id
    ).first()

    if not recording:
        raise HTTPException(status_code=404, detail="Recording not found")

    db.delete(recording)
    db.commit()

    return {"success": True, "message": "Recording deleted"}
