import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

interface Integration {
	name: string;
	type: string;
	status: 'online' | 'offline' | 'unknown';
	url?: string;
	details?: any;
}

async function checkService(url: string): Promise<boolean> {
	try {
		const controller = new AbortController();
		const timeout = setTimeout(() => controller.abort(), 3000);
		const response = await fetch(url, { signal: controller.signal });
		clearTimeout(timeout);
		return response.ok;
	} catch {
		return false;
	}
}

async function checkDocker(container: string): Promise<boolean> {
	try {
		const { stdout } = await execAsync(`docker inspect --format='{{.State.Running}}' ${container} 2>/dev/null`);
		return stdout.trim() === 'true';
	} catch {
		return false;
	}
}

export const GET: RequestHandler = async () => {
	const integrations: Integration[] = [];
	// Docker container IPs - DNS doesn't resolve outside Docker
	const focusUrl = process.env.FOCUS_URL || 'http://172.28.0.4:3017';
	const voiceUrl = process.env.VOICE_URL || 'http://172.27.0.5:8000';
	const speakUrl = process.env.SPEAK_URL || 'http://172.25.0.3:8000';

	// Check EspoCRM
	const espoOnline = await checkService('http://127.0.0.1:8080/api/v1/App/user');
	integrations.push({
		name: 'EspoCRM',
		type: 'crm',
		status: espoOnline ? 'online' : (await checkDocker('espocrm') ? 'online' : 'offline'),
		url: 'http://127.0.0.1:8080'
	});

	// Check Linear MCP
	integrations.push({
		name: 'Linear MCP',
		type: 'mcp',
		status: 'online', // Linear MCP is cloud-based
		url: 'https://mcp.linear.app'
	});

	// Check mgrep
	const mgrepOnline = await checkService('http://127.0.0.1:8001/health');
	integrations.push({
		name: 'mgrep (Semantic Search)',
		type: 'search',
		status: mgrepOnline ? 'online' : 'offline',
		url: 'http://127.0.0.1:8001'
	});

	// Check Redis
	const redisOnline = await checkDocker('kraliki-redis') || await checkDocker('redis');
	integrations.push({
		name: 'Redis',
		type: 'cache',
		status: redisOnline ? 'online' : 'offline'
	});

	// Check Qdrant
	const qdrantOnline = await checkService('http://127.0.0.1:6333/health');
	integrations.push({
		name: 'Qdrant',
		type: 'vector-db',
		status: qdrantOnline ? 'online' : 'offline',
		url: 'http://127.0.0.1:6333'
	});

	// Check N8N
	const n8nOnline = await checkService('http://127.0.0.1:5678/healthz');
	integrations.push({
		name: 'N8N',
		type: 'workflow',
		status: n8nOnline ? 'online' : 'offline',
		url: 'http://127.0.0.1:5678'
	});

	// Check Focus by Kraliki
	const focusOnline = await checkService(`${focusUrl}/health`);
	integrations.push({
		name: 'Focus by Kraliki',
		type: 'app',
		status: focusOnline ? 'online' : 'offline',
		url: focusUrl
	});

	// Check Voice by Kraliki
	const voiceOnline = await checkService(`${voiceUrl}/health`);
	integrations.push({
		name: 'Voice by Kraliki',
		type: 'app',
		status: voiceOnline ? 'online' : 'offline',
		url: voiceUrl
	});

	// Check Speak by Kraliki
	const speakOnline = await checkService(`${speakUrl}/health`);
	integrations.push({
		name: 'Speak by Kraliki',
		type: 'app',
		status: speakOnline ? 'online' : 'offline',
		url: speakUrl
	});

	const onlineCount = integrations.filter(i => i.status === 'online').length;
	const offlineCount = integrations.filter(i => i.status === 'offline').length;

	return json({
		integrations,
		summary: {
			total: integrations.length,
			online: onlineCount,
			offline: offlineCount
		},
		lastUpdated: new Date().toISOString()
	});
};
