import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { readFile, writeFile } from 'fs/promises';
import { existsSync } from 'fs';
import { spawn } from 'child_process';

const POLICY_FILE = '/home/adminmatej/github/applications/kraliki-lab/kraliki-swarm/config/cli_policy.json';
const PAUSE_STATE_FILE = '/home/adminmatej/github/applications/kraliki-lab/kraliki-swarm/config/pause_state.json';

interface CliConfig {
	enabled: boolean;
	reason?: string;
	priority?: number;
	disabled_until?: string;
}

interface CliPolicy {
	_description?: string;
	_updated?: string;
	clis: Record<string, CliConfig>;
	notes?: Record<string, unknown>;
}

interface PauseState {
	paused: boolean;
	paused_at?: string;
	paused_by?: string;
	previous_cli_state?: Record<string, CliConfig>;
}

async function loadPolicy(): Promise<CliPolicy> {
	try {
		if (existsSync(POLICY_FILE)) {
			const content = await readFile(POLICY_FILE, 'utf-8');
			return JSON.parse(content);
		}
	} catch (e) {
		console.error('Failed to load CLI policy:', e);
	}
	return {
		clis: {
			opencode: { enabled: true, reason: 'Default', priority: 1 },
			gemini: { enabled: true, reason: 'Default', priority: 2 },
			codex: { enabled: true, reason: 'Default', priority: 3 },
			claude: { enabled: true, reason: 'Default', priority: 4 }
		}
	};
}

async function savePolicy(policy: CliPolicy): Promise<void> {
	policy._updated = new Date().toISOString().split('T')[0];
	await writeFile(POLICY_FILE, JSON.stringify(policy, null, 2));
}

async function loadPauseState(): Promise<PauseState> {
	try {
		if (existsSync(PAUSE_STATE_FILE)) {
			const content = await readFile(PAUSE_STATE_FILE, 'utf-8');
			return JSON.parse(content);
		}
	} catch (e) {
		console.error('Failed to load pause state:', e);
	}
	return { paused: false };
}

async function savePauseState(state: PauseState): Promise<void> {
	await writeFile(PAUSE_STATE_FILE, JSON.stringify(state, null, 2));
}

// Kill running Claude/Codex agent processes
async function killAgentProcesses(): Promise<number> {
	return new Promise((resolve) => {
		const proc = spawn('pkill', ['-f', 'claude.*--print'], { stdio: 'ignore' });
		proc.on('close', (code) => {
			// Also kill codex processes
			const proc2 = spawn('pkill', ['-f', 'codex.*--dangerously-auto-edit'], { stdio: 'ignore' });
			proc2.on('close', () => {
				// Return approximate count (actual count not critical)
				resolve(code === 0 ? 1 : 0);
			});
		});
	});
}

// GET: Check current pause state
export const GET: RequestHandler = async () => {
	const pauseState = await loadPauseState();
	return json({
		paused: pauseState.paused,
		paused_at: pauseState.paused_at,
		paused_by: pauseState.paused_by
	});
};

// POST: Toggle pause state
export const POST: RequestHandler = async ({ request }) => {
	try {
		const body = await request.json();
		const { action, kill_running } = body;

		const currentPauseState = await loadPauseState();
		const policy = await loadPolicy();

		if (action === 'pause') {
			if (currentPauseState.paused) {
				return json({ success: false, message: 'Already paused', paused: true });
			}

			// Save current CLI states before disabling
			const previousState: Record<string, CliConfig> = {};
			for (const [cli, config] of Object.entries(policy.clis)) {
				previousState[cli] = { ...config };
			}

			// Disable all CLIs
			for (const cli of Object.keys(policy.clis)) {
				policy.clis[cli].enabled = false;
				policy.clis[cli].reason = 'PAUSED: All swarm activities paused via dashboard';
			}

			await savePolicy(policy);

			// Save pause state with previous CLI config
			const newPauseState: PauseState = {
				paused: true,
				paused_at: new Date().toISOString(),
				paused_by: 'dashboard',
				previous_cli_state: previousState
			};
			await savePauseState(newPauseState);

			// Optionally kill running agents
			let killed = 0;
			if (kill_running) {
				killed = await killAgentProcesses();
			}

			return json({
				success: true,
				paused: true,
				paused_at: newPauseState.paused_at,
				killed_agents: killed,
				message: `SWARM_PAUSED${killed > 0 ? ` (${killed} agents killed)` : ''}`
			});
		} else if (action === 'resume') {
			if (!currentPauseState.paused) {
				return json({ success: false, message: 'Not paused', paused: false });
			}

			// Restore previous CLI states
			if (currentPauseState.previous_cli_state) {
				for (const [cli, config] of Object.entries(currentPauseState.previous_cli_state)) {
					if (policy.clis[cli]) {
						policy.clis[cli] = { ...config, reason: 'Restored after pause' };
					}
				}
			} else {
				// Fallback: enable all CLIs
				for (const cli of Object.keys(policy.clis)) {
					policy.clis[cli].enabled = true;
					policy.clis[cli].reason = 'Enabled after pause (default restore)';
				}
			}

			await savePolicy(policy);

			// Clear pause state
			await savePauseState({ paused: false });

			return json({
				success: true,
				paused: false,
				message: 'SWARM_RESUMED'
			});
		} else {
			return json({ error: 'Invalid action. Use "pause" or "resume"' }, { status: 400 });
		}
	} catch (e) {
		console.error('Failed to toggle pause state:', e);
		return json({ error: 'Failed to toggle pause state' }, { status: 500 });
	}
};
