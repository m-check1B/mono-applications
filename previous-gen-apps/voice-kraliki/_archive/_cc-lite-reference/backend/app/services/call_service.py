"""Call service - Business logic for call management"""

from typing import Optional
from datetime import datetime
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.call import Call, CallStatus, CallDirection
from app.schemas.call import CallCreate, CallUpdate
from app.services.telephony_service import telephony_service
from app.core.logger import get_logger
from app.core.config import settings
from app.core.events import event_publisher

logger = get_logger(__name__)


class CallService:
    """Service for call management operations"""

    def __init__(self, db: AsyncSession):
        """
        Initialize call service

        Args:
            db: Database session
        """
        self.db = db

    async def create_call(
        self,
        call_data: CallCreate,
        organization_id: str,
        agent_id: Optional[str] = None
    ) -> Call:
        """
        Create a new call

        Args:
            call_data: Call creation data
            organization_id: Organization ID
            agent_id: Optional agent ID

        Returns:
            Created call

        Raises:
            ValueError: If telephony service unavailable
        """
        # Create call in Twilio if outbound
        twilio_call_sid = None
        if call_data.direction == CallDirection.OUTBOUND:
            if not telephony_service.is_available():
                raise ValueError("Telephony service not available")

            try:
                result = await telephony_service.create_call(
                    to_number=call_data.to_number,
                    from_number=call_data.from_number
                )
                twilio_call_sid = result["call_sid"]
            except Exception as e:
                logger.error(f"Failed to create Twilio call: {e}")
                raise

        # Create call in database
        call = Call(
            id=str(uuid4()),
            twilio_call_sid=twilio_call_sid,
            from_number=call_data.from_number,
            to_number=call_data.to_number,
            direction=call_data.direction,
            organization_id=organization_id,
            agent_id=agent_id,
            campaign_id=call_data.campaign_id,
            contact_id=call_data.contact_id,
            extra_metadata=call_data.metadata,
            status=CallStatus.QUEUED if call_data.direction == CallDirection.OUTBOUND else CallStatus.RINGING
        )

        self.db.add(call)
        await self.db.commit()
        await self.db.refresh(call)

        logger.info(f"Call created: {call.id} ({call.direction})")

        if getattr(settings, "ENABLE_EVENTS", False):
            try:
                await event_publisher.publish_call_started(
                    call_id=call.id,
                    from_number=call.from_number,
                    to_number=call.to_number,
                    campaign_id=call.campaign_id,
                    organization_id=organization_id,
                    user_id=agent_id or "system",
                )
            except Exception as exc:
                logger.warning(f"Failed to publish call.started event: {exc}")

        return call

    async def get_call(self, call_id: str) -> Optional[Call]:
        """
        Get call by ID

        Args:
            call_id: Call ID

        Returns:
            Call or None
        """
        result = await self.db.execute(
            select(Call).where(Call.id == call_id)
        )
        return result.scalar_one_or_none()

    async def update_call(self, call_id: str, call_data: CallUpdate) -> Optional[Call]:
        """
        Update call

        Args:
            call_id: Call ID
            call_data: Update data

        Returns:
            Updated call or None
        """
        call = await self.get_call(call_id)
        if not call:
            return None

        # Update fields
        for field, value in call_data.model_dump(exclude_unset=True).items():
            if field == "metadata":
                call.extra_metadata = value
                continue
            setattr(call, field, value)

        # If call is being marked as completed, set end_time and calculate duration
        if call_data.status == CallStatus.COMPLETED and not call.end_time:
            call.end_time = datetime.utcnow()
            if call.start_time:
                duration = (call.end_time - call.start_time).total_seconds()
                call.duration = int(duration)

        await self.db.commit()
        await self.db.refresh(call)

        logger.info(f"Call updated: {call.id}")
        return call

    async def list_calls(
        self,
        organization_id: str,
        status: Optional[CallStatus] = None,
        agent_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 20
    ) -> tuple[list[Call], int]:
        """
        List calls with filtering

        Args:
            organization_id: Organization ID
            status: Filter by status
            agent_id: Filter by agent
            skip: Offset
            limit: Limit

        Returns:
            Tuple of (calls list, total count)
        """
        query = select(Call).where(Call.organization_id == organization_id)

        if status:
            query = query.where(Call.status == status)
        if agent_id:
            query = query.where(Call.agent_id == agent_id)

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        # Get paginated results
        query = query.offset(skip).limit(limit).order_by(Call.start_time.desc())
        result = await self.db.execute(query)
        calls = result.scalars().all()

        return list(calls), total

    async def sync_call_from_twilio(self, twilio_call_sid: str) -> Optional[Call]:
        """
        Sync call status from Twilio

        Args:
            twilio_call_sid: Twilio call SID

        Returns:
            Updated call or None
        """
        # Get call from database
        result = await self.db.execute(
            select(Call).where(Call.twilio_call_sid == twilio_call_sid)
        )
        call = result.scalar_one_or_none()

        if not call:
            logger.warning(f"Call not found for Twilio SID: {twilio_call_sid}")
            return None

        # Fetch from Twilio
        try:
            twilio_call = await telephony_service.get_call(twilio_call_sid)

            # Update status
            call.status = CallStatus[twilio_call["status"].upper()]
            if twilio_call.get("duration"):
                call.duration = twilio_call["duration"]
            if twilio_call.get("end_time"):
                call.end_time = twilio_call["end_time"]

            await self.db.commit()
            await self.db.refresh(call)

            logger.info(f"Call synced from Twilio: {call.id}")
            return call

        except Exception as e:
            logger.error(f"Failed to sync call from Twilio: {e}")
            return None
