<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import { goto } from '$app/navigation';

	interface DashboardStats {
		active_calls: number;
		agents_available: number;
		agents_on_call: number;
		agents_on_break: number;
		agents_offline: number;
		queue_waiting: number;
		average_wait_time: number;
		abandon_rate: number;
		active_alerts: number;
		timestamp: string;
	}

	interface AgentStatus {
		agent_id: number;
		display_name: string;
		current_status: string;
		status_since: string;
		active_calls_count: number;
		active_calls: any[];
		is_available: boolean;
		max_concurrent_calls: number;
	}

	interface Alert {
		id: number;
		alert_type: string;
		severity: string;
		title: string;
		message: string;
		created_at: string;
		is_acknowledged: boolean;
	}

	let stats: DashboardStats | null = null;
	let agents: AgentStatus[] = [];
	let alerts: Alert[] = [];
	let loading = true;
	let error = '';
	let refreshInterval: any;
	let selectedTeam: number | null = null;

	const statusColors: Record<string, string> = {
		offline: 'bg-gray-400',
		available: 'bg-green-500',
		busy: 'bg-yellow-500',
		on_call: 'bg-blue-500',
		break: 'bg-orange-500',
		training: 'bg-purple-500',
		away: 'bg-red-500'
	};

	const alertSeverityColors: Record<string, string> = {
		info: 'bg-blue-100 text-blue-800 border-blue-200',
		warning: 'bg-yellow-100 text-yellow-800 border-yellow-200',
		critical: 'bg-red-100 text-red-800 border-red-200'
	};

	onMount(async () => {
		await loadDashboard();
		// Refresh every 5 seconds
		refreshInterval = setInterval(loadDashboard, 5000);
	});

	onDestroy(() => {
		if (refreshInterval) {
			clearInterval(refreshInterval);
		}
	});

	async function loadDashboard() {
		try {
			const token = localStorage.getItem('token');
			const teamParam = selectedTeam ? `?team_id=${selectedTeam}` : '';

			// Load stats
			const statsResponse = await fetch(`/api/supervisor/dashboard/stats${teamParam}`, {
				headers: { Authorization: `Bearer ${token}` }
			});
			if (statsResponse.ok) {
				stats = await statsResponse.json();
			}

			// Load agent live status
			const agentsResponse = await fetch(`/api/supervisor/agents/live-status${teamParam}`, {
				headers: { Authorization: `Bearer ${token}` }
			});
			if (agentsResponse.ok) {
				agents = await agentsResponse.json();
			}

			// Load active alerts
			const alertsResponse = await fetch(`/api/supervisor/alerts${teamParam}`, {
				headers: { Authorization: `Bearer ${token}` }
			});
			if (alertsResponse.ok) {
				alerts = await alertsResponse.json();
			}

			loading = false;
		} catch (err) {
			error = `Error loading dashboard: ${err}`;
			loading = false;
		}
	}

	async function acknowledgeAlert(alertId: number) {
		try {
			const token = localStorage.getItem('token');
			const response = await fetch(`/api/supervisor/alerts/${alertId}/acknowledge`, {
				method: 'POST',
				headers: { Authorization: `Bearer ${token}` }
			});

			if (response.ok) {
				await loadDashboard();
			}
		} catch (err) {
			console.error('Error acknowledging alert:', err);
		}
	}

	function formatDuration(seconds: number): string {
		const mins = Math.floor(seconds / 60);
		const secs = seconds % 60;
		return `${mins}m ${secs}s`;
	}

	function formatTimeSince(dateString: string): string {
		const date = new Date(dateString);
		const now = new Date();
		const diffMs = now.getTime() - date.getTime();
		const diffMins = Math.floor(diffMs / 60000);

		if (diffMins < 1) return 'Just now';
		if (diffMins < 60) return `${diffMins}m ago`;
		const diffHours = Math.floor(diffMins / 60);
		if (diffHours < 24) return `${diffHours}h ago`;
		const diffDays = Math.floor(diffHours / 24);
		return `${diffDays}d ago`;
	}
</script>

<div class="container mx-auto p-6">
	<div class="mb-6 flex items-center justify-between">
		<div>
			<h1 class="text-3xl font-bold">Supervisor Dashboard</h1>
			<p class="text-gray-600 mt-1">Real-time monitoring and control center</p>
		</div>

		<div class="flex gap-3">
			<button
				onclick={() => goto('/supervisor/queue')}
				class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
			>
				Call Queue
			</button>
			<button
				onclick={() => goto('/supervisor/active-calls')}
				class="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
			>
				Active Calls
			</button>
		</div>
	</div>

	{#if error}
		<div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
			{error}
		</div>
	{/if}

	{#if loading && !stats}
		<div class="text-center py-12">
			<div
				class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"
			></div>
			<p class="mt-4 text-gray-600">Loading dashboard...</p>
		</div>
	{:else if stats}
		<!-- Real-time Stats -->
		<div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
			<div class="bg-white p-6 rounded-lg shadow">
				<div class="flex items-center justify-between">
					<div>
						<div class="text-sm text-gray-600 mb-1">Active Calls</div>
						<div class="text-3xl font-bold text-blue-600">{stats.active_calls}</div>
					</div>
					<div class="text-4xl">📞</div>
				</div>
			</div>

			<div class="bg-white p-6 rounded-lg shadow">
				<div class="flex items-center justify-between">
					<div>
						<div class="text-sm text-gray-600 mb-1">Queue Waiting</div>
						<div class="text-3xl font-bold text-orange-600">{stats.queue_waiting}</div>
					</div>
					<div class="text-4xl">⏱️</div>
				</div>
			</div>

			<div class="bg-white p-6 rounded-lg shadow">
				<div class="flex items-center justify-between">
					<div>
						<div class="text-sm text-gray-600 mb-1">Avg Wait Time</div>
						<div class="text-3xl font-bold">{formatDuration(stats.average_wait_time)}</div>
					</div>
					<div class="text-4xl">⏳</div>
				</div>
			</div>

			<div class="bg-white p-6 rounded-lg shadow">
				<div class="flex items-center justify-between">
					<div>
						<div class="text-sm text-gray-600 mb-1">Abandon Rate</div>
						<div class="text-3xl font-bold text-red-600">{stats.abandon_rate.toFixed(1)}%</div>
					</div>
					<div class="text-4xl">📉</div>
				</div>
			</div>
		</div>

		<!-- Agent Status Overview -->
		<div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
			<div class="bg-white p-4 rounded-lg shadow">
				<div class="text-sm text-gray-600 mb-2">Available</div>
				<div class="text-2xl font-bold text-green-600">{stats.agents_available}</div>
			</div>
			<div class="bg-white p-4 rounded-lg shadow">
				<div class="text-sm text-gray-600 mb-2">On Call</div>
				<div class="text-2xl font-bold text-blue-600">{stats.agents_on_call}</div>
			</div>
			<div class="bg-white p-4 rounded-lg shadow">
				<div class="text-sm text-gray-600 mb-2">On Break</div>
				<div class="text-2xl font-bold text-orange-600">{stats.agents_on_break}</div>
			</div>
			<div class="bg-white p-4 rounded-lg shadow">
				<div class="text-sm text-gray-600 mb-2">Offline</div>
				<div class="text-2xl font-bold text-gray-600">{stats.agents_offline}</div>
			</div>
		</div>

		<!-- Alerts Section -->
		{#if alerts.length > 0}
			<div class="mb-6">
				<h2 class="text-xl font-semibold mb-3">Active Alerts ({alerts.length})</h2>
				<div class="space-y-2">
					{#each alerts.slice(0, 5) as alert}
						<div
							class="border rounded-lg p-4 {alertSeverityColors[alert.severity]} flex items-start justify-between"
						>
							<div class="flex-1">
								<div class="flex items-center gap-2 mb-1">
									<span class="font-semibold">{alert.title}</span>
									<span class="text-xs uppercase font-bold">{alert.severity}</span>
								</div>
								<p class="text-sm">{alert.message}</p>
								<p class="text-xs mt-1 opacity-75">{formatTimeSince(alert.created_at)}</p>
							</div>
							{#if !alert.is_acknowledged}
								<button
									onclick={() => acknowledgeAlert(alert.id)}
									class="ml-4 px-3 py-1 text-sm bg-white rounded hover:bg-gray-50"
								>
									Acknowledge
								</button>
							{/if}
						</div>
					{/each}
				</div>
				{#if alerts.length > 5}
					<button
						onclick={() => goto('/supervisor/alerts')}
						class="mt-2 text-blue-600 hover:text-blue-800 text-sm"
					>
						View all {alerts.length} alerts →
					</button>
				{/if}
			</div>
		{/if}

		<!-- Live Agent Grid -->
		<div class="bg-white rounded-lg shadow p-6">
			<div class="flex items-center justify-between mb-4">
				<h2 class="text-xl font-semibold">Live Agent Status ({agents.length})</h2>
				<button
					onclick={loadDashboard}
					class="text-blue-600 hover:text-blue-800 text-sm flex items-center gap-1"
				>
					<span>🔄</span>
					Refresh
				</button>
			</div>

			{#if agents.length === 0}
				<div class="text-center py-8 text-gray-500">No agents available</div>
			{:else}
				<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
					{#each agents as agent}
						<div class="border rounded-lg p-4 hover:shadow-md transition-shadow">
							<div class="flex items-start justify-between mb-2">
								<div class="flex items-center gap-2">
									<div
										class="w-3 h-3 rounded-full {statusColors[agent.current_status]}"
										title={agent.current_status}
									></div>
									<button
										onclick={() => goto(`/agents/${agent.agent_id}`)}
										class="font-medium hover:text-blue-600"
									>
										{agent.display_name}
									</button>
								</div>
								<span
									class="text-xs px-2 py-1 rounded-full capitalize {statusColors[
										agent.current_status
									]} text-white"
								>
									{agent.current_status.replace('_', ' ')}
								</span>
							</div>

							<div class="text-sm text-gray-600">
								<div>Since: {formatTimeSince(agent.status_since)}</div>
								<div class="mt-1">
									Calls: {agent.active_calls_count}/{agent.max_concurrent_calls}
								</div>
							</div>

							{#if agent.active_calls_count > 0}
								<div class="mt-3 space-y-1">
									{#each agent.active_calls as call}
										<div class="text-xs bg-gray-50 rounded p-2">
											<div class="flex items-center justify-between">
												<span class="capitalize">{call.direction}</span>
												<span class="font-medium">{formatDuration(call.duration_seconds)}</span>
											</div>
											{#if call.is_on_hold}
												<div class="text-orange-600 mt-1">🔇 On Hold</div>
											{/if}
										</div>
									{/each}
								</div>
							{/if}
						</div>
					{/each}
				</div>
			{/if}
		</div>

		<!-- Last Updated -->
		<div class="mt-4 text-center text-sm text-gray-500">
			Last updated: {formatTimeSince(stats.timestamp)}
			<span class="ml-2">• Auto-refreshing every 5 seconds</span>
		</div>
	{/if}
</div>
