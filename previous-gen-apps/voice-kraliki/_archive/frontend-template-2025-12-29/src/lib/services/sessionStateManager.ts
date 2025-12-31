/**
 * Session State Manager
 * 
 * Handles state persistence and recovery for agent sessions:
 * - Automatic state saving to localStorage
 * - Session recovery on page refresh
 * - Error state management and recovery
 * - Provider switching state preservation
 * - Call state persistence
 */

import { browser } from '$app/environment';
import { writable, type Readable, get } from 'svelte/store';
import type { ProviderType } from './providerSession';
import { logger } from '$lib/utils/logger';

export interface CallState {
	id: string;
	phoneNumber?: string;
	direction?: 'inbound' | 'outbound';
	status: 'idle' | 'connecting' | 'active' | 'ended' | 'error';
	startTime?: number;
	duration?: number;
	provider?: ProviderType;
	metadata?: Record<string, any>;
}

export interface ErrorState {
	code: string;
	message: string;
	timestamp: number;
	context?: Record<string, any>;
	recoverable: boolean;
	recoveryAction?: () => Promise<void>;
}

export interface SessionState {
	call: CallState | null;
	provider: ProviderType;
	audio: {
		isMuted: boolean;
		isRecording: boolean;
		inputLevel: number;
		outputLevel: number;
	};
	ui: {
		activePanel: 'transcription' | 'insights' | 'controls' | 'settings';
		sidebarOpen: boolean;
		theme: 'light' | 'dark';
	};
	errors: ErrorState[];
	lastActivity: number;
	version: string;
}

export interface SessionStateManager extends Readable<SessionState> {
	saveState(): void;
	restoreState(): boolean;
	clearState(): void;
	updateCallState(call: Partial<CallState>): void;
	updateProvider(provider: ProviderType): void;
	updateAudioState(audio: Partial<SessionState['audio']>): void;
	updateUIState(ui: Partial<SessionState['ui']>): void;
	addError(error: Omit<ErrorState, 'timestamp'>): void;
	clearErrors(): void;
	recoverFromError(errorCode: string): Promise<boolean>;
	getCallHistory(): CallState[];
	exportState(): string;
	importState(stateJson: string): boolean;
}

const STATE_VERSION = '1.0.0';
const STORAGE_KEY = 'voice-kraliki-session-state';
const MAX_CALL_HISTORY = 10;
const STATE_THROTTLE_MS = 1000;

export function createSessionStateManager(): SessionStateManager {
	const initialState: SessionState = {
		call: null,
		provider: 'gemini',
		audio: {
			isMuted: false,
			isRecording: false,
			inputLevel: 0,
			outputLevel: 0
		},
		ui: {
			activePanel: 'transcription',
			sidebarOpen: true,
			theme: 'light'
		},
		errors: [],
		lastActivity: Date.now(),
		version: STATE_VERSION
	};

	const state = writable<SessionState>(initialState);
	let saveTimeout: ReturnType<typeof setTimeout> | null = null;
	let callHistory: CallState[] = [];

	function throttleSave(): void {
		if (saveTimeout) {
			clearTimeout(saveTimeout);
		}
		saveTimeout = setTimeout(() => {
			saveState();
			saveTimeout = null;
		}, STATE_THROTTLE_MS);
	}

	function saveState(): void {
		if (!browser) return;

		try {
			const currentState = get(state);
			const stateToSave = {
				...currentState,
				lastActivity: Date.now()
			};

			localStorage.setItem(STORAGE_KEY, JSON.stringify(stateToSave));
			logger.debug('Session state saved');
		} catch (error) {
			logger.error('Failed to save session state', error as Error);
		}
	}

	function restoreState(): boolean {
		if (!browser) return false;

		try {
			const savedState = localStorage.getItem(STORAGE_KEY);
			if (!savedState) return false;

			const parsedState = JSON.parse(savedState);
			
			// Version check
			if (parsedState.version !== STATE_VERSION) {
				logger.warn('State version mismatch, clearing old state', { version: parsedState.version });
				clearState();
				return false;
			}

			// Validate state structure
			if (!validateState(parsedState)) {
				logger.warn('Invalid state structure, clearing state');
				clearState();
				return false;
			}

			// Restore call history if exists
			if (parsedState.callHistory) {
				callHistory = parsedState.callHistory.slice(0, MAX_CALL_HISTORY);
			}

			// Clear current call (don't restore active calls across refreshes)
			const restoredState = {
				...parsedState,
				call: null,
				audio: {
					...parsedState.audio,
					isRecording: false,
					inputLevel: 0,
					outputLevel: 0
				},
				errors: parsedState.errors.filter((error: ErrorState) => 
					Date.now() - error.timestamp < 300000 // Keep errors from last 5 minutes
				)
			};

			state.set(restoredState);
			logger.info('Session state restored');
			return true;
		} catch (error) {
			logger.error('Failed to restore session state', error as Error);
			clearState();
			return false;
		}
	}

	function clearState(): void {
		if (!browser) return;

		try {
			localStorage.removeItem(STORAGE_KEY);
			state.set(initialState);
			callHistory = [];
			logger.info('Session state cleared');
		} catch (error) {
			logger.error('Failed to clear session state', error as Error);
		}
	}

	function validateState(state: any): boolean {
		if (!state || typeof state !== 'object') return false;
		if (!state.version || !state.provider || !state.audio || !state.ui) return false;
		if (!['gemini', 'openai', 'deepgram_nova3'].includes(state.provider)) return false;
		return true;
	}

	function updateCallState(callUpdate: Partial<CallState>): void {
		state.update(current => {
			const newCall = current.call ? { ...current.call, ...callUpdate } : callUpdate;
			
			// If call is ending, add to history
			if (current.call && callUpdate.status === 'ended') {
				const endedCall = { ...current.call, ...callUpdate };
				callHistory = [endedCall, ...callHistory.slice(0, MAX_CALL_HISTORY - 1)];
			}

			return {
				...current,
				call: newCall as CallState | null
			};
		});
		throttleSave();
	}

	function updateProvider(provider: ProviderType): void {
		state.update(current => ({
			...current,
			provider
		}));
		throttleSave();
	}

	function updateAudioState(audioUpdate: Partial<SessionState['audio']>): void {
		state.update(current => ({
			...current,
			audio: { ...current.audio, ...audioUpdate }
		}));
		throttleSave();
	}

	function updateUIState(uiUpdate: Partial<SessionState['ui']>): void {
		state.update(current => ({
			...current,
			ui: { ...current.ui, ...uiUpdate }
		}));
		throttleSave();
	}

	function addError(error: Omit<ErrorState, 'timestamp'>): void {
		const errorWithTimestamp: ErrorState = {
			...error,
			timestamp: Date.now()
		};

		state.update(current => ({
			...current,
			errors: [...current.errors.slice(-9), errorWithTimestamp] // Keep last 10 errors
		}));
		throttleSave();
	}

	function clearErrors(): void {
		state.update(current => ({
			...current,
			errors: []
		}));
		throttleSave();
	}

	async function recoverFromError(errorCode: string): Promise<boolean> {
		const currentState = get(state);
		const error = currentState.errors.find(e => e.code === errorCode);
		
		if (!error || !error.recoverable || !error.recoveryAction) {
			return false;
		}

		try {
			logger.info('Attempting to recover from error', { errorCode });
			await error.recoveryAction();
			
			// Remove the error after successful recovery
			state.update(current => ({
				...current,
				errors: current.errors.filter(e => e.code !== errorCode)
			}));
			
			throttleSave();
			return true;
		} catch (recoveryError) {
			logger.error('Failed to recover from error', recoveryError as Error, { errorCode });
			return false;
		}
	}

	function getCallHistory(): CallState[] {
		return [...callHistory];
	}

	function exportState(): string {
		const currentState = get(state);
		const exportData = {
			...currentState,
			callHistory,
			exportedAt: Date.now()
		};
		return JSON.stringify(exportData, null, 2);
	}

	function importState(stateJson: string): boolean {
		try {
			const importedData = JSON.parse(stateJson);
			
			if (!validateState(importedData)) {
				throw new Error('Invalid state structure');
			}

			if (importedData.callHistory) {
				callHistory = importedData.callHistory.slice(0, MAX_CALL_HISTORY);
			}

			// Don't import active calls
			const importedState = {
				...importedData,
				call: null,
				audio: {
					...importedData.audio,
					isRecording: false,
					inputLevel: 0,
					outputLevel: 0
				}
			};

			state.set(importedState);
			throttleSave();
			logger.info('State imported successfully');
			return true;
		} catch (error) {
			logger.error('Failed to import state', error as Error);
			return false;
		}
	}

	// Auto-save on state changes
	state.subscribe(() => {
		throttleSave();
	});

	// Cleanup old errors periodically
	setInterval(() => {
		const currentState = get(state);
		const recentErrors = currentState.errors.filter(error => 
			Date.now() - error.timestamp < 300000 // 5 minutes
		);

		if (recentErrors.length !== currentState.errors.length) {
			state.update(current => ({
				...current,
				errors: recentErrors
			}));
		}
	}, 60000); // Check every minute

	return {
		subscribe: state.subscribe,
		saveState,
		restoreState,
		clearState,
		updateCallState,
		updateProvider,
		updateAudioState,
		updateUIState,
		addError,
		clearErrors,
		recoverFromError,
		getCallHistory,
		exportState,
		importState
	};
}

// Error recovery utilities
export const ErrorRecoveryActions = {
	// Microphone access recovery
	async recoverMicrophoneAccess(): Promise<void> {
		try {
			// Request microphone access again
			await navigator.mediaDevices.getUserMedia({ audio: true });
			logger.info('Microphone access recovered');
		} catch (error) {
			throw new Error('Failed to recover microphone access');
		}
	},

	// WebSocket connection recovery
	async recoverWebSocketConnection(): Promise<void> {
		// This would be implemented by the calling component
		// as it needs access to the WebSocket instance
		logger.info('WebSocket connection recovery requested');
	},

	// Provider switching recovery
	async recoverProviderSwitch(): Promise<void> {
		// This would be implemented by the calling component
		logger.info('Provider switch recovery requested');
	},

	// Audio context recovery
	async recoverAudioContext(): Promise<void> {
		try {
			// Create new audio context
			const AudioContext = window.AudioContext || (window as any).webkitAudioContext;
			const newContext = new AudioContext();
			await newContext.resume();
			logger.info('Audio context recovered');
		} catch (error) {
			throw new Error('Failed to recover audio context');
		}
	}
};

// Common error definitions
export const CommonErrors = {
	MICROPHONE_ACCESS_DENIED: {
		code: 'MICROPHONE_ACCESS_DENIED',
		message: 'Microphone access was denied. Please allow microphone access and try again.',
		recoverable: true,
		recoveryAction: ErrorRecoveryActions.recoverMicrophoneAccess
	},
	WEBSOCKET_CONNECTION_FAILED: {
		code: 'WEBSOCKET_CONNECTION_FAILED',
		message: 'WebSocket connection failed. Please check your internet connection.',
		recoverable: true,
		recoveryAction: ErrorRecoveryActions.recoverWebSocketConnection
	},
	PROVIDER_SWITCH_FAILED: {
		code: 'PROVIDER_SWITCH_FAILED',
		message: 'Failed to switch provider. Please try again.',
		recoverable: true,
		recoveryAction: ErrorRecoveryActions.recoverProviderSwitch
	},
	AUDIO_CONTEXT_FAILED: {
		code: 'AUDIO_CONTEXT_FAILED',
		message: 'Audio context initialization failed. Please refresh the page.',
		recoverable: true,
		recoveryAction: ErrorRecoveryActions.recoverAudioContext
	}
} as const;
