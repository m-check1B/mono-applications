"""
Onboarding router for Track 5: Persona Onboarding & Trust
Handles persona selection, privacy acknowledgment, and feature toggles
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, Dict, Any

from app.core.security import get_current_user
from app.core.database import get_db
from app.models.user import User

router = APIRouter(prefix="/onboarding", tags=["onboarding"])


# Persona definitions based on user research
PERSONA_TEMPLATES = {
    "solo-developer": {
        "id": "solo-developer",
        "name": "Solo Developer",
        "description": "Independent software developer balancing client work and side projects",
        "icon": "code",
        "features": {
            "voiceCapture": True,
            "shadowAnalysis": True,
            "githubIntegration": True,
            "naturalLanguageTasks": True,
            "dailyPlanning": True,
            "timeTracking": True,
            "ideaEvaluation": True
        },
        "preferences": {
            "defaultTaskPriority": "MEDIUM",
            "aiAutoEnhance": True,
            "voiceEnabled": True,
            "darkModeDefault": True
        },
        "onboardingTasks": [
            "Try voice capture: Say 'Add task review PR 123 tomorrow high priority'",
            "Use natural language: 'Show me priority tasks for today'",
            "Enable GitHub integration for automatic task creation"
        ]
    },
    "freelancer": {
        "id": "freelancer",
        "name": "Freelancer",
        "description": "Freelance designer or consultant managing multiple clients",
        "icon": "briefcase",
        "features": {
            "voiceCapture": True,
            "multiProjectManagement": True,
            "timeTrackingByClient": True,
            "deadlineTracking": True,
            "invoiceGeneration": True,
            "calendarIntegration": True
        },
        "preferences": {
            "defaultTaskPriority": "HIGH",
            "aiAutoEnhance": True,
            "voiceEnabled": True,
            "clientViewDefault": True
        },
        "onboardingTasks": [
            "Create your first client project",
            "Try voice capture during a client call",
            "Set up calendar integration for deadline tracking"
        ]
    },
    "explorer": {
        "id": "explorer",
        "name": "Explorer",
        "description": "Just exploring Focus by Kraliki to see what fits",
        "icon": "compass",
        "features": {
            "basicTaskManagement": True,
            "aiAssistant": True,
            "naturalLanguageTasks": True
        },
        "preferences": {
            "defaultTaskPriority": "MEDIUM",
            "aiAutoEnhance": True,
            "voiceEnabled": False
        },
        "onboardingTasks": [
            "Create your first task",
            "Ask the AI assistant: 'What should I work on today?'",
            "Explore the dashboard and insights"
        ]
    },
    "operations-lead": {
        "id": "operations-lead",
        "name": "Operations Lead",
        "description": "Team lead managing operations, schedules, and calendar coordination",
        "icon": "calendar-check",
        "features": {
            "voiceCapture": True,
            "calendarIntegration": True,
            "googleCalendarSync": True,
            "teamScheduling": True,
            "meetingManagement": True,
            "deadlineTracking": True,
            "naturalLanguageTasks": True,
            "dailyPlanning": True
        },
        "preferences": {
            "defaultTaskPriority": "HIGH",
            "aiAutoEnhance": True,
            "voiceEnabled": True,
            "calendarViewDefault": True
        },
        "onboardingTasks": [
            "Connect your Google Calendar for two-way sync",
            "Try voice capture: 'Schedule team standup tomorrow at 9am'",
            "Set up recurring meeting templates",
            "Enable calendar notifications for deadline reminders"
        ]
    }
}


class OnboardingStatusResponse(BaseModel):
    completed: bool
    currentStep: int
    selectedPersona: Optional[str] = None
    privacyAcknowledged: bool
    featureToggles: Dict[str, bool]


class SelectPersonaRequest(BaseModel):
    personaId: str


class UpdatePrivacyPreferencesRequest(BaseModel):
    geminiFileSearchEnabled: bool
    iiAgentEnabled: bool
    dataPrivacyAcknowledged: bool


class UpdateFeatureTogglesRequest(BaseModel):
    geminiFileSearch: bool
    iiAgent: bool
    voiceTranscription: bool


class CompleteOnboardingRequest(BaseModel):
    pass


@router.get("/status", response_model=OnboardingStatusResponse)
async def get_onboarding_status(
    current_user: User = Depends(get_current_user)
):
    """Get user's onboarding status and preferences"""
    privacy_prefs = current_user.privacyPreferences or {}
    feature_toggles = current_user.featureToggles or {
        "geminiFileSearch": True,
        "iiAgent": True,
        "voiceTranscription": True
    }

    return OnboardingStatusResponse(
        completed=current_user.onboardingCompleted,
        currentStep=current_user.onboardingStep,
        selectedPersona=current_user.selectedPersona,
        privacyAcknowledged=privacy_prefs.get("dataPrivacyAcknowledged", False),
        featureToggles=feature_toggles
    )


@router.get("/personas")
async def list_personas():
    """Get available persona templates"""
    return {
        "personas": list(PERSONA_TEMPLATES.values())
    }


@router.get("/personas/{persona_id}")
async def get_persona(persona_id: str):
    """Get detailed persona template"""
    if persona_id not in PERSONA_TEMPLATES:
        raise HTTPException(status_code=404, detail="Persona not found")

    return PERSONA_TEMPLATES[persona_id]


@router.post("/select-persona")
async def select_persona(
    request: SelectPersonaRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Select a persona template during onboarding"""
    if request.personaId not in PERSONA_TEMPLATES:
        raise HTTPException(status_code=400, detail="Invalid persona ID")

    persona = PERSONA_TEMPLATES[request.personaId]

    # Update user persona and preferences
    current_user.selectedPersona = request.personaId
    current_user.onboardingStep = max(current_user.onboardingStep, 1)

    # Apply persona default preferences if not already set
    if not current_user.preferences:
        current_user.preferences = persona["preferences"]

    db.commit()
    db.refresh(current_user)

    return {
        "success": True,
        "persona": persona,
        "nextStep": 2,
        "message": f"Welcome, {persona['name']}! Let's set up your privacy preferences."
    }


@router.post("/privacy-preferences")
async def update_privacy_preferences(
    request: UpdatePrivacyPreferencesRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user's privacy preferences during onboarding"""
    current_user.privacyPreferences = {
        "geminiFileSearchEnabled": request.geminiFileSearchEnabled,
        "iiAgentEnabled": request.iiAgentEnabled,
        "dataPrivacyAcknowledged": request.dataPrivacyAcknowledged
    }
    current_user.onboardingStep = max(current_user.onboardingStep, 2)

    db.commit()
    db.refresh(current_user)

    return {
        "success": True,
        "nextStep": 3,
        "message": "Privacy preferences saved. Now let's configure your features."
    }


@router.post("/feature-toggles")
async def update_feature_toggles(
    request: UpdateFeatureTogglesRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update feature toggles (can be called anytime)"""
    current_user.featureToggles = {
        "geminiFileSearch": request.geminiFileSearch,
        "iiAgent": request.iiAgent,
        "voiceTranscription": request.voiceTranscription
    }

    # If called during onboarding, advance step
    if not current_user.onboardingCompleted:
        current_user.onboardingStep = max(current_user.onboardingStep, 3)

    db.commit()
    db.refresh(current_user)

    return {
        "success": True,
        "featureToggles": current_user.featureToggles,
        "message": "Feature toggles updated successfully"
    }


@router.post("/complete")
async def complete_onboarding(
    request: CompleteOnboardingRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mark onboarding as complete.
    
    Requires completion of all 3 onboarding steps:
      1. POST /onboarding/select-persona - Choose your persona
      2. POST /onboarding/privacy-preferences - Set privacy settings
      3. POST /onboarding/feature-toggles - Configure features
    
    After completing all steps, call this endpoint to finalize onboarding.
    """
    if current_user.onboardingStep < 3:
        missing_steps = []
        if current_user.onboardingStep < 1:
            missing_steps.append("Step 1: Select persona (POST /onboarding/select-persona)")
        if current_user.onboardingStep < 2:
            missing_steps.append("Step 2: Set privacy preferences (POST /onboarding/privacy-preferences)")
        if current_user.onboardingStep < 3:
            missing_steps.append("Step 3: Configure feature toggles (POST /onboarding/feature-toggles)")
        
        raise HTTPException(
            status_code=400,
            detail={
                "message": "Please complete all onboarding steps first",
                "currentStep": current_user.onboardingStep,
                "requiredStep": 3,
                "missingSteps": missing_steps
            }
        )

    current_user.onboardingCompleted = True
    current_user.onboardingStep = 4

    db.commit()
    db.refresh(current_user)

    persona = PERSONA_TEMPLATES.get(current_user.selectedPersona, {})

    return {
        "success": True,
        "message": "Onboarding complete! Welcome to Focus by Kraliki.",
        "persona": persona,
        "nextSteps": persona.get("onboardingTasks", [])
    }


@router.post("/skip")
async def skip_onboarding(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Skip onboarding and use defaults"""
    current_user.onboardingCompleted = True
    current_user.selectedPersona = "explorer"
    current_user.onboardingStep = 4

    # Set default privacy preferences
    current_user.privacyPreferences = {
        "geminiFileSearchEnabled": True,
        "iiAgentEnabled": True,
        "dataPrivacyAcknowledged": False
    }

    # Set default feature toggles
    current_user.featureToggles = {
        "geminiFileSearch": True,
        "iiAgent": True,
        "voiceTranscription": True
    }

    db.commit()
    db.refresh(current_user)

    return {
        "success": True,
        "message": "Onboarding skipped. You can customize settings anytime."
    }
