from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from anthropic import Anthropic
from app.core.database import get_db
from app.core.security import get_current_user, generate_id
from app.core.config import settings
from app.models.user import User
from app.models.workflow_template import WorkflowTemplate
from app.models.task import Task, TaskStatus
from app.schemas.workflow import (
    WorkflowTemplateCreate,
    WorkflowTemplateUpdate,
    WorkflowTemplateResponse,
    WorkflowExecuteRequest,
    WorkflowExecuteResponse,
    WorkflowListResponse
)
from datetime import datetime, timedelta
from typing import List, Optional
import json
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/workflow", tags=["workflow"])

# Lazy initialization for Anthropic client
_anthropic_client = None

def get_anthropic_client():
    global _anthropic_client
    if _anthropic_client is None:
        _anthropic_client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    return _anthropic_client


@router.post("/templates", response_model=WorkflowTemplateResponse)
async def create_workflow_template(
    request: WorkflowTemplateCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new workflow template"""
    # Calculate total estimated time
    total_minutes = sum(step.get("estimatedMinutes", 0) for step in request.steps)

    template = WorkflowTemplate(
        id=generate_id(),
        userId=current_user.id if not request.isSystem else None,
        name=request.name,
        description=request.description,
        category=request.category,
        icon=request.icon,
        steps=request.steps,
        totalEstimatedMinutes=total_minutes,
        tags=request.tags,
        isPublic=request.isPublic,
        isSystem=request.isSystem,
        createdAt=datetime.utcnow()
    )

    db.add(template)
    db.commit()
    db.refresh(template)

    return WorkflowTemplateResponse(
        id=template.id,
        userId=template.userId,
        name=template.name,
        description=template.description,
        category=template.category,
        icon=template.icon,
        steps=template.steps,
        totalEstimatedMinutes=template.totalEstimatedMinutes,
        tags=template.tags,
        isPublic=template.isPublic,
        isSystem=template.isSystem,
        usageCount=template.usageCount,
        createdAt=template.createdAt
    )


@router.get("/templates", response_model=WorkflowListResponse)
async def list_workflow_templates(
    category: Optional[str] = None,
    include_system: bool = True,
    include_public: bool = True,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List available workflow templates"""
    query = db.query(WorkflowTemplate)

    # Build filter conditions
    conditions = []

    # User's own templates
    conditions.append(WorkflowTemplate.userId == current_user.id)

    # System templates
    if include_system:
        conditions.append(WorkflowTemplate.isSystem == True)

    # Public templates
    if include_public:
        conditions.append(WorkflowTemplate.isPublic == True)

    # Combine with OR
    from sqlalchemy import or_
    query = query.filter(or_(*conditions))

    # Filter by category
    if category:
        query = query.filter(WorkflowTemplate.category == category)

    templates = query.order_by(WorkflowTemplate.usageCount.desc()).all()

    return WorkflowListResponse(
        templates=[
            WorkflowTemplateResponse(
                id=t.id,
                userId=t.userId,
                name=t.name,
                description=t.description,
                category=t.category,
                icon=t.icon,
                steps=t.steps,
                totalEstimatedMinutes=t.totalEstimatedMinutes,
                tags=t.tags,
                isPublic=t.isPublic,
                isSystem=t.isSystem,
                usageCount=t.usageCount,
                createdAt=t.createdAt
            )
            for t in templates
        ],
        total=len(templates)
    )


@router.get("/templates/{template_id}", response_model=WorkflowTemplateResponse)
async def get_workflow_template(
    template_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific workflow template"""
    template = db.query(WorkflowTemplate).filter(
        WorkflowTemplate.id == template_id
    ).first()

    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    # Check access
    if (template.userId != current_user.id and
        not template.isPublic and
        not template.isSystem):
        raise HTTPException(status_code=403, detail="Access denied")

    return WorkflowTemplateResponse(
        id=template.id,
        userId=template.userId,
        name=template.name,
        description=template.description,
        category=template.category,
        icon=template.icon,
        steps=template.steps,
        totalEstimatedMinutes=template.totalEstimatedMinutes,
        tags=template.tags,
        isPublic=template.isPublic,
        isSystem=template.isSystem,
        usageCount=template.usageCount,
        createdAt=template.createdAt
    )


@router.put("/templates/{template_id}", response_model=WorkflowTemplateResponse)
async def update_workflow_template(
    template_id: str,
    request: WorkflowTemplateUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a workflow template"""
    template = db.query(WorkflowTemplate).filter(
        WorkflowTemplate.id == template_id,
        WorkflowTemplate.userId == current_user.id
    ).first()

    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    # Update fields
    if request.name is not None:
        template.name = request.name
    if request.description is not None:
        template.description = request.description
    if request.category is not None:
        template.category = request.category
    if request.icon is not None:
        template.icon = request.icon
    if request.steps is not None:
        template.steps = request.steps
        template.totalEstimatedMinutes = sum(step.get("estimatedMinutes", 0) for step in request.steps)
    if request.tags is not None:
        template.tags = request.tags
    if request.isPublic is not None:
        template.isPublic = request.isPublic

    template.updatedAt = datetime.utcnow()

    db.commit()
    db.refresh(template)

    return WorkflowTemplateResponse(
        id=template.id,
        userId=template.userId,
        name=template.name,
        description=template.description,
        category=template.category,
        icon=template.icon,
        steps=template.steps,
        totalEstimatedMinutes=template.totalEstimatedMinutes,
        tags=template.tags,
        isPublic=template.isPublic,
        isSystem=template.isSystem,
        usageCount=template.usageCount,
        createdAt=template.createdAt
    )


@router.delete("/templates/{template_id}")
async def delete_workflow_template(
    template_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a workflow template"""
    template = db.query(WorkflowTemplate).filter(
        WorkflowTemplate.id == template_id,
        WorkflowTemplate.userId == current_user.id
    ).first()

    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    db.delete(template)
    db.commit()

    return {"success": True, "message": "Template deleted"}


@router.post("/execute", response_model=WorkflowExecuteResponse)
async def execute_workflow(
    request: WorkflowExecuteRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Execute a workflow template and create tasks"""
    # Get template
    template = db.query(WorkflowTemplate).filter(
        WorkflowTemplate.id == request.templateId
    ).first()

    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    # Check access
    if (template.userId != current_user.id and
        not template.isPublic and
        not template.isSystem):
        raise HTTPException(status_code=403, detail="Access denied")

    # Increment usage count
    template.usageCount += 1

    # Create parent task
    parent_task = Task(
        id=generate_id(),
        userId=current_user.id,
        title=request.customTitle or template.name,
        description=template.description,
        priority=request.priority or 2,
        status=TaskStatus.PENDING,
        tags=template.tags + request.additionalTags,
        estimatedMinutes=template.totalEstimatedMinutes,
        createdAt=datetime.utcnow()
    )

    if request.startDate:
        parent_task.dueDate = datetime.fromisoformat(request.startDate.replace("Z", "+00:00"))

    db.add(parent_task)

    # Create subtasks from workflow steps
    created_tasks = []
    current_date = request.startDate

    for step in template.steps:
        subtask = Task(
            id=generate_id(),
            userId=current_user.id,
            parentTaskId=parent_task.id,
            title=step.get("action", f"Step {step.get('step')}"),
            description=f"Workflow step {step.get('step')}",
            priority=request.priority or 2,
            status=TaskStatus.PENDING,
            estimatedMinutes=step.get("estimatedMinutes", 30),
            tags=[f"workflow:{template.name}"],
            createdAt=datetime.utcnow()
        )

        # Set due dates if start date provided
        if current_date:
            try:
                date = datetime.fromisoformat(current_date.replace("Z", "+00:00"))
                subtask.dueDate = date
                # Increment by estimated time for next task
                minutes = step.get("estimatedMinutes", 30)
                current_date = (date + timedelta(minutes=minutes)).isoformat()
            except (ValueError, TypeError) as e:
                # Log date parse error but continue with subtask creation
                logger.warning(f"Failed to parse date '{current_date}': {e}")

        db.add(subtask)
        created_tasks.append({
            "id": subtask.id,
            "title": subtask.title,
            "step": step.get("step"),
            "estimatedMinutes": subtask.estimatedMinutes
        })

    db.commit()

    return WorkflowExecuteResponse(
        success=True,
        message=f"Workflow '{template.name}' executed successfully",
        parentTaskId=parent_task.id,
        createdTasks=created_tasks,
        totalTasks=len(created_tasks)
    )


@router.post("/generate", response_model=WorkflowTemplateResponse)
async def generate_workflow_from_description(
    description: str,
    category: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate a workflow template from natural language description using AI"""
    try:
        prompt = f"""Create a detailed workflow template from this description:

Description: "{description}"
Category: {category or "general"}

Generate a JSON workflow template with:
1. name: Clear, concise workflow name
2. description: Brief description
3. category: The workflow category
4. steps: Array of workflow steps with:
   - step: step number
   - action: Clear action description
   - estimatedMinutes: Time estimate
   - dependencies: Array of step numbers this depends on
   - type: "manual" or "automated"

Example output:
{{
  "name": "Blog Post Creation",
  "description": "Complete workflow for creating a blog post",
  "category": "content",
  "steps": [
    {{"step": 1, "action": "Research topic and gather sources", "estimatedMinutes": 30, "dependencies": [], "type": "manual"}},
    {{"step": 2, "action": "Create outline", "estimatedMinutes": 15, "dependencies": [1], "type": "manual"}},
    {{"step": 3, "action": "Write first draft", "estimatedMinutes": 60, "dependencies": [2], "type": "manual"}}
  ],
  "tags": ["writing", "content", "blog"]
}}

Return ONLY valid JSON."""

        response = get_anthropic_client().messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )

        result = json.loads(response.content[0].text)

        # Calculate total time
        total_minutes = sum(step.get("estimatedMinutes", 0) for step in result["steps"])

        # Create template
        template = WorkflowTemplate(
            id=generate_id(),
            userId=current_user.id,
            name=result.get("name", description[:100]),
            description=result.get("description"),
            category=result.get("category", category),
            steps=result["steps"],
            totalEstimatedMinutes=total_minutes,
            tags=result.get("tags", []),
            isPublic=False,
            isSystem=False,
            createdAt=datetime.utcnow()
        )

        db.add(template)
        db.commit()
        db.refresh(template)

        return WorkflowTemplateResponse(
            id=template.id,
            userId=template.userId,
            name=template.name,
            description=template.description,
            category=template.category,
            icon=template.icon,
            steps=template.steps,
            totalEstimatedMinutes=template.totalEstimatedMinutes,
            tags=template.tags,
            isPublic=template.isPublic,
            isSystem=template.isSystem,
            usageCount=template.usageCount,
            createdAt=template.createdAt
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Workflow generation failed: {str(e)}")


@router.get("/categories")
async def get_workflow_categories(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get list of workflow categories"""
    # Get unique categories
    from sqlalchemy import distinct
    categories = db.query(distinct(WorkflowTemplate.category)).filter(
        (WorkflowTemplate.userId == current_user.id) |
        (WorkflowTemplate.isPublic == True) |
        (WorkflowTemplate.isSystem == True)
    ).all()

    return {
        "categories": [cat[0] for cat in categories if cat[0]],
        "default_categories": [
            "productivity",
            "development",
            "content",
            "planning",
            "learning",
            "health",
            "business"
        ]
    }
