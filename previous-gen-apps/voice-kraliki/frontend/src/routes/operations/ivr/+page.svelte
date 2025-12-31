<script lang="ts">
	import { onMount } from 'svelte';
	import { Phone, Play, Edit, Trash2, Plus, Search } from 'lucide-svelte';

	interface IVRFlow {
		id: number;
		name: string;
		description: string | null;
		team_id: number;
		entry_node_id: number | null;
		is_active: boolean;
		version: number;
		timeout_seconds: number;
		max_retries: number;
		created_at: string;
		updated_at: string;
		nodes_count?: number;
	}

	let flows: IVRFlow[] = [];
	let loading = true;
	let error: string | null = null;
	let searchQuery = '';
	let statusFilter: 'all' | 'active' | 'inactive' = 'all';

	// Statistics
	let stats = {
		total_flows: 0,
		active_flows: 0,
		inactive_flows: 0,
		total_nodes: 0
	};

	onMount(async () => {
		await loadFlows();
	});

	async function loadFlows() {
		loading = true;
		error = null;
		try {
			const response = await fetch('http://localhost:8000/api/ivr/flows');
			if (!response.ok) throw new Error('Failed to load IVR flows');
			flows = await response.json();
			calculateStats();
		} catch (err) {
			error = err instanceof Error ? err.message : 'Unknown error occurred';
		} finally {
			loading = false;
		}
	}

	function calculateStats() {
		stats.total_flows = flows.length;
		stats.active_flows = flows.filter((f) => f.is_active).length;
		stats.inactive_flows = flows.filter((f) => !f.is_active).length;
		stats.total_nodes = flows.reduce((sum, f) => sum + (f.nodes_count || 0), 0);
	}

	async function toggleFlowStatus(flowId: number) {
		try {
			const flow = flows.find((f) => f.id === flowId);
			if (!flow) return;

			const response = await fetch(`http://localhost:8000/api/ivr/flows/${flowId}`, {
				method: 'PUT',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({
					name: flow.name,
					description: flow.description,
					is_active: !flow.is_active,
					timeout_seconds: flow.timeout_seconds,
					max_retries: flow.max_retries
				})
			});

			if (!response.ok) throw new Error('Failed to update flow status');
			await loadFlows();
		} catch (err) {
			alert(err instanceof Error ? err.message : 'Failed to update flow status');
		}
	}

	async function deleteFlow(flowId: number) {
		if (!confirm('Are you sure you want to delete this IVR flow?')) return;

		try {
			const response = await fetch(`http://localhost:8000/api/ivr/flows/${flowId}`, {
				method: 'DELETE'
			});

			if (!response.ok) throw new Error('Failed to delete flow');
			await loadFlows();
		} catch (err) {
			alert(err instanceof Error ? err.message : 'Failed to delete flow');
		}
	}

	async function testFlow(flowId: number) {
		try {
			const response = await fetch(`http://localhost:8000/api/ivr/flows/${flowId}/test`, {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({
					test_phone: '+1234567890',
					test_language: 'en'
				})
			});

			if (!response.ok) throw new Error('Failed to test flow');
			const result = await response.json();
			alert(`Flow test completed: ${result.status}`);
		} catch (err) {
			alert(err instanceof Error ? err.message : 'Failed to test flow');
		}
	}

	function formatDate(dateStr: string): string {
		return new Date(dateStr).toLocaleDateString('en-US', {
			month: 'short',
			day: 'numeric',
			year: 'numeric',
			hour: '2-digit',
			minute: '2-digit'
		});
	}

	function getStatusColor(isActive: boolean): string {
		return isActive ? 'text-green-600' : 'text-gray-400';
	}

	function getStatusBadge(isActive: boolean): string {
		return isActive
			? 'bg-green-100 text-green-800 border-green-200'
			: 'bg-gray-100 text-gray-600 border-gray-200';
	}

	$: filteredFlows = flows.filter((flow) => {
		const matchesSearch =
			searchQuery === '' ||
			flow.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
			(flow.description && flow.description.toLowerCase().includes(searchQuery.toLowerCase()));

		const matchesStatus =
			statusFilter === 'all' ||
			(statusFilter === 'active' && flow.is_active) ||
			(statusFilter === 'inactive' && !flow.is_active);

		return matchesSearch && matchesStatus;
	});
</script>

<div class="p-6 max-w-7xl mx-auto">
	<div class="mb-6">
		<h1 class="text-3xl font-bold text-gray-900 mb-2">IVR Flow Management</h1>
		<p class="text-gray-600">
			Configure and manage Interactive Voice Response (IVR) flows for call routing
		</p>
	</div>

	<!-- Statistics Cards -->
	<div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
		<div class="bg-white rounded-lg border border-gray-200 p-4">
			<div class="flex items-center justify-between">
				<div>
					<p class="text-sm text-gray-600">Total Flows</p>
					<p class="text-2xl font-bold text-gray-900">{stats.total_flows}</p>
				</div>
				<Phone class="w-8 h-8 text-blue-500" />
			</div>
		</div>

		<div class="bg-white rounded-lg border border-gray-200 p-4">
			<div class="flex items-center justify-between">
				<div>
					<p class="text-sm text-gray-600">Active Flows</p>
					<p class="text-2xl font-bold text-green-600">{stats.active_flows}</p>
				</div>
				<Play class="w-8 h-8 text-green-500" />
			</div>
		</div>

		<div class="bg-white rounded-lg border border-gray-200 p-4">
			<div class="flex items-center justify-between">
				<div>
					<p class="text-sm text-gray-600">Inactive Flows</p>
					<p class="text-2xl font-bold text-gray-600">{stats.inactive_flows}</p>
				</div>
				<Phone class="w-8 h-8 text-gray-400" />
			</div>
		</div>

		<div class="bg-white rounded-lg border border-gray-200 p-4">
			<div class="flex items-center justify-between">
				<div>
					<p class="text-sm text-gray-600">Total Nodes</p>
					<p class="text-2xl font-bold text-blue-600">{stats.total_nodes}</p>
				</div>
				<Phone class="w-8 h-8 text-blue-400" />
			</div>
		</div>
	</div>

	<!-- Filters and Actions -->
	<div class="bg-white rounded-lg border border-gray-200 p-4 mb-4">
		<div class="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
			<div class="flex flex-col md:flex-row gap-4 flex-1">
				<!-- Search -->
				<div class="relative flex-1">
					<Search class="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
					<input
						type="text"
						placeholder="Search flows..."
						bind:value={searchQuery}
						class="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
					/>
				</div>

				<!-- Status Filter -->
				<select
					bind:value={statusFilter}
					class="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
				>
					<option value="all">All Status</option>
					<option value="active">Active</option>
					<option value="inactive">Inactive</option>
				</select>
			</div>

			<!-- Create Flow Button -->
			<a
				href="/operations/ivr/builder"
				class="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
			>
				<Plus class="w-4 h-4" />
				Create Flow
			</a>
		</div>
	</div>

	<!-- IVR Flows Table -->
	<div class="bg-white rounded-lg border border-gray-200 overflow-hidden">
		{#if loading}
			<div class="p-8 text-center">
				<div class="inline-block animate-spin rounded-full h-8 w-8 border-4 border-gray-300 border-t-blue-600"></div>
				<p class="mt-2 text-gray-600">Loading IVR flows...</p>
			</div>
		{:else if error}
			<div class="p-8 text-center">
				<p class="text-red-600">{error}</p>
				<button
					onclick={loadFlows}
					class="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
				>
					Retry
				</button>
			</div>
		{:else if filteredFlows.length === 0}
			<div class="p-8 text-center">
				<Phone class="w-12 h-12 text-gray-300 mx-auto mb-2" />
				<p class="text-gray-600">No IVR flows found</p>
				<a
					href="/operations/ivr/builder"
					class="mt-4 inline-block px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
				>
					Create Your First Flow
				</a>
			</div>
		{:else}
			<table class="w-full">
				<thead class="bg-gray-50 border-b border-gray-200">
					<tr>
						<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
							Flow Name
						</th>
						<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
							Description
						</th>
						<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
							Status
						</th>
						<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
							Version
						</th>
						<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
							Timeout
						</th>
						<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
							Updated
						</th>
						<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
							Actions
						</th>
					</tr>
				</thead>
				<tbody class="bg-white divide-y divide-gray-200">
					{#each filteredFlows as flow}
						<tr class="hover:bg-gray-50">
							<td class="px-6 py-4 whitespace-nowrap">
								<div class="flex items-center">
									<Phone class="w-5 h-5 {getStatusColor(flow.is_active)} mr-2" />
									<div>
										<div class="text-sm font-medium text-gray-900">{flow.name}</div>
										<div class="text-sm text-gray-500">ID: {flow.id}</div>
									</div>
								</div>
							</td>
							<td class="px-6 py-4">
								<div class="text-sm text-gray-900 max-w-xs truncate">
									{flow.description || 'No description'}
								</div>
							</td>
							<td class="px-6 py-4 whitespace-nowrap">
								<span class="px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full border {getStatusBadge(flow.is_active)}">
									{flow.is_active ? 'Active' : 'Inactive'}
								</span>
							</td>
							<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
								v{flow.version}
							</td>
							<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
								{flow.timeout_seconds}s
							</td>
							<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
								{formatDate(flow.updated_at)}
							</td>
							<td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
								<div class="flex items-center gap-2">
									<button
										onclick={() => testFlow(flow.id)}
										class="text-blue-600 hover:text-blue-900"
										title="Test Flow"
									>
										<Play class="w-4 h-4" />
									</button>
									<a
										href="/operations/ivr/builder?id={flow.id}"
										class="text-indigo-600 hover:text-indigo-900"
										title="Edit Flow"
									>
										<Edit class="w-4 h-4" />
									</a>
									<button
										onclick={() => toggleFlowStatus(flow.id)}
										class={flow.is_active ? 'text-gray-600 hover:text-gray-900' : 'text-green-600 hover:text-green-900'}
										title={flow.is_active ? 'Deactivate' : 'Activate'}
									>
										<Phone class="w-4 h-4" />
									</button>
									<button
										onclick={() => deleteFlow(flow.id)}
										class="text-red-600 hover:text-red-900"
										title="Delete Flow"
									>
										<Trash2 class="w-4 h-4" />
									</button>
								</div>
							</td>
						</tr>
					{/each}
				</tbody>
			</table>
		{/if}
	</div>
</div>
