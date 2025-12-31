<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import { goto } from '$app/navigation';

	interface ActiveCall {
		id: number;
		call_sid: string;
		agent_id: number;
		direction: string;
		caller_phone: string;
		caller_name: string | null;
		status: string;
		started_at: string;
		duration_seconds: number | null;
		is_on_hold: boolean;
		hold_count: number;
		current_sentiment: string | null;
		detected_intent: string | null;
		is_being_monitored: boolean;
	}

	let activeCalls: ActiveCall[] = [];
	let loading = true;
	let error = '';
	let refreshInterval: any;

	const statusColors: Record<string, string> = {
		ringing: 'bg-blue-100 text-blue-800',
		connected: 'bg-green-100 text-green-800',
		on_hold: 'bg-yellow-100 text-yellow-800',
		transferring: 'bg-purple-100 text-purple-800',
		completed: 'bg-gray-100 text-gray-800',
		failed: 'bg-red-100 text-red-800'
	};

	const sentimentColors: Record<string, string> = {
		positive: 'text-green-600',
		neutral: 'text-gray-600',
		negative: 'text-red-600'
	};

	onMount(async () => {
		await loadActiveCalls();
		refreshInterval = setInterval(loadActiveCalls, 3000);
	});

	onDestroy(() => {
		if (refreshInterval) {
			clearInterval(refreshInterval);
		}
	});

	async function loadActiveCalls() {
		try {
			const token = localStorage.getItem('token');
			const response = await fetch('/api/supervisor/calls', {
				headers: { Authorization: `Bearer ${token}` }
			});

			if (response.ok) {
				activeCalls = await response.json();
			}
			loading = false;
		} catch (err) {
			error = `Error loading calls: ${err}`;
			loading = false;
		}
	}

	async function startMonitoring(callId: number) {
		try {
			const token = localStorage.getItem('token');
			const response = await fetch('/api/supervisor/interventions', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
					Authorization: `Bearer ${token}`
				},
				body: JSON.stringify({
					call_id: callId,
					intervention_type: 'monitor',
					reason: 'Quality monitoring'
				})
			});

			if (response.ok) {
				await loadActiveCalls();
			}
		} catch (err) {
			console.error('Error starting monitoring:', err);
		}
	}

	function formatDuration(seconds: number | null): string {
		if (seconds === null) return '-';
		const mins = Math.floor(seconds / 60);
		const secs = seconds % 60;
		return `${mins}:${secs.toString().padStart(2, '0')}`;
	}
</script>

<div class="container mx-auto p-6">
	<div class="mb-6 flex items-center justify-between">
		<div>
			<h1 class="text-3xl font-bold">Active Calls</h1>
			<p class="text-gray-600 mt-1">Monitor and intervene in real-time calls</p>
		</div>

		<button
			onclick={() => goto('/supervisor/dashboard')}
			class="px-4 py-2 border border-gray-300 rounded text-gray-700 hover:bg-gray-50"
		>
			← Back to Dashboard
		</button>
	</div>

	{#if error}
		<div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
			{error}
		</div>
	{/if}

	<!-- Active Calls Count -->
	<div class="mb-6 bg-white p-4 rounded-lg shadow">
		<div class="text-lg font-semibold">
			{activeCalls.length} Active {activeCalls.length === 1 ? 'Call' : 'Calls'}
		</div>
	</div>

	<!-- Calls List -->
	{#if loading && activeCalls.length === 0}
		<div class="text-center py-12">
			<div
				class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"
			></div>
			<p class="mt-4 text-gray-600">Loading active calls...</p>
		</div>
	{:else if activeCalls.length === 0}
		<div class="text-center py-12 bg-gray-50 rounded-lg">
			<p class="text-gray-600">No active calls</p>
		</div>
	{:else}
		<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
			{#each activeCalls as call}
				<div class="bg-white rounded-lg shadow p-4 hover:shadow-lg transition-shadow">
					<div class="flex items-start justify-between mb-3">
						<div class="flex-1">
							<div class="font-medium">{call.caller_name || 'Unknown'}</div>
							<div class="text-sm text-gray-600">{call.caller_phone}</div>
						</div>
						<span
							class="px-2 py-1 text-xs font-semibold rounded-full capitalize {statusColors[
								call.status
							]}"
						>
							{call.status.replace('_', ' ')}
						</span>
					</div>

					<div class="space-y-2 text-sm">
						<div class="flex justify-between">
							<span class="text-gray-600">Duration:</span>
							<span class="font-medium">{formatDuration(call.duration_seconds)}</span>
						</div>

						<div class="flex justify-between">
							<span class="text-gray-600">Direction:</span>
							<span class="font-medium capitalize">{call.direction}</span>
						</div>

						{#if call.current_sentiment}
							<div class="flex justify-between">
								<span class="text-gray-600">Sentiment:</span>
								<span
									class="font-medium capitalize {sentimentColors[call.current_sentiment]}"
								>
									{call.current_sentiment}
								</span>
							</div>
						{/if}

						{#if call.detected_intent}
							<div class="flex justify-between">
								<span class="text-gray-600">Intent:</span>
								<span class="font-medium">{call.detected_intent}</span>
							</div>
						{/if}

						{#if call.is_on_hold}
							<div class="flex items-center gap-2 text-orange-600">
								<span>🔇</span>
								<span>On Hold ({call.hold_count}x)</span>
							</div>
						{/if}

						{#if call.is_being_monitored}
							<div class="flex items-center gap-2 text-blue-600">
								<span>👁️</span>
								<span>Being Monitored</span>
							</div>
						{/if}
					</div>

					<div class="mt-4 flex gap-2">
						{#if !call.is_being_monitored}
							<button
								onclick={() => startMonitoring(call.id)}
								class="flex-1 px-3 py-2 text-sm bg-blue-600 text-white rounded hover:bg-blue-700"
							>
								Monitor
							</button>
						{/if}
						<button
							onclick={() => goto(`/supervisor/calls/${call.id}`)}
							class="flex-1 px-3 py-2 text-sm border border-gray-300 rounded hover:bg-gray-50"
						>
							Details
						</button>
					</div>
				</div>
			{/each}
		</div>

		<div class="mt-6 text-center text-sm text-gray-500">
			<span>🔄 Auto-refreshing every 3 seconds</span>
		</div>
	{/if}
</div>
