"""Tests for campaign management system."""
from uuid import uuid4

import pytest
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.campaign import Campaign, CampaignStatus, CampaignType
from app.models.contact_list import ContactList, Contact, ContactStatus
from app.models.call_flow import CallFlow, CampaignCall, CampaignCallStatus
from app.services.campaign_management import CampaignManagementService


@pytest.fixture
def campaign_service():
    """Get campaign management service instance."""
    return CampaignManagementService()


@pytest.fixture
async def sample_campaign(db_session: AsyncSession):
    """Create a sample campaign for testing."""
    campaign = Campaign(
        name="Test Campaign",
        description="Test description",
        campaign_type=CampaignType.OUTBOUND_SALES,
        status=CampaignStatus.DRAFT,
        primary_provider="openai",
        backup_providers=["gemini"],
        routing_strategy="round_robin",
        timezone="UTC",
        max_concurrent_calls=10,
        calls_per_hour=100,
        created_by=1
    )
    db_session.add(campaign)
    await db_session.commit()
    await db_session.refresh(campaign)
    return campaign


@pytest.fixture
async def sample_contact_list(db_session: AsyncSession, sample_campaign: Campaign):
    """Create a sample contact list for testing."""
    contact_list = ContactList(
        campaign_id=sample_campaign.id,
        name="Test Contact List",
        description="Test list description",
        total_contacts=0
    )
    db_session.add(contact_list)
    await db_session.commit()
    await db_session.refresh(contact_list)
    return contact_list


# ===== Campaign Tests =====

@pytest.mark.asyncio
async def test_create_campaign(db_session: AsyncSession, campaign_service: CampaignManagementService):
    """Test creating a new campaign."""
    from app.models.campaign import CampaignCreate

    campaign_data = CampaignCreate(
        name="New Campaign",
        description="New campaign description",
        campaign_type=CampaignType.OUTBOUND_SALES,
        primary_provider="openai",
        created_by=1
    )

    campaign = await campaign_service.create_campaign(db_session, campaign_data)

    assert campaign.id is not None
    assert campaign.name == "New Campaign"
    assert campaign.status == CampaignStatus.DRAFT
    assert campaign.total_calls == 0


@pytest.mark.asyncio
async def test_get_campaign(
    db_session: AsyncSession,
    campaign_service: CampaignManagementService,
    sample_campaign: Campaign
):
    """Test retrieving a campaign by ID."""
    campaign = await campaign_service.get_campaign(db_session, sample_campaign.id)

    assert campaign is not None
    assert campaign.id == sample_campaign.id
    assert campaign.name == sample_campaign.name


@pytest.mark.asyncio
async def test_update_campaign_status(
    db_session: AsyncSession,
    campaign_service: CampaignManagementService,
    sample_campaign: Campaign
):
    """Test updating campaign status."""
    updated = await campaign_service.update_campaign_status(
        db_session,
        sample_campaign.id,
        CampaignStatus.ACTIVE
    )

    assert updated is not None
    assert updated.status == CampaignStatus.ACTIVE


@pytest.mark.asyncio
async def test_delete_campaign(
    db_session: AsyncSession,
    campaign_service: CampaignManagementService,
    sample_campaign: Campaign
):
    """Test deleting a campaign."""
    deleted = await campaign_service.delete_campaign(db_session, sample_campaign.id)

    assert deleted is True

    # Verify campaign is deleted
    campaign = await campaign_service.get_campaign(db_session, sample_campaign.id)
    assert campaign is None


@pytest.mark.asyncio
async def test_get_campaigns_with_filter(
    db_session: AsyncSession,
    campaign_service: CampaignManagementService,
    sample_campaign: Campaign
):
    """Test getting campaigns with status filter."""
    campaigns = await campaign_service.get_campaigns(
        db_session,
        status=CampaignStatus.DRAFT
    )

    assert len(campaigns) > 0
    assert all(c.status == CampaignStatus.DRAFT for c in campaigns)


# ===== Contact List Tests =====

@pytest.mark.asyncio
async def test_create_contact_list(
    db_session: AsyncSession,
    campaign_service: CampaignManagementService,
    sample_campaign: Campaign
):
    """Test creating a contact list."""
    from app.models.contact_list import ContactListCreate

    list_data = ContactListCreate(
        campaign_id=sample_campaign.id,
        name="New Contact List",
        description="Test description"
    )

    contact_list = await campaign_service.create_contact_list(db_session, list_data)

    assert contact_list.id is not None
    assert contact_list.name == "New Contact List"
    assert contact_list.campaign_id == sample_campaign.id


@pytest.mark.asyncio
async def test_get_contact_lists_for_campaign(
    db_session: AsyncSession,
    campaign_service: CampaignManagementService,
    sample_contact_list: ContactList
):
    """Test getting all contact lists for a campaign."""
    lists = await campaign_service.get_contact_lists_for_campaign(
        db_session,
        sample_contact_list.campaign_id
    )

    assert len(lists) > 0
    assert any(l.id == sample_contact_list.id for l in lists)


@pytest.mark.asyncio
async def test_delete_contact_list(
    db_session: AsyncSession,
    campaign_service: CampaignManagementService,
    sample_contact_list: ContactList
):
    """Test deleting a contact list."""
    deleted = await campaign_service.delete_contact_list(db_session, sample_contact_list.id)

    assert deleted is True

    # Verify list is deleted
    contact_list = await campaign_service.get_contact_list(db_session, sample_contact_list.id)
    assert contact_list is None


# ===== Contact Tests =====

@pytest.mark.asyncio
async def test_create_contact(
    db_session: AsyncSession,
    campaign_service: CampaignManagementService,
    sample_contact_list: ContactList
):
    """Test creating a contact."""
    from app.models.contact_list import ContactCreate

    contact_data = ContactCreate(
        contact_list_id=sample_contact_list.id,
        phone_number="+1234567890",
        first_name="John",
        last_name="Doe",
        email=f"john-{uuid.uuid4()}@example.com"
    )

    contact = await campaign_service.create_contact(db_session, contact_data)

    assert contact.id is not None
    assert contact.phone_number == "+1234567890"
    assert contact.first_name == "John"
    assert contact.status == ContactStatus.PENDING


@pytest.mark.asyncio
async def test_create_contacts_bulk(
    db_session: AsyncSession,
    campaign_service: CampaignManagementService,
    sample_contact_list: ContactList
):
    """Test bulk creating contacts."""
    from app.models.contact_list import ContactCreate

    contacts_data = [
        ContactCreate(
            contact_list_id=sample_contact_list.id,
            phone_number=f"+123456789{i}",
            first_name=f"John{i}",
            last_name="Doe"
        )
        for i in range(5)
    ]

    contacts = await campaign_service.create_contacts_bulk(db_session, contacts_data)

    assert len(contacts) == 5

    # Verify contact list stats updated
    updated_list = await campaign_service.get_contact_list(db_session, sample_contact_list.id)
    assert updated_list.total_contacts == 5


@pytest.mark.asyncio
async def test_get_contacts_with_status_filter(
    db_session: AsyncSession,
    campaign_service: CampaignManagementService,
    sample_contact_list: ContactList
):
    """Test getting contacts with status filter."""
    from app.models.contact_list import ContactCreate

    # Create a contact
    contact_data = ContactCreate(
        contact_list_id=sample_contact_list.id,
        phone_number="+1234567890",
        first_name="John",
        last_name="Doe"
    )
    await campaign_service.create_contact(db_session, contact_data)

    # Get pending contacts
    contacts = await campaign_service.get_contacts(
        db_session,
        sample_contact_list.id,
        status=ContactStatus.PENDING
    )

    assert len(contacts) > 0
    assert all(c.status == ContactStatus.PENDING for c in contacts)


@pytest.mark.asyncio
async def test_update_contact(
    db_session: AsyncSession,
    campaign_service: CampaignManagementService,
    sample_contact_list: ContactList
):
    """Test updating a contact."""
    from app.models.contact_list import ContactCreate, ContactUpdate

    # Create a contact
    contact_data = ContactCreate(
        contact_list_id=sample_contact_list.id,
        phone_number="+1234567890",
        first_name="John",
        last_name="Doe"
    )
    contact = await campaign_service.create_contact(db_session, contact_data)

    # Update contact
    update_data = ContactUpdate(
        status=ContactStatus.COMPLETED,
        disposition="interested"
    )
    updated = await campaign_service.update_contact(db_session, contact.id, update_data)

    assert updated is not None
    assert updated.status == ContactStatus.COMPLETED
    assert updated.disposition == "interested"


# ===== Call Flow Tests =====

@pytest.mark.asyncio
async def test_create_call_flow(
    db_session: AsyncSession,
    campaign_service: CampaignManagementService,
    sample_campaign: Campaign
):
    """Test creating a call flow."""
    from app.models.call_flow import CallFlowCreate

    flow_data = CallFlowCreate(
        campaign_id=sample_campaign.id,
        name="Test Flow",
        description="Test flow description",
        flow_definition={
            "nodes": [
                {"id": "start", "type": "start", "next": "greeting"},
                {"id": "greeting", "type": "speak", "text": "Hello", "next": "end"},
                {"id": "end", "type": "end"}
            ]
        }
    )

    call_flow = await campaign_service.create_call_flow(db_session, flow_data)

    assert call_flow.id is not None
    assert call_flow.name == "Test Flow"
    assert call_flow.is_active is True
    assert "nodes" in call_flow.flow_definition


@pytest.mark.asyncio
async def test_get_call_flows_for_campaign(
    db_session: AsyncSession,
    campaign_service: CampaignManagementService,
    sample_campaign: Campaign
):
    """Test getting call flows for a campaign."""
    from app.models.call_flow import CallFlowCreate

    # Create a call flow
    flow_data = CallFlowCreate(
        campaign_id=sample_campaign.id,
        name="Test Flow",
        flow_definition={"nodes": []}
    )
    await campaign_service.create_call_flow(db_session, flow_data)

    # Get flows
    flows = await campaign_service.get_call_flows_for_campaign(
        db_session,
        sample_campaign.id
    )

    assert len(flows) > 0
    assert all(f.campaign_id == sample_campaign.id for f in flows)


# ===== Campaign Call Tests =====

@pytest.mark.asyncio
async def test_create_campaign_call(
    db_session: AsyncSession,
    campaign_service: CampaignManagementService,
    sample_campaign: Campaign,
    sample_contact_list: ContactList
):
    """Test creating a campaign call record."""
    from app.models.contact_list import ContactCreate
    from app.models.call_flow import CampaignCallCreate

    # Create a contact
    contact_data = ContactCreate(
        contact_list_id=sample_contact_list.id,
        phone_number="+1234567890",
        first_name="John",
        last_name="Doe"
    )
    contact = await campaign_service.create_contact(db_session, contact_data)

    # Create campaign call
    call_data = CampaignCallCreate(
        campaign_id=sample_campaign.id,
        contact_id=contact.id
    )
    campaign_call = await campaign_service.create_campaign_call(db_session, call_data)

    assert campaign_call.id is not None
    assert campaign_call.campaign_id == sample_campaign.id
    assert campaign_call.contact_id == contact.id
    assert campaign_call.status == CampaignCallStatus.SCHEDULED


@pytest.mark.asyncio
async def test_get_campaign_metrics(
    db_session: AsyncSession,
    campaign_service: CampaignManagementService,
    sample_campaign: Campaign,
    sample_contact_list: ContactList
):
    """Test getting campaign metrics."""
    from app.models.contact_list import ContactCreate

    # Create some contacts
    for i in range(3):
        contact_data = ContactCreate(
            contact_list_id=sample_contact_list.id,
            phone_number=f"+123456789{i}",
            first_name=f"John{i}",
            last_name="Doe"
        )
        await campaign_service.create_contact(db_session, contact_data)

    # Get metrics
    metrics = await campaign_service.get_campaign_metrics(db_session, sample_campaign.id)

    assert metrics is not None
    assert metrics["campaign_id"] == sample_campaign.id
    assert metrics["total_contacts"] == 3
    assert "contact_status_breakdown" in metrics
    assert "total_calls" in metrics


@pytest.mark.asyncio
async def test_contact_list_stats_update(
    db_session: AsyncSession,
    campaign_service: CampaignManagementService,
    sample_contact_list: ContactList
):
    """Test that contact list statistics are updated automatically."""
    from app.models.contact_list import ContactCreate, ContactUpdate

    # Create contacts
    for i in range(5):
        contact_data = ContactCreate(
            contact_list_id=sample_contact_list.id,
            phone_number=f"+123456789{i}",
            first_name=f"John{i}",
            last_name="Doe"
        )
        await campaign_service.create_contact(db_session, contact_data)

    # Get updated list
    updated_list = await campaign_service.get_contact_list(db_session, sample_contact_list.id)
    assert updated_list.total_contacts == 5
    assert updated_list.processed_contacts == 0

    # Update some contacts to completed
    contacts = await campaign_service.get_contacts(db_session, sample_contact_list.id)
    for contact in contacts[:2]:
        update_data = ContactUpdate(status=ContactStatus.COMPLETED)
        await campaign_service.update_contact(db_session, contact.id, update_data)

    # Check stats again
    updated_list = await campaign_service.get_contact_list(db_session, sample_contact_list.id)
    assert updated_list.processed_contacts == 2
    assert updated_list.successful_contacts == 2
