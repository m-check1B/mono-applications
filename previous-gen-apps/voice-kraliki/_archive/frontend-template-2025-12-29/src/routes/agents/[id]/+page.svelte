<script lang="ts">
	import { page } from '$app/stores';
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';

	interface Agent {
		id: number;
		user_id: number;
		team_id: number | null;
		employee_id: string | null;
		display_name: string | null;
		phone_number: string | null;
		extension: string | null;
		current_status: string;
		status_since: string;
		last_activity_at: string;
		skills: string[];
		languages: string[];
		max_concurrent_calls: number;
		total_calls_handled: number;
		total_talk_time_seconds: number;
		average_handle_time_seconds: number | null;
		satisfaction_score: number | null;
		quality_score: number | null;
		first_call_resolution_rate: number | null;
		calls_today: number;
		is_available: boolean;
		available_for_calls: boolean;
		auto_answer: boolean;
		notes: string | null;
		created_at: string;
	}

	interface Shift {
		id: number;
		shift_date: string;
		start_time: string;
		end_time: string;
		status: string;
		clock_in_time: string | null;
		clock_out_time: string | null;
	}

	interface Performance {
		period_date: string;
		total_calls: number;
		answered_calls: number;
		missed_calls: number;
		total_talk_time: number;
		average_handle_time: number | null;
		customer_satisfaction_score: number | null;
		quality_score: number | null;
		first_call_resolution_rate: number | null;
	}

	$: agentId = parseInt($page.params.id ?? "0");

	let agent: Agent | null = null;
	let shifts: Shift[] = [];
	let performance: Performance | null = null;
	let loading = true;
	let error = '';
	let activeTab = 'profile';
	let updatingStatus = false;

	const statusColors: Record<string, string> = {
		offline: 'bg-gray-500',
		available: 'bg-green-500',
		busy: 'bg-yellow-500',
		on_call: 'bg-blue-500',
		break: 'bg-orange-500',
		training: 'bg-purple-500',
		away: 'bg-red-500'
	};

	const shiftStatusColors: Record<string, string> = {
		scheduled: 'bg-blue-100 text-blue-800',
		in_progress: 'bg-green-100 text-green-800',
		completed: 'bg-gray-100 text-gray-800',
		cancelled: 'bg-red-100 text-red-800',
		no_show: 'bg-red-100 text-red-800'
	};

	onMount(async () => {
		await loadAgent();
		await loadShifts();
		await loadPerformance();
	});

	async function loadAgent() {
		try {
			const token = localStorage.getItem('token');
			const response = await fetch(`/api/team-management/agents/${agentId}`, {
				headers: { Authorization: `Bearer ${token}` }
			});

			if (response.ok) {
				agent = await response.json();
			} else {
				error = 'Agent not found';
			}
		} catch (err) {
			error = `Error loading agent: ${err}`;
		} finally {
			loading = false;
		}
	}

	async function loadShifts() {
		try {
			const token = localStorage.getItem('token');
			const response = await fetch(`/api/team-management/shifts?agent_id=${agentId}`, {
				headers: { Authorization: `Bearer ${token}` }
			});

			if (response.ok) {
				shifts = await response.json();
			}
		} catch (err) {
			console.error('Error loading shifts:', err);
		}
	}

	async function loadPerformance() {
		try {
			const token = localStorage.getItem('token');
			const today = new Date().toISOString().split('T')[0];
			const response = await fetch(
				`/api/team-management/agents/${agentId}/performance?period_date=${today}`,
				{
					headers: { Authorization: `Bearer ${token}` }
				}
			);

			if (response.ok) {
				performance = await response.json();
			}
		} catch (err) {
			console.error('Error loading performance:', err);
		}
	}

	async function updateStatus(newStatus: string) {
		try {
			updatingStatus = true;
			const token = localStorage.getItem('token');
			const response = await fetch(`/api/team-management/agents/${agentId}/status`, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
					Authorization: `Bearer ${token}`
				},
				body: JSON.stringify({ status: newStatus })
			});

			if (response.ok) {
				await loadAgent();
			} else {
				alert('Failed to update status');
			}
		} catch (err) {
			alert(`Error: ${err}`);
		} finally {
			updatingStatus = false;
		}
	}

	function formatTime(seconds: number | null) {
		if (seconds === null) return '-';
		const hours = Math.floor(seconds / 3600);
		const mins = Math.floor((seconds % 3600) / 60);
		const secs = Math.floor(seconds % 60);
		if (hours > 0) return `${hours}h ${mins}m`;
		if (mins > 0) return `${mins}m ${secs}s`;
		return `${secs}s`;
	}

	function formatPercentage(value: number | null) {
		if (value === null) return '-';
		return `${(value * 100).toFixed(1)}%`;
	}

	function formatScore(score: number | null) {
		if (score === null) return '-';
		return score.toFixed(2);
	}

	function formatDate(dateString: string) {
		return new Date(dateString).toLocaleDateString();
	}

	function formatDateTime(dateString: string | null) {
		if (!dateString) return '-';
		return new Date(dateString).toLocaleString();
	}
</script>

<div class="container mx-auto p-6">
	{#if loading}
		<div class="text-center py-12">
			<div
				class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"
			></div>
			<p class="mt-4 text-gray-600">Loading agent...</p>
		</div>
	{:else if error}
		<div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
			{error}
		</div>
	{:else if agent}
		<!-- Header -->
		<div class="mb-6">
			<div class="flex items-center justify-between mb-2">
				<div class="flex items-center gap-4">
					<button onclick={() => goto('/agents')} class="text-gray-600 hover:text-gray-900">
						← Back
					</button>
					<h1 class="text-3xl font-bold">{agent.display_name || 'Unnamed Agent'}</h1>
					<span
						class="px-3 py-1 text-sm font-semibold rounded-full text-white capitalize {statusColors[
							agent.current_status
						]}"
					>
						{agent.current_status.replace('_', ' ')}
					</span>
				</div>

				<div class="flex gap-2">
					<button
						onclick={() => goto(`/agents/${agentId}/edit`)}
						class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
					>
						Edit Profile
					</button>
				</div>
			</div>

			{#if agent.employee_id}
				<p class="text-gray-600">Employee ID: {agent.employee_id}</p>
			{/if}
		</div>

		<!-- Quick Actions -->
		<div class="mb-6 bg-white rounded-lg shadow p-4">
			<div class="flex items-center gap-2">
				<span class="text-sm font-medium text-gray-700">Change Status:</span>
				<div class="flex gap-2">
					{#each ['available', 'busy', 'break', 'training', 'away', 'offline'] as status}
						<button
							onclick={() => updateStatus(status)}
							disabled={updatingStatus || agent.current_status === status}
							class="px-3 py-1 text-sm rounded capitalize {agent.current_status === status
								? 'bg-gray-300 text-gray-600 cursor-not-allowed'
								: 'bg-gray-100 text-gray-700 hover:bg-gray-200'}"
						>
							{status.replace('_', ' ')}
						</button>
					{/each}
				</div>
			</div>
		</div>

		<!-- Stats Cards -->
		<div class="grid grid-cols-1 md:grid-cols-5 gap-4 mb-6">
			<div class="bg-white p-6 rounded-lg shadow">
				<div class="text-sm text-gray-600 mb-1">Total Calls</div>
				<div class="text-3xl font-bold">{agent.total_calls_handled}</div>
			</div>
			<div class="bg-white p-6 rounded-lg shadow">
				<div class="text-sm text-gray-600 mb-1">Calls Today</div>
				<div class="text-3xl font-bold text-blue-600">{agent.calls_today}</div>
			</div>
			<div class="bg-white p-6 rounded-lg shadow">
				<div class="text-sm text-gray-600 mb-1">Avg Handle Time</div>
				<div class="text-3xl font-bold">{formatTime(agent.average_handle_time_seconds)}</div>
			</div>
			<div class="bg-white p-6 rounded-lg shadow">
				<div class="text-sm text-gray-600 mb-1">CSAT Score</div>
				<div class="text-3xl font-bold">{formatScore(agent.satisfaction_score)}</div>
			</div>
			<div class="bg-white p-6 rounded-lg shadow">
				<div class="text-sm text-gray-600 mb-1">Quality Score</div>
				<div class="text-3xl font-bold">{formatScore(agent.quality_score)}</div>
			</div>
		</div>

		<!-- Tabs -->
		<div class="border-b mb-6">
			<nav class="flex gap-4">
				<button
					onclick={() => (activeTab = 'profile')}
					class="pb-2 px-1 {activeTab === 'profile'
						? 'border-b-2 border-blue-600 text-blue-600'
						: 'text-gray-600 hover:text-gray-900'}"
				>
					Profile
				</button>
				<button
					onclick={() => (activeTab = 'performance')}
					class="pb-2 px-1 {activeTab === 'performance'
						? 'border-b-2 border-blue-600 text-blue-600'
						: 'text-gray-600 hover:text-gray-900'}"
				>
					Performance
				</button>
				<button
					onclick={() => (activeTab = 'shifts')}
					class="pb-2 px-1 {activeTab === 'shifts'
						? 'border-b-2 border-blue-600 text-blue-600'
						: 'text-gray-600 hover:text-gray-900'}"
				>
					Shifts
				</button>
			</nav>
		</div>

		<!-- Tab Content -->
		{#if activeTab === 'profile'}
			<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
				<!-- Contact Information -->
				<div class="bg-white p-6 rounded-lg shadow">
					<h3 class="text-lg font-semibold mb-4">Contact Information</h3>
					<dl class="space-y-2">
						<div class="flex justify-between">
							<dt class="text-gray-600">Phone:</dt>
							<dd class="font-medium">{agent.phone_number || '-'}</dd>
						</div>
						<div class="flex justify-between">
							<dt class="text-gray-600">Extension:</dt>
							<dd class="font-medium">{agent.extension || '-'}</dd>
						</div>
						<div class="flex justify-between">
							<dt class="text-gray-600">Max Concurrent Calls:</dt>
							<dd class="font-medium">{agent.max_concurrent_calls}</dd>
						</div>
						<div class="flex justify-between">
							<dt class="text-gray-600">Auto Answer:</dt>
							<dd class="font-medium">{agent.auto_answer ? 'Yes' : 'No'}</dd>
						</div>
					</dl>
				</div>

				<!-- Skills & Languages -->
				<div class="bg-white p-6 rounded-lg shadow">
					<h3 class="text-lg font-semibold mb-4">Skills & Languages</h3>
					<div class="space-y-3">
						<div>
							<div class="text-sm text-gray-600 mb-2">Skills</div>
							<div class="flex flex-wrap gap-2">
								{#each agent.skills as skill}
									<span class="px-3 py-1 bg-blue-100 text-blue-800 text-sm rounded">
										{skill}
									</span>
								{:else}
									<span class="text-gray-500">No skills listed</span>
								{/each}
							</div>
						</div>
						<div>
							<div class="text-sm text-gray-600 mb-2">Languages</div>
							<div class="flex flex-wrap gap-2">
								{#each agent.languages as lang}
									<span class="px-3 py-1 bg-green-100 text-green-800 text-sm rounded">
										{lang}
									</span>
								{:else}
									<span class="text-gray-500">No languages listed</span>
								{/each}
							</div>
						</div>
					</div>
				</div>

				<!-- Status Info -->
				<div class="bg-white p-6 rounded-lg shadow">
					<h3 class="text-lg font-semibold mb-4">Status Information</h3>
					<dl class="space-y-2">
						<div class="flex justify-between">
							<dt class="text-gray-600">Current Status:</dt>
							<dd class="font-medium capitalize">{agent.current_status.replace('_', ' ')}</dd>
						</div>
						<div class="flex justify-between">
							<dt class="text-gray-600">Status Since:</dt>
							<dd class="font-medium">{formatDateTime(agent.status_since)}</dd>
						</div>
						<div class="flex justify-between">
							<dt class="text-gray-600">Last Activity:</dt>
							<dd class="font-medium">{formatDateTime(agent.last_activity_at)}</dd>
						</div>
						<div class="flex justify-between">
							<dt class="text-gray-600">Available for Calls:</dt>
							<dd class="font-medium">{agent.available_for_calls ? 'Yes' : 'No'}</dd>
						</div>
					</dl>
				</div>

				<!-- Notes -->
				{#if agent.notes}
					<div class="bg-white p-6 rounded-lg shadow">
						<h3 class="text-lg font-semibold mb-4">Notes</h3>
						<p class="text-gray-700">{agent.notes}</p>
					</div>
				{/if}
			</div>
		{:else if activeTab === 'performance'}
			{#if performance}
				<div class="space-y-6">
					<div class="grid grid-cols-1 md:grid-cols-4 gap-4">
						<div class="bg-white p-6 rounded-lg shadow">
							<div class="text-sm text-gray-600 mb-1">Total Calls</div>
							<div class="text-3xl font-bold">{performance.total_calls}</div>
						</div>
						<div class="bg-white p-6 rounded-lg shadow">
							<div class="text-sm text-gray-600 mb-1">Answered</div>
							<div class="text-3xl font-bold text-green-600">{performance.answered_calls}</div>
						</div>
						<div class="bg-white p-6 rounded-lg shadow">
							<div class="text-sm text-gray-600 mb-1">Missed</div>
							<div class="text-3xl font-bold text-red-600">{performance.missed_calls}</div>
						</div>
						<div class="bg-white p-6 rounded-lg shadow">
							<div class="text-sm text-gray-600 mb-1">Talk Time</div>
							<div class="text-3xl font-bold">{formatTime(performance.total_talk_time)}</div>
						</div>
					</div>

					<div class="bg-white p-6 rounded-lg shadow">
						<h3 class="text-lg font-semibold mb-4">Quality Metrics</h3>
						<dl class="grid grid-cols-2 gap-4">
							<div>
								<dt class="text-sm text-gray-600">CSAT Score</dt>
								<dd class="text-2xl font-semibold">
									{formatScore(performance.customer_satisfaction_score)}
								</dd>
							</div>
							<div>
								<dt class="text-sm text-gray-600">Quality Score</dt>
								<dd class="text-2xl font-semibold">{formatScore(performance.quality_score)}</dd>
							</div>
							<div>
								<dt class="text-sm text-gray-600">First Call Resolution</dt>
								<dd class="text-2xl font-semibold">
									{formatPercentage(performance.first_call_resolution_rate)}
								</dd>
							</div>
							<div>
								<dt class="text-sm text-gray-600">Avg Handle Time</dt>
								<dd class="text-2xl font-semibold">
									{formatTime(performance.average_handle_time)}
								</dd>
							</div>
						</dl>
					</div>
				</div>
			{:else}
				<div class="text-center py-12 bg-gray-50 rounded-lg">
					<p class="text-gray-600">No performance data available for today</p>
				</div>
			{/if}
		{:else if activeTab === 'shifts'}
			{#if shifts.length === 0}
				<div class="text-center py-12 bg-gray-50 rounded-lg">
					<p class="text-gray-600">No shifts scheduled</p>
				</div>
			{:else}
				<div class="bg-white rounded-lg shadow overflow-hidden">
					<table class="min-w-full divide-y divide-gray-200">
						<thead class="bg-gray-50">
							<tr>
								<th
									class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
								>
									Date
								</th>
								<th
									class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
								>
									Scheduled Time
								</th>
								<th
									class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
								>
									Clock In
								</th>
								<th
									class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
								>
									Clock Out
								</th>
								<th
									class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
								>
									Status
								</th>
							</tr>
						</thead>
						<tbody class="bg-white divide-y divide-gray-200">
							{#each shifts as shift}
								<tr class="hover:bg-gray-50">
									<td class="px-6 py-4 whitespace-nowrap">
										<div class="text-sm font-medium text-gray-900">
											{formatDate(shift.shift_date)}
										</div>
									</td>
									<td class="px-6 py-4 whitespace-nowrap">
										<div class="text-sm text-gray-900">
											{shift.start_time} - {shift.end_time}
										</div>
									</td>
									<td class="px-6 py-4 whitespace-nowrap">
										<div class="text-sm text-gray-900">{formatDateTime(shift.clock_in_time)}</div>
									</td>
									<td class="px-6 py-4 whitespace-nowrap">
										<div class="text-sm text-gray-900">
											{formatDateTime(shift.clock_out_time)}
										</div>
									</td>
									<td class="px-6 py-4 whitespace-nowrap">
										<span
											class="px-2 text-xs font-semibold rounded-full capitalize {shiftStatusColors[
												shift.status
											]}"
										>
											{shift.status.replace('_', ' ')}
										</span>
									</td>
								</tr>
							{/each}
						</tbody>
					</table>
				</div>
			{/if}
		{/if}
	{/if}
</div>
