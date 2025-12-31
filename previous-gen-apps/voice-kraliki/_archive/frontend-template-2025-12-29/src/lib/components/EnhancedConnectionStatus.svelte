<script lang="ts">
	/**
	 * Enhanced Connection Status Component
	 * 
	 * Provides comprehensive connection monitoring and recovery:
	 * - Real-time connection quality metrics
	 * - Error detection and recovery suggestions
	 * - Automatic reconnection with backoff
	 * - Provider switching support
	 * - Audio quality monitoring
	 */

	import { onMount, onDestroy } from 'svelte';
	import { browser } from '$app/environment';
	import { 
		Wifi, 
		WifiOff, 
		AlertTriangle, 
		RefreshCw, 
		Activity,
		Volume2,
		VolumeX,
		Settings,
		CheckCircle,
		XCircle
	} from 'lucide-svelte';
	import type { WebRTCStats } from '$lib/services/webrtcManager';
	import { CommonErrors } from '$lib/services/sessionStateManager';

	interface Props {
		stats?: WebRTCStats;
		isLive?: boolean;
		currentProvider?: string;
		onRetry?: () => Promise<void>;
		onSwitchProvider?: () => void;
		onSettings?: () => void;
		showDetails?: boolean;
	}

	let {
		stats = $bindable() as WebRTCStats,
		isLive = false,
		currentProvider = 'unknown',
		onRetry,
		onSwitchProvider,
		onSettings,
		showDetails = false
	}: Props = $props();

	// Local state
	let isExpanded = $state(false);
	let isRetrying = $state(false);
	let lastQualityCheck = $state(Date.now());
	let audioTestActive = $state(false);
	let audioTestResult = $state<'testing' | 'passed' | 'failed' | null>(null);

	// Computed values
	const connectionQuality = $derived(() => {
		if (!stats) return 'unknown';
		
		const { latency, packetLoss, bitrate } = stats;
		
		if (latency < 100 && packetLoss < 1 && bitrate > 50) return 'excellent';
		if (latency < 200 && packetLoss < 3 && bitrate > 30) return 'good';
		if (latency < 500 && packetLoss < 10 && bitrate > 10) return 'fair';
		return 'poor';
	});
	
	const connectionStatus = $derived(() => {
		if (!stats) return 'unknown';
		return stats.connectionState;
	});
	
	const statusColor = $derived(() => {
		switch (connectionQuality()) {
			case 'excellent': return 'text-green-500';
			case 'good': return 'text-blue-500';
			case 'fair': return 'text-yellow-500';
			case 'poor': return 'text-red-500';
			default: return 'text-gray-500';
		}
	});
	
	const statusIcon = $derived(() => {
		switch (connectionStatus()) {
			case 'connected': return CheckCircle;
			case 'connecting': return RefreshCw;
			case 'disconnected': return WifiOff;
			case 'failed': return XCircle;
			case 'reconnecting': return RefreshCw;
			default: return Activity;
		}
	});
	
	const statusText = $derived(() => {
		switch (connectionStatus()) {
			case 'connected': return 'Connected';
			case 'connecting': return 'Connecting...';
			case 'disconnected': return 'Disconnected';
			case 'failed': return 'Connection Failed';
			case 'reconnecting': return 'Reconnecting...';
			default: return 'Unknown';
		}
	});
	
	const qualityText = $derived(() => {
		switch (connectionQuality()) {
			case 'excellent': return 'Excellent';
			case 'good': return 'Good';
			case 'fair': return 'Fair';
			case 'poor': return 'Poor';
			default: return 'Unknown';
		}
	});
	
	const hasWarnings = $derived(() => {
		if (!stats) return false;
		return stats.latency > 300 || stats.packetLoss > 5 || stats.audioLevel < 0.1;
	});
	
	const recommendations = $derived(() => {
		const recommendations: string[] = [];
		
		if (!stats) return recommendations;
		
		if (stats.latency > 300) {
			recommendations.push('High latency detected. Check your internet connection.');
		}
		
		if (stats.packetLoss > 5) {
			recommendations.push('Packet loss detected. Consider switching providers or networks.');
		}
		
		if (stats.audioLevel < 0.1 && isLive) {
			recommendations.push('Low audio input detected. Check your microphone.');
		}
		
		if (stats.bitrate < 20 && isLive) {
			recommendations.push('Low audio quality detected. Check audio settings.');
		}
		
		return recommendations;
	});

	// Audio testing
	async function testAudioQuality(): Promise<void> {
		if (!browser) return;
		
		audioTestActive = true;
		audioTestResult = 'testing';
		
		try {
			// Test microphone access
			const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
			
			// Test audio levels
			const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
			const analyser = audioContext.createAnalyser();
			const source = audioContext.createMediaStreamSource(stream);
			
			source.connect(analyser);
			analyser.fftSize = 256;
			
			const dataArray = new Uint8Array(analyser.frequencyBinCount);
			analyser.getByteFrequencyData(dataArray);
			
			// Calculate average level
			const average = dataArray.reduce((sum, value) => sum + value, 0) / dataArray.length;
			const normalizedLevel = average / 255;
			
			// Cleanup
			stream.getTracks().forEach(track => track.stop());
			await audioContext.close();
			
			audioTestResult = normalizedLevel > 0.1 ? 'passed' : 'failed';
		} catch (error) {
			console.error('Audio test failed:', error);
			audioTestResult = 'failed';
		} finally {
			audioTestActive = false;
		}
	}

	async function handleRetry(): Promise<void> {
		if (isRetrying || !onRetry) return;
		
		isRetrying = true;
		try {
			await onRetry();
		} finally {
			isRetrying = false;
		}
	}

	function formatLatency(ms: number): string {
		if (ms < 1000) return `${Math.round(ms)}ms`;
		return `${(ms / 1000).toFixed(1)}s`;
	}

	function formatBitrate(kbps: number): string {
		if (kbps < 1000) return `${Math.round(kbps)} kbps`;
		return `${(kbps / 1000).toFixed(1)} Mbps`;
	}

	function formatPercentage(value: number): string {
		return `${Math.round(value * 100)}%`;
	}

	// Auto-expand when there are warnings
	$effect(() => {
		if (hasWarnings() && !isExpanded) {
			isExpanded = true;
		}
	});

	// Periodic quality checks
	let qualityCheckInterval: ReturnType<typeof setInterval>;
	
	onMount(() => {
		qualityCheckInterval = setInterval(() => {
			lastQualityCheck = Date.now();
		}, 5000);
	});
	
	onDestroy(() => {
		if (qualityCheckInterval) {
			clearInterval(qualityCheckInterval);
		}
	});
</script>

<div class="connection-status">
	<!-- Compact View -->
	<div class="compact-view" class:expanded={isExpanded} onclick={() => isExpanded = !isExpanded}>
		<div class="status-indicator">
			<svelte:component this={statusIcon()} class="icon {statusColor()} {connectionStatus() === 'connecting' || connectionStatus() === 'reconnecting' ? 'spinning' : ''}" />
			<span class="status-text">{statusText()}</span>
		</div>
		
		<div class="quality-indicator">
			<div class="quality-bar" class:excellent={connectionQuality() === 'excellent'} class:good={connectionQuality() === 'good'} class:fair={connectionQuality() === 'fair'} class:poor={connectionQuality() === 'poor'}>
				<div class="quality-fill"></div>
			</div>
			<span class="quality-text">{qualityText()}</span>
		</div>
		
		{#if hasWarnings()}
			<AlertTriangle class="warning-icon" />
		{/if}
		
		{#if showDetails}
			<Activity class="expand-icon {isExpanded ? 'rotated' : ''}" />
		{/if}
	</div>

	<!-- Expanded View -->
	{#if isExpanded && showDetails}
		<div class="expanded-view">
			<!-- Connection Metrics -->
			<div class="metrics-section">
				<h4>Connection Metrics</h4>
				<div class="metrics-grid">
					<div class="metric">
						<span class="label">Latency</span>
						<span class="value">{stats ? formatLatency(stats.latency) : 'N/A'}</span>
					</div>
					<div class="metric">
						<span class="label">Packet Loss</span>
						<span class="value">{stats ? formatPercentage(stats.packetLoss / 100) : 'N/A'}</span>
					</div>
					<div class="metric">
						<span class="label">Bitrate</span>
						<span class="value">{stats ? formatBitrate(stats.bitrate) : 'N/A'}</span>
					</div>
					<div class="metric">
						<span class="label">Audio Level</span>
						<span class="value">{stats ? formatPercentage(stats.audioLevel) : 'N/A'}</span>
					</div>
				</div>
			</div>

			<!-- Audio Test -->
			<div class="audio-section">
				<h4>Audio Test</h4>
				<div class="audio-test">
					<button 
						type="button"
						class="test-button"
						disabled={audioTestActive}
						onclick={testAudioQuality}
					>
						{#if audioTestActive}
							<RefreshCw class="animate-spin" />
							Testing...
						{:else if audioTestResult === 'passed'}
							<Volume2 class="text-green-500" />
							Mic Working
						{:else if audioTestResult === 'failed'}
							<VolumeX class="text-red-500" />
							Mic Issue
						{:else}
							<Volume2 />
							Test Microphone
						{/if}
					</button>
				</div>
			</div>

			<!-- Recommendations -->
			{#if recommendations().length > 0}
				<div class="recommendations-section">
					<h4>Recommendations</h4>
					<div class="recommendations">
						{#each recommendations() as recommendation}
							<div class="recommendation">
								<AlertTriangle class="icon" />
								<span>{recommendation}</span>
							</div>
						{/each}
					</div>
				</div>
			{/if}

			<!-- Actions -->
			<div class="actions-section">
				<h4>Actions</h4>
				<div class="actions">
					{#if connectionStatus() !== 'connected' && onRetry}
						<button 
							type="button"
							class="action-button primary"
							disabled={isRetrying}
							onclick={handleRetry}
						>
							{#if isRetrying}
								<RefreshCw class="animate-spin" />
								Retrying...
							{:else}
								<RefreshCw />
								Reconnect
							{/if}
						</button>
					{/if}
					
					{#if onSwitchProvider}
						<button 
							type="button"
							class="action-button secondary"
							onclick={onSwitchProvider}
						>
							<Wifi />
							Switch Provider
						</button>
					{/if}
					
					{#if onSettings}
						<button 
							type="button"
							class="action-button secondary"
							onclick={onSettings}
						>
							<Settings />
							Settings
						</button>
					{/if}
				</div>
			</div>

			<!-- Provider Info -->
			<div class="provider-section">
				<h4>Provider</h4>
				<div class="provider-info">
					<span class="provider-name">{currentProvider}</span>
					<span class="provider-status">
						{#if isLive}
							<span class="status-dot live"></span>
							Live
						{:else}
							<span class="status-dot idle"></span>
							Idle
						{/if}
					</span>
				</div>
			</div>
		</div>
	{/if}
</div>

<style>
	.connection-status {
		background: var(--color-surface);
		border: 1px solid var(--color-border);
		border-radius: 12px;
		overflow: hidden;
		transition: all 0.2s ease;
	}

	.compact-view {
		display: flex;
		align-items: center;
		gap: 12px;
		padding: 12px 16px;
		cursor: pointer;
		user-select: none;
	}

	.compact-view:hover {
		background: var(--color-surface-hover);
	}

	.compact-view.expanded {
		border-bottom: 1px solid var(--color-border);
	}

	.status-indicator {
		display: flex;
		align-items: center;
		gap: 8px;
		flex: 1;
	}

	.icon {
		width: 16px;
		height: 16px;
		transition: color 0.2s ease;
	}

	.icon.spinning {
		animation: spin 1s linear infinite;
	}

	@keyframes spin {
		from { transform: rotate(0deg); }
		to { transform: rotate(360deg); }
	}

	.status-text {
		font-size: 14px;
		font-weight: 500;
		color: var(--color-text-primary);
	}

	.quality-indicator {
		display: flex;
		align-items: center;
		gap: 8px;
	}

	.quality-bar {
		width: 60px;
		height: 4px;
		background: var(--color-border);
		border-radius: 2px;
		overflow: hidden;
		position: relative;
	}

	.quality-fill {
		height: 100%;
		width: 100%;
		background: var(--color-border);
		transition: background 0.3s ease;
	}

	.quality-bar.excellent .quality-fill {
		background: #10b981;
		width: 100%;
	}

	.quality-bar.good .quality-fill {
		background: #3b82f6;
		width: 80%;
	}

	.quality-bar.fair .quality-fill {
		background: #f59e0b;
		width: 60%;
	}

	.quality-bar.poor .quality-fill {
		background: #ef4444;
		width: 30%;
	}

	.quality-text {
		font-size: 12px;
		color: var(--color-text-secondary);
		min-width: 50px;
	}

	.warning-icon {
		width: 16px;
		height: 16px;
		color: #f59e0b;
	}

	.expand-icon {
		width: 16px;
		height: 16px;
		color: var(--color-text-secondary);
		transition: transform 0.2s ease;
	}

	.expand-icon.rotated {
		transform: rotate(180deg);
	}

	.expanded-view {
		padding: 16px;
		background: var(--color-surface-secondary);
	}

	.expanded-view h4 {
		font-size: 14px;
		font-weight: 600;
		color: var(--color-text-primary);
		margin-bottom: 12px;
	}

	.metrics-section {
		margin-bottom: 20px;
	}

	.metrics-grid {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
		gap: 12px;
	}

	.metric {
		display: flex;
		flex-direction: column;
		gap: 4px;
		padding: 8px;
		background: var(--color-surface);
		border-radius: 8px;
		border: 1px solid var(--color-border);
	}

	.metric .label {
		font-size: 12px;
		color: var(--color-text-secondary);
	}

	.metric .value {
		font-size: 14px;
		font-weight: 600;
		color: var(--color-text-primary);
	}

	.audio-section {
		margin-bottom: 20px;
	}

	.audio-test {
		display: flex;
		gap: 12px;
	}

	.test-button {
		display: flex;
		align-items: center;
		gap: 8px;
		padding: 8px 16px;
		background: var(--color-surface);
		border: 1px solid var(--color-border);
		border-radius: 8px;
		font-size: 14px;
		color: var(--color-text-primary);
		cursor: pointer;
		transition: all 0.2s ease;
	}

	.test-button:hover:not(:disabled) {
		background: var(--color-surface-hover);
		border-color: var(--color-primary);
	}

	.test-button:disabled {
		opacity: 0.6;
		cursor: not-allowed;
	}

	.recommendations-section {
		margin-bottom: 20px;
	}

	.recommendations {
		display: flex;
		flex-direction: column;
		gap: 8px;
	}

	.recommendation {
		display: flex;
		align-items: center;
		gap: 8px;
		padding: 8px 12px;
		background: #fef3c7;
		border: 1px solid #f59e0b;
		border-radius: 6px;
		font-size: 13px;
		color: #92400e;
	}

	.recommendation .icon {
		width: 14px;
		height: 14px;
		color: #f59e0b;
		flex-shrink: 0;
	}

	.actions-section {
		margin-bottom: 20px;
	}

	.actions {
		display: flex;
		gap: 8px;
		flex-wrap: wrap;
	}

	.action-button {
		display: flex;
		align-items: center;
		gap: 6px;
		padding: 8px 12px;
		border: 1px solid var(--color-border);
		border-radius: 6px;
		font-size: 13px;
		cursor: pointer;
		transition: all 0.2s ease;
	}

	.action-button.primary {
		background: var(--color-primary);
		color: white;
		border-color: var(--color-primary);
	}

	.action-button.primary:hover:not(:disabled) {
		background: var(--color-primary-hover);
	}

	.action-button.secondary {
		background: var(--color-surface);
		color: var(--color-text-primary);
	}

	.action-button.secondary:hover:not(:disabled) {
		background: var(--color-surface-hover);
		border-color: var(--color-primary);
	}

	.action-button:disabled {
		opacity: 0.6;
		cursor: not-allowed;
	}

	.provider-section {
		margin-bottom: 0;
	}

	.provider-info {
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: 8px 12px;
		background: var(--color-surface);
		border: 1px solid var(--color-border);
		border-radius: 6px;
	}

	.provider-name {
		font-size: 14px;
		font-weight: 500;
		color: var(--color-text-primary);
	}

	.provider-status {
		display: flex;
		align-items: center;
		gap: 6px;
		font-size: 12px;
		color: var(--color-text-secondary);
	}

	.status-dot {
		width: 8px;
		height: 8px;
		border-radius: 50%;
	}

	.status-dot.live {
		background: #10b981;
	}

	.status-dot.idle {
		background: #6b7280;
	}
</style>