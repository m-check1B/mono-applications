<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import { createEnhancedWebSocket, type ConnectionStatus, type EnhancedWebSocketCallbacks } from '$lib/services/enhancedWebSocket';
	import { fly } from 'svelte/transition';
	
	export let sessionId: string;
	export let compact = false;
	
	let wsClient: ReturnType<typeof createEnhancedWebSocket> | null = null;
	let status: ConnectionStatus | null = null;
	let showDetails = false;
	
	// Status colors and icons
	const statusConfig = {
		connecting: { color: 'text-yellow-600', bg: 'bg-yellow-100', icon: '⏳', label: 'Connecting' },
		connected: { color: 'text-green-600', bg: 'bg-green-100', icon: '✅', label: 'Connected' },
		disconnecting: { color: 'text-yellow-600', bg: 'bg-yellow-100', icon: '🔄', label: 'Disconnecting' },
		disconnected: { color: 'text-red-600', bg: 'bg-red-100', icon: '❌', label: 'Disconnected' },
		reconnecting: { color: 'text-yellow-600', bg: 'bg-yellow-100', icon: '🔄', label: 'Reconnecting' },
		error: { color: 'text-red-600', bg: 'bg-red-100', icon: '🚨', label: 'Error' }
	};
	
	const qualityConfigMap = {
		excellent: { color: 'text-green-600', icon: '🟢', label: 'Excellent' },
		good: { color: 'text-blue-600', icon: '🔵', label: 'Good' },
		fair: { color: 'text-yellow-600', icon: '🟡', label: 'Fair' },
		poor: { color: 'text-orange-600', icon: '🟠', label: 'Poor' },
		disconnected: { color: 'text-red-600', icon: '🔴', label: 'Disconnected' }
	};
	
	onMount(() => {
		if (sessionId) {
			initializeWebSocket();
		}
	});
	
	onDestroy(() => {
		if (wsClient) {
			wsClient.disconnect();
		}
	});
	
	function initializeWebSocket() {
		const callbacks: EnhancedWebSocketCallbacks = {
			onConnecting: () => {
				updateStatus();
			},
			onConnected: (newStatus) => {
				status = newStatus;
			},
			onDisconnecting: () => {
				updateStatus();
			},
			onDisconnected: (newStatus) => {
				status = newStatus;
			},
			onReconnecting: (attempt, maxAttempts) => {
				updateStatus();
				console.log(`Reconnection attempt ${attempt}/${maxAttempts}`);
			},
			onError: (error, newStatus) => {
				status = newStatus;
				console.error('WebSocket error:', error);
			},
			onHeartbeat: (latency) => {
				updateStatus();
			},
			onConnectionQualityChange: (quality) => {
				updateStatus();
				console.log('Connection quality changed to:', quality);
			},
			onUnhealthyConnection: (newStatus) => {
				status = newStatus;
				console.warn('Connection is unhealthy:', newStatus);
			}
		};
		
		wsClient = createEnhancedWebSocket(sessionId, callbacks, {
			heartbeatInterval: 15000, // 15 seconds for demo
			maxReconnectAttempts: 5,
			initialReconnectDelay: 1000,
			maxReconnectDelay: 10000
		});
	}
	
	function updateStatus() {
		if (wsClient) {
			status = wsClient.getStatus();
		}
	}
	
	function formatDuration(ms: number | null): string {
		if (!ms) return 'N/A';
		const seconds = Math.floor(ms / 1000);
		const minutes = Math.floor(seconds / 60);
		const hours = Math.floor(minutes / 60);
		
		if (hours > 0) {
			return `${hours}h ${minutes % 60}m`;
		} else if (minutes > 0) {
			return `${minutes}m ${seconds % 60}s`;
		} else {
			return `${seconds}s`;
		}
	}
	
	function formatLatency(ms: number): string {
		if (ms < 1000) {
			return `${Math.round(ms)}ms`;
		} else {
			return `${(ms / 1000).toFixed(1)}s`;
		}
	}
	
	$: currentConfig = status ? statusConfig[status.state] : statusConfig.disconnected;
	$: currentQualityConfig = status ? qualityConfigMap[status.metrics.connectionQuality] : qualityConfigMap.disconnected;
</script>

{#if compact}
	<!-- Compact view -->
	<div class="flex items-center gap-2 p-2 rounded-lg border {currentConfig.bg} transition-all duration-200">
		<span class="text-lg">{currentConfig.icon}</span>
		<span class="text-sm font-medium {currentConfig.color}">{currentConfig.label}</span>
		{#if status && status.metrics.averageLatency > 0}
			<span class="text-xs text-gray-500">{formatLatency(status.metrics.averageLatency)}</span>
		{/if}
	</div>
{:else}
	<!-- Full view -->
	<div class="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
		<div class="flex items-center justify-between mb-3">
			<h3 class="text-lg font-semibold text-gray-900">Connection Status</h3>
			<button
				onclick={() => showDetails = !showDetails}
				class="text-sm text-blue-600 hover:text-blue-800 transition-colors"
			>
				{showDetails ? 'Hide Details' : 'Show Details'}
			</button>
		</div>
		
		<!-- Status Overview -->
		<div class="flex items-center gap-3 mb-4">
			<div class="flex items-center gap-2 p-3 rounded-lg {currentConfig.bg} flex-1">
				<span class="text-2xl">{currentConfig.icon}</span>
				<div>
					<div class="font-medium {currentConfig.color}">{currentConfig.label}</div>
					{#if status}
						<div class="text-sm text-gray-600">
							Quality: {currentQualityConfig.label} {currentQualityConfig.icon}
						</div>
					{/if}
				</div>
			</div>
			
			{#if status}
				<div class="text-right">
					<div class="text-sm text-gray-500">Health</div>
					<div class="font-medium {status.isHealthy ? 'text-green-600' : 'text-red-600'}">
						{status.isHealthy ? 'Healthy' : 'Unhealthy'}
					</div>
				</div>
			{/if}
		</div>
		
		{#if showDetails && status}
			<div transition:fly={{ y: 10 }} class="space-y-3 border-t pt-4">
				<!-- Connection Metrics -->
				<div class="grid grid-cols-2 gap-4">
					<div>
						<div class="text-sm text-gray-500">Connected For</div>
						<div class="font-medium">
							{status.metrics.connectedAt 
								? formatDuration(Date.now() - status.metrics.connectedAt)
								: 'Not connected'
							}
						</div>
					</div>
					
					<div>
						<div class="text-sm text-gray-500">Average Latency</div>
						<div class="font-medium">
							{status.metrics.averageLatency > 0 
								? formatLatency(status.metrics.averageLatency)
								: 'N/A'
							}
						</div>
					</div>
					
					<div>
						<div class="text-sm text-gray-500">Reconnect Attempts</div>
						<div class="font-medium">{status.metrics.reconnectAttempts}</div>
					</div>
					
					<div>
						<div class="text-sm text-gray-500">Total Disconnections</div>
						<div class="font-medium">{status.metrics.totalDisconnections}</div>
					</div>
				</div>
				
				<!-- Timeline -->
				{#if status.metrics.connectedAt}
					<div>
						<div class="text-sm text-gray-500 mb-2">Connection Timeline</div>
						<div class="space-y-1 text-sm">
							{#if status.metrics.connectedAt}
								<div class="flex justify-between">
									<span>Connected at:</span>
									<span>{new Date(status.metrics.connectedAt).toLocaleTimeString()}</span>
								</div>
							{/if}
							{#if status.metrics.lastPingAt}
								<div class="flex justify-between">
									<span>Last ping:</span>
									<span>{new Date(status.metrics.lastPingAt).toLocaleTimeString()}</span>
								</div>
							{/if}
							{#if status.metrics.lastPongAt}
								<div class="flex justify-between">
									<span>Last pong:</span>
									<span>{new Date(status.metrics.lastPongAt).toLocaleTimeString()}</span>
								</div>
							{/if}
						</div>
					</div>
				{/if}
				
				<!-- Actions -->
				<div class="flex gap-2 pt-2">
					{#if wsClient}
						{#if wsClient.isConnected()}
							<button
								onclick={() => wsClient?.disconnect()}
								class="px-3 py-1 bg-red-600 text-white rounded hover:bg-red-700 transition-colors text-sm"
							>
								Disconnect
							</button>
						{:else}
							<button
								onclick={() => wsClient?.connect()}
								class="px-3 py-1 bg-green-600 text-white rounded hover:bg-green-700 transition-colors text-sm"
							>
								Connect
							</button>
						{/if}
					{/if}
					
					<button
						onclick={updateStatus}
						class="px-3 py-1 bg-gray-600 text-white rounded hover:bg-gray-700 transition-colors text-sm"
					>
						Refresh
					</button>
				</div>
			</div>
		{/if}
	</div>
{/if}