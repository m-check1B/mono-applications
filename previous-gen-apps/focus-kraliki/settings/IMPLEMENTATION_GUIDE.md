# Settings Implementation Guide

This guide shows how to migrate from hardcoded values to the centralized settings system.

## Quick Start

### Backend Migration

**Before (Hardcoded)**:
```python
# backend/app/routers/ai.py line 93
model_name = "claude-3-5-sonnet-20241022"

# backend/app/routers/ai.py line 163
model="google/gemini-2.5-flash-preview-09-2025"

# backend/app/routers/ai.py line 351
model="z-ai/glm-4.6"
```

**After (Centralized)**:
```python
from app.core.settings_loader import get_model_for_use_case, get_model_config

# Simple model name
model_name = get_model_for_use_case("chat")

# With full config (model + parameters)
config = get_model_config("parseTask")
model = config["model"]
max_tokens = config["maxTokens"]
temperature = config["temperature"]

# Use in API call
response = client.chat.completions.create(
    model=config["model"],
    max_tokens=config["maxTokens"],
    temperature=config["temperature"],
    messages=messages
)
```

### Prompt Migration

**Before (Hardcoded)**:
```python
# backend/app/routers/ai.py line 147-160
prompt = f"""Parse this natural language input into a structured task:

Input: "{request.input}"

Return a JSON object with:
- title: string (concise task title)
- description: string (optional details)
...
"""
```

**After (Centralized)**:
```python
from app.core.settings_loader import get_prompt_template

# Load and format prompt
prompt = get_prompt_template("parseTask", input=request.input)

# Prompts with multiple variables
prompt = get_prompt_template(
    "enhanceInput",
    text=request.text,
    context=json.dumps(request.context or {})
)
```

---

## Step-by-Step Migration

### 1. Install Settings Loader

The settings loader is already created at:
```
backend/app/core/settings_loader.py
```

### 2. Migrate AI Router (ai.py)

**File**: `backend/app/routers/ai.py`

#### Import Settings Loader

Add to imports (line ~10):
```python
from app.core.settings_loader import (
    get_model_for_use_case,
    get_model_config,
    get_prompt_template,
    get_escalation_keywords
)
```

#### Update `/chat` endpoint (line 79-139)

**Current**:
```python
if request.model:
    model_name = request.model
elif request.useHighReasoning:
    model_name = "x-ai/grok-4-fast"
else:
    model_name = "claude-3-5-sonnet-20241022"
```

**New**:
```python
if request.model:
    model_name = request.model
elif request.useHighReasoning:
    model_name = get_model_for_use_case("highReasoning")
else:
    model_name = get_model_for_use_case("chat")
```

#### Update `/parse-task` endpoint (line 141-186)

**Current**:
```python
prompt = f"""Parse this natural language input into a structured task:

Input: "{request.input}"
...
"""

response = get_openrouter_client().chat.completions.create(
    model="google/gemini-2.5-flash-preview-09-2025",
    messages=[{"role": "user", "content": prompt}],
    max_tokens=8192
)
```

**New**:
```python
prompt = get_prompt_template("parseTask", input=request.input)
config = get_model_config("parseTask")

response = get_openrouter_client().chat.completions.create(
    model=config["model"],
    messages=[{"role": "user", "content": prompt}],
    max_tokens=config["maxTokens"]
)
```

#### Update `/enhance-input` endpoint (line 188-306)

**Current**:
```python
prompt = f"""Enhance and analyze this user input: "{request.text}"

Context: {json.dumps(request.context or {}, indent=2)}
...
"""

# Hardcoded escalation keywords
escalation_keywords = ["research", "code", "website", "browser", "scrape", "gather", "analyze code"]
```

**New**:
```python
prompt = get_prompt_template(
    "enhanceInput",
    text=request.text,
    context=json.dumps(request.context or {})
)

# Load from config
escalation_keywords = get_escalation_keywords()
```

#### Update `/analyze-task` endpoint (line 308-373)

**Current**:
```python
prompt = f"""Analyze this task:

Title: {task.title}
Description: {task.description or "None"}
...
"""

response = get_openrouter_client().chat.completions.create(
    model="z-ai/glm-4.6",
    ...
)
```

**New**:
```python
prompt = get_prompt_template(
    "analyzeTask",
    title=task.title,
    description=task.description or "None",
    priority=task.priority,
    tags=task.tags,
    status=task.status.value
)

config = get_model_config("analyzeTask")
response = get_openrouter_client().chat.completions.create(
    model=config["model"],
    max_tokens=config["maxTokens"],
    ...
)
```

#### Update `/orchestrate-task` endpoint (line 375-492)

**Current**:
```python
model = "moonshotai/kimi-k2-thinking" if request.useHighReasoning else "google/gemini-2.5-flash-preview-09-2025"
```

**New**:
```python
use_case = "highReasoning" if request.useHighReasoning else "orchestrateTask"
config = get_model_config(use_case)
model = config["model"]
```

#### Update `/high-reasoning` endpoint (line 584-615)

**Current**:
```python
messages = [
    {"role": "system", "content": "You are an expert AI assistant with advanced reasoning capabilities."},
    {"role": "user", "content": request.prompt}
]

response = get_openrouter_client().chat.completions.create(
    model="openrouter/polaris-alpha",
    ...
)
```

**New**:
```python
system_prompt = get_system_prompt("highReasoning")
messages = [
    system_prompt,
    {"role": "user", "content": request.prompt}
]

config = get_model_config("highReasoning")
response = get_openrouter_client().chat.completions.create(
    model=config["model"],
    max_tokens=config.get("maxTokens", request.maxTokens),
    ...
)
```

#### Update other endpoints similarly

Apply the same pattern to:
- `/insights` (line 617-692) - Use `insights` use case
- `/task-recommendations` (line 694-748) - Use `taskRecommendations`
- `/cognitive-state` (line 750-785) - Use `cognitiveState`

---

### 3. Migrate Workflow Router (workflow.py)

**File**: `backend/app/routers/workflow.py`

#### Import Settings Loader

```python
from app.core.settings_loader import get_model_config, get_prompt_template
```

#### Update `/generate` endpoint (line 345-431)

**Current**:
```python
prompt = f"""Create a detailed workflow template from this description:

Description: "{description}"
Category: {category or "general"}
...
"""

response = get_anthropic_client().messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=2000,
    messages=[{"role": "user", "content": prompt}]
)
```

**New**:
```python
prompt = get_prompt_template(
    "generateWorkflow",
    description=description,
    category=category or "general"
)

config = get_model_config("workflowGeneration")
response = get_anthropic_client().messages.create(
    model=config["model"],
    max_tokens=config["maxTokens"],
    messages=[{"role": "user", "content": prompt}]
)
```

---

### 4. Testing the Migration

Create a test file to verify the migration:

**File**: `backend/tests/test_settings_migration.py`

```python
import pytest
from app.core.settings_loader import (
    get_model_for_use_case,
    get_model_config,
    get_prompt_template,
    get_escalation_keywords
)


def test_model_loading():
    """Test that models load correctly"""
    model = get_model_for_use_case("chat")
    assert model is not None
    assert isinstance(model, str)


def test_model_config():
    """Test full config loading"""
    config = get_model_config("chat")
    assert "model" in config
    assert "maxTokens" in config
    assert "temperature" in config


def test_prompt_template():
    """Test prompt template loading and formatting"""
    prompt = get_prompt_template("parseTask", input="Buy groceries")
    assert "Buy groceries" in prompt
    assert "JSON" in prompt  # Should contain instruction to return JSON


def test_escalation_keywords():
    """Test escalation keywords loading"""
    keywords = get_escalation_keywords()
    assert isinstance(keywords, list)
    assert len(keywords) > 0
    assert "research" in keywords


def test_all_use_cases():
    """Test that all use cases have valid models"""
    use_cases = [
        "chat",
        "parseTask",
        "enhanceInput",
        "analyzeTask",
        "orchestrateTask",
        "highReasoning",
        "insights",
        "taskRecommendations",
        "cognitiveState",
        "workflowGeneration"
    ]

    for use_case in use_cases:
        model = get_model_for_use_case(use_case)
        assert model is not None, f"Model not found for use case: {use_case}"
        assert isinstance(model, str)
```

Run tests:
```bash
cd backend
uv run pytest tests/test_settings_migration.py -v
```

---

### 5. Gradual Rollout Strategy

**Phase 1 - Non-Critical Endpoints** (Week 1):
- Migrate `/parse-task`
- Migrate `/task-recommendations`
- Migrate `/cognitive-state`
- Test in development

**Phase 2 - Core Endpoints** (Week 2):
- Migrate `/chat`
- Migrate `/enhance-input`
- Migrate `/orchestrate-task`
- Monitor in staging

**Phase 3 - Advanced Features** (Week 3):
- Migrate `/analyze-task`
- Migrate `/insights`
- Migrate `/high-reasoning`
- Migrate `/workflow/generate`

**Phase 4 - Cleanup** (Week 4):
- Remove all hardcoded model names
- Remove all hardcoded prompts
- Update documentation
- Deploy to production

---

### 6. Frontend Integration (Optional)

If you want to expose model selection in the frontend:

**File**: `frontend/src/lib/utils/settings-loader.ts`

```typescript
// Simple TypeScript interface for settings
interface ModelConfig {
  model: string;
  maxTokens: number;
  temperature: number;
}

export async function getAvailableModels(): Promise<string[]> {
  // Fetch from backend API that exposes settings
  const response = await fetch('/api/settings/models');
  return response.json();
}

export async function getModelForUseCase(useCase: string): Promise<string> {
  const response = await fetch(`/api/settings/models/${useCase}`);
  const data = await response.json();
  return data.model;
}
```

Add backend endpoint to expose settings:

```python
# backend/app/routers/settings.py
from fastapi import APIRouter
from app.core.settings_loader import get_settings_loader

router = APIRouter(prefix="/settings", tags=["settings"])

@router.get("/models")
async def get_available_models():
    """Get list of all configured models"""
    loader = get_settings_loader()
    return {
        "useCases": loader.get_all_use_cases(),
        "providers": loader.get_all_providers()
    }

@router.get("/models/{use_case}")
async def get_model_for_use_case(use_case: str):
    """Get model for a specific use case"""
    loader = get_settings_loader()
    return {
        "useCase": use_case,
        "model": loader.get_model_for_use_case(use_case),
        "config": loader.get_model_config(use_case)
    }
```

---

## Troubleshooting

### Settings Not Loading

**Problem**: `ValueError: Models configuration not loaded`

**Solution**:
```bash
# Check settings files exist
ls -la settings/models/ai_models.json
ls -la settings/prompts/ai_prompts.json

# Verify JSON is valid
python3 -m json.tool settings/models/ai_models.json
python3 -m json.tool settings/prompts/ai_prompts.json
```

### Model Not Found

**Problem**: `ValueError: Use case 'xyz' not found in configuration`

**Solution**: Add the use case to `settings/models/ai_models.json`:

```json
{
  "useCases": {
    "xyz": {
      "modelProvider": "openrouter",
      "modelKey": "default",
      "fallback": "anthropic.default",
      "maxTokens": 8192,
      "temperature": 0.7
    }
  }
}
```

### Template Variable Missing

**Problem**: `ValueError: Missing required variable 'xyz' for template 'abc'`

**Solution**: Provide all required variables when calling template:

```python
# Check what variables are required
loader = get_settings_loader()
templates = loader._prompts_config["templates"]
required_vars = templates["abc"]["variables"]
print(f"Required: {required_vars}")

# Provide all variables
prompt = get_prompt_template("abc", var1="value1", var2="value2")
```

---

## Benefits Checklist

After migration, you'll have:

- ✅ Single source of truth for all AI configurations
- ✅ Easy model updates without code changes
- ✅ Consistent prompt formatting across all endpoints
- ✅ Environment-specific configurations
- ✅ Fallback mechanisms for reliability
- ✅ Better testability and maintainability
- ✅ Documentation in JSON files
- ✅ Version control for configurations

---

## Next Steps

1. Start with Phase 1 migrations
2. Run tests after each migration
3. Monitor API performance and costs
4. Update models as new ones are released
5. Refine prompts based on user feedback

For questions, see [settings/README.md](./README.md) or check the [API Reference](../docs/API_REFERENCE.md).
