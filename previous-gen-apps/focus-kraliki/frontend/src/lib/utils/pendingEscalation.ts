import { logger } from '$lib/utils/logger';

export type PendingEscalation = {
	telemetryId?: string;
	reason?: Record<string, unknown>;
};

const STORAGE_KEY = 'focus_kraliki_pending_escalation';

const isBrowser = () => typeof window !== 'undefined' && typeof localStorage !== 'undefined';

export function setPendingEscalation(data: PendingEscalation) {
	if (!isBrowser()) return;
	localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
}

export function getPendingEscalation(): PendingEscalation | null {
	if (!isBrowser()) return null;
	const raw = localStorage.getItem(STORAGE_KEY);
	if (!raw) return null;
	try {
		return JSON.parse(raw) as PendingEscalation;
	} catch (err) {
		logger.warn('Failed to parse pending escalation payload', { error: err });
		localStorage.removeItem(STORAGE_KEY);
		return null;
	}
}

export function clearPendingEscalation() {
	if (!isBrowser()) return;
	localStorage.removeItem(STORAGE_KEY);
}
