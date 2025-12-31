import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);
const DARWIN2_DIR = process.env.KRALIKI_DIR || process.env.DARWIN2_PATH || '/home/adminmatej/github/applications/kraliki-lab/kraliki-swarm';
const SPAWN_SCRIPT = `${DARWIN2_DIR}/agents/spawn.py`;

export const POST: RequestHandler = async ({ request }) => {
	try {
		const { genome } = await request.json();

		if (!genome) {
			return json({ error: 'Genome name required' }, { status: 400 });
		}

		// Run spawn script
		const { stdout, stderr } = await execAsync(
			`python3 ${SPAWN_SCRIPT} ${genome}`,
			{ cwd: DARWIN2_DIR }
		);

		return json({
			success: true,
			genome,
			output: stdout,
			error: stderr || null
		});
	} catch (e) {
		console.error('Failed to spawn agent:', e);
		return json({
			error: 'Failed to spawn agent',
			details: e instanceof Error ? e.message : 'Unknown error'
		}, { status: 500 });
	}
};
