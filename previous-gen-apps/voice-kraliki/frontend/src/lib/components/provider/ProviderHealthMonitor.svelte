<script lang="ts">
	/**
	 * Provider Health Monitor Component
	 *
	 * Real-time visualization of provider health status:
	 * - Health indicators for all providers
	 * - Latency metrics
	 * - Uptime percentages
	 * - Error rates
	 * - Auto-refresh
	 */

	import { onMount, onDestroy } from 'svelte';

	interface ProviderMetrics {
		provider_id: string;
		provider_type: string;
		status: 'healthy' | 'degraded' | 'unhealthy' | 'offline' | 'unknown';
		total_checks: number;
		successful_checks: number;
		failed_checks: number;
		success_rate: number;
		average_latency_ms: number;
		min_latency_ms: number;
		max_latency_ms: number;
		last_check_time: string;
		last_success_time?: string;
		last_error?: string;
		consecutive_failures: number;
		uptime_percentage: number;
	}

	interface Props {
		autoRefresh?: boolean;
		refreshInterval?: number;
		compact?: boolean;
	}

	let {
		autoRefresh = true,
		refreshInterval = 15000,
		compact = false
	}: Props = $props();

	// State
	let providers = $state<Record<string, ProviderMetrics>>({});
	let isLoading = $state(true);
	let lastUpdate = $state<Date | null>(null);
	let error = $state<string | null>(null);
	let refreshTimer: ReturnType<typeof setInterval> | null = null;

	// Provider display names
	const providerNames: Record<string, string> = {
		gemini: 'Google Gemini',
		openai: 'OpenAI Realtime',
		deepgram_nova3: 'Deepgram Nova 3',
		twilio: 'Twilio',
		telnyx: 'Telnyx'
	};

	// Status colors
	const statusColors: Record<string, { bg: string; border: string; text: string; dot: string }> = {
		healthy: { bg: '#d1fae5', border: '#10b981', text: '#065f46', dot: '#10b981' },
		degraded: { bg: '#fef3c7', border: '#f59e0b', text: '#92400e', dot: '#f59e0b' },
		unhealthy: { bg: '#fee2e2', border: '#ef4444', text: '#991b1b', dot: '#ef4444' },
		offline: { bg: '#f3f4f6', border: '#6b7280', text: '#374151', dot: '#6b7280' },
		unknown: { bg: '#f3f4f6', border: '#9ca3af', text: '#6b7280', dot: '#9ca3af' }
	};

	/**
	 * Fetch provider health data
	 */
	async function fetchProviderHealth() {
		try {
			error = null;
			const response = await fetch('http://localhost:8000/providers/health');

			if (!response.ok) {
				throw new Error(`HTTP ${response.status}: ${response.statusText}`);
			}

			const data = await response.json();
			providers = data;
			lastUpdate = new Date();
			isLoading = false;
		} catch (err) {
			error = err instanceof Error ? err.message : 'Failed to fetch provider health';
			console.error('Failed to fetch provider health:', err);
			isLoading = false;
		}
	}

	/**
	 * Format latency for display
	 */
	function formatLatency(ms: number): string {
		if (ms < 1) return '<1ms';
		if (ms < 1000) return `${Math.round(ms)}ms`;
		return `${(ms / 1000).toFixed(2)}s`;
	}

	/**
	 * Get status icon
	 */
	function getStatusIcon(status: string): string {
		switch (status) {
			case 'healthy': return '✓';
			case 'degraded': return '⚠';
			case 'unhealthy': return '✗';
			case 'offline': return '○';
			default: return '?';
		}
	}

	// Setup auto-refresh
	onMount(() => {
		fetchProviderHealth();

		if (autoRefresh) {
			refreshTimer = setInterval(fetchProviderHealth, refreshInterval);
		}
	});

	onDestroy(() => {
		if (refreshTimer) {
			clearInterval(refreshTimer);
		}
	});
</script>

<div class="provider-health-monitor" class:compact>
	<!-- Header -->
	<div class="header">
		<div class="title-section">
			<h3 class="title">Provider Health</h3>
			{#if lastUpdate}
				<span class="last-update">Updated {lastUpdate.toLocaleTimeString()}</span>
			{/if}
		</div>
		<button class="refresh-btn" onclick={fetchProviderHealth} disabled={isLoading}>
			<span class="refresh-icon" class:spinning={isLoading}>🔄</span>
			Refresh
		</button>
	</div>

	<!-- Error Display -->
	{#if error}
		<div class="error-banner">
			<span class="error-icon">⚠</span>
			<span class="error-text">{error}</span>
		</div>
	{/if}

	<!-- Provider Cards -->
	<div class="providers-grid" class:compact>
		{#if isLoading && Object.keys(providers).length === 0}
			<div class="loading">Loading provider health...</div>
		{:else if Object.keys(providers).length === 0}
			<div class="no-data">No provider health data available</div>
		{:else}
			{#each Object.entries(providers) as [providerId, metrics]}
				{@const colors = statusColors[metrics.status]}
				<div class="provider-card" style="border-color: {colors.border}; background: {colors.bg}">
					<!-- Card Header -->
					<div class="card-header">
						<div class="provider-name">
							<span class="status-dot" style="background: {colors.dot}"></span>
							<span class="name-text">{providerNames[providerId] || providerId}</span>
						</div>
						<div class="status-badge" style="color: {colors.text}; border-color: {colors.border}">
							<span class="status-icon">{getStatusIcon(metrics.status)}</span>
							<span class="status-text">{metrics.status.toUpperCase()}</span>
						</div>
					</div>

					{#if !compact}
						<!-- Metrics Grid -->
						<div class="metrics-grid">
							<div class="metric-item">
								<span class="metric-label">Latency</span>
								<span class="metric-value">{formatLatency(metrics.average_latency_ms)}</span>
							</div>
							<div class="metric-item">
								<span class="metric-label">Uptime</span>
								<span class="metric-value">{metrics.uptime_percentage.toFixed(1)}%</span>
							</div>
							<div class="metric-item">
								<span class="metric-label">Success Rate</span>
								<span class="metric-value">{metrics.success_rate.toFixed(1)}%</span>
							</div>
							<div class="metric-item">
								<span class="metric-label">Checks</span>
								<span class="metric-value">{metrics.total_checks}</span>
							</div>
						</div>

						<!-- Progress Bars -->
						<div class="progress-section">
							<div class="progress-item">
								<div class="progress-label">
									<span>Uptime</span>
									<span>{metrics.uptime_percentage.toFixed(1)}%</span>
								</div>
								<div class="progress-bar">
									<div class="progress-fill" style="width: {metrics.uptime_percentage}%; background: {colors.border}"></div>
								</div>
							</div>
						</div>

						<!-- Footer Info -->
						{#if metrics.consecutive_failures > 0}
							<div class="warning-footer">
								⚠ {metrics.consecutive_failures} consecutive failures
							</div>
						{/if}

						{#if metrics.last_error}
							<div class="error-footer" title={metrics.last_error}>
								Last error: {metrics.last_error.substring(0, 50)}...
							</div>
						{/if}
					{/if}
				</div>
			{/each}
		{/if}
	</div>
</div>

<style>
	.provider-health-monitor {
		border: 2px solid hsl(var(--border));
		background: hsl(var(--card));
		box-shadow: var(--shadow-brutal);
		padding: 1.25rem;
		color: hsl(var(--foreground));
		display: flex;
		flex-direction: column;
		gap: 1rem;
	}

	.provider-health-monitor.compact {
		padding: 1rem;
	}

	.header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		gap: 0.75rem;
	}

	.title-section {
		display: flex;
		flex-direction: column;
		gap: 0.25rem;
	}

	.title {
		font-size: 1.1rem;
		font-weight: 900;
		margin: 0;
		text-transform: uppercase;
		letter-spacing: 0.05em;
	}

	.last-update {
		font-size: 0.8rem;
		color: hsl(var(--muted-foreground));
	}

	.refresh-btn {
		display: inline-flex;
		align-items: center;
		gap: 0.5rem;
		padding: 0.6rem 1rem;
		border: 2px solid hsl(var(--border));
		background: hsl(var(--card));
		color: hsl(var(--foreground));
		font-weight: 800;
		text-transform: uppercase;
		letter-spacing: 0.05em;
		cursor: pointer;
		box-shadow: var(--shadow-brutal-subtle);
		transition: transform 60ms linear, box-shadow 60ms linear, background-color 60ms linear, color 60ms linear;
	}

	.refresh-btn:hover:not(:disabled) {
		background: var(--color-terminal-green);
		color: #000;
		transform: translate(2px, 2px);
		box-shadow: 2px 2px 0px 0px hsl(var(--foreground));
	}

	.refresh-btn:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}

	.refresh-icon {
		font-size: 1rem;
		display: inline-block;
	}

	.refresh-icon.spinning {
		animation: spin 1s linear infinite;
	}

	@keyframes spin {
		from { transform: rotate(0deg); }
		to { transform: rotate(360deg); }
	}

	.providers-grid {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
		gap: 0.75rem;
	}

	.provider-card {
		border: 2px solid hsl(var(--border));
		padding: 1rem;
		box-shadow: var(--shadow-brutal-subtle);
		background: hsl(var(--card));
		transition: transform 60ms linear, box-shadow 60ms linear;
	}

	.provider-card:hover {
		transform: translate(2px, 2px);
		box-shadow: 2px 2px 0px 0px hsl(var(--foreground));
	}

	.card-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 0.75rem;
		padding-bottom: 0.75rem;
		border-bottom: 2px solid hsl(var(--border));
	}

	.provider-name {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		font-weight: 900;
		text-transform: uppercase;
		letter-spacing: 0.04em;
	}

	.status-dot {
		width: 12px;
		height: 12px;
		border: 2px solid hsl(var(--border));
		background: currentColor;
		animation: pulse 2s infinite;
	}

	@keyframes pulse {
		0%, 100% { opacity: 1; }
		50% { opacity: 0.5; }
	}

	.status-badge {
		display: inline-flex;
		align-items: center;
		gap: 0.35rem;
		padding: 0.35rem 0.6rem;
		border: 2px solid hsl(var(--border));
		background: hsl(var(--card));
		font-weight: 800;
		text-transform: uppercase;
		letter-spacing: 0.04em;
		box-shadow: var(--shadow-brutal-subtle);
	}

	.metrics-grid {
		display: grid;
		grid-template-columns: repeat(2, 1fr);
		gap: 0.75rem;
		margin-bottom: 1rem;
	}

	.metric-item {
		display: flex;
		flex-direction: column;
		gap: 0.25rem;
	}

	.metric-label {
		font-size: 0.8rem;
		color: hsl(var(--muted-foreground));
		text-transform: uppercase;
		letter-spacing: 0.05em;
		font-weight: 800;
	}

	.metric-value {
		font-size: 1.2rem;
		font-weight: 900;
	}

	.progress-section {
		margin-bottom: 0.75rem;
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
	}

	.progress-label {
		display: flex;
		justify-content: space-between;
		font-size: 0.8rem;
		color: hsl(var(--muted-foreground));
		font-weight: 800;
		text-transform: uppercase;
		letter-spacing: 0.04em;
	}

	.progress-bar {
		height: 10px;
		background: hsl(var(--secondary));
		border: 2px solid hsl(var(--border));
		box-shadow: var(--shadow-brutal-subtle);
		overflow: hidden;
	}

	.progress-fill {
		height: 100%;
		transition: width 0.2s linear;
		background: hsl(var(--primary));
	}

	.warning-footer, .error-footer {
		padding: 0.6rem;
		border: 2px solid hsl(var(--border));
		font-size: 0.8rem;
		font-weight: 800;
		text-transform: uppercase;
		letter-spacing: 0.03em;
		box-shadow: var(--shadow-brutal-subtle);
	}

	.warning-footer {
		background: hsl(var(--accent) / 0.2);
		color: hsl(var(--foreground));
	}

	.error-footer {
		background: hsl(var(--destructive) / 0.15);
		color: hsl(var(--foreground));
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
	}

	.empty-state {
		text-align: center;
		padding: 2rem;
		color: hsl(var(--muted-foreground));
		border: 2px dashed hsl(var(--border));
	}

	@media (max-width: 768px) {
		.providers-grid {
			grid-template-columns: 1fr;
		}

		.metrics-grid {
			grid-template-columns: 1fr;
		}
	}
</style>

