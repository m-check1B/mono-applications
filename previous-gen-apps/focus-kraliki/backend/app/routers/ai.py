from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from openai import OpenAI
from app.core.database import get_db
from app.core.security import get_current_user, generate_id
from app.core.config import settings
from app.middleware.rate_limit import limiter
from app.core.cache import get_cache_manager, get_flow_memory, CacheManager, FlowMemory
from app.models.user import User
from app.models.task import Task, TaskStatus
from app.models.request_telemetry import RequestTelemetry, TelemetryRoute
from app.models.knowledge_item import KnowledgeItem
from app.models.event import Event
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
import inspect
# WebSocket notifications
from app.routers.websocket import manager as websocket_manager
from app.schemas.ai import (
    ChatRequest,
    ChatResponse,
    ToolCall,
    NaturalLanguageTaskRequest,
    NaturalLanguageTaskResponse,
    CognitiveStateRequest,
    CognitiveStateResponse,
    MemorySaveRequest,
    MemoryRecallRequest,
    MemoryResponse,
    EnhanceInputRequest,
    EnhanceInputResponse,
    AnalyzeTaskRequest,
    TaskAnalysisResponse,
    OrchestrateTaskRequest,
    OrchestrateTaskResponse,
    TaskWorkflowStep,
    HighReasoningRequest,
    HighReasoningResponse,
    GenerateInsightsRequest,
    GenerateInsightsResponse,
    InsightItem,
    TaskRecommendationsRequest,
    TaskRecommendationsResponse,
    TaskRecommendation,
    TelemetryRouteUpdateRequest,
    WorkflowDecisionRequest,
    TelemetryRecord,
    TelemetrySummaryResponse,
)
from app.schemas.command_history import (
    UnifiedTimelineResponse,
    TimelineEntry,
    ActivitySummaryResponse,
)
import logging
from datetime import datetime, timedelta
import json
import re
import os

logger = logging.getLogger(__name__)

from app.services.request_telemetry import (
    log_enhance_input,
    log_orchestrate_event,
    update_workflow_details,
    mark_route_decision,
    record_workflow_decision,
)
from app.services.route_selector import (
    get_route_selector,
    RouteType,
)
from app.services.command_history import (
    get_unified_timeline,
    get_user_activity_summary,
)
from app.models.command_history import CommandSource

# Import settings loader for centralized configuration
from app.core.settings_loader import (
    get_model_for_use_case,
    get_model_config,
    get_prompt_template,
    get_system_prompt,
    get_escalation_keywords
)

router = APIRouter(prefix="/ai", tags=["ai"])
# Dedicated router without /ai prefix for flow memory endpoints exercised in tests
flow_memory_router = APIRouter(tags=["flow-memory"])

_openrouter_client = None


class FlowMemoryStoreRequest(BaseModel):
    content: str = Field(..., min_length=1)
    context: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class FlowMemoryUpdateRequest(BaseModel):
    content: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class FlowMemoryStore:
    """Lightweight in-memory flow memory placeholder used by tests."""

    async def store(self, user_id: str, content: str, context: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None):
        return {
            "id": generate_id(),
            "stored": True,
            "content": content,
            "context": context,
            "metadata": metadata or {},
        }

    async def search(self, user_id: str, query: Optional[str] = None, context: Optional[str] = None, contexts: Optional[List[str]] = None, limit: int = 10, min_similarity: Optional[float] = None):
        return {"results": [], "total": 0}

    async def get_recent(self, user_id: str, limit: int = 10):
        return {"memories": [], "total": 0}

    async def update(self, user_id: str, memory_id: str, content: Optional[str], metadata: Optional[Dict[str, Any]] = None):
        return {"id": memory_id, "updated": True, "content": content, "metadata": metadata or {}}

    async def delete(self, user_id: str, memory_id: str):
        return {"deleted": True}

    async def delete_all(self, user_id: str):
        return {"deleted_count": 0}


# Exposed for tests (patched via unittest.mock in flow memory tests)
flow_memory_store = FlowMemoryStore()


async def _resolve(result):
    """Await result if coroutine, otherwise return directly."""
    if inspect.isawaitable(result):
        return await result
    return result


def get_openrouter_client():
    global _openrouter_client
    if _openrouter_client is None:
        _openrouter_client = OpenAI(
            api_key=os.environ.get("AI_INTEGRATIONS_OPENROUTER_API_KEY"),
            base_url=os.environ.get("AI_INTEGRATIONS_OPENROUTER_BASE_URL")
        )
    return _openrouter_client

from app.services.swarm_orchestrator import get_swarm_orchestrator

@router.post("/chat", response_model=ChatResponse)
@limiter.limit("30/minute")  # Rate limit AI chat - LLM calls are expensive
async def chat_with_ai(
    http_request: Request,
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    cache: CacheManager = Depends(get_cache_manager),
    memory: FlowMemory = Depends(get_flow_memory),
    db: Session = Depends(get_db)
):
    try:
        # Select model based on user's choice, fallback to reasoning mode, then default
        if request.model == "darwin2-swarm":
            swarm = get_swarm_orchestrator(db)
            swarm_result = await swarm.execute_swarm(request.message, {"history": request.conversationHistory})
            return ChatResponse(
                response=swarm_result["final_response"],
                model="darwin2-swarm",
                reasoning="Autonomous Swarm Orchestration (Darwin2)",
                metadata={"swarm_steps": swarm_result["steps"]}
            )

        if request.model:
            model_name = request.model
        elif request.useHighReasoning:
            model_name = get_model_for_use_case("highReasoning")
        else:
            model_name = get_model_for_use_case("chat")

        # Check cache for repeated questions (only for non-conversation queries)
        if not request.conversationHistory or len(request.conversationHistory) == 0:
            cached_response = await cache.get_ai_response(model_name, request.message)
            if cached_response:
                return ChatResponse(
                    response=cached_response,
                    model=model_name,
                    reasoning="Cached response"
                )

        # Save interaction to flow memory
        await memory.add_interaction(
            current_user.id,
            {
                "type": "chat",
                "message": request.message,
                "timestamp": datetime.utcnow().isoformat()
            }
        )

        # Build message history
        messages = [{"role": m.role, "content": m.content} for m in request.conversationHistory]
        messages.append({"role": "user", "content": request.message})

        # Define available tools for function calling
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "create_task",
                    "description": "Create a new task for the user",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string", "description": "Task title"},
                            "description": {"type": "string", "description": "Task description"},
                            "priority": {"type": "integer", "description": "Priority 1-5", "default": 3},
                            "projectId": {"type": "string", "description": "Optional project ID"}
                        },
                        "required": ["title"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "create_knowledge_item",
                    "description": "Create a new knowledge item (note, document, resource)",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string", "description": "Item title"},
                            "content": {"type": "string", "description": "Item content"},
                            "typeId": {"type": "string", "description": "Knowledge type ID (optional)"}
                        },
                        "required": ["title"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "create_event",
                    "description": "Create a calendar event",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string", "description": "Event title"},
                            "startTime": {"type": "string", "description": "ISO datetime"},
                            "endTime": {"type": "string", "description": "ISO datetime"},
                            "description": {"type": "string", "description": "Event description"}
                        },
                        "required": ["title", "startTime"]
                    }
                }
            }
        ]

        # Use OpenRouter with function calling
        response = get_openrouter_client().chat.completions.create(
            model=model_name,
            messages=messages,
            max_tokens=8192,
            tools=tools,
            tool_choice="auto"  # Let AI decide when to use tools
        )

        message = response.choices[0].message
        response_text = message.content or ""
        executed_tools = []

        # Execute tool calls if present
        if message.tool_calls:
            for tool_call in message.tool_calls:
                function_name = tool_call.function.name
                try:
                    arguments = json.loads(tool_call.function.arguments)
                except json.JSONDecodeError:
                    arguments = {}

                result = None

                # Execute the appropriate function
                if function_name == "create_task":
                    task = Task(
                        id=generate_id(),
                        userId=current_user.id,
                        title=arguments.get("title", "Untitled Task"),
                        description=arguments.get("description"),
                        priority=arguments.get("priority", 3),
                        projectId=arguments.get("projectId"),
                        status=TaskStatus.PENDING
                    )
                    db.add(task)
                    db.commit()
                    db.refresh(task)

                    # ✨ WebSocket notification for real-time UI update (Gap #6)
                    await websocket_manager.send_personal_message({
                        "type": "item_created",
                        "entity": "task",
                        "data": {
                            "id": task.id,
                            "title": task.title,
                            "status": task.status.value,
                            "priority": task.priority
                        }
                    }, current_user.id)

                    result = {"id": task.id, "title": task.title, "type": "task"}
                    if not response_text:
                        response_text = f"Created task: {task.title}"

                elif function_name == "create_knowledge_item":
                    item = KnowledgeItem(
                        id=generate_id(),
                        userId=current_user.id,
                        title=arguments.get("title", "Untitled"),
                        content=arguments.get("content"),
                        typeId=arguments.get("typeId")
                    )
                    db.add(item)
                    db.commit()
                    db.refresh(item)

                    # ✨ WebSocket notification for real-time UI update (Gap #6)
                    await websocket_manager.send_personal_message({
                        "type": "item_created",
                        "entity": "knowledge",
                        "data": {
                            "id": item.id,
                            "title": item.title,
                            "typeId": item.typeId
                        }
                    }, current_user.id)

                    result = {"id": item.id, "title": item.title, "type": "knowledge"}
                    if not response_text:
                        response_text = f"Created knowledge item: {item.title}"

                elif function_name == "create_event":
                    event = Event(
                        id=generate_id(),
                        userId=current_user.id,
                        title=arguments.get("title", "Untitled Event"),
                        description=arguments.get("description"),
                        startTime=datetime.fromisoformat(arguments.get("startTime").replace("Z", "+00:00")),
                        endTime=datetime.fromisoformat(arguments.get("endTime").replace("Z", "+00:00")) if arguments.get("endTime") else None
                    )
                    db.add(event)
                    db.commit()
                    db.refresh(event)

                    # ✨ WebSocket notification for real-time UI update (Gap #6)
                    await websocket_manager.send_personal_message({
                        "type": "item_created",
                        "entity": "event",
                        "data": {
                            "id": event.id,
                            "title": event.title,
                            "startTime": event.startTime.isoformat()
                        }
                    }, current_user.id)

                    result = {"id": event.id, "title": event.title, "type": "event"}
                    if not response_text:
                        response_text = f"Created event: {event.title}"

                # Store executed tool info
                executed_tools.append(ToolCall(
                    id=tool_call.id,
                    name=function_name,
                    arguments=arguments,
                    result=result
                ))

        # Cache simple queries (without tool calls)
        if not request.conversationHistory and not executed_tools:
            await cache.cache_ai_response(model_name, request.message, response_text, ttl=3600)

        reasoning_text = f"High reasoning mode ({model_name})" if request.useHighReasoning else f"Standard mode ({model_name})"

        return ChatResponse(
            response=response_text,
            model=model_name,
            reasoning=reasoning_text,
            tool_calls=executed_tools if executed_tools else None
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI service error: {str(e)}")

@router.post("/parse-task", response_model=NaturalLanguageTaskResponse)
@limiter.limit("30/minute")  # Rate limit task parsing - LLM call
async def parse_natural_language_task(
    http_request: Request,
    request: NaturalLanguageTaskRequest,
    current_user: User = Depends(get_current_user)
):
    try:
        # Use centralized prompt template
        prompt = get_prompt_template("parseTask", input=request.input)
        config = get_model_config("parseTask")

        response = get_openrouter_client().chat.completions.create(
            model=config["model"],
            messages=[{"role": "user", "content": prompt}],
            max_tokens=config["maxTokens"]
        )

        result = json.loads(response.choices[0].message.content)

        return NaturalLanguageTaskResponse(
            task=result,
            confidence=result.get("confidence", 0.8),
            suggestions=[]
        )
    except Exception as e:
        logger.warning(f"Natural language task parsing failed for user {current_user.id}: {e}")
        # Fallback parsing
        return NaturalLanguageTaskResponse(
            task={
                "title": request.input[:100],
                "priority": 2,
                "tags": [],
                "energyRequired": "medium"
            },
            confidence=0.5,
            suggestions=["Could not parse fully, using basic extraction"]
        )

@router.post("/enhance-input", response_model=EnhanceInputResponse)
@limiter.limit("60/minute")  # Rate limit input enhancement - LLM call
async def enhance_input(
    http_request: Request,
    request: EnhanceInputRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Enhance user input with AI - detect intent, type, and provide suggestions.

    Now includes:
    - Intelligent route selection with complexity scoring and caching
    - Escalation detection based on HYBRID-EXECUTION-GUIDE criteria
    - Performance tracking for route optimization
    """
    # Get route selector for intelligent routing
    route_selector = get_route_selector()
    text_lower = request.text.lower()
    escalation_keywords = get_escalation_keywords()
    has_escalation_keywords = any(kw in text_lower for kw in escalation_keywords)

    try:
        # OPTIMIZATION: Check for cached routing decision first
        # This can skip AI classification for similar inputs
        cached_decision = None if has_escalation_keywords else route_selector.get_cached_decision(
            request.text,
            request.context,
        )
        if cached_decision and cached_decision.confidence > 0.8:
            # High-confidence cached decision - skip AI classification
            logger.debug(f"Using cached routing decision for user {current_user.id}")

            # Still need to get intent/type for the response
            # Use deterministic parsing for cached routes
            route_decision = cached_decision

            # Quick deterministic intent detection
            if any(kw in text_lower for kw in ["create task", "add task", "new task", "todo"]):
                intent = "create_task"
                detected_type = "task"
            elif any(kw in text_lower for kw in ["create project", "new project"]):
                intent = "create_project"
                detected_type = "project"
            elif any(kw in text_lower for kw in ["schedule", "remind", "calendar"]):
                intent = "schedule"
                detected_type = "event"
            else:
                intent = "general"
                detected_type = "task"

            telemetry = log_enhance_input(
                db,
                user_id=current_user.id,
                intent=intent,
                detected_type=detected_type,
                confidence=cached_decision.confidence,
                details={
                    "text": request.text,
                    "shouldEscalate": cached_decision.route == RouteType.ORCHESTRATED,
                    "fromCache": True,
                    "routeDecision": cached_decision.route.value,
                },
            )

            return EnhanceInputResponse(
                enhanced_text=request.text.capitalize(),
                intent=intent,
                confidence=cached_decision.confidence,
                detectedType=detected_type,
                typeConfidence=cached_decision.confidence,
                suggestions=[],
                telemetryId=telemetry.id,
                shouldEscalate=cached_decision.route == RouteType.ORCHESTRATED,
                routeDecision=cached_decision.route.value,
                routeConfidence=cached_decision.confidence,
                complexityScore=None,
                complexityFactors=None,
                routeDecisionTimeMs=cached_decision.decision_time_ms,
                fromCache=True,
            )

        # Use centralized prompt template for full AI classification
        prompt = get_prompt_template(
            "enhanceInput",
            text=request.text,
            context=json.dumps(request.context or {})
        )
        config = get_model_config("enhanceInput")

        response = get_openrouter_client().chat.completions.create(
            model=config["model"],
            messages=[{"role": "user", "content": prompt}],
            max_tokens=config["maxTokens"]
        )

        # Extract JSON from response
        text = response.choices[0].message.content
        json_match = re.search(r'\{[\s\S]*\}', text)
        if json_match:
            result = json.loads(json_match.group())

            # Apply escalation logic based on HYBRID-EXECUTION-GUIDE
            should_escalate = result.get("shouldEscalate", False)
            confidence = result.get("confidence", 0.7)
            intent = result.get("intent", "")
            detected_type = result.get("detectedType", "")

            # OPTIMIZATION: Use intelligent route selector
            route_decision = route_selector.select_route(
                text=request.text,
                context=request.context,
                ai_confidence=confidence,
                ai_should_escalate=should_escalate
            )

            # Override escalation based on route decision
            if route_decision.route == RouteType.ORCHESTRATED:
                should_escalate = True
            elif route_decision.route == RouteType.DETERMINISTIC and not should_escalate:
                # Trust the route selector for deterministic routes
                should_escalate = False

            # Additional heuristics for escalation - load from settings
            if confidence < 0.5 and has_escalation_keywords:
                should_escalate = True
                result["shouldEscalate"] = True
                if "escalationReason" not in result:
                    result["escalationReason"] = {
                        "confidence": confidence,
                        "keywords": [kw for kw in escalation_keywords if kw in request.text.lower()],
                    }

            telemetry = log_enhance_input(
                db,
                user_id=current_user.id,
                intent=intent,
                detected_type=detected_type,
                confidence=confidence,
                details={
                    "text": request.text,
                    "shouldEscalate": should_escalate,
                    "escalationReason": result.get("escalationReason"),
                    "routeDecision": route_decision.route.value,
                    "complexityScore": route_decision.complexity_score.score if route_decision.complexity_score else None,
                },
            )

            # Build response with routing optimization fields
            response_data = {
                **result,
                "shouldEscalate": should_escalate,
                "telemetryId": telemetry.id,
                "routeDecision": route_decision.route.value,
                "routeConfidence": route_decision.confidence,
                "complexityScore": route_decision.complexity_score.score if route_decision.complexity_score else None,
                "complexityFactors": route_decision.complexity_score.factors if route_decision.complexity_score else None,
                "routeDecisionTimeMs": route_decision.decision_time_ms,
                "fromCache": route_decision.from_cache,
            }

            return EnhanceInputResponse(**response_data)

        # Fall through to fallback path if JSON missing
    except Exception as e:
        error_detail = str(e)
        logger.warning(f"Enhance input failed for user {current_user.id}: {e}")
    else:
        error_detail = None

    # Fallback: Use deterministic routing
    route_decision = route_selector.select_route(
        text=request.text,
        context=request.context,
        ai_confidence=0.5,
        ai_should_escalate=False
    )

    fallback = EnhanceInputResponse(
        enhanced_text=request.text.capitalize(),
        intent="create_task",
        confidence=0.7,
        detectedType="task",
        typeConfidence=0.75,
        suggestions=[],
        shouldEscalate=route_decision.route == RouteType.ORCHESTRATED,
        routeDecision=route_decision.route.value,
        routeConfidence=route_decision.confidence,
        complexityScore=route_decision.complexity_score.score if route_decision.complexity_score else None,
        complexityFactors=route_decision.complexity_score.factors if route_decision.complexity_score else None,
        routeDecisionTimeMs=route_decision.decision_time_ms,
        fromCache=False,
    )
    telemetry = log_enhance_input(
        db,
        user_id=current_user.id,
        intent=fallback.intent,
        detected_type=fallback.detectedType,
        confidence=fallback.confidence,
        details={
            "text": request.text,
            "fallback": True,
            "error": error_detail,
            "routeDecision": route_decision.route.value,
        },
    )
    fallback.telemetryId = telemetry.id
    return fallback

@router.post("/analyze-task", response_model=TaskAnalysisResponse)
@limiter.limit("30/minute")  # Rate limit task analysis - LLM call
async def analyze_task(
    http_request: Request,
    request: AnalyzeTaskRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Analyze a task and provide intelligent insights"""
    task = db.query(Task).filter(
        Task.id == request.taskId,
        Task.userId == current_user.id
    ).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    try:
        prompt = f"""Analyze this task:

Title: {task.title}
Description: {task.description or "None"}
Priority: {task.priority}
Tags: {task.tags}
Current Status: {task.status.value}

Provide analysis:
1. Urgency score (0-1)
2. Complexity score (0-1)
3. Estimated minutes to complete
4. Energy required (low/medium/high)
5. Suggested actions
6. Related task ideas

Return JSON:
{{
  "urgencyScore": 0.8,
  "complexityScore": 0.6,
  "estimatedMinutes": 45,
  "energyRequired": "medium",
  "suggestedActions": ["action 1", "action 2"],
  "relatedTasks": ["related 1", "related 2"]
}}"""

        response = get_openrouter_client().chat.completions.create(
            model="z-ai/glm-4.6",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=8192
        )

        result = json.loads(response.choices[0].message.content)

        # Update task with AI insights
        task.aiInsights = result
        task.urgencyScore = result.get("urgencyScore", 0.5)
        db.commit()

        return TaskAnalysisResponse(**result)
    except Exception as e:
        logger.warning(f"Task analysis failed for task {request.taskId}: {e}")
        # Fallback analysis
        return TaskAnalysisResponse(
            urgencyScore=0.5,
            complexityScore=0.5,
            estimatedMinutes=30,
            energyRequired="medium",
            suggestedActions=["Start working on the task"],
            relatedTasks=[]
        )

@router.post("/orchestrate-task", response_model=OrchestrateTaskResponse)
@limiter.limit("20/minute")  # Rate limit task orchestration - complex LLM call
async def orchestrate_task(
    http_request: Request,
    request: OrchestrateTaskRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Convert natural language to structured task with workflow"""
    metadata = None
    telemetry_record = None
    workflow = None
    confidence = 0.5

    try:
        # Use centralized prompt template and model selection
        prompt = get_prompt_template(
            "orchestrateTask",
            input=request.input,
            context=json.dumps(request.context or {})
        )

        use_case = "highReasoning" if request.useHighReasoning else "orchestrateTask"
        config = get_model_config(use_case)

        response = get_openrouter_client().chat.completions.create(
            model=config["model"],
            messages=[{"role": "user", "content": prompt}],
            max_tokens=config["maxTokens"]
        )
        result = json.loads(response.choices[0].message.content)
        workflow = [TaskWorkflowStep(**step) for step in result["workflow"]]
        confidence = result.get("confidence", 0.8)
        metadata = {
            "mainTaskTitle": result.get("mainTask", {}).get("title"),
            "suggestionsCount": len(result.get("suggestions", [])),
        }

        if request.telemetryId:
            telemetry_record = update_workflow_details(
                db,
                telemetry_id=request.telemetryId,
                workflow_steps=len(workflow),
                confidence=confidence,
                details=metadata,
            )
        if not telemetry_record:
            telemetry_record = log_orchestrate_event(
                db,
                user_id=current_user.id,
                workflow_steps=len(workflow),
                confidence=confidence,
                details=metadata,
            )

        return OrchestrateTaskResponse(
            mainTask=result["mainTask"],
            workflow=workflow,
            suggestions=result.get("suggestions", []),
            confidence=confidence,
            telemetryId=telemetry_record.id
        )
    except Exception as e:
        logger.error(f"Orchestration failed for user {current_user.id}: {e}", exc_info=True)
        # Fall back to deterministic workflow creation
        workflow = [
            TaskWorkflowStep(
                step=1,
                action="Complete the task",
                estimatedMinutes=30,
                dependencies=[]
            )
        ]
        fallback_main = {
            "title": request.input[:100],
            "priority": 2,
            "estimatedMinutes": 30
        }
        if request.telemetryId:
            telemetry_record = update_workflow_details(
                db,
                telemetry_id=request.telemetryId,
                workflow_steps=len(workflow),
                confidence=confidence,
                details={"fallback": True},
            )
        if not telemetry_record:
            telemetry_record = log_orchestrate_event(
                db,
                user_id=current_user.id,
                workflow_steps=len(workflow),
                confidence=confidence,
                details={"fallback": True},
            )

        return OrchestrateTaskResponse(
            mainTask=fallback_main,
            workflow=workflow,
            suggestions=[],
            confidence=confidence,
            telemetryId=telemetry_record.id
        )


@router.post("/telemetry/{telemetry_id}/route", response_model=TelemetryRecord)
async def update_telemetry_route(
    telemetry_id: str,
    request: TelemetryRouteUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    telemetry = (
        db.query(RequestTelemetry)
        .filter(
            RequestTelemetry.id == telemetry_id,
            RequestTelemetry.userId == current_user.id
        )
        .first()
    )
    if not telemetry:
        raise HTTPException(status_code=404, detail="Telemetry record not found")

    updated = mark_route_decision(
        db,
        telemetry_id=telemetry_id,
        route=request.route,
        reason=request.reason,
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Telemetry record not found")
    return updated


@router.post("/telemetry/{telemetry_id}/decision", response_model=TelemetryRecord)
async def save_workflow_decision(
    telemetry_id: str,
    request: WorkflowDecisionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    telemetry = (
        db.query(RequestTelemetry)
        .filter(
            RequestTelemetry.id == telemetry_id,
            RequestTelemetry.userId == current_user.id
        )
        .first()
    )
    if not telemetry:
        raise HTTPException(status_code=404, detail="Telemetry record not found")

    updated = record_workflow_decision(
        db,
        telemetry_id=telemetry_id,
        status=request.status,
        notes=request.notes,
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Telemetry record not found")
    return updated


@router.get("/telemetry/summary", response_model=TelemetrySummaryResponse)
async def get_telemetry_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    base_query = db.query(RequestTelemetry).filter(
        RequestTelemetry.userId == current_user.id
    )
    total = base_query.count()
    deterministic = base_query.filter(
        RequestTelemetry.route == TelemetryRoute.DETERMINISTIC
    ).count()
    orchestrated = base_query.filter(
        RequestTelemetry.route == TelemetryRoute.ORCHESTRATED
    ).count()
    unknown = total - deterministic - orchestrated

    recent = (
        base_query.order_by(RequestTelemetry.createdAt.desc())
        .limit(20)
        .all()
    )

    return TelemetrySummaryResponse(
        total=total,
        deterministic=deterministic,
        orchestrated=orchestrated,
        unknown=unknown,
        recent=recent
    )


@router.get("/routing/stats")
async def get_routing_stats(
    current_user: User = Depends(get_current_user),
):
    """
    Get hybrid execution routing performance statistics.

    Returns metrics for each route type including:
    - Total requests
    - Success rate
    - Average latency
    - Circuit breaker status

    This endpoint is useful for monitoring routing efficiency
    and identifying performance bottlenecks.
    """
    route_selector = get_route_selector()
    stats = route_selector.get_performance_stats()

    return {
        "routes": stats,
        "cache_enabled": True,
        "circuit_breaker_enabled": True,
        "optimization_version": "1.0.0"
    }


@router.post("/routing/analyze")
async def analyze_routing(
    text: str,
    context: Optional[Dict[str, Any]] = None,
    current_user: User = Depends(get_current_user),
):
    """
    Analyze routing decision for a given input without executing.

    This endpoint is useful for debugging and understanding
    how the routing system classifies different inputs.

    Returns:
    - Recommended route
    - Complexity score and factors
    - Detailed reasoning
    """
    route_selector = get_route_selector()
    route, reason, factors = route_selector.get_recommended_route_with_reason(text, context)

    return {
        "route": route.value,
        "reason": reason,
        "details": factors
    }


@router.post("/high-reasoning", response_model=HighReasoningResponse)
@limiter.limit("10/minute")  # Rate limit high-reasoning - expensive LLM call
async def high_reasoning(
    http_request: Request,
    request: HighReasoningRequest,
    current_user: User = Depends(get_current_user)
):
    """Use high-reasoning models for complex tasks"""
    try:
        # Load system prompt and model from settings
        system_prompt = get_system_prompt("highReasoning")
        config = get_model_config("highReasoning")

        messages = [
            system_prompt,
            {"role": "user", "content": request.prompt}
        ]

        if request.context:
            messages.insert(1, {
                "role": "user",
                "content": f"Context: {json.dumps(request.context, indent=2)}"
            })

        response = get_openrouter_client().chat.completions.create(
            model=config["model"],
            messages=messages,
            max_tokens=request.maxTokens or config["maxTokens"]
        )

        return HighReasoningResponse(
            response=response.choices[0].message.content,
            reasoning=f"High reasoning mode using {config['model']}",
            confidence=0.95,
            model=config["model"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"High reasoning failed: {str(e)}")

@router.post("/insights", response_model=GenerateInsightsResponse)
@limiter.limit("10/minute")  # Rate limit insights - expensive analysis
async def generate_insights(
    http_request: Request,
    request: GenerateInsightsRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate productivity insights based on user's task history"""
    # Calculate time range
    if request.timeRange == "7d":
        since = datetime.utcnow() - timedelta(days=7)
    elif request.timeRange == "30d":
        since = datetime.utcnow() - timedelta(days=30)
    else:
        since = datetime.utcnow() - timedelta(days=7)

    tasks = db.query(Task).filter(
        Task.userId == current_user.id,
        Task.createdAt >= since
    ).all()

    task_data = [
        {
            "title": t.title,
            "status": t.status.value,
            "priority": t.priority,
            "completedAt": t.completedAt.isoformat() if t.completedAt else None,
            "tags": t.tags
        }
        for t in tasks
    ]

    try:
        prompt = f"""Analyze this productivity data and generate insights:

Tasks (last {request.timeRange}): {json.dumps(task_data, indent=2)}

Generate insights about:
1. Productivity patterns
2. Task completion rates
3. Time management
4. Priority balance
5. Areas for improvement

Return JSON:
{{
  "insights": [
    {{"category": "productivity", "insight": "...", "actionable": true, "priority": "high"}}
  ],
  "summary": "Overall summary..."
}}"""

        response = get_openrouter_client().chat.completions.create(
            model="z-ai/glm-4.6",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=8192
        )

        result = json.loads(response.choices[0].message.content)

        return GenerateInsightsResponse(
            insights=[InsightItem(**i) for i in result["insights"]],
            summary=result["summary"]
        )
    except Exception as e:
        logger.warning(f"Generating insights failed for user {current_user.id}: {e}")
        # Fallback insights
        return GenerateInsightsResponse(
            insights=[
                InsightItem(
                    category="productivity",
                    insight="Continue tracking your tasks for better insights",
                    actionable=True,
                    priority="medium"
                )
            ],
            summary=f"Analyzed {len(tasks)} tasks from the last {request.timeRange}"
        )

@router.post("/task-recommendations", response_model=TaskRecommendationsResponse)
@limiter.limit("10/minute")  # Rate limit recommendations - LLM analysis
async def get_task_recommendations(
    http_request: Request,
    request: TaskRecommendationsRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get AI-powered task recommendations based on user patterns"""
    # Get recent task history
    recent_tasks = db.query(Task).filter(
        Task.userId == current_user.id
    ).order_by(Task.createdAt.desc()).limit(20).all()

    task_patterns = [
        {"title": t.title, "tags": t.tags, "priority": t.priority}
        for t in recent_tasks
    ]

    try:
        prompt = f"""Based on this user's task history, suggest new relevant tasks:

Recent tasks: {json.dumps(task_patterns, indent=2)}
Current context: {json.dumps(request.currentContext or {}, indent=2)}

Suggest 5 tasks that would be valuable based on patterns.

Return JSON:
{{
  "recommendations": [
    {{
      "title": "Task title",
      "description": "Why this matters",
      "priority": 3,
      "reasoning": "Based on your pattern of..."
    }}
  ]
}}"""

        response = get_openrouter_client().chat.completions.create(
            model="google/gemini-2.5-flash-preview-09-2025",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=8192
        )

        result = json.loads(response.choices[0].message.content)

        return TaskRecommendationsResponse(
            recommendations=[TaskRecommendation(**r) for r in result["recommendations"]],
            total=len(result["recommendations"])
        )
    except Exception as e:
        logger.warning(f"Task recommendations failed for user {current_user.id}: {e}")
        # Fallback
        return TaskRecommendationsResponse(
            recommendations=[],
            total=0
        )

@router.post("/cognitive-state", response_model=CognitiveStateResponse)
async def analyze_cognitive_state(
    request: CognitiveStateRequest,
    current_user: User = Depends(get_current_user)
):
    try:
        prompt = f"""Analyze cognitive state from this activity data:

{json.dumps(request.activityData, indent=2)}

Determine:
1. Current cognitive state (focused, distracted, fatigued, flow)
2. Cognitive load score (0-1)
3. Recommendations for optimal productivity

Return JSON with:
- state: string
- score: number (0-1)
- recommendations: array of strings"""

        response = get_openrouter_client().chat.completions.create(
            model="google/gemini-2.5-flash-preview-09-2025",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=8192
        )

        result = json.loads(response.choices[0].message.content)

        return CognitiveStateResponse(**result)
    except Exception as e:
        logger.warning(f"Cognitive state analysis failed for user {current_user.id}: {e}")
        # Fallback
        return CognitiveStateResponse(
            state="unknown",
            score=0.5,
            recommendations=["Unable to analyze state at this time"]
        )

@router.post("/notes")
async def save_note(
    note: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Save AI-generated note to memory system"""
    # Store note in user preferences or create notes table
    prefs = current_user.preferences or {}
    notes = prefs.get("ai_notes", [])

    note_entry = {
        "id": generate_id(),
        "content": note.get("content", ""),
        "tags": note.get("tags", []),
        "createdAt": datetime.utcnow().isoformat()
    }

    notes.append(note_entry)
    prefs["ai_notes"] = notes[-50:]  # Keep last 50 notes

    current_user.preferences = prefs
    db.commit()

    return {"success": True, "note": note_entry}

@router.get("/notes")
async def get_notes(
    limit: int = 20,
    current_user: User = Depends(get_current_user)
):
    """Get user's saved AI notes"""
    prefs = current_user.preferences or {}
    notes = prefs.get("ai_notes", [])

    return {
        "notes": notes[-limit:],
        "total": len(notes)
    }

@router.post("/memory/save")
async def save_memory(
    request: MemorySaveRequest,
    current_user: User = Depends(get_current_user),
    memory: FlowMemory = Depends(get_flow_memory)
):
    """Save memory to Redis flow memory system"""
    success = await memory.save_memory(
        current_user.id,
        request.key,
        request.value
    )
    return {"success": success, "message": "Memory saved" if success else "Failed to save memory"}

@router.post("/memory/recall", response_model=MemoryResponse)
async def recall_memories(
    request: MemoryRecallRequest,
    current_user: User = Depends(get_current_user),
    memory: FlowMemory = Depends(get_flow_memory)
):
    """Recall memory from Redis flow memory system"""
    recalled = await memory.recall_memory(current_user.id, request.query)

    if recalled:
        return MemoryResponse(
            memories=[recalled],
            total=1
        )
    return MemoryResponse(
        memories=[],
        total=0
    )


@router.post("/flow-memory/store", status_code=201)
async def flow_memory_store_endpoint(
    request: FlowMemoryStoreRequest,
    current_user: User = Depends(get_current_user),
):
    """Store a memory snippet for the current user."""
    result = await _resolve(
        flow_memory_store.store(
            current_user.id,
            request.content,
            request.context,
            request.metadata,
        )
    )
    if not isinstance(result, dict):
        raise HTTPException(status_code=500, detail="Failed to store memory")
    return result


@router.get("/flow-memory/search")
async def flow_memory_search_endpoint(
    query: Optional[str] = None,
    context: Optional[str] = None,
    contexts: Optional[str] = None,
    limit: int = 10,
    min_similarity: Optional[float] = None,
    current_user: User = Depends(get_current_user),
):
    """Search stored memories."""
    contexts_list = contexts.split(",") if contexts else None
    result = await _resolve(
        flow_memory_store.search(
            current_user.id,
            query=query,
            context=context,
            contexts=contexts_list,
            limit=limit,
            min_similarity=min_similarity,
        )
    )
    result = result or {"results": [], "total": 0}

    if min_similarity is not None and isinstance(result, dict) and "results" in result:
        filtered = [r for r in result.get("results", []) if r.get("similarity", 0) >= min_similarity]
        result["results"] = filtered
        result["total"] = len(filtered)

    return result


@router.get("/flow-memory/recent")
async def flow_memory_recent_endpoint(
    limit: int = 10,
    current_user: User = Depends(get_current_user),
):
    """Return the most recent memories."""
    result = await _resolve(flow_memory_store.get_recent(current_user.id, limit))
    return result or {"memories": [], "total": 0}


@router.patch("/flow-memory/{memory_id}")
async def flow_memory_update_endpoint(
    memory_id: str,
    request: FlowMemoryUpdateRequest,
    current_user: User = Depends(get_current_user),
):
    """Update an existing memory."""
    try:
        result = await _resolve(
            flow_memory_store.update(
                current_user.id,
                memory_id,
                request.content,
                request.metadata,
            )
        )
    except Exception as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    return result or {"id": memory_id, "updated": True}


@router.delete("/flow-memory/{memory_id}")
async def flow_memory_delete_endpoint(
    memory_id: str,
    current_user: User = Depends(get_current_user),
):
    """Delete a memory by ID."""
    result = await _resolve(flow_memory_store.delete(current_user.id, memory_id))
    return result or {"deleted": True}


@router.delete("/flow-memory/all")
async def flow_memory_delete_all_endpoint(
    current_user: User = Depends(get_current_user),
):
    """Delete all memories for the current user."""
    result = await _resolve(flow_memory_store.delete_all(current_user.id))
    return result or {"deleted_count": 0}


# Register the same flow-memory endpoints on a root-level router (no /ai prefix)
flow_memory_router.add_api_route(
    "/flow-memory/store",
    flow_memory_store_endpoint,
    methods=["POST"],
    status_code=201,
)
flow_memory_router.add_api_route(
    "/flow-memory/search",
    flow_memory_search_endpoint,
    methods=["GET"],
)
flow_memory_router.add_api_route(
    "/flow-memory/recent",
    flow_memory_recent_endpoint,
    methods=["GET"],
)
flow_memory_router.add_api_route(
    "/flow-memory/{memory_id}",
    flow_memory_update_endpoint,
    methods=["PATCH"],
)
flow_memory_router.add_api_route(
    "/flow-memory/{memory_id}",
    flow_memory_delete_endpoint,
    methods=["DELETE"],
)
flow_memory_router.add_api_route(
    "/flow-memory/all",
    flow_memory_delete_all_endpoint,
    methods=["DELETE"],
)


@router.get("/flow/context/{session_id}")
async def get_flow_context(
    session_id: str,
    current_user: User = Depends(get_current_user),
    memory: FlowMemory = Depends(get_flow_memory)
):
    """Get flow context for a session"""
    context = await memory.get_context(current_user.id, session_id)
    return {
        "session_id": session_id,
        "context": context or {},
        "has_context": context is not None
    }


@router.post("/flow/context/{session_id}")
async def save_flow_context(
    session_id: str,
    context: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    memory: FlowMemory = Depends(get_flow_memory)
):
    """Save flow context for a session"""
    success = await memory.save_context(current_user.id, session_id, context)
    return {
        "success": success,
        "session_id": session_id,
        "message": "Context saved" if success else "Failed to save context"
    }


@router.get("/flow/interactions")
async def get_recent_interactions(
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    memory: FlowMemory = Depends(get_flow_memory)
):
    """Get recent user interactions from flow memory"""
    interactions = await memory.get_recent_interactions(current_user.id, limit)
    return {
        "interactions": interactions,
        "total": len(interactions)
    }


@router.get("/flow/interactions")
async def get_recent_interactions(
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    memory: FlowMemory = Depends(get_flow_memory)
):
    """Get recent user interactions from flow memory"""
    interactions = await memory.get_recent_interactions(current_user.id, limit)
    return {
        "interactions": interactions,
        "total": len(interactions)
    }


# ========== Unified Timeline & History Endpoints ==========

from fastapi import Query
from typing import List, Optional

@router.get("/telemetry/history", response_model=UnifiedTimelineResponse)
async def get_telemetry_history(
    since: Optional[datetime] = Query(None, description="Start date (default: 7 days ago)"),
    until: Optional[datetime] = Query(None, description="End date (default: now)"),
    sources: Optional[List[str]] = Query(None, description="Filter by command sources"),
    includeTelemetry: bool = Query(True, description="Include routing telemetry"),
    limit: int = Query(100, ge=1, le=500, description="Maximum timeline entries"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get unified timeline of user activity across commands and telemetry.
    
    This endpoint answers the question: "What did I work on last week?"
    
    It provides a chronological view of all user interactions including:
    - Voice and text assistant commands
    - Deterministic API operations (tasks, projects, etc.)
    - II-Agent orchestrated executions
    - Workflow executions
    - Routing telemetry (classification decisions)
    
    Query Parameters:
    - since: Start date in ISO 8601 format (default: 7 days ago)
    - until: End date in ISO 8601 format (default: now)
    - sources: Filter by command sources (can be specified multiple times)
    - includeTelemetry: Include routing telemetry in timeline (default: true)
    - limit: Maximum number of timeline entries (1-500, default 100)
    
    Returns:
        Unified timeline with commands and telemetry sorted by timestamp
    """
    # Convert source strings to CommandSource enums if provided
    source_enums = None
    if sources:
        try:
            source_enums = [CommandSource(s) for s in sources]
        except ValueError as e:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid command source: {e}. Valid sources: {[s.value for s in CommandSource]}"
            )
    
    timeline_data = get_unified_timeline(
        db,
        user_id=current_user.id,
        since=since,
        until=until,
        sources=source_enums,
        include_telemetry=includeTelemetry,
        limit=limit,
    )
    
    # Calculate period
    actual_since = since or (datetime.utcnow() - timedelta(days=7))
    actual_until = until or datetime.utcnow()
    
    return UnifiedTimelineResponse(
        timeline=[TimelineEntry(**entry) for entry in timeline_data],
        total=len(timeline_data),
        period={
            "since": actual_since.isoformat(),
            "until": actual_until.isoformat(),
        }
    )


@router.get("/telemetry/activity-summary", response_model=ActivitySummaryResponse)
async def get_activity_summary(
    since: Optional[datetime] = Query(None, description="Start date (default: 7 days ago)"),
    until: Optional[datetime] = Query(None, description="End date (default: now)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get summary statistics of user activity.
    
    Provides aggregate metrics about user activity including:
    - Total commands executed
    - Success/failure rates
    - Breakdown by source (voice, API, agent, etc.)
    - Breakdown by intent (create_task, update_task, etc.)
    - Average execution duration
    
    Query Parameters:
    - since: Start date in ISO 8601 format (default: 7 days ago)
    - until: End date in ISO 8601 format (default: now)
    
    Returns:
        Activity summary with statistics
    """
    summary = get_user_activity_summary(
        db,
        user_id=current_user.id,
        since=since,
        until=until,
    )
    
    return ActivitySummaryResponse(**summary)
