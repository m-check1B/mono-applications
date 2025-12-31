<script lang="ts">
	import { onMount } from "svelte";

	interface LeaderboardEntry {
		id: string;
		lab: string | null;
		labName: string | null;
		role: string | null;
		points: number;
		rank: string;
		badge: string;
		achievements: string[];
		wins: number;
		losses: number;
		fitnessScore: number | null;
		tasksCompleted: number;
		tasksAttempted: number;
		successRate: number;
		avgQualityScore: number;
		coordinationScore: number;
		learningScore: number;
		totalTokens: number;
		lastActive: string | null;
	}

	interface Analytics {
		totalAgents: number;
		totalPoints: number;
		avgFitness: number;
		byLab: Record<string, { agents: number; points: number; avgFitness: number }>;
		byRole: Record<string, { agents: number; points: number }>;
	}

	interface RecentEvent {
		time: string;
		type: string;
		agent?: string;
		points?: number;
		reason?: string;
	}

	interface LeaderboardData {
		entries: LeaderboardEntry[];
		analytics: Analytics;
		governor: string | null;
		pendingChallenges: unknown[];
		recentEvents: RecentEvent[];
		season: string | null;
		lastUpdated: string;
	}

	let data = $state<LeaderboardData | null>(null);
	let loading = $state(true);
	let sortBy = $state<'points' | 'fitness' | 'tasks' | 'success'>('points');
	let filterLab = $state<string | null>(null);

	const LAB_COLORS: Record<string, string> = {
		CC: '#c9a227',
		OC: 'var(--terminal-green)',
		CX: 'var(--cyan-data)',
		GE: 'var(--warning)',
		GR: 'var(--system-red)'
	};

	async function fetchData() {
		loading = true;
		try {
			const res = await fetch('/api/leaderboard');
			if (res.ok) {
				data = await res.json();
			}
		} catch (e) {
			console.error('Failed to fetch leaderboard:', e);
		} finally {
			loading = false;
		}
	}

	function formatTime(isoTime: string | null): string {
		if (!isoTime) return '--';
		const date = new Date(isoTime);
		const now = new Date();
		const diffMs = now.getTime() - date.getTime();
		const diffMins = Math.floor(diffMs / 60000);
		const diffHours = Math.floor(diffMs / 3600000);
		const diffDays = Math.floor(diffMs / 86400000);

		if (diffMins < 60) return `${diffMins}m ago`;
		if (diffHours < 24) return `${diffHours}h ago`;
		return `${diffDays}d ago`;
	}

	function formatTokens(tokens: number): string {
		if (tokens >= 1000000) return `${(tokens / 1000000).toFixed(1)}M`;
		if (tokens >= 1000) return `${(tokens / 1000).toFixed(1)}K`;
		return tokens.toString();
	}

	function getMedalEmoji(index: number): string {
		if (index === 0) return '1ST';
		if (index === 1) return '2ND';
		if (index === 2) return '3RD';
		return `${index + 1}TH`;
	}

	function getFitnessColor(score: number | null): string {
		if (score === null) return 'var(--text-muted)';
		if (score >= 80) return 'var(--terminal-green)';
		if (score >= 60) return 'var(--cyan-data)';
		if (score >= 40) return 'var(--warning)';
		return 'var(--system-red)';
	}

	const sortedEntries = $derived(() => {
		if (!data) return [];
		let entries = [...data.entries];

		// Filter by lab if selected
		if (filterLab) {
			entries = entries.filter(e => e.lab === filterLab);
		}

		// Sort
		switch (sortBy) {
			case 'fitness':
				entries.sort((a, b) => (b.fitnessScore ?? 0) - (a.fitnessScore ?? 0));
				break;
			case 'tasks':
				entries.sort((a, b) => b.tasksCompleted - a.tasksCompleted);
				break;
			case 'success':
				entries.sort((a, b) => b.successRate - a.successRate);
				break;
			default:
				entries.sort((a, b) => b.points - a.points);
		}

		return entries;
	});

	const availableLabs = $derived(() => {
		if (!data) return [];
		const labs = new Set<string>();
		for (const entry of data.entries) {
			if (entry.lab) labs.add(entry.lab);
		}
		return Array.from(labs).sort();
	});

	onMount(() => {
		fetchData();
		const interval = setInterval(fetchData, 60000); // Refresh every minute
		return () => clearInterval(interval);
	});
</script>

<div class="page">
	<div class="page-header">
		<h2 class="glitch">Swarm Leaderboard // Agent Rankings</h2>
		<div class="header-controls">
			<button class="brutal-btn" onclick={fetchData} disabled={loading}>
				{loading ? 'SYNCING...' : 'REFRESH'}
			</button>
		</div>
	</div>

	{#if loading && !data}
		<div class="loading">SCANNING_AGENT_REGISTRY...</div>
	{:else if data}
		<!-- Season & Governor Info -->
		<div class="info-bar">
			<div class="info-item">
				<span class="info-label">SEASON</span>
				<span class="info-value">{data.season?.replace('week_', 'WEEK_') || 'ACTIVE'}</span>
			</div>
			{#if data.governor}
				<div class="info-item governor">
					<span class="info-label">GOVERNOR</span>
					<span class="info-value">{data.governor}</span>
				</div>
			{/if}
			<div class="info-item">
				<span class="info-label">UPDATED</span>
				<span class="info-value">{formatTime(data.lastUpdated)}</span>
			</div>
		</div>

		<!-- Analytics Summary -->
		<div class="analytics-grid">
			<div class="analytics-card">
				<div class="analytics-value">{data.analytics.totalAgents}</div>
				<div class="analytics-label">TOTAL_AGENTS</div>
			</div>
			<div class="analytics-card">
				<div class="analytics-value yellow">{data.analytics.totalPoints}</div>
				<div class="analytics-label">TOTAL_POINTS</div>
			</div>
			<div class="analytics-card">
				<div class="analytics-value cyan">{data.analytics.avgFitness.toFixed(1)}</div>
				<div class="analytics-label">AVG_FITNESS</div>
			</div>
			<div class="analytics-card">
				<div class="analytics-value">{Object.keys(data.analytics.byLab).length}</div>
				<div class="analytics-label">ACTIVE_LABS</div>
			</div>
		</div>

		<!-- Lab Breakdown -->
		{#if Object.keys(data.analytics.byLab).length > 0}
			<div class="card">
				<h2>LAB_PERFORMANCE // BY_UNIT</h2>
				<div class="lab-grid">
					{#each Object.entries(data.analytics.byLab).sort((a, b) => b[1].points - a[1].points) as [lab, labData]}
						<div
							class="lab-card"
							class:active={filterLab === lab}
							style="--lab-color: {LAB_COLORS[lab] || 'var(--terminal-green)'}"
							onclick={() => filterLab = filterLab === lab ? null : lab}
							role="button"
							tabindex="0"
							onkeydown={(e) => e.key === 'Enter' && (filterLab = filterLab === lab ? null : lab)}
						>
							<div class="lab-header">
								<span class="lab-badge" data-lab={lab}>{lab}</span>
								<span class="lab-name">{labData.agents} AGENTS</span>
							</div>
							<div class="lab-stats">
								<div class="lab-stat">
									<span class="lab-stat-value yellow">{labData.points}</span>
									<span class="lab-stat-label">POINTS</span>
								</div>
								<div class="lab-stat">
									<span class="lab-stat-value" style="color: {getFitnessColor(labData.avgFitness)}">{labData.avgFitness.toFixed(1)}</span>
									<span class="lab-stat-label">FITNESS</span>
								</div>
							</div>
						</div>
					{/each}
				</div>
			</div>
		{/if}

		<!-- Sort Controls -->
		<div class="controls-bar">
			<div class="sort-controls">
				<span class="control-label">SORT_BY:</span>
				<button class="sort-btn" class:active={sortBy === 'points'} onclick={() => sortBy = 'points'}>POINTS</button>
				<button class="sort-btn" class:active={sortBy === 'fitness'} onclick={() => sortBy = 'fitness'}>FITNESS</button>
				<button class="sort-btn" class:active={sortBy === 'tasks'} onclick={() => sortBy = 'tasks'}>TASKS</button>
				<button class="sort-btn" class:active={sortBy === 'success'} onclick={() => sortBy = 'success'}>SUCCESS_RATE</button>
			</div>
			{#if filterLab}
				<button class="brutal-btn" onclick={() => filterLab = null}>CLEAR_FILTER: {filterLab}</button>
			{/if}
		</div>

		<!-- Leaderboard Table -->
		<div class="card leaderboard-card">
			<h2>AGENT_RANKINGS // {sortedEntries().length} ENTRIES {filterLab ? `[${filterLab}]` : ''}</h2>

			{#if sortedEntries().length === 0}
				<p class="hint">No agents found. The arena is empty.</p>
			{:else}
				<div class="leaderboard-table">
					<div class="leaderboard-row header">
						<span class="col-rank">#</span>
						<span class="col-agent">AGENT</span>
						<span class="col-lab">LAB</span>
						<span class="col-role">ROLE</span>
						<span class="col-points">POINTS</span>
						<span class="col-fitness">FITNESS</span>
						<span class="col-tasks">TASKS</span>
						<span class="col-success">SUCCESS</span>
						<span class="col-tokens">TOKENS</span>
						<span class="col-active">LAST_ACTIVE</span>
					</div>
					{#each sortedEntries() as entry, i}
						<div
							class="leaderboard-row"
							class:top-3={i < 3}
							class:first={i === 0}
							style="--lab-color: {LAB_COLORS[entry.lab || ''] || 'var(--terminal-green)'}"
						>
							<span class="col-rank">
								<span class="rank-badge" class:gold={i === 0} class:silver={i === 1} class:bronze={i === 2}>{getMedalEmoji(i)}</span>
							</span>
							<span class="col-agent">
								<span class="agent-badge">{entry.badge}</span>
								<span class="agent-id" style="color: var(--lab-color)">{entry.id}</span>
							</span>
							<span class="col-lab">
								<span class="lab-badge-small" data-lab={entry.lab}>{entry.lab || '--'}</span>
							</span>
							<span class="col-role">{entry.role?.toUpperCase() || '--'}</span>
							<span class="col-points yellow">{entry.points}</span>
							<span class="col-fitness" style="color: {getFitnessColor(entry.fitnessScore)}">
								{entry.fitnessScore !== null ? entry.fitnessScore.toFixed(1) : '--'}
							</span>
							<span class="col-tasks">
								<span class="tasks-completed">{entry.tasksCompleted}</span>
								<span class="tasks-sep">/</span>
								<span class="tasks-attempted">{entry.tasksAttempted}</span>
							</span>
							<span class="col-success" class:high={entry.successRate >= 80} class:medium={entry.successRate >= 50 && entry.successRate < 80} class:low={entry.successRate < 50}>
								{entry.successRate.toFixed(0)}%
							</span>
							<span class="col-tokens">{formatTokens(entry.totalTokens)}</span>
							<span class="col-active">{formatTime(entry.lastActive)}</span>
						</div>
					{/each}
				</div>
			{/if}
		</div>

		<!-- Recent Events -->
		{#if data.recentEvents.length > 0}
			<div class="card">
				<h2>RECENT_EVENTS // ACTIVITY_LOG</h2>
				<div class="events-list">
					{#each data.recentEvents as event}
						<div class="event-item" data-type={event.type}>
							<span class="event-time">[{event.time.slice(11, 19)}]</span>
							<span class="event-type">{event.type.toUpperCase()}</span>
							{#if event.agent}
								<span class="event-agent">{event.agent}</span>
							{/if}
							{#if event.points}
								<span class="event-points" class:positive={event.points > 0} class:negative={event.points < 0}>
									{event.points > 0 ? '+' : ''}{event.points} PTS
								</span>
							{/if}
							{#if event.reason}
								<span class="event-reason">{event.reason}</span>
							{/if}
						</div>
					{/each}
				</div>
			</div>
		{/if}
	{/if}
</div>

<style>
	.page {
		display: flex;
		flex-direction: column;
		gap: 24px;
	}

	.page-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 8px;
		border-bottom: 2px solid var(--border);
		padding-bottom: 16px;
	}

	.header-controls {
		display: flex;
		gap: 12px;
		align-items: center;
	}

	.info-bar {
		display: flex;
		flex-wrap: wrap;
		gap: 16px;
		padding: 12px 16px;
		background: hsl(var(--card));
		border: 2px solid hsl(var(--border));
		box-shadow: 4px 4px 0 0 hsl(var(--border));
	}

	.info-item {
		display: flex;
		align-items: center;
		gap: 8px;
	}

	.info-item.governor {
		border-left: 3px solid var(--warning);
		padding-left: 12px;
	}

	.info-label {
		font-size: 10px;
		color: hsl(var(--muted-foreground));
		text-transform: uppercase;
	}

	.info-value {
		font-size: 12px;
		font-weight: 700;
		color: var(--terminal-green);
		font-family: 'JetBrains Mono', monospace;
	}

	.analytics-grid {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
		gap: 16px;
	}

	.analytics-card {
		background: hsl(var(--card));
		border: 2px solid hsl(var(--border));
		padding: 20px;
		text-align: center;
		box-shadow: 4px 4px 0 0 hsl(var(--border));
		transition: all 0.1s ease;
	}

	.analytics-card:hover {
		transform: translate(-2px, -2px);
		box-shadow: 6px 6px 0 0 var(--terminal-green);
		border-color: var(--terminal-green);
	}

	.analytics-value {
		font-family: 'Archivo Black', Impact, sans-serif;
		font-size: 28px;
		color: var(--terminal-green);
	}

	.analytics-value.yellow { color: var(--warning); }
	.analytics-value.cyan { color: var(--cyan-data); }

	.analytics-label {
		font-size: 10px;
		color: hsl(var(--muted-foreground));
		text-transform: uppercase;
		margin-top: 8px;
		letter-spacing: 0.1em;
	}

	.lab-grid {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
		gap: 16px;
	}

	.lab-card {
		background: hsl(var(--card));
		border: 2px solid hsl(var(--border));
		padding: 16px;
		cursor: pointer;
		transition: all 0.1s ease;
		box-shadow: 4px 4px 0 0 hsl(var(--border));
	}

	.lab-card:hover, .lab-card.active {
		border-color: var(--lab-color, var(--terminal-green));
		box-shadow: 4px 4px 0 0 var(--lab-color, var(--terminal-green));
		transform: translate(-2px, -2px);
	}

	.lab-card.active {
		background: hsla(var(--foreground) / 0.05);
	}

	.lab-header {
		display: flex;
		align-items: center;
		gap: 12px;
		margin-bottom: 12px;
	}

	.lab-stats {
		display: flex;
		justify-content: space-around;
	}

	.lab-stat {
		text-align: center;
	}

	.lab-stat-value {
		font-family: 'JetBrains Mono', monospace;
		font-size: 16px;
		font-weight: 700;
	}

	.lab-stat-label {
		font-size: 9px;
		color: hsl(var(--muted-foreground));
		text-transform: uppercase;
	}

	.controls-bar {
		display: flex;
		flex-wrap: wrap;
		justify-content: space-between;
		align-items: center;
		gap: 16px;
		padding: 12px 16px;
		background: hsl(var(--card));
		border: 2px solid hsl(var(--border));
	}

	.sort-controls {
		display: flex;
		align-items: center;
		gap: 8px;
		flex-wrap: wrap;
	}

	.control-label {
		font-size: 10px;
		color: hsl(var(--muted-foreground));
		text-transform: uppercase;
	}

	.sort-btn {
		padding: 6px 12px;
		font-family: 'JetBrains Mono', monospace;
		font-size: 10px;
		text-transform: uppercase;
		background: transparent;
		color: hsl(var(--muted-foreground));
		border: 2px solid hsl(var(--border));
		cursor: pointer;
		transition: all 0.1s ease;
	}

	.sort-btn:hover {
		border-color: var(--terminal-green);
		color: var(--terminal-green);
	}

	.sort-btn.active {
		background: var(--terminal-green);
		color: var(--void);
		border-color: var(--terminal-green);
	}

	.leaderboard-card {
		overflow-x: auto;
	}

	.leaderboard-table {
		display: flex;
		flex-direction: column;
		gap: 4px;
		min-width: 1000px;
	}

	.leaderboard-row {
		display: grid;
		grid-template-columns: 60px 2fr 70px 100px 80px 80px 100px 80px 80px 100px;
		gap: 12px;
		padding: 12px;
		align-items: center;
		background: hsl(var(--card));
		border: 2px solid hsl(var(--border));
		font-size: 11px;
		transition: all 0.1s ease;
	}

	.leaderboard-row:hover:not(.header) {
		transform: translate(-2px, -2px);
		box-shadow: 4px 4px 0 0 var(--lab-color, var(--terminal-green));
		border-color: var(--lab-color, var(--terminal-green));
	}

	.leaderboard-row.header {
		background: transparent;
		border: none;
		color: hsl(var(--muted-foreground));
		font-size: 10px;
		text-transform: uppercase;
		padding-bottom: 8px;
		border-bottom: 2px solid hsl(var(--border));
	}

	.leaderboard-row.top-3 {
		border-width: 3px;
	}

	.leaderboard-row.first {
		background: hsla(var(--foreground) / 0.05);
		border-color: var(--warning);
		box-shadow: 4px 4px 0 0 var(--warning);
	}

	.rank-badge {
		font-family: 'Archivo Black', Impact, sans-serif;
		font-size: 12px;
		padding: 4px 8px;
		border: 2px solid hsl(var(--muted-foreground));
		text-align: center;
	}

	.rank-badge.gold {
		border-color: #c9a227;
		color: #c9a227;
		background: rgba(201, 162, 39, 0.1);
	}

	.rank-badge.silver {
		border-color: #888;
		color: #888;
		background: rgba(136, 136, 136, 0.1);
	}

	.rank-badge.bronze {
		border-color: #cd7f32;
		color: #cd7f32;
		background: rgba(205, 127, 50, 0.1);
	}

	.col-agent {
		display: flex;
		align-items: center;
		gap: 8px;
	}

	.agent-badge {
		font-size: 16px;
		min-width: 24px;
	}

	.agent-id {
		font-weight: 700;
		text-transform: uppercase;
		white-space: nowrap;
		overflow: hidden;
		text-overflow: ellipsis;
	}

	.lab-badge-small {
		font-size: 9px;
		font-weight: 700;
		padding: 2px 6px;
		border: 2px solid hsl(var(--muted-foreground));
		text-align: center;
	}

	.lab-badge-small[data-lab="CC"] { border-color: #c9a227; color: #c9a227; }
	.lab-badge-small[data-lab="OC"] { border-color: var(--terminal-green); color: var(--terminal-green); }
	.lab-badge-small[data-lab="CX"] { border-color: var(--cyan-data); color: var(--cyan-data); }
	.lab-badge-small[data-lab="GE"] { border-color: var(--warning); color: var(--warning); }
	.lab-badge-small[data-lab="GR"] { border-color: var(--system-red); color: var(--system-red); }

	.col-role {
		color: hsl(var(--muted-foreground));
		text-transform: uppercase;
	}

	.col-points {
		font-family: 'JetBrains Mono', monospace;
		font-weight: 700;
	}

	.col-fitness {
		font-family: 'JetBrains Mono', monospace;
		font-weight: 700;
	}

	.col-tasks {
		font-family: 'JetBrains Mono', monospace;
	}

	.tasks-completed {
		color: var(--terminal-green);
		font-weight: 700;
	}

	.tasks-sep {
		color: hsl(var(--muted-foreground));
		margin: 0 2px;
	}

	.tasks-attempted {
		color: hsl(var(--muted-foreground));
	}

	.col-success {
		font-family: 'JetBrains Mono', monospace;
		font-weight: 700;
	}

	.col-success.high { color: var(--terminal-green); }
	.col-success.medium { color: var(--warning); }
	.col-success.low { color: var(--system-red); }

	.col-tokens {
		font-family: 'JetBrains Mono', monospace;
		color: hsl(var(--muted-foreground));
	}

	.col-active {
		font-family: 'JetBrains Mono', monospace;
		color: hsl(var(--muted-foreground));
		font-size: 10px;
	}

	.yellow { color: var(--warning); }

	.events-list {
		display: flex;
		flex-direction: column;
		gap: 6px;
		max-height: 300px;
		overflow-y: auto;
	}

	.event-item {
		display: flex;
		flex-wrap: wrap;
		gap: 12px;
		padding: 10px;
		background: hsl(var(--background));
		border: 2px solid hsl(var(--border));
		font-size: 11px;
		align-items: center;
	}

	.event-item:hover {
		border-color: var(--terminal-green);
	}

	.event-time {
		color: hsl(var(--muted-foreground));
		font-family: 'JetBrains Mono', monospace;
	}

	.event-type {
		padding: 2px 6px;
		border: 2px solid hsl(var(--muted-foreground));
		font-weight: 700;
		text-transform: uppercase;
	}

	.event-item[data-type="points"] .event-type {
		border-color: var(--warning);
		color: var(--warning);
	}

	.event-item[data-type="achievement"] .event-type {
		border-color: var(--cyan-data);
		color: var(--cyan-data);
	}

	.event-item[data-type="season_reset"] .event-type {
		border-color: var(--system-red);
		color: var(--system-red);
	}

	.event-agent {
		color: var(--terminal-green);
		font-weight: 700;
		text-transform: uppercase;
	}

	.event-points {
		font-family: 'JetBrains Mono', monospace;
		font-weight: 700;
	}

	.event-points.positive { color: var(--terminal-green); }
	.event-points.negative { color: var(--system-red); }

	.event-reason {
		color: hsl(var(--muted-foreground));
		flex: 1;
	}

	.hint {
		color: hsl(var(--muted-foreground));
		font-size: 11px;
		text-transform: uppercase;
		padding: 20px;
		text-align: center;
	}

	.loading {
		display: flex;
		align-items: center;
		justify-content: center;
		padding: 60px;
		color: var(--terminal-green);
		font-family: 'JetBrains Mono', monospace;
		text-transform: uppercase;
	}
</style>
