/**
 * Cross-Tab Sync Integration Examples
 *
 * This file contains practical examples of how to integrate cross-tab sync
 * into your components and services.
 */

import { crossTabSync } from './crossTabSync';
import { broadcastSessionUpdate, subscribeToSessionUpdates } from './sessionSync';

// ============================================================================
// Example 1: Basic Message Broadcasting
// ============================================================================

export function example1_BasicBroadcast() {
	// Broadcast a simple message to other tabs
	crossTabSync.broadcast('session_updated', {
		message: 'Hello from this tab!',
		timestamp: Date.now()
	});
}

// ============================================================================
// Example 2: Subscribing to Messages in a Component
// ============================================================================

export function example2_ComponentSubscription() {
	// In a Svelte component using Runes:
	/*
	<script lang="ts">
		import { crossTabSync } from '$lib/services/crossTabSync';

		let messages = $state<string[]>([]);

		// Subscribe when component mounts, unsubscribe on cleanup
		$effect(() => {
			const unsubscribe = crossTabSync.subscribe('session_updated', (message) => {
				messages = [...messages, JSON.stringify(message.payload)];
			});

			return () => unsubscribe();
		});
	</script>

	<div>
		{#each messages as msg}
			<p>{msg}</p>
		{/each}
	</div>
	*/
}

// ============================================================================
// Example 3: Syncing Custom Data
// ============================================================================

export function example3_SyncCustomData() {
	interface UserPreferences {
		theme: 'light' | 'dark';
		notifications: boolean;
		language: string;
	}

	// Save and broadcast preferences
	function savePreferences(prefs: UserPreferences) {
		// Save to localStorage
		localStorage.setItem('user_preferences', JSON.stringify(prefs));

		// Broadcast to other tabs
		crossTabSync.broadcast('session_updated', {
			type: 'preferences_updated',
			preferences: prefs
		});
	}

	// Listen for preference updates from other tabs
	function listenForPreferenceUpdates(
		callback: (prefs: UserPreferences) => void
	): () => void {
		return crossTabSync.subscribe('session_updated', (message) => {
			if (message.payload.type === 'preferences_updated') {
				callback(message.payload.preferences);
			}
		});
	}

	return { savePreferences, listenForPreferenceUpdates };
}

// ============================================================================
// Example 4: Checking Availability Before Use
// ============================================================================

export function example4_CheckAvailability() {
	function notifyOtherTabs(data: any) {
		// Always check if BroadcastChannel is supported
		if (crossTabSync.isAvailable()) {
			crossTabSync.broadcast('session_updated', data);
		} else {
			console.warn('Cross-tab sync not available in this browser');
			// Fallback behavior - maybe use localStorage events
		}
	}

	return { notifyOtherTabs };
}

// ============================================================================
// Example 5: Session Management with Sync
// ============================================================================

export function example5_SessionManagement() {
	interface Session {
		id: string;
		status: 'active' | 'paused' | 'ended';
		startTime: number;
		data: Record<string, any>;
	}

	class SessionManager {
		private sessions: Map<string, Session> = new Map();

		constructor() {
			// Subscribe to session updates from other tabs
			subscribeToSessionUpdates((sessionId, data) => {
				this.handleExternalUpdate(sessionId, data);
			});
		}

		createSession(sessionId: string, data: Record<string, any>): Session {
			const session: Session = {
				id: sessionId,
				status: 'active',
				startTime: Date.now(),
				data
			};

			this.sessions.set(sessionId, session);

			// Broadcast to other tabs
			broadcastSessionUpdate(sessionId, session);

			return session;
		}

		updateSession(sessionId: string, updates: Partial<Session>) {
			const session = this.sessions.get(sessionId);
			if (!session) return;

			const updatedSession = { ...session, ...updates };
			this.sessions.set(sessionId, updatedSession);

			// Broadcast to other tabs
			broadcastSessionUpdate(sessionId, updatedSession);
		}

		private handleExternalUpdate(sessionId: string, data: any) {
			// Handle updates from other tabs
			this.sessions.set(sessionId, data);
			console.log('Session updated from another tab:', sessionId);
		}
	}

	return new SessionManager();
}

// ============================================================================
// Example 6: Debounced Broadcasting
// ============================================================================

export function example6_DebouncedBroadcast() {
	function debounce<T extends (...args: any[]) => void>(
		func: T,
		wait: number
	): (...args: Parameters<T>) => void {
		let timeout: ReturnType<typeof setTimeout>;

		return (...args: Parameters<T>) => {
			clearTimeout(timeout);
			timeout = setTimeout(() => func(...args), wait);
		};
	}

	// Debounced broadcast function
	const debouncedBroadcast = debounce(
		(data: any) => {
			crossTabSync.broadcast('session_updated', data);
		},
		300 // Wait 300ms before broadcasting
	);

	// Use it for rapid updates (e.g., typing)
	function handleInputChange(value: string) {
		// Update local state immediately
		// ...

		// Broadcast to other tabs (debounced)
		debouncedBroadcast({ inputValue: value });
	}

	return { handleInputChange };
}

// ============================================================================
// Example 7: Message Filtering by Type
// ============================================================================

export function example7_MessageFiltering() {
	type CustomMessageType = 'user_action' | 'data_update' | 'notification';

	interface CustomPayload {
		messageType: CustomMessageType;
		data: any;
	}

	function broadcastTypedMessage(type: CustomMessageType, data: any) {
		const payload: CustomPayload = {
			messageType: type,
			data
		};

		crossTabSync.broadcast('session_updated', payload);
	}

	function subscribeToTypedMessage(
		type: CustomMessageType,
		callback: (data: any) => void
	): () => void {
		return crossTabSync.subscribe('session_updated', (message) => {
			const payload = message.payload as CustomPayload;
			if (payload.messageType === type) {
				callback(payload.data);
			}
		});
	}

	return { broadcastTypedMessage, subscribeToTypedMessage };
}

// ============================================================================
// Example 8: Svelte Store with Cross-Tab Sync
// ============================================================================

export function example8_SyncedStore() {
	/*
	import { writable } from 'svelte/store';
	import { crossTabSync } from './crossTabSync';

	interface TodoItem {
		id: string;
		text: string;
		completed: boolean;
	}

	function createSyncedTodoStore() {
		const { subscribe, set, update } = writable<TodoItem[]>([]);

		// Listen for updates from other tabs
		crossTabSync.subscribe('session_updated', (message) => {
			if (message.payload.type === 'todos_updated') {
				set(message.payload.todos);
			}
		});

		return {
			subscribe,
			addTodo(text: string) {
				update(todos => {
					const newTodos = [...todos, {
						id: crypto.randomUUID(),
						text,
						completed: false
					}];

					// Broadcast to other tabs
					crossTabSync.broadcast('session_updated', {
						type: 'todos_updated',
						todos: newTodos
					});

					return newTodos;
				});
			},
			toggleTodo(id: string) {
				update(todos => {
					const newTodos = todos.map(todo =>
						todo.id === id ? { ...todo, completed: !todo.completed } : todo
					);

					// Broadcast to other tabs
					crossTabSync.broadcast('session_updated', {
						type: 'todos_updated',
						todos: newTodos
					});

					return newTodos;
				});
			}
		};
	}

	export const todoStore = createSyncedTodoStore();
	*/
}

// ============================================================================
// Example 9: Error Handling
// ============================================================================

export function example9_ErrorHandling() {
	function safeBroadcast(type: any, payload: any) {
		try {
			if (!crossTabSync.isAvailable()) {
				throw new Error('BroadcastChannel not supported');
			}

			// Validate payload size (optional)
			const payloadSize = JSON.stringify(payload).length;
			if (payloadSize > 100000) {
				console.warn('Payload is very large:', payloadSize, 'bytes');
			}

			crossTabSync.broadcast(type, payload);
		} catch (error) {
			console.error('Failed to broadcast message:', error);
			// Fallback: use localStorage events or other mechanism
			handleBroadcastFailure(payload);
		}
	}

	function handleBroadcastFailure(payload: any) {
		// Fallback implementation
		console.log('Using fallback sync mechanism');
		// Could use localStorage events, polling, etc.
	}

	return { safeBroadcast };
}

// ============================================================================
// Example 10: Real-World Integration - Notification System
// ============================================================================

export function example10_NotificationSystem() {
	interface Notification {
		id: string;
		title: string;
		message: string;
		type: 'info' | 'success' | 'warning' | 'error';
		timestamp: number;
	}

	class NotificationManager {
		private notifications: Notification[] = [];
		private listeners: Set<(notifications: Notification[]) => void> = new Set();

		constructor() {
			// Listen for notifications from other tabs
			crossTabSync.subscribe('session_updated', (message) => {
				if (message.payload.type === 'notification') {
					this.addNotification(message.payload.notification, false);
				} else if (message.payload.type === 'notification_dismissed') {
					this.dismissNotification(message.payload.notificationId, false);
				}
			});
		}

		addNotification(notification: Omit<Notification, 'id' | 'timestamp'>, broadcast = true) {
			const newNotification: Notification = {
				...notification,
				id: crypto.randomUUID(),
				timestamp: Date.now()
			};

			this.notifications = [...this.notifications, newNotification];
			this.notifyListeners();

			// Broadcast to other tabs
			if (broadcast && crossTabSync.isAvailable()) {
				crossTabSync.broadcast('session_updated', {
					type: 'notification',
					notification: newNotification
				});
			}
		}

		dismissNotification(id: string, broadcast = true) {
			this.notifications = this.notifications.filter(n => n.id !== id);
			this.notifyListeners();

			// Broadcast to other tabs
			if (broadcast && crossTabSync.isAvailable()) {
				crossTabSync.broadcast('session_updated', {
					type: 'notification_dismissed',
					notificationId: id
				});
			}
		}

		subscribe(listener: (notifications: Notification[]) => void): () => void {
			this.listeners.add(listener);
			return () => this.listeners.delete(listener);
		}

		private notifyListeners() {
			this.listeners.forEach(listener => listener(this.notifications));
		}
	}

	return new NotificationManager();
}

// ============================================================================
// Usage Summary
// ============================================================================

/*
To use these examples in your code:

1. Import the service:
   import { crossTabSync } from '$lib/services/crossTabSync';

2. Check availability:
   if (crossTabSync.isAvailable()) { ... }

3. Broadcast messages:
   crossTabSync.broadcast('session_updated', { data: 'value' });

4. Subscribe to messages:
   const unsubscribe = crossTabSync.subscribe('session_updated', handler);

5. Clean up:
   unsubscribe();

See the demo page at /cross-tab-demo for a working example.
*/
