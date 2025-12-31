"""
API endpoints for campaign script management.
"""

from typing import Any

from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel

from app.middleware.rate_limit import (
    API_RATE_LIMIT,
    WRITE_OPERATION_RATE_LIMIT,
    limiter,
)

router = APIRouter(prefix="/api/campaign-scripts", tags=["campaign-scripts"])


class CampaignScriptResponse(BaseModel):
    """Simple response model for campaign scripts."""
    id: int
    title: str
    description: str | None = None
    campaign_data: dict[str, Any]
    version: int
    language: str
    company_id: int
    status: str
    is_template: bool
    tags: list[str]
    usage_count: int
    success_rate: float | None = None


class CampaignScriptCreate(BaseModel):
    """Request model for creating campaign scripts."""
    title: str
    description: str | None = None
    campaign_data: dict[str, Any]
    language: str = "en"
    company_id: int
    is_template: bool = False
    tags: list[str] = []


class CampaignScriptUpdate(BaseModel):
    """Request model for updating campaign scripts."""
    title: str | None = None
    description: str | None = None
    campaign_data: dict[str, Any] | None = None
    language: str | None = None
    status: str | None = None
    is_template: bool | None = None
    tags: list[str] | None = None


# Mock data storage
scripts_db = {
    1: CampaignScriptResponse(
        id=1,
        title="Insurance Sales Script",
        description="Script for selling insurance policies",
        campaign_data={
            "id": 1,
            "type": "outbound",
            "language": "en",
            "category": "insurance",
            "title": "Insurance Sales",
            "campaign": "insurance_sales",
            "agentPersona": {
                "name": "Insurance Agent",
                "tone": "professional",
                "humanEmulation": True,
                "recordedMessageConfirmation": "Thank you for calling",
                "vocabularyRestrictions": ["insurance", "policy", "coverage"],
                "behavioralGuidelines": {"empathy": "high"},
                "focusAndHandlingPolicy": {"priority": "sales"},
                "dispositionOptions": ["sale", "not_interested", "callback"]
            },
            "script": {
                "start": [
                    {
                        "type": "statement",
                        "content": "Hello, I'm calling from Insurance Company."
                    }
                ]
            }
        },
        version=1,
        language="en",
        company_id=1,
        status="active",
        is_template=False,
        tags=["insurance", "sales"],
        usage_count=45,
        success_rate=78.5
    ),
    2: CampaignScriptResponse(
        id=2,
        title="Customer Support Script",
        description="Script for customer support calls",
        campaign_data={
            "id": 2,
            "type": "inbound",
            "language": "en",
            "category": "support",
            "title": "Customer Support",
            "campaign": "customer_support",
            "agentPersona": {
                "name": "Support Agent",
                "tone": "helpful",
                "humanEmulation": True,
                "recordedMessageConfirmation": "How can I help you today?",
                "vocabularyRestrictions": ["support", "help", "resolve"],
                "behavioralGuidelines": {"empathy": "high"},
                "focusAndHandlingPolicy": {"priority": "resolution"},
                "dispositionOptions": ["resolved", "escalated", "callback"]
            },
            "script": {
                "start": [
                    {
                        "type": "statement",
                        "content": "Thank you for calling support. How can I help you?"
                    }
                ]
            }
        },
        version=1,
        language="en",
        company_id=1,
        status="active",
        is_template=False,
        tags=["support", "customer_service"],
        usage_count=120,
        success_rate=92.3
    )
}


@router.get("/", response_model=list[CampaignScriptResponse])
async def get_scripts(
    company_id: int | None = Query(None),
    language: str | None = Query(None),
    status: str | None = Query(None),
    is_template: bool | None = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """Get campaign scripts with filtering."""
    scripts = list(scripts_db.values())

    # Apply filters
    if company_id:
        scripts = [s for s in scripts if s.company_id == company_id]
    if language:
        scripts = [s for s in scripts if s.language == language]
    if status:
        scripts = [s for s in scripts if s.status == status]
    if is_template is not None:
        scripts = [s for s in scripts if s.is_template == is_template]

    return scripts[offset:offset + limit]


@limiter.limit(API_RATE_LIMIT)
@router.get("/{script_id}", response_model=CampaignScriptResponse)
async def get_script(request: Request, script_id: int):
    """Get a specific campaign script."""
    if script_id not in scripts_db:
        raise HTTPException(status_code=404, detail="Script not found")

    return scripts_db[script_id]


@limiter.limit(WRITE_OPERATION_RATE_LIMIT)
@router.post("/", response_model=CampaignScriptResponse)
async def create_script(request: Request, script_data: CampaignScriptCreate):
    """Create a new campaign script."""
    new_id = max(scripts_db.keys()) + 1 if scripts_db else 1

    new_script = CampaignScriptResponse(
        id=new_id,
        title=script_data.title,
        description=script_data.description,
        campaign_data=script_data.campaign_data,
        version=1,
        language=script_data.language,
        company_id=script_data.company_id,
        status="draft",
        is_template=script_data.is_template,
        tags=script_data.tags,
        usage_count=0,
        success_rate=None
    )

    scripts_db[new_id] = new_script
    return new_script


@limiter.limit(API_RATE_LIMIT)
@router.put("/{script_id}", response_model=CampaignScriptResponse)
async def update_script(request: Request, script_id: int, script_data: CampaignScriptUpdate):
    """Update a campaign script."""
    if script_id not in scripts_db:
        raise HTTPException(status_code=404, detail="Script not found")

    script = scripts_db[script_id]

    # Update fields
    if script_data.title is not None:
        script.title = script_data.title
    if script_data.description is not None:
        script.description = script_data.description
    if script_data.campaign_data is not None:
        script.campaign_data = script_data.campaign_data
    if script_data.language is not None:
        script.language = script_data.language
    if script_data.status is not None:
        script.status = script_data.status
    if script_data.is_template is not None:
        script.is_template = script_data.is_template
    if script_data.tags is not None:
        script.tags = script_data.tags

    script.version += 1

    return script


@limiter.limit(WRITE_OPERATION_RATE_LIMIT)
@router.delete("/{script_id}")
async def delete_script(request: Request, script_id: int):
    """Delete a campaign script."""
    if script_id not in scripts_db:
        raise HTTPException(status_code=404, detail="Script not found")

    del scripts_db[script_id]
    return {"message": "Script deleted successfully"}


@limiter.limit(API_RATE_LIMIT)
@router.get("/templates/", response_model=list[CampaignScriptResponse])
async def get_script_templates(request: Request):
    """Get available script templates."""
    templates = [s for s in scripts_db.values() if s.is_template]
    return templates


@limiter.limit(WRITE_OPERATION_RATE_LIMIT)
@router.post("/{script_id}/duplicate", response_model=CampaignScriptResponse)
async def duplicate_script(request: Request, script_id: int):
    """Duplicate a campaign script."""
    if script_id not in scripts_db:
        raise HTTPException(status_code=404, detail="Script not found")

    original = scripts_db[script_id]
    new_id = max(scripts_db.keys()) + 1 if scripts_db else 1

    duplicated_script = CampaignScriptResponse(
        id=new_id,
        title=f"{original.title} (Copy)",
        description=original.description,
        campaign_data=original.campaign_data.copy(),
        version=1,
        language=original.language,
        company_id=original.company_id,
        status="draft",
        is_template=False,
        tags=original.tags.copy(),
        usage_count=0,
        success_rate=None
    )

    scripts_db[new_id] = duplicated_script
    return duplicated_script
