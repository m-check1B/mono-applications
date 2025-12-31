import { exec } from 'child_process';
import { promisify } from 'util';
import { readFile, readdir, open, stat } from 'fs/promises';
import { existsSync } from 'fs';

const execAsync = promisify(exec);

// Base path: Use KRALIKI_DIR or KRALIKI_DATA_PATH env var, or default for host
const KRALIKI_BASE = process.env.KRALIKI_DIR || process.env.KRALIKI_DATA_PATH || '/home/adminmatej/github/applications/kraliki-lab/kraliki-swarm';
const GITHUB_BASE = process.env.GITHUB_PATH || '/home/adminmatej/github';
const AGENT_LOGS_DIR = `${KRALIKI_BASE}/logs/agents`;

const PATHS = {
	kralikiStats: `${KRALIKI_BASE}/logs/daily/latest.json`,
	linear: `${KRALIKI_BASE}/data/linear.json`,
	pendingLinear: `${KRALIKI_BASE}/data/pending_linear_issues.json`,
	leaderboard: `${KRALIKI_BASE}/arena/data/leaderboard.json`,
	socialFeed: `${KRALIKI_BASE}/arena/data/social_feed.json`,
	blackboard: `${KRALIKI_BASE}/arena/data/board.json`,
	tasks: `${KRALIKI_BASE}/tasks/queue.json`,
	recall: `http://127.0.0.1:3020/api/stats`,
	circuitBreakers: `${KRALIKI_BASE}/control/circuit-breakers.json`,
	fitness: `${KRALIKI_BASE}/data/fitness/agents.json`
};


async function readJsonFile<T>(path: string, fallback: T): Promise<T> {
	try {
		if (!existsSync(path)) return fallback;
		const content = await readFile(path, 'utf-8');
		return JSON.parse(content);
	} catch {
		return fallback;
	}
}



export interface HeatMapEntry {
	folder: string;
	count: number;
}

export interface RecentFile {
	time: string;
	path: string;
}

export interface AgentStatusEntry {
	id: string;
	genome: string | null;
	cli: string | null;
	status: 'running' | 'completed' | 'failed';
	pid: number | null;
	startTime: string;
	duration: string;
	points: number | null;
}


export interface LinearData {
	stats: {
		total: number;
		human_assigned: number;
		blockers: number;
	};
	issues: Array<{
		id: string;
		identifier: string;
		title: string;
		priority: number;
		priorityLabel: string;
		state: string;
		stateColor: string;
		assignee: string;
		isAssignedToMe: boolean;
		labels: string[];
		url: string;
	}>;
}

export interface PendingLinearIssue {
	title: string;
	description: string;
	priority: number;
	labels: string[];
}

export interface PendingLinearData {
	generated_at: string;
	generated_by: string;
	note: string;
	issues: PendingLinearIssue[];
}

export interface RecallStats {
	total_entries: number;
	total_stores: number;
	total_retrieves: number;
	by_agent: Record<string, { stores: number; retrieves: number }>;
}

export interface MemoryStats {
	total_memories: number;
	total_agents: number;
	ephemeral_files: number;
	oldest_memory: string | null;
	newest_memory: string | null;
	total_size_kb: number;
	top_agents: Array<{
		agent: string;
		count: number;
		size_kb: number;
		last_active: string;
		ephemeral: boolean;
	}>;
	mgrep_available: boolean;
}

export interface CircuitBreakerEntry {
	state: 'open' | 'closed' | 'half-open';
	failure_count: number;
	last_failure_time: string | null;
	last_success_time: string | null;
	last_update?: string;
	note?: string;
	last_failure_reason?: string;
}

export type CircuitBreakersData = Record<string, CircuitBreakerEntry>;

export interface FitnessReport {
	time: string;
	agent_id: string;
	task_id: string;
	success: boolean;
	tokens_used: number;
	quality_score: number;
}

export interface FitnessData {
	agents: Record<string, any>;
	reports: FitnessReport[];
	last_updated: string;
}

export async function getFitnessData(): Promise<FitnessData | null> {
	return await readJsonFile<FitnessData | null>(PATHS.fitness, null);
}

// Decision Trace types and functions
export interface DecisionTraceEntry {
	trace_id: string;
	timestamp: string;
	agent_id: string;
	decision_type: string;
	decision: string;
	reasoning: string;
	outcome?: string;
	linear_issue?: string;
}

export interface DecisionTraceStats {
	total_traces: number;
	traces_today: number;
	by_type: Record<string, number>;
	by_outcome: Record<string, number>;
	recent_traces: DecisionTraceEntry[];
}

// Genome Stats types and functions
export interface GenomeStat {
	name: string;
	cli: string;
	spawns_today: number;
	points_earned: number;
	decisions: number;
	last_active: string | null;
}

export interface GenomeStats {
	total_genomes: number;
	active_today: number;
	top_performers: GenomeStat[];
	by_cli: Record<string, { genomes: number; spawns: number; points: number }>;
}

export async function getDecisionTraceStats(): Promise<DecisionTraceStats | null> {
	const ARENA_DIR = `${KRALIKI_BASE}/arena`;
	const TRACES_FILE = `${ARENA_DIR}/data/decision_traces.json`;

	try {
		const data = await readJsonFile<{ traces: any[] } | null>(TRACES_FILE, null);
		if (!data || !data.traces) return null;

		const traces = data.traces;
		const today = new Date().toISOString().slice(0, 10);

		const stats: DecisionTraceStats = {
			total_traces: traces.length,
			traces_today: 0,
			by_type: {},
			by_outcome: {},
			recent_traces: []
		};

		for (const trace of traces) {
			// Count today's traces
			if (trace.timestamp?.startsWith(today)) {
				stats.traces_today++;
			}

			// By type
			const dtype = trace.decision_type || 'unknown';
			stats.by_type[dtype] = (stats.by_type[dtype] || 0) + 1;

			// By outcome
			const outcome = trace.outcome || 'pending';
			stats.by_outcome[outcome] = (stats.by_outcome[outcome] || 0) + 1;
		}

		// Get recent traces (last 5, sorted by timestamp desc)
		const sortedTraces = [...traces]
			.sort((a, b) => (b.timestamp || '').localeCompare(a.timestamp || ''))
			.slice(0, 5);

		stats.recent_traces = sortedTraces.map(t => ({
			trace_id: t.trace_id,
			timestamp: t.timestamp,
			agent_id: t.agent_id,
			decision_type: t.decision_type,
			decision: t.decision,
			reasoning: t.reasoning,
			outcome: t.outcome,
			linear_issue: t.linear_issue
		}));

		return stats;
	} catch {
		return null;
	}
}

export async function getGenomeStats(): Promise<GenomeStats | null> {
	const GENOMES_DIR = `${KRALIKI_BASE}/genomes`;
	const TRACES_FILE = `${KRALIKI_BASE}/arena/data/decision_traces.json`;

	try {
		// Get list of genome files
		const genomeFiles = await readdir(GENOMES_DIR).catch(() => []);
		const genomeNames = genomeFiles
			.filter(f => f.endsWith('.md') && !f.startsWith('_'))
			.map(f => f.replace('.md', ''));

		// Load traces for today's activity
		const tracesData = await readJsonFile<{ traces: any[] } | null>(TRACES_FILE, null);
		const traces = tracesData?.traces || [];
		const today = new Date().toISOString().slice(0, 10);

		// Load leaderboard for points
		const leaderboard = await readJsonFile<{ rankings: any[] } | null>(PATHS.leaderboard, null);
		const rankings = leaderboard?.rankings || [];

		// Aggregate by genome
		const genomeData: Record<string, GenomeStat> = {};

		// Initialize from genome files
		for (const name of genomeNames) {
			const parts = name.split('_');
			const cli = parts[0] || 'unknown';
			genomeData[name] = {
				name,
				cli,
				spawns_today: 0,
				points_earned: 0,
				decisions: 0,
				last_active: null
			};
		}

		// Count spawns and decisions from traces
		for (const trace of traces) {
			const genome = trace.genome;
			if (!genome) continue;

			if (!genomeData[genome]) {
				const parts = genome.split('_');
				genomeData[genome] = {
					name: genome,
					cli: parts[0] || 'unknown',
					spawns_today: 0,
					points_earned: 0,
					decisions: 0,
					last_active: null
				};
			}

			// Count decisions
			genomeData[genome].decisions++;

			// Track today's spawns
			if (trace.decision_type === 'spawn' && trace.timestamp?.startsWith(today)) {
				genomeData[genome].spawns_today++;
			}

			// Track last active
			const timestamp = trace.timestamp;
			if (timestamp && (!genomeData[genome].last_active || timestamp > genomeData[genome].last_active)) {
				genomeData[genome].last_active = timestamp;
			}
		}

		// Add points from leaderboard (match by genome in agent_id)
		for (const agent of rankings) {
			const agentId = agent.id || '';
			// Extract genome from agent ID format: CC-builder-HH:MM.DD.MM.XX
			const parts = agentId.split('-');
			if (parts.length >= 2) {
				const lab = parts[0];
				const role = parts[1];
				const cliMap: Record<string, string> = { CC: 'claude', OC: 'opencode', CX: 'codex', GE: 'gemini', GR: 'grok' };
				const cli = cliMap[lab] || lab.toLowerCase();
				const genomeName = `${cli}_${role}`;

				if (genomeData[genomeName]) {
					genomeData[genomeName].points_earned += agent.points || 0;
				}
			}
		}

		// Calculate stats
		const allGenomes = Object.values(genomeData);
		const activeToday = allGenomes.filter(g => g.spawns_today > 0 || (g.last_active?.startsWith(today)));

		// Sort by points + spawns for top performers
		const topPerformers = [...allGenomes]
			.sort((a, b) => (b.points_earned + b.spawns_today * 10) - (a.points_earned + a.spawns_today * 10))
			.slice(0, 10);

		// Aggregate by CLI
		const byCli: Record<string, { genomes: number; spawns: number; points: number }> = {};
		for (const genome of allGenomes) {
			if (!byCli[genome.cli]) {
				byCli[genome.cli] = { genomes: 0, spawns: 0, points: 0 };
			}
			byCli[genome.cli].genomes++;
			byCli[genome.cli].spawns += genome.spawns_today;
			byCli[genome.cli].points += genome.points_earned;
		}

		return {
			total_genomes: allGenomes.length,
			active_today: activeToday.length,
			top_performers: topPerformers,
			by_cli: byCli
		};
	} catch {
		return null;
	}
}

export async function getLinearData(): Promise<LinearData | null> {
	return await readJsonFile<LinearData | null>(PATHS.linear, null);
}

export async function getPendingLinearIssues(): Promise<PendingLinearData | null> {
	const data = await readJsonFile<PendingLinearData | null>(PATHS.pendingLinear, null);
	if (!data || !data.issues || data.issues.length === 0) return null;
	return data;
}

export async function getRecallData(): Promise<RecallStats | null> {
	try {
		const res = await fetch(PATHS.recall, { signal: AbortSignal.timeout(2000) });
		if (!res.ok) return null;
		return await res.json();
	} catch {
		return null;
	}
}

export async function getCircuitBreakers(): Promise<CircuitBreakersData | null> {
	return await readJsonFile<CircuitBreakersData | null>(PATHS.circuitBreakers, null);
}

export async function getMemoryStats(): Promise<MemoryStats | null> {
	const MEMORY_DIR = `${KRALIKI_BASE}/arena/data/memories`;

	try {
		if (!existsSync(MEMORY_DIR)) return null;

		const files = await readdir(MEMORY_DIR);
		const jsonlFiles = files.filter(f => f.endsWith('.jsonl'));

		if (jsonlFiles.length === 0) return null;

		let totalMemories = 0;
		let oldestMemory: string | null = null;
		let newestMemory: string | null = null;
		let totalSizeKb = 0;
		let ephemeralCount = 0;

		const ephemeralPattern = /^[A-Z]{2}-[a-z_]+-\d{2}:\d{2}\.\d{2}\.\d{2}\.[A-Z]{2}$/;

		const agentData: Array<{
			agent: string;
			count: number;
			size_kb: number;
			last_active: string;
			ephemeral: boolean;
		}> = [];

		for (const file of jsonlFiles) {
			const filePath = `${MEMORY_DIR}/${file}`;
			const agentName = file.replace('.jsonl', '');
			const isEphemeral = ephemeralPattern.test(agentName);

			if (isEphemeral) ephemeralCount++;

			try {
				const fileStat = await stat(filePath);
				const sizeKb = fileStat.size / 1024;
				totalSizeKb += sizeKb;

				const content = await readFile(filePath, 'utf-8');
				const lines = content.trim().split('\n').filter(l => l);
				const count = lines.length;
				totalMemories += count;

				let firstTime: string | null = null;
				let lastTime: string | null = null;

				for (const line of lines) {
					try {
						const mem = JSON.parse(line);
						const time = mem?.metadata?.time;
						if (time) {
							if (!firstTime) firstTime = time;
							lastTime = time;
						}
					} catch { /* skip invalid JSON */ }
				}

				// Update global oldest/newest
				if (firstTime) {
					if (!oldestMemory || firstTime < oldestMemory) {
						oldestMemory = firstTime;
					}
				}
				if (lastTime) {
					if (!newestMemory || lastTime > newestMemory) {
						newestMemory = lastTime;
					}
				}

				agentData.push({
					agent: agentName,
					count,
					size_kb: Math.round(sizeKb * 10) / 10,
					last_active: lastTime?.slice(0, 10) || '?',
					ephemeral: isEphemeral
				});
			} catch { /* skip unreadable files */ }
		}

		// Sort by count descending and take top 10
		agentData.sort((a, b) => b.count - a.count);
		const topAgents = agentData.slice(0, 10);

		// Check if mgrep is available
		let mgrepAvailable = false;
		try {
			const res = await fetch(`http://localhost:8001/v1/stores/kraliki_memories`, {
				signal: AbortSignal.timeout(1000)
			});
			mgrepAvailable = res.ok;
		} catch { /* mgrep not available */ }

		return {
			total_memories: totalMemories,
			total_agents: jsonlFiles.length,
			ephemeral_files: ephemeralCount,
			oldest_memory: oldestMemory,
			newest_memory: newestMemory,
			total_size_kb: Math.round(totalSizeKb * 10) / 10,
			top_agents: topAgents,
			mgrep_available: mgrepAvailable
		};
	} catch {
		return null;
	}
}

export async function getActivityHeatMap(): Promise<HeatMapEntry[]> {
	try {
		const { stdout } = await execAsync(`
			find ${GITHUB_BASE} -type f -mmin -120 \
				-not -path '*/.git/*' \
				-not -path '*/node_modules/*' \
				-not -path '*/.venv/*' \
				-not -path '*/__pycache__/*' \
				-not -path '*/.pm2/*' \
				-not -path '*/logs/*' \
				-not -path '*/progress/*' \
				-not -path '*/mgrep-selfhosted/data/*' \
				-not -name '*.log' \
				2>/dev/null | \
			sed 's|${GITHUB_BASE}/||' | \
			awk -F'/' '{if(NF>=2) print $1"/"$2; else print $1}' | \
			sort | uniq -c | sort -rn | head -12
		`);

		return stdout.split('\n')
			.filter((line: string) => line.trim())
			.map((line: string) => {
				const match = line.trim().match(/^(\d+)\s+(.+)$/);
				if (match) {
					return { count: parseInt(match[1]), folder: match[2] };
				}
				return null;
			})
			.filter((item): item is HeatMapEntry => item !== null);
	} catch {
		return [];
	}
}

export async function getRecentFiles(): Promise<RecentFile[]> {
	try {
		const { stdout } = await execAsync(`
			find ${GITHUB_BASE} -type f -mmin -120 \
				-not -path '*/.git/*' \
				-not -path '*/node_modules/*' \
				-not -path '*/.venv/*' \
				-not -path '*/__pycache__/*' \
				-not -path '*/.pm2/*' \
				-not -path '*/logs/*' \
				-not -name '*.log' \
				-printf '%T+ %p\n' 2>/dev/null | \
			sort -r | head -15 | \
			sed 's|${GITHUB_BASE}/||'
		`);

		return stdout.split('\n')
			.filter((line: string) => line.trim())
			.map((line: string) => {
				const parts = line.split(' ');
				const time = parts[0]?.split('.')[0]?.replace('T', ' ') || '';
				const path = parts.slice(1).join(' ');
				return { time: time.slice(11, 16), path }; // Just HH:MM
			});
	} catch {
		return [];
	}
}



// Task Queue types and functions
export interface Task {
	id: string;
	title: string;
	type: string;
	priority: string;
	app: string;
	status: string;
	claimed_by: string | null;
	description: string;
	blocked_reason?: string;
	estimated_time?: string;
	for_agent?: string;
}

export interface TaskQueueData {
	version: number;
	updated: string;
	tasks: Task[];
	stats: {
		total: number;
		open: number;
		claimed: number;
		completed: number;
		blocked: number;
		by_type: Record<string, number>;
	};
}

export async function getTaskQueue(): Promise<TaskQueueData | null> {
	const data = await readJsonFile<{ version: number; updated: string; tasks: Task[] } | null>(PATHS.tasks, null);
	if (!data) return null;

	// Calculate stats
	const stats = {
		total: data.tasks.length,
		open: data.tasks.filter(t => t.status === 'open').length,
		claimed: data.tasks.filter(t => t.status === 'claimed').length,
		completed: data.tasks.filter(t => t.status === 'completed').length,
		blocked: data.tasks.filter(t => t.status === 'blocked').length,
		by_type: {} as Record<string, number>
	};

	for (const task of data.tasks) {
		stats.by_type[task.type] = (stats.by_type[task.type] || 0) + 1;
	}

	return { ...data, stats };
}

// Blackboard types and functions
export interface BlackboardData {
	messages: BlackboardMessage[];
	stats: {
		total: number;
		by_topic: Record<string, number>;
		by_agent: Record<string, number>;
	};
}

export async function getBlackboard(): Promise<BlackboardData | null> {
	const data = await readJsonFile<{ messages: BlackboardMessage[] } | null>(PATHS.blackboard, null);
	if (!data) return null;

	// Get last 50 messages, sorted by time descending
	const messages = [...data.messages].sort((a, b) => b.time.localeCompare(a.time)).slice(0, 50);

	// Calculate stats
	const stats = {
		total: data.messages.length,
		by_topic: {} as Record<string, number>,
		by_agent: {} as Record<string, number>
	};

	for (const msg of data.messages) {
		stats.by_topic[msg.topic] = (stats.by_topic[msg.topic] || 0) + 1;
		stats.by_agent[msg.agent] = (stats.by_agent[msg.agent] || 0) + 1;
	}

	return { messages, stats };
}

export async function getFullStatus() {
	const results = await Promise.allSettled([
		getKralikiStats(),
		getActivityHeatMap(),
		getRecentFiles(),
		getLinearData(),
		getLeaderboard(),
		getSocialFeed(),
		getTaskQueue(),
		getBlackboard(),
		getAgentAnalytics(),
		getAgentStatus(),
		getRecallData(),
		getCircuitBreakers(),
		getCrashAnalytics(),
		getFitnessData(),
		getMemoryStats(),
		getDecisionTraceStats(),
		getGenomeStats(),
		getOrchestratorsState(),
		getCostAnalytics(),
		getPendingLinearIssues()
	]);

	const [kraliki, heatMap, recentFiles, linear, leaderboard, social, tasks, blackboard, analytics, agentStatus, recall, circuitBreakers, crashAnalytics, fitness, memoryStats, decisionTraces, genomeStats, orchestrators, costAnalytics, pendingLinear] =
		results.map(r => r.status === 'fulfilled' ? r.value : null);

	return {
		timestamp: new Date().toISOString(),
		kraliki,
		heatMap: heatMap || [],
		recentFiles: recentFiles || [],
		linear,
		pendingLinear,
		leaderboard,
		social: social || [],
		tasks,
		blackboard,
		analytics,
		agentStatus: agentStatus || [],
		recall,
		circuitBreakers,
		crashAnalytics,
		fitness,
		memoryStats,
		decisionTraces,
		genomeStats,
		orchestrators,
		costAnalytics
	};
}

export interface KralikiStats {
	timestamp: string;
	date: string;
	pm2: {
		total: number;
		online: number;
		stopped: number;
		errored: number;
		processes: Array<{
			name: string;
			status: string;
			restarts: number;
			uptime: number;
			memory: number;
			cpu: number;
		}>;
	};
	features?: Record<string, unknown>;
	dev?: {
		tasks_completed: number;
		commits: number;
		lines_added: number;
		lines_deleted: number;
		repos_with_commits: string[];
	};
	arena?: {
		total_points: number;
		active_agents: number;
		blackboard_messages: number;
	};
	system?: {
		uptime_seconds?: number;
		load_avg: number[];
		memory: {
			total_kb: number;
			used_kb: number;
			percent_used: number;
		};
	};
	health?: {
		timestamp: string;
		overall: 'healthy' | 'degraded' | 'unhealthy';
		endpoints: Array<{
			name: string;
			url: string;
			status: string;
			status_code: number;
		}>;
		pm2_issues: Array<{
			name: string;
			status: string;
			restarts: number;
		}>;
	};
	highways?: {
		collection_time: string;
		hours_analyzed: number;
		total_cycles: number;
		total_errors: number;
		total_successes: number;
	};
}

export async function getKralikiStats(): Promise<KralikiStats | null> {
	return await readJsonFile<KralikiStats | null>(PATHS.kralikiStats, null);
}

// Leaderboard types and functions
export interface LeaderboardEntry {
	id: string;
	points: number;
	rank: string;
	badge: string;
	achievements: string[];
	wins: number;
	losses: number;
}

export interface LeaderboardEvent {
	time: string;
	type: string;
	agent: string;
	points?: number;
	reason?: string;
}

export interface LeaderboardData {
	rankings: LeaderboardEntry[];
	governor: string | null;
	pending_challenges: unknown[];
	recent_events: LeaderboardEvent[];
	last_updated: string;
}

export async function getLeaderboard(): Promise<LeaderboardData | null> {
	return await readJsonFile<LeaderboardData | null>(PATHS.leaderboard, null);
}

// Agent Analytics - computed from leaderboard data
export interface AgentAnalytics {
	by_lab: Record<string, { agents: number; points: number; lab_name: string | null }>;
	by_role: Record<string, { agents: number; points: number }>;
	total_agents: number;
	total_points: number;
}

// Lab prefix mapping
const LAB_NAMES: Record<string, string> = {
	CC: 'Claude Code',
	OC: 'OpenCode',
	CX: 'Codex',
	GE: 'Gemini',
	GR: 'Grok'
};

function parseAgentId(agentId: string): { lab: string | null; role: string | null } {
	// New format: LAB-role-HH:MM.DD.MM.XX (e.g., CC-explorer-23:05.24.12.AA)
	const parts = agentId.split('-');
	if (parts.length >= 3 && LAB_NAMES[parts[0]]) {
		return { lab: parts[0], role: parts[1] };
	}
	// Legacy format: darwin-{cli}-{role}
	if (agentId.startsWith('darwin-') && parts.length >= 3) {
		const cli = parts[1];
		const cliToLab: Record<string, string> = { claude: 'CC', gemini: 'GE', codex: 'CX', opencode: 'OC' };
		return { lab: cliToLab[cli] || null, role: parts.slice(2).join('-') };
	}
	return { lab: null, role: null };
}

export async function getAgentAnalytics(): Promise<AgentAnalytics | null> {
	const leaderboard = await getLeaderboard();
	if (!leaderboard) return null;

	const analytics: AgentAnalytics = {
		by_lab: {},
		by_role: {},
		total_agents: leaderboard.rankings.length,
		total_points: leaderboard.rankings.reduce((sum, a) => sum + (a.points || 0), 0)
	};

	for (const agent of leaderboard.rankings) {
		const parsed = parseAgentId(agent.id);
		const lab = parsed.lab || 'unknown';
		const role = parsed.role || 'unknown';
		const points = agent.points || 0;

		// By lab
		if (!analytics.by_lab[lab]) {
			analytics.by_lab[lab] = { agents: 0, points: 0, lab_name: LAB_NAMES[lab] || null };
		}
		analytics.by_lab[lab].agents += 1;
		analytics.by_lab[lab].points += points;

		// By role
		if (!analytics.by_role[role]) {
			analytics.by_role[role] = { agents: 0, points: 0 };
		}
		analytics.by_role[role].agents += 1;
		analytics.by_role[role].points += points;
	}

	return analytics;
}

// Social Feed types and functions
export interface SocialFeedItem {
	id: string | number;
	timestamp?: string;
	time?: string;
	agent?: string;
	author?: string;
	channel?: string;
	content?: string;
	message?: string;
	type?: string;
	reactions?: Record<string, number>;
}

interface BlackboardMessage {
	id: number;
	time: string;
	agent: string;
	topic: string;
	message: string;
}

export async function getSocialFeed(): Promise<SocialFeedItem[]> {
	// Read from both social_feed.json and board.json (blackboard)
	const [socialData, blackboardData] = await Promise.all([
		readJsonFile<{ posts: SocialFeedItem[] } | null>(PATHS.socialFeed, null),
		readJsonFile<{ messages: BlackboardMessage[] } | null>(PATHS.blackboard, null)
	]);

	const allPosts: SocialFeedItem[] = [];

	// Add social feed posts
	if (socialData?.posts) {
		allPosts.push(...socialData.posts);
	}

	// Add blackboard messages (convert to SocialFeedItem format)
	if (blackboardData?.messages) {
		for (const msg of blackboardData.messages) {
			allPosts.push({
				id: `bb-${msg.id}`,
				timestamp: msg.time,
				time: msg.time,
				agent: msg.agent,
				author: msg.agent,
				channel: msg.topic,
				content: msg.message,
				message: msg.message,
				type: 'blackboard'
			});
		}
	}

	// Sort by timestamp descending, return latest 30
	allPosts.sort((a, b) => {
		const timeA = a.timestamp || a.time || '';
		const timeB = b.timestamp || b.time || '';
		return timeB.localeCompare(timeA);
	});

	return allPosts.slice(0, 30);
}

function formatDateTime(timestamp: Date | null): string {
	if (!timestamp) return '--';
	const year = timestamp.getFullYear();
	const month = String(timestamp.getMonth() + 1).padStart(2, '0');
	const day = String(timestamp.getDate()).padStart(2, '0');
	const hour = String(timestamp.getHours()).padStart(2, '0');
	const minute = String(timestamp.getMinutes()).padStart(2, '0');
	return `${year}-${month}-${day} ${hour}:${minute}`;
}

function formatDuration(ms: number | null): string {
	if (ms === null || Number.isNaN(ms) || ms < 0) return '--';
	const totalMinutes = Math.floor(ms / 60000);
	const hours = Math.floor(totalMinutes / 60);
	const minutes = totalMinutes % 60;
	if (hours > 0) {
		return `${hours}h ${minutes}m`;
	}
	if (minutes > 0) {
		return `${minutes}m`;
	}
	const seconds = Math.floor(ms / 1000);
	return `${seconds}s`;
}

const LAB_PREFIXES: Record<string, string> = {
	CC: 'claude',
	OC: 'opencode',
	CX: 'codex',
	GE: 'gemini',
	GR: 'grok'
};

function detectCliFromAgentId(agentId: string | null, command: string | null): string | null {
	if (agentId) {
		const prefix = agentId.split('-')[0];
		if (LAB_PREFIXES[prefix]) return LAB_PREFIXES[prefix];
	}
	if (command) {
		if (command.includes('codex')) return 'codex';
		if (command.includes('claude')) return 'claude';
		if (command.includes('gemini')) return 'gemini';
		if (command.includes('opencode')) return 'opencode';
	}
	return null;
}

function extractAgentIdFromCommand(command: string): string | null {
	// Match Kraliki agent ID format: "Kraliki agent CC-role-HH:MM.DD.MM.XX"
	const kralikiMatch = command.match(/Kraliki agent ([A-Z]{2}-[a-z_]+-\d{2}:\d{2}\.\d{2}\.\d{2}\.[A-Z]{2})/);
	if (kralikiMatch) return kralikiMatch[1];
	// Legacy format: AGENT_ID: xxx
	const legacyMatch = command.match(/AGENT_ID:\s*([A-Za-z0-9_.:-]+)/);
	return legacyMatch ? legacyMatch[1] : null;
}

function extractGenomeFromCommand(command: string): string | null {
	const match = command.match(/name:\s*([A-Za-z0-9_-]+)/);
	return match ? match[1] : null;
}

function parseAgentLogName(fileName: string, fileMtime: Date): {
	id: string;
	genome: string | null;
	cli: string | null;
	startTime: Date | null;
} {
	const baseName = fileName.replace(/\.log$/, '');

	if (baseName.startsWith('CC-') || baseName.startsWith('OC-') || baseName.startsWith('CX-') || baseName.startsWith('GE-') || baseName.startsWith('GR-')) {
		const [lab, role, timePart] = baseName.split('-', 3);
		const cli = LAB_PREFIXES[lab] || null;
		const genome = role || null;
		let startTime: Date | null = null;
		if (timePart) {
			const [time, day, month] = timePart.split('.');
			if (time && day && month) {
				const [hour, minute] = time.split(':');
				const year = fileMtime.getFullYear();
				startTime = new Date(year, Number(month) - 1, Number(day), Number(hour), Number(minute));
			}
		}
		return { id: baseName, genome, cli, startTime };
	}

	const legacyMatch = baseName.match(/^(?<genome>[a-z0-9_]+)_(?<date>\d{8})_(?<time>\d{6})$/);
	if (legacyMatch?.groups) {
		const genome = legacyMatch.groups.genome;
		const datePart = legacyMatch.groups.date;
		const timePart = legacyMatch.groups.time;
		const year = Number(datePart.slice(0, 4));
		const month = Number(datePart.slice(4, 6));
		const day = Number(datePart.slice(6, 8));
		const hour = Number(timePart.slice(0, 2));
		const minute = Number(timePart.slice(2, 4));
		const startTime = new Date(year, month - 1, day, hour, minute);
		const cli = genome.split('_')[0] || null;
		return { id: baseName, genome, cli, startTime };
	}

	return { id: baseName, genome: null, cli: null, startTime: null };
}

async function readTail(path: string, maxBytes = 65536): Promise<string> {
	try {
		const handle = await open(path, 'r');
		const fileStats = await handle.stat();
		const size = fileStats.size;
		if (size <= 0) {
			await handle.close();
			return '';
		}
		const readSize = Math.min(size, maxBytes);
		const buffer = Buffer.alloc(readSize);
		await handle.read(buffer, 0, readSize, size - readSize);
		await handle.close();
		return buffer.toString('utf-8');
	} catch {
		return '';
	}
}

function parseCompletionStatus(tail: string): 'completed' | 'failed' {
	const match = tail.match(/status:\s*([A-Za-z_-]+)/);
	if (!match) return 'completed';
	const status = match[1].toLowerCase();
	if (status === 'failed' || status === 'error' || status === 'timeout') {
		return 'failed';
	}
	return 'completed';
}

async function getRunningAgentProcesses(pointsByAgent: Map<string, number>): Promise<AgentStatusEntry[]> {
	const entries: AgentStatusEntry[] = [];
	const CONTROL_DIR = `${KRALIKI_BASE}/control`;

	try {
		// Read orchestrator state files to find spawned agents
		const controlFiles = await readdir(CONTROL_DIR).catch(() => []);
		const stateFiles = controlFiles.filter(f => f.startsWith('orchestrator_state_') && f.endsWith('.json'));

		for (const stateFile of stateFiles) {
			try {
				const content = await readFile(`${CONTROL_DIR}/${stateFile}`, 'utf-8');
				const state = JSON.parse(content);
				const pid = state.pid;
				const agentId = state.agent_id;
				const cli = state.cli;

				if (!pid || !agentId) continue;

				// Check if PID is still running
				try {
					await execAsync(`ps -p ${pid} -o pid=`);
				} catch {
					continue; // Process not running
				}

				// Get process start time and duration
				let startTime = '--';
				let duration = '--';
				try {
					const { stdout: startStdout } = await execAsync(`ps -p ${pid} -o lstart=`);
					startTime = formatDateTime(new Date(startStdout.trim()));
					const { stdout: elapsedStdout } = await execAsync(`ps -p ${pid} -o etimes=`);
					const elapsedSeconds = Number(elapsedStdout.trim());
					const durationMs = Number.isNaN(elapsedSeconds) ? null : elapsedSeconds * 1000;
					duration = formatDuration(durationMs);
				} catch {
					// Use spawned_at from state file
					if (state.spawned_at) {
						startTime = formatDateTime(new Date(state.spawned_at));
						const durationMs = Date.now() - new Date(state.spawned_at).getTime();
						duration = formatDuration(durationMs);
					}
				}

				// Extract genome from agent_id (e.g., CC-orchestrator-23:04.25.12.AA -> orchestrator)
				const parts = agentId.split('-');
				const genome = parts.length >= 2 ? `${cli}_${parts[1]}` : null;

				entries.push({
					id: agentId,
					genome,
					cli,
					status: 'running',
					pid,
					startTime,
					duration,
					points: pointsByAgent.get(agentId) ?? null
				});
			} catch {
				continue;
			}
		}

		// Also check for recently active log files (written in last 5 minutes)
		const logFiles = await readdir(AGENT_LOGS_DIR).catch(() => []);
		const now = Date.now();
		const FIVE_MINUTES = 5 * 60 * 1000;

		for (const logFile of logFiles) {
			if (!logFile.endsWith('.log')) continue;
			const logPath = `${AGENT_LOGS_DIR}/${logFile}`;
			const logStat = await stat(logPath).catch(() => null);
			if (!logStat) continue;

			// Check if log was written to in last 5 minutes
			if (now - logStat.mtime.getTime() < FIVE_MINUTES) {
				const { id, genome, cli, startTime: parsedStart } = parseAgentLogName(logFile, logStat.mtime);

				// Skip if we already have this agent from orchestrator state
				if (entries.some(e => e.id === id)) continue;

				const durationMs = parsedStart ? now - parsedStart.getTime() : null;

				entries.push({
					id,
					genome,
					cli,
					status: 'running',
					pid: null,
					startTime: formatDateTime(parsedStart),
					duration: formatDuration(durationMs),
					points: pointsByAgent.get(id) ?? null
				});
			}
		}
	} catch {
		return entries;
	}
	return entries;
}

// Crash Analytics types and functions
export interface CrashAnalytics {
	summary: {
		total_spawns_today: number;
		total_crashes_today: number;
		crash_rate_percent: number;
		zero_byte_crashes: number;
	};
	by_cli: Record<string, { spawns: number; crashes: number; zero_byte: number; crash_rate: number }>;
	recent_crashes: Array<{
		id: string;
		cli: string | null;
		genome: string | null;
		time: string;
		type: 'zero_byte' | 'error' | 'timeout';
		error_snippet?: string;
	}>;
	error_patterns: Record<string, number>;
}

export async function getCrashAnalytics(): Promise<CrashAnalytics | null> {
	if (!existsSync(AGENT_LOGS_DIR)) return null;

	const analytics: CrashAnalytics = {
		summary: {
			total_spawns_today: 0,
			total_crashes_today: 0,
			crash_rate_percent: 0,
			zero_byte_crashes: 0
		},
		by_cli: {},
		recent_crashes: [],
		error_patterns: {}
	};

	try {
		const logEntries = await readdir(AGENT_LOGS_DIR, { withFileTypes: true });
		const logFiles = logEntries.filter(entry => entry.isFile() && entry.name.endsWith('.log'));

		const today = new Date();
		const todayStr = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`;

		const fileStats = await Promise.all(
			logFiles.map(async entry => {
				const filePath = `${AGENT_LOGS_DIR}/${entry.name}`;
				const stats = await stat(filePath);
				return { entry, filePath, stats };
			})
		);

		// Sort by modification time descending
		fileStats.sort((a, b) => b.stats.mtime.getTime() - a.stats.mtime.getTime());

		for (const fileInfo of fileStats) {
			const { entry, filePath, stats: fileStat } = fileInfo;
			const { id, genome, cli, startTime } = parseAgentLogName(entry.name, fileStat.mtime);

			// Check if from today
			const fileDate = fileStat.mtime.toISOString().slice(0, 10);
			const isToday = fileDate === todayStr;

			// Initialize CLI stats
			const cliKey = cli || 'unknown';
			if (!analytics.by_cli[cliKey]) {
				analytics.by_cli[cliKey] = { spawns: 0, crashes: 0, zero_byte: 0, crash_rate: 0 };
			}

			if (isToday) {
				analytics.summary.total_spawns_today++;
				analytics.by_cli[cliKey].spawns++;
			}

			// Check for crash indicators
			const isZeroByte = fileStat.size === 0;
			let crashType: 'zero_byte' | 'error' | 'timeout' | null = null;
			let errorSnippet: string | undefined;

			if (isZeroByte) {
				crashType = 'zero_byte';
				if (isToday) {
					analytics.summary.zero_byte_crashes++;
					analytics.by_cli[cliKey].zero_byte++;
				}
			} else {
				// Check for error patterns in log
				const tail = await readTail(filePath, 8192);
				if (tail) {
					// Look for common error patterns
					const errorPatterns = [
						{ pattern: /NotFoundError/i, key: 'NotFoundError' },
						{ pattern: /RATE_LIMIT/i, key: 'RateLimit' },
						{ pattern: /timeout/i, key: 'Timeout' },
						{ pattern: /connection refused/i, key: 'ConnectionRefused' },
						{ pattern: /authentication failed/i, key: 'AuthFailed' },
						{ pattern: /Error:\s*(.{0,50})/i, key: 'GenericError' },
						{ pattern: /status:\s*failed/i, key: 'StatusFailed' },
						{ pattern: /exit code:\s*[1-9]/i, key: 'NonZeroExit' }
					];

					for (const { pattern, key } of errorPatterns) {
						const match = tail.match(pattern);
						if (match) {
							crashType = key === 'Timeout' ? 'timeout' : 'error';
							analytics.error_patterns[key] = (analytics.error_patterns[key] || 0) + 1;
							errorSnippet = match[0].slice(0, 80);
							break;
						}
					}
				}
			}

			if (crashType && isToday) {
				analytics.summary.total_crashes_today++;
				analytics.by_cli[cliKey].crashes++;

				// Add to recent crashes (limit to 20)
				if (analytics.recent_crashes.length < 20) {
					analytics.recent_crashes.push({
						id,
						cli,
						genome,
						time: formatDateTime(fileStat.mtime),
						type: crashType,
						error_snippet: errorSnippet
					});
				}
			}
		}

		// Calculate crash rates
		if (analytics.summary.total_spawns_today > 0) {
			analytics.summary.crash_rate_percent = Math.round(
				(analytics.summary.total_crashes_today / analytics.summary.total_spawns_today) * 100
			);
		}

		for (const cliKey of Object.keys(analytics.by_cli)) {
			const cliStats = analytics.by_cli[cliKey];
			if (cliStats.spawns > 0) {
				cliStats.crash_rate = Math.round((cliStats.crashes / cliStats.spawns) * 100);
			}
		}

		return analytics;
	} catch {
		return null;
	}
}

export async function getAgentStatus(): Promise<AgentStatusEntry[]> {
	if (!existsSync(AGENT_LOGS_DIR)) return [];

	const [logEntries, leaderboard] = await Promise.all([
		readdir(AGENT_LOGS_DIR, { withFileTypes: true }),
		getLeaderboard()
	]);

	const pointsByAgent = new Map<string, number>();
	if (leaderboard?.rankings) {
		for (const agent of leaderboard.rankings) {
			pointsByAgent.set(agent.id, agent.points || 0);
		}
	}

	const runningEntries = await getRunningAgentProcesses(pointsByAgent);
	const runningIds = new Set(runningEntries.map(entry => entry.id));

	const logFiles = logEntries.filter(entry => entry.isFile() && entry.name.endsWith('.log'));
	const fileStats = await Promise.all(
		logFiles.map(async entry => {
			const filePath = `${AGENT_LOGS_DIR}/${entry.name}`;
			return {
				entry,
				filePath,
				stats: await stat(filePath)
			};
		})
	);

	const completedCandidates: {
		entry: AgentStatusEntry;
		endTime: Date;
		filePath: string;
	}[] = [];

	for (const fileInfo of fileStats) {
		const { entry, filePath, stats: fileStat } = fileInfo;
		const { id, genome, cli, startTime } = parseAgentLogName(entry.name, fileStat.mtime);
		if (runningIds.has(id)) continue;
		const endTime = fileStat.mtime;
		const durationMs = startTime ? endTime.getTime() - startTime.getTime() : null;
		const entryBase: AgentStatusEntry = {
			id,
			genome,
			cli,
			status: 'completed',
			pid: null,
			startTime: formatDateTime(startTime),
			duration: formatDuration(durationMs),
			points: pointsByAgent.get(id) ?? null
		};
		completedCandidates.push({ entry: entryBase, endTime, filePath });
	}

	completedCandidates.sort((a, b) => b.endTime.getTime() - a.endTime.getTime());
	const completedEntries = completedCandidates.slice(0, 10);

	const completedWithStatus: AgentStatusEntry[] = [];
	for (const completed of completedEntries) {
		const tail = await readTail(completed.filePath);
		const status = parseCompletionStatus(tail);
		const genomeMatch = tail.match(/genome:\s*([A-Za-z0-9_-]+)/);
		const nameMatch = tail.match(/name:\s*([A-Za-z0-9_-]+)/);
		const genome = genomeMatch?.[1] || nameMatch?.[1] || completed.entry.genome;
		const cli = detectCliFromAgentId(completed.entry.id, tail) || completed.entry.cli;
		completedWithStatus.push({
			...completed.entry,
			status,
			genome,
			cli
		});
	}

	runningEntries.sort((a, b) => a.startTime.localeCompare(b.startTime));
	return [...runningEntries, ...completedWithStatus];
}

// Orchestrator State types and functions
export interface OrchestratorState {
	cli: string;
	pid: number | null;
	agent_id: string | null;
	spawned_at: string | null;
	duration: string;
	is_running: boolean;
}

export interface OrchestratorsData {
	orchestrators: OrchestratorState[];
	active_count: number;
	total_runtime_minutes: number;
}

export async function getOrchestratorsState(): Promise<OrchestratorsData | null> {
	const CONTROL_DIR = `${KRALIKI_BASE}/control`;
	const CLIS = ['claude', 'codex', 'opencode', 'gemini'];

	try {
		const orchestrators: OrchestratorState[] = [];
		let totalRuntimeMs = 0;
		let activeCount = 0;

		for (const cli of CLIS) {
			const stateFile = `${CONTROL_DIR}/orchestrator_state_${cli}.json`;

			try {
				if (!existsSync(stateFile)) {
					orchestrators.push({
						cli,
						pid: null,
						agent_id: null,
						spawned_at: null,
						duration: '--',
						is_running: false
					});
					continue;
				}

				const content = await readFile(stateFile, 'utf-8');
				const state = JSON.parse(content);
				const pid = state.pid;
				const agentId = state.agent_id;
				const spawnedAt = state.spawned_at;

				// Check if PID is running
				let isRunning = false;
				if (pid) {
					try {
						await execAsync(`ps -p ${pid} -o pid=`);
						isRunning = true;
						activeCount++;
					} catch {
						isRunning = false;
					}
				}

				// Calculate duration
				let duration = '--';
				if (spawnedAt) {
					const startTime = new Date(spawnedAt);
					const durationMs = Date.now() - startTime.getTime();
					if (isRunning) {
						totalRuntimeMs += durationMs;
					}
					duration = formatDuration(durationMs);
				}

				orchestrators.push({
					cli,
					pid,
					agent_id: agentId,
					spawned_at: spawnedAt,
					duration,
					is_running: isRunning
				});
			} catch {
				orchestrators.push({
					cli,
					pid: null,
					agent_id: null,
					spawned_at: null,
					duration: '--',
					is_running: false
				});
			}
		}

		return {
			orchestrators,
			active_count: activeCount,
			total_runtime_minutes: Math.floor(totalRuntimeMs / 60000)
		};
	} catch {
		return null;
	}
}

// Cost Analytics types and functions
export interface CostAnalytics {
	summary: {
		total_cost_today: number;
		total_cost_week: number;
		total_tokens_today: number;
		total_agents_today: number;
		avg_cost_per_agent: number;
	};
	by_cli: Record<string, { agents: number; cost: number; tokens: number }>;
	by_model: Record<string, { requests: number; cost: number; input_tokens: number; output_tokens: number }>;
	top_agents: Array<{
		id: string;
		cli: string | null;
		cost: number;
		duration_ms: number;
		points: number | null;
		efficiency: number | null; // points per dollar
	}>;
	hourly_costs: Array<{ hour: string; cost: number; agents: number }>;
}

// Pricing tables for cost calculation (USD per 1M tokens)
const MODEL_PRICING = {
	// Anthropic Claude
	'claude-opus-4-20250514': { input: 15, output: 75, tier: 'premium' },
	'claude-opus-4-5-20251101': { input: 15, output: 75, tier: 'premium' },
	'claude-sonnet-4-20250514': { input: 3, output: 15, tier: 'standard' },
	'claude-sonnet-4-5-20250929': { input: 3, output: 15, tier: 'standard' },
	'claude-3-5-sonnet-20241022': { input: 3, output: 15, tier: 'standard' },
	'claude-3-5-haiku-20241022': { input: 0.8, output: 4, tier: 'economy' },
	// Google Gemini
	'gemini-2.5-flash': { input: 0.075, output: 0.30, tier: 'economy' },
	'gemini-2.5-pro': { input: 1.25, output: 5, tier: 'standard' },
	'gemini-2.0-flash': { input: 0.075, output: 0.30, tier: 'economy' },
	// OpenAI
	'gpt-4.1': { input: 2.5, output: 10, tier: 'standard' },
	'gpt-4.5': { input: 2.5, output: 10, tier: 'standard' },
	'gpt-4o': { input: 2.5, output: 10, tier: 'standard' },
	'o3-mini': { input: 1.1, output: 4.4, tier: 'economy' },
	'o4-mini': { input: 1.1, output: 4.4, tier: 'economy' },
	// ZhipuAI (via OpenCode)
	'glm-4.7': { input: 0.1, output: 0.1, tier: 'economy' },
	'glm-4.7-free': { input: 0, output: 0, tier: 'free' },
} as const;

export async function getCostAnalytics(): Promise<CostAnalytics | null> {
	if (!existsSync(AGENT_LOGS_DIR)) return null;

	const analytics: CostAnalytics = {
		summary: {
			total_cost_today: 0,
			total_cost_week: 0,
			total_tokens_today: 0,
			total_agents_today: 0,
			avg_cost_per_agent: 0
		},
		by_cli: {},
		by_model: {},
		top_agents: [],
		hourly_costs: []
	};

	try {
		const logEntries = await readdir(AGENT_LOGS_DIR, { withFileTypes: true });
		const logFiles = logEntries.filter(entry => entry.isFile() && entry.name.endsWith('.log'));

		const today = new Date();
		const todayStr = today.toISOString().slice(0, 10);
		const weekAgo = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000);

		const fileStats = await Promise.all(
			logFiles.map(async entry => {
				const filePath = `${AGENT_LOGS_DIR}/${entry.name}`;
				const stats = await stat(filePath);
				return { entry, filePath, stats };
			})
		);

		// Sort by modification time descending
		fileStats.sort((a, b) => b.stats.mtime.getTime() - a.stats.mtime.getTime());

		const hourlyCosts: Record<string, { cost: number; agents: number }> = {};
		const agentCosts: Array<{
			id: string;
			cli: string | null;
			cost: number;
			duration_ms: number;
			points: number | null;
			time: Date;
		}> = [];

		// Process only recent files (last 100 to keep it fast)
		for (const fileInfo of fileStats.slice(0, 100)) {
			const { entry, filePath, stats: fileStat } = fileInfo;
			const { id, cli } = parseAgentLogName(entry.name, fileStat.mtime);

			// Check date
			const fileDate = fileStat.mtime.toISOString().slice(0, 10);
			const isToday = fileDate === todayStr;
			const isThisWeek = fileStat.mtime >= weekAgo;

			if (!isThisWeek) continue;

			try {
				// Read the last line which contains the result JSON
				const content = await readTail(filePath, 32768);
				const lines = content.split('\n').filter(l => l.trim());
				const lastLine = lines[lines.length - 1];

				if (!lastLine) continue;

				const result = JSON.parse(lastLine);
				const cost = result.total_cost_usd || 0;
				const durationMs = result.duration_ms || 0;
				const usage = result.usage || {};
				const modelUsage = result.modelUsage || {};

				// Extract points from result text
				let points: number | null = null;
				const resultText = result.result || '';
				const pointsMatch = resultText.match(/points[_\s]*(?:earned)?[:\s]*(\d+)/i);
				if (pointsMatch) {
					points = parseInt(pointsMatch[1], 10);
				}

				// Update summaries
				if (isToday) {
					analytics.summary.total_cost_today += cost;
					analytics.summary.total_agents_today++;
					analytics.summary.total_tokens_today +=
						(usage.input_tokens || 0) + (usage.output_tokens || 0);
				}
				analytics.summary.total_cost_week += cost;

				// By CLI
				const cliKey = cli || 'unknown';
				if (!analytics.by_cli[cliKey]) {
					analytics.by_cli[cliKey] = { agents: 0, cost: 0, tokens: 0 };
				}
				if (isToday) {
					analytics.by_cli[cliKey].agents++;
					analytics.by_cli[cliKey].cost += cost;
					analytics.by_cli[cliKey].tokens +=
						(usage.input_tokens || 0) + (usage.output_tokens || 0);
				}

				// By model
				for (const [model, modelData] of Object.entries(modelUsage)) {
					const data = modelData as any;
					if (!analytics.by_model[model]) {
						analytics.by_model[model] = { requests: 0, cost: 0, input_tokens: 0, output_tokens: 0 };
					}
					if (isToday) {
						analytics.by_model[model].requests++;
						analytics.by_model[model].cost += data.costUSD || 0;
						analytics.by_model[model].input_tokens += data.inputTokens || 0;
						analytics.by_model[model].output_tokens += data.outputTokens || 0;
					}
				}

				// Hourly costs (today only)
				if (isToday) {
					const hour = fileStat.mtime.toISOString().slice(11, 13) + ':00';
					if (!hourlyCosts[hour]) {
						hourlyCosts[hour] = { cost: 0, agents: 0 };
					}
					hourlyCosts[hour].cost += cost;
					hourlyCosts[hour].agents++;
				}

				// Top agents (today only)
				if (isToday && cost > 0) {
					agentCosts.push({
						id,
						cli,
						cost,
						duration_ms: durationMs,
						points,
						time: fileStat.mtime
					});
				}
			} catch {
				// Skip files that can't be parsed
			}
		}

		// Calculate average
		if (analytics.summary.total_agents_today > 0) {
			analytics.summary.avg_cost_per_agent =
				analytics.summary.total_cost_today / analytics.summary.total_agents_today;
		}

		// Format hourly costs
		analytics.hourly_costs = Object.entries(hourlyCosts)
			.map(([hour, data]) => ({ hour, ...data }))
			.sort((a, b) => a.hour.localeCompare(b.hour));

		// Top agents by cost
		analytics.top_agents = agentCosts
			.sort((a, b) => b.cost - a.cost)
			.slice(0, 10)
			.map(a => ({
				id: a.id,
				cli: a.cli,
				cost: Math.round(a.cost * 100) / 100,
				duration_ms: a.duration_ms,
				points: a.points,
				efficiency: a.points && a.cost > 0
					? Math.round((a.points / a.cost) * 10) / 10
					: null
			}));

		// Round numbers
		analytics.summary.total_cost_today = Math.round(analytics.summary.total_cost_today * 100) / 100;
		analytics.summary.total_cost_week = Math.round(analytics.summary.total_cost_week * 100) / 100;
		analytics.summary.avg_cost_per_agent = Math.round(analytics.summary.avg_cost_per_agent * 100) / 100;

		return analytics;
	} catch {
		return null;
	}
}
