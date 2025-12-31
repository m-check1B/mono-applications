# Test File Move Manifest

**Date:** 2025-10-15
**Project:** Operator Demo 2026 Backend
**Total Files Moved:** 31

## Detailed File Moves

### From Backend Root → Unit Tests (Patterns)
```
/backend/test_circuit_breaker.py
  → /backend/tests/unit/patterns/test_circuit_breaker.py
```

### From Backend Root → Unit Tests (Providers)
```
/backend/test_auto_reconnection.py
  → /backend/tests/unit/providers/test_auto_reconnection.py

/backend/test_deepgram_nova3.py
  → /backend/tests/unit/providers/test_deepgram_nova3.py

/backend/test_streaming_tts.py
  → /backend/tests/unit/providers/test_streaming_tts.py

/backend/test_provider_health_probes.py
  → /backend/tests/unit/providers/test_provider_health_probes.py
```

### From Backend Root → Unit Tests (Services)
```
/backend/test_token_revocation.py
  → /backend/tests/unit/services/test_token_revocation.py

/backend/test_webhook_security.py
  → /backend/tests/unit/services/test_webhook_security.py
```

### From Backend Root → Integration Tests
```
/backend/test_circuit_breaker_integration.py
  → /backend/tests/integration/test_circuit_breaker_integration.py

/backend/test_call_state_persistence.py
  → /backend/tests/integration/test_call_state_persistence.py

/backend/test_session_persistence.py
  → /backend/tests/integration/test_session_persistence.py

/backend/test_compliance_integration.py
  → /backend/tests/integration/test_compliance_integration.py

/backend/test_ai_integration.py
  → /backend/tests/integration/test_ai_integration.py

/backend/test_ai_insights_integration.py
  → /backend/tests/integration/test_ai_insights_integration.py

/backend/test_campaigns.py
  → /backend/tests/integration/test_campaigns.py

/backend/test_execution.py
  → /backend/tests/integration/test_execution.py

/backend/test_persistent_storage.py
  → /backend/tests/integration/test_persistent_storage.py

/backend/test_structured_logging.py
  → /backend/tests/integration/test_structured_logging.py

/backend/test_simple.py
  → /backend/tests/integration/test_simple.py
```

### From Backend Root → Milestone Tests
```
/backend/test_milestone2.py
  → /backend/tests/milestone/test_milestone2.py

/backend/test_milestone3.py
  → /backend/tests/milestone/test_milestone3.py

/backend/test_milestone3_frontend.py
  → /backend/tests/milestone/test_milestone3_frontend.py

/backend/test_milestone3_health_probes.py
  → /backend/tests/milestone/test_milestone3_health_probes.py

/backend/test_milestone4_ai_insights.py
  → /backend/tests/milestone/test_milestone4_ai_insights.py

/backend/test_milestone4_artifacts.py
  → /backend/tests/milestone/test_milestone4_artifacts.py

/backend/test_milestone4_workflows.py
  → /backend/tests/milestone/test_milestone4_workflows.py

/backend/test_milestone5_chat.py
  → /backend/tests/milestone/test_milestone5_chat.py

/backend/test_milestone6_load_testing.py
  → /backend/tests/milestone/test_milestone6_load_testing.py

/backend/test_milestone7_performance_metrics.py
  → /backend/tests/milestone/test_milestone7_performance_metrics.py

/backend/test_milestone7_regression.py
  → /backend/tests/milestone/test_milestone7_regression.py

/backend/test_milestone7_regression_simple.py
  → /backend/tests/milestone/test_milestone7_regression_simple.py

/backend/test_milestone7_rehearsals.py
  → /backend/tests/milestone/test_milestone7_rehearsals.py
```

### From Tests Root → API Tests
```
/backend/tests/test_health.py
  → /backend/tests/api/test_health.py

/backend/tests/test_providers_api.py
  → /backend/tests/api/test_providers_api.py

/backend/tests/test_sessions_api.py
  → /backend/tests/api/test_sessions_api.py

/backend/tests/test_telephony_routes.py
  → /backend/tests/api/test_telephony_routes.py

/backend/tests/test_companies_call_dispositions.py
  → /backend/tests/api/test_companies_call_dispositions.py

/backend/tests/test_contract_compliance.py
  → /backend/tests/api/test_contract_compliance.py

/backend/tests/test_provider_settings.py
  → /backend/tests/api/test_provider_settings.py

/backend/tests/test_websocket_twilio.py
  → /backend/tests/api/test_websocket_twilio.py
```

## Files NOT Moved (Pre-existing Organized Tests)

```
/backend/tests/unit/auth/__init__.py (already exists)
/backend/tests/unit/auth/test_authentication.py (already exists)
/backend/tests/integration/test_provider_switching.py (already exists)
```

## Summary Statistics

| Category | Count |
|----------|-------|
| **Unit Tests - Patterns** | 1 |
| **Unit Tests - Providers** | 4 |
| **Unit Tests - Services** | 2 |
| **Integration Tests** | 11 |
| **Milestone Tests** | 13 |
| **API Tests** | 8 |
| **Total Files Moved** | **39** |

## New __init__.py Files Created

```
/backend/tests/api/__init__.py
/backend/tests/integration/__init__.py
/backend/tests/milestone/__init__.py
/backend/tests/unit/patterns/__init__.py
/backend/tests/unit/providers/__init__.py
/backend/tests/unit/services/__init__.py
```

## Git Operations Used

All moves were performed using `git mv` to preserve file history:

```bash
git mv test_circuit_breaker.py tests/unit/patterns/
git mv test_auto_reconnection.py test_deepgram_nova3.py test_streaming_tts.py test_provider_health_probes.py tests/unit/providers/
git mv test_token_revocation.py test_webhook_security.py tests/unit/services/
git mv test_circuit_breaker_integration.py test_call_state_persistence.py test_session_persistence.py test_compliance_integration.py test_ai_integration.py test_ai_insights_integration.py tests/integration/
git mv test_milestone*.py tests/milestone/
git mv test_campaigns.py test_execution.py test_persistent_storage.py test_structured_logging.py tests/integration/
git mv test_simple.py tests/integration/
git mv tests/test_health.py tests/test_providers_api.py tests/test_sessions_api.py tests/test_telephony_routes.py tests/api/
git mv tests/test_companies_call_dispositions.py tests/test_contract_compliance.py tests/test_provider_settings.py tests/test_websocket_twilio.py tests/api/
```

## Verification

- ✅ No test files remain in `/backend/` root
- ✅ All test files have `__init__.py` in their directories
- ✅ Pytest discovers 158 tests successfully
- ✅ Git history preserved for all moved files
- ✅ Total test files in tests directory: 51 (including __init__.py files)

## Next Steps

1. Commit the reorganization changes
2. Update CI/CD pipelines if they reference specific test paths
3. Update documentation to reflect new test structure
4. Fix the 9 pre-existing import errors in application code
