import { mkdir, readFile, writeFile, access } from 'fs/promises';
import { constants } from 'fs';
import { join } from 'path';
import { randomUUID } from 'crypto';
import type { Cookies } from '@sveltejs/kit';

export interface FocusProject {
	id: string;
	name: string;
	description?: string;
	status: 'active' | 'archived' | 'completed';
	task_count?: number;
	completed_count?: number;
	created_at?: string;
}

export interface FocusTask {
	id: string;
	title: string;
	description?: string;
	status: 'todo' | 'in_progress' | 'done' | 'archived';
	priority: 'low' | 'medium' | 'high' | 'urgent';
	project_id?: string;
	linear_id?: string;
	linear_url?: string;
	created_at?: string;
	due_date?: string;
}

export interface FocusCapture {
	id: string;
	title: string;
	source: 'text' | 'file' | 'voice';
	created_at: string;
}

export interface FocusStore {
	projects: FocusProject[];
	tasks: FocusTask[];
	captures: FocusCapture[];
	updated_at: string;
}

export interface FocusUser {
	id: string;
	email: string;
	name: string;
}

const DEFAULT_STORE: FocusStore = {
	projects: [],
	tasks: [],
	captures: [],
	updated_at: new Date().toISOString()
};

const ROOT_CANDIDATES = [
	process.env.KRALIKI_DIR,
	process.cwd(),
	join(process.cwd(), '..')
].filter((value): value is string => Boolean(value));

const APP_ROOT = process.env.KRALIKI_DIR
	? join(process.env.KRALIKI_DIR, '..')
	: join(process.cwd(), '..');

const DATA_DIR_CANDIDATES = [
	...ROOT_CANDIDATES.flatMap((root) => [
		join(root, 'data', 'focus'),
		join(root, 'data', 'focus-kraliki')
	]),
	// Monorepo layouts for Focus by Kraliki and Swarm data.
	join(APP_ROOT, 'focus-kraliki', 'data'),
	join(APP_ROOT, 'kraliki-swarm', 'data', 'focus')
];

let dataDirCache: string | null = null;

async function resolveDataDir(): Promise<string> {
	if (dataDirCache) return dataDirCache;

	for (const candidate of DATA_DIR_CANDIDATES) {
		try {
			await access(candidate, constants.F_OK);
			dataDirCache = candidate;
			return candidate;
		} catch {
			// Try next candidate.
		}
	}

	dataDirCache = DATA_DIR_CANDIDATES[0];
	await mkdir(dataDirCache, { recursive: true });
	return dataDirCache;
}

function safeUserId(userId: string) {
	return userId.replace(/[^a-zA-Z0-9_-]/g, '_');
}

export function getFocusUser(cookies: Cookies): FocusUser {
	const sessionToken = cookies.get('session');
	if (!sessionToken) {
		return {
			id: 'local-agent',
			email: 'agent@kraliki.local',
			name: 'Local Agent'
		};
	}

	try {
		const userData = JSON.parse(atob(sessionToken));
		return {
			id: userData.sub || 'unknown',
			email: userData.email || `${userData.sub}@kraliki.local`,
			name: userData.name || 'Kraliki User'
		};
	} catch {
		return {
			id: 'local-agent',
			email: 'agent@kraliki.local',
			name: 'Local Agent'
		};
	}
}

export function createFocusId(): string {
	return randomUUID();
}

export async function loadFocusStore(userId: string): Promise<FocusStore> {
	const dataDir = await resolveDataDir();
	const filePath = join(dataDir, `${safeUserId(userId)}.json`);

	try {
		const raw = await readFile(filePath, 'utf-8');
		const parsed = JSON.parse(raw) as FocusStore;
		return {
			...DEFAULT_STORE,
			...parsed,
			projects: parsed.projects || [],
			tasks: parsed.tasks || [],
			captures: parsed.captures || [],
			updated_at: parsed.updated_at || new Date().toISOString()
		};
	} catch {
		return { ...DEFAULT_STORE };
	}
}

export async function saveFocusStore(userId: string, store: FocusStore): Promise<void> {
	const dataDir = await resolveDataDir();
	await mkdir(dataDir, { recursive: true });

	const filePath = join(dataDir, `${safeUserId(userId)}.json`);
	const payload = {
		...store,
		updated_at: new Date().toISOString()
	};
	await writeFile(filePath, JSON.stringify(payload, null, 2), 'utf-8');
}

export function withProjectStats(
	projects: FocusProject[],
	tasks: FocusTask[]
): FocusProject[] {
	const stats = new Map<string, { total: number; completed: number }>();

	for (const task of tasks) {
		if (!task.project_id) continue;
		const current = stats.get(task.project_id) || { total: 0, completed: 0 };
		current.total += 1;
		if (task.status === 'done') current.completed += 1;
		stats.set(task.project_id, current);
	}

	return projects.map(project => {
		const projectStats = stats.get(project.id);
		return {
			...project,
			task_count: projectStats?.total ?? project.task_count ?? 0,
			completed_count: projectStats?.completed ?? project.completed_count ?? 0
		};
	});
}
