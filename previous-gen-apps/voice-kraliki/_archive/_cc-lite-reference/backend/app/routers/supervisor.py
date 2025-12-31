"""Supervisor router - FastAPI endpoints for supervisor controls"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional

from app.core.database import get_db
from app.core.logger import get_logger
from app.models.call import Call, CallTranscript, CallStatus
from app.models.user import User
from app.schemas.supervisor import (
    CallSummaryResponse,
    MonitorCallResponse,
    ActiveCallsResponse
)
from app.dependencies import require_supervisor

logger = get_logger(__name__)

router = APIRouter(prefix="/api/supervisor", tags=["supervisor"])


@router.get("/active-calls", response_model=ActiveCallsResponse)
async def get_active_calls(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_supervisor)
):
    """
    Get all active calls in organization

    Args:
        db: Database session
        current_user: Authenticated user (must be supervisor or admin)

    Returns:
        List of active calls
    """
    result = await db.execute(
        select(Call).where(
            Call.organization_id == current_user.organization_id,
            Call.status == CallStatus.IN_PROGRESS
        ).order_by(Call.start_time.desc())
    )
    active_calls = result.scalars().all()

    return {
        "calls": active_calls,
        "total": len(active_calls)
    }


@router.get("/calls/{call_id}/summary", response_model=CallSummaryResponse)
async def get_call_summary(
    call_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_supervisor)
):
    """
    Get detailed call summary with transcripts and analytics

    Args:
        call_id: Call ID
        db: Database session
        current_user: Authenticated user (must be supervisor or admin)

    Returns:
        Call summary with transcripts and keywords
    """
    # Get call
    result = await db.execute(
        select(Call).where(
            Call.id == call_id,
            Call.organization_id == current_user.organization_id
        )
    )
    call = result.scalar_one_or_none()

    if not call:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Call not found"
        )

    # Get transcripts
    transcripts_result = await db.execute(
        select(CallTranscript).where(
            CallTranscript.call_id == call_id
        ).order_by(CallTranscript.timestamp.asc())
    )
    transcripts = transcripts_result.scalars().all()

    # Calculate duration
    duration_sec = 0
    if call.start_time and call.end_time:
        duration_sec = int((call.end_time - call.start_time).total_seconds())
    elif call.duration:
        duration_sec = call.duration

    # Extract keywords from transcripts
    text_all = " ".join([t.content.lower() for t in transcripts if t.content])
    common_keywords = ['refund', 'cancel', 'order', 'issue', 'account', 'payment', 'price', 'help', 'support']
    keywords = []
    for word in common_keywords:
        count = text_all.count(word)
        if count > 0:
            keywords.append({"word": word, "count": count})
    keywords.sort(key=lambda x: x["count"], reverse=True)

    # Simple sentiment analysis
    positive_words = ['great', 'thanks', 'appreciate', 'good', 'happy', 'excellent']
    negative_words = ['angry', 'cancel', 'problem', 'issue', 'complaint', 'frustrated']
    pos_count = sum(text_all.count(word) for word in positive_words)
    neg_count = sum(text_all.count(word) for word in negative_words)

    if pos_count > neg_count * 1.2:
        sentiment = "positive"
    elif neg_count > pos_count * 1.2:
        sentiment = "negative"
    else:
        sentiment = "neutral"

    return {
        "call_id": call.id,
        "agent_id": call.agent_id,
        "from_number": call.from_number,
        "to_number": call.to_number,
        "status": call.status,
        "direction": call.direction,
        "duration_sec": duration_sec,
        "total_exchanges": len(transcripts),
        "first_utterance": transcripts[0].content if transcripts else "",
        "last_utterance": transcripts[-1].content if len(transcripts) > 0 else "",
        "keywords": keywords[:10],
        "sentiment": sentiment,
        "transcripts": [
            {
                "role": t.role,
                "content": t.content,
                "timestamp": t.timestamp
            }
            for t in transcripts
        ]
    }


@router.post("/calls/{call_id}/monitor", response_model=MonitorCallResponse)
async def monitor_call(
    call_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_supervisor)
):
    """
    Start monitoring a call (listen-only mode)

    Args:
        call_id: Call ID
        db: Database session
        current_user: Authenticated user (must be supervisor or admin)

    Returns:
        Monitor session details
    """
    # Get call
    result = await db.execute(
        select(Call).where(
            Call.id == call_id,
            Call.organization_id == current_user.organization_id
        )
    )
    call = result.scalar_one_or_none()

    if not call:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Call not found"
        )

    if call.status != CallStatus.IN_PROGRESS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Call is not active"
        )

    # Update call to add supervisor
    call.supervisor_id = current_user.id
    await db.commit()

    logger.info(f"Supervisor {current_user.id} monitoring call {call_id}")

    # TODO: Integrate with Twilio to join call in listen-only mode
    return {
        "success": True,
        "call_id": call_id,
        "monitor_url": f"wss://monitor/{call_id}",  # TODO: Real WebSocket URL
        "message": "Monitoring started"
    }


@router.post("/calls/{call_id}/whisper")
async def whisper_to_agent(
    call_id: str,
    message: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_supervisor)
):
    """
    Whisper to agent during call (agent hears, customer doesn't)

    Args:
        call_id: Call ID
        message: Message to whisper
        db: Database session
        current_user: Authenticated user (must be supervisor or admin)

    Returns:
        Success status
    """
    # Get call
    result = await db.execute(
        select(Call).where(
            Call.id == call_id,
            Call.organization_id == current_user.organization_id
        )
    )
    call = result.scalar_one_or_none()

    if not call:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Call not found"
        )

    logger.info(f"Supervisor {current_user.id} whispering to agent on call {call_id}")

    # TODO: Integrate with Twilio for whisper functionality
    return {
        "success": True,
        "message": "Whisper sent to agent"
    }


@router.post("/calls/{call_id}/barge-in")
async def barge_in_call(
    call_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_supervisor)
):
    """
    Barge into call (all parties can hear supervisor)

    Args:
        call_id: Call ID
        db: Database session
        current_user: Authenticated user (must be supervisor or admin)

    Returns:
        Success status
    """
    # Get call
    result = await db.execute(
        select(Call).where(
            Call.id == call_id,
            Call.organization_id == current_user.organization_id
        )
    )
    call = result.scalar_one_or_none()

    if not call:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Call not found"
        )

    # Update call with supervisor
    call.supervisor_id = current_user.id
    await db.commit()

    logger.info(f"Supervisor {current_user.id} barging into call {call_id}")

    # TODO: Integrate with Twilio for barge-in functionality
    return {
        "success": True,
        "conference_url": f"wss://conference/{call_id}",  # TODO: Real conference URL
        "message": "Barge-in started"
    }


@router.post("/calls/{call_id}/end")
async def end_call(
    call_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_supervisor)
):
    """
    End an active call

    Args:
        call_id: Call ID
        db: Database session
        current_user: Authenticated user (must be supervisor or admin)

    Returns:
        Success status
    """
    # Get call
    result = await db.execute(
        select(Call).where(
            Call.id == call_id,
            Call.organization_id == current_user.organization_id
        )
    )
    call = result.scalar_one_or_none()

    if not call:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Call not found"
        )

    # Update call status
    call.status = CallStatus.COMPLETED
    await db.commit()

    logger.info(f"Supervisor {current_user.id} ended call {call_id}")

    # TODO: Integrate with Twilio to end call
    return {
        "success": True,
        "message": "Call ended"
    }
