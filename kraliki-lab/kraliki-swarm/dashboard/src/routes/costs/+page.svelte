<script lang="ts">
	import { onMount } from 'svelte';

	interface CostAnalytics {
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
			efficiency: number | null;
		}>;
		hourly_costs: Array<{ hour: string; cost: number; agents: number }>;
	}

	let data = $state<CostAnalytics | null>(null);
	let loading = $state(true);
	let error = $state<string | null>(null);

	async function loadCosts() {
		loading = true;
		error = null;
		try {
			const response = await fetch('/api/costs');
			if (!response.ok) throw new Error('Failed to load cost data');
			data = await response.json();
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to load costs';
		} finally {
			loading = false;
		}
	}

	function formatCost(cost: number): string {
		return `$${cost.toFixed(2)}`;
	}

	function formatTokens(tokens: number): string {
		if (tokens >= 1000000) return `${(tokens / 1000000).toFixed(1)}M`;
		if (tokens >= 1000) return `${(tokens / 1000).toFixed(1)}K`;
		return tokens.toString();
	}

	function formatDuration(ms: number): string {
		const minutes = Math.floor(ms / 60000);
		if (minutes >= 60) {
			const hours = Math.floor(minutes / 60);
			const mins = minutes % 60;
			return `${hours}h ${mins}m`;
		}
		return `${minutes}m`;
	}

	function getCliColor(cli: string): string {
		const colors: Record<string, string> = {
			claude: '#33ff00',
			opencode: '#00d4ff',
			codex: '#9d4edd',
			gemini: '#ff9500',
			grok: '#ff4444'
		};
		return colors[cli] || '#6b7280';
	}

	function getModelShortName(model: string): string {
		if (model.includes('opus')) return 'OPUS';
		if (model.includes('sonnet')) return 'SONNET';
		if (model.includes('haiku')) return 'HAIKU';
		if (model.includes('gemini')) return 'GEMINI';
		return model.toUpperCase().slice(0, 12);
	}

	onMount(() => {
		loadCosts();
		const interval = setInterval(loadCosts, 60000); // Refresh every minute
		return () => clearInterval(interval);
	});

	const maxHourlyCost = $derived(
		data?.hourly_costs.reduce((max, h) => Math.max(max, h.cost), 0) || 1
	);
</script>

<div class="page">
	<div class="page-header">
		<h2 class="glitch">Agent Cost Analytics // Claude Code Agents Only</h2>
		<div class="controls">
			<button class="brutal-btn" onclick={loadCosts} disabled={loading}>
				{loading ? 'LOADING...' : 'REFRESH'}
			</button>
		</div>
	</div>

	<div class="tracking-notice">
		<span class="notice-icon">ℹ️</span>
		<div class="notice-content">
			<strong>TRACKING SCOPE:</strong> This dashboard tracks costs from Claude Code agents spawned via the Task tool.
			Interactive CLI usage (claude, codex, gemini, opencode commands) is not currently tracked.
		</div>
	</div>

	{#if loading && !data}
		<div class="loading-state">
			<span class="loading-text">CALCULATING_EXPENDITURES...</span>
		</div>
	{:else if error}
		<div class="error-state">
			<span class="error-text">ERROR: {error}</span>
		</div>
	{:else if data}
		<!-- Summary Cards -->
		<div class="stats-grid">
			<div class="stat-card highlight">
				<span class="stat-value">{formatCost(data.summary.total_cost_today)}</span>
				<span class="stat-label">AGENT COST TODAY</span>
			</div>
			<div class="stat-card">
				<span class="stat-value">{formatCost(data.summary.total_cost_week)}</span>
				<span class="stat-label">7-DAY AGENT COST</span>
			</div>
			<div class="stat-card">
				<span class="stat-value">{formatTokens(data.summary.total_tokens_today)}</span>
				<span class="stat-label">AGENT TOKENS TODAY</span>
			</div>
			<div class="stat-card">
				<span class="stat-value green">{data.summary.total_agents_today}</span>
				<span class="stat-label">AGENTS RUN TODAY</span>
			</div>
			<div class="stat-card">
				<span class="stat-value cyan">{formatCost(data.summary.avg_cost_per_agent)}</span>
				<span class="stat-label">AVG COST/AGENT</span>
			</div>
		</div>

		<div class="grid-2">
			<!-- Cost by CLI -->
			<div class="card">
				<h3>AGENT COST BY CLI // TODAY</h3>
				<div class="cli-bars">
					{#each Object.entries(data.by_cli).sort((a, b) => b[1].cost - a[1].cost) as [cli, stats]}
						{@const maxCost = Math.max(...Object.values(data.by_cli).map(s => s.cost)) || 1}
						<div class="cli-bar">
							<div class="cli-info">
								<span class="cli-name" style="color: {getCliColor(cli)}">{cli.toUpperCase()}</span>
								<span class="cli-stats">{stats.agents} agents / {formatTokens(stats.tokens)} tokens</span>
							</div>
							<div class="bar-container">
								<div
									class="bar-fill"
									style="width: {(stats.cost / maxCost) * 100}%; background: {getCliColor(cli)}"
								></div>
							</div>
							<span class="cli-cost">{formatCost(stats.cost)}</span>
						</div>
					{/each}
				</div>
			</div>

			<!-- Cost by Model -->
			<div class="card">
				<h3>AGENT COST BY MODEL // TODAY</h3>
				<div class="model-list">
					{#each Object.entries(data.by_model).sort((a, b) => b[1].cost - a[1].cost) as [model, stats]}
						<div class="model-item">
							<div class="model-header">
								<span class="model-name">{getModelShortName(model)}</span>
								<span class="model-cost">{formatCost(stats.cost)}</span>
							</div>
							<div class="model-stats">
								<span>{stats.requests} requests</span>
								<span>In: {formatTokens(stats.input_tokens)}</span>
								<span>Out: {formatTokens(stats.output_tokens)}</span>
							</div>
						</div>
					{/each}
				</div>
			</div>
		</div>

		<!-- Hourly Cost Chart -->
		{#if data.hourly_costs.length > 0}
			<div class="card">
				<h3>HOURLY COST DISTRIBUTION // TODAY</h3>
				<div class="hourly-chart">
					{#each data.hourly_costs as hour}
						<div class="hour-bar">
							<div class="hour-fill" style="height: {(hour.cost / maxHourlyCost) * 100}%"></div>
							<span class="hour-label">{hour.hour.slice(0, 2)}</span>
							<span class="hour-value">{formatCost(hour.cost)}</span>
						</div>
					{/each}
				</div>
			</div>
		{/if}

		<!-- Top Agents by Cost -->
		{#if data.top_agents.length > 0}
			<div class="card">
				<h3>TOP AGENTS BY COST // TODAY</h3>
				<p class="hint">Efficiency = points earned per dollar spent (higher is better)</p>
				<div class="agent-table">
					<div class="agent-row header">
						<span>AGENT</span>
						<span>CLI</span>
						<span>COST</span>
						<span>DURATION</span>
						<span>POINTS</span>
						<span>EFFICIENCY</span>
					</div>
					{#each data.top_agents as agent}
						<div class="agent-row">
							<span class="agent-id">{agent.id}</span>
							<span class="agent-cli" style="color: {getCliColor(agent.cli || 'unknown')}">{(agent.cli || 'UNKNOWN').toUpperCase()}</span>
							<span class="agent-cost">{formatCost(agent.cost)}</span>
							<span class="agent-duration">{formatDuration(agent.duration_ms)}</span>
							<span class="agent-points" class:has-points={agent.points !== null}>{agent.points ?? '--'}</span>
							<span class="agent-efficiency" class:good={agent.efficiency && agent.efficiency > 50} class:bad={agent.efficiency && agent.efficiency < 10}>
								{agent.efficiency !== null ? `${agent.efficiency} pts/$` : '--'}
							</span>
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
		border-bottom: 2px solid var(--border);
		padding-bottom: 16px;
	}

	.controls {
		display: flex;
		gap: 12px;
	}

	.tracking-notice {
		display: flex;
		gap: 12px;
		align-items: flex-start;
		padding: 16px;
		background: rgba(255, 149, 0, 0.1);
		border: 2px solid var(--warning);
		box-shadow: 4px 4px 0 0 var(--warning);
		margin-bottom: 8px;
	}

	.notice-icon {
		font-size: 20px;
		line-height: 1;
	}

	.notice-content {
		font-family: 'JetBrains Mono', monospace;
		font-size: 11px;
		color: var(--text-main);
		line-height: 1.5;
	}

	.notice-content strong {
		color: var(--warning);
		text-transform: uppercase;
		letter-spacing: 0.05em;
	}

	.stats-grid {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
		gap: 16px;
	}

	.stat-card {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 8px;
		padding: 20px 16px;
		background: var(--surface);
		border: 2px solid var(--border);
		box-shadow: 4px 4px 0 0 var(--border);
	}

	.stat-card.highlight {
		border-color: var(--terminal-green);
		box-shadow: 4px 4px 0 0 var(--terminal-green);
	}

	.stat-value {
		font-family: 'JetBrains Mono', monospace;
		font-size: 28px;
		font-weight: 700;
		color: var(--text-main);
	}

	.stat-value.green { color: var(--terminal-green); }
	.stat-value.cyan { color: var(--cyan-data); }

	.stat-label {
		font-family: 'JetBrains Mono', monospace;
		font-size: 9px;
		text-transform: uppercase;
		color: var(--text-muted);
		letter-spacing: 0.1em;
	}

	.grid-2 {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
		gap: 24px;
	}

	.card {
		padding: 20px;
		background: var(--surface);
		border: 2px solid var(--border);
		box-shadow: 4px 4px 0 0 var(--border);
	}

	.card h3 {
		font-family: 'JetBrains Mono', monospace;
		font-size: 12px;
		text-transform: uppercase;
		color: var(--text-muted);
		margin-bottom: 16px;
		letter-spacing: 0.1em;
	}

	.hint {
		font-size: 10px;
		color: var(--text-muted);
		margin-bottom: 16px;
		text-transform: uppercase;
	}

	.hint::before {
		content: '>>';
		color: var(--terminal-green);
		margin-right: 8px;
	}

	/* CLI Bars */
	.cli-bars {
		display: flex;
		flex-direction: column;
		gap: 12px;
	}

	.cli-bar {
		display: grid;
		grid-template-columns: 1fr 2fr 80px;
		gap: 12px;
		align-items: center;
	}

	.cli-info {
		display: flex;
		flex-direction: column;
		gap: 2px;
	}

	.cli-name {
		font-family: 'JetBrains Mono', monospace;
		font-size: 12px;
		font-weight: 700;
	}

	.cli-stats {
		font-family: 'JetBrains Mono', monospace;
		font-size: 9px;
		color: var(--text-muted);
	}

	.bar-container {
		height: 16px;
		background: var(--border);
		border-radius: 0;
	}

	.bar-fill {
		height: 100%;
		transition: width 0.3s ease;
	}

	.cli-cost {
		font-family: 'JetBrains Mono', monospace;
		font-size: 12px;
		font-weight: 700;
		text-align: right;
		color: var(--terminal-green);
	}

	/* Model List */
	.model-list {
		display: flex;
		flex-direction: column;
		gap: 12px;
	}

	.model-item {
		padding: 12px;
		background: rgba(0, 0, 0, 0.3);
		border: 1px solid var(--border);
	}

	.model-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 8px;
	}

	.model-name {
		font-family: 'JetBrains Mono', monospace;
		font-size: 12px;
		font-weight: 700;
		color: var(--cyan-data);
	}

	.model-cost {
		font-family: 'JetBrains Mono', monospace;
		font-size: 12px;
		font-weight: 700;
		color: var(--terminal-green);
	}

	.model-stats {
		display: flex;
		gap: 16px;
		font-family: 'JetBrains Mono', monospace;
		font-size: 10px;
		color: var(--text-muted);
	}

	/* Hourly Chart */
	.hourly-chart {
		display: flex;
		align-items: flex-end;
		gap: 4px;
		height: 150px;
		padding-top: 20px;
	}

	.hour-bar {
		flex: 1;
		display: flex;
		flex-direction: column;
		align-items: center;
		height: 100%;
		position: relative;
	}

	.hour-fill {
		width: 100%;
		background: var(--terminal-green);
		position: absolute;
		bottom: 24px;
		transition: height 0.3s ease;
	}

	.hour-label {
		font-family: 'JetBrains Mono', monospace;
		font-size: 9px;
		color: var(--text-muted);
		position: absolute;
		bottom: 0;
	}

	.hour-value {
		font-family: 'JetBrains Mono', monospace;
		font-size: 8px;
		color: var(--terminal-green);
		position: absolute;
		top: 0;
		opacity: 0;
		transition: opacity 0.2s ease;
	}

	.hour-bar:hover .hour-value {
		opacity: 1;
	}

	/* Agent Table */
	.agent-table {
		font-family: 'JetBrains Mono', monospace;
		font-size: 11px;
	}

	.agent-row {
		display: grid;
		grid-template-columns: 2fr 1fr 1fr 1fr 1fr 1fr;
		gap: 12px;
		padding: 10px;
		border-bottom: 1px solid var(--border);
		align-items: center;
	}

	.agent-row.header {
		font-weight: 700;
		color: var(--text-muted);
		text-transform: uppercase;
		font-size: 10px;
		border-bottom: 2px solid var(--border);
	}

	.agent-id {
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
	}

	.agent-cost {
		color: var(--terminal-green);
	}

	.agent-points.has-points {
		color: var(--warning);
	}

	.agent-efficiency.good {
		color: var(--terminal-green);
	}

	.agent-efficiency.bad {
		color: var(--system-red);
	}

	/* Loading/Error States */
	.loading-state, .error-state {
		display: flex;
		justify-content: center;
		align-items: center;
		padding: 100px;
	}

	.loading-text {
		font-family: 'JetBrains Mono', monospace;
		font-size: 12px;
		color: var(--terminal-green);
		animation: blink 1s ease-in-out infinite;
	}

	.error-text {
		font-family: 'JetBrains Mono', monospace;
		font-size: 12px;
		color: var(--system-red);
	}

	@keyframes blink {
		0%, 100% { opacity: 1; }
		50% { opacity: 0.5; }
	}
</style>
