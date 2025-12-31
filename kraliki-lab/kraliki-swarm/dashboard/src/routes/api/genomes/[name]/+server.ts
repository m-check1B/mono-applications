import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { readFile } from 'fs/promises';
import { existsSync } from 'fs';

const GENOMES_DIR = process.env.GENOMES_PATH || '/home/adminmatej/github/applications/kraliki-lab/kraliki-swarm/genomes';

export const GET: RequestHandler = async ({ params }) => {
	try {
		const { name } = params;

		if (!name) {
			return json({ error: 'Genome name required' }, { status: 400 });
		}

		// Try enabled path first, then disabled
		const enabledPath = `${GENOMES_DIR}/${name}.md`;
		const disabledPath = `${GENOMES_DIR}/${name}.md.disabled`;

		let filePath: string | null = null;
		if (existsSync(enabledPath)) {
			filePath = enabledPath;
		} else if (existsSync(disabledPath)) {
			filePath = disabledPath;
		}

		if (!filePath) {
			return json({ error: 'Genome not found' }, { status: 404 });
		}

		const content = await readFile(filePath, 'utf-8');

		return json({
			name,
			content,
			enabled: filePath === enabledPath
		});
	} catch (e) {
		console.error('Failed to read genome:', e);
		return json({ error: 'Failed to read genome' }, { status: 500 });
	}
};
