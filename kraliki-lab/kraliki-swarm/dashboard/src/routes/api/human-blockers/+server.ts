import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { readFile, readdir, writeFile } from 'fs/promises';
import { join } from 'path';
import { getScopePath, getSubpath } from '$lib/server/scopes';

interface HumanBlocker {
	id: string;
	task: string;
	priority: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
	time: string;
	notes: string;
	file?: string;
}

function parsePriority(section: string): 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW' {
	if (section.includes('CRITICAL')) return 'CRITICAL';
	if (section.includes('HIGH')) return 'HIGH';
	if (section.includes('MEDIUM')) return 'MEDIUM';
	return 'LOW';
}

function parseQueueStatus(content: string): HumanBlocker[] {
	const blockers: HumanBlocker[] = [];
	const lines = content.split('\n');

	let currentPriority: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW' = 'MEDIUM';
	let inTable = false;
	let inCompleted = false;

	for (const line of lines) {
		// Skip completed/archive section
		if (line.includes('Recently Completed') || line.includes('Archive')) {
			inCompleted = true;
			inTable = false;
			continue;
		}

		// Detect priority section (handles both "## CRITICAL" and "### CRITICAL" formats)
		if (line.match(/^#{2,3}\s+CRITICAL/i)) {
			currentPriority = 'CRITICAL';
			inTable = false;
			inCompleted = false;
		} else if (line.match(/^#{2,3}\s+HIGH/i)) {
			currentPriority = 'HIGH';
			inTable = false;
			inCompleted = false;
		} else if (line.match(/^#{2,3}\s+MEDIUM/i)) {
			currentPriority = 'MEDIUM';
			inTable = false;
			inCompleted = false;
		} else if (line.match(/^#{2,3}\s+LOW/i) || line.includes('Can Wait') || line.includes('Verification')) {
			currentPriority = 'LOW';
			inTable = false;
			inCompleted = false;
		}

		// Skip table header and separator
		if (line.startsWith('| ID') || line.startsWith('|----')) {
			inTable = true;
			continue;
		}

		// Parse table rows (skip completed section)
		if (!inCompleted && inTable && line.startsWith('|') && line.includes('HW-')) {
			const parts = line.split('|').map(p => p.trim()).filter(Boolean);
			// Format: | ID | Task | Priority | Est. Time | Notes |
			if (parts.length >= 2) {
				const id = parts[0].replace(/\*\*/g, '').trim();
				const task = parts[1].trim();
				// Check if priority is in column 3 (new format) or use section priority
				let priority = currentPriority;
				if (parts[2] && ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'].includes(parts[2].toUpperCase())) {
					priority = parts[2].toUpperCase() as 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
				}
				const time = parts[3] || parts[2] || '';
				const notes = parts[4] || parts[3] || '';

				blockers.push({
					id,
					task,
					priority,
					time,
					notes
				});
			}
		}
	}

	return blockers;
}

export const GET: RequestHandler = async () => {
	try {
		// Get blockers scope path
		const blockersPath = await getScopePath('blockers');
		if (!blockersPath) {
			return json({ error: 'Blockers scope not configured', blockers: [], total: 0, critical: 0, high: 0 });
		}

		const queueFile = join(blockersPath, 'QUEUE_STATUS.md');
		const content = await readFile(queueFile, 'utf-8');
		const blockers = parseQueueStatus(content);

		// Sort by priority
		const priorityOrder = { CRITICAL: 0, HIGH: 1, MEDIUM: 2, LOW: 3 };
		blockers.sort((a, b) => priorityOrder[a.priority] - priorityOrder[b.priority]);

		return json({
			blockers,
			total: blockers.length,
			critical: blockers.filter(b => b.priority === 'CRITICAL').length,
			high: blockers.filter(b => b.priority === 'HIGH').length,
			lastUpdated: new Date().toISOString()
		});
	} catch (e) {
		console.error('Failed to read human blockers:', e);
		return json({
			blockers: [],
			total: 0,
			critical: 0,
			high: 0,
			error: 'Failed to read queue status'
		});
	}
};

export const POST: RequestHandler = async ({ request }) => {
	try {
		const { action, id } = await request.json();

		// Get blockers scope path
		const blockersPath = await getScopePath('blockers');
		if (!blockersPath) {
			return json({ error: 'Blockers scope not configured' }, { status: 500 });
		}
		const queueFile = join(blockersPath, 'QUEUE_STATUS.md');

		if (action === 'mark_done') {
			// Read current queue
			let content = await readFile(queueFile, 'utf-8');

			// Find and remove the line with this ID
			const lines = content.split('\n');
			const newLines = lines.filter(line => !line.includes(id));

			// Add to recently resolved
			const resolvedSection = lines.findIndex(l => l.includes('## RECENTLY RESOLVED'));
			if (resolvedSection !== -1) {
				// Find the table in resolved section
				let insertAt = resolvedSection + 4; // After header row and separator
				newLines.splice(insertAt, 0, `| ${id} | Marked done via dashboard | Human | ${new Date().toISOString().split('T')[0]} |`);
			}

			await writeFile(queueFile, newLines.join('\n'));

			return json({ success: true, message: `${id} marked as done` });
		}

		return json({ error: 'Unknown action' }, { status: 400 });
	} catch (e) {
		console.error('Failed to update human blockers:', e);
		return json({ error: 'Failed to update' }, { status: 500 });
	}
};
