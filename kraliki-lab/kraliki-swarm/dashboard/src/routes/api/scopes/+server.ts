import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { readFile, writeFile, stat } from 'fs/promises';
import { join } from 'path';
import { loadScopes, clearScopesCache, type ScopesConfig } from '$lib/server/scopes';

const WORKSPACE_DIR = process.env.KRALIKI_WORKSPACE || '/home/adminmatej/github/applications/kraliki-lab/kraliki-swarm/workspace';
const SCOPES_FILE = join(WORKSPACE_DIR, 'scopes.json');

interface ScopeStatus {
	name: string;
	path: string;
	description?: string;
	exists: boolean;
	accessible: boolean;
	subpaths?: Record<string, { path: string; exists: boolean }>;
}

async function checkPathExists(path: string): Promise<boolean> {
	try {
		await stat(path);
		return true;
	} catch {
		return false;
	}
}

export const GET: RequestHandler = async () => {
	try {
		const scopes = await loadScopes();

		// Check each scope's status
		const scopeStatuses: ScopeStatus[] = [];

		for (const [name, config] of Object.entries(scopes.scopes)) {
			const exists = await checkPathExists(config.path);
			const status: ScopeStatus = {
				name,
				path: config.path,
				description: config.description,
				exists,
				accessible: exists
			};

			// Check subpaths if they exist
			if (config.subpaths) {
				status.subpaths = {};
				for (const [subName, subPath] of Object.entries(config.subpaths)) {
					const fullPath = join(config.path, subPath);
					status.subpaths[subName] = {
						path: fullPath,
						exists: await checkPathExists(fullPath)
					};
				}
			}

			scopeStatuses.push(status);
		}

		return json({
			config: scopes,
			statuses: scopeStatuses,
			workspaceDir: WORKSPACE_DIR,
			lastChecked: new Date().toISOString()
		});
	} catch (e) {
		console.error('Failed to load scopes:', e);
		return json({
			error: 'Failed to load scopes configuration',
			details: e instanceof Error ? e.message : 'Unknown error'
		}, { status: 500 });
	}
};

	export const PUT: RequestHandler = async ({ request }) => {
		try {
			const updates = await request.json();

			// Load current config
			const currentContent = await readFile(SCOPES_FILE, 'utf-8');
			const current: ScopesConfig = JSON.parse(currentContent);

			// Merge updates
			if (updates.scopes) {
				for (const [name, config] of Object.entries(updates.scopes)) {
					if (config === null) {
						// Delete scope
						delete current.scopes[name];
					} else {
						// Update or add scope
						current.scopes[name] = config as any;
					}
				}
			}

			if (updates.name) current.name = updates.name;
			if (updates.description) current.description = updates.description;
			if (updates.version) current.version = updates.version;
			if (updates.storage) {
				if (updates.storage.type) current.storage.type = updates.storage.type;
				if (updates.storage.base) current.storage.base = updates.storage.base;
			}

			current.lastModified = new Date().toISOString().split('T')[0];

			// Write back
			await writeFile(SCOPES_FILE, JSON.stringify(current, null, 2));

			// Clear cache so next read gets fresh data
			clearScopesCache();

			return json({
				success: true,
				message: 'Scopes configuration updated',
				config: current
			});
		} catch (e) {
			console.error('Failed to update scopes:', e);
			return json({
				error: 'Failed to update scopes configuration',
				details: e instanceof Error ? e.message : 'Unknown error'
			}, { status: 500 });
		}
	};
