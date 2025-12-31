<script lang="ts">
	import { onMount } from 'svelte';
	import { GitBranch, Play, Edit, Trash2, Plus, Search, ArrowUpDown } from 'lucide-svelte';

	interface RoutingRule {
		id: number;
		name: string;
		description: string | null;
		team_id: number;
		priority: number;
		strategy: string;
		is_active: boolean;
		conditions: any[];
		targets: any[];
		fallback_action: string | null;
		created_at: string;
		updated_at: string;
	}

	let rules: RoutingRule[] = [];
	let loading = true;
	let error: string | null = null;
	let searchQuery = '';
	let statusFilter: 'all' | 'active' | 'inactive' = 'all';
	let strategyFilter: string = 'all';

	// Statistics
	let stats = {
		total_rules: 0,
		active_rules: 0,
		inactive_rules: 0,
		avg_priority: 0
	};

	const strategyLabels: Record<string, string> = {
		skill_based: 'Skill-Based',
		least_busy: 'Least Busy',
		longest_idle: 'Longest Idle',
		round_robin: 'Round Robin',
		priority: 'Priority',
		language: 'Language',
		vip: 'VIP',
		custom: 'Custom'
	};

	onMount(async () => {
		await loadRules();
	});

	async function loadRules() {
		loading = true;
		error = null;
		try {
			const response = await fetch('http://localhost:8000/api/routing/rules');
			if (!response.ok) throw new Error('Failed to load routing rules');
			rules = await response.json();
			calculateStats();
		} catch (err) {
			error = err instanceof Error ? err.message : 'Unknown error occurred';
		} finally {
			loading = false;
		}
	}

	function calculateStats() {
		stats.total_rules = rules.length;
		stats.active_rules = rules.filter((r) => r.is_active).length;
		stats.inactive_rules = rules.filter((r) => !r.is_active).length;
		stats.avg_priority =
			rules.length > 0
				? Math.round(rules.reduce((sum, r) => sum + r.priority, 0) / rules.length)
				: 0;
	}

	async function toggleRuleStatus(ruleId: number) {
		try {
			const rule = rules.find((r) => r.id === ruleId);
			if (!rule) return;

			const response = await fetch(`http://localhost:8000/api/routing/rules/${ruleId}`, {
				method: 'PUT',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({
					...rule,
					is_active: !rule.is_active
				})
			});

			if (!response.ok) throw new Error('Failed to update rule status');
			await loadRules();
		} catch (err) {
			alert(err instanceof Error ? err.message : 'Failed to update rule status');
		}
	}

	async function deleteRule(ruleId: number) {
		if (!confirm('Are you sure you want to delete this routing rule?')) return;

		try {
			const response = await fetch(`http://localhost:8000/api/routing/rules/${ruleId}`, {
				method: 'DELETE'
			});

			if (!response.ok) throw new Error('Failed to delete rule');
			await loadRules();
		} catch (err) {
			alert(err instanceof Error ? err.message : 'Failed to delete rule');
		}
	}

	async function testRule(ruleId: number) {
		try {
			const response = await fetch(`http://localhost:8000/api/routing/rules/${ruleId}/test`, {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({
					caller_phone: '+1234567890',
					required_skills: ['sales'],
					language: 'en'
				})
			});

			if (!response.ok) throw new Error('Failed to test rule');
			const result = await response.json();
			alert(`Test Result:\n${JSON.stringify(result, null, 2)}`);
		} catch (err) {
			alert(err instanceof Error ? err.message : 'Failed to test rule');
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

	function getStrategyBadge(strategy: string): string {
		const badges: Record<string, string> = {
			skill_based: 'bg-blue-100 text-blue-800 border-blue-200',
			least_busy: 'bg-purple-100 text-purple-800 border-purple-200',
			longest_idle: 'bg-indigo-100 text-indigo-800 border-indigo-200',
			round_robin: 'bg-green-100 text-green-800 border-green-200',
			priority: 'bg-red-100 text-red-800 border-red-200',
			language: 'bg-yellow-100 text-yellow-800 border-yellow-200',
			vip: 'bg-pink-100 text-pink-800 border-pink-200',
			custom: 'bg-gray-100 text-gray-800 border-gray-200'
		};
		return badges[strategy] || 'bg-gray-100 text-gray-800 border-gray-200';
	}

	$: filteredRules = rules.filter((rule) => {
		const matchesSearch =
			searchQuery === '' ||
			rule.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
			(rule.description && rule.description.toLowerCase().includes(searchQuery.toLowerCase()));

		const matchesStatus =
			statusFilter === 'all' ||
			(statusFilter === 'active' && rule.is_active) ||
			(statusFilter === 'inactive' && !rule.is_active);

		const matchesStrategy = strategyFilter === 'all' || rule.strategy === strategyFilter;

		return matchesSearch && matchesStatus && matchesStrategy;
	}).sort((a, b) => a.priority - b.priority);
</script>

<div class="p-6 max-w-7xl mx-auto">
	<div class="mb-6">
		<h1 class="text-3xl font-bold text-gray-900 mb-2">Call Routing Rules</h1>
		<p class="text-gray-600">
			Configure intelligent call routing strategies to connect callers with the right agents
		</p>
	</div>

	<!-- Statistics Cards -->
	<div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
		<div class="bg-white rounded-lg border border-gray-200 p-4">
			<div class="flex items-center justify-between">
				<div>
					<p class="text-sm text-gray-600">Total Rules</p>
					<p class="text-2xl font-bold text-gray-900">{stats.total_rules}</p>
				</div>
				<GitBranch class="w-8 h-8 text-blue-500" />
			</div>
		</div>

		<div class="bg-white rounded-lg border border-gray-200 p-4">
			<div class="flex items-center justify-between">
				<div>
					<p class="text-sm text-gray-600">Active Rules</p>
					<p class="text-2xl font-bold text-green-600">{stats.active_rules}</p>
				</div>
				<Play class="w-8 h-8 text-green-500" />
			</div>
		</div>

		<div class="bg-white rounded-lg border border-gray-200 p-4">
			<div class="flex items-center justify-between">
				<div>
					<p class="text-sm text-gray-600">Inactive Rules</p>
					<p class="text-2xl font-bold text-gray-600">{stats.inactive_rules}</p>
				</div>
				<GitBranch class="w-8 h-8 text-gray-400" />
			</div>
		</div>

		<div class="bg-white rounded-lg border border-gray-200 p-4">
			<div class="flex items-center justify-between">
				<div>
					<p class="text-sm text-gray-600">Avg Priority</p>
					<p class="text-2xl font-bold text-blue-600">{stats.avg_priority}</p>
				</div>
				<ArrowUpDown class="w-8 h-8 text-blue-400" />
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
						placeholder="Search rules..."
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

				<!-- Strategy Filter -->
				<select
					bind:value={strategyFilter}
					class="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
				>
					<option value="all">All Strategies</option>
					{#each Object.entries(strategyLabels) as [value, label]}
						<option value={value}>{label}</option>
					{/each}
				</select>
			</div>

			<!-- Create Rule Button -->
			<a
				href="/operations/routing/builder"
				class="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
			>
				<Plus class="w-4 h-4" />
				Create Rule
			</a>
		</div>
	</div>

	<!-- Routing Rules Table -->
	<div class="bg-white rounded-lg border border-gray-200 overflow-hidden">
		{#if loading}
			<div class="p-8 text-center">
				<div class="inline-block animate-spin rounded-full h-8 w-8 border-4 border-gray-300 border-t-blue-600"></div>
				<p class="mt-2 text-gray-600">Loading routing rules...</p>
			</div>
		{:else if error}
			<div class="p-8 text-center">
				<p class="text-red-600">{error}</p>
				<button
					onclick={loadRules}
					class="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
				>
					Retry
				</button>
			</div>
		{:else if filteredRules.length === 0}
			<div class="p-8 text-center">
				<GitBranch class="w-12 h-12 text-gray-300 mx-auto mb-2" />
				<p class="text-gray-600">No routing rules found</p>
				<a
					href="/operations/routing/builder"
					class="mt-4 inline-block px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
				>
					Create Your First Rule
				</a>
			</div>
		{:else}
			<table class="w-full">
				<thead class="bg-gray-50 border-b border-gray-200">
					<tr>
						<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
							Priority
						</th>
						<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
							Rule Name
						</th>
						<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
							Strategy
						</th>
						<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
							Conditions
						</th>
						<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
							Targets
						</th>
						<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
							Status
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
					{#each filteredRules as rule}
						<tr class="hover:bg-gray-50">
							<td class="px-6 py-4 whitespace-nowrap">
								<div class="flex items-center">
									<span class="px-3 py-1 bg-gray-100 text-gray-800 rounded-full text-sm font-medium">
										{rule.priority}
									</span>
								</div>
							</td>
							<td class="px-6 py-4">
								<div class="flex items-center">
									<GitBranch class="w-5 h-5 {getStatusColor(rule.is_active)} mr-2" />
									<div>
										<div class="text-sm font-medium text-gray-900">{rule.name}</div>
										<div class="text-sm text-gray-500">
											{rule.description || 'No description'}
										</div>
									</div>
								</div>
							</td>
							<td class="px-6 py-4 whitespace-nowrap">
								<span class="px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full border {getStrategyBadge(rule.strategy)}">
									{strategyLabels[rule.strategy] || rule.strategy}
								</span>
							</td>
							<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
								{rule.conditions?.length || 0}
							</td>
							<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
								{rule.targets?.length || 0}
							</td>
							<td class="px-6 py-4 whitespace-nowrap">
								<span class="px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full border {getStatusBadge(rule.is_active)}">
									{rule.is_active ? 'Active' : 'Inactive'}
								</span>
							</td>
							<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
								{formatDate(rule.updated_at)}
							</td>
							<td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
								<div class="flex items-center gap-2">
									<button
										onclick={() => testRule(rule.id)}
										class="text-blue-600 hover:text-blue-900"
										title="Test Rule"
									>
										<Play class="w-4 h-4" />
									</button>
									<a
										href="/operations/routing/builder?id={rule.id}"
										class="text-indigo-600 hover:text-indigo-900"
										title="Edit Rule"
									>
										<Edit class="w-4 h-4" />
									</a>
									<button
										onclick={() => toggleRuleStatus(rule.id)}
										class={rule.is_active ? 'text-gray-600 hover:text-gray-900' : 'text-green-600 hover:text-green-900'}
										title={rule.is_active ? 'Deactivate' : 'Activate'}
									>
										<GitBranch class="w-4 h-4" />
									</button>
									<button
										onclick={() => deleteRule(rule.id)}
										class="text-red-600 hover:text-red-900"
										title="Delete Rule"
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
