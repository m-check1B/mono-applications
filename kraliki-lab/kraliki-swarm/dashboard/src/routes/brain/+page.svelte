<script lang="ts">
	import { onMount } from 'svelte';
	import { isReadOnly } from '$lib/stores/mode';

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
		period: string;
		period_dates: string;
		strategic_focus: string;
		streams: Record<string, StreamConfig>;
	}

	interface HumanBlocker {
		id: string;
		task: string;
		priority: string;
	}

	interface ME90Data {
		start: string;
		end: string;
		totalDays: number;
		daysPassed: number;
		daysRemaining: number;
		progress: string;
	}

	interface StrategyDoc {
		id: string;
		title: string;
		path: string;
		type: 'decision' | 'plan' | 'roadmap';
		date: string;
		status?: string;
		summary?: string;
		tasks?: { id: string; title: string; status: string }[];
	}

	let master = $state<MasterPlan | null>(null);
	let me90 = $state<ME90Data | null>(null);
	let blockers = $state<HumanBlocker[]>([]);
	let strategies = $state<StrategyDoc[]>([]);
	let strategyCounts = $state<{ decision: number; plan: number; roadmap: number }>({ decision: 0, plan: 0, roadmap: 0 });
	let loading = $state(true);
	let sendingToFocus = $state<string | null>(null);
	let strategyFilter = $state<string>('all');

	const streamColors: Record<string, string> = {
		business: 'var(--terminal-green)',
		marketing: 'var(--cyan-data, #00d4ff)',
		apps: 'var(--warning, #ffaa00)',
		infra: '#888'
	};

	let appDomain = $state('verduona.dev');

	const apps = $derived([
		{ name: 'Focus by Kraliki', url: `https://focus.${appDomain}`, status: appDomain === 'verduona.dev' ? 'beta' : 'prod' },
		{ name: 'Voice by Kraliki', url: `https://voice.${appDomain}`, status: appDomain === 'verduona.dev' ? 'beta' : 'prod' },
		{ name: 'Speak by Kraliki', url: `https://speak.${appDomain}`, status: appDomain === 'verduona.dev' ? 'beta' : 'prod' },
		{ name: 'Lab by Kraliki', url: `https://lab.${appDomain}`, status: appDomain === 'verduona.dev' ? 'beta' : 'prod' },
		{ name: 'Learn by Kraliki', url: `https://learn.${appDomain}`, status: appDomain === 'verduona.dev' ? 'dev' : 'prod' },
	]);

	const paymentLinks = [
		{ product: 'Lab by Kraliki Pro', price: '299', url: 'https://buy.stripe.com/7sY9AUbfx0drdPRcp96J200' },
		{ product: 'Workshop Early Bird', price: '149', url: 'https://buy.stripe.com/5kQ00k3N58JX8vx88T6J201' },
		{ product: 'Workshop Standard', price: '249', url: 'https://buy.stripe.com/14AdRadnF6BP27960L6J202' },
		{ product: 'Consulting Diagnostic', price: '999', url: 'https://buy.stripe.com/6oUaEY83lf8l9zB3SD6J203' },
	];

	async function fetchData() {
		loading = true;
		try {
			// Fetch brain data from brain-2026
			const brainRes = await fetch('/api/brain');
			if (brainRes.ok) {
				const data = await brainRes.json();
				master = data.master;
				me90 = data.me90;
			}

			// Fetch human blockers
			const blockersRes = await fetch('/api/human-blockers');
			if (blockersRes.ok) {
				const data = await blockersRes.json();
				blockers = data.blockers?.filter((b: HumanBlocker) =>
					b.priority === 'CRITICAL' || b.priority === 'HIGH'
				) || [];
			}

			// Fetch strategies
			const strategyRes = await fetch('/api/brain/strategy');
			if (strategyRes.ok) {
				const data = await strategyRes.json();
				strategies = data.strategies || [];
				strategyCounts = data.types || { decision: 0, plan: 0, roadmap: 0 };
			}
		} catch (e) {
			console.error('Failed to fetch brain data:', e);
		} finally {
			loading = false;
		}
	}

	async function sendToFocus(strategy: StrategyDoc) {
		sendingToFocus = strategy.id;
		try {
			const res = await fetch('/api/brain/strategy', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({
					strategyId: strategy.id,
					strategyPath: strategy.path
				})
			});

			if (res.ok) {
				const result = await res.json();
				alert(`Created: ${result.message}`);
			} else {
				const error = await res.json();
				alert(`Failed: ${error.error}`);
			}
		} catch (e) {
			console.error('Error sending to Focus:', e);
			alert('Error connecting to Focus');
		} finally {
			sendingToFocus = null;
		}
	}

	const filteredStrategies = $derived(
		strategyFilter === 'all'
			? strategies.slice(0, 10)
			: strategies.filter(s => s.type === strategyFilter).slice(0, 10)
	);

	onMount(() => {
		appDomain = window.location.hostname.endsWith('verduona.dev') ? 'verduona.dev' : 'kraliki.com';
		fetchData();
		const interval = setInterval(fetchData, 120000); // 2 min refresh
		return () => clearInterval(interval);
	});

	const streams = $derived(
		master?.streams
			? Object.entries(master.streams).map(([name, config]) => ({
				name: name.toUpperCase(),
				attention: parseInt(config.attention) || 0,
				status: config.status,
				color: streamColors[name] || '#888'
			}))
			: []
	);
</script>

<div class="page">
	<div class="page-header">
		<h2 class="glitch">Brain // Strategic Command</h2>
		<div style="display: flex; gap: 12px; align-items: center;">
			{#if me90}
				<span class="me90-badge">ME-90: DAY {me90.daysPassed} / {me90.totalDays}</span>
			{/if}
			<button class="brutal-btn" onclick={fetchData} disabled={loading}>
				{loading ? 'LOADING...' : 'REFRESH'}
			</button>
		</div>
	</div>

	{#if loading && !master}
		<div class="loading">LOADING_STRATEGIC_DATA...</div>
	{:else}
		<div class="brain-grid">
			<!-- Strategic Focus -->
			{#if master}
				<div class="card span-2 focus-card">
					<h3>STRATEGIC_FOCUS</h3>
					<div class="focus-text">{master.strategic_focus}</div>
				</div>
			{/if}

			<!-- ME-90 Goal Tracker -->
			<div class="card span-2">
				<h3>ME-90 PROGRESS // TARGET: 3-5K MRR</h3>
				<div class="progress-container">
					<div class="progress-bar" style="width: {me90?.progress || 0}%"></div>
					<span class="progress-label">{me90?.progress || 0}% ({me90?.daysRemaining || '?'} DAYS LEFT)</span>
				</div>
				<div class="goal-stats">
					<div class="goal-stat">
						<span class="stat-label">START</span>
						<span class="stat-value">{me90?.start || '2025-12-02'}</span>
					</div>
					<div class="goal-stat">
						<span class="stat-label">END</span>
						<span class="stat-value">{me90?.end || '2026-03-01'}</span>
					</div>
					<div class="goal-stat">
						<span class="stat-label">TARGET_MRR</span>
						<span class="stat-value green">3,000 - 5,000</span>
					</div>
				</div>
			</div>

		<!-- Strategic Attention Allocation -->
		<div class="card">
			<h3>ATTENTION_ALLOCATION</h3>
			<div class="streams-list">
				{#each streams as stream}
					<div class="stream-item">
						<div class="stream-header">
							<span class="stream-name">{stream.name}</span>
							<span class="stream-percent">{stream.attention}%</span>
						</div>
						<div class="stream-bar-bg">
							<div class="stream-bar" style="width: {stream.attention}%; background: {stream.color}"></div>
						</div>
					</div>
				{/each}
			</div>
		</div>

		<!-- Revenue Links -->
		<div class="card">
			<h3>ACTIVE_PAYMENT_LINKS</h3>
			<div class="payment-list">
				{#each paymentLinks as link}
					<a href={link.url} target="_blank" class="payment-item">
						<span class="payment-name">{link.product}</span>
						<span class="payment-price">{link.price}</span>
					</a>
				{/each}
			</div>
		</div>

		<!-- Critical Blockers -->
		<div class="card" class:alert={blockers.length > 0}>
			<h3 class:red={blockers.length > 0}>
				CRITICAL_BLOCKERS // {blockers.length > 0 ? `${blockers.length} PENDING` : 'CLEAR'}
			</h3>
			{#if blockers.length === 0}
				<div class="all-clear">NO CRITICAL BLOCKERS</div>
			{:else}
				<div class="blockers-mini">
					{#each blockers.slice(0, 5) as blocker}
						<div class="blocker-mini">
							<span class="blocker-id">{blocker.id}</span>
							<span class="blocker-task">{blocker.task}</span>
						</div>
					{/each}
				</div>
				<a href="/jobs" class="brutal-btn" style="width: 100%; margin-top: 12px;">VIEW_ALL_BLOCKERS</a>
			{/if}
		</div>

		<!-- Apps Status -->
		<div class="card">
			<h3>PRODUCT_PORTFOLIO</h3>
			<div class="apps-grid">
				{#each apps as app}
					<a href={app.url} target="_blank" class="app-item">
						<span class="app-name">{app.name}</span>
						<span class="app-status" class:beta={app.status === 'beta'} class:dev={app.status === 'dev'}>
							{app.status.toUpperCase()}
						</span>
					</a>
				{/each}
			</div>
		</div>

		<!-- Strategy Loader (File-based Brain → Focus integration) -->
		<div class="card span-2 strategy-card">
			<div class="strategy-header">
				<h3>STRATEGY_LOADER // BRAIN → FOCUS</h3>
				<div class="strategy-filters">
					<button class="filter-btn" class:active={strategyFilter === 'all'} onclick={() => strategyFilter = 'all'}>
						ALL ({strategies.length})
					</button>
					<button class="filter-btn" class:active={strategyFilter === 'decision'} onclick={() => strategyFilter = 'decision'}>
						DECISIONS ({strategyCounts.decision})
					</button>
					<button class="filter-btn" class:active={strategyFilter === 'plan'} onclick={() => strategyFilter = 'plan'}>
						PLANS ({strategyCounts.plan})
					</button>
					<button class="filter-btn" class:active={strategyFilter === 'roadmap'} onclick={() => strategyFilter = 'roadmap'}>
						ROADMAPS ({strategyCounts.roadmap})
					</button>
				</div>
			</div>

			<div class="strategy-info">
				<span>Brain docs are file-based (any agent can edit). Load into Focus for project management.</span>
			</div>

			{#if filteredStrategies.length === 0}
				<div class="no-strategies">NO STRATEGY DOCS FOUND</div>
			{:else}
				<div class="strategy-list">
					{#each filteredStrategies as strategy}
						<div class="strategy-item">
							<div class="strategy-meta">
								<span class="strategy-type" class:decision={strategy.type === 'decision'} class:plan={strategy.type === 'plan'} class:roadmap={strategy.type === 'roadmap'}>
									{strategy.type.toUpperCase()}
								</span>
								<span class="strategy-date">{strategy.date}</span>
							</div>
							<div class="strategy-content">
								<div class="strategy-title">{strategy.title}</div>
								{#if strategy.summary}
									<div class="strategy-summary">{strategy.summary}</div>
								{/if}
								{#if strategy.tasks && strategy.tasks.length > 0}
									<div class="strategy-tasks-count">
										{strategy.tasks.filter(t => t.status === 'complete').length}/{strategy.tasks.length} tasks complete
									</div>
								{/if}
							</div>
							<button
								class="brutal-btn send-btn"
								onclick={() => sendToFocus(strategy)}
								disabled={sendingToFocus === strategy.id || $isReadOnly}
								title={$isReadOnly ? 'Read-only mode' : ''}
							>
								{sendingToFocus === strategy.id ? 'SENDING...' : 'SEND_TO_FOCUS'}
							</button>
						</div>
					{/each}
				</div>
			{/if}

			<div class="strategy-flow">
				<span class="flow-node">BRAIN</span>
				<span class="flow-arrow">→</span>
				<span class="flow-node active">FOCUS</span>
				<span class="flow-arrow">→</span>
				<span class="flow-node">LINEAR</span>
				<span class="flow-arrow">→</span>
				<span class="flow-node">SWARM</span>
			</div>
		</div>
		</div>
	{/if}
</div>

<style>
	.loading {
		padding: 40px;
		text-align: center;
		color: var(--text-muted);
		font-size: 12px;
		text-transform: uppercase;
		letter-spacing: 0.1em;
	}

	.focus-card {
		border-color: var(--terminal-green);
	}

	.focus-text {
		font-size: 18px;
		font-weight: 700;
		color: var(--terminal-green);
		letter-spacing: 0.05em;
	}
	.page {
		display: flex;
		flex-direction: column;
		gap: 20px;
	}

	.page-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		border-bottom: 2px solid var(--border);
		padding-bottom: 16px;
	}

	.me90-badge {
		background: var(--terminal-green);
		color: var(--void);
		padding: 8px 16px;
		font-family: 'JetBrains Mono', monospace;
		font-size: 12px;
		font-weight: 700;
	}

	.brain-grid {
		display: grid;
		grid-template-columns: repeat(2, 1fr);
		gap: 20px;
	}

	.card {
		background: var(--surface);
		border: 2px solid var(--border);
		padding: 20px;
		box-shadow: 4px 4px 0 0 var(--border);
	}

	.card.alert {
		border-color: #ff5555;
		box-shadow: 4px 4px 0 0 #ff5555;
	}

	.card h3 {
		font-size: 12px;
		font-weight: 700;
		margin: 0 0 16px 0;
		text-transform: uppercase;
		letter-spacing: 0.05em;
	}

	.span-2 {
		grid-column: span 2;
	}

	/* Progress bar */
	.progress-container {
		position: relative;
		height: 30px;
		background: rgba(255, 255, 255, 0.1);
		border: 2px solid var(--border);
		margin-bottom: 16px;
	}

	.progress-bar {
		height: 100%;
		background: var(--terminal-green);
		transition: width 0.3s ease;
	}

	.progress-label {
		position: absolute;
		top: 50%;
		left: 50%;
		transform: translate(-50%, -50%);
		font-size: 11px;
		font-weight: 700;
		color: var(--text-main);
	}

	.goal-stats {
		display: flex;
		gap: 24px;
	}

	.goal-stat {
		display: flex;
		flex-direction: column;
		gap: 4px;
	}

	.stat-label {
		font-size: 10px;
		color: var(--text-muted);
	}

	.stat-value {
		font-family: 'JetBrains Mono', monospace;
		font-size: 14px;
		font-weight: 700;
	}

	.stat-value.green {
		color: var(--terminal-green);
	}

	/* Streams */
	.streams-list {
		display: flex;
		flex-direction: column;
		gap: 12px;
	}

	.stream-item {
		display: flex;
		flex-direction: column;
		gap: 4px;
	}

	.stream-header {
		display: flex;
		justify-content: space-between;
		font-size: 11px;
	}

	.stream-name {
		font-weight: 700;
	}

	.stream-percent {
		color: var(--text-muted);
	}

	.stream-bar-bg {
		height: 8px;
		background: rgba(255, 255, 255, 0.1);
	}

	.stream-bar {
		height: 100%;
		transition: width 0.3s ease;
	}

	/* Payment links */
	.payment-list {
		display: flex;
		flex-direction: column;
		gap: 8px;
	}

	.payment-item {
		display: flex;
		justify-content: space-between;
		padding: 10px 12px;
		background: rgba(51, 255, 0, 0.05);
		border: 1px solid var(--border);
		text-decoration: none;
		color: var(--text-main);
		transition: all 0.1s ease;
	}

	.payment-item:hover {
		background: rgba(51, 255, 0, 0.15);
		border-color: var(--terminal-green);
	}

	.payment-name {
		font-size: 12px;
	}

	.payment-price {
		font-family: 'JetBrains Mono', monospace;
		font-weight: 700;
		color: var(--terminal-green);
	}

	.payment-price::before {
		content: '';
	}

	/* Blockers */
	.all-clear {
		padding: 20px;
		text-align: center;
		color: var(--terminal-green);
		font-size: 12px;
		border: 2px dashed var(--terminal-green);
	}

	.blockers-mini {
		display: flex;
		flex-direction: column;
		gap: 8px;
	}

	.blocker-mini {
		display: flex;
		gap: 8px;
		padding: 8px;
		background: rgba(255, 85, 85, 0.1);
		border-left: 3px solid #ff5555;
	}

	.blocker-id {
		font-family: 'JetBrains Mono', monospace;
		font-size: 10px;
		color: #ff5555;
		flex-shrink: 0;
	}

	.blocker-task {
		font-size: 11px;
		color: var(--text-main);
	}

	.red {
		color: #ff5555 !important;
	}

	/* Apps */
	.apps-grid {
		display: flex;
		flex-direction: column;
		gap: 8px;
	}

	.app-item {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 10px 12px;
		background: var(--surface);
		border: 1px solid var(--border);
		text-decoration: none;
		color: var(--text-main);
		transition: all 0.1s ease;
	}

	.app-item:hover {
		border-color: var(--terminal-green);
		background: rgba(51, 255, 0, 0.05);
	}

	.app-name {
		font-size: 12px;
		font-weight: 600;
	}

	.app-status {
		font-size: 9px;
		padding: 2px 6px;
		text-transform: uppercase;
		font-weight: 700;
	}

	.app-status.beta {
		background: var(--terminal-green);
		color: var(--void);
	}

	.app-status.dev {
		background: var(--warning, #ffaa00);
		color: var(--void);
	}

	/* Strategy Loader */
	.strategy-card {
		border-color: var(--cyan-data, #00d4ff);
	}

	.strategy-header {
		display: flex;
		justify-content: space-between;
		align-items: flex-start;
		margin-bottom: 12px;
		flex-wrap: wrap;
		gap: 12px;
	}

	.strategy-filters {
		display: flex;
		gap: 8px;
		flex-wrap: wrap;
	}

	.filter-btn {
		background: transparent;
		border: 1px solid var(--border);
		color: var(--text-muted);
		padding: 4px 8px;
		font-size: 10px;
		font-family: 'JetBrains Mono', monospace;
		cursor: pointer;
		transition: all 0.1s;
	}

	.filter-btn:hover {
		border-color: var(--text-main);
		color: var(--text-main);
	}

	.filter-btn.active {
		background: var(--terminal-green);
		border-color: var(--terminal-green);
		color: var(--void);
	}

	.strategy-info {
		background: rgba(0, 212, 255, 0.1);
		border-left: 3px solid var(--cyan-data, #00d4ff);
		padding: 8px 12px;
		font-size: 11px;
		color: var(--text-muted);
		margin-bottom: 16px;
	}

	.no-strategies {
		padding: 20px;
		text-align: center;
		color: var(--text-muted);
		border: 2px dashed var(--border);
	}

	.strategy-list {
		display: flex;
		flex-direction: column;
		gap: 12px;
		max-height: 400px;
		overflow-y: auto;
	}

	.strategy-item {
		display: grid;
		grid-template-columns: 100px 1fr auto;
		gap: 12px;
		align-items: center;
		padding: 12px;
		background: rgba(255, 255, 255, 0.02);
		border: 1px solid var(--border);
	}

	.strategy-meta {
		display: flex;
		flex-direction: column;
		gap: 4px;
	}

	.strategy-type {
		font-size: 9px;
		padding: 2px 6px;
		font-weight: 700;
		text-align: center;
	}

	.strategy-type.decision {
		background: #ff6b6b;
		color: var(--void);
	}

	.strategy-type.plan {
		background: var(--terminal-green);
		color: var(--void);
	}

	.strategy-type.roadmap {
		background: var(--cyan-data, #00d4ff);
		color: var(--void);
	}

	.strategy-date {
		font-size: 10px;
		color: var(--text-muted);
		text-align: center;
	}

	.strategy-content {
		display: flex;
		flex-direction: column;
		gap: 4px;
	}

	.strategy-title {
		font-size: 12px;
		font-weight: 600;
	}

	.strategy-summary {
		font-size: 11px;
		color: var(--text-muted);
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
	}

	.strategy-tasks-count {
		font-size: 10px;
		color: var(--terminal-green);
	}

	.send-btn {
		font-size: 10px;
		padding: 6px 12px;
		white-space: nowrap;
	}

	.send-btn:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}

	.strategy-flow {
		display: flex;
		align-items: center;
		justify-content: center;
		gap: 8px;
		margin-top: 16px;
		padding-top: 16px;
		border-top: 1px solid var(--border);
	}

	.flow-node {
		padding: 6px 12px;
		font-size: 11px;
		font-weight: 700;
		background: rgba(255, 255, 255, 0.05);
		border: 1px solid var(--border);
	}

	.flow-node.active {
		background: var(--terminal-green);
		border-color: var(--terminal-green);
		color: var(--void);
	}

	.flow-arrow {
		color: var(--text-muted);
		font-size: 14px;
	}

	@media (max-width: 768px) {
		.brain-grid {
			grid-template-columns: 1fr;
		}

		.span-2 {
			grid-column: span 1;
		}

		.strategy-item {
			grid-template-columns: 1fr;
		}

		.strategy-meta {
			flex-direction: row;
			gap: 8px;
		}
	}
</style>
