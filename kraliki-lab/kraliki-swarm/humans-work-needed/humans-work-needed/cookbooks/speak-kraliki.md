# Mac Computer Use Cookbook: Speak by Kraliki

**App:** speak-kraliki
**Type:** Web App (AI Voice Employee Feedback)
**Status:** Development

---

## Purpose

This cookbook provides instructions for Anthropic Mac Computer Use to perform visual and manual testing of the Speak by Kraliki platform.

---

## Access Information

### Admin (Company) Console

| Item | Value |
|------|-------|
| Frontend URL (dev) | `http://127.0.0.1:5175` |
| Backend API (dev) | `http://127.0.0.1:8020` |
| Access Method | Email + password (register/login) |
| Test Account | Use a test company email (if unavailable, request access) |

### Employee Check-in

| Item | Value |
|------|-------|
| Check-in URL | `http://127.0.0.1:5175/v/{token}` |
| Transcript Review | `http://127.0.0.1:5175/v/{token}/transcript` |
| Access Method | Token from survey invitation |
| Test Token | Generate via survey launch or request one |

---

## Visual Elements to Verify

### 1. Landing / Login

**Expected Elements:**
- Speak by Kraliki branding
- Login form (email, password)
- Link to registration

**Screenshot Reference:**
```
Expected format:
------------------------------------------
SPEAK BY KRALIKI
[ Email input ]
[ Password input ]
[ Login button ]
Register link
------------------------------------------
```

### 2. Registration

**Expected Elements:**
- Company registration form
- Required fields highlighted
- Success confirmation or redirect to dashboard

### 3. Dashboard Overview

**Expected Elements:**
- KPI tiles (sentiment, participation, trends)
- Signal clusters / topics panel
- Live alert stream
- Execution timeline (Action Loop)
- "New Campaign" button

### 4. Surveys Management

**Expected Elements:**
- Survey list with status
- Create survey modal with name, description, frequency
- Launch/Pause buttons per survey

### 5. Employees

**Expected Elements:**
- Employee list table
- Add employee modal
- CSV import section (file upload)
- Fields: first name, last name, email, department, job title

### 6. Alerts & Actions

**Expected Elements:**
- Alerts list with severity and timestamps
- Action items list with status (open/resolved)
- Create action flow

---

## Voice Check-in Flow

### Consent Screen (Trust Layer)

**Expected Elements:**
- Consent copy explaining anonymity and usage
- "I consent" / continue button
- No recording until consent is given

### Voice Session

**Expected Elements:**
- Record / stop button
- Visual recording state indicator
- AI response area (transcript turns)
- Conversation ends with a completion state

### Transcript Review

**Expected Elements:**
- Transcript list with speaker labels
- Redact controls (if present)
- Submit/confirm button
- Thank you state after submission

---

## Payment Flows

No payment flows in the current app. Skip during testing.

---

## OAuth/Identity Setup

Speak by Kraliki uses email/password with JWT auth. No external OAuth required.

---

## Test Scenarios

### Scenario 1: Admin Registration + Login
1. Open `http://127.0.0.1:5175`
2. Go to registration
3. Create a company account
4. Login with the new account
5. Confirm redirect to dashboard

### Scenario 2: Create and Launch Survey
1. Navigate to Surveys
2. Create a survey with 2+ questions
3. Launch the survey
4. Confirm status changes to active

### Scenario 3: Employee Invitation + Voice Check-in
1. From survey, obtain employee token link
2. Open `http://127.0.0.1:5175/v/{token}`
3. Accept consent
4. Start a voice session (microphone prompt expected)
5. End session and verify completion screen

### Scenario 4: Transcript Review
1. Open transcript page `http://127.0.0.1:5175/v/{token}/transcript`
2. Verify transcript entries render
3. Redact a line (if supported)
4. Submit transcript

### Scenario 5: Alerts + Actions
1. Open Alerts in dashboard
2. Confirm alerts list renders (or empty state)
3. Open Actions and create a new action
4. Mark action resolved

---

## Expected States (Screenshots)

### State 1: Login Screen
- Branding + login form visible

### State 2: Dashboard Overview
- KPI tiles + signal clusters visible

### State 3: Surveys Page
- Survey list + create button

### State 4: Consent Screen
- Trust layer copy + consent button

### State 5: Transcript Review
- Transcript turns visible + submit button

---

## Verification Checklist

- [ ] Login and registration work
- [ ] Dashboard loads without errors
- [ ] Survey creation + launch works
- [ ] Employee token link opens check-in page
- [ ] Consent gate blocks recording until accepted
- [ ] Voice session starts and completes
- [ ] Transcript review page loads
- [ ] Alerts and actions pages load

---

## Known Issues

1. Voice check-in requires microphone permissions and Gemini API key.
2. Employee token must be generated via survey launch; if missing, request one.

---

## Contact

For testing issues, escalate to development team.

---

*Cookbook for Speak by Kraliki - AI voice employee intelligence platform*
