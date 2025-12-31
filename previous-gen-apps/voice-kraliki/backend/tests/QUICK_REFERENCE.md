# Test Directory Quick Reference

## Test File Locations

### API Tests (`/backend/tests/api/`)
Run with: `pytest tests/api/`

| Test File | Purpose |
|-----------|---------|
| test_companies_call_dispositions.py | Companies & call disposition endpoints |
| test_contract_compliance.py | Contract compliance API |
| test_health.py | Health check endpoints |
| test_providers_api.py | Providers API endpoints |
| test_provider_settings.py | Provider settings API |
| test_sessions_api.py | Sessions API endpoints |
| test_telephony_routes.py | Telephony routes |
| test_websocket_twilio.py | Twilio WebSocket functionality |

### Integration Tests (`/backend/tests/integration/`)
Run with: `pytest tests/integration/`

| Test File | Purpose |
|-----------|---------|
| test_ai_insights_integration.py | AI insights integration |
| test_ai_integration.py | AI system integration |
| test_call_state_persistence.py | Call state persistence |
| test_campaigns.py | Campaign system |
| test_circuit_breaker_integration.py | Circuit breaker integration |
| test_compliance_integration.py | Compliance integration |
| test_execution.py | Execution system |
| test_persistent_storage.py | Persistent storage |
| test_provider_switching.py | Provider switching logic |
| test_session_persistence.py | Session persistence |
| test_simple.py | Simple campaign system |
| test_structured_logging.py | Structured logging |

### Milestone Tests (`/backend/tests/milestone/`)
Run with: `pytest tests/milestone/`

| Test File | Purpose |
|-----------|---------|
| test_milestone2.py | Milestone 2 validation |
| test_milestone3.py | Milestone 3 validation |
| test_milestone3_frontend.py | Milestone 3 frontend |
| test_milestone3_health_probes.py | Milestone 3 health probes |
| test_milestone4_ai_insights.py | Milestone 4 AI insights |
| test_milestone4_artifacts.py | Milestone 4 artifacts |
| test_milestone4_workflows.py | Milestone 4 workflows |
| test_milestone5_chat.py | Milestone 5 chat |
| test_milestone6_load_testing.py | Milestone 6 load testing |
| test_milestone7_performance_metrics.py | Milestone 7 performance |
| test_milestone7_regression.py | Milestone 7 regression |
| test_milestone7_regression_simple.py | Milestone 7 simple regression |
| test_milestone7_rehearsals.py | Milestone 7 rehearsals |

### Unit Tests - Auth (`/backend/tests/unit/auth/`)
Run with: `pytest tests/unit/auth/`

| Test File | Purpose |
|-----------|---------|
| test_authentication.py | Authentication logic |

### Unit Tests - Patterns (`/backend/tests/unit/patterns/`)
Run with: `pytest tests/unit/patterns/`

| Test File | Purpose |
|-----------|---------|
| test_circuit_breaker.py | Circuit breaker pattern |

### Unit Tests - Providers (`/backend/tests/unit/providers/`)
Run with: `pytest tests/unit/providers/`

| Test File | Purpose |
|-----------|---------|
| test_auto_reconnection.py | Auto-reconnection logic |
| test_deepgram_nova3.py | Deepgram Nova 3 provider |
| test_provider_health_probes.py | Provider health checks |
| test_streaming_tts.py | Streaming TTS |

### Unit Tests - Services (`/backend/tests/unit/services/`)
Run with: `pytest tests/unit/services/`

| Test File | Purpose |
|-----------|---------|
| test_token_revocation.py | Token revocation service |
| test_webhook_security.py | Webhook security |

## Quick Commands

```bash
# Run all tests
pytest tests/

# Run specific test category
pytest tests/api/
pytest tests/integration/
pytest tests/milestone/
pytest tests/unit/

# Run specific test file
pytest tests/api/test_health.py

# Discover all tests (don't run)
pytest --collect-only -q

# Run with coverage
pytest tests/ --cov=app --cov-report=html

# Run specific test function
pytest tests/api/test_health.py::test_function_name
```

## Directory Structure

```
tests/
├── api/                    # API endpoint tests (8 files)
├── integration/            # Integration tests (12 files)
├── milestone/              # Milestone validation tests (13 files)
└── unit/                   # Unit tests
    ├── auth/              # Authentication (1 file)
    ├── patterns/          # Design patterns (1 file)
    ├── providers/         # Provider implementations (4 files)
    └── services/          # Service layer (3 files)
```

## Adding New Tests

### API Test
Place in: `/backend/tests/api/test_<feature>_api.py`

### Integration Test
Place in: `/backend/tests/integration/test_<feature>_integration.py`

### Unit Test
Place in appropriate subdirectory:
- Auth: `/backend/tests/unit/auth/test_<feature>.py`
- Pattern: `/backend/tests/unit/patterns/test_<pattern>.py`
- Provider: `/backend/tests/unit/providers/test_<provider>.py`
- Service: `/backend/tests/unit/services/test_<service>.py`

### Milestone Test
Place in: `/backend/tests/milestone/test_milestone<N>_<feature>.py`

## Test Discovery

Pytest automatically discovers tests matching these patterns:
- `test_*.py` files
- `*_test.py` files
- `Test*` classes
- `test_*` functions

All test directories have `__init__.py` files to make them proper Python packages.
