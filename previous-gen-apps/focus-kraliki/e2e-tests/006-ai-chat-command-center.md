# Test 006: AI Chat / Command Center

**Priority:** P0 (Critical)
**URL:** https://focus.verduona.dev/dashboard
**Estimated Time:** 5 minutes

## Objective

Verify the AI chat functionality and command center works correctly.

## Preconditions

- User is logged in
- On the dashboard page

## Test Steps

### Scenario A: Send a Basic Message

1. Navigate to: `https://focus.verduona.dev/dashboard`
2. Locate the AI input field
3. Type: `Hello, what can you help me with?`
4. Submit the message (press Enter or click send)

**Expected Results:**
- [ ] Message is sent successfully
- [ ] Processing indicator appears at top ("Processing...")
- [ ] User message appears in conversation
- [ ] AI response is received and displayed
- [ ] Processing indicator disappears

### Scenario B: Use Quick Prompt

1. Click on "Show urgent tasks" quick prompt button

**Expected Results:**
- [ ] Input field is populated with the prompt text
- [ ] Message is sent automatically OR ready to send
- [ ] AI processes the request
- [ ] Response related to tasks is displayed

### Scenario C: Fast Path Commands

1. Type in the input field: `+ Buy groceries`
2. Submit the message

**Expected Results:**
- [ ] Fast path is recognized (starts with +)
- [ ] Task is created directly (no AI processing needed)
- [ ] Success toast appears: "Created Task: Buy groceries"
- [ ] Input field is cleared

### Scenario D: Fast Path - Note

1. Type in the input field: `# Meeting notes from today`
2. Submit the message

**Expected Results:**
- [ ] Fast path is recognized (starts with #)
- [ ] Note is created
- [ ] Success toast appears
- [ ] Input field is cleared

### Scenario E: Model Selection (if available)

1. Look for model selection dropdown
2. Check available models

**Expected Results:**
- [ ] Model selector shows options:
  - Darwin2 Swarm (Auto)
  - Claude 3.5 Sonnet
  - Claude Haiku 4.5
  - GPT-4o mini

## Fast Path Command Reference

| Prefix | Type | Example |
|--------|------|---------|
| `+` | Task | `+ Call John` |
| `/task` | Task | `/task Review PR` |
| `#` | Note | `# Idea for feature` |
| `/note` | Note | `/note Remember this` |
| `/idea` | Idea | `/idea New feature concept` |
| `/bug` | Bug | `/bug Button not working` |

## Error Handling

### Scenario F: Empty Message

1. Leave input field empty
2. Try to submit

**Expected Results:**
- [ ] Nothing happens (empty messages not sent)
- [ ] No error message needed

### Scenario G: Network Error

1. Disable network (if testable)
2. Send a message

**Expected Results:**
- [ ] Error message appears in conversation
- [ ] Processing indicator stops
- [ ] User can retry

## Pass Criteria

- Basic messages are sent and receive responses
- Quick prompts work correctly
- Fast path commands create items
- Error states are handled gracefully

## Screenshots Required

1. AI canvas before sending message
2. Processing state (indicator visible)
3. Conversation with user and AI messages
4. Fast path success toast
