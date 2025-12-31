"""Recording Management API endpoints."""

from datetime import datetime

from app.auth.jwt_auth import get_current_user
from app.database import get_db
from app.models.recording import (
    DownloadUrlRequest,
    DownloadUrlResponse,
    RecordingCreate,
    RecordingResponse,
    RecordingStatus,
    RecordingUpdate,
    StorageConfigCreate,
    StorageConfigResponse,
    TranscriptCreate,
    TranscriptResponse,
    TranscriptUpdate,
)
from app.models.user import User
from app.services.recording import RecordingError, RecordingService
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

router = APIRouter()


# ===== Recording Management =====

@router.post("/recordings", response_model=RecordingResponse, status_code=status.HTTP_201_CREATED)
def create_recording(
    recording_data: RecordingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new recording entry."""
    service = RecordingService(db)

    try:
        recording = service.create_recording(recording_data)
        return recording
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create recording: {str(e)}"
        )


@router.get("/recordings", response_model=list[RecordingResponse])
def list_recordings(
    agent_id: int | None = Query(None),
    team_id: int | None = Query(None),
    campaign_id: int | None = Query(None),
    status_filter: RecordingStatus | None = Query(None, alias="status"),
    start_date: datetime | None = Query(None),
    end_date: datetime | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List recordings with optional filters."""
    service = RecordingService(db)

    recordings = service.list_recordings(
        agent_id=agent_id,
        team_id=team_id,
        campaign_id=campaign_id,
        status=status_filter,
        start_date=start_date,
        end_date=end_date,
        skip=skip,
        limit=limit
    )

    return recordings


@router.get("/recordings/{recording_id}", response_model=RecordingResponse)
def get_recording(
    recording_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific recording by ID."""
    service = RecordingService(db)

    recording = service.get_recording(recording_id)
    if not recording:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recording {recording_id} not found"
        )

    return recording


@router.get("/recordings/call/{call_sid}", response_model=RecordingResponse)
def get_recording_by_call(
    call_sid: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a recording by call SID."""
    service = RecordingService(db)

    recording = service.get_recording_by_call_sid(call_sid)
    if not recording:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recording not found for call {call_sid}"
        )

    return recording


@router.put("/recordings/{recording_id}", response_model=RecordingResponse)
def update_recording(
    recording_id: int,
    recording_data: RecordingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a recording."""
    service = RecordingService(db)

    recording = service.update_recording(recording_id, recording_data)
    if not recording:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recording {recording_id} not found"
        )

    return recording


@router.post("/recordings/{recording_id}/complete", response_model=RecordingResponse)
def complete_recording(
    recording_id: int,
    duration_seconds: int = Query(..., ge=0),
    file_size_bytes: int = Query(..., ge=0),
    checksum_md5: str | None = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark a recording as completed."""
    service = RecordingService(db)

    recording = service.complete_recording(
        recording_id=recording_id,
        duration_seconds=duration_seconds,
        file_size_bytes=file_size_bytes,
        checksum_md5=checksum_md5
    )

    if not recording:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recording {recording_id} not found"
        )

    return recording


@router.delete("/recordings/{recording_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_recording(
    recording_id: int,
    hard_delete: bool = Query(False, description="Permanently delete (true) or soft delete (false)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a recording."""
    service = RecordingService(db)

    success = service.delete_recording(recording_id, hard_delete=hard_delete)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recording {recording_id} not found"
        )

    return None


@router.post("/recordings/{recording_id}/download-url", response_model=DownloadUrlResponse)
def generate_download_url(
    recording_id: int,
    request: DownloadUrlRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate a signed download URL for a recording."""
    service = RecordingService(db)

    try:
        recording = service.get_recording(recording_id)
        if not recording:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Recording {recording_id} not found"
            )

        url, expires_at = service.generate_download_url(
            recording_id=recording_id,
            expires_in_seconds=request.expires_in_seconds
        )

        return DownloadUrlResponse(
            recording_id=recording_id,
            download_url=url,
            expires_at=expires_at,
            file_format=recording.file_format,
            file_size_bytes=recording.file_size_bytes
        )
    except RecordingError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate download URL: {str(e)}"
        )


# ===== Transcription Management =====

@router.post("/transcripts", response_model=TranscriptResponse, status_code=status.HTTP_201_CREATED)
def create_transcript(
    transcript_data: TranscriptCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a transcription request for a recording."""
    service = RecordingService(db)

    try:
        transcript = service.create_transcript(transcript_data)
        return transcript
    except RecordingError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create transcript: {str(e)}"
        )


@router.get("/transcripts/{transcript_id}", response_model=TranscriptResponse)
def get_transcript(
    transcript_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a transcript by ID."""
    service = RecordingService(db)

    transcript = service.get_transcript(transcript_id)
    if not transcript:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transcript {transcript_id} not found"
        )

    return transcript


@router.get("/recordings/{recording_id}/transcript", response_model=TranscriptResponse)
def get_recording_transcript(
    recording_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get the transcript for a recording."""
    service = RecordingService(db)

    transcript = service.get_recording_transcript(recording_id)
    if not transcript:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No completed transcript found for recording {recording_id}"
        )

    return transcript


@router.put("/transcripts/{transcript_id}", response_model=TranscriptResponse)
def update_transcript(
    transcript_id: int,
    transcript_data: TranscriptUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a transcript."""
    service = RecordingService(db)

    transcript = service.update_transcript(transcript_id, transcript_data)
    if not transcript:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transcript {transcript_id} not found"
        )

    return transcript


@router.get("/transcripts/search", response_model=list[TranscriptResponse])
def search_transcripts(
    query: str = Query(..., min_length=3),
    agent_id: int | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Search transcripts by text content."""
    service = RecordingService(db)

    transcripts = service.search_transcripts(
        search_query=query,
        agent_id=agent_id,
        skip=skip,
        limit=limit
    )

    return transcripts


# ===== Storage Management =====

@router.post("/storage", response_model=StorageConfigResponse, status_code=status.HTTP_201_CREATED)
def create_storage_config(
    config_data: StorageConfigCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a storage provider configuration."""
    service = RecordingService(db)

    try:
        storage = service.create_storage_config(config_data)
        return storage
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create storage config: {str(e)}"
        )


@router.get("/storage/{storage_id}", response_model=StorageConfigResponse)
def get_storage_config(
    storage_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get storage configuration by ID."""
    service = RecordingService(db)

    storage = service.get_storage_config(storage_id)
    if not storage:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Storage configuration {storage_id} not found"
        )

    return storage


@router.get("/storage/default", response_model=StorageConfigResponse)
def get_default_storage(
    team_id: int | None = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get default storage configuration."""
    service = RecordingService(db)

    storage = service.get_default_storage(team_id=team_id)
    if not storage:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No default storage configuration found"
        )

    return storage


# ===== Analytics & Maintenance =====

@router.get("/recordings/stats", response_model=dict)
def get_recording_stats(
    agent_id: int | None = Query(None),
    team_id: int | None = Query(None),
    start_date: datetime | None = Query(None),
    end_date: datetime | None = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get recording statistics."""
    service = RecordingService(db)

    stats = service.get_recording_stats(
        agent_id=agent_id,
        team_id=team_id,
        start_date=start_date,
        end_date=end_date
    )

    return stats


@router.post("/recordings/apply-retention", response_model=dict)
def apply_retention_policy(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Apply retention policy and cleanup expired recordings."""
    service = RecordingService(db)

    deleted_count = service.apply_retention_policy()

    return {
        "deleted_count": deleted_count,
        "message": f"Successfully applied retention policy. {deleted_count} recordings marked for deletion."
    }
