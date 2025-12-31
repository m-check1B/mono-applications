import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { exec } from 'child_process';
import { promisify } from 'util';
import path from 'path';

const execAsync = promisify(exec);

const KRALIKI_DIR =
	process.env.KRALIKI_DIR ||
	process.env.KRALIKI_DATA_PATH ||
	'/home/adminmatej/github/applications/kraliki-lab/kraliki-swarm';
const DASHBOARD_DIR = path.join(KRALIKI_DIR, 'dashboard');

export const POST: RequestHandler = async () => {
	const startedAt = new Date().toISOString();

	try {
		await execAsync('pnpm build', { cwd: DASHBOARD_DIR });

		setTimeout(() => {
			exec('pm2 restart kraliki-swarm-dashboard kraliki-swarm-dashboard-local', (err) => {
				if (err) {
					console.error('[dashboard-redeploy] Restart failed:', err);
				}
			});
		}, 500);

		return json({
			success: true,
			message: 'Dashboard build complete; restart queued',
			started_at: startedAt,
			finished_at: new Date().toISOString()
		});
	} catch (error) {
		const message = error instanceof Error ? error.message : 'Unknown error';
		return json({
			success: false,
			message: `Dashboard redeploy failed: ${message}`,
			started_at: startedAt
		}, { status: 500 });
	}
};
