<script lang="ts">
	/**
	 * Provider Metrics Display Component
	 *
	 * Advanced metrics visualization:
	 * - Time-series charts (calls, sentiment, quality)
	 * - Provider performance comparison
	 * - Historical trends analysis
	 * - Detailed metrics tables
	 */

	import { onMount, onDestroy } from 'svelte';

	interface TimeSeriesDataPoint {
		timestamp: string;
		value: number;
		label?: string;
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

	interface Props {
		timeRange?: '1h' | '24h' | '7d' | '30d';
		autoRefresh?: boolean;
		refreshInterval?: number;
	}

	let {
		timeRange = '24h',
		autoRefresh = true,
		refreshInterval = 60000
	}: Props = $props();

	// State
	let callsData = $state<TimeSeriesDataPoint[]>([]);
	let sentimentData = $state<TimeSeriesDataPoint[]>([]);
	let qualityData = $state<TimeSeriesDataPoint[]>([]);
	let providerPerformance = $state<Record<string, ProviderPerformance>>({});
	let isLoading = $state(true);
	let error = $state<string | null>(null);
	let selectedChart = $state<'calls' | 'sentiment' | 'quality'>('calls');
	let refreshTimer: ReturnType<typeof setInterval> | null = null;

	// Provider display names and colors
	const providerNames: Record<string, string> = {
		gemini: 'Google Gemini',
		openai: 'OpenAI Realtime',
		deepgram_nova3: 'Deepgram Nova 3',
		twilio: 'Twilio',
		telnyx: 'Telnyx'
	};

	const providerColors: Record<string, string> = {
		gemini: '#4285f4',
		openai: '#10b981',
		deepgram_nova3: '#f59e0b',
		twilio: '#ef4444',
		telnyx: '#8b5cf6'
	};

	/**
	 * Fetch metrics data
	 */
	async function fetchMetrics() {
		try {
			error = null;
			const response = await fetch('http://localhost:8000/analytics/summary');

			if (!response.ok) {
				throw new Error(`HTTP ${response.status}: ${response.statusText}`);
			}

			const data = await response.json();
			const summary = data.summary;

			callsData = summary.calls_over_time || [];
			sentimentData = summary.sentiment_over_time || [];
			qualityData = summary.quality_over_time || [];
			providerPerformance = summary.provider_performance || {};

			isLoading = false;
		} catch (err) {
			error = err instanceof Error ? err.message : 'Failed to fetch metrics';
			console.error('Failed to fetch metrics:', err);
			isLoading = false;
		}
	}

	/**
	 * Format chart data for visualization
	 */
	function formatChartData(data: TimeSeriesDataPoint[]): {x: number, y: number, label: string}[] {
		if (data.length === 0) return [];

		return data.map((point, index) => ({
			x: index,
			y: point.value,
			label: new Date(point.timestamp).toLocaleTimeString()
		}));
	}

	/**
	 * Calculate chart dimensions
	 */
	function getChartDimensions(data: {x: number, y: number}[]) {
		if (data.length === 0) {
			return { minY: 0, maxY: 100, minX: 0, maxX: 100 };
		}

		const values = data.map(d => d.y);
		const minY = Math.min(...values);
		const maxY = Math.max(...values);
		const minX = 0;
		const maxX = data.length - 1;

		// Add padding
		const yPadding = (maxY - minY) * 0.1 || 10;

		return {
			minY: minY - yPadding,
			maxY: maxY + yPadding,
			minX,
			maxX
		};
	}

	/**
	 * Generate SVG path for line chart
	 */
	function generateLinePath(
		data: {x: number, y: number}[],
		dims: {minX: number, maxX: number, minY: number, maxY: number},
		width: number,
		height: number
	): string {
		if (data.length === 0) return '';

		const scaleX = (x: number) => ((x - dims.minX) / (dims.maxX - dims.minX)) * width;
		const scaleY = (y: number) => height - ((y - dims.minY) / (dims.maxY - dims.minY)) * height;

		const points = data.map(d => `${scaleX(d.x)},${scaleY(d.y)}`);
		return `M ${points.join(' L ')}`;
	}

	/**
	 * Get current chart data
	 */
	const currentChartData = $derived(() => {
		switch (selectedChart) {
			case 'calls':
				return formatChartData(callsData);
			case 'sentiment':
				return formatChartData(sentimentData);
			case 'quality':
				return formatChartData(qualityData);
			default:
				return [];
		}
	});

	/**
	 * Get chart title and color
	 */
	const chartConfig = $derived(() => {
		switch (selectedChart) {
			case 'calls':
				return { title: 'Call Volume Over Time', color: '#3b82f6', unit: 'calls' };
			case 'sentiment':
				return { title: 'Sentiment Trend', color: '#10b981', unit: 'score' };
			case 'quality':
				return { title: 'Audio Quality Trend', color: '#f59e0b', unit: 'score' };
			default:
				return { title: 'Metrics', color: '#6b7280', unit: '' };
		}
	});

	// Setup auto-refresh
	onMount(() => {
		fetchMetrics();

		if (autoRefresh) {
			refreshTimer = setInterval(fetchMetrics, refreshInterval);
		}
	});

	onDestroy(() => {
		if (refreshTimer) {
			clearInterval(refreshTimer);
		}
	});
</script>

<div class="provider-metrics-display">
	<!-- Header -->
	<div class="header">
		<h3 class="title">Provider Metrics & Trends</h3>
		<button class="refresh-btn" onclick={fetchMetrics} disabled={isLoading}>
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

	{#if isLoading && callsData.length === 0}
		<div class="loading-state">
			<span class="spinner">⟳</span>
			<p>Loading metrics...</p>
		</div>
	{:else}
		<!-- Chart Selector -->
		<div class="chart-selector">
			<button
				class="selector-btn"
				class:active={selectedChart === 'calls'}
				onclick={() => selectedChart = 'calls'}
			>
				📞 Call Volume
			</button>
			<button
				class="selector-btn"
				class:active={selectedChart === 'sentiment'}
				onclick={() => selectedChart = 'sentiment'}
			>
				😊 Sentiment
			</button>
			<button
				class="selector-btn"
				class:active={selectedChart === 'quality'}
				onclick={() => selectedChart = 'quality'}
			>
				🎤 Audio Quality
			</button>
		</div>

		<!-- Time Series Chart -->
		<div class="chart-container">
			<div class="chart-header">
				<h4 class="chart-title">{chartConfig().title}</h4>
				<span class="data-points">
					{currentChartData().length} data points
				</span>
			</div>

			{#if currentChartData().length > 0}
				{@const chartData = currentChartData()}
				{@const dims = getChartDimensions(chartData)}
				{@const chartWidth = 800}
				{@const chartHeight = 300}
				{@const path = generateLinePath(chartData, dims, chartWidth, chartHeight)}

				<div class="chart-wrapper">
					<svg
						class="chart-svg"
						viewBox="0 0 {chartWidth} {chartHeight}"
						preserveAspectRatio="xMidYMid meet"
					>
						<!-- Grid lines -->
						<defs>
							<pattern id="grid" width="80" height="60" patternUnits="userSpaceOnUse">
								<path d="M 80 0 L 0 0 0 60" fill="none" stroke="#e5e7eb" stroke-width="1"/>
							</pattern>
						</defs>
						<rect width="100%" height="100%" fill="url(#grid)" />

						<!-- Line chart -->
						<path
							d={path}
							fill="none"
							stroke={chartConfig().color}
							stroke-width="3"
							stroke-linecap="round"
							stroke-linejoin="round"
						/>

						<!-- Data points -->
						{#each chartData as point, i}
							{@const x = ((point.x - dims.minX) / (dims.maxX - dims.minX)) * chartWidth}
							{@const y = chartHeight - ((point.y - dims.minY) / (dims.maxY - dims.minY)) * chartHeight}
							<circle
								cx={x}
								cy={y}
								r="4"
								fill={chartConfig().color}
								stroke="white"
								stroke-width="2"
							>
								<title>{point.label}: {point.y.toFixed(2)}</title>
							</circle>
						{/each}
					</svg>
				</div>

				<!-- Chart Legend -->
				<div class="chart-legend">
					<div class="legend-item">
						<div class="legend-color" style="background: {chartConfig().color}"></div>
						<span class="legend-label">{chartConfig().title}</span>
					</div>
					<div class="legend-stats">
						<span class="stat-item">
							Min: {Math.min(...chartData.map(d => d.y)).toFixed(2)}
						</span>
						<span class="stat-item">
							Max: {Math.max(...chartData.map(d => d.y)).toFixed(2)}
						</span>
						<span class="stat-item">
							Avg: {(chartData.reduce((sum, d) => sum + d.y, 0) / chartData.length).toFixed(2)}
						</span>
					</div>
				</div>
			{:else}
				<div class="no-chart-data">
					<p>No {selectedChart} data available</p>
					<p class="hint">Data will appear once calls are made</p>
				</div>
			{/if}
		</div>

		<!-- Provider Comparison Table -->
		{#if Object.keys(providerPerformance).length > 0}
			<div class="comparison-section">
				<h4 class="comparison-title">Provider Performance Comparison</h4>
				<div class="comparison-table">
					<div class="table-header">
						<span class="col-provider">Provider</span>
						<span class="col-calls">Total Calls</span>
						<span class="col-success">Success Rate</span>
						<span class="col-latency">Avg Latency</span>
						<span class="col-quality">Audio Quality</span>
						<span class="col-uptime">Uptime</span>
						<span class="col-error">Error Rate</span>
					</div>
					{#each Object.entries(providerPerformance) as [providerId, perf]}
						<div class="table-row">
							<span class="col-provider">
								<span
									class="provider-dot"
									style="background: {providerColors[providerId] || '#6b7280'}"
								></span>
								{providerNames[providerId] || providerId}
							</span>
							<span class="col-calls">{perf.total_calls}</span>
							<span class="col-success">
								{((perf.successful_calls / perf.total_calls) * 100).toFixed(1)}%
							</span>
							<span class="col-latency">{perf.average_latency_ms.toFixed(0)}ms</span>
							<span class="col-quality">{perf.average_audio_quality.toFixed(1)}</span>
							<span class="col-uptime">{perf.uptime_percentage.toFixed(1)}%</span>
							<span class="col-error" class:high-error={perf.error_rate > 10}>
								{perf.error_rate.toFixed(1)}%
							</span>
						</div>
					{/each}
				</div>
			</div>
		{/if}
	{/if}
</div>

<style>
	.provider-metrics-display {
		border: 2px solid hsl(var(--border));
		background: hsl(var(--card));
		box-shadow: var(--shadow-brutal);
		padding: 1.25rem;
		display: flex;
		flex-direction: column;
		gap: 1rem;
		color: hsl(var(--foreground));
	}

	.header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		gap: 1rem;
	}

	.title {
		font-size: 1.1rem;
		font-weight: 900;
		margin: 0;
		text-transform: uppercase;
		letter-spacing: 0.05em;
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

	.error-banner,
	.loading-state,
	.empty-state {
		display: flex;
		align-items: center;
		gap: 0.75rem;
		padding: 1rem;
		border: 2px solid hsl(var(--border));
		background: hsl(var(--card));
		box-shadow: var(--shadow-brutal-subtle);
		color: hsl(var(--foreground));
	}

	.loading-state,
	.empty-state {
		justify-content: center;
		text-align: center;
	}

	.spinner {
		font-size: 2.2rem;
		animation: spin 1s linear infinite;
	}

	.chart-selector {
		display: flex;
		gap: 0.5rem;
		flex-wrap: wrap;
	}

	.selector-btn {
		padding: 0.6rem 1rem;
		border: 2px solid hsl(var(--border));
		background: hsl(var(--card));
		color: hsl(var(--muted-foreground));
		font-weight: 800;
		text-transform: uppercase;
		letter-spacing: 0.04em;
		cursor: pointer;
		box-shadow: var(--shadow-brutal-subtle);
		transition: transform 60ms linear, box-shadow 60ms linear, background-color 60ms linear, color 60ms linear;
	}

	.selector-btn:hover {
		background: var(--color-terminal-green);
		color: #000;
		transform: translate(2px, 2px);
		box-shadow: 2px 2px 0px 0px hsl(var(--foreground));
	}

	.selector-btn.active {
		background: var(--color-terminal-green);
		color: #000;
	}

	.chart-container {
		border: 2px solid hsl(var(--border));
		background: hsl(var(--card));
		box-shadow: var(--shadow-brutal-subtle);
		padding: 1rem;
		display: flex;
		flex-direction: column;
		gap: 0.75rem;
	}

	.chart-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		gap: 0.5rem;
	}

	.chart-title {
		margin: 0;
		font-weight: 900;
		text-transform: uppercase;
		letter-spacing: 0.04em;
	}

	.chart-summary {
		color: hsl(var(--muted-foreground));
		font-weight: 700;
	}

	.chart-stats {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
		gap: 0.75rem;
	}

	.stat-card {
		border: 2px solid hsl(var(--border));
		background: hsl(var(--card));
		padding: 0.75rem;
		box-shadow: var(--shadow-brutal-subtle);
	}

	.stat-label {
		font-size: 0.8rem;
		color: hsl(var(--muted-foreground));
		text-transform: uppercase;
		letter-spacing: 0.05em;
		font-weight: 800;
	}

	.stat-value {
		font-size: 1.2rem;
		font-weight: 900;
	}

	.table-container {
		border: 2px solid hsl(var(--border));
		box-shadow: var(--shadow-brutal-subtle);
	}

	.metrics-table {
		width: 100%;
		border-collapse: collapse;
	}

	.metrics-table th,
	.metrics-table td {
		padding: 0.75rem 0.85rem;
		border: 2px solid hsl(var(--border));
	}

	.metrics-table th {
		background: hsl(var(--secondary));
		text-transform: uppercase;
		letter-spacing: 0.05em;
		font-weight: 900;
		color: hsl(var(--foreground));
	}

	.metrics-table td {
		background: hsl(var(--card));
	}

	.severity-low { color: #33ff00; }
	.severity-medium { color: #f59e0b; }
	.severity-high { color: #ff3333; }

	.empty-state {
		flex-direction: column;
	}

	.providers-grid {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
		gap: 0.75rem;
	}

	.provider-card {
		border: 2px solid hsl(var(--border));
		background: hsl(var(--card));
		padding: 0.9rem;
		box-shadow: var(--shadow-brutal-subtle);
		display: flex;
		flex-direction: column;
		gap: 0.75rem;
	}

	.provider-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding-bottom: 0.6rem;
		border-bottom: 2px solid hsl(var(--border));
	}

	.provider-name {
		font-weight: 900;
		letter-spacing: 0.04em;
		text-transform: uppercase;
	}

	.provider-subtitle {
		font-size: 0.85rem;
		color: hsl(var(--muted-foreground));
	}

	.provider-badges {
		display: flex;
		gap: 0.4rem;
		flex-wrap: wrap;
	}

	.badge {
		border: 2px solid hsl(var(--border));
		background: hsl(var(--card));
		box-shadow: var(--shadow-brutal-subtle);
		font-weight: 800;
		text-transform: uppercase;
		letter-spacing: 0.04em;
		padding: 0.35rem 0.55rem;
	}

	.badge.success { color: #33ff00; }
	.badge.warn { color: #f59e0b; }
	.badge.info { color: hsl(var(--foreground)); }

	.provider-body {
		display: grid;
		grid-template-columns: repeat(2, 1fr);
		gap: 0.75rem;
	}

	.metric-block {
		display: flex;
		flex-direction: column;
		gap: 0.15rem;
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

	.metric-trend {
		font-size: 0.8rem;
		color: hsl(var(--muted-foreground));
	}

	.comparison-section {
		border: 2px solid hsl(var(--border));
		background: hsl(var(--card));
		box-shadow: var(--shadow-brutal-subtle);
		padding: 1rem;
		display: flex;
		flex-direction: column;
		gap: 0.75rem;
	}

	.comparison-title {
		margin: 0;
		font-weight: 900;
		text-transform: uppercase;
		letter-spacing: 0.04em;
	}

	.comparison-table {
		display: flex;
		flex-direction: column;
		gap: 0.35rem;
	}

	.table-header,
	.table-row {
		display: grid;
		grid-template-columns: 2fr repeat(5, 1fr);
		gap: 0.5rem;
		align-items: center;
		padding: 0.6rem 0.75rem;
		border: 2px solid hsl(var(--border));
		background: hsl(var(--card));
	}

	.table-header {
		background: hsl(var(--secondary));
		font-weight: 900;
		text-transform: uppercase;
		letter-spacing: 0.05em;
	}

	.provider-dot {
		width: 10px;
		height: 10px;
		display: inline-block;
		margin-right: 0.35rem;
	}

	.high-error {
		color: #ff3333;
	}

	.no-chart-data {
		border: 2px dashed hsl(var(--border));
		padding: 1rem;
		text-align: center;
		color: hsl(var(--muted-foreground));
	}

	.stat-item {
		font-weight: 800;
	}

	@media (max-width: 768px) {
		.header,
		.chart-header {
			flex-direction: column;
			align-items: flex-start;
		}

		.provider-body {
			grid-template-columns: 1fr;
		}

		.table-header,
		.table-row {
			grid-template-columns: 1fr;
		}
	}
</style>

