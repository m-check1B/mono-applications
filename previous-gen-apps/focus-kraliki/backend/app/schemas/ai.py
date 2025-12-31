from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

from app.models.request_telemetry import TelemetryRoute, WorkflowDecisionStatus

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    conversationHistory: List[ChatMessage] = []
    useHighReasoning: bool = False
    model: Optional[str] = None  # Allow user to select specific model

class ToolCall(BaseModel):
    """Represents an AI function/tool call"""
    id: str
    name: str
    arguments: Dict[str, Any]
    result: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    response: str
    model: str
    reasoning: Optional[str] = None
    tool_calls: Optional[List[ToolCall]] = None  # AI-executed actions

class NaturalLanguageTaskRequest(BaseModel):
    input: str
    context: Optional[Dict[str, Any]] = None

class NaturalLanguageTaskResponse(BaseModel):
    task: Optional[Dict[str, Any]]
    confidence: float
    suggestions: List[str] = []

class ShadowAnalysisRequest(BaseModel):
    userId: str
    recentActivity: List[Dict[str, Any]] = []

class ShadowAnalysisResponse(BaseModel):
    insights: List[str]
    patterns: Dict[str, Any]
    recommendations: List[str]

class CognitiveStateRequest(BaseModel):
    userId: str
    activityData: Dict[str, Any]

class CognitiveStateResponse(BaseModel):
    state: str
    score: float
    recommendations: List[str]

class MemorySaveRequest(BaseModel):
    userId: str
    key: str
    value: Dict[str, Any]
    tags: List[str] = []

class MemoryRecallRequest(BaseModel):
    userId: str
    query: str
    limit: int = 10

class MemoryResponse(BaseModel):
    memories: List[Dict[str, Any]]
    total: int

# New schemas for Phase 1+2

class EnhanceInputRequest(BaseModel):
    text: str
    context: Optional[Dict[str, Any]] = None

class EnhanceInputResponse(BaseModel):
    enhanced_text: str
    intent: str
    confidence: float
    detectedType: str
    typeConfidence: float
    suggestions: List[str]
    telemetryId: Optional[str] = None
    shouldEscalate: bool = False
    escalationReason: Optional[Dict[str, Any]] = None
    # Hybrid execution routing optimization fields
    routeDecision: Optional[str] = None  # "deterministic", "orchestrated", "hybrid", "cached"
    routeConfidence: Optional[float] = None
    complexityScore: Optional[float] = None
    complexityFactors: Optional[Dict[str, float]] = None
    routeDecisionTimeMs: Optional[float] = None
    fromCache: bool = False

class AnalyzeTaskRequest(BaseModel):
    taskId: str
    includeRecommendations: bool = True

class TaskAnalysisResponse(BaseModel):
    urgencyScore: float
    complexityScore: float
    estimatedMinutes: int
    energyRequired: str
    suggestedActions: List[str]
    relatedTasks: List[str]

class OrchestrateTaskRequest(BaseModel):
    input: str
    useHighReasoning: bool = False
    includeWorkflow: bool = True
    context: Optional[Dict[str, Any]] = None
    telemetryId: Optional[str] = None

class TaskWorkflowStep(BaseModel):
    step: int
    action: str
    estimatedMinutes: int
    dependencies: List[int] = []

class OrchestrateTaskResponse(BaseModel):
    mainTask: Dict[str, Any]
    workflow: List[TaskWorkflowStep]
    suggestions: List[str]
    confidence: float
    telemetryId: Optional[str] = None
    shouldEscalate: bool = False
    escalationReason: Optional[Dict[str, Any]] = None
    agentSessionId: Optional[str] = None

class HighReasoningRequest(BaseModel):
    prompt: str
    context: Optional[Dict[str, Any]] = None
    maxTokens: int = 4000

class HighReasoningResponse(BaseModel):
    response: str
    reasoning: str
    confidence: float
    model: str

class GenerateInsightsRequest(BaseModel):
    userId: str
    timeRange: str = "7d"

class InsightItem(BaseModel):
    category: str
    insight: str
    actionable: bool
    priority: str

class GenerateInsightsResponse(BaseModel):
    insights: List[InsightItem]
    summary: str

class TaskRecommendationsRequest(BaseModel):
    userId: str
    currentContext: Optional[Dict[str, Any]] = None

class TaskRecommendation(BaseModel):
    title: str
    description: str
    priority: int
    reasoning: str

class TaskRecommendationsResponse(BaseModel):
    recommendations: List[TaskRecommendation]
    total: int


class TelemetryRouteUpdateRequest(BaseModel):
    route: TelemetryRoute
    reason: Optional[Dict[str, Any]] = None


class WorkflowDecisionRequest(BaseModel):
    status: WorkflowDecisionStatus
    notes: Optional[Dict[str, Any]] = None


class TelemetryRecord(BaseModel):
    id: str
    source: str
    intent: Optional[str]
    detectedType: Optional[str]
    confidence: Optional[float]
    workflowSteps: Optional[int]
    route: str
    decisionStatus: Optional[str]
    decisionNotes: Optional[Dict[str, Any]]
    decisionAt: Optional[datetime]
    createdAt: datetime

    class Config:
        from_attributes = True


class TelemetrySummaryResponse(BaseModel):
    total: int
    deterministic: int
    orchestrated: int
    unknown: int
    recent: List[TelemetryRecord]


# Agent Session Schemas

class AgentSessionCreate(BaseModel):
    """Request to create an agent session with II-Agent."""
    goal: str
    structuredGoal: Optional[Dict[str, Any]] = None
    context: Optional[Dict[str, Any]] = None
    escalationReason: Optional[Dict[str, Any]] = None
    telemetryId: Optional[str] = None


class AgentSessionResponse(BaseModel):
    """Response containing agent session details."""
    id: str
    sessionUuid: str
    status: str
    goal: str
    structuredGoal: Optional[Dict[str, Any]]
    context: Optional[Dict[str, Any]]
    agentToken: str
    toolCallCount: int
    progressPercent: Optional[float]
    currentStep: Optional[str]
    createdAt: datetime

    class Config:
        from_attributes = True


class AgentSessionEventResponse(BaseModel):
    """Response containing agent session event details."""
    id: str
    sessionId: str
    eventType: str
    toolName: Optional[str]
    toolInput: Optional[Dict[str, Any]]
    toolOutput: Optional[Dict[str, Any]]
    toolError: Optional[str]
    eventData: Optional[Dict[str, Any]]
    createdAt: datetime

    class Config:
        from_attributes = True


class AgentSessionStatusUpdate(BaseModel):
    """Request to update agent session status."""
    status: str
    errorMessage: Optional[str] = None
    result: Optional[Dict[str, Any]] = None


class AgentSessionProgressUpdate(BaseModel):
    """Request to update agent session progress."""
    progressPercent: Optional[float] = None
    currentStep: Optional[str] = None


class AgentToolCallEvent(BaseModel):
    """Request to record a tool call event."""
    toolName: str
    toolInput: Optional[Dict[str, Any]] = None
    toolOutput: Optional[Dict[str, Any]] = None
    toolError: Optional[str] = None
    durationMs: Optional[int] = None
