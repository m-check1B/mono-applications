import { browser } from '$app/environment';
import { writable, type Readable, get } from 'svelte/store';
import { RealtimeClient } from '$lib/services/realtime';
import { authStore } from '$lib/stores/auth';

// Re-export from providerSession for multi-provider support
export {
	createProviderSession,
	createOpenAISession,
	createDeepgramSession,
	type ProviderSession,
	type ProviderType,
	type SessionConfig
} from './providerSession';

export type GeminiSessionStatus =
	| 'idle'
	| 'connecting'
	| 'connected'
	| 'disconnected'
	| 'error';

export interface GeminiSessionState {
	status: GeminiSessionStatus;
	error?: string;
	lastEvent?: unknown;
	lastEventAt?: number;
}

export interface GeminiSession extends Readable<GeminiSessionState> {
	connect(): void;
	disconnect(): void;
	send(data: string | ArrayBufferLike | Blob | ArrayBufferView): void;
	reset(): void;
	getState(): GeminiSessionState;
}

// Legacy Gemini-specific session (maintained for backwards compatibility)
export function createGeminiSession(path = '/test-outbound'): GeminiSession {
	const initialState: GeminiSessionState = {
		status: 'idle'
	};
	const state = writable<GeminiSessionState>(initialState);

	let client: RealtimeClient | null = null;

	function getAccessToken(): string | undefined {
		const snapshot = authStore.getSnapshot();
		return snapshot.tokens?.accessToken;
	}

	function ensureClient() {
		if (client) return client;
		client = new RealtimeClient({
			path,
			token: () => getAccessToken(),
			reconnect: false
		});

		client.onOpen(() => {
			state.set({ status: 'connected', error: undefined });
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
			state.set({ status: 'error', error: message });
		});

		client.onClose((event) => {
			state.set({
				status: 'disconnected',
				error: event.wasClean ? undefined : `Connection closed (${event.code})`
			});
		});

		return client;
	}

	return {
		subscribe: state.subscribe,
		connect() {
			if (!browser) return;
			state.set({ status: 'connecting' });
			ensureClient().connect();
		},
		disconnect() {
			client?.disconnect();
			client = null;
			state.set({ status: 'disconnected' });
		},
		send(data) {
			client?.send(data);
		},
		reset() {
			client?.disconnect();
			client = null;
			state.set(initialState);
		},
		getState() {
			return get(state);
		}
	};
}
