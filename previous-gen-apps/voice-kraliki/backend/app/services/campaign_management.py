"""Campaign management service for CRUD operations."""

from typing import Any

from sqlalchemy import delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.call_flow import (
    CallFlow,
    CallFlowCreate,
    CallFlowUpdate,
    CampaignCall,
    CampaignCallCreate,
    CampaignCallStatus,
    CampaignCallUpdate,
)
from app.models.campaign import Campaign, CampaignCreate, CampaignStatus, CampaignUpdate
from app.models.contact_list import (
    Contact,
    ContactCreate,
    ContactList,
    ContactListCreate,
    ContactListUpdate,
    ContactStatus,
    ContactUpdate,
)


class CampaignManagementService:
    """Service for managing campaigns, contact lists, and call flows."""

    # ===== Campaign Operations =====

    async def create_campaign(
        self,
        db: AsyncSession,
        campaign_data: CampaignCreate
    ) -> Campaign:
        """Create a new campaign."""
        db_campaign = Campaign(**campaign_data.model_dump())
        db.add(db_campaign)
        await db.commit()
        await db.refresh(db_campaign)
        return db_campaign

    async def get_campaign(
        self,
        db: AsyncSession,
        campaign_id: int,
        include_lists: bool = False,
        include_flows: bool = False
    ) -> Campaign | None:
        """Get a campaign by ID with optional relationships."""
        query = select(Campaign).where(Campaign.id == campaign_id)

        if include_lists:
            query = query.options(selectinload(Campaign.contact_lists))
        if include_flows:
            query = query.options(selectinload(Campaign.call_flows))

        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def get_campaigns(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        status: CampaignStatus | None = None,
        created_by: int | None = None
    ) -> list[Campaign]:
        """Get all campaigns with optional filtering."""
        query = select(Campaign)

        if status:
            query = query.where(Campaign.status == status)
        if created_by:
            query = query.where(Campaign.created_by == created_by)

        query = query.offset(skip).limit(limit).order_by(Campaign.created_at.desc())
        result = await db.execute(query)
        return list(result.scalars().all())

    async def update_campaign(
        self,
        db: AsyncSession,
        campaign_id: int,
        campaign_data: CampaignUpdate
    ) -> Campaign | None:
        """Update a campaign."""
        update_data = campaign_data.model_dump(exclude_unset=True)
        if not update_data:
            return await self.get_campaign(db, campaign_id)

        query = (
            update(Campaign)
            .where(Campaign.id == campaign_id)
            .values(**update_data)
            .returning(Campaign)
        )
        result = await db.execute(query)
        await db.commit()
        return result.scalar_one_or_none()

    async def delete_campaign(
        self,
        db: AsyncSession,
        campaign_id: int
    ) -> bool:
        """Delete a campaign and all related data."""
        query = delete(Campaign).where(Campaign.id == campaign_id)
        result = await db.execute(query)
        await db.commit()
        return result.rowcount > 0

    async def update_campaign_status(
        self,
        db: AsyncSession,
        campaign_id: int,
        status: CampaignStatus
    ) -> Campaign | None:
        """Update campaign status."""
        query = (
            update(Campaign)
            .where(Campaign.id == campaign_id)
            .values(status=status)
            .returning(Campaign)
        )
        result = await db.execute(query)
        await db.commit()
        return result.scalar_one_or_none()

    async def get_campaign_metrics(
        self,
        db: AsyncSession,
        campaign_id: int
    ) -> dict[str, Any]:
        """Get aggregated metrics for a campaign."""
        # Get total contacts
        contacts_query = select(func.count(Contact.id)).select_from(ContactList).join(
            Contact
        ).where(ContactList.campaign_id == campaign_id)
        total_contacts = (await db.execute(contacts_query)).scalar() or 0

        # Get contact status breakdown
        status_query = select(
            Contact.status,
            func.count(Contact.id)
        ).select_from(ContactList).join(Contact).where(
            ContactList.campaign_id == campaign_id
        ).group_by(Contact.status)
        status_result = await db.execute(status_query)
        status_breakdown = {row[0]: row[1] for row in status_result.all()}

        # Get call metrics
        calls_query = select(
            func.count(CampaignCall.id),
            func.avg(CampaignCall.duration_seconds),
            func.sum(CampaignCall.cost)
        ).where(CampaignCall.campaign_id == campaign_id)
        call_result = await db.execute(calls_query)
        total_calls, avg_duration, total_cost = call_result.first() or (0, 0, 0)

        # Get disposition breakdown
        disposition_query = select(
            CampaignCall.disposition,
            func.count(CampaignCall.id)
        ).where(
            CampaignCall.campaign_id == campaign_id,
            CampaignCall.disposition.isnot(None)
        ).group_by(CampaignCall.disposition)
        disp_result = await db.execute(disposition_query)
        disposition_breakdown = {row[0]: row[1] for row in disp_result.all()}

        return {
            "campaign_id": campaign_id,
            "total_contacts": total_contacts,
            "contact_status_breakdown": status_breakdown,
            "total_calls": total_calls or 0,
            "average_duration_seconds": float(avg_duration or 0),
            "total_cost": float(total_cost or 0),
            "disposition_breakdown": disposition_breakdown
        }

    # ===== Contact List Operations =====

    async def create_contact_list(
        self,
        db: AsyncSession,
        list_data: ContactListCreate
    ) -> ContactList:
        """Create a new contact list."""
        db_list = ContactList(**list_data.model_dump())
        db.add(db_list)
        await db.commit()
        await db.refresh(db_list)
        return db_list

    async def get_contact_list(
        self,
        db: AsyncSession,
        list_id: int,
        include_contacts: bool = False
    ) -> ContactList | None:
        """Get a contact list by ID."""
        query = select(ContactList).where(ContactList.id == list_id)

        if include_contacts:
            query = query.options(selectinload(ContactList.contacts))

        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def get_contact_lists_for_campaign(
        self,
        db: AsyncSession,
        campaign_id: int
    ) -> list[ContactList]:
        """Get all contact lists for a campaign."""
        query = select(ContactList).where(
            ContactList.campaign_id == campaign_id
        ).order_by(ContactList.created_at.desc())
        result = await db.execute(query)
        return list(result.scalars().all())

    async def update_contact_list(
        self,
        db: AsyncSession,
        list_id: int,
        list_data: ContactListUpdate
    ) -> ContactList | None:
        """Update a contact list."""
        update_data = list_data.model_dump(exclude_unset=True)
        if not update_data:
            return await self.get_contact_list(db, list_id)

        query = (
            update(ContactList)
            .where(ContactList.id == list_id)
            .values(**update_data)
            .returning(ContactList)
        )
        result = await db.execute(query)
        await db.commit()
        return result.scalar_one_or_none()

    async def delete_contact_list(
        self,
        db: AsyncSession,
        list_id: int
    ) -> bool:
        """Delete a contact list and all contacts."""
        query = delete(ContactList).where(ContactList.id == list_id)
        result = await db.execute(query)
        await db.commit()
        return result.rowcount > 0

    # ===== Contact Operations =====

    async def create_contact(
        self,
        db: AsyncSession,
        contact_data: ContactCreate
    ) -> Contact:
        """Create a new contact."""
        db_contact = Contact(**contact_data.model_dump())
        db.add(db_contact)
        await db.commit()
        await db.refresh(db_contact)

        # Update contact list statistics
        await self._update_contact_list_stats(db, contact_data.contact_list_id)

        return db_contact

    async def create_contacts_bulk(
        self,
        db: AsyncSession,
        contacts_data: list[ContactCreate]
    ) -> list[Contact]:
        """Create multiple contacts at once."""
        db_contacts = [Contact(**c.model_dump()) for c in contacts_data]
        db.add_all(db_contacts)
        await db.commit()

        # Update contact list statistics
        if contacts_data:
            await self._update_contact_list_stats(
                db,
                contacts_data[0].contact_list_id
            )

        return db_contacts

    async def get_contact(
        self,
        db: AsyncSession,
        contact_id: int
    ) -> Contact | None:
        """Get a contact by ID."""
        query = select(Contact).where(Contact.id == contact_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def get_contacts(
        self,
        db: AsyncSession,
        contact_list_id: int,
        skip: int = 0,
        limit: int = 100,
        status: ContactStatus | None = None
    ) -> list[Contact]:
        """Get contacts from a contact list."""
        query = select(Contact).where(Contact.contact_list_id == contact_list_id)

        if status:
            query = query.where(Contact.status == status)

        query = query.offset(skip).limit(limit).order_by(Contact.created_at.desc())
        result = await db.execute(query)
        return list(result.scalars().all())

    async def update_contact(
        self,
        db: AsyncSession,
        contact_id: int,
        contact_data: ContactUpdate
    ) -> Contact | None:
        """Update a contact."""
        update_data = contact_data.model_dump(exclude_unset=True)
        if not update_data:
            return await self.get_contact(db, contact_id)

        # Get contact first to know which list to update
        contact = await self.get_contact(db, contact_id)
        if not contact:
            return None

        query = (
            update(Contact)
            .where(Contact.id == contact_id)
            .values(**update_data)
            .returning(Contact)
        )
        result = await db.execute(query)
        await db.commit()

        updated_contact = result.scalar_one_or_none()

        # Update contact list statistics if status changed
        if updated_contact and "status" in update_data:
            await self._update_contact_list_stats(db, contact.contact_list_id)

        return updated_contact

    async def delete_contact(
        self,
        db: AsyncSession,
        contact_id: int
    ) -> bool:
        """Delete a contact."""
        # Get contact to update list stats
        contact = await self.get_contact(db, contact_id)
        if not contact:
            return False

        query = delete(Contact).where(Contact.id == contact_id)
        result = await db.execute(query)
        await db.commit()

        if result.rowcount > 0:
            await self._update_contact_list_stats(db, contact.contact_list_id)
            return True
        return False

    async def _update_contact_list_stats(
        self,
        db: AsyncSession,
        list_id: int
    ) -> None:
        """Update contact list statistics."""
        # Get counts
        total_query = select(func.count(Contact.id)).where(
            Contact.contact_list_id == list_id
        )
        total = (await db.execute(total_query)).scalar() or 0

        processed_query = select(func.count(Contact.id)).where(
            Contact.contact_list_id == list_id,
            Contact.status.in_([ContactStatus.COMPLETED, ContactStatus.FAILED])
        )
        processed = (await db.execute(processed_query)).scalar() or 0

        successful_query = select(func.count(Contact.id)).where(
            Contact.contact_list_id == list_id,
            Contact.status == ContactStatus.COMPLETED
        )
        successful = (await db.execute(successful_query)).scalar() or 0

        failed_query = select(func.count(Contact.id)).where(
            Contact.contact_list_id == list_id,
            Contact.status == ContactStatus.FAILED
        )
        failed = (await db.execute(failed_query)).scalar() or 0

        # Update the list
        await db.execute(
            update(ContactList)
            .where(ContactList.id == list_id)
            .values(
                total_contacts=total,
                processed_contacts=processed,
                successful_contacts=successful,
                failed_contacts=failed
            )
        )
        await db.commit()

    # ===== Call Flow Operations =====

    async def create_call_flow(
        self,
        db: AsyncSession,
        flow_data: CallFlowCreate
    ) -> CallFlow:
        """Create a new call flow."""
        db_flow = CallFlow(**flow_data.model_dump())
        db.add(db_flow)
        await db.commit()
        await db.refresh(db_flow)
        return db_flow

    async def get_call_flow(
        self,
        db: AsyncSession,
        flow_id: int
    ) -> CallFlow | None:
        """Get a call flow by ID."""
        query = select(CallFlow).where(CallFlow.id == flow_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def get_call_flows_for_campaign(
        self,
        db: AsyncSession,
        campaign_id: int,
        active_only: bool = True
    ) -> list[CallFlow]:
        """Get call flows for a campaign."""
        query = select(CallFlow).where(CallFlow.campaign_id == campaign_id)

        if active_only:
            query = query.where(CallFlow.is_active == True)

        query = query.order_by(CallFlow.version.desc())
        result = await db.execute(query)
        return list(result.scalars().all())

    async def update_call_flow(
        self,
        db: AsyncSession,
        flow_id: int,
        flow_data: CallFlowUpdate
    ) -> CallFlow | None:
        """Update a call flow."""
        update_data = flow_data.model_dump(exclude_unset=True)
        if not update_data:
            return await self.get_call_flow(db, flow_id)

        query = (
            update(CallFlow)
            .where(CallFlow.id == flow_id)
            .values(**update_data)
            .returning(CallFlow)
        )
        result = await db.execute(query)
        await db.commit()
        return result.scalar_one_or_none()

    async def delete_call_flow(
        self,
        db: AsyncSession,
        flow_id: int
    ) -> bool:
        """Delete a call flow."""
        query = delete(CallFlow).where(CallFlow.id == flow_id)
        result = await db.execute(query)
        await db.commit()
        return result.rowcount > 0

    # ===== Campaign Call Operations =====

    async def create_campaign_call(
        self,
        db: AsyncSession,
        call_data: CampaignCallCreate
    ) -> CampaignCall:
        """Create a new campaign call record."""
        db_call = CampaignCall(**call_data.model_dump())
        db.add(db_call)
        await db.commit()
        await db.refresh(db_call)
        return db_call

    async def get_campaign_call(
        self,
        db: AsyncSession,
        call_id: int
    ) -> CampaignCall | None:
        """Get a campaign call by ID."""
        query = select(CampaignCall).where(CampaignCall.id == call_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def get_campaign_calls(
        self,
        db: AsyncSession,
        campaign_id: int,
        skip: int = 0,
        limit: int = 100,
        status: CampaignCallStatus | None = None
    ) -> list[CampaignCall]:
        """Get campaign calls with optional filtering."""
        query = select(CampaignCall).where(CampaignCall.campaign_id == campaign_id)

        if status:
            query = query.where(CampaignCall.status == status)

        query = query.offset(skip).limit(limit).order_by(CampaignCall.created_at.desc())
        result = await db.execute(query)
        return list(result.scalars().all())

    async def update_campaign_call(
        self,
        db: AsyncSession,
        call_id: int,
        call_data: CampaignCallUpdate
    ) -> CampaignCall | None:
        """Update a campaign call."""
        update_data = call_data.model_dump(exclude_unset=True)
        if not update_data:
            return await self.get_campaign_call(db, call_id)

        query = (
            update(CampaignCall)
            .where(CampaignCall.id == call_id)
            .values(**update_data)
            .returning(CampaignCall)
        )
        result = await db.execute(query)
        await db.commit()
        return result.scalar_one_or_none()


# Singleton instance
_campaign_service: CampaignManagementService | None = None


def get_campaign_service() -> CampaignManagementService:
    """Get the campaign management service instance."""
    global _campaign_service
    if _campaign_service is None:
        _campaign_service = CampaignManagementService()
    return _campaign_service
