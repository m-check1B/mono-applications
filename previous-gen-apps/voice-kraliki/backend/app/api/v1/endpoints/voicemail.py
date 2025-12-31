"""Voicemail API endpoints."""

from app.auth.jwt_auth import get_current_user
from app.database import get_db
from app.models.user import User
from app.models.voicemail import (
    GreetingCreate,
    GreetingResponse,
    GreetingType,
    VoicemailBoxCreate,
    VoicemailBoxResponse,
    VoicemailBoxUpdate,
    VoicemailCreate,
    VoicemailMarkRequest,
    VoicemailResponse,
    VoicemailStatsResponse,
    VoicemailStatus,
    VoicemailUpdate,
)
from app.services.voicemail import VoicemailError, VoicemailService
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

router = APIRouter()


# ===== Voicemail Message Management =====

@router.post("/voicemails", response_model=VoicemailResponse, status_code=status.HTTP_201_CREATED)
def create_voicemail(
    voicemail_data: VoicemailCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new voicemail message."""
    service = VoicemailService(db)

    try:
        voicemail = service.create_voicemail(voicemail_data)
        return voicemail
    except VoicemailError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create voicemail: {str(e)}"
        )


@router.get("/voicemails", response_model=list[VoicemailResponse])
def list_voicemails(
    agent_id: int = Query(..., description="Agent ID to list voicemails for"),
    status_filter: VoicemailStatus | None = Query(None, alias="status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List voicemails for an agent."""
    service = VoicemailService(db)

    voicemails = service.list_voicemails(
        agent_id=agent_id,
        status=status_filter,
        skip=skip,
        limit=limit
    )

    return voicemails


@router.get("/voicemails/{voicemail_id}", response_model=VoicemailResponse)
def get_voicemail(
    voicemail_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific voicemail by ID."""
    service = VoicemailService(db)

    voicemail = service.get_voicemail(voicemail_id)
    if not voicemail:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Voicemail {voicemail_id} not found"
        )

    return voicemail


@router.put("/voicemails/{voicemail_id}", response_model=VoicemailResponse)
def update_voicemail(
    voicemail_id: int,
    voicemail_data: VoicemailUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a voicemail."""
    service = VoicemailService(db)

    voicemail = service.update_voicemail(voicemail_id, voicemail_data)
    if not voicemail:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Voicemail {voicemail_id} not found"
        )

    return voicemail


@router.post("/voicemails/{voicemail_id}/heard", response_model=VoicemailResponse)
def mark_as_heard(
    voicemail_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark a voicemail as heard."""
    service = VoicemailService(db)

    voicemail = service.mark_as_heard(voicemail_id)
    if not voicemail:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Voicemail {voicemail_id} not found"
        )

    return voicemail


@router.delete("/voicemails/{voicemail_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_voicemail(
    voicemail_id: int,
    hard_delete: bool = Query(False, description="Permanently delete (true) or soft delete (false)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a voicemail."""
    service = VoicemailService(db)

    success = service.delete_voicemail(voicemail_id, hard_delete=hard_delete)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Voicemail {voicemail_id} not found"
        )

    return None


@router.post("/voicemails/bulk-mark", response_model=dict)
def bulk_mark_voicemails(
    request: VoicemailMarkRequest,
    agent_id: int = Query(..., description="Agent ID for authorization"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Bulk update voicemail status."""
    service = VoicemailService(db)

    count = service.bulk_mark(
        voicemail_ids=request.voicemail_ids,
        status=request.status,
        agent_id=agent_id
    )

    return {
        "updated_count": count,
        "status": request.status.value,
        "message": f"Successfully updated {count} voicemails"
    }


# ===== Mailbox Management =====

@router.post("/mailboxes", response_model=VoicemailBoxResponse, status_code=status.HTTP_201_CREATED)
def create_mailbox(
    mailbox_data: VoicemailBoxCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a voicemail mailbox for an agent."""
    service = VoicemailService(db)

    try:
        mailbox = service.create_mailbox(mailbox_data)
        return mailbox
    except VoicemailError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create mailbox: {str(e)}"
        )


@router.get("/mailboxes/{mailbox_id}", response_model=VoicemailBoxResponse)
def get_mailbox(
    mailbox_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a mailbox by ID."""
    service = VoicemailService(db)

    mailbox = service.get_mailbox(mailbox_id)
    if not mailbox:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Mailbox {mailbox_id} not found"
        )

    return mailbox


@router.get("/mailboxes/agent/{agent_id}", response_model=VoicemailBoxResponse)
def get_mailbox_by_agent(
    agent_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a mailbox by agent ID."""
    service = VoicemailService(db)

    mailbox = service.get_mailbox_by_agent(agent_id)
    if not mailbox:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Mailbox not found for agent {agent_id}"
        )

    return mailbox


@router.put("/mailboxes/{mailbox_id}", response_model=VoicemailBoxResponse)
def update_mailbox(
    mailbox_id: int,
    mailbox_data: VoicemailBoxUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a mailbox."""
    service = VoicemailService(db)

    mailbox = service.update_mailbox(mailbox_id, mailbox_data)
    if not mailbox:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Mailbox {mailbox_id} not found"
        )

    return mailbox


# ===== Greeting Management =====

@router.post("/greetings", response_model=GreetingResponse, status_code=status.HTTP_201_CREATED)
def create_greeting(
    greeting_data: GreetingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a voicemail greeting."""
    service = VoicemailService(db)

    try:
        greeting = service.create_greeting(greeting_data)
        return greeting
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create greeting: {str(e)}"
        )


@router.get("/greetings/{greeting_id}", response_model=GreetingResponse)
def get_greeting(
    greeting_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a greeting by ID."""
    service = VoicemailService(db)

    greeting = service.get_greeting(greeting_id)
    if not greeting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Greeting {greeting_id} not found"
        )

    return greeting


@router.get("/mailboxes/{mailbox_id}/greetings", response_model=list[GreetingResponse])
def list_greetings(
    mailbox_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all greetings for a mailbox."""
    service = VoicemailService(db)

    greetings = service.list_greetings(mailbox_id)
    return greetings


@router.post("/mailboxes/{mailbox_id}/greetings/{greeting_id}/activate", response_model=VoicemailBoxResponse)
def set_active_greeting(
    mailbox_id: int,
    greeting_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Set the active greeting for a mailbox."""
    service = VoicemailService(db)

    mailbox = service.set_active_greeting(mailbox_id, greeting_id)
    if not mailbox:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mailbox or greeting not found"
        )

    return mailbox


# ===== Statistics & Maintenance =====

@router.get("/voicemails/agent/{agent_id}/stats", response_model=VoicemailStatsResponse)
def get_voicemail_stats(
    agent_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get voicemail statistics for an agent."""
    service = VoicemailService(db)

    stats = service.get_voicemail_stats(agent_id)
    return VoicemailStatsResponse(**stats)


@router.post("/voicemails/apply-retention", response_model=dict)
def apply_retention_policy(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Apply retention policy and cleanup expired voicemails."""
    service = VoicemailService(db)

    deleted_count = service.apply_retention_policy()

    return {
        "deleted_count": deleted_count,
        "message": f"Successfully applied retention policy. {deleted_count} voicemails marked for deletion."
    }


@router.get("/greeting-types", response_model=list[dict])
def get_greeting_types(
    current_user: User = Depends(get_current_user)
):
    """Get list of available greeting types."""
    return [
        {"value": gt.value, "name": gt.name.replace("_", " ").title()}
        for gt in GreetingType
    ]
