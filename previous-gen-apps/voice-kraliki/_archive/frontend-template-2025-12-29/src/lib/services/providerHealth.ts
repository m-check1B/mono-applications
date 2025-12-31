import { writable, type Readable } from 'svelte/store';
import { apiGet } from '$lib/utils/api';

export interface ProviderHealthResponse {
	success: boolean;
	timestamp: string;
	providerHealth?: {
		gemini?: {
			status?: string;
			model?: string;
			voice?: string;
		};
	};
	activeConnections?: number;
}

export function createProviderHealthStore(refreshMs = 15000) {
	const state = writable<ProviderHealthResponse | null>(null);
	let timer: ReturnType<typeof setInterval> | null = null;

	async function refresh() {
		try {
			const data = await apiGet<ProviderHealthResponse>('/api/provider-health');
			state.set(data);
		} catch (error) {
			console.error('Failed to fetch provider health', error);
		}
	}

	function start() {
		refresh();
		if (timer) clearInterval(timer);
		timer = setInterval(refresh, refreshMs);
	}

	function stop() {
		if (timer) clearInterval(timer);
		timer = null;
	}

	return {
		subscribe: state.subscribe,
		start,
		stop,
		refresh
	};
}
