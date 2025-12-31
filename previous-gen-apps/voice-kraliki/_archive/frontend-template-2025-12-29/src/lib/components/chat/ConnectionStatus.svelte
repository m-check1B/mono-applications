<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import { chatStore } from '$lib/stores/chat';
	import { offlineManager } from '$lib/services/offlineManager';
	import { fly } from 'svelte/transition';
	import { Wifi, WifiOff, AlertCircle, RefreshCw } from 'lucide-svelte';

	let status = $state(offlineManager.getConnectionStatus());
	let isExpanded = $state(false);
	let reconnecting = $state(false);

	// Auto-hide when online and stable
	let hideTimer: number;

	// Subscribe to chat store for connection status updates
	let unsubscribe: () => void;

	onMount(() => {
		unsubscribe = chatStore.subscribe((state) => {
			status = state.connectionStatus;
		});
	});

	onDestroy(() => {
		if (unsubscribe) unsubscribe();
		if (hideTimer) clearTimeout(hideTimer);
	});

	$effect(() => {
		if (status.isOnline && status.queuedMessages === 0) {
			hideTimer = setTimeout(() => {
				isExpanded = false;
			}, 3000);
		} else {
			clearTimeout(hideTimer);
			isExpanded = true;
		}

		return () => clearTimeout(hideTimer);
	});

	async function handleReconnect() {
		reconnecting = true;
		try {
			// Trigger reconnection attempt
			window.location.reload();
		} finally {
			reconnecting = false;
		}
	}

	function getStatusColor() {
		if (!status.isOnline) return 'bg-red-500';
		if (status.queuedMessages > 0) return 'bg-yellow-500';
		return 'bg-green-500';
	}

	function getStatusText() {
		if (!status.isOnline) return 'Offline';
		if (status.queuedMessages > 0) return `${status.queuedMessages} queued`;
		return 'Online';
	}
</script>

<div class="fixed bottom-4 right-4 z-50">
	<div
		class="bg-white rounded-lg shadow-lg border border-gray-200 overflow-hidden transition-all duration-300 {isExpanded ? 'w-80' : 'w-auto'}"
		transition:fly={{ y: 20, duration: 300 }}
	>
		<!-- Status bar -->
		<div
			class="flex items-center gap-2 p-3 cursor-pointer hover:bg-gray-50 transition-colors"
			onclick={() => (isExpanded = !isExpanded)}
		>
			<div class="relative">
				{#if status.isOnline}
					<Wifi class="w-5 h-5 text-green-600" />
				{:else}
					<WifiOff class="w-5 h-5 text-red-600" />
				{/if}
				<div
					class="absolute -top-1 -right-1 w-3 h-3 rounded-full {getStatusColor()}"
					class:animate-pulse={!status.isOnline || status.queuedMessages > 0}
				></div>
			</div>

			<span class="font-medium text-sm">{getStatusText()}</span>

			<div class="flex-1"></div>

			{#if status.queuedMessages > 0}
				<span class="bg-yellow-100 text-yellow-800 text-xs px-2 py-1 rounded-full">
					{status.queuedMessages}
				</span>
			{/if}

			<RefreshCw
				class="w-4 h-4 text-gray-400 transition-transform {reconnecting ? 'animate-spin' : ''}"
			/>
		</div>

		<!-- Expanded details -->
		{#if isExpanded}
			<div class="border-t border-gray-200 p-3 space-y-2">
				<!-- Connection details -->
				<div class="flex items-center justify-between text-sm">
					<span class="text-gray-600">Status:</span>
					<span class="font-medium {status.isOnline ? 'text-green-600' : 'text-red-600'}">
						{status.isOnline ? 'Connected' : 'Disconnected'}
					</span>
				</div>

				{#if status.lastConnected}
					<div class="flex items-center justify-between text-sm">
						<span class="text-gray-600">Last connected:</span>
						<span class="font-medium">
							{new Date(status.lastConnected).toLocaleTimeString()}
						</span>
					</div>
				{/if}

				{#if status.reconnectAttempts > 0}
					<div class="flex items-center justify-between text-sm">
						<span class="text-gray-600">Reconnect attempts:</span>
						<span class="font-medium">{status.reconnectAttempts}</span>
					</div>
				{/if}

				{#if status.queuedMessages > 0}
					<div class="flex items-center justify-between text-sm">
						<span class="text-gray-600">Queued messages:</span>
						<span class="font-medium text-yellow-600">{status.queuedMessages}</span>
					</div>

					<div class="bg-yellow-50 border border-yellow-200 rounded-md p-2">
						<div class="flex items-start gap-2">
							<AlertCircle class="w-4 h-4 text-yellow-600 mt-0.5 flex-shrink-0" />
							<p class="text-xs text-yellow-800">
								Messages will be sent automatically when connection is restored.
							</p>
						</div>
					</div>
				{/if}

				<!-- Actions -->
				<div class="flex gap-2 pt-2">
					{#if !status.isOnline}
						<button
							class="flex-1 bg-blue-600 text-white text-sm px-3 py-1.5 rounded-md hover:bg-blue-700 transition-colors disabled:opacity-50"
							disabled={reconnecting}
							onclick={handleReconnect}
						>
							{reconnecting ? 'Reconnecting...' : 'Reconnect'}
						</button>
					{/if}

					{#if status.queuedMessages > 0}
						<button
							class="flex-1 bg-gray-600 text-white text-sm px-3 py-1.5 rounded-md hover:bg-gray-700 transition-colors"
							onclick={() => offlineManager.clearQueue()}
						>
							Clear Queue
						</button>
					{/if}
				</div>
			</div>
		{/if}
	</div>
</div>

<style>
	.animate-pulse {
		animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
	}

	@keyframes pulse {
		0%, 100% {
			opacity: 1;
		}
		50% {
			opacity: 0.5;
		}
	}

	.animate-spin {
		animation: spin 1s linear infinite;
	}

	@keyframes spin {
		from {
			transform: rotate(0deg);
		}
		to {
			transform: rotate(360deg);
		}
	}
</style>