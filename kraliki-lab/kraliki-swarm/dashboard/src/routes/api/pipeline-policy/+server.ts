import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { readFile, writeFile } from 'fs/promises';
import { existsSync } from 'fs';

const POLICY_FILE =
	'/home/adminmatej/github/applications/kraliki-lab/kraliki-swarm/config/pipeline_policy.json';
const TAXONOMY_FILE =
	'/home/adminmatej/github/applications/kraliki-lab/kraliki-swarm/config/pipeline_taxonomy.json';
const LINEAR_FILE =
	'/home/adminmatej/github/applications/kraliki-lab/kraliki-swarm/data/linear.json';
const RUNNING_AGENTS_FILE =
	'/home/adminmatej/github/applications/kraliki-lab/kraliki-swarm/control/running_agents.json';

interface PipelineConfig {
	enabled: boolean;
	reason?: string;
}

interface PipelinePolicy {
	_description?: string;
	_updated?: string;
	pipelines: Record<string, PipelineConfig>;
}

interface PipelineTaxonomyEntry {
	roles?: string[];
	labels?: string[];
}

interface PipelineTaxonomy {
	_description?: string;
	always_allowed_roles?: string[];
	order?: string[];
	pipelines?: Record<string, PipelineTaxonomyEntry>;
}

interface LinearIssueEntry {
	labels?: string[];
}

interface RunningAgentsData {
	agents?: Record<string, { genome?: string }>;
}

const DEFAULT_POLICY: PipelinePolicy = {
	pipelines: {
		dev: { enabled: true, reason: 'Default' },
		biz: { enabled: true, reason: 'Default' },
		self_improve: { enabled: true, reason: 'Default' }
	}
};

const DEFAULT_TAXONOMY: PipelineTaxonomy = {
	always_allowed_roles: ['orchestrator', 'caretaker'],
	order: ['biz', 'dev', 'self_improve'],
	pipelines: {
		dev: {
			roles: ['builder', 'patcher', 'tester', 'integrator', 'explorer', 'dev_discovery', 'reviewer', 'promoter', 'rnd'],
			labels: ['stream:asset-engine', 'stream:apps']
		},
		biz: {
			roles: ['business', 'biz_discovery', 'marketer', 'researcher', 'researcher_external'],
			labels: ['stream:cash-engine']
		},
		self_improve: {
			roles: ['self_improver'],
			labels: []
		}
	}
};

async function loadPolicy(): Promise<PipelinePolicy> {
	try {
		if (existsSync(POLICY_FILE)) {
			const content = await readFile(POLICY_FILE, 'utf-8');
			return JSON.parse(content);
		}
	} catch (e) {
		console.error('Failed to load pipeline policy:', e);
	}
	return DEFAULT_POLICY;
}

async function loadTaxonomy(): Promise<PipelineTaxonomy> {
	try {
		if (existsSync(TAXONOMY_FILE)) {
			const content = await readFile(TAXONOMY_FILE, 'utf-8');
			return JSON.parse(content);
		}
	} catch (e) {
		console.error('Failed to load pipeline taxonomy:', e);
	}
	return DEFAULT_TAXONOMY;
}

async function savePolicy(policy: PipelinePolicy): Promise<void> {
	policy._updated = new Date().toISOString().split('T')[0];
	await writeFile(POLICY_FILE, JSON.stringify(policy, null, 2));
}

async function readJsonFile<T>(path: string, fallback: T): Promise<T> {
	try {
		if (!existsSync(path)) return fallback;
		const content = await readFile(path, 'utf-8');
		return JSON.parse(content);
	} catch {
		return fallback;
	}
}

function extractRole(genome: string): string {
	let role = genome;
	for (const prefix of ['claude_', 'opencode_', 'gemini_', 'codex_', 'grok_']) {
		if (role.startsWith(prefix)) {
			role = role.slice(prefix.length);
			break;
		}
	}
	return role;
}

function pipelineForRole(role: string, taxonomy: PipelineTaxonomy): string | null {
	const alwaysAllowed = new Set(taxonomy.always_allowed_roles || []);
	if (alwaysAllowed.has(role)) {
		return null;
	}

	const pipelines = taxonomy.pipelines || {};
	for (const [name, config] of Object.entries(pipelines)) {
		if ((config.roles || []).includes(role)) {
			return name;
		}
	}

	return 'dev';
}

async function detectIntendedPipelines(taxonomy: PipelineTaxonomy): Promise<Record<string, { signals: string[] }>> {
	const intended: Record<string, { signals: string[] }> = {};

	const linearData = await readJsonFile<{ issues?: LinearIssueEntry[] } | null>(LINEAR_FILE, null);
	const issues = linearData?.issues || [];
	const pipelines = taxonomy.pipelines || {};

	const pipelineLabels = Object.entries(pipelines).reduce((acc, [name, config]) => {
		acc[name] = new Set((config.labels || []).map((label) => label.trim()).filter(Boolean));
		return acc;
	}, {} as Record<string, Set<string>>);

	for (const issue of issues) {
		const labels = issue.labels || [];
		for (const [pipeline, labelSet] of Object.entries(pipelineLabels)) {
			if (labels.some((label) => labelSet.has(label))) {
				if (!intended[pipeline]) intended[pipeline] = { signals: [] };
				if (!intended[pipeline].signals.includes('linear')) {
					intended[pipeline].signals.push('linear');
				}
			}
		}
	}

	const runningAgents = await readJsonFile<RunningAgentsData | null>(RUNNING_AGENTS_FILE, null);
	const agents = runningAgents?.agents || {};
	for (const agent of Object.values(agents)) {
		const genome = agent.genome || '';
		if (!genome) continue;
		const pipeline = pipelineForRole(extractRole(genome), taxonomy);
		if (!pipeline) continue;
		if (!intended[pipeline]) intended[pipeline] = { signals: [] };
		if (!intended[pipeline].signals.includes('agents')) {
			intended[pipeline].signals.push('agents');
		}
	}

	return intended;
}

function getPipelineOrder(taxonomy: PipelineTaxonomy): string[] {
	const order = taxonomy?.order;
	if (Array.isArray(order) && order.length > 0) {
		return order;
	}
	return ['biz', 'dev', 'self_improve'];
}

function sortPipelines(
	names: string[],
	order: string[],
	intended: Record<string, { signals: string[] }>
): string[] {
	return [...names].sort((a, b) => {
		const aIntended = intended[a] ? 1 : 0;
		const bIntended = intended[b] ? 1 : 0;
		if (aIntended !== bIntended) return bIntended - aIntended;
		const aIndex = order.indexOf(a);
		const bIndex = order.indexOf(b);
		const aRank = aIndex === -1 ? 999 : aIndex;
		const bRank = bIndex === -1 ? 999 : bIndex;
		if (aRank !== bRank) return aRank - bRank;
		return a.localeCompare(b);
	});
}

export const GET: RequestHandler = async () => {
	const policy = await loadPolicy();
	const taxonomy = await loadTaxonomy();
	const intended = await detectIntendedPipelines(taxonomy);

	const pipelineNames = new Set<string>();
	Object.keys(policy.pipelines || {}).forEach((name) => pipelineNames.add(name));
	Object.keys(taxonomy.pipelines || {}).forEach((name) => pipelineNames.add(name));
	Object.keys(intended || {}).forEach((name) => pipelineNames.add(name));

	const pipelines = sortPipelines(Array.from(pipelineNames), getPipelineOrder(taxonomy), intended).map((name) => {
		const config = policy.pipelines[name] || { enabled: true };
		const intent = intended[name];
		return {
			name,
			enabled: config.enabled ?? true,
			reason: config.reason || 'Default',
			intended: Boolean(intent),
			signals: intent?.signals || []
		};
	});

	return json({
		pipelines,
		updated: policy._updated
	});
};

export const POST: RequestHandler = async ({ request }) => {
	try {
		const { pipeline, enabled, reason } = await request.json();

		if (!pipeline || typeof enabled !== 'boolean') {
			return json({ error: 'Invalid request - need pipeline and enabled' }, { status: 400 });
		}

		const policy = await loadPolicy();
		if (!policy.pipelines[pipeline]) {
			policy.pipelines[pipeline] = { enabled, reason: reason || 'Toggled via dashboard' };
		} else {
			policy.pipelines[pipeline].enabled = enabled;
			if (reason) {
				policy.pipelines[pipeline].reason = reason;
			}
		}

		await savePolicy(policy);

		const taxonomy = await loadTaxonomy();
		const intended = await detectIntendedPipelines(taxonomy);
		const pipelineNames = new Set<string>();
		Object.keys(policy.pipelines || {}).forEach((name) => pipelineNames.add(name));
		Object.keys(taxonomy.pipelines || {}).forEach((name) => pipelineNames.add(name));
		Object.keys(intended || {}).forEach((name) => pipelineNames.add(name));

		const pipelines = sortPipelines(Array.from(pipelineNames), getPipelineOrder(taxonomy), intended).map((name) => {
			const config = policy.pipelines[name] || { enabled: true };
			const intent = intended[name];
			return {
				name,
				enabled: config.enabled ?? true,
				reason: config.reason || 'Default',
				intended: Boolean(intent),
				signals: intent?.signals || []
			};
		});

		return json({
			success: true,
			pipelines,
			updated: policy._updated
		});
	} catch (e) {
		console.error('Failed to update pipeline policy:', e);
		return json({ error: 'Failed to update pipeline policy' }, { status: 500 });
	}
};
