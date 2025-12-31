# Cross-Tab Sync Quick Reference Card

## 🚀 Quick Start

### Demo Page
Visit `/cross-tab-demo` to see it in action!

### Basic Usage

```typescript
import { crossTabSync } from '$lib/services/crossTabSync';

// Broadcast to other tabs
crossTabSync.broadcast('session_updated', { myData: 'value' });

// Listen for updates
const unsubscribe = crossTabSync.subscribe('session_updated', (msg) => {
  console.log('Received:', msg.payload);
});

// Clean up when done
unsubscribe();
```

## 📦 What's Included

### Core Files
- `crossTabSync.ts` - Main BroadcastChannel service
- `sessionSync.ts` - Session-specific helpers
- `CrossTabSyncIndicator.svelte` - Visual indicator component
- Demo page at `/cross-tab-demo`

### Integrated Stores
- ✅ Auth Store - Login/logout sync
- ✅ Chat Store - Session lifecycle sync

## 🔧 API Reference

### crossTabSync Service

```typescript
// Check if available
crossTabSync.isAvailable(): boolean

// Broadcast message
crossTabSync.broadcast(
  type: 'auth_updated' | 'auth_logout' | 'session_updated' | 'session_ended',
  payload: any
): void

// Subscribe to messages
crossTabSync.subscribe(
  type: MessageType,
  listener: (message: SyncMessage) => void
): () => void  // Returns unsubscribe function

// Close channel
crossTabSync.close(): void
```

### sessionSync Helpers

```typescript
// Broadcast session update
broadcastSessionUpdate(sessionId: string, data: any): void

// Broadcast session end
broadcastSessionEnd(sessionId: string): void

// Listen for session updates
subscribeToSessionUpdates(
  callback: (sessionId: string, data: any) => void
): () => void

// Listen for session end
subscribeToSessionEnd(
  callback: (sessionId: string) => void
): () => void

// Check availability
isSyncAvailable(): boolean
```

## 💡 Common Patterns

### Pattern 1: Component Subscription (Svelte Runes)

```svelte
<script lang="ts">
  import { crossTabSync } from '$lib/services/crossTabSync';

  let data = $state(initialValue);

  $effect(() => {
    const unsubscribe = crossTabSync.subscribe('session_updated', (msg) => {
      data = msg.payload;
    });

    return () => unsubscribe();
  });
</script>
```

### Pattern 2: Store with Sync

```typescript
import { writable } from 'svelte/store';
import { crossTabSync } from '$lib/services/crossTabSync';

function createSyncedStore() {
  const { subscribe, set, update } = writable(initialValue);

  // Listen for updates from other tabs
  crossTabSync.subscribe('session_updated', (msg) => {
    if (msg.payload.type === 'my_store') {
      set(msg.payload.value);
    }
  });

  return {
    subscribe,
    set(value) {
      set(value);
      crossTabSync.broadcast('session_updated', {
        type: 'my_store',
        value
      });
    }
  };
}
```

### Pattern 3: Conditional Sync

```typescript
function updateData(data: any) {
  // Update local state
  localState = data;

  // Sync to other tabs if available
  if (crossTabSync.isAvailable()) {
    crossTabSync.broadcast('session_updated', data);
  }
}
```

## 📋 Message Types

| Type | When Used | Payload |
|------|-----------|---------|
| `auth_updated` | Login, register, token refresh | `{ tokens, user }` |
| `auth_logout` | User logs out | `{}` |
| `session_updated` | Session created/updated | `{ sessionId, data }` |
| `session_ended` | Session terminated | `{ sessionId }` |

## ✅ Features

- ✅ Real-time sync (< 10ms)
- ✅ Type-safe API
- ✅ Auto cleanup
- ✅ Browser compatibility check
- ✅ No server load
- ✅ Same-origin security
- ✅ Graceful degradation

## 🌐 Browser Support

| Browser | Support |
|---------|---------|
| Chrome 54+ | ✅ |
| Firefox 38+ | ✅ |
| Safari 15.4+ | ✅ |
| Edge 79+ | ✅ |
| IE | ❌ |

## ⚠️ Important Notes

1. **Always check availability** before broadcasting
2. **Clean up subscriptions** when components unmount
3. **Keep payloads small** (< 100KB recommended)
4. **Same origin only** - protocol/domain/port must match
5. **No persistence** - messages only sent to open tabs

## 🔍 Debugging

```javascript
// In browser console

// Check if supported
typeof BroadcastChannel !== 'undefined'

// Listen to all messages
const channel = new BroadcastChannel('operator-demo-sync');
channel.onmessage = (e) => console.log(e.data);

// Send test message
import { crossTabSync } from '$lib/services/crossTabSync';
crossTabSync.broadcast('session_updated', { test: 'hello' });
```

## 📚 Documentation

- Full docs: `/frontend/CROSS_TAB_SYNC.md`
- Testing guide: `/frontend/src/lib/services/crossTabSync.test.md`
- Examples: `/frontend/src/lib/services/crossTabSync.example.ts`
- Demo: Visit `/cross-tab-demo`

## 🎯 Real-World Examples

### Example 1: Sync User Preferences

```typescript
function updateTheme(theme: 'light' | 'dark') {
  localStorage.setItem('theme', theme);
  crossTabSync.broadcast('session_updated', {
    type: 'theme_change',
    theme
  });
}

crossTabSync.subscribe('session_updated', (msg) => {
  if (msg.payload.type === 'theme_change') {
    applyTheme(msg.payload.theme);
  }
});
```

### Example 2: Shopping Cart Sync

```typescript
function addToCart(item: CartItem) {
  cart.push(item);
  saveCart();

  crossTabSync.broadcast('session_updated', {
    type: 'cart_updated',
    cart: cart
  });
}

crossTabSync.subscribe('session_updated', (msg) => {
  if (msg.payload.type === 'cart_updated') {
    cart = msg.payload.cart;
    renderCart();
  }
});
```

### Example 3: Notification System

```typescript
function showNotification(message: string) {
  displayNotification(message);

  crossTabSync.broadcast('session_updated', {
    type: 'notification',
    message,
    timestamp: Date.now()
  });
}

crossTabSync.subscribe('session_updated', (msg) => {
  if (msg.payload.type === 'notification') {
    displayNotification(msg.payload.message);
  }
});
```

## 🛠️ Troubleshooting

| Problem | Solution |
|---------|----------|
| Messages not syncing | Check browser support and same-origin |
| State inconsistency | Verify localStorage updates |
| Memory leak | Ensure subscriptions are cleaned up |
| Performance issues | Reduce payload size, debounce broadcasts |

## 📞 Getting Help

1. Check the demo: `/cross-tab-demo`
2. Review examples: `crossTabSync.example.ts`
3. Read full docs: `CROSS_TAB_SYNC.md`
4. Check console for errors
5. Verify browser compatibility

---

**Quick Tip:** Add `<CrossTabSyncIndicator />` to your layout to see sync activity in real-time!

---

Last Updated: October 14, 2025
Version: 1.0.0
