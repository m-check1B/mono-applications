# Cross-Tab Synchronization Testing Guide

## Overview
This document describes how to test the cross-tab synchronization feature implemented using the BroadcastChannel API.

## Features Implemented

### 1. Core Service (`crossTabSync.ts`)
- BroadcastChannel-based message broadcasting
- Tab identification and message filtering
- Type-safe message types: `auth_updated`, `auth_logout`, `session_updated`, `session_ended`
- Subscribe/unsubscribe pattern for listeners
- Automatic cleanup on page unload
- Browser compatibility checking

### 2. Auth Store Integration (`auth.ts`)
- Login synchronization across tabs
- Logout synchronization across tabs
- Token refresh synchronization
- Registration synchronization
- Automatic localStorage updates

### 3. Session Sync Service (`sessionSync.ts`)
- Helper functions for session broadcasting
- Session update broadcasting
- Session end broadcasting
- Subscribe to session events
- Availability checking

### 4. Chat Store Integration (`chat.ts`)
- Session initialization sync
- Session end sync
- Context update sync
- Automatic cross-tab updates

## Testing Instructions

### Test 1: Authentication Synchronization

1. **Setup:**
   - Open the application in Tab 1
   - Open the cross-tab demo page in Tab 2: `/cross-tab-demo`

2. **Test Login Sync:**
   - In Tab 1, navigate to `/auth/login`
   - Log in with valid credentials
   - **Expected:** Tab 2 should immediately show "Auth updated" message
   - **Expected:** Auth status in Tab 2 should change to "authenticated"
   - **Expected:** User email should appear in Tab 2

3. **Test Logout Sync:**
   - In Tab 1, click logout
   - **Expected:** Tab 2 should show "Logout detected" message
   - **Expected:** Auth status in Tab 2 should change to "unauthenticated"
   - **Expected:** User info should disappear in Tab 2

### Test 2: Multi-Tab Login

1. **Setup:**
   - Open 3 tabs with the cross-tab demo page
   - Ensure all tabs show "unauthenticated"

2. **Test:**
   - Open a 4th tab and login
   - **Expected:** All 3 demo tabs should update simultaneously
   - **Expected:** All tabs should show the same user info
   - **Expected:** Each tab should show a message from a different tab ID

### Test 3: Session Updates

1. **Setup:**
   - Open the cross-tab demo page in 2 tabs

2. **Test Custom Messages:**
   - In Tab 1, type a test message and click "Send to Other Tabs"
   - **Expected:** Tab 2 should receive and display the message
   - **Expected:** Tab 1 should NOT display its own message (filters out same-tab messages)
   - Repeat from Tab 2
   - **Expected:** Tab 1 should receive the message

### Test 4: Token Refresh Sync

1. **Setup:**
   - Login in Tab 1
   - Open cross-tab demo in Tab 2
   - Wait for token refresh to occur (or trigger manually if you have a refresh button)

2. **Test:**
   - When token refresh happens in Tab 1
   - **Expected:** Tab 2 should receive auth update
   - **Expected:** Both tabs should have the same token
   - **Expected:** No re-authentication required

### Test 5: Browser Compatibility

1. **Test in Chrome/Edge:**
   - BroadcastChannel should be available
   - Status should show "✓ Supported"
   - All sync features should work

2. **Test in Firefox:**
   - BroadcastChannel should be available
   - Status should show "✓ Supported"
   - All sync features should work

3. **Test in Safari:**
   - BroadcastChannel should be available (Safari 15.4+)
   - Status should show "✓ Supported"
   - All sync features should work

4. **Test in older browsers:**
   - Status should show "✗ Not Supported"
   - Application should still work (graceful degradation)
   - No errors should be thrown

### Test 6: Session End Sync

1. **Setup:**
   - Create a chat session in Tab 1
   - Open another tab with access to chat store

2. **Test:**
   - End the session in Tab 1
   - **Expected:** Other tabs should be notified
   - **Expected:** Session status should update to "ended" in all tabs

### Test 7: Message Ordering

1. **Setup:**
   - Open 2 tabs

2. **Test:**
   - Rapidly send multiple messages from Tab 1
   - **Expected:** All messages should arrive in Tab 2
   - **Expected:** Messages should be in correct order
   - **Expected:** No messages should be lost

## Expected Behaviors

### ✓ Successful Sync
- Messages appear in other tabs within milliseconds
- Auth state updates are immediate
- No page refresh required
- localStorage is kept in sync
- No duplicate messages in originating tab

### ✓ Graceful Degradation
- When BroadcastChannel is not supported:
  - No JavaScript errors
  - Application continues to work
  - Each tab maintains its own state
  - Manual refresh required for sync

### ✓ Security
- Messages only broadcast within same origin
- No cross-origin message leakage
- Tab IDs are unique and unpredictable
- Timestamps are included for debugging

## Debugging

### Check BroadcastChannel Status
```javascript
// In browser console
console.log(typeof BroadcastChannel !== 'undefined')
```

### Monitor All Messages
```javascript
// In browser console
const channel = new BroadcastChannel('voice-kraliki-sync');
channel.onmessage = (e) => console.log('Message:', e.data);
```

### Test Message Sending
```javascript
// In browser console
import { crossTabSync } from '$lib/services/crossTabSync';
crossTabSync.broadcast('session_updated', { test: 'Hello from console' });
```

## Known Limitations

1. **Same Origin Only:** BroadcastChannel only works between pages from the same origin
2. **Browser Support:** Not supported in IE11 (use Chrome, Firefox, Safari 15.4+, or Edge)
3. **No Persistence:** Messages are not persisted, only live tabs receive them
4. **Same Browser Only:** Messages don't sync across different browsers
5. **Incognito Mode:** Separate incognito windows don't share channels

## Troubleshooting

### Issue: Messages Not Received

**Possible Causes:**
- Browser doesn't support BroadcastChannel
- Tabs are from different origins
- Tab IDs are matching (shouldn't happen)

**Solutions:**
- Check browser compatibility
- Verify both tabs are from same domain/port
- Check console for errors

### Issue: Duplicate Messages

**Possible Causes:**
- Tab ID filtering not working
- Multiple subscriptions

**Solutions:**
- Verify tab ID generation
- Check for unsubscribed listeners

### Issue: State Inconsistency

**Possible Causes:**
- Race conditions
- Storage not updating
- Messages arriving out of order

**Solutions:**
- Check localStorage values
- Verify message timestamps
- Test with slower intervals

## Performance Considerations

- **Low Overhead:** BroadcastChannel is very efficient
- **No Polling:** Event-driven, no server polling required
- **Memory Usage:** Minimal, listeners are cleaned up
- **Network Usage:** None, purely client-side

## Security Considerations

- Messages are only shared between tabs in the same browser
- Same-origin policy applies
- No server involvement
- Tab IDs prevent infinite loops
- Timestamps help with debugging and ordering
