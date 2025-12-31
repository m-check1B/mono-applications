import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

// Stale threshold: 2 hours in seconds
const STALE_THRESHOLD_SECONDS = 7200;

interface StaleProcess {
	pid: number;
	runtime: number; // seconds
	command: string;
}

async function findStaleAgents(): Promise<StaleProcess[]> {
	const stale: StaleProcess[] = [];

	try {
		// Find Kraliki agent processes with their runtime
		// ps -eo pid,etimes,args gives PID, elapsed time in seconds, and command
		const { stdout } = await execAsync(
			`ps -eo pid,etimes,args 2>/dev/null | grep -E "(Kraliki agent|claude.*append-system-prompt|codex exec|codex.*full-auto|gemini.*-p|opencode run.*--print-logs)" | grep -v grep | grep -v watchdog || true`
		);

		for (const line of stdout.split('\n')) {
			if (!line.trim()) continue;

			const parts = line.trim().split(/\s+/);
			if (parts.length < 3) continue;

			const pid = parseInt(parts[0]);
			const runtime = parseInt(parts[1]);
			const command = parts.slice(2).join(' ').substring(0, 100);

			if (!isNaN(pid) && !isNaN(runtime) && runtime > STALE_THRESHOLD_SECONDS) {
				stale.push({ pid, runtime, command });
			}
		}
	} catch {
		// Ignore errors
	}

	return stale;
}

async function killProcess(pid: number): Promise<boolean> {
	try {
		// Try graceful SIGTERM first
		await execAsync(`kill -15 ${pid} 2>/dev/null || true`);

		// Wait briefly
		await new Promise(resolve => setTimeout(resolve, 1000));

		// Check if still alive, force kill if needed
		try {
			await execAsync(`kill -0 ${pid} 2>/dev/null`);
			// Still alive, force kill
			await execAsync(`kill -9 ${pid} 2>/dev/null || true`);
		} catch {
			// Process already dead, good
		}

		return true;
	} catch {
		return false;
	}
}

export const POST: RequestHandler = async () => {
	try {
		// Find stale agents (running > 2 hours)
		const staleAgents = await findStaleAgents();

		if (staleAgents.length === 0) {
			return json({
				success: true,
				message: 'No stale agents found',
				killed: 0,
				threshold_hours: STALE_THRESHOLD_SECONDS / 3600,
				timestamp: new Date().toISOString()
			});
		}

		// Kill each stale agent
		const killed: { pid: number; runtime_hours: number }[] = [];

		for (const agent of staleAgents) {
			const success = await killProcess(agent.pid);
			if (success) {
				killed.push({
					pid: agent.pid,
					runtime_hours: Math.round(agent.runtime / 3600 * 10) / 10
				});
			}
		}

		return json({
			success: true,
			message: `Killed ${killed.length} stale agent(s)`,
			killed: killed.length,
			details: killed,
			threshold_hours: STALE_THRESHOLD_SECONDS / 3600,
			timestamp: new Date().toISOString()
		});
	} catch (error) {
		const message = error instanceof Error ? error.message : 'Unknown error';
		return json({
			success: false,
			message: `Soft reset failed: ${message}`
		}, { status: 500 });
	}
};

// GET endpoint to check for stale agents without killing
export const GET: RequestHandler = async () => {
	try {
		const staleAgents = await findStaleAgents();

		return json({
			stale_count: staleAgents.length,
			threshold_hours: STALE_THRESHOLD_SECONDS / 3600,
			stale_agents: staleAgents.map(a => ({
				pid: a.pid,
				runtime_hours: Math.round(a.runtime / 3600 * 10) / 10,
				command: a.command
			})),
			timestamp: new Date().toISOString()
		});
	} catch (error) {
		const message = error instanceof Error ? error.message : 'Unknown error';
		return json({
			success: false,
			message
		}, { status: 500 });
	}
};
