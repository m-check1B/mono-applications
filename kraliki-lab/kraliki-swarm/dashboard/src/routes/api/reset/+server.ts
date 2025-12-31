import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

const KRALIKI_BASE = process.env.KRALIKI_DIR || process.env.KRALIKI_DATA_PATH || '/home/adminmatej/github/applications/kraliki-lab/kraliki-swarm';

export const POST: RequestHandler = async () => {
	const results: string[] = [];

	try {
		// 1. Kill zombie agent processes (claude, codex, gemini, opencode CLIs running as agents)
		const killPatterns = [
			'Kraliki agent',
			'claude.*--append-system-prompt',
			'codex.*--full-auto',
			'gemini.*-p',
			'opencode.*--agent'
		];

		for (const pattern of killPatterns) {
			try {
				await execAsync(`pkill -9 -f "${pattern}" 2>/dev/null || true`);
			} catch {
				// Ignore errors - process may not exist
			}
		}
		results.push('Killed zombie agents');

		// 2. Clear stale agent state files
		try {
			await execAsync(`rm -f ${KRALIKI_BASE}/control/orchestrators/*.json 2>/dev/null || true`);
			results.push('Cleared orchestrator state');
		} catch {
			// Ignore
		}

		// 3. Stop all PM2 Kraliki processes except dashboard (to avoid killing ourselves)
		const stopProcesses = [
			'kraliki-watchdog-claude',
			'kraliki-watchdog-opencode',
			'kraliki-watchdog-gemini',
			'kraliki-watchdog-codex',
			'kraliki-health',
			'kraliki-stats',
			'kraliki-n8n-api',
			'kraliki-comm',
			'kraliki-comm-zt',
			'kraliki-comm-ws',
			'kraliki-msg-poller',
			'kraliki-linear-sync',
			'kraliki-agent-board',
			'kraliki-recall',
			'kraliki-events-bridge'
		];

		for (const proc of stopProcesses) {
			try {
				await execAsync(`pm2 stop ${proc} 2>/dev/null || true`);
			} catch {
				// Ignore
			}
		}
		results.push('Stopped PM2 processes');

		// 4. Restart all PM2 Kraliki processes fresh (except dashboard which is already running)
		for (const proc of stopProcesses) {
			try {
				await execAsync(`pm2 restart ${proc} 2>/dev/null || true`);
			} catch {
				// Ignore
			}
		}
		results.push('Started PM2 processes');

		return json({
			success: true,
			message: 'Kraliki swarm reset complete',
			details: results,
			timestamp: new Date().toISOString()
		});
	} catch (error) {
		const message = error instanceof Error ? error.message : 'Unknown error';
		return json({
			success: false,
			message: `Reset failed: ${message}`,
			details: results
		}, { status: 500 });
	}
};
