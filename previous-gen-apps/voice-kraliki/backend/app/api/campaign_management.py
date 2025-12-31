"""Campaign management API endpoints."""

import csv
import io

from fastapi import APIRouter, Depends, File, HTTPException, Query, Request, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.jwt_auth import require_user
from app.database import get_db
from app.middleware.rate_limit import BULK_OPERATION_RATE_LIMIT, WRITE_OPERATION_RATE_LIMIT, limiter
from app.models.call_flow import (
    CallFlowCreate,
    CallFlowResponse,
    CallFlowUpdate,
    CampaignCallCreate,
    CampaignCallResponse,
    CampaignCallStatus,
    CampaignCallUpdate,
)
from app.models.campaign import (
    CampaignCreate,
    CampaignResponse,
    CampaignStatus,
    CampaignUpdate,
)
from app.models.contact_list import (
    ContactBulkCreate,
    ContactCreate,
    ContactImportResult,
    ContactListCreate,
    ContactListResponse,
    ContactListUpdate,
    ContactResponse,
    ContactStatus,
    ContactUpdate,
)
from app.models.user import User
from app.services.campaign_management import get_campaign_service
from app.services.campaign_scheduler import get_campaign_scheduler, run_scheduler_checks

router = APIRouter(prefix="/campaign-management", tags=["Campaign Management"])


# ===== Campaign Endpoints =====


@router.post("/campaigns", response_model=CampaignResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit(WRITE_OPERATION_RATE_LIMIT)
async def create_campaign(
    request: Request,
    campaign_data: CampaignCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_user),
):
    """Create a new campaign. Rate limited to prevent abuse."""
    service = get_campaign_service()
    campaign = await service.create_campaign(db, campaign_data)
    return campaign


@router.get("/campaigns", response_model=list[CampaignResponse])
async def list_campaigns(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    status: CampaignStatus | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_user),
):
    """Get all campaigns with optional filtering."""
    service = get_campaign_service()
    campaigns = await service.get_campaigns(
        db, skip=skip, limit=limit, status=status, created_by=current_user.id
    )
    return campaigns


@router.get("/campaigns/{campaign_id}", response_model=CampaignResponse)
async def get_campaign(
    campaign_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(require_user)
):
    """Get a specific campaign by ID."""
    service = get_campaign_service()
    campaign = await service.get_campaign(db, campaign_id)

    if not campaign:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found")

    return campaign


@router.put("/campaigns/{campaign_id}", response_model=CampaignResponse)
@limiter.limit(WRITE_OPERATION_RATE_LIMIT)
async def update_campaign(
    request: Request,
    campaign_id: int,
    campaign_data: CampaignUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_user),
):
    """Update a campaign. Rate limited to prevent abuse."""
    service = get_campaign_service()
    campaign = await service.update_campaign(db, campaign_id, campaign_data)

    if not campaign:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found")

    return campaign


@router.delete("/campaigns/{campaign_id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit(WRITE_OPERATION_RATE_LIMIT)
async def delete_campaign(
    request: Request,
    campaign_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_user),
):
    """Delete a campaign. Rate limited to prevent abuse."""
    service = get_campaign_service()
    deleted = await service.delete_campaign(db, campaign_id)

    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found")


@router.post("/campaigns/{campaign_id}/start", response_model=CampaignResponse)
@limiter.limit(WRITE_OPERATION_RATE_LIMIT)
async def start_campaign(
    request: Request,
    campaign_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_user),
):
    """Start a campaign. Rate limited to prevent abuse."""
    service = get_campaign_service()
    campaign = await service.update_campaign_status(db, campaign_id, CampaignStatus.ACTIVE)

    if not campaign:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found")

    return campaign


@router.post("/campaigns/{campaign_id}/pause", response_model=CampaignResponse)
@limiter.limit(WRITE_OPERATION_RATE_LIMIT)
async def pause_campaign(
    request: Request,
    campaign_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_user),
):
    """Pause a campaign. Rate limited to prevent abuse."""
    service = get_campaign_service()
    campaign = await service.update_campaign_status(db, campaign_id, CampaignStatus.PAUSED)

    if not campaign:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found")

    return campaign


@router.post("/campaigns/{campaign_id}/complete", response_model=CampaignResponse)
@limiter.limit(WRITE_OPERATION_RATE_LIMIT)
async def complete_campaign(
    request: Request,
    campaign_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_user),
):
    """Mark campaign as completed. Rate limited to prevent abuse."""
    service = get_campaign_service()
    campaign = await service.update_campaign_status(db, campaign_id, CampaignStatus.COMPLETED)

    if not campaign:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found")

    return campaign


@router.get("/campaigns/{campaign_id}/metrics")
async def get_campaign_metrics(
    campaign_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(require_user)
):
    """Get aggregated metrics for a campaign."""
    service = get_campaign_service()
    metrics = await service.get_campaign_metrics(db, campaign_id)
    return metrics


# ===== Contact List Endpoints =====


@router.post(
    "/contact-lists", response_model=ContactListResponse, status_code=status.HTTP_201_CREATED
)
@limiter.limit(WRITE_OPERATION_RATE_LIMIT)
async def create_contact_list(
    request: Request,
    list_data: ContactListCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_user),
):
    """Create a new contact list. Rate limited to prevent abuse."""
    service = get_campaign_service()
    contact_list = await service.create_contact_list(db, list_data)
    return contact_list


@router.get("/campaigns/{campaign_id}/contact-lists", response_model=list[ContactListResponse])
async def list_contact_lists(
    campaign_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(require_user)
):
    """Get all contact lists for a campaign."""
    service = get_campaign_service()
    lists = await service.get_contact_lists_for_campaign(db, campaign_id)
    return lists


@router.get("/contact-lists/{list_id}", response_model=ContactListResponse)
async def get_contact_list(
    list_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(require_user)
):
    """Get a specific contact list."""
    service = get_campaign_service()
    contact_list = await service.get_contact_list(db, list_id)

    if not contact_list:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact list not found")

    return contact_list


@router.put("/contact-lists/{list_id}", response_model=ContactListResponse)
@limiter.limit(WRITE_OPERATION_RATE_LIMIT)
async def update_contact_list(
    request: Request,
    list_id: int,
    list_data: ContactListUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_user),
):
    """Update a contact list. Rate limited to prevent abuse."""
    service = get_campaign_service()
    contact_list = await service.update_contact_list(db, list_id, list_data)

    if not contact_list:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact list not found")

    return contact_list


@router.delete("/contact-lists/{list_id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit(WRITE_OPERATION_RATE_LIMIT)
async def delete_contact_list(
    request: Request,
    list_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_user),
):
    """Delete a contact list and all its contacts. Rate limited to prevent abuse."""
    service = get_campaign_service()
    deleted = await service.delete_contact_list(db, list_id)

    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact list not found")


# ===== Contact Endpoints =====


@router.post("/contacts", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit(WRITE_OPERATION_RATE_LIMIT)
async def create_contact(
    request: Request,
    contact_data: ContactCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_user),
):
    """Create a new contact. Rate limited to prevent abuse."""
    service = get_campaign_service()
    contact = await service.create_contact(db, contact_data)
    return contact


@router.post("/contacts/bulk", response_model=ContactImportResult)
@limiter.limit(BULK_OPERATION_RATE_LIMIT)
async def create_contacts_bulk(
    request: Request,
    bulk_data: ContactBulkCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_user),
):
    """Create multiple contacts at once. Rate limited to prevent abuse."""
    service = get_campaign_service()

    try:
        contacts = await service.create_contacts_bulk(db, bulk_data.contacts)
        return ContactImportResult(
            total=len(bulk_data.contacts), successful=len(contacts), failed=0, errors=[]
        )
    except Exception as e:
        return ContactImportResult(
            total=len(bulk_data.contacts),
            successful=0,
            failed=len(bulk_data.contacts),
            errors=[{"error": str(e)}],
        )


@router.post("/contact-lists/{list_id}/import-csv", response_model=ContactImportResult)
@limiter.limit(BULK_OPERATION_RATE_LIMIT)
async def import_contacts_from_csv(
    request: Request,
    list_id: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_user),
):
    """Import contacts from a CSV file. Rate limited to prevent abuse."""
    service = get_campaign_service()

    # Verify contact list exists
    contact_list = await service.get_contact_list(db, list_id)
    if not contact_list:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact list not found")

    # Read CSV file
    contents = await file.read()
    csv_data = csv.DictReader(io.StringIO(contents.decode("utf-8")))

    contacts_to_create = []
    errors = []
    row_num = 0

    for row in csv_data:
        row_num += 1
        try:
            contact = ContactCreate(
                contact_list_id=list_id,
                phone_number=row.get("phone_number", ""),
                first_name=row.get("first_name"),
                last_name=row.get("last_name"),
                email=row.get("email"),
                company=row.get("company"),
                custom_fields={
                    k: v
                    for k, v in row.items()
                    if k not in ["phone_number", "first_name", "last_name", "email", "company"]
                },
            )
            contacts_to_create.append(contact)
        except Exception as e:
            errors.append({"row": row_num, "error": str(e)})

    # Create contacts
    successful = 0
    if contacts_to_create:
        try:
            created = await service.create_contacts_bulk(db, contacts_to_create)
            successful = len(created)
        except Exception as e:
            errors.append({"error": f"Bulk insert failed: {str(e)}"})

    return ContactImportResult(
        total=row_num, successful=successful, failed=row_num - successful, errors=errors
    )


@router.get("/contact-lists/{list_id}/contacts", response_model=list[ContactResponse])
async def list_contacts(
    list_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    status: ContactStatus | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_user),
):
    """Get all contacts in a contact list."""
    service = get_campaign_service()
    contacts = await service.get_contacts(db, list_id, skip=skip, limit=limit, status=status)
    return contacts


@router.get("/contacts/{contact_id}", response_model=ContactResponse)
async def get_contact(
    contact_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(require_user)
):
    """Get a specific contact."""
    service = get_campaign_service()
    contact = await service.get_contact(db, contact_id)

    if not contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")

    return contact


@router.put("/contacts/{contact_id}", response_model=ContactResponse)
@limiter.limit(WRITE_OPERATION_RATE_LIMIT)
async def update_contact(
    request: Request,
    contact_id: int,
    contact_data: ContactUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_user),
):
    """Update a contact. Rate limited to prevent abuse."""
    service = get_campaign_service()
    contact = await service.update_contact(db, contact_id, contact_data)

    if not contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")

    return contact


@router.delete("/contacts/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit(WRITE_OPERATION_RATE_LIMIT)
async def delete_contact(
    request: Request,
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_user),
):
    """Delete a contact. Rate limited to prevent abuse."""
    service = get_campaign_service()
    deleted = await service.delete_contact(db, contact_id)

    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")


# ===== Call Flow Endpoints =====


@router.post("/call-flows", response_model=CallFlowResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit(WRITE_OPERATION_RATE_LIMIT)
async def create_call_flow(
    request: Request,
    flow_data: CallFlowCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_user),
):
    """Create a new call flow. Rate limited to prevent abuse."""
    service = get_campaign_service()
    call_flow = await service.create_call_flow(db, flow_data)
    return call_flow


@router.get("/campaigns/{campaign_id}/call-flows", response_model=list[CallFlowResponse])
async def list_call_flows(
    campaign_id: int,
    active_only: bool = True,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_user),
):
    """Get all call flows for a campaign."""
    service = get_campaign_service()
    flows = await service.get_call_flows_for_campaign(db, campaign_id, active_only=active_only)
    return flows


@router.get("/call-flows/{flow_id}", response_model=CallFlowResponse)
async def get_call_flow(
    flow_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(require_user)
):
    """Get a specific call flow."""
    service = get_campaign_service()
    call_flow = await service.get_call_flow(db, flow_id)

    if not call_flow:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Call flow not found")

    return call_flow


@router.put("/call-flows/{flow_id}", response_model=CallFlowResponse)
@limiter.limit(WRITE_OPERATION_RATE_LIMIT)
async def update_call_flow(
    request: Request,
    flow_id: int,
    flow_data: CallFlowUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_user),
):
    """Update a call flow. Rate limited to prevent abuse."""
    service = get_campaign_service()
    call_flow = await service.update_call_flow(db, flow_id, flow_data)

    if not call_flow:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Call flow not found")

    return call_flow


@router.delete("/call-flows/{flow_id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit(WRITE_OPERATION_RATE_LIMIT)
async def delete_call_flow(
    request: Request,
    flow_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_user),
):
    """Delete a call flow. Rate limited to prevent abuse."""
    service = get_campaign_service()
    deleted = await service.delete_call_flow(db, flow_id)

    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Call flow not found")


# ===== Campaign Call Endpoints =====


@router.post(
    "/campaign-calls", response_model=CampaignCallResponse, status_code=status.HTTP_201_CREATED
)
@limiter.limit(WRITE_OPERATION_RATE_LIMIT)
async def create_campaign_call(
    request: Request,
    call_data: CampaignCallCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_user),
):
    """Create a new campaign call record. Rate limited to prevent abuse."""
    service = get_campaign_service()
    campaign_call = await service.update_campaign_call(db, call_id, call_data)

    if not campaign_call:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign call not found")

    return campaign_call


# ===== Scheduler Endpoints =====


@router.post("/scheduler/check")
@limiter.limit(WRITE_OPERATION_RATE_LIMIT)
async def run_scheduler(
    request: Request, db: AsyncSession = Depends(get_db), current_user: User = Depends(require_user)
):
    """
    Manually trigger scheduler checks to start/stop campaigns.
    Useful for testing or when background scheduler isn't running.
    Rate limited to prevent abuse.
    """
    result = await run_scheduler_checks(db)
    return result


@router.get("/scheduler/status")
async def get_scheduler_status(
    db: AsyncSession = Depends(get_db), current_user: User = Depends(require_user)
):
    """
    Get scheduler status and campaign summary.
    """
    scheduler = get_campaign_scheduler()
    summary = await scheduler.get_campaign_status_summary(db)
    running = scheduler.get_running_campaigns()

    return {
        "campaign_summary": summary,
        "running_campaigns": running,
        "running_count": len(running),
    }


@router.get("/campaigns/{campaign_id}/calls", response_model=list[CampaignCallResponse])
async def list_campaign_calls(
    campaign_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    status: CampaignCallStatus | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_user),
):
    """Get all calls for a campaign."""
    service = get_campaign_service()
    calls = await service.get_campaign_calls(db, campaign_id, skip=skip, limit=limit, status=status)
    return calls


@router.get("/campaign-calls/{call_id}", response_model=CampaignCallResponse)
async def get_campaign_call(
    call_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(require_user)
):
    """Get a specific campaign call."""
    service = get_campaign_service()
    campaign_call = await service.get_campaign_call(db, call_id)

    if not campaign_call:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign call not found")

    return campaign_call


@router.put("/campaign-calls/{call_id}", response_model=CampaignCallResponse)
@limiter.limit(WRITE_OPERATION_RATE_LIMIT)
async def update_campaign_call(
    request: Request,
    call_id: int,
    call_data: CampaignCallUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_user),
):
    """Update a campaign call. Rate limited to prevent abuse."""
    service = get_campaign_service()
    campaign_call = await service.update_campaign_call(db, call_id, call_data)

    if not campaign_call:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign call not found")

    return campaign_call
