<script lang="ts">
	import { onMount } from "svelte";

	import type {
		KralikiStats,
		BlackboardData,
		AgentStatusEntry,
		LinearData,
	} from "$lib/server/data";

	interface Status {
		timestamp: string;
		kraliki: KralikiStats | null;
		blackboard: BlackboardData | null;
		agentStatus: AgentStatusEntry[];
		linear: LinearData | null;
	}

	interface FocusPriority {
		title: string;
		priority: string;
	}

	interface FocusDailyPlan {
		greeting: string;
		priorities: FocusPriority[];
		overdue: number;
		due_today: number;
		insight?: string;
	}

	interface FocusNextAction {
		action: string;
		reason?: string;
	}

	let status = $state<Status | null>(null);
	let loading = $state(true);
	let error = $state<string | null>(null);
	let focusPlan = $state<FocusDailyPlan | null>(null);
	let focusNext = $state<FocusNextAction | null>(null);
	let focusLoading = $state(false);
	let focusError = $state<string | null>(null);

	async function fetchStatus() {
		try {
			const res = await fetch("/api/status");
			if (!res.ok) throw new Error("Failed to fetch status");
			status = await res.json();
			error = null;
		} catch (e) {
			error = e instanceof Error ? e.message : "Unknown error";
		} finally {
			loading = false;
		}
	}

	function isSystemHealthy(s: Status | null): boolean {
		if (!s?.kraliki) return false;
		const health = s.kraliki.health?.overall;
		return health === 'healthy' || health === 'degraded';
	}

	function getRunningAgentCount(s: Status | null): number {
		if (!s?.agentStatus) return 0;
		return s.agentStatus.filter(a => a.status === 'running').length;
	}

	function priorityFromScore(score?: number) {
		if (score === undefined || score === null) return 'medium';
		if (score >= 80) return 'high';
		if (score >= 60) return 'medium';
		return 'low';
	}

	function priorityTone(priority: string) {
		if (priority === 'high' || priority === 'urgent') return 'red';
		if (priority === 'medium') return 'yellow';
		return 'cyan';
	}

	function normalizeFocusPlan(raw: Record<string, any> | null): FocusDailyPlan | null {
		if (!raw) return null;
		const priorities = raw.priorities
			|| raw.top_tasks?.map((item: Record<string, any>) => ({
				title: item.title || item.task?.title || 'Untitled task',
				priority: item.priority || priorityFromScore(item.priority_score)
			}))
			|| [];

		return {
			greeting: raw.greeting || 'Ready to focus?',
			priorities,
			overdue: raw.overdue ?? raw.overdue_count ?? 0,
			due_today: raw.due_today ?? raw.due_today_count ?? 0,
			insight: raw.insight || raw.shadow_insight || raw.reasoning || raw.recommendation
		};
	}

	function normalizeNextAction(raw: Record<string, any> | null): FocusNextAction | null {
		if (!raw) return null;
		const action = raw.message || raw.action || 'Next action ready';
		const reason = raw.reason || raw.reasoning || raw.suggestion;
		return { action, reason };
	}

	async function fetchFocusPulse() {
		focusLoading = true;
		focusError = null;
		try {
			const [planRes, actionRes] = await Promise.all([
				fetch('/api/focus/brain?action=daily-plan', { signal: AbortSignal.timeout(15000) }),
				fetch('/api/focus/brain?action=next-action', { signal: AbortSignal.timeout(15000) })
			]);

			if (planRes.ok) {
				const data = await planRes.json();
				focusPlan = normalizeFocusPlan(data.data || data);
			}

			if (actionRes.ok) {
				const data = await actionRes.json();
				focusNext = normalizeNextAction(data.data || data);
			}

			if (!planRes.ok && !actionRes.ok) {
				focusError = 'Focus Brain unavailable';
			}
		} catch (e) {
			focusError = e instanceof Error ? e.message : 'Focus Brain error';
		} finally {
			focusLoading = false;
		}
	}

	onMount(() => {
		fetchStatus();
		fetchFocusPulse();
		const interval = setInterval(fetchStatus, 30000);
		return () => clearInterval(interval);
	});
</script>

{#if loading && !status}
	<div class="loading">
		<div class="loading-text">ESTABLISHING SECURE CONNECTION</div>
		<div class="loading-bar"></div>
		<div class="subtitle">Interrogating Kraliki Subsystems</div>
	</div>
{:else if error}
	<div class="container">
		<div class="card pulse-scan" style="max-width: 600px; margin: 100px auto;">
			<h2 class="red">SYSTEM_CRITICAL // CONNECTION_FAILURE</h2>
			<div class="log-box mt-16" style="color: var(--system-red); border-color: var(--system-red);">
				ERROR_LOG: {error.toUpperCase()}
				TRACE: SESSION_REJECTED_BY_HOST
				ACTION: RETRY_REQUIRED
			</div>
			<button class="brutal-btn mt-16" style="width: 100%; border-color: var(--system-red);" onclick={fetchStatus}>REINIT_CONNECTION_PROTOCOL</button>
		</div>
	</div>
{:else if status}
	<!-- System Status Banner -->
	<div class="status-banner" class:healthy={isSystemHealthy(status)} class:unhealthy={!isSystemHealthy(status)}>
		<div class="status-icon">
			{#if isSystemHealthy(status)}
				<span class="pulse-dot green big"></span>
			{:else}
				<span class="pulse-dot red big pulse-brutal"></span>
			{/if}
		</div>
		<div class="status-text">
			<span class="status-label">SYSTEM_STATUS</span>
			<span class="status-value">{isSystemHealthy(status) ? 'OPERATIONAL' : 'DEGRADED'}</span>
		</div>
		<div class="status-summary">
			<span>AGENTS: {getRunningAgentCount(status)} RUNNING</span>
			{#if status.linear}
				<span>ISSUES: {status.linear.stats.total} TOTAL</span>
			{/if}
			<span>UPTIME: {Math.floor((status?.kraliki?.system?.uptime_seconds || 0) / 86400)}D</span>
		</div>
	</div>

	<div class="grid">
		<!-- Focus / Daily Objective -->
		<div class="card focus-card">
			<h2 class="glitch">
				FOCUS // TODAY
				<span style="margin-left: auto; display: flex; gap: 8px;">
					<a href="/focus" class="brutal-btn small">OPEN</a>
					<button class="brutal-btn small outline" onclick={fetchFocusPulse} disabled={focusLoading}>
						{focusLoading ? 'LOADING...' : 'REFRESH'}
					</button>
				</span>
			</h2>

			{#if focusError}
				<div class="log-box" style="color: var(--system-red); border-color: var(--system-red);">
					FOCUS_BRAIN_OFFLINE // {focusError}
				</div>
			{:else if focusPlan || focusNext}
				{#if focusNext}
					<div class="log-box">
						NEXT_ACTION: {focusNext.action}
						{#if focusNext.reason}
							{"\n"}REASON: {focusNext.reason}
						{/if}
					</div>
				{/if}

				{#if focusPlan}
					<div class="stat-row">
						<span class="stat-label">Greeting</span>
						<span class="stat-value cyan">{focusPlan.greeting}</span>
					</div>
					<div class="stat-row">
						<span class="stat-label">Overdue</span>
						<span class="stat-value red">{focusPlan.overdue}</span>
					</div>
					<div class="stat-row">
						<span class="stat-label">Due Today</span>
						<span class="stat-value yellow">{focusPlan.due_today}</span>
					</div>

					{#if focusPlan.priorities.length}
						<div style="margin-top: 12px;">
							<div class="stat-label" style="margin-bottom: 6px;">Top Priorities</div>
							{#each focusPlan.priorities.slice(0, 3) as priority}
								<div class="stat-row">
									<span class="stat-label">{priority.title}</span>
									<span class="stat-value {priorityTone(priority.priority)}">{priority.priority.toUpperCase()}</span>
								</div>
							{/each}
						</div>
					{/if}

					{#if focusPlan.insight}
						<div class="log-box" style="margin-top: 12px;">
							INSIGHT: {focusPlan.insight}
						</div>
					{/if}
				{/if}
			{:else if focusLoading}
				<div style="color: var(--muted-foreground); font-size: 11px;">Loading Focus by Kraliki...</div>
			{:else}
				<div style="color: var(--muted-foreground); font-size: 11px;">No Focus data yet.</div>
			{/if}
		</div>

		<!-- Quick Actions Grid -->
		<div class="card actions-card">
			<h2 class="glitch">QUICK_ACTIONS</h2>
			<div class="actions-grid">
				<a href="/agents" class="action-btn">
					<div class="action-icon">🤖</div>
					<div class="action-label">SPAWN_AGENT</div>
				</a>
				<a href="/notebook" class="action-btn">
					<div class="action-icon">📓</div>
					<div class="action-label">NOTEBOOK</div>
				</a>
				<a href="/linear" class="action-btn">
					<div class="action-icon">📋</div>
					<div class="action-label">VIEW_ISSUES</div>
				</a>
				<a href="/health" class="action-btn">
					<div class="action-icon">❤️</div>
					<div class="action-label">HEALTH</div>
				</a>
				<a href="/blackboard" class="action-btn">
					<div class="action-icon">💬</div>
					<div class="action-label">BLACKBOARD</div>
				</a>
				<a href="/agents" class="action-btn">
					<div class="action-icon">👥</div>
					<div class="action-label">SWARM</div>
				</a>
				<a href="/recall" class="action-btn">
					<div class="action-icon">🧠</div>
					<div class="action-label">RECALL</div>
				</a>
				<a href="/costs" class="action-btn">
					<div class="action-icon">💰</div>
					<div class="action-label">COSTS</div>
				</a>
			</div>
		</div>

		<!-- Active Agents Summary -->
		<div class="card agents-card">
			<h2 class="glitch">ACTIVE_AGENTS // {getRunningAgentCount(status)} RUNNING</h2>
			{#if status.agentStatus && status.agentStatus.length > 0}
				<div class="agents-summary">
					<div class="agent-stat">
						<span class="stat-label">Running</span>
						<span class="stat-value green">{getRunningAgentCount(status)}</span>
					</div>
					<div class="agent-stat">
						<span class="stat-label">Completed</span>
						<span class="stat-value cyan">{status.agentStatus.filter(a => a.status === 'completed').length}</span>
					</div>
					<div class="agent-stat">
						<span class="stat-label">Failed</span>
						<span class="stat-value" class:red={status.agentStatus.filter(a => a.status === 'failed').length > 0}>{status.agentStatus.filter(a => a.status === 'failed').length}</span>
					</div>
				</div>
				<a href="/agents" class="brutal-btn mt-16" style="width: 100%;">VIEW_ALL_AGENTS</a>
			{:else}
				<p class="hint">No agents currently active.</p>
				<a href="/agents" class="brutal-btn mt-16" style="width: 100%;">MANAGE_SWARM</a>
			{/if}
		</div>

		<!-- Blackboard Feed -->
		{#if status.blackboard}
			<div class="card blackboard-card span-2">
				<h2>BLACKBOARD // {status.blackboard.stats.total} PACKETS</h2>
				<div class="blackboard-stats">
					<span>TOPICS: {Object.keys(status.blackboard.stats.by_topic).join(', ').toUpperCase()}</span>
					<span>ACTIVE_AGENTS: {Object.keys(status.blackboard.stats.by_agent).length}</span>
				</div>
				<div class="blackboard-feed">
					{#each status.blackboard.messages.slice(0, 20) as msg}
						<div class="bb-message">
							<div class="bb-header">
								<span class="bb-agent">{msg.agent.toUpperCase()}</span>
								<span class="bb-topic">#{msg.topic.toUpperCase()}</span>
								<span class="bb-time">[{msg.time.slice(11, 19)}]</span>
							</div>
							<div class="bb-content">{msg.message.slice(0, 400)}{msg.message.length > 400 ? '...' : ''}</div>
						</div>
					{/each}
				</div>
				<a href="/blackboard" class="brutal-btn mt-16" style="width: 100%;">VIEW_FULL_FEED</a>
			</div>
		{/if}
	</div>
{/if}

<style>
	.grid {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
		gap: 24px;
		margin-top: 24px;
	}

	.span-2 {
		grid-column: span 2;
	}

	@media (max-width: 800px) {
		.span-2 {
			grid-column: span 1;
		}
	}

	.hint {
		font-size: 11px;
		color: var(--muted-foreground);
		text-transform: uppercase;
	}

	/* Status Banner */
	.status-banner {
		display: flex;
		align-items: center;
		gap: 24px;
		padding: 24px;
		border: 3px solid var(--border);
		background: var(--surface);
		box-shadow: 6px 6px 0 0 var(--border);
		margin-bottom: 24px;
	}

	.status-banner.healthy {
		border-color: var(--terminal-green);
		box-shadow: 6px 6px 0 0 var(--terminal-green);
	}

	.status-banner.unhealthy {
		border-color: var(--system-red);
		box-shadow: 6px 6px 0 0 var(--system-red);
		animation: pulse-border 1s ease-in-out infinite;
	}

	.status-text {
		display: flex;
		flex-direction: column;
		gap: 4px;
	}

	.status-label {
		font-size: 10px;
		color: var(--muted-foreground);
		text-transform: uppercase;
		letter-spacing: 0.1em;
	}

	.status-value {
		font-family: 'JetBrains Mono', monospace;
		font-size: 24px;
		font-weight: 700;
	}

	.status-summary {
		display: flex;
		gap: 24px;
		margin-left: auto;
		font-family: 'JetBrains Mono', monospace;
		font-size: 12px;
		color: var(--muted-foreground);
	}

	/* Focus Card */
	.focus-card {
		min-height: 400px;
	}

	/* Actions Card */
	.actions-card {
		grid-column: span 2;
	}

	@media (max-width: 800px) {
		.actions-card {
			grid-column: span 1;
		}
	}

	.actions-grid {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
		gap: 12px;
	}

	.action-btn {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 12px;
		padding: 20px;
		border: 2px solid var(--border);
		background: var(--surface);
		text-decoration: none;
		transition: all 0.1s ease;
		box-shadow: 4px 4px 0 0 var(--border);
	}

	.action-btn:hover {
		border-color: var(--terminal-green);
		background: rgba(51, 255, 0, 0.05);
		transform: translate(-2px, -2px);
		box-shadow: 6px 6px 0 0 var(--terminal-green);
	}

	.action-icon {
		font-size: 28px;
	}

	.action-label {
		font-family: 'JetBrains Mono', monospace;
		font-size: 10px;
		font-weight: 700;
		text-transform: uppercase;
		text-align: center;
		letter-spacing: 0.05em;
	}

	/* Agents Summary */
	.agents-summary {
		display: grid;
		grid-template-columns: repeat(3, 1fr);
		gap: 16px;
		margin-bottom: 16px;
	}

	.agent-stat {
		display: flex;
		flex-direction: column;
		align-items: center;
		padding: 16px;
		border: 2px solid var(--border);
		background: rgba(240, 240, 240, 0.02);
	}

	.agent-stat .stat-label {
		font-size: 10px;
		color: var(--muted-foreground);
		text-transform: uppercase;
	}

	.agent-stat .stat-value {
		font-family: 'JetBrains Mono', monospace;
		font-size: 24px;
		font-weight: 700;
		margin-top: 4px;
	}

	/* Blackboard Card */
	.blackboard-card {
		min-height: 500px;
	}

	.blackboard-stats {
		display: flex;
		gap: 24px;
		margin-bottom: 16px;
		font-family: 'JetBrains Mono', monospace;
		font-size: 10px;
		color: var(--muted-foreground);
	}

	.blackboard-feed {
		display: flex;
		flex-direction: column;
		gap: 8px;
		max-height: 400px;
		overflow-y: auto;
	}

	.bb-message {
		padding: 12px;
		border: 1px solid var(--border);
		background: rgba(240, 240, 240, 0.02);
	}

	.bb-header {
		display: flex;
		gap: 12px;
		margin-bottom: 8px;
		font-size: 10px;
		flex-wrap: wrap;
	}

	.bb-agent {
		font-weight: 700;
		color: var(--terminal-green);
	}

	.bb-topic {
		color: var(--cyan-data);
	}

	.bb-time {
		color: var(--muted-foreground);
		font-family: 'JetBrains Mono', monospace;
	}

	.bb-content {
		font-size: 11px;
		line-height: 1.4;
	}

	/* Color classes */
	.red { color: var(--system-red) !important; }
	.yellow { color: var(--warning) !important; }
	.green { color: var(--terminal-green) !important; }
	.cyan { color: var(--cyan-data) !important; }

	/* Pulse dot */
	.pulse-dot {
		width: 10px;
		height: 10px;
		border-radius: 50%;
		display: inline-block;
	}

	.pulse-dot.big {
		width: 24px;
		height: 24px;
	}

	.pulse-dot.green {
		background: var(--terminal-green);
		box-shadow: 0 0 10px var(--terminal-green);
	}

	.pulse-dot.red {
		background: var(--system-red);
		box-shadow: 0 0 10px var(--system-red);
	}

	.pulse-brutal {
		animation: pulse 1s ease-in-out infinite;
	}

	.pulse-scan {
		animation: scan 2s ease-in-out infinite;
	}

	@keyframes pulse {
		0%, 100% { opacity: 1; }
		50% { opacity: 0.5; }
	}

	@keyframes scan {
		0%, 100% { box-shadow: 4px 4px 0 0 var(--system-red); }
		50% { box-shadow: 4px 4px 10px 0 var(--system-red); }
	}

	@keyframes pulse-border {
		0%, 100% { box-shadow: 6px 6px 0 0 var(--system-red); }
		50% { box-shadow: 6px 6px 15px 0 var(--system-red); }
	}

	.mt-16 { margin-top: 16px; }

	/* Log box styles from global */
	.log-box {
		font-family: 'JetBrains Mono', monospace;
		font-size: 11px;
		padding: 12px;
		border: 2px solid var(--border);
		background: rgba(240, 240, 240, 0.02);
		white-space: pre-wrap;
		word-break: break-word;
	}

	.stat-row {
		display: flex;
		justify-content: space-between;
		padding: 8px 0;
		border-bottom: 1px solid rgba(240, 240, 240, 0.1);
	}

	.stat-label {
		color: var(--muted-foreground);
		font-size: 11px;
		text-transform: uppercase;
	}

	.stat-value {
		font-family: 'JetBrains Mono', monospace;
		font-size: 12px;
		font-weight: 600;
	}

	/* Loading */
	.loading {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		min-height: 100vh;
		background: var(--void);
	}

	.loading-text {
		font-family: 'JetBrains Mono', monospace;
		font-size: 14px;
		color: var(--terminal-green);
		margin-bottom: 16px;
	}

	.loading-bar {
		width: 200px;
		height: 4px;
		background: var(--border);
		position: relative;
		overflow: hidden;
	}

	.loading-bar::after {
		content: '';
		position: absolute;
		top: 0;
		left: -100%;
		width: 50%;
		height: 100%;
		background: var(--terminal-green);
		animation: loading-slide 1s ease-in-out infinite;
	}

	@keyframes loading-slide {
		0% { left: -50%; }
		100% { left: 200%; }
	}

	.subtitle {
		font-family: 'JetBrains Mono', monospace;
		font-size: 10px;
		color: var(--muted-foreground);
	}
</style>
