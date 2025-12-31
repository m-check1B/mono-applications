# Test 003: Employee Feedback Flow (Voice/Text Submission)

**Priority:** CRITICAL
**URL:** https://speak.verduona.dev/v/[token]

## Preconditions

- Browser is open
- Valid employee token exists (or test with mock token)
- Microphone permissions may be needed for voice mode

## Test Steps

### Step 1: Load Feedback Page with Token

1. Navigate to https://speak.verduona.dev/v/test-token-123

**Expected:**
- Consent screen is displayed
- "SPEAK BY KRALIKI" title is visible
- Trust layer messages are shown

### Step 2: Verify Trust Layer Messages

1. Read the consent screen content

**Expected:**
- Message about 100% anonymous conversation
- Message that manager won't see individual responses
- Message about seeing aggregated trends only
- Message about reviewing/editing transcript
- Message about data deletion rights

### Step 3: Test Skip Option

1. Find the skip/decline option
2. Click "PRESKOCIT" or "SKIP" button

**Expected:**
- Thank you message appears
- User is not forced to participate

### Step 4: Accept Consent

1. Navigate back to /v/test-token-123
2. Click "ROZUMIM, POJDME NA TO" or "UNDERSTAND" button

**Expected:**
- Consent is recorded
- Voice conversation interface loads
- Mode indicator shows "Hlasovy rezim" (Voice mode)
- Microphone prompt may appear

### Step 5: Switch to Text Mode

1. Find the "PREJIT NA TEXT" or "SWITCH TO TEXT" button
2. Click it

**Expected:**
- Mode switches to text
- Text input field appears
- Mode indicator shows "Textovy rezim" (Text mode)
- Send button is visible

### Step 6: Send Text Message

1. Type a test message: "Toto je testovaci zprava"
2. Click "ODESLAT" or "SEND" button

**Expected:**
- Message appears in transcript area
- AI processing indicator appears ("Premyslim..." or "Thinking...")
- AI response appears after processing

### Step 7: End Conversation

1. Click "UKONCIT" or "END" button

**Expected:**
- Completion screen appears
- "DEKUJEME!" or "THANK YOU" message is visible
- "ZOBRAZIT PREPIS" (VIEW TRANSCRIPT) button is available

### Step 8: View Transcript

1. Click "ZOBRAZIT PREPIS" button

**Expected:**
- Transcript page loads
- Conversation history is displayed
- Trust layer features available (edit/redact options if applicable)

### Step 9: Invalid Token Handling

1. Navigate to /v/invalid-expired-token-12345

**Expected:**
- Error message is displayed
- "CHYBA" or "ERROR" indicator
- Message about invalid or expired token

## Success Criteria

- Consent flow works correctly
- Voice/text mode switching functions
- Messages can be sent and responses received
- Conversation can be ended properly
- Transcript is accessible
- Invalid tokens show appropriate error

## Notes

- For real testing, a valid employee token from an active survey is needed
- Mock tokens may show error state (expected for invalid tokens)
- Voice mode requires microphone permissions
- Language: Czech (cs) by default
