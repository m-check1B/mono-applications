import { browser } from '$app/environment';
import { writable, type Readable, get } from 'svelte/store';
import { RealtimeClient } from '$lib/services/realtime';
import { authStore } from '$lib/stores/auth';
import { bootstrapSession, startSession, endSession, type SessionBootstrapResponse } from '$lib/api/sessions';

export type ProviderType = 'gemini' | 'openai' | 'deepgram_nova3';

export type SessionStatus =
	| 'idle'
	| 'connecting'
	| 'connected'
	| 'disconnected'
	| 'error';

export interface SessionState {
	status: SessionStatus;
	provider: ProviderType;
	sessionId?: string;
	metadata?: Record<string, unknown>;
	websocketPath?: string;
	error?: string;
	lastEvent?: unknown;
	lastEventAt?: number;
}

export interface ProviderSession extends Readable<SessionState> {
	connect(): void;
	disconnect(): void;
	send(data: string | ArrayBufferLike | Blob | ArrayBufferView): void;
	reset(): void;
	getState(): SessionState;
	switchProvider(newProvider: ProviderType): Promise<void>;
}

export interface CallSession extends ProviderSession {
	// Call-specific properties and methods
	id: string;
	status: SessionStatus;
	provider: ProviderType;
	callId?: string;
	phoneNumber?: string;
	direction?: 'inbound' | 'outbound';
	startCall(phoneNumber: string, direction?: 'inbound' | 'outbound'): Promise<void>;
	endCall(): Promise<void>;
}

export interface SessionConfig {
	provider?: ProviderType;
	path?: string;
	reconnect?: boolean;
}

export function createProviderSession(config: SessionConfig = {}): ProviderSession {
	const initialProvider = config.provider || 'gemini';

	const initialState: SessionState = {
		status: 'idle',
		provider: initialProvider
	};
	const state = writable<SessionState>(initialState);

	let client: RealtimeClient | null = null;
	let currentProvider = initialProvider;
	let sessionId: string | undefined = undefined;
	let websocketPath: string | undefined = undefined;
	let bootstrapTask: Promise<SessionBootstrapResponse> | null = null;
	let sessionStarted = false;
	let lastBootstrap: SessionBootstrapResponse | null = null;

	function getAccessToken(): string | undefined {
		const snapshot = authStore.getSnapshot();
		return snapshot.tokens?.accessToken;
	}

	async function ensureBootstrap(provider: ProviderType): Promise<SessionBootstrapResponse> {
		if (sessionId && websocketPath && currentProvider === provider && lastBootstrap) {
			return lastBootstrap;
		}

		if (!bootstrapTask) {
			bootstrapTask = bootstrapSession({
				provider_type: provider,
				provider
			});
		}

		let response: SessionBootstrapResponse;
		try {
			response = await bootstrapTask;
		} finally {
			bootstrapTask = null;
		}
		const parsedUrl = (() => {
			try {
				return new URL(response.websocket_url);
			} catch {
				return null;
			}
		})();

		sessionId = response.session_id;
		websocketPath = parsedUrl ? `${parsedUrl.pathname}${parsedUrl.search}` : `/ws/sessions/${sessionId}`;
		sessionStarted = false;
		lastBootstrap = response;

		state.update((prev) => ({
			...prev,
			provider,
			sessionId,
			metadata: response.metadata,
			websocketPath
		}));

		return response;
	}

	function ensureClient(): RealtimeClient {
		if (client) return client;

		if (!websocketPath) {
			throw new Error('Session not initialized');
		}

		client = new RealtimeClient({
			path: websocketPath,
			token: () => getAccessToken(),
			reconnect: config.reconnect ?? false
		});

		client.onOpen(() => {
			state.update(prev => ({ ...prev, status: 'connected', error: undefined }));
		});

		client.onMessage((event) => {
			let payload: unknown = event.data;
			try {
				if (typeof event.data === 'string') {
					payload = JSON.parse(event.data);
				}
			} catch (error) {
				console.warn('Failed to parse realtime payload', error);
			}

			state.update((prev) => ({
				...prev,
				lastEvent: payload,
				lastEventAt: Date.now()
			}));
		});

		client.onError((event) => {
			const message = event instanceof ErrorEvent ? event.message : 'WebSocket error';
			state.update(prev => ({ ...prev, status: 'error', error: message }));
		});

		client.onClose((event) => {
			state.update(prev => ({
				...prev,
				status: 'disconnected',
				error: event.wasClean ? undefined : `Connection closed (${event.code})`
			}));
		});

		return client;
	}

	async function switchProvider(newProvider: ProviderType): Promise<void> {
		if (newProvider === currentProvider) return;

		// Disconnect current client
		if (client) {
			client.disconnect();
			client = null;
		}

		// Reset session tracking
		sessionId = undefined;
		websocketPath = undefined;
		bootstrapTask = null;
		sessionStarted = false;
		lastBootstrap = null;

		// Update provider
		currentProvider = newProvider;
		state.update(prev => ({ ...prev, provider: newProvider, status: 'idle', sessionId: undefined }));

		// Reconnect with new provider if we were connected
		const currentState = get(state);
		if (currentState.status === 'connected' || currentState.status === 'connecting') {
			state.update(prev => ({ ...prev, status: 'connecting' }));
			void ensureBootstrap(newProvider)
				.then(() => ensureClient().connect())
				.catch((error) => {
					console.error('Failed to bootstrap session on provider switch', error);
					state.update(prev => ({ ...prev, status: 'error', error: String(error) }));
				});
		}
	}

	return {
		subscribe: state.subscribe,
		connect() {
			if (!browser) return;
			state.update(prev => ({ ...prev, status: 'connecting' }));
			void ensureBootstrap(currentProvider)
				.then(async () => {
					if (sessionId && !sessionStarted) {
						try {
							await startSession(sessionId);
							sessionStarted = true;
						} catch (error) {
							console.error('Failed to start session', error);
						}
					}
					ensureClient().connect();
				})
				.catch((error) => {
					console.error('Failed to bootstrap session', error);
					state.update(prev => ({ ...prev, status: 'error', error: String(error) }));
				});
		},
		disconnect() {
			if (sessionId) {
				void endSession(sessionId).catch((error) => {
					console.error('Failed to end session', error);
				});
			}
			client?.disconnect();
			client = null;
			sessionId = undefined;
			websocketPath = undefined;
			bootstrapTask = null;
			sessionStarted = false;
			lastBootstrap = null;
			state.update(prev => ({ ...prev, status: 'disconnected', sessionId: undefined }));
		},
		send(data) {
			client?.send(data);
		},
		reset() {
			client?.disconnect();
			client = null;
			sessionId = undefined;
			websocketPath = undefined;
			bootstrapTask = null;
			sessionStarted = false;
			lastBootstrap = null;
			state.set({ ...initialState, provider: currentProvider });
		},
		getState() {
			return get(state);
		},
		async switchProvider(newProvider: ProviderType) {
			await switchProvider(newProvider);
		}
	};
}

// Legacy compatibility - returns a session configured for Gemini
export function createGeminiSession(path = '/test-outbound') {
	return createProviderSession({ provider: 'gemini', path });
}

// New factory functions for specific providers
export function createOpenAISession(path = '/test-outbound') {
	return createProviderSession({ provider: 'openai', path });
}

export function createDeepgramSession(path = '/test-outbound') {
	return createProviderSession({ provider: 'deepgram_nova3', path });
}
