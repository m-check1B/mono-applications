import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { readdir, readFile, rename, stat } from 'fs/promises';
import { existsSync } from 'fs';
import path from 'path';

const KRALIKI_BASE = process.env.KRALIKI_DIR || '/home/adminmatej/github/applications/kraliki-lab/kraliki-swarm';
const GITHUB_DIR = process.env.GITHUB_DIR || path.resolve(KRALIKI_BASE, '../../../..');
const GENOMES_DIR = process.env.GENOMES_PATH || `${KRALIKI_BASE}/genomes`;
const GENOME_PACKS_PATH =
	process.env.GENOME_PACKS_PATH || path.join(GITHUB_DIR, 'products-portfolio', 'GENOME_PACKS.json');
const TRACES_FILE = `${KRALIKI_BASE}/arena/data/decision_traces.json`;
const LEADERBOARD_FILE = `${KRALIKI_BASE}/arena/data/leaderboard.json`;

interface GenomeEntry {
	name: string;
	cli: string;
	enabled: boolean;
	spawns_today: number;
	points_earned: number;
	decisions: number;
	last_active: string | null;
}

interface GenomeData {
	genomes: GenomeEntry[];
	by_cli: Record<string, { genomes: number; spawns: number; points: number }>;
	total_genomes: number;
	active_today: number;
	template_packs?: TemplatePackData[];
}

interface TemplatePackConfig {
	description?: string;
	active_roles: string[];
}

interface TemplatePackData {
	template: string;
	description?: string;
	active_roles: string[];
	muted_roles: string[];
	active_genome_count: number;
	muted_genome_count: number;
	missing_roles: string[];
}

function detectCli(name: string): string {
	if (name.startsWith('claude_')) return 'claude';
	if (name.startsWith('codex_')) return 'codex';
	if (name.startsWith('gemini_')) return 'gemini';
	if (name.startsWith('opencode_')) return 'opencode';
	return 'unknown';
}

function extractRole(name: string): string {
	const prefixes = ['claude_', 'codex_', 'gemini_', 'opencode_', 'grok_'];
	for (const prefix of prefixes) {
		if (name.startsWith(prefix)) {
			return name.slice(prefix.length);
		}
	}
	return name;
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

async function readTemplatePacks(): Promise<Record<string, TemplatePackConfig>> {
	const data = await readJsonFile<{ templates?: Record<string, TemplatePackConfig> } | null>(
		GENOME_PACKS_PATH,
		null
	);
	if (!data) return {};
	if (data.templates) return data.templates;
	return data as Record<string, TemplatePackConfig>;
}

export const GET: RequestHandler = async () => {
	try {
		if (!existsSync(GENOMES_DIR)) {
			return json({ genomes: [], by_cli: {}, total_genomes: 0, active_today: 0 });
		}

		const entries = await readdir(GENOMES_DIR);
		const today = new Date().toISOString().slice(0, 10);

		// Load traces for activity data
		const tracesData = await readJsonFile<{ traces: any[] } | null>(TRACES_FILE, null);
		const traces = tracesData?.traces || [];

		// Load leaderboard for points
		const leaderboard = await readJsonFile<{ rankings: any[] } | null>(LEADERBOARD_FILE, null);
		const rankings = leaderboard?.rankings || [];

		// Build genome stats
		const genomeStats: Record<string, { spawns_today: number; points_earned: number; decisions: number; last_active: string | null }> = {};

		// Initialize from genome files
		const genomeNames: string[] = [];
		for (const entry of entries) {
			if (entry.endsWith('.md') || entry.endsWith('.md.disabled')) {
				const name = entry.replace('.md.disabled', '').replace('.md', '');
				genomeNames.push(name);
				genomeStats[name] = { spawns_today: 0, points_earned: 0, decisions: 0, last_active: null };
			}
		}

		// Count from traces
		for (const trace of traces) {
			const genome = trace.genome;
			if (!genome) continue;

			if (!genomeStats[genome]) {
				genomeStats[genome] = { spawns_today: 0, points_earned: 0, decisions: 0, last_active: null };
			}

			genomeStats[genome].decisions++;

			if (trace.decision_type === 'spawn' && trace.timestamp?.startsWith(today)) {
				genomeStats[genome].spawns_today++;
			}

			const timestamp = trace.timestamp;
			if (timestamp && (!genomeStats[genome].last_active || timestamp > genomeStats[genome].last_active)) {
				genomeStats[genome].last_active = timestamp;
			}
		}

		// Add points from leaderboard
		for (const agent of rankings) {
			const agentId = agent.id || '';
			const parts = agentId.split('-');
			if (parts.length >= 2) {
				const lab = parts[0];
				const role = parts[1];
				const cliMap: Record<string, string> = { CC: 'claude', OC: 'opencode', CX: 'codex', GE: 'gemini', GR: 'grok' };
				const cli = cliMap[lab] || lab.toLowerCase();
				const genomeName = `${cli}_${role}`;

				if (genomeStats[genomeName]) {
					genomeStats[genomeName].points_earned += agent.points || 0;
				}
			}
		}

		// Build response
		const genomes: GenomeEntry[] = [];
		for (const entry of entries) {
			if (entry.endsWith('.md') || entry.endsWith('.md.disabled')) {
				const isDisabled = entry.endsWith('.disabled');
				const name = entry.replace('.md.disabled', '').replace('.md', '');
				const stats = genomeStats[name] || { spawns_today: 0, points_earned: 0, decisions: 0, last_active: null };
				genomes.push({
					name,
					cli: detectCli(name),
					enabled: !isDisabled,
					spawns_today: stats.spawns_today,
					points_earned: stats.points_earned,
					decisions: stats.decisions,
					last_active: stats.last_active
				});
			}
		}

		// Sort by spawns then points (most active first)
		genomes.sort((a, b) => {
			const scoreA = a.spawns_today * 10 + a.points_earned;
			const scoreB = b.spawns_today * 10 + b.points_earned;
			if (scoreA !== scoreB) return scoreB - scoreA;
			return a.name.localeCompare(b.name);
		});

		// Aggregate by CLI
		const by_cli: Record<string, { genomes: number; spawns: number; points: number }> = {};
		for (const genome of genomes) {
			if (!by_cli[genome.cli]) {
				by_cli[genome.cli] = { genomes: 0, spawns: 0, points: 0 };
			}
			by_cli[genome.cli].genomes++;
			by_cli[genome.cli].spawns += genome.spawns_today;
			by_cli[genome.cli].points += genome.points_earned;
		}

		const active_today = genomes.filter(g => g.spawns_today > 0 || g.last_active?.startsWith(today)).length;

		// Template packs (role-based) -> derive active/muted from available roles
		const templatePacksConfig = await readTemplatePacks();
		const roleIndex: Record<string, string[]> = {};
		for (const genome of genomes) {
			const role = extractRole(genome.name);
			roleIndex[role] = roleIndex[role] || [];
			roleIndex[role].push(genome.name);
		}

		const availableRoles = Object.keys(roleIndex).sort();
		const template_packs: TemplatePackData[] = Object.entries(templatePacksConfig).map(
			([template, pack]) => {
				const active_roles = Array.from(
					new Set((pack.active_roles || []).map(role => role.trim()).filter(Boolean))
				).sort();
				const missing_roles = active_roles.filter(role => !roleIndex[role]);
				const muted_roles = availableRoles.filter(role => !active_roles.includes(role));
				const active_genome_count = active_roles.reduce(
					(total, role) => total + (roleIndex[role]?.length || 0),
					0
				);
				const muted_genome_count = muted_roles.reduce(
					(total, role) => total + (roleIndex[role]?.length || 0),
					0
				);

				return {
					template,
					description: pack.description,
					active_roles,
					muted_roles,
					active_genome_count,
					muted_genome_count,
					missing_roles
				};
			}
		);

		return json({
			genomes,
			by_cli,
			total_genomes: genomes.length,
			active_today,
			template_packs
		} satisfies GenomeData);
	} catch (e) {
		console.error('Failed to list genomes:', e);
		return json({ genomes: [], by_cli: {}, total_genomes: 0, active_today: 0 });
	}
};

export const POST: RequestHandler = async ({ request }) => {
	try {
		const { name, enabled } = await request.json();

		if (!name || typeof enabled !== 'boolean') {
			return json({ error: 'Invalid request' }, { status: 400 });
		}

		const enabledPath = `${GENOMES_DIR}/${name}.md`;
		const disabledPath = `${GENOMES_DIR}/${name}.md.disabled`;

		if (enabled) {
			// Enable: rename .md.disabled to .md
			if (existsSync(disabledPath)) {
				await rename(disabledPath, enabledPath);
			}
		} else {
			// Disable: rename .md to .md.disabled
			if (existsSync(enabledPath)) {
				await rename(enabledPath, disabledPath);
			}
		}

		// Return updated list
		const entries = await readdir(GENOMES_DIR);
		const genomes: Array<{ name: string; cli: string; enabled: boolean }> = [];

		for (const entry of entries) {
			if (entry.endsWith('.md') || entry.endsWith('.md.disabled')) {
				const isDisabled = entry.endsWith('.disabled');
				const genomeName = entry.replace('.md.disabled', '').replace('.md', '');
				genomes.push({
					name: genomeName,
					cli: detectCli(genomeName),
					enabled: !isDisabled
				});
			}
		}

		genomes.sort((a, b) => {
			if (a.cli !== b.cli) return a.cli.localeCompare(b.cli);
			return a.name.localeCompare(b.name);
		});

		return json(genomes);
	} catch (e) {
		console.error('Failed to toggle genome:', e);
		return json({ error: 'Failed to toggle genome' }, { status: 500 });
	}
};
