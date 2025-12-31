"""
Brain API Router - Central AI Intelligence for Focus

The Brain helps humans:
- Understand and break down goals
- Get daily planning recommendations
- Ask questions about their work
- Get AI-powered suggestions

This is the main AI interface for Focus by Kraliki.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, Dict, Any

from app.core.database import get_db
from app.routers.auth import get_current_user
from app.models.user import User
from app.services.brain import FocusBrain

router = APIRouter(prefix="/brain", tags=["brain"])


class GoalRequest(BaseModel):
    """Request to parse a natural language goal."""
    goal: str
    create_project: bool = False  # If True, create project and tasks


class AskRequest(BaseModel):
    """Request to ask the Brain anything."""
    question: str
    context: Optional[Dict[str, Any]] = None


class CaptureRequest(BaseModel):
    """Request to capture any input (AI auto-categorizes)."""
    input: str
    create: bool = False  # If True, create the item. If False, just classify.


class BrainResponse(BaseModel):
    """Standard Brain response."""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None


@router.post("/understand-goal", response_model=BrainResponse)
async def understand_goal(
    request: GoalRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Parse a natural language goal and optionally create project/tasks.

    Example:
        POST /brain/understand-goal
        {"goal": "Launch my SaaS by March 2026", "create_project": true}

    Returns:
        Parsed goal with suggested project and tasks.
        If create_project=true, actually creates them.
    """
    brain = FocusBrain(current_user, db)

    # Parse the goal
    result = await brain.understand_goal(request.goal)

    if not result.get("success"):
        return BrainResponse(
            success=False,
            message=result.get("message", "Failed to parse goal"),
            data=result
        )

    # Optionally create project and tasks
    if request.create_project and result.get("parsed"):
        create_result = await brain.create_from_goal(result["parsed"])
        result["created"] = create_result

    return BrainResponse(
        success=True,
        message=result.get("message", "Goal understood"),
        data=result
    )


@router.get("/daily-plan", response_model=BrainResponse)
async def get_daily_plan(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get the daily plan: "Good morning! Here's your day..."

    Returns:
        - Greeting
        - Top 3 priority tasks
        - Overdue count
        - Due today count
        - Peak productivity hours
        - Shadow insight (if available)
    """
    brain = FocusBrain(current_user, db)
    plan = await brain.get_daily_plan()

    return BrainResponse(
        success=True,
        message=plan.get("message", "Here's your plan"),
        data=plan
    )


@router.post("/ask", response_model=BrainResponse)
async def ask_brain(
    request: AskRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Ask the Brain anything about your work.

    Examples:
        "What should I work on?"
        "Am I on track to finish my project?"
        "Help me break down this task"
        "When should I schedule deep work?"
    """
    brain = FocusBrain(current_user, db)
    result = await brain.ask(request.question, request.context)

    return BrainResponse(
        success=result.get("success", False),
        message=result.get("answer", "I couldn't process that"),
        data=result
    )


@router.get("/next-action", response_model=BrainResponse)
async def suggest_next_action(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    What should the user do RIGHT NOW?

    Returns the single most important action based on:
    - Current priorities
    - In-progress work
    - Time of day
    - User patterns
    """
    brain = FocusBrain(current_user, db)
    suggestion = await brain.suggest_next_action()

    return BrainResponse(
        success=True,
        message=suggestion.get("message", ""),
        data=suggestion
    )


@router.post("/capture", response_model=BrainResponse)
async def capture_input(
    request: CaptureRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    AI-First Capture: Say anything, Brain organizes it.

    The Brain unloads your mind so you can focus on creativity:
    - "I have an idea for a new product" → Idea
    - "Remember to call John tomorrow" → Note
    - "My goal is to launch by March" → Plan
    - "I need to fix the login bug" → Task

    Just speak or type. Brain categorizes automatically.
    """
    brain = FocusBrain(current_user, db)
    result = await brain.capture(request.input, request.create)

    return BrainResponse(
        success=result.get("success", False),
        message=result.get("message", ""),
        data=result
    )


@router.get("/summary", response_model=BrainResponse)
async def get_knowledge_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get summary of everything you've captured.

    Returns counts and recent items for each type:
    - Ideas, Notes, Tasks, Plans, custom types
    """
    brain = FocusBrain(current_user, db)
    summary = await brain.get_knowledge_summary()

    return BrainResponse(
        success=True,
        message=f"You have {summary['total_items']} items across {len(summary['types'])} types",
        data=summary
    )


@router.get("/health")
async def brain_health():
    """Check if the Brain is operational."""
    return {"status": "online", "service": "Focus Brain"}
