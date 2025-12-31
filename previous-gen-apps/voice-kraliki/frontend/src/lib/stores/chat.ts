import { writable, derived } from 'svelte/store';
import { offlineManager, type ConnectionStatus } from '$lib/services/offlineManager';
import { broadcastSessionUpdate, broadcastSessionEnd, subscribeToSessionUpdates, subscribeToSessionEnd } from '$lib/services/sessionSync';

export interface ChatMessage {
	id: string;
	sessionId: string;
	role: 'user' | 'assistant' | 'system';
	content: string;
	timestamp: Date;
	metadata?: {
		intent?: string;
		sentiment?: string;
		confidence?: number;
		provider?: string;
	};
}

export interface ChatSession {
	id: string;
	userId: string;
	companyId: string;
	status: 'active' | 'paused' | 'ended';
	createdAt: Date;
	lastActivity: Date;
	messages: ChatMessage[];
	context: {
		voiceSessionId?: string;
		provider?: string;
		campaign?: string;
		customerInfo?: Record<string, any>;
	};
}

export interface ChatState {
	sessions: Record<string, ChatSession>;
	activeSessionId: string | null;
	isConnected: boolean;
	isTyping: boolean;
	unreadCount: number;
	connectionStatus: ConnectionStatus;
	offlineMode: boolean;
}

function createChatStore() {
	const initialState: ChatState = {
		sessions: {},
		activeSessionId: null,
		isConnected: false,
		isTyping: false,
		unreadCount: 0,
		connectionStatus: offlineManager.getConnectionStatus(),
		offlineMode: !navigator.onLine
	};

	const { subscribe, set, update } = writable(initialState);

	// Initialize offline manager event listeners
	offlineManager.on('connectionChange', (status: ConnectionStatus) => {
		update(state => ({
			...state,
			connectionStatus: status,
			isConnected: status.isOnline,
			offlineMode: !status.isOnline
		}));
	});

	// Initialize cross-tab sync listeners
	subscribeToSessionUpdates((sessionId, data) => {
		update(state => {
			const session = state.sessions[sessionId];
			if (!session) return state;

			return {
				...state,
				sessions: {
					...state.sessions,
					[sessionId]: {
						...session,
						...data,
						lastActivity: new Date()
					}
				}
			};
		});
	});

	subscribeToSessionEnd((sessionId) => {
		update(state => ({
			...state,
			sessions: {
				...state.sessions,
				[sessionId]: {
					...state.sessions[sessionId],
					status: 'ended'
				}
			}
		}));
	});

	return {
		subscribe,

		// Session management
		initializeSession: (sessionData: { sessionId: string; userId: string; companyId: string }) => {
			update(state => {
				const newSession: ChatSession = {
					id: sessionData.sessionId,
					userId: sessionData.userId,
					companyId: sessionData.companyId,
					status: 'active',
					createdAt: new Date(),
					lastActivity: new Date(),
					messages: [],
					context: {}
				};

				// Broadcast to other tabs
				broadcastSessionUpdate(sessionData.sessionId, newSession);

				return {
					...state,
					sessions: {
						...state.sessions,
						[sessionData.sessionId]: newSession
					},
					activeSessionId: sessionData.sessionId
				};
			});
		},

		setActiveSession: (sessionId: string) => {
			update(state => ({
				...state,
				activeSessionId: sessionId
			}));
		},

		endSession: (sessionId: string) => {
			update(state => ({
				...state,
				sessions: {
					...state.sessions,
					[sessionId]: {
						...state.sessions[sessionId],
						status: 'ended'
					}
				}
			}));

			// Broadcast to other tabs
			broadcastSessionEnd(sessionId);
		},

		// Message management
		addMessage: (message: Omit<ChatMessage, 'id' | 'timestamp'>, queueOffline: boolean = true) => {
			const newMessage: ChatMessage = {
				...message,
				id: `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
				timestamp: new Date()
			};

			update(state => {
				const session = state.sessions[message.sessionId];
				if (!session) return state;

				return {
					...state,
					sessions: {
						...state.sessions,
						[message.sessionId]: {
							...session,
							messages: [...session.messages, newMessage],
							lastActivity: new Date()
						}
					},
					unreadCount: state.activeSessionId !== message.sessionId 
						? state.unreadCount + 1 
						: state.unreadCount
				};
			});

			// Queue message for offline handling if it's a user message
			if (queueOffline && message.role === 'user') {
				offlineManager.queueMessage('message', {
					session_id: message.sessionId,
					message: {
						role: message.role,
						content: message.content,
						metadata: message.metadata
					}
				});
			}

			return newMessage.id;
		},

		// Send message with offline support
		sendMessage: async (sessionId: string, content: string, metadata?: any) => {
			const messageId = chatStore.addMessage({
				sessionId,
				role: 'user',
				content,
				metadata
			}, false); // Don't queue here, let offline manager handle it

			// Try to send immediately or queue for later
			try {
				if (offlineManager.getConnectionStatus().isOnline) {
					// Send directly if online
					const response = await fetch('/api/chat/messages', {
						method: 'POST',
						headers: {
							'Content-Type': 'application/json',
						},
						body: JSON.stringify({
							session_id: sessionId,
							message: {
								role: 'user',
								content,
								metadata
							}
						})
					});

					if (!response.ok) {
						throw new Error(`HTTP ${response.status}: ${response.statusText}`);
					}
				} else {
					// Queue for offline sending
					offlineManager.queueMessage('message', {
						session_id: sessionId,
						message: {
							role: 'user',
							content,
							metadata
						}
					});
				}
			} catch (error) {
				console.error('Failed to send message:', error);
				// Queue for retry
				offlineManager.queueMessage('message', {
					session_id: sessionId,
					message: {
						role: 'user',
						content,
						metadata
					}
				});
			}

			return messageId;
		},

		updateMessage: (sessionId: string, messageId: string, updates: Partial<ChatMessage>) => {
			update(state => {
				const session = state.sessions[sessionId];
				if (!session) return state;

				return {
					...state,
					sessions: {
						...state.sessions,
						[sessionId]: {
							...session,
							messages: session.messages.map(msg =>
								msg.id === messageId ? { ...msg, ...updates } : msg
							)
						}
					}
				};
			});
		},

		// Connection state
		setConnectionState: (isConnected: boolean) => {
			update(state => ({
				...state,
				isConnected
			}));
		},

		setTypingState: (isTyping: boolean) => {
			update(state => ({
				...state,
				isTyping
			}));
		},

		// Context management
		updateSessionContext: (sessionId: string, context: Partial<ChatSession['context']>) => {
			update(state => {
				const session = state.sessions[sessionId];
				if (!session) return state;

				const updatedContext = {
					...session.context,
					...context
				};

				// Broadcast to other tabs
				broadcastSessionUpdate(sessionId, { context: updatedContext });

				return {
					...state,
					sessions: {
						...state.sessions,
						[sessionId]: {
							...session,
							context: updatedContext
						}
					}
				};
			});

			// Queue context update for offline handling
			offlineManager.queueMessage('session_update', {
				session_id: sessionId,
				context
			});
		},

		updateCustomerInfo: (sessionId: string, customerInfo: Record<string, any>) => {
			update(state => {
				const session = state.sessions[sessionId];
				if (!session) return state;

				return {
					...state,
					sessions: {
						...state.sessions,
						[sessionId]: {
							...session,
							context: {
								...session.context,
								customerInfo: {
									...session.context.customerInfo,
									...customerInfo
								}
							}
						}
					}
				};
			});

			// Queue customer info update for offline handling
			offlineManager.queueMessage('context_update', {
				session_id: sessionId,
				customer_info: customerInfo
			});
		},

		// Utility
		clearUnreadCount: () => {
			update(state => ({
				...state,
				unreadCount: 0
			}));
		},

		// Offline management
		getOfflineStatus: () => offlineManager.getConnectionStatus(),
		getQueuedMessages: () => offlineManager.getQueuedMessages(),
		clearOfflineQueue: () => offlineManager.clearQueue()
	};
}

export const chatStore = createChatStore();

// Derived stores for convenience
export const activeSession = derived(
	chatStore,
	$chatStore => $chatStore.activeSessionId ? $chatStore.sessions[$chatStore.activeSessionId] : null
);

export const activeMessages = derived(
	activeSession,
	$activeSession => $activeSession?.messages || []
);

export const isConnected = derived(
	chatStore,
	$chatStore => $chatStore.isConnected
);