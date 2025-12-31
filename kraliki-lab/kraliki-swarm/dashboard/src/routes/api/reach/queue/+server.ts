import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';

// Voice by Kraliki backend URL (Docker container IP)
const VOICE_URL = process.env.VOICE_URL || 'http://172.21.0.27:8000';

interface QueueItem {
	id: string;
	channel: 'voice' | 'sms' | 'email' | 'chat';
	type: 'inbound' | 'outbound';
	status: 'waiting' | 'in_progress' | 'completed' | 'failed';
	caller?: string;
	callee?: string;
	waitTime: number;
	startedAt: string;
	agent?: string;
}

async function fetchVoiceQueue(): Promise<QueueItem[]> {
	try {
		const controller = new AbortController();
		const timeoutId = setTimeout(() => controller.abort(), 5000);

		const response = await fetch(`${VOICE_URL}/api/queue/available-agents`, {
			signal: controller.signal
		});

		clearTimeout(timeoutId);

		if (response.ok) {
			// Queue data might be nested in response
			return [];
		}
		return [];
	} catch {
		return [];
	}
}

async function fetchVoicemails(): Promise<QueueItem[]> {
	try {
		const controller = new AbortController();
		const timeoutId = setTimeout(() => controller.abort(), 5000);

		const response = await fetch(`${VOICE_URL}/voicemails`, {
			signal: controller.signal
		});

		clearTimeout(timeoutId);

		if (response.ok) {
			const data = await response.json();
			if (Array.isArray(data)) {
				return data.map((vm: Record<string, unknown>) => ({
					id: String(vm.id),
					channel: 'voice' as const,
					type: 'inbound' as const,
					status: vm.heard ? 'completed' as const : 'waiting' as const,
					caller: String(vm.caller || vm.from_number || 'Unknown'),
					waitTime: 0,
					startedAt: String(vm.created_at || new Date().toISOString())
				}));
			}
		}
		return [];
	} catch {
		return [];
	}
}

export const GET: RequestHandler = async ({ url }) => {
	const type = url.searchParams.get('type') || 'all';

	const queueItems = await fetchVoiceQueue();
	const voicemails = await fetchVoicemails();

	let items = [...queueItems, ...voicemails];

	if (type === 'inbound') {
		items = items.filter(i => i.type === 'inbound');
	} else if (type === 'outbound') {
		items = items.filter(i => i.type === 'outbound');
	}

	return json({
		items,
		total: items.length,
		waiting: items.filter(i => i.status === 'waiting').length,
		inProgress: items.filter(i => i.status === 'in_progress').length,
		avgWaitTime: items.length > 0
			? Math.round(items.reduce((sum, i) => sum + i.waitTime, 0) / items.length)
			: 0
	});
};
