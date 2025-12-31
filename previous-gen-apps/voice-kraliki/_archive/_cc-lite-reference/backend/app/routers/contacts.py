"""Contacts router - FastAPI endpoints for contact management"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from uuid import uuid4
from typing import Optional
import csv
import io

from app.core.database import get_db
from app.core.logger import get_logger
from app.core.events import event_publisher
from app.core.config import settings
from app.models.contact import Contact, ContactStatus
from app.models.campaign import Campaign
from app.models.user import User
from app.schemas.contact import (
    ContactCreate,
    ContactUpdate,
    ContactResponse,
    ContactListResponse,
    BulkImportResponse
)
from app.dependencies import get_current_user, require_supervisor

logger = get_logger(__name__)

router = APIRouter(prefix="/api/contacts", tags=["contacts"])


@router.get("/", response_model=ContactListResponse)
async def list_contacts(
    campaign_id: Optional[str] = None,
    status: Optional[ContactStatus] = None,
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List contacts with filtering

    Args:
        campaign_id: Filter by campaign
        status: Filter by status
        skip: Offset for pagination
        limit: Number of contacts to return
        db: Database session
        current_user: Authenticated user

    Returns:
        List of contacts with pagination info
    """
    # Build query
    query = select(Contact)

    # Filter by campaign if specified
    if campaign_id:
        # Verify campaign belongs to user's organization
        campaign_result = await db.execute(
            select(Campaign).where(
                Campaign.id == campaign_id,
                Campaign.organization_id == current_user.organization_id
            )
        )
        campaign = campaign_result.scalar_one_or_none()
        if not campaign:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campaign not found"
            )
        query = query.where(Contact.campaign_id == campaign_id)
    else:
        # Get all campaigns for user's organization
        campaigns_result = await db.execute(
            select(Campaign.id).where(
                Campaign.organization_id == current_user.organization_id
            )
        )
        campaign_ids = [row[0] for row in campaigns_result.fetchall()]
        query = query.where(Contact.campaign_id.in_(campaign_ids))

    # Filter by status
    if status:
        query = query.where(Contact.status == status)

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Get paginated results
    query = query.offset(skip).limit(limit).order_by(Contact.created_at.desc())
    result = await db.execute(query)
    contacts = result.scalars().all()

    return {
        "contacts": contacts,
        "total": total,
        "skip": skip,
        "limit": limit
    }


@router.get("/{contact_id}", response_model=ContactResponse)
async def get_contact(
    contact_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get contact by ID

    Args:
        contact_id: Contact ID
        db: Database session
        current_user: Authenticated user

    Returns:
        Contact details
    """
    # Get contact
    result = await db.execute(
        select(Contact).where(Contact.id == contact_id)
    )
    contact = result.scalar_one_or_none()

    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found"
        )

    # Verify campaign belongs to user's organization
    campaign_result = await db.execute(
        select(Campaign).where(
            Campaign.id == contact.campaign_id,
            Campaign.organization_id == current_user.organization_id
        )
    )
    if not campaign_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    return contact


@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(
    contact_data: ContactCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new contact

    Args:
        contact_data: Contact creation data
        db: Database session
        current_user: Authenticated user

    Returns:
        Created contact
    """
    # Verify campaign exists and belongs to user's organization
    campaign_result = await db.execute(
        select(Campaign).where(
            Campaign.id == contact_data.campaign_id,
            Campaign.organization_id == current_user.organization_id
        )
    )
    campaign = campaign_result.scalar_one_or_none()

    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )

    # Create contact
    contact = Contact(
        id=str(uuid4()),
        campaign_id=contact_data.campaign_id,
        phone_number=contact_data.phone_number,
        name=contact_data.name,
        email=contact_data.email,
        notes=contact_data.notes,
        extra_metadata=contact_data.extra_metadata
    )

    db.add(contact)
    await db.commit()
    await db.refresh(contact)

    logger.info(f"Contact created: {contact.id} for campaign {campaign.id}")

    # Emit contact.created event
    if getattr(settings, "ENABLE_EVENTS", False):
        try:
            await event_publisher.publish(
                event_type="contact.created",
                data={
                    "contact_id": contact.id,
                    "campaign_id": contact.campaign_id,
                    "phone_number": contact.phone_number,
                    "name": contact.name
                },
                organization_id=current_user.organization_id,
                user_id=current_user.id
            )
        except Exception as exc:
            logger.warning(f"Failed to publish contact.created event: {exc}")

    return contact


@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(
    contact_id: str,
    contact_data: ContactUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update contact

    Args:
        contact_id: Contact ID
        contact_data: Update data
        db: Database session
        current_user: Authenticated user

    Returns:
        Updated contact
    """
    # Get contact
    result = await db.execute(
        select(Contact).where(Contact.id == contact_id)
    )
    contact = result.scalar_one_or_none()

    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found"
        )

    # Verify access
    campaign_result = await db.execute(
        select(Campaign).where(
            Campaign.id == contact.campaign_id,
            Campaign.organization_id == current_user.organization_id
        )
    )
    if not campaign_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    # Update fields
    for field, value in contact_data.model_dump(exclude_unset=True).items():
        setattr(contact, field, value)

    await db.commit()
    await db.refresh(contact)

    return contact


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(
    contact_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_supervisor)
):
    """
    Delete contact

    Args:
        contact_id: Contact ID
        db: Database session
        current_user: Authenticated user (must be supervisor or admin)
    """
    # Get contact
    result = await db.execute(
        select(Contact).where(Contact.id == contact_id)
    )
    contact = result.scalar_one_or_none()

    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found"
        )

    # Verify access
    campaign_result = await db.execute(
        select(Campaign).where(
            Campaign.id == contact.campaign_id,
            Campaign.organization_id == current_user.organization_id
        )
    )
    if not campaign_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    await db.delete(contact)
    await db.commit()


@router.post("/bulk-import", response_model=BulkImportResponse)
async def bulk_import_contacts(
    campaign_id: str,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_supervisor)
):
    """
    Bulk import contacts from CSV file

    CSV Format: phone_number, name, email, notes

    Args:
        campaign_id: Campaign ID
        file: CSV file upload
        db: Database session
        current_user: Authenticated user (must be supervisor or admin)

    Returns:
        Import statistics
    """
    # Verify campaign
    campaign_result = await db.execute(
        select(Campaign).where(
            Campaign.id == campaign_id,
            Campaign.organization_id == current_user.organization_id
        )
    )
    campaign = campaign_result.scalar_one_or_none()

    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )

    # Read CSV file
    contents = await file.read()
    csv_data = io.StringIO(contents.decode('utf-8'))
    reader = csv.DictReader(csv_data)

    imported = 0
    failed = 0
    errors = []

    for row in reader:
        try:
            # Create contact from row
            contact = Contact(
                id=str(uuid4()),
                campaign_id=campaign_id,
                phone_number=row.get('phone_number', '').strip(),
                name=row.get('name', '').strip() or None,
                email=row.get('email', '').strip() or None,
                notes=row.get('notes', '').strip() or None
            )

            if not contact.phone_number:
                failed += 1
                errors.append(f"Row missing phone_number: {row}")
                continue

            db.add(contact)
            imported += 1

        except Exception as e:
            failed += 1
            errors.append(f"Error importing row {row}: {str(e)}")

    await db.commit()

    logger.info(f"Bulk import completed: {imported} imported, {failed} failed for campaign {campaign_id}")

    return {
        "imported": imported,
        "failed": failed,
        "total": imported + failed,
        "errors": errors[:10]  # Return first 10 errors
    }
