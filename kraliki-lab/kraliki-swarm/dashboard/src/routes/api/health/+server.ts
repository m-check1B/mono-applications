import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

interface HealthCheck {
	service: string;
	status: 'healthy' | 'unhealthy' | 'unknown';
	message?: string;
}

async function checkPm2(): Promise<HealthCheck> {
	try {
		const { stdout } = await execAsync('pm2 jlist 2>/dev/null');
		const processes = JSON.parse(stdout);
		const online = processes.filter((p: any) => p.pm2_env?.status === 'online').length;
		const total = processes.length;
		return {
			service: 'pm2',
			status: online === total ? 'healthy' : 'unhealthy',
			message: `${online}/${total} processes online`
		};
	} catch {
		return { service: 'pm2', status: 'unknown', message: 'pm2 not available' };
	}
}

async function checkRedis(): Promise<HealthCheck> {
	try {
		const { stdout } = await execAsync('docker exec kraliki-redis redis-cli ping 2>/dev/null || redis-cli ping 2>/dev/null');
		return {
			service: 'redis',
			status: stdout.trim() === 'PONG' ? 'healthy' : 'unhealthy'
		};
	} catch {
		return { service: 'redis', status: 'unknown' };
	}
}

export const GET: RequestHandler = async () => {
	const checks = await Promise.all([checkPm2(), checkRedis()]);

	const allHealthy = checks.every((c) => c.status === 'healthy');

	return json({
		status: allHealthy ? 'healthy' : 'degraded',
		timestamp: new Date().toISOString(),
		checks
	});
};
