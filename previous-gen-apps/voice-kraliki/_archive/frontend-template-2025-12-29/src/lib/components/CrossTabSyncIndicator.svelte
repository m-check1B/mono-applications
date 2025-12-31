<script lang="ts">
	/**
	 * CrossTabSyncIndicator Component
	 *
	 * A simple indicator component that shows whether cross-tab sync is available.
	 * Can be added to any page to show sync status.
	 *
	 * Usage:
	 * ```svelte
	 * import CrossTabSyncIndicator from '$lib/components/CrossTabSyncIndicator.svelte';
	 *
	 * <CrossTabSyncIndicator />
	 * ```
	 */
	import { crossTabSync } from '$lib/services/crossTabSync';
	import { authStore } from '$lib/stores/auth';

	let lastSyncMessage = $state<string>('');
	let messageCount = $state(0);

	// Listen for sync events
	$effect(() => {
		const unsubscribers = [
			crossTabSync.subscribe('auth_updated', (msg) => {
				lastSyncMessage = `Auth synced from another tab`;
				messageCount++;
			}),
			crossTabSync.subscribe('auth_logout', (msg) => {
				lastSyncMessage = `Logout synced from another tab`;
				messageCount++;
			}),
			crossTabSync.subscribe('session_updated', (msg) => {
				lastSyncMessage = `Session synced from another tab`;
				messageCount++;
			}),
			crossTabSync.subscribe('session_ended', (msg) => {
				lastSyncMessage = `Session ended from another tab`;
				messageCount++;
			})
		];

		return () => unsubscribers.forEach(unsub => unsub());
	});

	const isAvailable = crossTabSync.isAvailable();
	const isAuthenticated = $derived($authStore.status === 'authenticated');
</script>

{#if isAvailable}
	<div class="sync-indicator" class:has-synced={messageCount > 0}>
		<div class="status">
			<span class="icon">🔄</span>
			<span class="label">Cross-Tab Sync Active</span>
		</div>

		{#if lastSyncMessage}
			<div class="last-sync">
				<span class="message">{lastSyncMessage}</span>
				<span class="count">({messageCount} syncs)</span>
			</div>
		{/if}
	</div>
{/if}

<style>
	.sync-indicator {
		position: fixed;
		bottom: 1rem;
		right: 1rem;
		background: hsl(var(--card));
		border: 2px solid hsl(var(--border));
		padding: 0.9rem 1rem;
		box-shadow: var(--shadow-brutal);
		font-size: 0.875rem;
		z-index: 1000;
		min-width: 200px;
	}

	.sync-indicator.has-synced {
		border-color: hsl(var(--border));
		background: hsl(var(--card));
	}

	.status {
		display: flex;
		align-items: center;
		gap: 0.5rem;
	}

	.icon {
		font-size: 1rem;
	}

	.label {
		color: #667eea;
		font-weight: 600;
	}

	.last-sync {
		margin-top: 0.5rem;
		padding-top: 0.5rem;
		border-top: 1px solid #e2e8f0;
		font-size: 0.75rem;
		color: #64748b;
		display: flex;
		flex-direction: column;
		gap: 0.25rem;
	}

	.message {
		color: #334155;
	}

	.count {
		color: #94a3b8;
		font-size: 0.7rem;
	}

	@media (max-width: 640px) {
		.sync-indicator {
			bottom: 0.5rem;
			right: 0.5rem;
			font-size: 0.75rem;
			min-width: 150px;
		}
	}
</style>
