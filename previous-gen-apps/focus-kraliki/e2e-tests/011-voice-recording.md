# Test 011: Voice Recording

**Priority:** P2 (Medium)
**URL:** https://focus.verduona.dev/dashboard
**Estimated Time:** 5 minutes

## Objective

Verify voice recording functionality works for voice-to-task and voice commands.

## Preconditions

- User is logged in
- On the dashboard page
- Microphone permission available
- Voice Transcription feature enabled in settings

## Test Steps

### Scenario A: Voice Button Visibility

1. Navigate to: `https://focus.verduona.dev/dashboard`
2. Locate the voice recording button in AI canvas

**Expected Results:**
- [ ] Voice/microphone button is visible
- [ ] Button is interactive (not disabled)
- [ ] Indicates voice feature is available

### Scenario B: Check Microphone Support

1. Verify browser supports MediaRecorder API

**Expected Results:**
- [ ] `supportsRecording` is true
- [ ] Voice button is functional

### Scenario C: Start Recording

1. Click the voice/microphone button
2. Allow microphone access if prompted

**Expected Results:**
- [ ] Browser prompts for microphone permission (first time)
- [ ] Recording starts after permission granted
- [ ] Visual indicator shows recording in progress
- [ ] Recording button may change state (e.g., red, pulsing)

### Scenario D: Stop Recording

1. With recording active
2. Click the stop/microphone button again

**Expected Results:**
- [ ] Recording stops
- [ ] Audio is processed
- [ ] Processing indicator appears
- [ ] Transcription is generated

### Scenario E: Recording to Action

1. Record a voice message: "Create a task to buy milk"
2. Stop recording

**Expected Results:**
- [ ] Audio is transcribed
- [ ] Intent is detected (create_task)
- [ ] Task panel may open
- [ ] Task is created or ready to create

### Scenario F: Voice Provider Selection

1. Look for voice provider selector in canvas

**Expected Results:**
- [ ] Provider options visible:
  - Gemini Native
  - OpenAI Realtime
- [ ] Can switch between providers
- [ ] Setting is applied

### Scenario G: Recording Error

1. Deny microphone permission
2. Try to start recording

**Expected Results:**
- [ ] Error message appears
- [ ] "Microphone access denied" or similar
- [ ] Recording does not start

### Scenario H: Feature Disabled

1. Go to Settings panel
2. Disable Voice Transcription
3. Return to dashboard

**Expected Results:**
- [ ] Voice button is hidden or disabled
- [ ] Cannot start recording

## Voice Processing Flow

1. User clicks record
2. Audio is captured (WebM format)
3. Audio is uploaded to backend
4. Backend transcribes via Gemini/OpenAI/Deepgram
5. Intent is extracted
6. Action is performed (create task, schedule event, etc.)

## Intent Types

| Intent | Action |
|--------|--------|
| create_task | Opens tasks panel, creates task |
| update_task | Updates existing task |
| schedule_event | Opens calendar, creates event |
| start_timer | Starts focus timer |
| stop_timer | Stops timer |
| run_workflow | Opens workflow panel |
| question | Sends to AI chat |
| command | Executes command |

## Pass Criteria

- Voice button is visible when feature enabled
- Can start and stop recording
- Audio is transcribed correctly
- Intent detection works
- Feature can be disabled in settings

## Screenshots Required

1. Voice button visible in AI canvas
2. Recording in progress state
3. Processing audio state
4. Transcription result
