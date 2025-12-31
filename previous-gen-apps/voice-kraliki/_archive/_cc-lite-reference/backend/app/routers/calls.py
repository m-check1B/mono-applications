"""Calls router - FastAPI with Event Publishing"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.events import event_publisher
from app.schemas.call import CallCreate, CallUpdate, CallResponse, CallList
# from app.services.call_service import CallService

router = APIRouter(prefix="/api/calls", tags=["calls"])

# Example: Event publishing integration
# When a call is created:
#   await event_publisher.publish_call_started(
#       call_id=call.id,
#       from_number=call.from_number,
#       to_number=call.to_number,
#       campaign_id=call.campaign_id,
#       organization_id=current_user.organization_id,
#       user_id=current_user.id
#   )
#
# When a call ends:
#   await event_publisher.publish_call_ended(
#       call_id=call.id,
#       duration=call.duration,
#       outcome=call.outcome,
#       transcript=call.transcript,
#       organization_id=current_user.organization_id,
#       user_id=current_user.id
#   )


@router.get("/", response_model=CallList)
async def list_calls(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    call_status: str | None = None,
    agent_id: str | None = None,
    db: AsyncSession = Depends(get_db)
):
    """
    List calls with pagination and filtering

    Args:
        page: Page number
        page_size: Items per page
        call_status: Filter by call status
        agent_id: Filter by agent
        db: Database session

    Returns:
        Paginated list of calls
    """
    from app.services.call_service import CallService
    from app.models.call import CallStatus
    from app.dependencies import get_current_user
    from app.models.user import User

    # Get current user for organization filtering
    # For now, use a default organization ID (TODO: Add proper auth)
    organization_id = "default-org"  # TODO: Get from current_user

    # Convert status string to enum
    status_filter = None
    if call_status:
        try:
            status_filter = CallStatus[call_status.upper()]
        except KeyError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid call status: {call_status}"
            )

    # Calculate pagination
    skip = (page - 1) * page_size

    # Get calls
    call_service = CallService(db)
    calls, total = await call_service.list_calls(
        organization_id=organization_id,
        status=status_filter,
        agent_id=agent_id,
        skip=skip,
        limit=page_size
    )

    return {
        "items": calls,
        "total": total,
        "page": page,
        "page_size": page_size,
        "has_more": total > (page * page_size)
    }


@router.post("/", response_model=CallResponse, status_code=status.HTTP_201_CREATED)
async def create_call(
    call_data: CallCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new outbound call

    Args:
        call_data: Call creation data
        db: Database session

    Returns:
        Created call details
    """
    from app.services.call_service import CallService

    # TODO: Get organization_id and agent_id from current_user
    organization_id = "default-org"
    agent_id = None

    try:
        call_service = CallService(db)
        call = await call_service.create_call(
            call_data=call_data,
            organization_id=organization_id,
            agent_id=agent_id
        )

        # Publish call started event
        if call.twilio_call_sid:
            await event_publisher.publish_call_started(
                call_id=call.id,
                from_number=call.from_number,
                to_number=call.to_number,
                campaign_id=call.campaign_id,
                organization_id=organization_id,
                user_id=agent_id
            )

        return call

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create call: {str(e)}"
        )


@router.get("/{call_id}", response_model=CallResponse)
async def get_call(
    call_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get call details by ID

    Args:
        call_id: Call ID
        db: Database session

    Returns:
        Call details
    """
    from app.services.call_service import CallService

    call_service = CallService(db)
    call = await call_service.get_call(call_id)

    if not call:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Call {call_id} not found"
        )

    return call


@router.put("/{call_id}", response_model=CallResponse)
async def update_call(
    call_id: str,
    call_data: CallUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update call details

    Args:
        call_id: Call ID
        call_data: Call update data
        db: Database session

    Returns:
        Updated call details
    """
    from app.services.call_service import CallService
    from app.models.call import CallStatus

    call_service = CallService(db)
    call = await call_service.update_call(call_id, call_data)

    if not call:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Call {call_id} not found"
        )

    # Publish call ended event if call was marked as completed
    if call_data.status == CallStatus.COMPLETED:
        await event_publisher.publish_call_ended(
            call_id=call.id,
            duration=call.duration or 0,
            outcome=call.disposition or "unknown",
            transcript="",  # TODO: Add transcript
            organization_id=call.organization_id,
            user_id=call.agent_id
        )

    return call


@router.post("/{call_id}/end", response_model=CallResponse)
async def end_call(
    call_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    End an active call

    Args:
        call_id: Call ID
        db: Database session

    Returns:
        Updated call with ended status
    """
    from app.services.call_service import CallService
    from app.models.call import CallStatus
    from datetime import datetime
    from app.core.logger import get_logger

    logger = get_logger(__name__)
    call_service = CallService(db)
    call = await call_service.get_call(call_id)

    if not call:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Call {call_id} not found"
        )

    # Mark call as completed
    call.status = CallStatus.COMPLETED
    call.end_time = datetime.utcnow()

    # Calculate duration if start_time exists
    if call.start_time:
        duration = (call.end_time - call.start_time).total_seconds()
        call.duration = int(duration)

    await db.commit()
    await db.refresh(call)

    # Publish call ended event
    await event_publisher.publish_call_ended(
        call_id=call.id,
        duration=call.duration or 0,
        outcome=call.disposition or "ended",
        transcript="",  # TODO: Add transcript when available
        organization_id=call.organization_id,
        user_id=call.agent_id
    )

    logger.info(f"Call ended: {call.id} (duration: {call.duration}s)")
    return call


@router.delete("/{call_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_call(
    call_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a call (soft delete)

    Args:
        call_id: Call ID
        db: Database session
    """
    from app.services.call_service import CallService
    from sqlalchemy import delete as sql_delete
    from app.models.call import Call

    call_service = CallService(db)
    call = await call_service.get_call(call_id)

    if not call:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Call {call_id} not found"
        )

    # Hard delete for now (TODO: Implement soft delete with is_deleted flag)
    await db.execute(sql_delete(Call).where(Call.id == call_id))
    await db.commit()

    return None
