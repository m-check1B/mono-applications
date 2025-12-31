<script lang="ts">
	/**
	 * Analytics Dashboard Page
	 *
	 * Comprehensive analytics and metrics visualization:
	 * - Real-time metrics overview
	 * - Time-series charts
	 * - Provider performance comparison
	 * - Agent performance metrics
	 * - Historical data analysis
	 */

	import EnhancedDashboard from '$lib/components/analytics/EnhancedDashboard.svelte';
	import ProviderMetricsDisplay from '$lib/components/analytics/ProviderMetricsDisplay.svelte';
	import ProviderHealthMonitor from '$lib/components/provider/ProviderHealthMonitor.svelte';

	// State for tab selection
	let activeTab = $state<'overview' | 'metrics' | 'health'>('overview');
</script>

<svelte:head>
	<title>Analytics Dashboard | Voice by Kraliki</title>
	<meta name="description" content="Real-time analytics and performance metrics" />
</svelte:head>

<div class="analytics-page">
	<!-- Page Header -->
	<div class="page-header">
		<div class="header-content">
			<h1 class="page-title">Analytics & Insights</h1>
			<p class="page-description">
				Real-time monitoring of call metrics, provider performance, and agent activity
			</p>
		</div>
	</div>

	<!-- Tab Navigation -->
	<div class="tab-navigation">
		<button
			class="tab-btn"
			class:active={activeTab === 'overview'}
			onclick={() => activeTab = 'overview'}
		>
			<span class="tab-icon">📊</span>
			<span class="tab-label">Overview</span>
		</button>
		<button
			class="tab-btn"
			class:active={activeTab === 'metrics'}
			onclick={() => activeTab = 'metrics'}
		>
			<span class="tab-icon">📈</span>
			<span class="tab-label">Metrics & Charts</span>
		</button>
		<button
			class="tab-btn"
			class:active={activeTab === 'health'}
			onclick={() => activeTab = 'health'}
		>
			<span class="tab-icon">🏥</span>
			<span class="tab-label">Provider Health</span>
		</button>
	</div>

	<!-- Tab Content -->
	<div class="tab-content">
		{#if activeTab === 'overview'}
			<div class="tab-panel" data-tab="overview">
				<EnhancedDashboard autoRefresh={true} refreshInterval={30000} />
			</div>
		{:else if activeTab === 'metrics'}
			<div class="tab-panel" data-tab="metrics">
				<ProviderMetricsDisplay autoRefresh={true} refreshInterval={60000} />
			</div>
		{:else if activeTab === 'health'}
			<div class="tab-panel" data-tab="health">
				<ProviderHealthMonitor autoRefresh={true} refreshInterval={15000} compact={false} />
			</div>
		{/if}
	</div>

	<!-- Info Cards -->
	<div class="info-section">
		<div class="info-card">
			<div class="info-icon">💡</div>
			<div class="info-content">
				<h4 class="info-title">Getting Started</h4>
				<p class="info-text">
					Analytics data is collected from all active calls. Visit the <a href="/calls/agent">Agent Operations</a> page to start demo calls and see live metrics.
				</p>
			</div>
		</div>

		<div class="info-card">
			<div class="info-icon">⚙️</div>
			<div class="info-content">
				<h4 class="info-title">Auto-Refresh</h4>
				<p class="info-text">
					All dashboards auto-refresh to show the latest data. Overview refreshes every 30 seconds, metrics every 60 seconds, and health every 15 seconds.
				</p>
			</div>
		</div>

		<div class="info-card">
			<div class="info-icon">📋</div>
			<div class="info-content">
				<h4 class="info-title">Data Retention</h4>
				<p class="info-text">
					Time-series data is retained for 24 hours. Historical summaries can be retrieved via the API with custom date ranges.
				</p>
			</div>
		</div>
	</div>
</div>

<style>
	.analytics-page {
		min-height: 100vh;
		background: hsl(var(--background));
		color: hsl(var(--foreground));
		padding: 1.5rem;
		display: flex;
		flex-direction: column;
		gap: 1rem;
	}

	.page-header {
		padding: 1rem;
		border: 2px solid hsl(var(--border));
		background: hsl(var(--card));
		box-shadow: var(--shadow-brutal);
	}

	.header-content {
		max-width: 900px;
	}

	.page-title {
		font-size: 2.1rem;
		font-weight: 900;
		color: hsl(var(--foreground));
		margin: 0 0 0.4rem 0;
		text-transform: uppercase;
		letter-spacing: 0.05em;
	}

	.page-description {
		font-size: 0.95rem;
		color: hsl(var(--muted-foreground));
		margin: 0;
		line-height: 1.5;
	}

	.tab-navigation {
		display: flex;
		gap: 0.5rem;
		padding: 0.5rem;
		border: 2px solid hsl(var(--border));
		background: hsl(var(--card));
		box-shadow: var(--shadow-brutal);
		overflow-x: auto;
	}

	.tab-btn {
		display: inline-flex;
		align-items: center;
		gap: 0.65rem;
		padding: 0.75rem 1.25rem;
		border: 2px solid hsl(var(--border));
		background: hsl(var(--card));
		color: hsl(var(--muted-foreground));
		font-weight: 800;
		text-transform: uppercase;
		letter-spacing: 0.05em;
		cursor: pointer;
		box-shadow: var(--shadow-brutal-subtle);
		transition: transform 60ms linear, box-shadow 60ms linear, background-color 60ms linear, color 60ms linear;
		white-space: nowrap;
	}

	.tab-btn:hover {
		background: var(--color-terminal-green);
		color: #000;
		transform: translate(2px, 2px);
		box-shadow: 2px 2px 0px 0px hsl(var(--foreground));
	}

	.tab-btn.active {
		background: var(--color-terminal-green);
		color: #000;
	}

	.tab-icon {
		font-size: 1.1rem;
	}

	.tab-label {
		font-size: 0.9rem;
	}

	.tab-content {
		margin-bottom: 1rem;
	}

	.tab-panel {
		animation: fadeIn 0.18s linear;
	}

	@keyframes fadeIn {
		from { opacity: 0; transform: translateY(6px); }
		to { opacity: 1; transform: translateY(0); }
	}

	.info-section {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
		gap: 1rem;
	}

	.info-card {
		display: flex;
		gap: 0.75rem;
		padding: 1rem;
		border: 2px solid hsl(var(--border));
		background: hsl(var(--card));
		box-shadow: var(--shadow-brutal);
	}

	.info-icon {
		font-size: 1.6rem;
	}

	.info-title {
		font-size: 1rem;
		font-weight: 800;
		margin: 0 0 0.35rem 0;
		text-transform: uppercase;
		letter-spacing: 0.04em;
	}

	.info-text {
		font-size: 0.9rem;
		color: hsl(var(--muted-foreground));
		margin: 0;
		line-height: 1.4;
	}

	.info-text a {
		color: hsl(var(--foreground));
		font-weight: 800;
		text-decoration: underline;
	}

	@media (max-width: 768px) {
		.analytics-page {
			padding: 1rem;
		}

		.tab-btn {
			padding: 0.65rem 1rem;
		}
	}
</style>
