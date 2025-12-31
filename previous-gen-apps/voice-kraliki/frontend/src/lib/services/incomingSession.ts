import { writable, get, type Readable } from 'svelte/store';
import { createGeminiSession, type GeminiSessionState } from '$lib/services/audioSession';
import { createAudioManager } from '$lib/services/audioManager';
import { int16ToBase64 } from '$lib/utils/pcm';

export type IncomingStatus = 'idle' | 'connecting' | 'connected' | 'error';

export interface IncomingEvent {
	type: string;
	[key: string]: unknown;
}

export interface IncomingState {
	status: IncomingStatus;
	session: GeminiSessionState;
	audioStatus: string;
	activeCall?: {
		from?: string;
		metadata?: unknown;
	};
	lastEvent?: IncomingEvent;
	error?: string;
}

export interface IncomingSession extends Readable<IncomingState> {
	connect(): void;
	disconnect(): void;
	accept(): Promise<void>;
	decline(): void;
	getState(): IncomingState;
}

export function createIncomingSession(path = '/test-inbound'): IncomingSession {
	const gemini = createGeminiSession(path);
	const audioManager = createAudioManager();

	const state = writable<IncomingState>({
		status: 'idle',
		session: gemini.getState(),
		audioStatus: audioManager.getState().status
	});

	let lastProcessedEventAt: number | null = null;

	const unsubSession = gemini.subscribe((session) => {
		state.update((prev) => ({
			...prev,
			session,
			status: session.status === 'error' ? 'error' : session.status === 'connected' ? 'connected' : session.status === 'connecting' ? 'connecting' : prev.status
		}));
	});

	const unsubAudio = audioManager.subscribe((audio) => {
		state.update((prev) => ({ ...prev, audioStatus: audio.status }));
	});

	audioManager.sendCapturedFrame((buffer) => {
		const base64 = int16ToBase64(buffer);
		try {
			gemini.send(
				JSON.stringify({ type: 'audio-data', audioData: base64 })
			);
		} catch (error) {
			console.error('Failed to send inbound audio frame', error);
		}
	});

	function updateFromEvent(event: IncomingEvent) {
		switch (event.type) {
			case 'call-offer':
				state.update((prev) => ({
					...prev,
					activeCall: {
						from: typeof event.from === 'string' ? event.from : undefined,
						metadata: event
					},
					lastEvent: event
				}));
				break;
			case 'call-ended':
				state.update((prev) => ({
					...prev,
					activeCall: undefined,
					lastEvent: event
				}));
				break;
			case 'audio':
				if (typeof event.audio === 'string') {
					audioManager
						.playBase64Audio(event.audio as string, typeof event.mimeType === 'string' ? event.mimeType : undefined)
						.catch((error) => {
							console.error('Failed to play inbound audio chunk', error);
						});
				}
				break;
			default:
				state.update((prev) => ({ ...prev, lastEvent: event }));
		}
	}

	const unsubscribeRealtime = gemini.subscribe((session) => {
		if (!session.lastEventAt || session.lastEventAt === lastProcessedEventAt) return;
		lastProcessedEventAt = session.lastEventAt;

		const payload = session.lastEvent;
		if (payload && typeof payload === 'object' && 'type' in payload) {
			updateFromEvent(payload as IncomingEvent);
		}
	});

	return {
		subscribe: state.subscribe,
		connect() {
			state.update((prev) => ({ ...prev, status: 'connecting', error: undefined }));
			gemini.connect();
		},
		disconnect() {
			gemini.disconnect();
			audioManager.stop();
			state.update((prev) => ({
				...prev,
				status: 'idle',
				activeCall: undefined
			}));
		},
		async accept() {
			const result = await audioManager.startMicrophone();
			if (!result.success) {
				state.update((prev) => ({ ...prev, error: result.error ?? 'Microphone access failed.' }));
				return;
			}
			gemini.send(JSON.stringify({ type: 'accept-call' }));
		},
		decline() {
			gemini.send(JSON.stringify({ type: 'decline-call' }));
			state.update((prev) => ({ ...prev, activeCall: undefined }));
		},
		getState() {
			return get(state);
		}
	};
}
