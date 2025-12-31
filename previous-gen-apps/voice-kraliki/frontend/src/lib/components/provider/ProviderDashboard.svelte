<script lang="ts">
	/**
	 * Provider Dashboard Component
	 *
	 * Comprehensive provider management interface:
	 * - Real-time provider health monitoring
	 * - Interactive provider selection
	 * - Performance metrics visualization
	 * - Provider switching capabilities
	 * - Health status indicators
	 */

	import { onMount, onDestroy } from 'svelte';
	import { Settings, Activity, Zap, AlertTriangle, CheckCircle, XCircle, Clock } from 'lucide-svelte';

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

	interface ProviderInfo {
		id: string;
		name: string;
		type: string;
		description: string;
		capabilities: {
			realtime: boolean;
			streaming: boolean;
			multimodal: boolean;
			functionCalling: boolean;
		};
		costTier: 'standard' | 'premium';
		icon: string;
		color: string;
	}

	interface Props {
		autoRefresh?: boolean;
		refreshInterval?: number;
		compact?: boolean;
		allowSwitching?: boolean;
		currentProvider?: string | null;
		onProviderSwitch?: (providerId: string) => void | Promise<void>;
	}

	let {
		autoRefresh = true,
		refreshInterval = 15000,
		compact = false,
		allowSwitching = true,
		currentProvider = null,
		onProviderSwitch
	}: Props = $props();

	// State
	let providers = $state<Record<string, ProviderMetrics>>({});
	let isLoading = $state(true);
	let lastUpdate = $state<Date | null>(null);
	let error = $state<string | null>(null);
	let selectedProvider = $state<string | null>(currentProvider);
	let isSwitching = $state(false);
	let refreshTimer: ReturnType<typeof setInterval> | null = null;

	// Provider information registry
	const providerRegistry: Record<string, ProviderInfo> = {
		gemini: {
			id: 'gemini',
			name: 'Google Gemini',
			type: 'gemini',
			description: 'Multimodal AI with real-time capabilities',
			capabilities: {
				realtime: true,
				streaming: true,
				multimodal: true,
				functionCalling: true
			},
			costTier: 'standard',
			icon: '🤖',
			color: '#4285f4'
		},
		openai: {
			id: 'openai',
			name: 'OpenAI Realtime',
			type: 'openai',
			description: 'GPT-4 with real-time voice processing',
			capabilities: {
				realtime: true,
				streaming: true,
				multimodal: false,
				functionCalling: true
			},
			costTier: 'premium',
			icon: '🔷',
			color: '#10a37f'
		},
		deepgram_nova3: {
			id: 'deepgram_nova3',
			name: 'Deepgram Nova 3',
			type: 'deepgram',
			description: 'State-of-the-art speech recognition',
			capabilities: {
				realtime: true,
				streaming: true,
				multimodal: false,
				functionCalling: false
			},
			costTier: 'premium',
			icon: '🎙️',
			color: '#ff6b35'
		},
		twilio: {
			id: 'twilio',
			name: 'Twilio',
			type: 'twilio',
			description: 'Telephony and voice services',
			capabilities: {
				realtime: true,
				streaming: true,
				multimodal: false,
				functionCalling: false
			},
			costTier: 'standard',
			icon: '📞',
			color: '#f22f46'
		},
		telnyx: {
			id: 'telnyx',
			name: 'Telnyx',
			type: 'telnyx',
			description: 'Communications and voice API',
			capabilities: {
				realtime: true,
				streaming: true,
				multimodal: false,
				functionCalling: false
			},
			costTier: 'standard',
			icon: '🌐',
			color: '#00d4aa'
		}
	};

	// Status configuration
	const statusConfig = {
		healthy: {
			icon: CheckCircle,
			color: '#10b981',
			bgColor: '#d1fae5',
			borderColor: '#10b981',
			text: 'Healthy'
		},
		degraded: {
			icon: AlertTriangle,
			color: '#f59e0b',
			bgColor: '#fef3c7',
			borderColor: '#f59e0b',
			text: 'Degraded'
		},
		unhealthy: {
			icon: XCircle,
			color: '#ef4444',
			bgColor: '#fee2e2',
			borderColor: '#ef4444',
			text: 'Unhealthy'
		},
		offline: {
			icon: XCircle,
			color: '#6b7280',
			bgColor: '#f3f4f6',
			borderColor: '#6b7280',
			text: 'Offline'
		},
		unknown: {
			icon: Clock,
			color: '#9ca3af',
			bgColor: '#f3f4f6',
			borderColor: '#9ca3af',
			text: 'Unknown'
		}
	};

	/**
	 * Fetch provider health data from API
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
	 * Handle provider switching
	 */
	async function handleProviderSwitch(providerId: string) {
		if (!allowSwitching || isSwitching || providerId === selectedProvider) return;

		isSwitching = true;
		try {
			if (onProviderSwitch) {
				await onProviderSwitch(providerId);
			}
			selectedProvider = providerId;
		} catch (error) {
			console.error('Failed to switch provider:', error);
		} finally {
			isSwitching = false;
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
	 * Get status configuration for a provider
	 */
	function getStatusConfig(status: string) {
		return statusConfig[status as keyof typeof statusConfig] || statusConfig.unknown;
	}

	/**
	 * Get provider info from registry
	 */
	function getProviderInfo(providerId: string): ProviderInfo | null {
		return providerRegistry[providerId] || null;
	}

	/**
	 * Calculate overall health score
	 */
	function getOverallHealthScore(): number {
		const providerList = Object.values(providers);
		if (providerList.length === 0) return 0;

		const healthyCount = providerList.filter(p => p.status === 'healthy').length;
		return Math.round((healthyCount / providerList.length) * 100);
	}

	/**
	 * Get average latency across all providers
	 */
	function getAverageLatency(): number {
		const providerList = Object.values(providers);
		if (providerList.length === 0) return 0;

		const totalLatency = providerList.reduce((sum, p) => sum + p.average_latency_ms, 0);
		return Math.round(totalLatency / providerList.length);
	}

	// Lifecycle
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

<div class="provider-dashboard" class:compact>
	<!-- Header -->
	<div class="dashboard-header">
		<div class="header-content">
			<div class="title-section">
				<div class="title-with-icon">
					<Settings class="title-icon" />
					<h2 class="title">Provider Dashboard</h2>
				</div>
				{#if lastUpdate}
					<span class="last-update">Updated {lastUpdate.toLocaleTimeString()}</span>
				{/if}
			</div>
			
			<!-- Overall Stats -->
			<div class="overall-stats">
				<div class="stat-item">
					<span class="stat-label">Health Score</span>
					<span class="stat-value">{getOverallHealthScore()}%</span>
				</div>
				<div class="stat-item">
					<span class="stat-label">Avg Latency</span>
					<span class="stat-value">{formatLatency(getAverageLatency())}</span>
				</div>
				<div class="stat-item">
					<span class="stat-label">Providers</span>
					<span class="stat-value">{Object.keys(providers).length}</span>
				</div>
			</div>
		</div>
		
		<button class="refresh-btn" onclick={fetchProviderHealth} disabled={isLoading}>
			<span class:spinning={isLoading}>
				<Activity class="refresh-icon" />
			</span>
			Refresh
		</button>
	</div>

	<!-- Error Display -->
	{#if error}
		<div class="error-banner">
			<AlertTriangle class="error-icon" />
			<span class="error-text">{error}</span>
		</div>
	{/if}

	<!-- Provider Grid -->
	<div class="providers-grid" class:compact>
		{#if isLoading && Object.keys(providers).length === 0}
			<div class="loading-state">
				<div class="loading-spinner"></div>
				<span>Loading provider health...</span>
			</div>
		{:else if Object.keys(providers).length === 0}
			<div class="empty-state">
				<Settings class="empty-icon" />
				<h3>No Provider Data</h3>
				<p>Unable to load provider health information</p>
			</div>
		{:else}
			{#each Object.entries(providers) as [providerId, metrics]}
				{@const providerInfo = getProviderInfo(providerId)}
				{@const statusConfig = getStatusConfig(metrics.status)}
				{@const isSelected = selectedProvider === providerId}
				
				<div 
					class="provider-card" 
					class:selected={isSelected}
					class:switchable={allowSwitching}
					style="border-color: {statusConfig.borderColor}"
				>
					<!-- Card Header -->
					<div class="card-header">
						<div class="provider-info">
							<div class="provider-icon" style="background: {providerInfo?.color || '#6b7280'}">
								<span class="icon-emoji">{providerInfo?.icon || '⚡'}</span>
							</div>
							<div class="provider-details">
								<h3 class="provider-name">
									{providerInfo?.name || providerId}
								</h3>
								<p class="provider-description">
									{providerInfo?.description || 'AI Provider'}
								</p>
							</div>
						</div>
						
						<div class="status-section">
							<div class="status-badge" style="background: {statusConfig.bgColor}; color: {statusConfig.color};">
								<svelte:component this={statusConfig.icon} class="status-icon" />
								<span class="status-text">{statusConfig.text}</span>
							</div>
							
							{#if allowSwitching}
								<button 
									class="switch-btn"
									class:active={isSelected}
									class:loading={isSwitching}
									onclick={() => handleProviderSwitch(providerId)}
									disabled={isSwitching || metrics.status === 'offline'}
								>
									{#if isSelected}
										<CheckCircle class="btn-icon" />
										Active
									{:else if isSwitching}
										<div class="btn-spinner"></div>
										Switching...
									{:else}
										<Zap class="btn-icon" />
										Switch
									{/if}
								</button>
							{/if}
						</div>
					</div>

					{#if !compact}
						<!-- Capabilities -->
						{#if providerInfo}
							<div class="capabilities">
								{#each Object.entries(providerInfo.capabilities) as [key, enabled]}
									{#if enabled}
										<span class="capability-badge">{key}</span>
									{/if}
								{/each}
								<span class="cost-tier" class:premium={providerInfo.costTier === 'premium'}>
									{providerInfo.costTier}
								</span>
							</div>
						{/if}

						<!-- Metrics -->
						<div class="metrics-row">
							<div class="metric">
								<span class="metric-label">Latency</span>
								<span class="metric-value">{formatLatency(metrics.average_latency_ms)}</span>
							</div>
							<div class="metric">
								<span class="metric-label">Uptime</span>
								<span class="metric-value">{metrics.uptime_percentage.toFixed(1)}%</span>
							</div>
							<div class="metric">
								<span class="metric-label">Success</span>
								<span class="metric-value">{metrics.success_rate.toFixed(1)}%</span>
							</div>
						</div>

						<!-- Progress Bar -->
						<div class="progress-section">
							<div class="progress-label">
								<span>Uptime</span>
								<span>{metrics.uptime_percentage.toFixed(1)}%</span>
							</div>
							<div class="progress-bar">
								<div 
									class="progress-fill" 
									style="width: {metrics.uptime_percentage}%; background: {statusConfig.color};"
								></div>
							</div>
						</div>

						<!-- Warnings -->
						{#if metrics.consecutive_failures > 0}
							<div class="warning">
								<AlertTriangle class="warning-icon" />
								<span>{metrics.consecutive_failures} consecutive failures</span>
							</div>
						{/if}

						{#if metrics.last_error}
							<div class="error-details" title={metrics.last_error}>
								<span class="error-label">Last error:</span>
								<span class="error-text">{metrics.last_error.substring(0, 60)}...</span>
							</div>
						{/if}
					{/if}
				</div>
			{/each}
		{/if}
	</div>

	<!-- Switching Indicator -->
	{#if isSwitching}
		<div class="switching-overlay">
			<div class="switching-content">
				<div class="switching-spinner"></div>
				<span>Switching providers...</span>
			</div>
		</div>
	{/if}
</div>

<style>
	.provider-dashboard {
		background: hsl(var(--card));
		padding: 1.5rem;
		box-shadow: var(--shadow-brutal);
		border: 2px solid hsl(var(--border));
		position: relative;
		color: hsl(var(--foreground));
	}

	.provider-dashboard.compact {
		padding: 1rem;
	}

	.dashboard-header {
		display: flex;
		justify-content: space-between;
		align-items: flex-start;
		margin-bottom: 2rem;
		gap: 1rem;
	}

	.header-content {
		display: flex;
		justify-content: space-between;
		align-items: center;
		flex: 1;
		gap: 2rem;
	}

	.title-section {
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
	}

	.title-with-icon {
		display: flex;
		align-items: center;
		gap: 0.75rem;
	}

	.title-icon {
		width: 24px;
		height: 24px;
		color: #6b7280;
	}

	.title {
		font-size: 1.5rem;
		font-weight: 700;
		color: #1f2937;
		margin: 0;
	}

	.last-update {
		font-size: 0.875rem;
		color: #9ca3af;
	}

	.overall-stats {
		display: flex;
		gap: 2rem;
	}

	.stat-item {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 0.25rem;
	}

	.stat-label {
		font-size: 0.75rem;
		color: #6b7280;
		font-weight: 500;
		text-transform: uppercase;
		letter-spacing: 0.05em;
	}

	.stat-value {
		font-size: 1.25rem;
		font-weight: 700;
		color: #1f2937;
	}

	.refresh-btn {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		padding: 0.625rem 1.25rem;
		background: #f8fafc;
		border: 1px solid #e2e8f0;
		border-radius: 8px;
		font-size: 0.875rem;
		font-weight: 500;
		color: #475569;
		cursor: pointer;
		transition: all 0.2s ease;
	}

	.refresh-btn:hover:not(:disabled) {
		background: #f1f5f9;
		border-color: #cbd5e1;
	}

	.refresh-btn:disabled {
		opacity: 0.6;
		cursor: not-allowed;
	}

	.refresh-icon {
		width: 16px;
		height: 16px;
	}

	.refresh-icon.spinning {
		animation: spin 1s linear infinite;
	}

	@keyframes spin {
		from { transform: rotate(0deg); }
		to { transform: rotate(360deg); }
	}

	.error-banner {
		display: flex;
		align-items: center;
		gap: 0.75rem;
		padding: 1rem;
		background: #fef2f2;
		border: 1px solid #fecaca;
		border-radius: 8px;
		margin-bottom: 1.5rem;
	}

	.error-icon {
		width: 20px;
		height: 20px;
		color: #ef4444;
	}

	.error-text {
		font-size: 0.875rem;
		color: #991b1b;
	}

	.providers-grid {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
		gap: 1.5rem;
	}

	.providers-grid.compact {
		grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
		gap: 1rem;
	}

	.loading-state, .empty-state {
		grid-column: 1 / -1;
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		padding: 3rem;
		color: #6b7280;
		text-align: center;
	}

	.loading-spinner {
		width: 40px;
		height: 40px;
		border: 3px solid #e5e7eb;
		border-top: 3px solid #3b82f6;
		border-radius: 50%;
		animation: spin 1s linear infinite;
		margin-bottom: 1rem;
	}

	.empty-icon {
		width: 48px;
		height: 48px;
		color: #d1d5db;
		margin-bottom: 1rem;
	}

		.provider-card {
			border: 2px solid hsl(var(--border));
			padding: 1.5rem;
			background: hsl(var(--card));
			position: relative;
			box-shadow: var(--shadow-brutal-subtle);
			transition: transform 60ms linear, box-shadow 60ms linear;
		}

		.provider-card.switchable:hover {
			transform: translate(2px, 2px);
			box-shadow: 2px 2px 0px 0px hsl(var(--foreground));
		}

		.provider-card.selected {
			background: hsl(var(--card));
			border-color: hsl(var(--border));
			box-shadow: var(--shadow-brutal);
		}

	.card-header {
		display: flex;
		justify-content: space-between;
		align-items: flex-start;
		margin-bottom: 1rem;
		gap: 1rem;
	}

	.provider-info {
		display: flex;
		align-items: flex-start;
		gap: 1rem;
		flex: 1;
	}

		.provider-icon {
			width: 48px;
			height: 48px;
			display: flex;
			align-items: center;
			justify-content: center;
			flex-shrink: 0;
			border: 2px solid hsl(var(--border));
			box-shadow: var(--shadow-brutal-subtle);
		}

	.icon-emoji {
		font-size: 1.5rem;
	}

	.provider-details {
		flex: 1;
	}

	.provider-name {
		font-size: 1.125rem;
		font-weight: 600;
		color: #1f2937;
		margin: 0 0 0.25rem 0;
	}

	.provider-description {
		font-size: 0.875rem;
		color: #6b7280;
		margin: 0;
		line-height: 1.4;
	}

	.status-section {
		display: flex;
		flex-direction: column;
		align-items: flex-end;
		gap: 0.75rem;
	}

	.status-badge {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		padding: 0.375rem 0.75rem;
		border-radius: 20px;
		font-size: 0.75rem;
		font-weight: 600;
		text-transform: uppercase;
		letter-spacing: 0.05em;
	}

	.status-icon {
		width: 14px;
		height: 14px;
	}

	.switch-btn {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		padding: 0.5rem 1rem;
		background: white;
		border: 2px solid #e5e7eb;
		border-radius: 8px;
		font-size: 0.875rem;
		font-weight: 500;
		color: #6b7280;
		cursor: pointer;
		transition: all 0.2s ease;
	}

	.switch-btn:hover:not(:disabled) {
		border-color: #3b82f6;
		color: #3b82f6;
		background: #f8fafc;
	}

	.switch-btn.active {
		background: #3b82f6;
		border-color: #3b82f6;
		color: white;
	}

	.switch-btn.loading {
		opacity: 0.7;
		cursor: not-allowed;
	}

	.btn-icon {
		width: 16px;
		height: 16px;
	}

	.btn-spinner {
		width: 16px;
		height: 16px;
		border: 2px solid #e5e7eb;
		border-top: 2px solid currentColor;
		border-radius: 50%;
		animation: spin 1s linear infinite;
	}

	.capabilities {
		display: flex;
		flex-wrap: wrap;
		gap: 0.5rem;
		margin-bottom: 1rem;
	}

		.capability-badge {
			padding: 0.25rem 0.625rem;
			background: hsl(var(--card));
			color: hsl(var(--foreground));
			border: 2px solid hsl(var(--border));
			font-size: 0.75rem;
			font-weight: 800;
			text-transform: uppercase;
			letter-spacing: 0.04em;
			box-shadow: var(--shadow-brutal-subtle);
		}

		.cost-tier {
			padding: 0.25rem 0.625rem;
			background: hsl(var(--card));
			color: hsl(var(--muted-foreground));
			border: 2px solid hsl(var(--border));
			font-size: 0.75rem;
			font-weight: 800;
			text-transform: uppercase;
			letter-spacing: 0.04em;
			box-shadow: var(--shadow-brutal-subtle);
		}

		.cost-tier.premium {
			background: hsl(var(--primary));
			color: hsl(var(--primary-foreground));
		}

	.metrics-row {
		display: grid;
		grid-template-columns: repeat(3, 1fr);
		gap: 1rem;
		margin-bottom: 1rem;
	}

	.metric {
		display: flex;
		flex-direction: column;
		gap: 0.25rem;
	}

	.metric-label {
		font-size: 0.75rem;
		color: #6b7280;
		font-weight: 500;
	}

	.metric-value {
		font-size: 1rem;
		font-weight: 700;
		color: #1f2937;
	}

	.progress-section {
		margin-bottom: 1rem;
	}

	.progress-label {
		display: flex;
		justify-content: space-between;
		font-size: 0.75rem;
		color: #6b7280;
		font-weight: 500;
		margin-bottom: 0.5rem;
	}

	.progress-bar {
		height: 8px;
		background: #f3f4f6;
		border-radius: 4px;
		overflow: hidden;
	}

	.progress-fill {
		height: 100%;
		transition: width 0.3s ease;
	}

	.warning {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		padding: 0.75rem;
		background: hsl(var(--accent) / 0.2);
		color: hsl(var(--foreground));
		border: 2px solid hsl(var(--border));
		box-shadow: var(--shadow-brutal-subtle);
		font-size: 0.9rem;
		margin-bottom: 0.75rem;
	}

	.warning-icon {
		width: 16px;
		height: 16px;
		flex-shrink: 0;
	}

	.error-details {
		display: flex;
		flex-direction: column;
		gap: 0.25rem;
		padding: 0.75rem;
		background: hsl(var(--destructive) / 0.15);
		color: hsl(var(--foreground));
		border: 2px solid hsl(var(--border));
		box-shadow: var(--shadow-brutal-subtle);
		font-size: 0.85rem;
	}

	.error-label {
		font-weight: 600;
	}

	.error-text {
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
	}

	.switching-overlay {
		position: absolute;
		top: 0;
		left: 0;
		right: 0;
		bottom: 0;
		background: hsl(var(--card) / 0.95);
		display: flex;
		align-items: center;
		justify-content: center;
		border: 2px solid hsl(var(--border));
		z-index: 10;
	}

	.switching-content {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 1rem;
		color: #374151;
	}

	.switching-spinner {
		width: 32px;
		height: 32px;
		border: 3px solid hsl(var(--border));
		border-top: 3px solid hsl(var(--primary));
		animation: spin 1s linear infinite;
	}

	@media (max-width: 768px) {
		.dashboard-header {
			flex-direction: column;
			align-items: stretch;
		}

		.header-content {
			flex-direction: column;
			align-items: stretch;
			gap: 1rem;
		}

		.overall-stats {
			justify-content: space-around;
		}

		.providers-grid {
			grid-template-columns: 1fr;
		}

		.card-header {
			flex-direction: column;
			align-items: stretch;
			gap: 1rem;
		}

		.status-section {
			align-items: stretch;
		}

		.switch-btn {
			justify-content: center;
		}
	}
</style>
