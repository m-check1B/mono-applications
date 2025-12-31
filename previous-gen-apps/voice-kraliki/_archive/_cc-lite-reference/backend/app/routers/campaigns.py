"""Campaigns router - FastAPI"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models.campaign import Campaign
from app.schemas.campaign import CampaignCreate, CampaignUpdate, CampaignResponse
from app.core.events import event_publisher
from app.core.config import settings
from app.core.logger import get_logger
# from app.services.auth_service import get_current_user

logger = get_logger(__name__)

router = APIRouter(prefix="/api/campaigns", tags=["campaigns"])


@router.get("/", response_model=list[CampaignResponse])
async def list_campaigns(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    active: bool | None = None,
    type: str | None = None,
    db: AsyncSession = Depends(get_db)
):
    """
    List campaigns with filtering

    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        active: Filter by active status
        type: Filter by campaign type
        db: Database session

    Returns:
        List of campaigns
    """
    query = select(Campaign)

    if active is not None:
        query = query.where(Campaign.active == active)
    if type:
        query = query.where(Campaign.type == type)

    query = query.offset(skip).limit(limit).order_by(Campaign.created_at.desc())

    result = await db.execute(query)
    campaigns = result.scalars().all()
    return campaigns


@router.post("/", response_model=CampaignResponse, status_code=status.HTTP_201_CREATED)
async def create_campaign(
    campaign_data: CampaignCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new campaign

    Args:
        campaign_data: Campaign creation data
        db: Database session

    Returns:
        Created campaign
    """
    from uuid import uuid4

    campaign_data_dict = campaign_data.model_dump()
    metadata = campaign_data_dict.pop("metadata", None)

    campaign = Campaign(
        id=str(uuid4()),
        **campaign_data_dict
    )

    if metadata is not None:
        campaign.metadata_payload = metadata

    db.add(campaign)
    await db.commit()
    await db.refresh(campaign)

    # Emit campaign.created event
    if getattr(settings, "ENABLE_EVENTS", False):
        try:
            await event_publisher.publish(
                event_type="campaign.created",
                data={
                    "campaign_id": campaign.id,
                    "name": campaign.name,
                    "type": campaign.type,
                    "status": "active" if campaign.active else "inactive"
                },
                organization_id=campaign.organization_id or "default",
                user_id="system"
            )
        except Exception as exc:
            logger.warning(f"Failed to publish campaign.created event: {exc}")

    return campaign


@router.get("/{campaign_id}", response_model=CampaignResponse)
async def get_campaign(
    campaign_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get campaign by ID

    Args:
        campaign_id: Campaign ID
        db: Database session

    Returns:
        Campaign details
    """
    result = await db.execute(
        select(Campaign).where(Campaign.id == campaign_id)
    )
    campaign = result.scalar_one_or_none()

    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )

    return campaign


@router.put("/{campaign_id}", response_model=CampaignResponse)
async def update_campaign(
    campaign_id: str,
    campaign_data: CampaignUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update campaign

    Args:
        campaign_id: Campaign ID
        campaign_data: Campaign update data
        db: Database session

    Returns:
        Updated campaign
    """
    result = await db.execute(
        select(Campaign).where(Campaign.id == campaign_id)
    )
    campaign = result.scalar_one_or_none()

    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )

    # Update fields
    for field, value in campaign_data.model_dump(exclude_unset=True).items():
        if field == "metadata":
            campaign.metadata_payload = value
            continue
        setattr(campaign, field, value)

    await db.commit()
    await db.refresh(campaign)

    # Emit campaign.updated event
    if getattr(settings, "ENABLE_EVENTS", False):
        try:
            await event_publisher.publish(
                event_type="campaign.updated",
                data={
                    "campaign_id": campaign.id,
                    "name": campaign.name,
                    "type": campaign.type,
                    "status": "active" if campaign.active else "inactive"
                },
                organization_id=campaign.organization_id or "default",
                user_id="system"
            )
        except Exception as exc:
            logger.warning(f"Failed to publish campaign.updated event: {exc}")

    return campaign


@router.delete("/{campaign_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_campaign(
    campaign_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete campaign

    Args:
        campaign_id: Campaign ID
        db: Database session
    """
    result = await db.execute(
        select(Campaign).where(Campaign.id == campaign_id)
    )
    campaign = result.scalar_one_or_none()

    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )

    await db.delete(campaign)
    await db.commit()
