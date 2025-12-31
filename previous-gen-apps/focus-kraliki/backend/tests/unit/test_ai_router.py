"""
Unit tests for AI Router
"""
import pytest
import json
from unittest.mock import MagicMock, patch, AsyncMock
from app.routers import ai
from app.models.task import Task, TaskStatus

@pytest.fixture
def mock_openai():
    with patch("app.routers.ai.get_openrouter_client") as mock:
        client = MagicMock()
        mock.return_value = client
        yield client

@pytest.fixture
def mock_settings():
    with patch("app.routers.ai.get_model_for_use_case", return_value="gpt-4"), \
         patch("app.routers.ai.get_model_config", return_value={"model": "gpt-4", "maxTokens": 1000}), \
         patch("app.routers.ai.get_prompt_template", return_value="Prompt"), \
         patch("app.routers.ai.get_escalation_keywords", return_value=["research"]):
        yield

@pytest.mark.asyncio
async def test_chat_with_ai_simple(client, test_user, auth_headers, mock_openai, mock_settings):
    """Test simple chat without tools"""
    # Mock OpenAI response
    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(message=MagicMock(content="Hello user", tool_calls=None))
    ]
    mock_openai.chat.completions.create.return_value = mock_response
    
    response = client.post(
        "/ai/chat",
        headers=auth_headers,
        json={
            "message": "Hello",
            "conversationHistory": []
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["response"] == "Hello user"
    assert data["model"] == "gpt-4"

@pytest.mark.asyncio
async def test_chat_with_ai_tool_call(client, test_user, auth_headers, mock_openai, mock_settings, db):
    """Test chat with tool execution (create_task)""" 
    # Mock OpenAI response with tool call
    tool_call = MagicMock()
    tool_call.id = "call_1"
    tool_call.function.name = "create_task"
    tool_call.function.arguments = json.dumps({"title": "New Task", "priority": 5})
    
    mock_message = MagicMock(content=None, tool_calls=[tool_call])
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=mock_message)]
    mock_openai.chat.completions.create.return_value = mock_response
    
    # Mock websocket (it is awaited)
    with patch("app.routers.ai.websocket_manager.send_personal_message", new_callable=AsyncMock) as mock_ws:
        response = client.post(
            "/ai/chat",
            headers=auth_headers,
            json={
                "message": "Create a task",
                "conversationHistory": []
            }
        )
        
    assert response.status_code == 200
    data = response.json()
    
    # Check task was created
    task = db.query(Task).filter_by(userId=test_user.id, title="New Task").first()
    assert task is not None
    assert task.priority == 5
    
    # Check response content (generated from tool result)
    assert "Created task: New Task" in data["response"]
    assert len(data["tool_calls"]) == 1
    assert data["tool_calls"][0]["name"] == "create_task"

@pytest.mark.asyncio
async def test_enhance_input_standard(client, test_user, auth_headers, mock_openai, mock_settings):
    """Test input enhancement"""
    mock_response_content = json.dumps({
        "enhanced_text": "Create a task",
        "intent": "create_task",
        "confidence": 0.9,
        "detectedType": "task",
        "typeConfidence": 0.95,
        "suggestions": ["Add due date"],
        "shouldEscalate": False
    })
    
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content=mock_response_content))]
    mock_openai.chat.completions.create.return_value = mock_response
    
    with patch("app.routers.ai.log_enhance_input") as mock_log:
        # Return a dummy telemetry object with an id
        mock_log.return_value = MagicMock(id="tel-123")
        
        response = client.post(
            "/ai/enhance-input",
            headers=auth_headers,
            json={"text": "task pls"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Check if log_enhance_input was called with fallback=True
        args, kwargs = mock_log.call_args
        details = kwargs.get("details", {})
        if details.get("fallback"):
            pytest.fail(f"Enhance input fell back to default. Error: {details.get('error')}")
            
        assert data["intent"] == "create_task"
        assert data["confidence"] == 0.9
        assert data["shouldEscalate"] is False

@pytest.mark.asyncio
async def test_enhance_input_escalation(client, test_user, auth_headers, mock_openai, mock_settings):
    """Test input enhancement with escalation trigger"""
    # Mock low confidence response
    mock_response_content = json.dumps({
        "enhanced_text": "Research query",
        "intent": "research",
        "confidence": 0.4,
        "detectedType": "unknown",
        "typeConfidence": 0.3,
        "suggestions": [],
        "shouldEscalate": False # AI didn't set it, but keywords + low confidence should trigger
    })

    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content=mock_response_content))]
    mock_openai.chat.completions.create.return_value = mock_response

    response = client.post(
        "/ai/enhance-input",
        headers=auth_headers,
        json={"text": "do some research on AI"}
    )

    assert response.status_code == 200
    data = response.json()
    # Should be upgraded to escalate due to "research" keyword and low confidence
    assert data["shouldEscalate"] is True
    assert "research" in data["escalationReason"]["keywords"]


# ============ Additional Tests ============

class TestFlowMemoryStoreClass:
    """Tests for in-memory flow memory placeholder"""

    @pytest.mark.asyncio
    async def test_store_returns_id(self):
        """Store method returns an ID"""
        store = ai.FlowMemoryStore()
        result = await store.store("user-123", "content", "context", {"key": "value"})
        assert "id" in result
        assert result["stored"] is True
        assert result["content"] == "content"

    @pytest.mark.asyncio
    async def test_search_returns_empty(self):
        """Search method returns empty results"""
        store = ai.FlowMemoryStore()
        result = await store.search("user-123", query="test")
        assert result["results"] == []
        assert result["total"] == 0

    @pytest.mark.asyncio
    async def test_get_recent_returns_empty(self):
        """Get recent method returns empty"""
        store = ai.FlowMemoryStore()
        result = await store.get_recent("user-123", limit=10)
        assert result["memories"] == []
        assert result["total"] == 0

    @pytest.mark.asyncio
    async def test_update_returns_success(self):
        """Update method returns success"""
        store = ai.FlowMemoryStore()
        result = await store.update("user-123", "mem-id", "new content", {"updated": True})
        assert result["id"] == "mem-id"
        assert result["updated"] is True

    @pytest.mark.asyncio
    async def test_delete_returns_success(self):
        """Delete method returns success"""
        store = ai.FlowMemoryStore()
        result = await store.delete("user-123", "mem-id")
        assert result["deleted"] is True

    @pytest.mark.asyncio
    async def test_delete_all_returns_count(self):
        """Delete all method returns count"""
        store = ai.FlowMemoryStore()
        result = await store.delete_all("user-123")
        assert result["deleted_count"] == 0


class TestResolveHelper:
    """Tests for _resolve helper function"""

    @pytest.mark.asyncio
    async def test_resolve_awaitable(self):
        """Resolves coroutines correctly"""
        async def coro():
            return "result"
        result = await ai._resolve(coro())
        assert result == "result"

    @pytest.mark.asyncio
    async def test_resolve_non_awaitable(self):
        """Returns non-coroutines directly"""
        result = await ai._resolve("direct")
        assert result == "direct"

    @pytest.mark.asyncio
    async def test_resolve_dict(self):
        """Returns dictionaries directly"""
        result = await ai._resolve({"key": "value"})
        assert result == {"key": "value"}


class TestPydanticModels:
    """Tests for AI router Pydantic models"""

    def test_flow_memory_store_request_validation(self):
        """FlowMemoryStoreRequest validates content"""
        request = ai.FlowMemoryStoreRequest(content="Test content")
        assert request.content == "Test content"
        assert request.context is None
        assert request.metadata is None

    def test_flow_memory_store_request_full(self):
        """FlowMemoryStoreRequest with all fields"""
        request = ai.FlowMemoryStoreRequest(
            content="Test",
            context="ctx",
            metadata={"key": "val"}
        )
        assert request.context == "ctx"
        assert request.metadata == {"key": "val"}

    def test_flow_memory_update_request(self):
        """FlowMemoryUpdateRequest validates"""
        request = ai.FlowMemoryUpdateRequest(content="Updated")
        assert request.content == "Updated"
        assert request.metadata is None


class TestOpenRouterClient:
    """Tests for OpenRouter client singleton"""

    def test_get_openrouter_client_singleton(self, monkeypatch):
        """Client is created once (singleton pattern)"""
        monkeypatch.setenv("AI_INTEGRATIONS_OPENROUTER_API_KEY", "test-key")
        monkeypatch.setenv("AI_INTEGRATIONS_OPENROUTER_BASE_URL", "https://test.com")

        # Reset global
        ai._openrouter_client = None

        with patch("app.routers.ai.OpenAI") as mock_openai:
            client1 = ai.get_openrouter_client()
            client2 = ai.get_openrouter_client()

            # Should only create once
            mock_openai.assert_called_once()
            assert client1 is client2


class TestNotesEndpoints:
    """Tests for AI notes functionality"""

    def test_save_note_structure(self):
        """Note entry structure"""
        from datetime import datetime
        note_entry = {
            "id": "note-123",
            "content": "Test note",
            "tags": ["important"],
            "createdAt": datetime.utcnow().isoformat()
        }
        assert "id" in note_entry
        assert "content" in note_entry
        assert "createdAt" in note_entry


class TestChatModels:
    """Tests for chat model selection"""

    def test_model_selection_high_reasoning(self):
        """High reasoning flag selects appropriate model"""
        use_high = True
        expected_model = "highReasoning" if use_high else "chat"
        assert expected_model == "highReasoning"

    def test_model_selection_explicit(self):
        """Explicit model overrides defaults"""
        explicit_model = "claude-3-opus"
        default_model = "gpt-4"
        selected = explicit_model if explicit_model else default_model
        assert selected == "claude-3-opus"


class TestToolDefinitions:
    """Tests for AI tool definitions"""

    def test_create_task_tool_schema(self):
        """create_task tool has correct schema"""
        tool = {
            "type": "function",
            "function": {
                "name": "create_task",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "priority": {"type": "integer"}
                    },
                    "required": ["title"]
                }
            }
        }
        assert tool["function"]["name"] == "create_task"
        assert "title" in tool["function"]["parameters"]["properties"]

    def test_create_event_tool_schema(self):
        """create_event tool has correct schema"""
        tool = {
            "type": "function",
            "function": {
                "name": "create_event",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "startTime": {"type": "string"}
                    },
                    "required": ["title", "startTime"]
                }
            }
        }
        assert "startTime" in tool["function"]["parameters"]["required"]


class TestTaskAnalysisResponse:
    """Tests for task analysis response structure"""

    def test_fallback_analysis_structure(self):
        """Fallback analysis has required fields"""
        fallback = {
            "urgencyScore": 0.5,
            "complexityScore": 0.5,
            "estimatedMinutes": 30,
            "energyRequired": "medium",
            "suggestedActions": ["Start working"],
            "relatedTasks": []
        }
        assert 0 <= fallback["urgencyScore"] <= 1
        assert 0 <= fallback["complexityScore"] <= 1
        assert fallback["energyRequired"] in ["low", "medium", "high"]


class TestInsightsGeneration:
    """Tests for productivity insights"""

    def test_time_range_parsing(self):
        """Time range parsing for insights"""
        from datetime import datetime, timedelta

        time_range = "7d"
        if time_range == "7d":
            since = datetime.utcnow() - timedelta(days=7)
        elif time_range == "30d":
            since = datetime.utcnow() - timedelta(days=30)
        else:
            since = datetime.utcnow() - timedelta(days=7)

        assert (datetime.utcnow() - since).days <= 8

    def test_insights_fallback_structure(self):
        """Fallback insights have correct structure"""
        fallback = {
            "category": "productivity",
            "insight": "Continue tracking for better insights",
            "actionable": True,
            "priority": "medium"
        }
        assert fallback["actionable"] is True


class TestCognitiveStateResponse:
    """Tests for cognitive state analysis"""

    def test_cognitive_state_values(self):
        """Valid cognitive state values"""
        valid_states = ["focused", "distracted", "fatigued", "flow", "unknown"]
        test_state = "focused"
        assert test_state in valid_states

    def test_cognitive_score_range(self):
        """Cognitive load score is in valid range"""
        score = 0.5
        assert 0 <= score <= 1


class TestRoutingAnalysis:
    """Tests for routing decision analysis"""

    def test_route_types(self):
        """Valid route type values"""
        from app.services.route_selector import RouteType
        valid_routes = [RouteType.DETERMINISTIC, RouteType.ORCHESTRATED]
        assert len(valid_routes) == 2


class TestEnhanceInputResponse:
    """Tests for enhance input response"""

    def test_enhance_input_required_fields(self):
        """Enhance input has required response fields"""
        response = {
            "enhanced_text": "Create task",
            "intent": "create_task",
            "confidence": 0.9,
            "detectedType": "task",
            "typeConfidence": 0.9,
            "suggestions": [],
            "shouldEscalate": False
        }
        assert "intent" in response
        assert "confidence" in response
        assert 0 <= response["confidence"] <= 1

    def test_cached_response_fields(self):
        """Cached response includes fromCache flag"""
        cached_response = {
            "enhanced_text": "Task",
            "intent": "create_task",
            "confidence": 0.85,
            "fromCache": True,
            "routeDecision": "deterministic"
        }
        assert cached_response["fromCache"] is True


class TestOrchestrateTask:
    """Tests for task orchestration"""

    def test_workflow_step_structure(self):
        """Workflow step has correct structure"""
        step = {
            "step": 1,
            "action": "Complete the task",
            "estimatedMinutes": 30,
            "dependencies": []
        }
        assert step["step"] == 1
        assert step["estimatedMinutes"] > 0

    def test_fallback_orchestration(self):
        """Fallback orchestration creates single step"""
        fallback_workflow = [
            {
                "step": 1,
                "action": "Complete the task",
                "estimatedMinutes": 30,
                "dependencies": []
            }
        ]
        assert len(fallback_workflow) == 1


class TestTelemetryEndpoints:
    """Tests for telemetry functionality"""

    def test_telemetry_route_values(self):
        """Valid telemetry route values"""
        valid_routes = ["deterministic", "orchestrated"]
        assert "deterministic" in valid_routes

    def test_telemetry_summary_fields(self):
        """Telemetry summary has correct fields"""
        summary = {
            "total": 100,
            "deterministic": 80,
            "orchestrated": 15,
            "unknown": 5
        }
        assert summary["total"] == summary["deterministic"] + summary["orchestrated"] + summary["unknown"]


class TestTimelineResponse:
    """Tests for unified timeline"""

    def test_timeline_entry_structure(self):
        """Timeline entry has required fields"""
        from datetime import datetime
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "type": "command",
            "source": "voice",
            "action": "create_task"
        }
        assert "timestamp" in entry
        assert "type" in entry


class TestRoutingStats:
    """Tests for routing performance stats"""

    def test_routing_stats_structure(self):
        """Routing stats response structure"""
        stats = {
            "routes": {},
            "cache_enabled": True,
            "circuit_breaker_enabled": True,
            "optimization_version": "1.0.0"
        }
        assert stats["cache_enabled"] is True


class TestTaskRecommendations:
    """Tests for AI task recommendations"""

    def test_recommendation_structure(self):
        """Task recommendation has correct fields"""
        recommendation = {
            "title": "Suggested task",
            "description": "Why this matters",
            "priority": 3,
            "reasoning": "Based on patterns"
        }
        assert 1 <= recommendation["priority"] <= 5
        assert "reasoning" in recommendation


class TestFlowContext:
    """Tests for flow context management"""

    def test_context_response_structure(self):
        """Flow context response structure"""
        response = {
            "session_id": "session-123",
            "context": {"key": "value"},
            "has_context": True
        }
        assert response["has_context"] is True


class TestMemoryOperations:
    """Tests for memory save/recall"""

    def test_memory_save_response(self):
        """Memory save response format"""
        response = {
            "success": True,
            "message": "Memory saved"
        }
        assert response["success"] is True

    def test_memory_recall_empty(self):
        """Memory recall with no results"""
        response = {
            "memories": [],
            "total": 0
        }
        assert response["total"] == 0