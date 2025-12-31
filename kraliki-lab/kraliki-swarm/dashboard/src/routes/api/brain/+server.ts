import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { readFile } from 'fs/promises';
import { join } from 'path';
import { getScopePath, getSubpath } from '$lib/server/scopes';

interface StreamConfig {
	path: string;
	plans: string[];
	attention: string;
	status: string;
	note?: string;
	can_parallel: boolean;
}

interface MasterPlan {
	version: string;
	created: string;
	period: string;
	period_dates: string;
	strategic_focus: string;
	streams: Record<string, StreamConfig>;
	parallelism: {
		enabled: boolean;
		max_concurrent_streams: number;
		note: string;
	};
	review: {
		human_review_required: boolean;
		auto_execute: boolean;
		status: string;
	};
}

async function loadPlanFile(planningDir: string, filename: string): Promise<any | null> {
	try {
		const content = await readFile(join(planningDir, filename), 'utf-8');
		return JSON.parse(content);
	} catch {
		return null;
	}
}

export const GET: RequestHandler = async () => {
	try {
		// Get brain scope path
		const brainPath = await getScopePath('brain');
		if (!brainPath) {
			return json({ error: 'Brain scope not configured' }, { status: 500 });
		}

		const planningDir = join(brainPath, 'ai-planning');

		// Load master plan
		const masterContent = await readFile(join(planningDir, 'master.json'), 'utf-8');
		const master: MasterPlan = JSON.parse(masterContent);

		// Load individual stream plans
		const streamDetails: Record<string, any[]> = {};

		for (const [streamName, streamConfig] of Object.entries(master.streams)) {
			streamDetails[streamName] = [];
			for (const planFile of streamConfig.plans) {
				const planPath = join(streamConfig.path, planFile);
				const plan = await loadPlanFile(planningDir, planPath);
				if (plan) {
					streamDetails[streamName].push({
						file: planFile,
						...plan
					});
				}
			}
		}

		// Calculate ME-90 progress
		const [startStr, endStr] = master.period_dates.split(' to ');
		const me90Start = new Date(startStr);
		const me90End = new Date(endStr);
		const today = new Date();
		const totalDays = Math.ceil((me90End.getTime() - me90Start.getTime()) / (1000 * 60 * 60 * 24));
		const daysPassed = Math.ceil((today.getTime() - me90Start.getTime()) / (1000 * 60 * 60 * 24));
		const daysRemaining = totalDays - daysPassed;
		const progress = Math.min(100, Math.max(0, (daysPassed / totalDays) * 100));

		return json({
			master,
			streamDetails,
			me90: {
				start: startStr,
				end: endStr,
				totalDays,
				daysPassed,
				daysRemaining,
				progress: progress.toFixed(1)
			},
			lastUpdated: new Date().toISOString()
		});
	} catch (e) {
		console.error('Failed to load brain data:', e);
		return json({
			error: 'Failed to load brain data',
			details: e instanceof Error ? e.message : 'Unknown error'
		}, { status: 500 });
	}
};
