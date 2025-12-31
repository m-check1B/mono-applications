# Week 7-8 Call Center Operations - Implementation Checklist

**Purpose:** Quick reference for developers implementing Week 7-8 features  
**Last Updated:** November 11, 2025

---

## Phase 1: Complete Queue Management (2-3 days) ⏳

### Backend - Queue Configuration
- [ ] Create `QueueConfig` model in `models/supervisor.py`
  ```python
  class QueueConfig:
    - id, team_id, queue_name
    - max_queue_size, max_wait_time
    - overflow_destination
    - skill_requirements (JSON)
    - ivr_greeting, hold_music_url
  ```
- [ ] Add `QueueConfigService` methods
  ```python
  - create_queue()
  - update_queue()
  - delete_queue()
  - get_queue_settings()
  ```
- [ ] Create API endpoints
  ```
  POST /api/supervisor/queues - Create queue
  GET /api/supervisor/queues - List queues
  PUT /api/supervisor/queues/{id} - Update config
  DELETE /api/supervisor/queues/{id} - Delete queue
  ```

### Backend - Skill-Based Routing
- [ ] Enhance `assign_to_agent()` in SupervisorService
  - Implement skill matching algorithm
  - Check required_skills against agent.skills
  - Implement skill proficiency scoring
- [ ] Add tests for skill routing
- [ ] Create SkillMatcher utility class

### Backend - Enhanced Statistics
- [ ] Add SLA metrics to queue statistics
  ```
  - service_level_percentage (% answered within SLA)
  - occupancy_rate (talk time / available time)
  - average_handle_time
  - adherence_percentage
  ```
- [ ] Create QueueMetricsService

### Frontend - Queue Management UI
- [ ] Create `/supervisor/queues/config` page
  - Queue creation form
  - Queue settings panel
  - Queue status display
- [ ] Add components:
  - QueueConfigForm
  - QueueStatusCard
  - SkillRequirementsSelector
- [ ] Enhance dashboard with queue metrics

### Testing
- [ ] Unit tests for skill matching
- [ ] Integration tests for queue configuration
- [ ] E2E tests for queue operations
- [ ] Load test queue under stress

---

## Phase 2: IVR System (5-7 days) 🔴

### Database Schema
- [ ] Create migration for IVR tables
  ```sql
  - ivr_flows (id, name, description, status)
  - ivr_menus (id, flow_id, name, prompt_text)
  - ivr_menu_options (id, menu_id, key, action_type, target)
  - ivr_scripts (id, text, language, audio_url)
  - ivr_logs (id, call_id, flow_traversal_json)
  ```

### Backend Models
- [ ] Implement `IVRFlow` model
- [ ] Implement `IVRMenu` model
- [ ] Implement `IVRMenuOption` model
- [ ] Implement `IVRScript` model
- [ ] Add Pydantic schemas for API validation

### Backend Services
- [ ] Create `IVRService` class
  ```python
  - start_ivr_flow(call_id, flow_id)
  - handle_dtmf_input(call_id, key)
  - handle_speech_input(call_id, text)
  - play_prompt(menu_id)
  - transfer_to_agent(call_id, target)
  - handle_timeout(call_id, menu_id)
  - log_ivr_event(call_id, event)
  ```
- [ ] Implement flow traversal logic
- [ ] Add DTMF/speech parsing

### Backend API
- [ ] Create `ivr.py` router
  ```
  GET /api/ivr/flows - List flows
  POST /api/ivr/flows - Create flow
  PUT /api/ivr/flows/{id} - Update flow
  DELETE /api/ivr/flows/{id} - Delete flow
  GET /api/ivr/flows/{id} - Get flow details
  POST /api/ivr/{flow_id}/start - Start IVR session
  POST /api/ivr/{flow_id}/input - Send DTMF/voice input
  GET /api/ivr/logs - Get IVR logs
  ```

### Frontend - Visual Flow Builder
- [ ] Create IVRFlowBuilder component
  - Drag-drop menu nodes
  - Connect nodes with arrows
  - Edit node properties
- [ ] Create MenuNodeEditor
  - Key mapping (0-9, *, #)
  - Action type selector (navigate, transfer, voicemail, end)
  - Target selection

### Frontend - IVR Management Pages
- [ ] `/operations/ivr` - Main IVR page
  - List flows with CRUD operations
  - Quick actions (test, preview)
- [ ] `/operations/ivr/builder` - Visual flow editor
  - Drag-drop interface
  - Flow validation
  - Save/version control
- [ ] `/operations/ivr/scripts` - Script library
  - Manage prompts/scripts
  - Upload audio files
  - TTS preview

### Testing
- [ ] Unit tests for flow navigation
- [ ] DTMF input parsing tests
- [ ] End-to-end flow traversal tests
- [ ] Builder UI tests

---

## Phase 3: Call Routing Engine (3-5 days) 🔴

### Database Schema
- [ ] Create migration for routing tables
  ```sql
  - routing_rules (id, name, priority, strategy)
  - routing_conditions (id, rule_id, condition_json)
  - routing_targets (id, rule_id, target_type, target_id)
  - routing_logs (id, call_id, rule_applied, target)
  ```

### Backend Models
- [ ] Implement `RoutingRule` model
- [ ] Implement `RoutingCondition` model
- [ ] Implement `RoutingTarget` model
- [ ] Add routing strategy enum

### Backend Services
- [ ] Create `RoutingService` class
  ```python
  - evaluate_rule(call, rule)
  - select_target(rule, available_agents)
  - match_skills(agent, required_skills)
  - match_language(agent, required_language)
  - get_least_busy_agent(agents)
  - route_call(call_id)
  - log_routing_decision(call_id, rule, target)
  ```
- [ ] Implement routing algorithms:
  - Skill-based matching
  - Language matching
  - Least active calls
  - Round-robin
  - Custom conditions

### Backend API
- [ ] Create `routing.py` router
  ```
  GET /api/routing/rules - List rules
  POST /api/routing/rules - Create rule
  PUT /api/routing/rules/{id} - Update rule
  DELETE /api/routing/rules/{id} - Delete rule
  GET /api/routing/strategies - Get available strategies
  POST /api/routing/rules/{id}/test - Test rule with sample call
  GET /api/routing/logs - Get routing audit logs
  ```

### Frontend - Rule Builder
- [ ] Create RoutingRuleEditor component
  - Rule name/description
  - Priority field
  - Condition builder (AND/OR logic)
  - Target selection

### Frontend - Pages
- [ ] `/operations/routing` - Manage rules
  - List all rules with status
  - Drag-drop priority ordering
  - Quick test button
- [ ] `/operations/routing/builder` - Rule editor
- [ ] `/operations/routing/test` - Rule tester
  - Simulate call scenarios
  - Show routing decision

### Testing
- [ ] Unit tests for routing algorithms
- [ ] Rule evaluation tests
- [ ] Skill matching tests
- [ ] Language matching tests
- [ ] Fallback/error handling tests

---

## Phase 4: Recording Management (2-3 days) 🟡

### Database Schema (Replace Mocks)
- [ ] Create migration for recording tables
  ```sql
  - recordings (id, call_id, agent_id, file_path, duration)
  - recording_storage (id, provider, bucket, region)
  - recording_transcripts (id, recording_id, text, language)
  ```

### Backend Models
- [ ] Implement `Recording` model
- [ ] Implement `RecordingTranscript` model
- [ ] Implement `RecordingStorage` model

### Backend Services
- [ ] Create `RecordingService` class (replace mocks in telephony.py)
  ```python
  - start_recording(call_id)
  - stop_recording(call_id, recording_path)
  - upload_to_storage(file_path, provider)
  - download_recording(recording_id, signed_url)
  - delete_recording(recording_id)
  - apply_retention_policy()
  - get_transcription(recording_id)
  ```
- [ ] Integrate with S3/Azure storage
- [ ] Add encryption support

### Backend API
- [ ] Replace mock endpoints in `telephony.py`
  ```
  POST /api/recordings - Start recording
  GET /api/recordings - List recordings
  GET /api/recordings/{id} - Get metadata
  GET /api/recordings/{id}/download - Download (signed URL)
  DELETE /api/recordings/{id} - Delete
  POST /api/recordings/{id}/transcribe - Trigger transcription
  GET /api/recordings/{id}/transcript - Get transcript
  ```

### Frontend - Recording Library
- [ ] Create `/operations/recordings` page
  - Recording list/grid view
  - Search and filter
  - Download button
  - Delete with confirmation
- [ ] Create RecordingPlayer component
  - Audio player with controls
  - Timestamp slider
  - Playback speed controls
- [ ] Create TranscriptViewer component
  - Display transcript text
  - Search within transcript
  - Highlight speaker turns

### Testing
- [ ] Storage integration tests
- [ ] Download/upload tests
- [ ] Retention policy tests
- [ ] Player UI tests

---

## Phase 5: Voicemail System (3-4 days) 🔴

### Database Schema
- [ ] Create migration for voicemail tables
  ```sql
  - voicemails (id, agent_id, caller_phone, recording_url)
  - voicemail_boxes (id, agent_id, greeting_url, settings_json)
  - voicemail_transcripts (id, voicemail_id, text)
  ```

### Backend Models
- [ ] Implement `Voicemail` model
- [ ] Implement `VoicemailBox` model
- [ ] Implement `VoicemailTranscript` model
- [ ] Add notification preferences model

### Backend Services
- [ ] Create `VoicemailService` class
  ```python
  - save_voicemail(call_id, recording_path)
  - get_voicemail_box(agent_id)
  - transcribe_voicemail(voicemail_id)
  - send_notification(voicemail_id, agent_id)
  - update_greeting(agent_id, greeting_audio)
  - mark_as_heard(voicemail_id)
  - archive_voicemail(voicemail_id)
  - delete_voicemail(voicemail_id)
  - apply_retention_policy()
  ```

### Backend API
- [ ] Create `voicemail.py` router
  ```
  GET /api/voicemails - List voicemails
  GET /api/voicemails/{id} - Get details
  PUT /api/voicemails/{id} - Mark read/archive/delete
  GET /api/voicemails/{id}/audio - Get audio
  GET /api/voicemail/settings - User settings
  PUT /api/voicemail/settings - Update settings
  POST /api/voicemail/greeting - Set greeting
  GET /api/voicemail/greeting - Get greeting
  ```

### Frontend - Voicemail Center
- [ ] Create `/operations/voicemail` page
  - Voicemail list/inbox view
  - Status (unheard, heard, archived)
  - Sort/filter options
- [ ] Create VoicemailPlayer component
  - Audio playback controls
  - Mark as heard button
  - Callback button
  - Archive/delete buttons
- [ ] Create VoicemailSettings page
  - Greeting management
  - Notification preferences (email, SMS)
  - Auto-delete settings

### Testing
- [ ] Voicemail save/retrieve tests
- [ ] Transcription tests
- [ ] Notification tests
- [ ] Retention policy tests
- [ ] Player UI tests

---

## Cross-Phase Tasks

### Database & Migrations
- [ ] Review all new schema designs
- [ ] Create clean migration files with proper rollbacks
- [ ] Test migrations up and down
- [ ] Add database indexes for performance

### Backend Integration
- [ ] Update `main.py` to register new routers
- [ ] Add new service imports
- [ ] Update API documentation (OpenAPI/Swagger)
- [ ] Add structured logging to all services

### Frontend Integration
- [ ] Add new routes to main navigation
- [ ] Create operations section in sidebar
- [ ] Update layout.svelte with new menu items
- [ ] Add TypeScript types for all API responses

### Testing & Quality
- [ ] Create comprehensive pytest suites
- [ ] Write E2E tests with Playwright
- [ ] Test error handling and edge cases
- [ ] Validate API response schemas
- [ ] Check database constraints

### Documentation
- [ ] Update API documentation
- [ ] Create user guides for each feature
- [ ] Document database schema
- [ ] Add code comments for complex logic
- [ ] Create troubleshooting guides

### Performance & Security
- [ ] Add database indexes
- [ ] Implement caching where needed
- [ ] Add rate limiting to APIs
- [ ] Validate user permissions
- [ ] Encrypt sensitive data (recordings)
- [ ] Implement audit logging

---

## Key Dependencies to Add

```python
# In requirements.txt:
boto3>=1.26.0  # AWS S3
azure-storage-blob>=12.0.0  # Azure Blob Storage
pydub>=0.25.0  # Audio format conversion
python-multipart>=0.0.5  # File uploads
aiofiles>=23.0.0  # Async file operations
```

---

## File Structure Reference

```
backend/
├── app/
│   ├── models/
│   │   ├── supervisor.py (✅ exists - queue, active_calls)
│   │   ├── recording.py (NEW - Week 4)
│   │   ├── ivr.py (NEW - Week 2)
│   │   └── routing.py (NEW - Week 3)
│   ├── services/
│   │   ├── supervisor.py (✅ exists - queue management)
│   │   ├── recording.py (NEW - Week 4)
│   │   ├── ivr.py (NEW - Week 2)
│   │   └── routing.py (NEW - Week 3)
│   └── api/
│       ├── supervisor.py (✅ exists - queue endpoints)
│       ├── recording.py (NEW - Week 4)
│       ├── ivr.py (NEW - Week 2)
│       └── routing.py (NEW - Week 3)

frontend/
├── src/
│   ├── routes/
│   │   └── operations/ (NEW - Week 7-8)
│   │       ├── queue/
│   │       ├── ivr/
│   │       ├── routing/
│   │       ├── recordings/
│   │       └── voicemail/
│   └── lib/
│       └── components/
│           ├── operations/
│           │   ├── QueueConfigForm.svelte
│           │   ├── IVRFlowBuilder.svelte
│           │   ├── RoutingRuleEditor.svelte
│           │   ├── RecordingPlayer.svelte
│           │   └── VoicemailPlayer.svelte
```

---

## Success Criteria Checklist

### Week 7-8 Complete
- [ ] All 5 features fully implemented
- [ ] Queue management enhanced with routing
- [ ] IVR system fully functional
- [ ] Call routing engine operational
- [ ] Recording management working
- [ ] Voicemail system complete
- [ ] 50+ new tests passing
- [ ] 95+ unit test code coverage
- [ ] All E2E tests passing
- [ ] Production score maintained at 90+
- [ ] Zero failing tests
- [ ] All endpoints documented in OpenAPI
- [ ] User documentation complete

---

## Testing Command Reference

```bash
# Run all backend tests
pytest backend/tests/ -v

# Run specific feature tests
pytest backend/tests/test_queue_config.py -v
pytest backend/tests/test_ivr.py -v
pytest backend/tests/test_routing.py -v
pytest backend/tests/test_recording.py -v
pytest backend/tests/test_voicemail.py -v

# Run E2E tests
pnpm test:e2e:operations

# Check coverage
pytest backend/tests/ --cov=app --cov-report=html

# Type check
mypy backend/app/

# Format check
black --check backend/
isort --check-only backend/
```

---

## Resources & References

### Existing Code Patterns
- Queue management: `/backend/app/services/supervisor.py` (588 lines)
- API patterns: `/backend/app/api/supervisor.py`
- Model patterns: `/backend/app/models/supervisor.py`
- Frontend patterns: `/frontend/src/routes/supervisor/dashboard/+page.svelte`

### Documentation
- APP_EXPANSION_PLAN.md - Full feature expansion plan
- ARCHITECTURE_DECISIONS.md - Architecture patterns
- TECHNICAL_IMPLEMENTATION_GUIDE.md - Implementation guide

---

**Status:** Ready for implementation  
**Estimated Total Time:** 42 days (15 backend + 16 frontend + 11 testing)  
**Next Steps:** Begin with Phase 1 (Queue Management enhancement)

