# Focus by Kraliki Settings Directory

This directory contains all centralized configuration files for Focus by Kraliki, making the application easily configurable without code changes.

## Structure

```
settings/
├── models/          # AI model configurations
│   └── ai_models.json
├── prompts/         # AI prompt templates
│   └── ai_prompts.json
├── workflows/       # Workflow configurations
└── README.md        # This file
```

## Why Centralized Settings?

### Before (Hardcoded):
```python
# Scattered across codebase
model="claude-3-5-sonnet-20241022"  # ai.py:93
model="google/gemini-2.5-flash-preview-09-2025"  # ai.py:163
model="z-ai/glm-4.6"  # ai.py:351
```

### After (Centralized):
```python
# Single source of truth
from app.core.settings_loader import get_model_for_use_case
model = get_model_for_use_case("chat")  # Loads from settings/models/ai_models.json
```

## Benefits

1. **Easy Updates**: Update model names in one place when new models are released
2. **Environment-Specific**: Different settings for dev/staging/prod
3. **No Code Changes**: Update configurations without touching source code
4. **Version Control**: Track configuration changes separately from code
5. **Documentation**: JSON files are self-documenting with metadata
6. **Validation**: JSON schema validation ensures correct configuration

## File Descriptions

### `models/ai_models.json`
- **Purpose**: Configure AI models for different use cases
- **Contains**: Model names, providers, fallbacks, parameters
- **Updated**: When new models are released or pricing changes
- **Schema**: Self-validating with inline documentation

**Use Cases Configured**:
- `chat` - General chat interactions
- `parseTask` - Natural language task parsing
- `enhanceInput` - Input enhancement and intent detection
- `analyzeTask` - Task analysis and insights
- `orchestrateTask` - Workflow orchestration
- `highReasoning` - Complex reasoning tasks
- `insights` - Productivity insights generation
- `taskRecommendations` - AI task suggestions
- `cognitiveState` - Cognitive state analysis
- `workflowGeneration` - Workflow template generation

### `prompts/ai_prompts.json`
- **Purpose**: Centralize all AI prompts and templates
- **Contains**: System prompts, user prompts templates, variables
- **Updated**: When prompts need refinement or new features are added
- **Benefits**: A/B testing, prompt versioning, consistency

**Prompt Types**:
- `systemPrompts` - Role/behavior definitions for AI
- `templates` - Reusable prompt templates with variables
- `escalationKeywords` - Keywords triggering II-Agent escalation

## Usage

### Backend (Python)

```python
from app.core.settings_loader import SettingsLoader

# Load settings
settings = SettingsLoader()

# Get model for use case
model = settings.get_model("chat")
# Returns: "anthropic/claude-3.5-sonnet:beta"

# Get prompt template
prompt_template = settings.get_prompt_template("parseTask")
prompt = prompt_template.format(input="Buy groceries")

# Get model config with all parameters
config = settings.get_model_config("orchestrateTask")
# Returns: {
#   "model": "google/gemini-2.0-flash-thinking-exp:free",
#   "maxTokens": 8192,
#   "temperature": 0.5
# }
```

### Frontend (TypeScript)

```typescript
import { settingsLoader } from '$lib/utils/settings-loader';

// Get model for display
const chatModel = settingsLoader.getModel('chat');

// Get all available models
const models = settingsLoader.getAllModels();
```

## Model Configuration Structure

```json
{
  "providers": {
    "openrouter": {
      "models": {
        "default": "anthropic/claude-3.5-sonnet:beta",
        "highReasoning": "x-ai/grok-2-1212"
      }
    }
  },
  "useCases": {
    "chat": {
      "modelProvider": "openrouter",
      "modelKey": "default",
      "fallback": "anthropic.default",
      "maxTokens": 8192,
      "temperature": 0.7
    }
  }
}
```

## Prompt Configuration Structure

```json
{
  "templates": {
    "parseTask": {
      "template": "Parse this input: \"{input}\"...",
      "variables": ["input"],
      "outputFormat": "json"
    }
  }
}
```

## Best Practices

1. **Version Control**: Always commit settings changes with descriptive messages
2. **Testing**: Test configuration changes in dev before production
3. **Documentation**: Update metadata sections when making changes
4. **Validation**: Validate JSON files before deployment
5. **Fallbacks**: Always configure fallback models for reliability
6. **Monitoring**: Track model costs and performance after updates

## Environment Overrides

Settings can be overridden via environment variables:

```bash
# Override chat model
FOCUS_MODEL_CHAT="anthropic/claude-3-opus-20240229"

# Override API base URL
FOCUS_OPENROUTER_BASE_URL="https://openrouter.ai/api/v1"
```

## Updating Models (2025 Example)

When OpenRouter releases new models:

1. Check OpenRouter docs: https://openrouter.ai/models
2. Update `settings/models/ai_models.json`
3. Test in development environment
4. Update `lastUpdated` timestamp
5. Commit changes
6. Deploy to production

**Recent Updates (2025)**:
- ✅ Upgraded to Gemini 2.0 Flash (from 1.5)
- ✅ Added DeepSeek R1 for reasoning tasks
- ✅ Added Gemini 2.0 Flash Thinking for orchestration
- ✅ Updated to Grok 2 (from Grok 1)
- ✅ Switched to free tier models where available

## Troubleshooting

**Model not found error**:
- Check `useCases` section has the use case defined
- Verify `modelProvider` and `modelKey` point to valid entries
- Check fallback model is configured

**Prompt rendering error**:
- Verify all `{variables}` in template are provided
- Check JSON syntax is valid
- Ensure template exists in `prompts/ai_prompts.json`

## See Also

- [API Reference](../docs/API_REFERENCE.md)
- [Model Pricing](https://openrouter.ai/models)
- [Prompt Engineering Best Practices](../docs/PROMPT_ENGINEERING.md)
