import { crossTabSync } from './crossTabSync';

export interface SessionData {
	sessionId: string;
	status: 'active' | 'ended' | 'paused';
	data?: any;
	timestamp: number;
}

/**
 * Broadcast session update to other tabs
 */
export function broadcastSessionUpdate(sessionId: string, data: any): void {
	if (crossTabSync.isAvailable()) {
		crossTabSync.broadcast('session_updated', {
			sessionId,
			data,
			timestamp: Date.now()
		});
	}
}

/**
 * Broadcast session end to other tabs
 */
export function broadcastSessionEnd(sessionId: string): void {
	if (crossTabSync.isAvailable()) {
		crossTabSync.broadcast('session_ended', {
			sessionId,
			timestamp: Date.now()
		});
	}
}

/**
 * Subscribe to session updates from other tabs
 */
export function subscribeToSessionUpdates(
	callback: (sessionId: string, data: any) => void
): () => void {
	if (!crossTabSync.isAvailable()) {
		return () => {};
	}

	return crossTabSync.subscribe('session_updated', (message) => {
		const { sessionId, data } = message.payload;
		callback(sessionId, data);
	});
}

/**
 * Subscribe to session end events from other tabs
 */
export function subscribeToSessionEnd(callback: (sessionId: string) => void): () => void {
	if (!crossTabSync.isAvailable()) {
		return () => {};
	}

	return crossTabSync.subscribe('session_ended', (message) => {
		const { sessionId } = message.payload;
		callback(sessionId);
	});
}

/**
 * Check if cross-tab sync is available
 */
export function isSyncAvailable(): boolean {
	return crossTabSync.isAvailable();
}
