<script lang="ts">
	/**
	 * Enhanced Analytics Dashboard Component
	 *
	 * Real-time analytics visualization:
	 * - Call metrics overview (total, active, success rate)
	 * - Live charts (calls, sentiment, quality over time)
	 * - Provider performance comparison
	 * - Agent performance metrics
	 * - Active calls monitoring
	 */

	import { onMount, onDestroy } from 'svelte';

	interface AnalyticsSummary {
		period_start: string;
		period_end: string;
		total_calls: number;
		completed_calls: number;
		failed_calls: number;
		average_call_duration: number;
		success_rate: number;
		average_sentiment: number;
		average_audio_quality: number;
		average_transcription_accuracy: number;
		provider_performance: Record<string, ProviderPerformance>;
		agent_performance: Record<string, AgentPerformance>;
		calls_over_time: TimeSeriesDataPoint[];
		sentiment_over_time: TimeSeriesDataPoint[];
		quality_over_time: TimeSeriesDataPoint[];
	}

	interface ProviderPerformance {
		provider_id: string;
		total_calls: number;
		successful_calls: number;
		failed_calls: number;
		average_latency_ms: number;
		average_audio_quality: number;
		uptime_percentage: number;
		error_rate: number;
	}

	interface AgentPerformance {
		agent_id: string;
		total_calls: number;
		completed_calls: number;
		failed_calls: number;
		average_call_duration: number;
		average_sentiment: number;
		total_suggestions_used: number;
		compliance_warnings: number;
		quality_score: number;
	}

	interface TimeSeriesDataPoint {
		timestamp: string;
		value: number;
		label?: string;
	}

	interface RealtimeMetrics {
		timestamp: string;
		active_calls: number;
		total_calls: number;
		recent_calls_last_hour: number;
		recent_success_rate: number;
		recent_average_sentiment: number;
		recent_average_duration: number;
	}

	interface Props {
		timeRange?: '1h' | '24h' | '7d' | '30d';
		autoRefresh?: boolean;
		refreshInterval?: number;
	}

	let {
		timeRange = '24h',
		autoRefresh = true,
		refreshInterval = 30000
	}: Props = $props();

	// State
	let summary = $state<AnalyticsSummary | null>(null);
	let realtimeMetrics = $state<RealtimeMetrics | null>(null);
	let isLoading = $state(true);
	let error = $state<string | null>(null);
	let lastUpdate = $state<Date | null>(null);
	let refreshTimer: ReturnType<typeof setInterval> | null = null;

	// Provider display names
	const providerNames: Record<string, string> = {
		gemini: 'Google Gemini',
		openai: 'OpenAI Realtime',
		deepgram_nova3: 'Deepgram Nova 3',
		twilio: 'Twilio',
		telnyx: 'Telnyx'
	};

	/**
	 * Fetch analytics summary
	 */
	async function fetchAnalytics() {
		try {
			error = null;

			// Fetch summary and realtime metrics in parallel
			const [summaryRes, realtimeRes] = await Promise.all([
				fetch('http://localhost:8000/analytics/summary'),
				fetch('http://localhost:8000/analytics/metrics/realtime')
			]);

			if (!summaryRes.ok) {
				throw new Error(`HTTP ${summaryRes.status}: ${summaryRes.statusText}`);
			}
			if (!realtimeRes.ok) {
				throw new Error(`HTTP ${realtimeRes.status}: ${realtimeRes.statusText}`);
			}

			const summaryData = await summaryRes.json();
			const realtimeData = await realtimeRes.json();

			summary = summaryData.summary;
			realtimeMetrics = realtimeData;
			lastUpdate = new Date();
			isLoading = false;
		} catch (err) {
			error = err instanceof Error ? err.message : 'Failed to fetch analytics';
			console.error('Failed to fetch analytics:', err);
			isLoading = false;
		}
	}

	/**
	 * Format duration
	 */
	function formatDuration(seconds: number): string {
		const mins = Math.floor(seconds / 60);
		const secs = Math.round(seconds % 60);
		return `${mins}m ${secs}s`;
	}

	/**
	 * Format percentage
	 */
	function formatPercent(value: number): string {
		return `${value.toFixed(1)}%`;
	}

	/**
	 * Get sentiment color
	 */
	function getSentimentColor(sentiment: number): string {
		if (sentiment >= 0.5) return '#10b981'; // Very positive
		if (sentiment >= 0.2) return '#84cc16'; // Positive
		if (sentiment >= -0.2) return '#f59e0b'; // Neutral
		if (sentiment >= -0.5) return '#f97316'; // Negative
		return '#ef4444'; // Very negative
	}

	/**
	 * Get quality color
	 */
	function getQualityColor(quality: number): string {
		if (quality >= 80) return '#10b981'; // Excellent
		if (quality >= 60) return '#84cc16'; // Good
		if (quality >= 40) return '#f59e0b'; // Fair
		if (quality >= 20) return '#f97316'; // Poor
		return '#ef4444'; // Critical
	}

	/**
	 * Format time ago
	 */
	function formatTimeAgo(date: Date): string {
		const seconds = Math.floor((new Date().getTime() - date.getTime()) / 1000);
		if (seconds < 60) return `${seconds}s ago`;
		const minutes = Math.floor(seconds / 60);
		if (minutes < 60) return `${minutes}m ago`;
		const hours = Math.floor(minutes / 60);
		return `${hours}h ago`;
	}

	// Setup auto-refresh
	onMount(() => {
		fetchAnalytics();

		if (autoRefresh) {
			refreshTimer = setInterval(fetchAnalytics, refreshInterval);
		}
	});

	onDestroy(() => {
		if (refreshTimer) {
			clearInterval(refreshTimer);
		}
	});
</script>

<div class="enhanced-dashboard">
	<!-- Header -->
	<div class="dashboard-header">
		<div class="title-section">
			<h2 class="dashboard-title">Analytics Dashboard</h2>
			{#if lastUpdate}
				<span class="last-update">Updated {formatTimeAgo(lastUpdate)}</span>
			{/if}
		</div>
		<button class="refresh-btn" onclick={fetchAnalytics} disabled={isLoading}>
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

	{#if isLoading && !summary}
		<div class="loading-state">
			<span class="spinner">⟳</span>
			<p>Loading analytics...</p>
		</div>
	{:else if summary}
		<!-- Real-time Metrics Bar -->
		{#if realtimeMetrics}
			<div class="realtime-bar">
				<div class="realtime-item">
					<span class="realtime-label">Active Calls</span>
					<span class="realtime-value active">{realtimeMetrics.active_calls}</span>
				</div>
				<div class="realtime-item">
					<span class="realtime-label">Calls (Last Hour)</span>
					<span class="realtime-value">{realtimeMetrics.recent_calls_last_hour}</span>
				</div>
				<div class="realtime-item">
					<span class="realtime-label">Recent Success Rate</span>
					<span class="realtime-value">{formatPercent(realtimeMetrics.recent_success_rate)}</span>
				</div>
				<div class="realtime-item">
					<span class="realtime-label">Avg Sentiment</span>
					<span
						class="realtime-value"
						style="color: {getSentimentColor(realtimeMetrics.recent_average_sentiment)}"
					>
						{realtimeMetrics.recent_average_sentiment.toFixed(2)}
					</span>
				</div>
			</div>
		{/if}

		<!-- Key Metrics Grid -->
		<div class="metrics-grid">
			<div class="metric-card">
				<div class="metric-icon">📞</div>
				<div class="metric-content">
					<span class="metric-label">Total Calls</span>
					<span class="metric-value">{summary.total_calls}</span>
				</div>
			</div>

			<div class="metric-card">
				<div class="metric-icon">✓</div>
				<div class="metric-content">
					<span class="metric-label">Completed Calls</span>
					<span class="metric-value success">{summary.completed_calls}</span>
				</div>
			</div>

			<div class="metric-card">
				<div class="metric-icon">✗</div>
				<div class="metric-content">
					<span class="metric-label">Failed Calls</span>
					<span class="metric-value error">{summary.failed_calls}</span>
				</div>
			</div>

			<div class="metric-card">
				<div class="metric-icon">📊</div>
				<div class="metric-content">
					<span class="metric-label">Success Rate</span>
					<span class="metric-value">{formatPercent(summary.success_rate)}</span>
				</div>
			</div>

			<div class="metric-card">
				<div class="metric-icon">⏱️</div>
				<div class="metric-content">
					<span class="metric-label">Avg Duration</span>
					<span class="metric-value">{formatDuration(summary.average_call_duration)}</span>
				</div>
			</div>

			<div class="metric-card">
				<div class="metric-icon">😊</div>
				<div class="metric-content">
					<span class="metric-label">Avg Sentiment</span>
					<span
						class="metric-value"
						style="color: {getSentimentColor(summary.average_sentiment)}"
					>
						{summary.average_sentiment.toFixed(2)}
					</span>
				</div>
			</div>

			<div class="metric-card">
				<div class="metric-icon">🎤</div>
				<div class="metric-content">
					<span class="metric-label">Audio Quality</span>
					<span
						class="metric-value"
						style="color: {getQualityColor(summary.average_audio_quality)}"
					>
						{summary.average_audio_quality.toFixed(1)}
					</span>
				</div>
			</div>

			<div class="metric-card">
				<div class="metric-icon">📝</div>
				<div class="metric-content">
					<span class="metric-label">Transcription</span>
					<span class="metric-value">{formatPercent(summary.average_transcription_accuracy * 100)}</span>
				</div>
			</div>
		</div>

		<!-- Provider Performance -->
		{#if Object.keys(summary.provider_performance).length > 0}
			<div class="section-card">
				<h3 class="section-title">Provider Performance</h3>
				<div class="provider-grid">
					{#each Object.entries(summary.provider_performance) as [providerId, performance]}
						<div class="provider-card">
							<div class="provider-header">
								<span class="provider-name">{providerNames[providerId] || providerId}</span>
								<span class="provider-calls">{performance.total_calls} calls</span>
							</div>
							<div class="provider-metrics">
								<div class="provider-metric">
									<span class="pm-label">Success</span>
									<span class="pm-value">{formatPercent((performance.successful_calls / performance.total_calls) * 100)}</span>
								</div>
								<div class="provider-metric">
									<span class="pm-label">Quality</span>
									<span class="pm-value">{performance.average_audio_quality.toFixed(1)}</span>
								</div>
								<div class="provider-metric">
									<span class="pm-label">Uptime</span>
									<span class="pm-value">{formatPercent(performance.uptime_percentage)}</span>
								</div>
								<div class="provider-metric">
									<span class="pm-label">Error Rate</span>
									<span class="pm-value error">{formatPercent(performance.error_rate)}</span>
								</div>
							</div>
						</div>
					{/each}
				</div>
			</div>
		{/if}

		<!-- Agent Performance -->
		{#if Object.keys(summary.agent_performance).length > 0}
			<div class="section-card">
				<h3 class="section-title">Agent Performance</h3>
				<div class="agent-table">
					<div class="agent-table-header">
						<span class="agent-col">Agent ID</span>
						<span class="agent-col">Calls</span>
						<span class="agent-col">Success</span>
						<span class="agent-col">Avg Duration</span>
						<span class="agent-col">Sentiment</span>
						<span class="agent-col">Quality</span>
					</div>
					{#each Object.entries(summary.agent_performance) as [agentId, performance]}
						<div class="agent-table-row">
							<span class="agent-col agent-id">{agentId}</span>
							<span class="agent-col">{performance.total_calls}</span>
							<span class="agent-col">{formatPercent((performance.completed_calls / performance.total_calls) * 100)}</span>
							<span class="agent-col">{formatDuration(performance.average_call_duration)}</span>
							<span
								class="agent-col"
								style="color: {getSentimentColor(performance.average_sentiment)}"
							>
								{performance.average_sentiment.toFixed(2)}
							</span>
							<span class="agent-col">{performance.quality_score.toFixed(1)}</span>
						</div>
					{/each}
				</div>
			</div>
		{/if}

		<!-- Time Series Preview -->
		{#if summary.calls_over_time.length > 0}
			<div class="section-card">
				<h3 class="section-title">Call Activity</h3>
				<div class="timeseries-info">
					<p>{summary.calls_over_time.length} data points over the last 24 hours</p>
					<p class="note">Detailed charts available in Provider Metrics Display</p>
				</div>
			</div>
		{/if}
	{:else}
		<div class="no-data">
			<p>No analytics data available</p>
			<p class="hint">Start making calls to see analytics</p>
		</div>
	{/if}
</div>

<style>
	.enhanced-dashboard {
		display: flex;
		flex-direction: column;
		gap: 1rem;
		color: hsl(var(--foreground));
		background: hsl(var(--background));
	}

	.dashboard-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		gap: 1rem;
		padding: 1rem;
		background: hsl(var(--card));
		border: 2px solid hsl(var(--border));
		box-shadow: var(--shadow-brutal);
	}

	.title-section {
		display: flex;
		flex-direction: column;
		gap: 0.2rem;
	}

	.dashboard-title {
		font-size: 1.6rem;
		font-weight: 900;
		margin: 0;
		text-transform: uppercase;
		letter-spacing: 0.05em;
	}

	.last-update {
		font-size: 0.85rem;
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
		font-size: 1.1rem;
		display: inline-block;
	}

	.refresh-icon.spinning {
		animation: spin 1s linear infinite;
	}

	@keyframes spin {
		from { transform: rotate(0deg); }
		to { transform: rotate(360deg); }
	}

	.error-banner,
	.loading-state,
	.no-data {
		display: flex;
		align-items: center;
		gap: 0.75rem;
		padding: 1rem;
		border: 2px solid hsl(var(--border));
		background: hsl(var(--card));
		box-shadow: var(--shadow-brutal);
		color: hsl(var(--foreground));
	}

	.loading-state,
	.no-data {
		flex-direction: column;
		text-align: center;
		justify-content: center;
		gap: 0.5rem;
	}

	.error-text {
		font-weight: 800;
	}

	.spinner {
		font-size: 2.5rem;
		animation: spin 1s linear infinite;
	}

	.no-data .hint {
		font-size: 0.85rem;
		color: hsl(var(--muted-foreground));
	}

	.realtime-bar {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
		gap: 0.75rem;
		padding: 1rem;
		border: 2px solid hsl(var(--border));
		background: hsl(var(--card));
		box-shadow: var(--shadow-brutal);
	}

	.realtime-item {
		display: flex;
		flex-direction: column;
		gap: 0.35rem;
	}

	.realtime-label {
		font-size: 0.8rem;
		color: hsl(var(--muted-foreground));
		text-transform: uppercase;
		letter-spacing: 0.05em;
		font-weight: 800;
	}

	.realtime-value {
		font-size: 1.6rem;
		font-weight: 900;
	}

	.realtime-value.active {
		color: var(--color-terminal-green);
	}

	.metrics-grid {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
		gap: 0.75rem;
	}

	.metric-card {
		display: flex;
		align-items: center;
		gap: 0.75rem;
		padding: 1rem;
		border: 2px solid hsl(var(--border));
		background: hsl(var(--card));
		box-shadow: var(--shadow-brutal-subtle);
	}

	.metric-icon {
		font-size: 1.6rem;
	}

	.metric-label {
		font-size: 0.8rem;
		color: hsl(var(--muted-foreground));
		text-transform: uppercase;
		letter-spacing: 0.05em;
		font-weight: 800;
	}

	.metric-value {
		font-size: 1.4rem;
		font-weight: 900;
	}

	.section-card {
		border: 2px solid hsl(var(--border));
		background: hsl(var(--card));
		box-shadow: var(--shadow-brutal);
		padding: 1.25rem;
		display: flex;
		flex-direction: column;
		gap: 1rem;
	}

	.section-title {
		font-size: 1.1rem;
		font-weight: 900;
		margin: 0;
		text-transform: uppercase;
		letter-spacing: 0.05em;
	}

	.provider-grid {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
		gap: 0.75rem;
	}

	.provider-card {
		border: 2px solid hsl(var(--border));
		background: hsl(var(--card));
		padding: 0.85rem;
		box-shadow: var(--shadow-brutal-subtle);
	}

	.provider-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding-bottom: 0.75rem;
		border-bottom: 2px solid hsl(var(--border));
	}

	.provider-name {
		font-weight: 900;
		letter-spacing: 0.04em;
		text-transform: uppercase;
	}

	.provider-calls {
		font-size: 0.85rem;
		color: hsl(var(--muted-foreground));
	}

	.provider-metrics {
		display: grid;
		grid-template-columns: repeat(2, 1fr);
		gap: 0.5rem;
		margin-top: 0.75rem;
	}

	.provider-metric {
		display: flex;
		flex-direction: column;
		gap: 0.2rem;
	}

	.pm-label {
		font-size: 0.75rem;
		color: hsl(var(--muted-foreground));
		text-transform: uppercase;
		letter-spacing: 0.05em;
		font-weight: 800;
	}

	.pm-value {
		font-size: 1rem;
		font-weight: 900;
	}

	.agent-table {
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
	}

	.agent-table-header {
		display: grid;
		grid-template-columns: 2fr repeat(5, 1fr);
		gap: 0.75rem;
		padding: 0.75rem;
		border: 2px solid hsl(var(--border));
		background: hsl(var(--secondary));
		color: hsl(var(--foreground));
		text-transform: uppercase;
		letter-spacing: 0.05em;
		font-weight: 900;
	}

	.agent-table-row {
		display: grid;
		grid-template-columns: 2fr repeat(5, 1fr);
		gap: 0.75rem;
		padding: 0.75rem;
		border: 2px solid hsl(var(--border));
		background: hsl(var(--card));
		box-shadow: var(--shadow-brutal-subtle);
	}

	.agent-col {
		display: flex;
		align-items: center;
	}

	.agent-id {
		font-weight: 900;
	}

	.timeseries-info {
		border: 2px solid hsl(var(--border));
		background: hsl(var(--card));
		padding: 1rem;
		text-align: center;
		box-shadow: var(--shadow-brutal-subtle);
	}

	.timeseries-info p {
		margin: 0.35rem 0;
		color: hsl(var(--muted-foreground));
	}

	.timeseries-info .note {
		font-style: italic;
		color: hsl(var(--foreground));
	}

	@media (max-width: 768px) {
		.dashboard-header {
			flex-direction: column;
			align-items: flex-start;
		}

		.realtime-bar,
		.metrics-grid {
			grid-template-columns: 1fr;
		}

		.provider-grid {
			grid-template-columns: 1fr;
		}

		.agent-table-header,
		.agent-table-row {
			grid-template-columns: 1fr;
		}
	}
</style>
