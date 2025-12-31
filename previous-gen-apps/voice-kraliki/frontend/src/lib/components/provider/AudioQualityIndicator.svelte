<script lang="ts">
	/**
	 * Audio Quality Indicator Component
	 *
	 * Real-time audio quality visualization:
	 * - Overall quality score
	 * - Signal-to-noise ratio
	 * - Volume level meters
	 * - Clarity score
	 * - Issue warnings
	 * - Optimization recommendations
	 */

	import { onMount, onDestroy } from 'svelte';

	interface AudioMetrics {
		session_id: string;
		timestamp: string;
		quality_level: 'excellent' | 'good' | 'fair' | 'poor' | 'critical';
		overall_score: number;
		signal_to_noise_ratio_db: number;
		clarity_score: number;
		volume_level_db: number;
		peak_level_db: number;
		dynamic_range_db: number;
		has_clipping: boolean;
		has_dropouts: boolean;
		has_echo: boolean;
		sample_rate_hz: number;
		bit_depth: number;
		channels: number;
		issues: string[];
		recommendations: string[];
	}

	interface Props {
		sessionId: string;
		autoRefresh?: boolean;
		refreshInterval?: number;
		compact?: boolean;
	}

	let {
		sessionId,
		autoRefresh = true,
		refreshInterval = 1000,
		compact = false
	}: Props = $props();

	// State
	let metrics = $state<AudioMetrics | null>(null);
	let isLoading = $state(true);
	let error = $state<string | null>(null);
	let refreshTimer: ReturnType<typeof setInterval> | null = null;

	// Quality level colors and icons
	const qualityConfig = {
		excellent: { color: '#10b981', icon: '★', label: 'Excellent' },
		good: { color: '#84cc16', icon: '✓', label: 'Good' },
		fair: { color: '#f59e0b', icon: '~', label: 'Fair' },
		poor: { color: '#f97316', icon: '!', label: 'Poor' },
		critical: { color: '#ef4444', icon: '✗', label: 'Critical' }
	};

	// Issue icons
	const issueIcons: Record<string, string> = {
		low_volume: '🔉',
		high_volume: '🔊',
		high_noise: '📢',
		low_clarity: '🌫️',
		clipping: '⚡',
		dropouts: '⚠️',
		echo: '🔄'
	};

	/**
	 * Fetch audio quality metrics
	 */
	async function fetchAudioMetrics() {
		if (!sessionId) return;

		try {
			error = null;
			const response = await fetch(`http://localhost:8000/providers/audio/metrics/${sessionId}`);

			if (!response.ok) {
				if (response.status === 404) {
					error = 'No audio metrics available for this session';
					return;
				}
				throw new Error(`HTTP ${response.status}: ${response.statusText}`);
			}

			const data = await response.json();
			metrics = data;
			isLoading = false;
		} catch (err) {
			error = err instanceof Error ? err.message : 'Failed to fetch audio metrics';
			console.error('Failed to fetch audio metrics:', err);
			isLoading = false;
		}
	}

	/**
	 * Get volume bar position (-60 to 0 dB range)
	 */
	function getVolumeBarPosition(db: number): number {
		// Map -60 to 0 dB to 0-100%
		return Math.max(0, Math.min(100, ((db + 60) / 60) * 100));
	}

	/**
	 * Get volume bar color based on level
	 */
	function getVolumeBarColor(db: number): string {
		if (db > -10) return '#ef4444'; // Too loud
		if (db > -20) return '#10b981'; // Good
		if (db > -40) return '#f59e0b'; // Acceptable
		return '#f97316'; // Too quiet
	}

	/**
	 * Format issue name
	 */
	function formatIssueName(issue: string): string {
		return issue.split('_').map(word =>
			word.charAt(0).toUpperCase() + word.slice(1)
		).join(' ');
	}

	// Setup auto-refresh
	onMount(() => {
		fetchAudioMetrics();

		if (autoRefresh) {
			refreshTimer = setInterval(fetchAudioMetrics, refreshInterval);
		}
	});

	onDestroy(() => {
		if (refreshTimer) {
			clearInterval(refreshTimer);
		}
	});
</script>

<div class="audio-quality-indicator" class:compact>
	{#if error}
		<div class="error-state">
			<span class="error-icon">⚠</span>
			<p class="error-text">{error}</p>
		</div>
	{:else if isLoading && !metrics}
		<div class="loading-state">
			<span class="spinner">⟳</span>
			<p>Loading audio metrics...</p>
		</div>
	{:else if metrics}
		{@const quality = qualityConfig[metrics.quality_level]}

		<!-- Header -->
		<div class="header">
			<h4 class="title">Audio Quality</h4>
			<div class="quality-badge" style="background: {quality.color}">
				<span class="quality-icon">{quality.icon}</span>
				<span class="quality-label">{quality.label}</span>
			</div>
		</div>

		<!-- Overall Score -->
		<div class="score-section">
			<div class="score-circle" style="--score: {metrics.overall_score}; --color: {quality.color}">
				<svg class="score-svg" viewBox="0 0 100 100">
					<circle class="score-bg" cx="50" cy="50" r="45"></circle>
					<circle class="score-fill" cx="50" cy="50" r="45"
						style="stroke-dasharray: {(metrics.overall_score / 100) * 283} 283"></circle>
				</svg>
				<div class="score-content">
					<span class="score-value">{Math.round(metrics.overall_score)}</span>
					<span class="score-label">Score</span>
				</div>
			</div>
		</div>

		{#if !compact}
			<!-- Technical Metrics -->
			<div class="metrics-section">
				<div class="metric-row">
					<span class="metric-label">Signal-to-Noise Ratio</span>
					<span class="metric-value">{metrics.signal_to_noise_ratio_db.toFixed(1)} dB</span>
				</div>
				<div class="metric-row">
					<span class="metric-label">Clarity Score</span>
					<span class="metric-value">{(metrics.clarity_score * 100).toFixed(0)}%</span>
				</div>
				<div class="metric-row">
					<span class="metric-label">Dynamic Range</span>
					<span class="metric-value">{metrics.dynamic_range_db.toFixed(1)} dB</span>
				</div>
			</div>

			<!-- Volume Level -->
			<div class="volume-section">
				<div class="volume-header">
					<span class="volume-label">Volume Level</span>
					<span class="volume-value">{metrics.volume_level_db.toFixed(1)} dB</span>
				</div>
				<div class="volume-bar">
					<div class="volume-markers">
						<span class="marker">-60</span>
						<span class="marker">-40</span>
						<span class="marker">-20</span>
						<span class="marker">0</span>
					</div>
					<div class="volume-track">
						<div class="volume-fill"
							style="width: {getVolumeBarPosition(metrics.volume_level_db)}%;
							background: {getVolumeBarColor(metrics.volume_level_db)}"></div>
						<div class="volume-indicator"
							style="left: {getVolumeBarPosition(metrics.volume_level_db)}%;
							background: {getVolumeBarColor(metrics.volume_level_db)}"></div>
					</div>
					<div class="volume-zones">
						<div class="zone quiet">Quiet</div>
						<div class="zone good">Good</div>
						<div class="zone loud">Loud</div>
					</div>
				</div>
			</div>

			<!-- Issues -->
			{#if metrics.issues.length > 0}
				<div class="issues-section">
					<h5 class="issues-title">Issues Detected</h5>
					<div class="issues-list">
						{#each metrics.issues as issue}
							<div class="issue-badge">
								<span class="issue-icon">{issueIcons[issue] || '⚠️'}</span>
								<span class="issue-text">{formatIssueName(issue)}</span>
							</div>
						{/each}
					</div>
				</div>
			{/if}

			<!-- Recommendations -->
			{#if metrics.recommendations.length > 0}
				<div class="recommendations-section">
					<h5 class="recommendations-title">Recommendations</h5>
					<ul class="recommendations-list">
						{#each metrics.recommendations as recommendation}
							<li class="recommendation-item">{recommendation}</li>
						{/each}
					</ul>
				</div>
			{/if}

			<!-- Technical Info -->
			<div class="technical-info">
				<span class="tech-item">{metrics.sample_rate_hz / 1000}kHz</span>
				<span class="tech-item">{metrics.bit_depth}-bit</span>
				<span class="tech-item">{metrics.channels === 1 ? 'Mono' : 'Stereo'}</span>
			</div>
		{/if}
	{:else}
		<div class="no-data">
			<p>No audio quality data available</p>
		</div>
	{/if}
</div>

<style>
	.audio-quality-indicator {
		background: white;
		border-radius: 12px;
		padding: 1.5rem;
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
		border: 1px solid #e5e7eb;
	}

	.audio-quality-indicator.compact {
		padding: 1rem;
	}

	.error-state, .loading-state, .no-data {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		padding: 2rem;
		text-align: center;
		color: #9ca3af;
	}

	.error-icon, .spinner {
		font-size: 2rem;
		margin-bottom: 0.5rem;
	}

	.spinner {
		animation: spin 1s linear infinite;
	}

	@keyframes spin {
		from { transform: rotate(0deg); }
		to { transform: rotate(360deg); }
	}

	.header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 1.5rem;
	}

	.title {
		font-size: 1rem;
		font-weight: 600;
		color: #1f2937;
		margin: 0;
	}

	.quality-badge {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		padding: 0.375rem 0.75rem;
		border-radius: 12px;
		color: white;
		font-size: 0.85rem;
		font-weight: 600;
	}

	.score-section {
		display: flex;
		justify-content: center;
		margin-bottom: 1.5rem;
	}

	.score-circle {
		position: relative;
		width: 120px;
		height: 120px;
	}

	.score-svg {
		width: 100%;
		height: 100%;
		transform: rotate(-90deg);
	}

	.score-bg {
		fill: none;
		stroke: #e5e7eb;
		stroke-width: 8;
	}

	.score-fill {
		fill: none;
		stroke: var(--color);
		stroke-width: 8;
		stroke-linecap: round;
		transition: stroke-dasharray 0.3s ease;
	}

	.score-content {
		position: absolute;
		top: 50%;
		left: 50%;
		transform: translate(-50%, -50%);
		display: flex;
		flex-direction: column;
		align-items: center;
	}

	.score-value {
		font-size: 2rem;
		font-weight: 700;
		color: #1f2937;
		line-height: 1;
	}

	.score-label {
		font-size: 0.75rem;
		color: #6b7280;
		margin-top: 0.25rem;
	}

	.metrics-section {
		display: flex;
		flex-direction: column;
		gap: 0.75rem;
		margin-bottom: 1.5rem;
		padding: 1rem;
		background: #f9fafb;
		border-radius: 8px;
	}

	.metric-row {
		display: flex;
		justify-content: space-between;
		align-items: center;
		font-size: 0.85rem;
	}

	.metric-label {
		color: #6b7280;
		font-weight: 500;
	}

	.metric-value {
		color: #1f2937;
		font-weight: 600;
	}

	.volume-section {
		margin-bottom: 1.5rem;
	}

	.volume-header {
		display: flex;
		justify-content: space-between;
		margin-bottom: 0.75rem;
		font-size: 0.85rem;
	}

	.volume-label {
		color: #6b7280;
		font-weight: 500;
	}

	.volume-value {
		color: #1f2937;
		font-weight: 600;
	}

	.volume-bar {
		position: relative;
	}

	.volume-markers {
		display: flex;
		justify-content: space-between;
		font-size: 0.7rem;
		color: #9ca3af;
		margin-bottom: 0.25rem;
	}

	.volume-track {
		position: relative;
		height: 12px;
		background: #e5e7eb;
		border-radius: 6px;
		overflow: hidden;
	}

	.volume-fill {
		height: 100%;
		transition: width 0.2s ease, background 0.2s ease;
	}

	.volume-indicator {
		position: absolute;
		top: -2px;
		transform: translateX(-50%);
		width: 16px;
		height: 16px;
		border-radius: 50%;
		border: 3px solid white;
		box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
		transition: left 0.2s ease, background 0.2s ease;
	}

	.volume-zones {
		display: flex;
		justify-content: space-between;
		margin-top: 0.5rem;
		font-size: 0.7rem;
	}

	.zone {
		color: #9ca3af;
	}

	.zone.good {
		font-weight: 600;
		color: #10b981;
	}

	.issues-section {
		margin-bottom: 1rem;
	}

	.issues-title {
		font-size: 0.85rem;
		font-weight: 600;
		color: #1f2937;
		margin: 0 0 0.75rem 0;
	}

	.issues-list {
		display: flex;
		flex-wrap: wrap;
		gap: 0.5rem;
	}

	.issue-badge {
		display: flex;
		align-items: center;
		gap: 0.375rem;
		padding: 0.375rem 0.75rem;
		background: #fef2f2;
		border: 1px solid #fecaca;
		border-radius: 12px;
		font-size: 0.75rem;
		color: #991b1b;
	}

	.issue-icon {
		font-size: 1rem;
	}

	.recommendations-section {
		margin-bottom: 1rem;
	}

	.recommendations-title {
		font-size: 0.85rem;
		font-weight: 600;
		color: #1f2937;
		margin: 0 0 0.5rem 0;
	}

	.recommendations-list {
		list-style: none;
		padding: 0;
		margin: 0;
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
	}

	.recommendation-item {
		padding: 0.5rem 0.75rem;
		background: #eff6ff;
		border-left: 3px solid #3b82f6;
		border-radius: 4px;
		font-size: 0.8rem;
		color: #1e40af;
	}

	.technical-info {
		display: flex;
		gap: 1rem;
		justify-content: center;
		padding-top: 1rem;
		border-top: 1px solid #e5e7eb;
	}

	.tech-item {
		font-size: 0.75rem;
		color: #6b7280;
		font-weight: 500;
	}
</style>
