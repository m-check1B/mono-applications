/**
 * Provider Switching API Client
 *
 * Provides methods for mid-call provider switching with context preservation.
 */

import { apiGet, apiPost } from '$lib/utils/api';

/**
 * Provider switch request payload
 */
export interface ProviderSwitchRequest {
	provider: string;
	preserve_context?: boolean;
	reason?: string;
}

/**
 * Provider switch response
 */
export interface ProviderSwitchResponse {
	success: boolean;
	session_id: string;
	from_provider: string;
	to_provider: string;
	context_preserved: number;
	switched_at: string;
	error_message?: string;
}

/**
 * Switch status response
 */
export interface SwitchStatusResponse {
	in_progress: boolean;
	from_provider?: string;
	to_provider?: string;
	started_at?: string;
	reason?: string;
	status?: string;
	message?: string;
}

/**
 * Provider switch history item
 */
export interface ProviderSwitchHistoryItem {
	from_provider: string;
	to_provider: string;
	switched_at: string;
	context_preserved: number;
	success: boolean;
	error_message?: string;
}

/**
 * Switch history response
 */
export interface SwitchHistoryResponse {
	session_id: string;
	total_switches: number;
	switches: ProviderSwitchHistoryItem[];
}

/**
 * Auto-failover response
 */
export interface AutoFailoverResponse {
	failover_triggered: boolean;
	success?: boolean;
	from_provider?: string;
	to_provider?: string;
	context_preserved?: number;
	switched_at?: string;
	error_message?: string;
	message?: string;
}

/**
 * Switch AI provider for an active session
 *
 * @param sessionId - Session identifier
 * @param provider - Target provider ID (e.g., 'openai', 'gemini', 'deepgram')
 * @param preserveContext - Whether to preserve conversation context (default: true)
 * @param reason - Optional reason for the switch
 * @returns Provider switch result
 */
export async function switchProvider(
	sessionId: string,
	provider: string,
	preserveContext: boolean = true,
	reason?: string
): Promise<ProviderSwitchResponse> {
	const request: ProviderSwitchRequest = {
		provider,
		preserve_context: preserveContext,
		...(reason && { reason })
	};

	return apiPost<ProviderSwitchResponse, ProviderSwitchRequest>(
		`/api/v1/sessions/${sessionId}/switch-provider`,
		request
	);
}

/**
 * Get current provider switch status for a session
 *
 * @param sessionId - Session identifier
 * @returns Switch status information
 */
export async function getSwitchStatus(sessionId: string): Promise<SwitchStatusResponse> {
	return apiGet<SwitchStatusResponse>(`/api/v1/sessions/${sessionId}/switch-status`);
}

/**
 * Get provider switch history for a session
 *
 * @param sessionId - Session identifier
 * @returns History of all provider switches
 */
export async function getSwitchHistory(sessionId: string): Promise<SwitchHistoryResponse> {
	return apiGet<SwitchHistoryResponse>(`/api/v1/sessions/${sessionId}/switch-history`);
}

/**
 * Trigger automatic failover check for a session
 *
 * Checks if the current provider is unhealthy and automatically switches
 * to a healthy alternative if needed.
 *
 * @param sessionId - Session identifier
 * @param force - Force failover even if provider is healthy (default: false)
 * @returns Auto-failover result
 */
export async function triggerAutoFailover(
	sessionId: string,
	force: boolean = false
): Promise<AutoFailoverResponse> {
	return apiPost<AutoFailoverResponse, { force: boolean }>(
		`/api/v1/sessions/${sessionId}/auto-failover`,
		{ force }
	);
}

/**
 * Check if a provider switch is currently in progress
 *
 * @param sessionId - Session identifier
 * @returns True if switch is in progress
 */
export async function isSwitchInProgress(sessionId: string): Promise<boolean> {
	const status = await getSwitchStatus(sessionId);
	return status.in_progress;
}

/**
 * Wait for a provider switch to complete
 *
 * Polls the switch status until the switch is complete or times out.
 *
 * @param sessionId - Session identifier
 * @param pollInterval - Polling interval in milliseconds (default: 500)
 * @param timeout - Maximum wait time in milliseconds (default: 10000)
 * @returns True if switch completed successfully
 */
export async function waitForSwitchCompletion(
	sessionId: string,
	pollInterval: number = 500,
	timeout: number = 10000
): Promise<boolean> {
	const startTime = Date.now();

	while (Date.now() - startTime < timeout) {
		const status = await getSwitchStatus(sessionId);

		if (!status.in_progress) {
			return true;
		}

		await new Promise(resolve => setTimeout(resolve, pollInterval));
	}

	return false;
}

/**
 * Switch provider with automatic retry on failure
 *
 * @param sessionId - Session identifier
 * @param provider - Target provider ID
 * @param preserveContext - Whether to preserve conversation context
 * @param maxRetries - Maximum number of retry attempts (default: 2)
 * @returns Provider switch result
 */
export async function switchProviderWithRetry(
	sessionId: string,
	provider: string,
	preserveContext: boolean = true,
	maxRetries: number = 2
): Promise<ProviderSwitchResponse> {
	let lastError: Error | null = null;

	for (let attempt = 0; attempt <= maxRetries; attempt++) {
		try {
			const result = await switchProvider(sessionId, provider, preserveContext);

			if (result.success) {
				return result;
			}

			// If not successful but no exception, treat as error
			lastError = new Error(result.error_message || 'Switch failed');

			if (attempt < maxRetries) {
				// Wait before retry
				await new Promise(resolve => setTimeout(resolve, 1000 * (attempt + 1)));
			}
		} catch (error) {
			lastError = error as Error;

			if (attempt < maxRetries) {
				// Wait before retry
				await new Promise(resolve => setTimeout(resolve, 1000 * (attempt + 1)));
			}
		}
	}

	throw lastError || new Error('Switch failed after all retries');
}
