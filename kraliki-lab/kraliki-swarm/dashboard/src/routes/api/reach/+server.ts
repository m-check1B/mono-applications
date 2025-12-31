import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';

// Voice by Kraliki backend URL (Docker container IP)
const VOICE_URL = process.env.VOICE_URL || 'http://172.21.0.27:8000';

interface ChannelStatus {
	id: string;
	name: string;
	status: 'active' | 'inactive' | 'coming';
	provider: string;
	inbound: number;
	outbound: number;
	lastActivity?: string;
}

interface ReachStats {
	totalInbound: number;
	totalOutbound: number;
	activeChannels: number;
	avgResponseTime: number;
	voiceStatus: 'online' | 'offline';
	channels: ChannelStatus[];
}

async function checkVoiceHealth(): Promise<boolean> {
	try {
		const controller = new AbortController();
		const timeoutId = setTimeout(() => controller.abort(), 2000);

		const response = await fetch(`${VOICE_URL}/health`, {
			signal: controller.signal
		});

		clearTimeout(timeoutId);
		return response.ok;
	} catch {
		return false;
	}
}

async function getVoiceAnalytics(): Promise<{ inbound: number; outbound: number }> {
	try {
		const controller = new AbortController();
		const timeoutId = setTimeout(() => controller.abort(), 3000);

		const response = await fetch(`${VOICE_URL}/api/analytics/dashboard/overview`, {
			signal: controller.signal
		});

		clearTimeout(timeoutId);

		if (response.ok) {
			const data = await response.json();
			return {
				inbound: data.inbound_calls || data.total_inbound || 0,
				outbound: data.outbound_calls || data.total_outbound || 0
			};
		}
		return { inbound: 0, outbound: 0 };
	} catch {
		return { inbound: 0, outbound: 0 };
	}
}

export const GET: RequestHandler = async () => {
	const voiceOnline = await checkVoiceHealth();
	const voiceStats = voiceOnline ? await getVoiceAnalytics() : { inbound: 0, outbound: 0 };

	const channels: ChannelStatus[] = [
		{
			id: 'voice',
			name: 'Voice/Calls',
			status: voiceOnline ? 'active' : 'inactive',
			provider: 'Voice by Kraliki',
			inbound: voiceStats.inbound,
			outbound: voiceStats.outbound,
			lastActivity: voiceOnline ? new Date().toISOString() : undefined
		},
		{
			id: 'sms',
			name: 'SMS',
			status: 'coming',
			provider: 'Twilio (planned)',
			inbound: 0,
			outbound: 0
		},
		{
			id: 'email',
			name: 'Email',
			status: 'coming',
			provider: 'SMTP (planned)',
			inbound: 0,
			outbound: 0
		},
		{
			id: 'chat',
			name: 'Chat',
			status: 'coming',
			provider: 'Voice by Kraliki Chat API',
			inbound: 0,
			outbound: 0
		},
		{
			id: 'social',
			name: 'Social',
			status: 'coming',
			provider: 'Meta/LinkedIn (planned)',
			inbound: 0,
			outbound: 0
		}
	];

	const stats: ReachStats = {
		totalInbound: channels.reduce((sum, c) => sum + c.inbound, 0),
		totalOutbound: channels.reduce((sum, c) => sum + c.outbound, 0),
		activeChannels: channels.filter(c => c.status === 'active').length,
		avgResponseTime: 0,
		voiceStatus: voiceOnline ? 'online' : 'offline',
		channels
	};

	return json(stats);
};
