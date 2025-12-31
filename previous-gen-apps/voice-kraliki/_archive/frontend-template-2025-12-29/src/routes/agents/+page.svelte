<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';

	interface Agent {
		id: number;
		user_id: number;
		team_id: number | null;
		employee_id: string | null;
		display_name: string | null;
		phone_number: string | null;
		current_status: string;
		status_since: string;
		last_activity_at: string;
		skills: string[];
		languages: string[];
		max_concurrent_calls: number;
		total_calls_handled: number;
		satisfaction_score: number | null;
		is_available: boolean;
		available_for_calls: boolean;
		created_at: string;
	}

	let agents: Agent[] = [];
	let filteredAgents: Agent[] = [];
	let loading = true;
	let error = '';
	let statusFilter = 'all';
	let searchQuery = '';

	const statusColors: Record<string, string> = {
		offline: 'bg-gray-200 text-gray-800',
		available: 'bg-green-200 text-green-800',
		busy: 'bg-yellow-200 text-yellow-800',
		on_call: 'bg-blue-200 text-blue-800',
		break: 'bg-orange-200 text-orange-800',
		training: 'bg-purple-200 text-purple-800',
		away: 'bg-red-200 text-red-800'
	};

	const statusOptions = [
		'all',
		'offline',
		'available',
		'busy',
		'on_call',
		'break',
		'training',
		'away'
	];

	onMount(async () => {
		await loadAgents();
	});

	async function loadAgents() {
		try {
			loading = true;
			const token = localStorage.getItem('token');
			const response = await fetch('/api/team-management/agents', {
				headers: { Authorization: `Bearer ${token}` }
			});

			if (response.ok) {
				agents = await response.json();
				filterAgents();
			}
		} catch (err) {
			error = `Error loading agents: ${err}`;
		} finally {
			loading = false;
		}
	}

	function filterAgents() {
		filteredAgents = agents.filter((agent) => {
			const matchesStatus = statusFilter === 'all' || agent.current_status === statusFilter;
			const matchesSearch =
				searchQuery === '' ||
				agent.display_name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
				agent.employee_id?.toLowerCase().includes(searchQuery.toLowerCase());

			return matchesStatus && matchesSearch;
		});
	}

	function handleStatusFilter(status: string) {
		statusFilter = status;
		filterAgents();
	}

	function handleSearch(event: Event) {
		searchQuery = (event.target as HTMLInputElement).value;
		filterAgents();
	}

	function formatDate(dateString: string) {
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

	function formatScore(score: number | null) {
		if (score === null) return '-';
		return score.toFixed(2);
	}
</script>

<div class="container mx-auto p-6">
	<div class="mb-6 flex items-center justify-between">
		<div>
			<h1 class="text-3xl font-bold">Agents</h1>
			<p class="text-gray-600 mt-1">Manage agent profiles and monitor status</p>
		</div>

		<button
			onclick={() => goto('/agents/new')}
			class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
		>
			+ New Agent
		</button>
	</div>

	{#if error}
		<div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
			{error}
		</div>
	{/if}

	<!-- Search and Filters -->
	<div class="mb-6 bg-white rounded-lg shadow p-4">
		<div class="flex gap-4 mb-4">
			<input
				type="text"
				placeholder="Search by name or employee ID..."
				oninput={handleSearch}
				class="flex-1 px-4 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
			/>
		</div>

		<div class="flex gap-2 flex-wrap">
			{#each statusOptions as status}
				<button
					onclick={() => handleStatusFilter(status)}
					class="px-4 py-2 rounded-md capitalize {statusFilter === status
						? 'bg-blue-600 text-white'
						: 'bg-gray-200 text-gray-700 hover:bg-gray-300'}"
				>
					{status === 'all' ? 'All' : status.replace('_', ' ')}
				</button>
			{/each}
		</div>
	</div>

	<!-- Agents List -->
	{#if loading}
		<div class="text-center py-12">
			<div
				class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"
			></div>
			<p class="mt-4 text-gray-600">Loading agents...</p>
		</div>
	{:else if filteredAgents.length === 0}
		<div class="text-center py-12 bg-gray-50 rounded-lg">
			<p class="text-gray-600 mb-4">
				{agents.length === 0 ? 'No agents yet' : 'No agents match your filters'}
			</p>
			{#if agents.length === 0}
				<button
					onclick={() => goto('/agents/new')}
					class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
				>
					Create First Agent
				</button>
			{/if}
		</div>
	{:else}
		<!-- Stats Summary -->
		<div class="grid grid-cols-1 md:grid-cols-5 gap-4 mb-6">
			<div class="bg-white p-4 rounded-lg shadow">
				<div class="text-sm text-gray-600 mb-1">Total</div>
				<div class="text-2xl font-bold">{agents.length}</div>
			</div>
			<div class="bg-white p-4 rounded-lg shadow">
				<div class="text-sm text-gray-600 mb-1">Available</div>
				<div class="text-2xl font-bold text-green-600">
					{agents.filter((a) => a.current_status === 'available').length}
				</div>
			</div>
			<div class="bg-white p-4 rounded-lg shadow">
				<div class="text-sm text-gray-600 mb-1">On Call</div>
				<div class="text-2xl font-bold text-blue-600">
					{agents.filter((a) => a.current_status === 'on_call').length}
				</div>
			</div>
			<div class="bg-white p-4 rounded-lg shadow">
				<div class="text-sm text-gray-600 mb-1">Break</div>
				<div class="text-2xl font-bold text-orange-600">
					{agents.filter((a) => a.current_status === 'break').length}
				</div>
			</div>
			<div class="bg-white p-4 rounded-lg shadow">
				<div class="text-sm text-gray-600 mb-1">Offline</div>
				<div class="text-2xl font-bold text-gray-600">
					{agents.filter((a) => a.current_status === 'offline').length}
				</div>
			</div>
		</div>

		<!-- Agents Table -->
		<div class="bg-white rounded-lg shadow overflow-hidden">
			<table class="min-w-full divide-y divide-gray-200">
				<thead class="bg-gray-50">
					<tr>
						<th
							class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
						>
							Agent
						</th>
						<th
							class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
						>
							Status
						</th>
						<th
							class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
						>
							Skills
						</th>
						<th
							class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
						>
							Total Calls
						</th>
						<th
							class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
						>
							CSAT
						</th>
						<th
							class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
						>
							Last Activity
						</th>
						<th
							class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider"
						>
							Actions
						</th>
					</tr>
				</thead>
				<tbody class="bg-white divide-y divide-gray-200">
					{#each filteredAgents as agent}
						<tr class="hover:bg-gray-50">
							<td class="px-6 py-4 whitespace-nowrap">
								<div class="flex items-center">
									<div>
										<div class="text-sm font-medium text-gray-900">
											{agent.display_name || 'Unnamed Agent'}
										</div>
										{#if agent.employee_id}
											<div class="text-sm text-gray-500">ID: {agent.employee_id}</div>
										{/if}
									</div>
								</div>
							</td>
							<td class="px-6 py-4 whitespace-nowrap">
								<div class="flex flex-col gap-1">
									<span
										class="px-2 text-xs font-semibold rounded-full capitalize {statusColors[
											agent.current_status
										]}"
									>
										{agent.current_status.replace('_', ' ')}
									</span>
									<span class="text-xs text-gray-500">{formatDate(agent.status_since)}</span>
								</div>
							</td>
							<td class="px-6 py-4">
								<div class="flex flex-wrap gap-1">
									{#each agent.skills.slice(0, 3) as skill}
										<span class="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded">
											{skill}
										</span>
									{/each}
									{#if agent.skills.length > 3}
										<span class="px-2 py-1 bg-gray-100 text-gray-800 text-xs rounded">
											+{agent.skills.length - 3}
										</span>
									{/if}
								</div>
							</td>
							<td class="px-6 py-4 whitespace-nowrap">
								<div class="text-sm text-gray-900">{agent.total_calls_handled}</div>
							</td>
							<td class="px-6 py-4 whitespace-nowrap">
								<div class="text-sm text-gray-900">{formatScore(agent.satisfaction_score)}</div>
							</td>
							<td class="px-6 py-4 whitespace-nowrap">
								<div class="text-sm text-gray-500">{formatDate(agent.last_activity_at)}</div>
							</td>
							<td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
								<button
									onclick={() => goto(`/agents/${agent.id}`)}
									class="text-blue-600 hover:text-blue-900"
								>
									View
								</button>
							</td>
						</tr>
					{/each}
				</tbody>
			</table>
		</div>

		<div class="mt-4 text-sm text-gray-600">
			Showing {filteredAgents.length} of {agents.length} agents
		</div>
	{/if}
</div>
