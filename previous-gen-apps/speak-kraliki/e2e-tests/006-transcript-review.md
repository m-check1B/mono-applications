# Test 006: Transcript Review (Trust Layer)

**Priority:** MEDIUM
**URL:** https://speak.verduona.dev/v/[token]/transcript

## Preconditions

- Browser is open
- Valid employee token exists with completed conversation
- Conversation has been completed (not in progress)

## Test Steps

### Step 1: Access Transcript Page

1. Navigate to https://speak.verduona.dev/v/[valid-token]/transcript
2. Wait for page to load

**Expected:**
- Transcript page loads
- Page title indicates transcript view
- Conversation history is displayed

### Step 2: Verify Transcript Content

1. Review the transcript display

**Expected:**
- Messages are displayed chronologically
- User messages are clearly distinguished from AI messages
- Timestamps or turn indicators visible
- Messages are readable and properly formatted

### Step 3: Verify Message Attribution

1. Check message styling

**Expected:**
- AI messages labeled "SPEAK BY KRALIKI"
- User messages labeled "TY" (You)
- Different visual styling for each speaker

### Step 4: Trust Layer Features (if available)

1. Look for edit/redact options

**Expected (if feature exists):**
- Option to review sensitive content
- Ability to request redaction
- Data deletion request option

### Step 5: Navigation from Transcript

1. Look for navigation options

**Expected:**
- Back button or link to return
- No access to other users' transcripts

### Step 6: Expired/Invalid Token

1. Navigate to /v/invalid-token/transcript

**Expected:**
- Error message displayed
- Access denied to non-existent transcript

### Step 7: Verify Anonymity

1. Check for any identifying information

**Expected:**
- No employee name displayed
- No email or identifying info visible
- Anonymous ID only (if shown)

## Success Criteria

- Transcript loads for valid completed conversations
- Message attribution is clear
- No unauthorized access to transcripts
- Anonymity is preserved

## Notes

- This page is critical for the Trust Layer feature
- Employees should feel safe reviewing what they said
- GDPR: Right to view and request deletion of data
- Future: May include edit/redact functionality
