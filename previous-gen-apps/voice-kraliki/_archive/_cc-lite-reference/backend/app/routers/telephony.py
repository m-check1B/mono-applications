"""Telephony router - Advanced telephony operations"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import uuid4
from datetime import datetime
from pydantic import BaseModel, Field
from app.core.database import get_db
from app.dependencies import get_current_user, require_supervisor
from app.core.logger import get_logger
from app.models.user import User
from app.models.call import Call, CallStatus, CallDirection
from app.services.telephony_service import get_telephony_service
import re

router = APIRouter(prefix="/api/telephony", tags=["telephony"])
logger = get_logger(__name__)


class TestCallRequest(BaseModel):
    """Request for test outbound call"""
    to: str = Field(..., pattern=r'^\+?[1-9]\d{7,14}$')
    message: str = None


class TransferCallRequest(BaseModel):
    """Request to transfer call"""
    call_id: str
    to: str = Field(..., pattern=r'^\+?[1-9]\d{7,14}$')
    blind: bool = False


@router.post("/test-call", response_model=dict, dependencies=[Depends(require_supervisor)])
async def test_outbound_call(
    request: TestCallRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Initiate test outbound call

    **Protected**: Requires supervisor role
    """
    try:
        telephony = get_telephony_service()

        # Clean phone number (E.164 format)
        clean_number = request.to if request.to.startswith('+') else f'+{request.to}'

        # Make call via Twilio
        call_sid = await telephony.make_outbound_call(
            to=clean_number,
            metadata={
                'purpose': 'test',
                'initiated_by': current_user.id,
                'message': request.message or 'Test outbound call'
            }
        )

        # Create call record
        call = Call(
            id=str(uuid4()),
            provider_call_id=call_sid,
            from_number=telephony.from_number,
            to_number=clean_number,
            direction=CallDirection.OUTBOUND,
            status=CallStatus.QUEUED,
            agent_id=current_user.id,
            organization_id=current_user.organization_id,
            start_time=datetime.utcnow()
        )
        db.add(call)
        await db.commit()

        return {
            'success': True,
            'callSid': call_sid,
            'message': f'Test call initiated to {clean_number}',
            'to': clean_number
        }

    except Exception as e:
        logger.error(f"Error initiating test call: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initiate test call: {str(e)}"
        )


@router.post("/transfer", response_model=dict, dependencies=[Depends(require_supervisor)])
async def transfer_call(
    request: TransferCallRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Transfer active call to another number

    **Protected**: Requires supervisor role
    """
    try:
        # Get call
        stmt = select(Call).where(
            Call.id == request.call_id,
            Call.organization_id == current_user.organization_id
        )
        result = await db.execute(stmt)
        call = result.scalar_one_or_none()

        if not call:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Call not found"
            )

        if call.status not in [CallStatus.IN_PROGRESS, CallStatus.ON_HOLD]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Call is not active"
            )

        telephony = get_telephony_service()
        clean_number = request.to if request.to.startswith('+') else f'+{request.to}'

        # Transfer call
        success = await telephony.transfer_call(
            call.provider_call_id,
            clean_number,
            blind=request.blind
        )

        if success:
            metadata = call.extra_metadata or {}
            metadata['transferred_to'] = clean_number
            metadata['transferred_by'] = current_user.id
            metadata['transfer_type'] = 'blind' if request.blind else 'attended'
            call.extra_metadata = metadata
            await db.commit()

        return {
            'success': success,
            'message': f"Call transferred to {clean_number}",
            'transferType': 'blind' if request.blind else 'attended'
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error transferring call: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to transfer call: {str(e)}"
        )


@router.post("/hold/{call_id}", response_model=dict)
async def hold_call(
    call_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Put call on hold

    **Protected**: Requires authentication
    """
    try:
        stmt = select(Call).where(
            Call.id == call_id,
            Call.organization_id == current_user.organization_id
        )
        result = await db.execute(stmt)
        call = result.scalar_one_or_none()

        if not call:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Call not found"
            )

        telephony = get_telephony_service()
        success = await telephony.hold_call(call.provider_call_id)

        if success:
            call.status = CallStatus.ON_HOLD
            await db.commit()

        return {'success': success, 'message': 'Call on hold'}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error holding call: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to hold call: {str(e)}"
        )


@router.post("/unhold/{call_id}", response_model=dict)
async def unhold_call(
    call_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Resume call from hold

    **Protected**: Requires authentication
    """
    try:
        stmt = select(Call).where(
            Call.id == call_id,
            Call.organization_id == current_user.organization_id
        )
        result = await db.execute(stmt)
        call = result.scalar_one_or_none()

        if not call:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Call not found"
            )

        telephony = get_telephony_service()
        success = await telephony.unhold_call(call.provider_call_id)

        if success:
            call.status = CallStatus.IN_PROGRESS
            await db.commit()

        return {'success': success, 'message': 'Call resumed'}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error resuming call: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to resume call: {str(e)}"
        )


@router.post("/mute/{call_id}", response_model=dict)
async def mute_call(
    call_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Mute call audio

    **Protected**: Requires authentication
    """
    try:
        stmt = select(Call).where(
            Call.id == call_id,
            Call.organization_id == current_user.organization_id
        )
        result = await db.execute(stmt)
        call = result.scalar_one_or_none()

        if not call:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Call not found"
            )

        telephony = get_telephony_service()
        success = await telephony.mute_call(call.provider_call_id)

        return {'success': success, 'message': 'Call muted'}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error muting call: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to mute call: {str(e)}"
        )


@router.post("/unmute/{call_id}", response_model=dict)
async def unmute_call(
    call_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Unmute call audio

    **Protected**: Requires authentication
    """
    try:
        stmt = select(Call).where(
            Call.id == call_id,
            Call.organization_id == current_user.organization_id
        )
        result = await db.execute(stmt)
        call = result.scalar_one_or_none()

        if not call:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Call not found"
            )

        telephony = get_telephony_service()
        success = await telephony.unmute_call(call.provider_call_id)

        return {'success': success, 'message': 'Call unmuted'}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error unmuting call: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to unmute call: {str(e)}"
        )


@router.get("/providers", response_model=dict)
async def get_providers(current_user: User = Depends(get_current_user)):
    """
    Get available telephony providers

    **Protected**: Requires authentication
    """
    return {
        'providers': [
            {
                'id': 'twilio',
                'name': 'Twilio',
                'status': 'active',
                'capabilities': ['voice', 'sms', 'recording', 'transcription']
            }
        ]
    }
