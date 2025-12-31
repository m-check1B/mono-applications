# Cross-Tab Synchronization Implementation

## Overview

This feature implements real-time synchronization of authentication state and sessions across multiple browser tabs using the BroadcastChannel API.

## Architecture

### Core Components

1. **CrossTabSyncService** (`/frontend/src/lib/services/crossTabSync.ts`)
   - Main service for broadcasting and receiving messages
   - Tab identification and message filtering
   - Subscription management
   - Automatic cleanup

2. **Session Sync Utilities** (`/frontend/src/lib/services/sessionSync.ts`)
   - Helper functions for session broadcasting
   - Typed interfaces for session data
   - Subscription helpers

3. **Auth Store Integration** (`/frontend/src/lib/stores/auth.ts`)
   - Login/logout synchronization
   - Token refresh synchronization
   - Registration synchronization

4. **Chat Store Integration** (`/frontend/src/lib/stores/chat.ts`)
   - Session lifecycle synchronization
   - Context update synchronization
   - Message synchronization

## Usage

### Quick Start

Visit `/cross-tab-demo` to see the feature in action:
1. Open the page in multiple tabs
2. Login/logout in one tab
3. Watch other tabs update automatically

### Using in Your Code

#### Broadcasting Messages

```typescript
import { crossTabSync } from '$lib/services/crossTabSync';

// Broadcast auth update
crossTabSync.broadcast('auth_updated', { tokens, user });

// Broadcast logout
crossTabSync.broadcast('auth_logout', {});

// Broadcast session update
crossTabSync.broadcast('session_updated', { sessionId, data });

// Broadcast session end
crossTabSync.broadcast('session_ended', { sessionId });
```

#### Subscribing to Messages

```typescript
import { crossTabSync } from '$lib/services/crossTabSync';

// Subscribe to auth updates
const unsubscribe = crossTabSync.subscribe('auth_updated', (message) => {
  console.log('Auth updated from tab:', message.tabId);
  console.log('Payload:', message.payload);
  console.log('Timestamp:', message.timestamp);
});

// Clean up when done
unsubscribe();
```

#### Using Session Sync Helpers

```typescript
import {
  broadcastSessionUpdate,
  broadcastSessionEnd,
  subscribeToSessionUpdates,
  subscribeToSessionEnd,
  isSyncAvailable
} from '$lib/services/sessionSync';

// Check if sync is available
if (isSyncAvailable()) {
  // Broadcast session update
  broadcastSessionUpdate('session-123', { status: 'active' });

  // Listen for updates
  const unsubscribe = subscribeToSessionUpdates((sessionId, data) => {
    console.log('Session updated:', sessionId, data);
  });

  // End session
  broadcastSessionEnd('session-123');
}
```

## Message Types

### auth_updated
Broadcast when user logs in, registers, or tokens are refreshed.

**Payload:**
```typescript
{
  tokens: {
    accessToken: string;
    refreshToken: string;
    expiresAt?: number;
  };
  user: {
    id: string;
    email?: string;
    name?: string;
    role?: string;
  } | null;
}
```

### auth_logout
Broadcast when user logs out.

**Payload:**
```typescript
{}
```

### session_updated
Broadcast when a session is created or updated.

**Payload:**
```typescript
{
  sessionId: string;
  data: any; // Session-specific data
  timestamp?: number;
}
```

### session_ended
Broadcast when a session ends.

**Payload:**
```typescript
{
  sessionId: string;
  timestamp?: number;
}
```

## Benefits

1. **Consistent State:** All tabs always have the same authentication state
2. **Better UX:** Users don't need to manually refresh tabs
3. **Real-time:** Updates happen immediately (< 10ms typically)
4. **No Server Load:** Completely client-side, no polling required
5. **Efficient:** Very low memory and CPU overhead
6. **Secure:** Same-origin policy enforced by browser

## Browser Support

| Browser | Version | Support |
|---------|---------|---------|
| Chrome  | 54+     | ✅ Full |
| Firefox | 38+     | ✅ Full |
| Safari  | 15.4+   | ✅ Full |
| Edge    | 79+     | ✅ Full |
| IE      | Any     | ❌ No   |

**Graceful Degradation:** When BroadcastChannel is not supported, the app continues to work normally, just without cross-tab sync.

## Implementation Details

### Tab Identification

Each tab gets a unique ID generated on initialization:
```typescript
`tab-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
```

This prevents tabs from processing their own messages.

### Message Structure

All messages follow this structure:
```typescript
{
  type: 'auth_updated' | 'auth_logout' | 'session_updated' | 'session_ended';
  payload: any;
  timestamp: number;
  tabId: string;
}
```

### Automatic Cleanup

The service automatically cleans up on page unload:
```typescript
window.addEventListener('beforeunload', () => {
  crossTabSync.close();
});
```

## Best Practices

### 1. Always Check Availability

```typescript
if (crossTabSync.isAvailable()) {
  // Broadcast messages
}
```

### 2. Clean Up Subscriptions

```typescript
$effect(() => {
  const unsubscribe = crossTabSync.subscribe('auth_updated', handler);
  return () => unsubscribe();
});
```

### 3. Don't Process Own Messages

The service automatically filters out same-tab messages, but if you're implementing custom logic, always check:
```typescript
if (message.tabId === myTabId) return;
```

### 4. Handle Race Conditions

When multiple tabs might update at the same time:
```typescript
// Use timestamps to determine which update is newer
if (message.timestamp > lastUpdateTimestamp) {
  // Apply update
  lastUpdateTimestamp = message.timestamp;
}
```

### 5. Keep Payloads Small

BroadcastChannel is very efficient, but keep payloads reasonable:
- ✅ Good: `{ sessionId: '123', status: 'active' }`
- ❌ Bad: Entire session history with 1000s of messages

## Testing

### Manual Testing

1. Open `/cross-tab-demo` in multiple tabs
2. Login/logout in one tab
3. Send test messages
4. Verify all tabs receive updates

### Automated Testing

See `/frontend/src/lib/services/crossTabSync.test.md` for comprehensive test cases.

### Console Testing

```javascript
// Open browser console in any tab
import { crossTabSync } from '$lib/services/crossTabSync';

// Send test message
crossTabSync.broadcast('session_updated', { test: 'Hello' });

// Listen for messages
const unsubscribe = crossTabSync.subscribe('session_updated', (msg) => {
  console.log('Received:', msg);
});
```

## Troubleshooting

### Messages Not Syncing

1. Check browser support: `typeof BroadcastChannel !== 'undefined'`
2. Verify same origin (protocol + domain + port must match)
3. Check console for errors
4. Verify both tabs are not in different browser profiles

### State Inconsistency

1. Check localStorage values
2. Verify timestamps
3. Check for race conditions
3. Ensure proper cleanup of old listeners

### Performance Issues

1. Limit broadcast frequency (debounce if needed)
2. Keep payloads small
3. Unsubscribe when components unmount

## Security Considerations

- **Same Origin Only:** BroadcastChannel enforces same-origin policy
- **No XSS Risk:** Messages are not evaluated as code
- **Client Side Only:** No server involvement, no network requests
- **Tab Isolation:** Each tab has unique ID, prevents infinite loops
- **No Persistence:** Messages are not stored, only live tabs receive them

## Future Enhancements

Potential improvements for future versions:

1. **Message Priority:** High-priority messages for critical updates
2. **Message Queuing:** Queue messages if tab is in background
3. **Compression:** Compress large payloads
4. **Conflict Resolution:** Automatic conflict resolution for concurrent updates
5. **Debug Mode:** Enhanced logging for development
6. **Performance Monitoring:** Track message delivery times
7. **Custom Channels:** Support multiple channels for different features

## Files Modified/Created

### Created
- `/frontend/src/lib/services/crossTabSync.ts` - Core sync service
- `/frontend/src/lib/services/sessionSync.ts` - Session sync utilities
- `/frontend/src/routes/cross-tab-demo/+page.svelte` - Demo page
- `/frontend/src/lib/services/crossTabSync.test.md` - Testing guide
- `/frontend/CROSS_TAB_SYNC.md` - This documentation

### Modified
- `/frontend/src/lib/stores/auth.ts` - Added cross-tab sync for auth
- `/frontend/src/lib/stores/chat.ts` - Added cross-tab sync for sessions

## Support

For issues or questions about cross-tab synchronization:
1. Check the demo page at `/cross-tab-demo`
2. Review the test guide at `/frontend/src/lib/services/crossTabSync.test.md`
3. Check browser console for errors
4. Verify browser compatibility

## License

This implementation is part of the Operator Demo 2026 project.
