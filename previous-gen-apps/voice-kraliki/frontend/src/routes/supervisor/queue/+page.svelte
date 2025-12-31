<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import { goto } from '$app/navigation';

	interface QueueEntry {
		id: number;
		caller_phone: string;
		caller_name: string | null;
		direction: string;
		priority: number;
		status: string;
		queue_position: number | null;
		estimated_wait_time: number | null;
		queued_at: string;
		assigned_agent_id: number | null;
		required_skills: string[];
		required_language: string | null;
		routing_attempts: number;
	}

	interface QueueStats {
		waiting_count: number;
		average_wait_seconds: number;
		abandoned_count: number;
		abandon_rate_percentage: number;
		total_calls_last_hour: number;
	}

	let queueEntries: QueueEntry[] = [];
	let stats: QueueStats | null = null;
	let loading = true;
	let error = '';
	let refreshInterval: any;
	let statusFilter = 'waiting';

	const statusColors: Record<string, string> = {
		waiting: 'bg-yellow-100 text-yellow-800',
		routing: 'bg-blue-100 text-blue-800',
		assigned: 'bg-green-100 text-green-800',
		abandoned: 'bg-red-100 text-red-800',
		answered: 'bg-gray-100 text-gray-800'
	};

	onMount(async () => {
		await loadQueue();
		// Refresh every 3 seconds
		refreshInterval = setInterval(loadQueue, 3000);
	});

	onDestroy(() => {
		if (refreshInterval) {
			clearInterval(refreshInterval);
		}
	});

	async function loadQueue() {
		try {
			const token = localStorage.getItem('token');

			// Load queue entries
			const statusParam = statusFilter !== 'all' ? `?status=${statusFilter}` : '';
			const queueResponse = await fetch(`/api/supervisor/queue${statusParam}`, {
				headers: { Authorization: `Bearer ${token}` }
			});
			if (queueResponse.ok) {
				queueEntries = await queueResponse.json();
			}

			// Load stats
			const statsResponse = await fetch('/api/supervisor/queue/statistics', {
				headers: { Authorization: `Bearer ${token}` }
			});
			if (statsResponse.ok) {
				stats = await statsResponse.json();
			}

			loading = false;
		} catch (err) {
			error = `Error loading queue: ${err}`;
			loading = false;
		}
	}

	function formatDuration(seconds: number | null): string {
		if (seconds === null) return '-';
		const mins = Math.floor(seconds / 60);
		const secs = seconds % 60;
		return `${mins}:${secs.toString().padStart(2, '0')}`;
	}

	function formatTimeSince(dateString: string): string {
		const date = new Date(dateString);
		const now = new Date();
		const diffSeconds = Math.floor((now.getTime() - date.getTime()) / 1000);

		if (diffSeconds < 60) return `${diffSeconds}s`;
		const diffMins = Math.floor(diffSeconds / 60);
		if (diffMins < 60) return `${diffMins}m`;
		const diffHours = Math.floor(diffMins / 60);
		return `${diffHours}h ${diffMins % 60}m`;
	}

	async function handleStatusFilter(status: string) {
		statusFilter = status;
		await loadQueue();
	}
</script>

<div class="container mx-auto p-6">
	<div class="mb-6 flex items-center justify-between">
		<div>
			<h1 class="text-3xl font-bold">Call Queue</h1>
			<p class="text-gray-600 mt-1">Manage incoming call queue and routing</p>
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

	<!-- Queue Statistics -->
	{#if stats}
		<div class="grid grid-cols-1 md:grid-cols-5 gap-4 mb-6">
			<div class="bg-white p-4 rounded-lg shadow">
				<div class="text-sm text-gray-600 mb-1">Waiting Now</div>
				<div class="text-3xl font-bold text-yellow-600">{stats.waiting_count}</div>
			</div>
			<div class="bg-white p-4 rounded-lg shadow">
				<div class="text-sm text-gray-600 mb-1">Avg Wait Time</div>
				<div class="text-3xl font-bold">{formatDuration(stats.average_wait_seconds)}</div>
			</div>
			<div class="bg-white p-4 rounded-lg shadow">
				<div class="text-sm text-gray-600 mb-1">Abandon Rate</div>
				<div class="text-3xl font-bold text-red-600">
					{stats.abandon_rate_percentage.toFixed(1)}%
				</div>
			</div>
			<div class="bg-white p-4 rounded-lg shadow">
				<div class="text-sm text-gray-600 mb-1">Abandoned</div>
				<div class="text-3xl font-bold text-red-600">{stats.abandoned_count}</div>
			</div>
			<div class="bg-white p-4 rounded-lg shadow">
				<div class="text-sm text-gray-600 mb-1">Last Hour</div>
				<div class="text-3xl font-bold">{stats.total_calls_last_hour}</div>
			</div>
		</div>
	{/if}

	<!-- Filters -->
	<div class="mb-6 bg-white rounded-lg shadow p-4">
		<div class="flex gap-2">
			{#each ['all', 'waiting', 'routing', 'assigned', 'abandoned'] as status}
				<button
					onclick={() => handleStatusFilter(status)}
					class="px-4 py-2 rounded-md capitalize {statusFilter === status
						? 'bg-blue-600 text-white'
						: 'bg-gray-200 text-gray-700 hover:bg-gray-300'}"
				>
					{status}
				</button>
			{/each}
		</div>
	</div>

	<!-- Queue Table -->
	{#if loading && queueEntries.length === 0}
		<div class="text-center py-12">
			<div
				class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"
			></div>
			<p class="mt-4 text-gray-600">Loading queue...</p>
		</div>
	{:else if queueEntries.length === 0}
		<div class="text-center py-12 bg-gray-50 rounded-lg">
			<p class="text-gray-600">No calls in queue</p>
		</div>
	{:else}
		<div class="bg-white rounded-lg shadow overflow-hidden">
			<table class="min-w-full divide-y divide-gray-200">
				<thead class="bg-gray-50">
					<tr>
						<th
							class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
						>
							Position
						</th>
						<th
							class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
						>
							Caller
						</th>
						<th
							class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
						>
							Direction
						</th>
						<th
							class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
						>
							Wait Time
						</th>
						<th
							class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
						>
							Est. Wait
						</th>
						<th
							class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
						>
							Priority
						</th>
						<th
							class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
						>
							Skills
						</th>
						<th
							class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
						>
							Status
						</th>
					</tr>
				</thead>
				<tbody class="bg-white divide-y divide-gray-200">
					{#each queueEntries as entry}
						<tr class="hover:bg-gray-50">
							<td class="px-6 py-4 whitespace-nowrap">
								<div class="text-sm font-medium text-gray-900">
									{entry.queue_position || '-'}
								</div>
							</td>
							<td class="px-6 py-4 whitespace-nowrap">
								<div class="text-sm font-medium text-gray-900">
									{entry.caller_name || 'Unknown'}
								</div>
								<div class="text-sm text-gray-500">{entry.caller_phone}</div>
							</td>
							<td class="px-6 py-4 whitespace-nowrap">
								<div class="text-sm text-gray-900 capitalize">{entry.direction}</div>
							</td>
							<td class="px-6 py-4 whitespace-nowrap">
								<div class="text-sm text-gray-900">{formatTimeSince(entry.queued_at)}</div>
							</td>
							<td class="px-6 py-4 whitespace-nowrap">
								<div class="text-sm text-gray-900">
									{formatDuration(entry.estimated_wait_time)}
								</div>
							</td>
							<td class="px-6 py-4 whitespace-nowrap">
								<div class="text-sm">
									{#if entry.priority > 0}
										<span class="px-2 py-1 bg-red-100 text-red-800 rounded-full text-xs font-semibold">
											High ({entry.priority})
										</span>
									{:else}
										<span class="text-gray-500">Normal</span>
									{/if}
								</div>
							</td>
							<td class="px-6 py-4">
								<div class="flex flex-wrap gap-1">
									{#each entry.required_skills as skill}
										<span class="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded">{skill}</span>
									{/each}
									{#if entry.required_language}
										<span class="px-2 py-1 bg-green-100 text-green-800 text-xs rounded">
											{entry.required_language}
										</span>
									{/if}
								</div>
							</td>
							<td class="px-6 py-4 whitespace-nowrap">
								<span
									class="px-2 py-1 text-xs font-semibold rounded-full capitalize {statusColors[
										entry.status
									]}"
								>
									{entry.status}
								</span>
								{#if entry.routing_attempts > 0}
									<div class="text-xs text-gray-500 mt-1">
										{entry.routing_attempts} attempts
									</div>
								{/if}
							</td>
						</tr>
					{/each}
				</tbody>
			</table>
		</div>

		<div class="mt-4 text-sm text-gray-600 flex items-center justify-between">
			<div>Showing {queueEntries.length} calls</div>
			<div class="flex items-center gap-2">
				<span>🔄</span>
				<span>Auto-refreshing every 3 seconds</span>
			</div>
		</div>
	{/if}
</div>
