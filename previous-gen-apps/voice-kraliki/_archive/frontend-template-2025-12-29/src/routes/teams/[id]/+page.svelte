<script lang="ts">
	import { page } from '$app/stores';
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';

	interface Team {
		id: number;
		name: string;
		description: string;
		parent_team_id: number | null;
		manager_id: number | null;
		timezone: string;
		working_hours: { start: string; end: string };
		working_days: number[];
		total_agents: number;
		active_agents: number;
		total_calls_handled: number;
		average_handle_time: number | null;
		satisfaction_score: number | null;
		is_active: boolean;
		created_at: string;
		tags: string[];
	}

	interface TeamMember {
		id: number;
		user_id: number;
		role: string;
		is_active: boolean;
		joined_at: string;
		user?: {
			email: string;
			full_name: string;
		};
	}

	interface Performance {
		period_date: string;
		total_calls: number;
		active_agents: number;
		average_wait_time_seconds: number | null;
		service_level_percentage: number | null;
		average_csat: number | null;
		average_handle_time_seconds: number | null;
	}

	$: teamId = parseInt($page.params.id ?? "0");

	let team: Team | null = null;
	let members: TeamMember[] = [];
	let performance: Performance | null = null;
	let loading = true;
	let error = '';
	let activeTab = 'overview';

	const roleColors: Record<string, string> = {
		owner: 'bg-purple-100 text-purple-800',
		manager: 'bg-blue-100 text-blue-800',
		supervisor: 'bg-green-100 text-green-800',
		agent: 'bg-gray-100 text-gray-800',
		viewer: 'bg-yellow-100 text-yellow-800'
	};

	const dayNames = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

	onMount(async () => {
		await loadTeam();
		await loadMembers();
		await loadPerformance();
	});

	async function loadTeam() {
		try {
			const token = localStorage.getItem('token');
			const response = await fetch(`/api/team-management/teams/${teamId}`, {
				headers: { Authorization: `Bearer ${token}` }
			});

			if (response.ok) {
				team = await response.json();
			} else {
				error = 'Team not found';
			}
		} catch (err) {
			error = `Error loading team: ${err}`;
		} finally {
			loading = false;
		}
	}

	async function loadMembers() {
		try {
			const token = localStorage.getItem('token');
			const response = await fetch(`/api/team-management/teams/${teamId}/members`, {
				headers: { Authorization: `Bearer ${token}` }
			});

			if (response.ok) {
				members = await response.json();
			}
		} catch (err) {
			console.error('Error loading members:', err);
		}
	}

	async function loadPerformance() {
		try {
			const token = localStorage.getItem('token');
			const today = new Date().toISOString().split('T')[0];
			const response = await fetch(
				`/api/team-management/teams/${teamId}/performance?period_date=${today}`,
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

	async function removeMember(memberId: number) {
		if (!confirm('Are you sure you want to remove this team member?')) return;

		try {
			const token = localStorage.getItem('token');
			const response = await fetch(`/api/team-management/team-members/${memberId}`, {
				method: 'DELETE',
				headers: { Authorization: `Bearer ${token}` }
			});

			if (response.ok) {
				await loadMembers();
				await loadTeam(); // Refresh team stats
			} else {
				alert('Failed to remove member');
			}
		} catch (err) {
			alert(`Error: ${err}`);
		}
	}

	function formatTime(seconds: number | null) {
		if (seconds === null) return '-';
		const mins = Math.floor(seconds / 60);
		const secs = Math.floor(seconds % 60);
		return `${mins}m ${secs}s`;
	}

	function formatPercentage(value: number | null) {
		if (value === null) return '-';
		return `${value.toFixed(1)}%`;
	}

	function formatScore(score: number | null) {
		if (score === null) return '-';
		return score.toFixed(2);
	}

	function formatDate(dateString: string) {
		return new Date(dateString).toLocaleDateString();
	}
</script>

<div class="container mx-auto p-6">
	{#if loading}
		<div class="text-center py-12">
			<div
				class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"
			></div>
			<p class="mt-4 text-gray-600">Loading team...</p>
		</div>
	{:else if error}
		<div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
			{error}
		</div>
	{:else if team}
		<!-- Header -->
		<div class="mb-6">
			<div class="flex items-center justify-between mb-2">
				<div class="flex items-center gap-4">
					<button onclick={() => goto('/teams')} class="text-gray-600 hover:text-gray-900">
						← Back
					</button>
					<h1 class="text-3xl font-bold">{team.name}</h1>
					<span
						class="px-3 py-1 text-sm font-semibold rounded-full {team.is_active
							? 'bg-green-100 text-green-800'
							: 'bg-gray-100 text-gray-800'}"
					>
						{team.is_active ? 'Active' : 'Inactive'}
					</span>
				</div>

				<div class="flex gap-2">
					<button
						onclick={() => goto(`/teams/${teamId}/add-member`)}
						class="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
					>
						+ Add Member
					</button>
					<button
						onclick={() => goto(`/teams/${teamId}/edit`)}
						class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
					>
						Edit
					</button>
				</div>
			</div>
			<p class="text-gray-600">{team.description || 'No description provided'}</p>

			{#if team.tags.length > 0}
				<div class="flex gap-2 mt-2">
					{#each team.tags as tag}
						<span class="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded">{tag}</span>
					{/each}
				</div>
			{/if}
		</div>

		<!-- Stats Cards -->
		<div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
			<div class="bg-white p-6 rounded-lg shadow">
				<div class="text-sm text-gray-600 mb-1">Total Agents</div>
				<div class="text-3xl font-bold">{team.total_agents}</div>
			</div>
			<div class="bg-white p-6 rounded-lg shadow">
				<div class="text-sm text-gray-600 mb-1">Active Agents</div>
				<div class="text-3xl font-bold text-green-600">{team.active_agents}</div>
			</div>
			<div class="bg-white p-6 rounded-lg shadow">
				<div class="text-sm text-gray-600 mb-1">Total Calls</div>
				<div class="text-3xl font-bold">{team.total_calls_handled}</div>
			</div>
			<div class="bg-white p-6 rounded-lg shadow">
				<div class="text-sm text-gray-600 mb-1">Avg Handle Time</div>
				<div class="text-3xl font-bold">{formatTime(team.average_handle_time)}</div>
			</div>
		</div>

		<!-- Tabs -->
		<div class="border-b mb-6">
			<nav class="flex gap-4">
				<button
					onclick={() => (activeTab = 'overview')}
					class="pb-2 px-1 {activeTab === 'overview'
						? 'border-b-2 border-blue-600 text-blue-600'
						: 'text-gray-600 hover:text-gray-900'}"
				>
					Overview
				</button>
				<button
					onclick={() => (activeTab = 'members')}
					class="pb-2 px-1 {activeTab === 'members'
						? 'border-b-2 border-blue-600 text-blue-600'
						: 'text-gray-600 hover:text-gray-900'}"
				>
					Members ({members.length})
				</button>
				<button
					onclick={() => (activeTab = 'performance')}
					class="pb-2 px-1 {activeTab === 'performance'
						? 'border-b-2 border-blue-600 text-blue-600'
						: 'text-gray-600 hover:text-gray-900'}"
				>
					Performance
				</button>
			</nav>
		</div>

		<!-- Tab Content -->
		{#if activeTab === 'overview'}
			<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
				<!-- Team Details -->
				<div class="bg-white p-6 rounded-lg shadow">
					<h3 class="text-lg font-semibold mb-4">Team Details</h3>
					<dl class="space-y-2">
						<div class="flex justify-between">
							<dt class="text-gray-600">Timezone:</dt>
							<dd class="font-medium">{team.timezone}</dd>
						</div>
						<div class="flex justify-between">
							<dt class="text-gray-600">Working Hours:</dt>
							<dd class="font-medium">
								{team.working_hours.start} - {team.working_hours.end}
							</dd>
						</div>
						<div class="flex justify-between">
							<dt class="text-gray-600">Working Days:</dt>
							<dd class="font-medium">
								{team.working_days.map((d) => dayNames[d]).join(', ')}
							</dd>
						</div>
						<div class="flex justify-between">
							<dt class="text-gray-600">Created:</dt>
							<dd class="font-medium">{formatDate(team.created_at)}</dd>
						</div>
					</dl>
				</div>

				<!-- Performance Metrics -->
				<div class="bg-white p-6 rounded-lg shadow">
					<h3 class="text-lg font-semibold mb-4">Performance Metrics</h3>
					<dl class="space-y-2">
						<div class="flex justify-between">
							<dt class="text-gray-600">Satisfaction Score:</dt>
							<dd class="font-medium">{formatScore(team.satisfaction_score)}</dd>
						</div>
						<div class="flex justify-between">
							<dt class="text-gray-600">Average Handle Time:</dt>
							<dd class="font-medium">{formatTime(team.average_handle_time)}</dd>
						</div>
						<div class="flex justify-between">
							<dt class="text-gray-600">Total Calls Handled:</dt>
							<dd class="font-medium">{team.total_calls_handled}</dd>
						</div>
					</dl>
				</div>
			</div>
		{:else if activeTab === 'members'}
			{#if members.length === 0}
				<div class="text-center py-12 bg-gray-50 rounded-lg">
					<p class="text-gray-600 mb-4">No team members yet</p>
					<button
						onclick={() => goto(`/teams/${teamId}/add-member`)}
						class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
					>
						Add First Member
					</button>
				</div>
			{:else}
				<div class="bg-white rounded-lg shadow overflow-hidden">
					<table class="min-w-full divide-y divide-gray-200">
						<thead class="bg-gray-50">
							<tr>
								<th
									class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
								>
									Member
								</th>
								<th
									class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
								>
									Role
								</th>
								<th
									class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
								>
									Status
								</th>
								<th
									class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
								>
									Joined
								</th>
								<th
									class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider"
								>
									Actions
								</th>
							</tr>
						</thead>
						<tbody class="bg-white divide-y divide-gray-200">
							{#each members as member}
								<tr class="hover:bg-gray-50">
									<td class="px-6 py-4 whitespace-nowrap">
										<div class="text-sm font-medium text-gray-900">
											{member.user?.full_name || 'Unknown'}
										</div>
										<div class="text-sm text-gray-500">{member.user?.email || ''}</div>
									</td>
									<td class="px-6 py-4 whitespace-nowrap">
										<span
											class="px-2 text-xs font-semibold rounded-full capitalize {roleColors[
												member.role
											] || 'bg-gray-100 text-gray-800'}"
										>
											{member.role}
										</span>
									</td>
									<td class="px-6 py-4 whitespace-nowrap">
										<span
											class="px-2 text-xs font-semibold rounded-full {member.is_active
												? 'bg-green-100 text-green-800'
												: 'bg-gray-100 text-gray-800'}"
										>
											{member.is_active ? 'Active' : 'Inactive'}
										</span>
									</td>
									<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
										{formatDate(member.joined_at)}
									</td>
									<td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
										<button
											onclick={() => removeMember(member.id)}
											class="text-red-600 hover:text-red-900"
										>
											Remove
										</button>
									</td>
								</tr>
							{/each}
						</tbody>
					</table>
				</div>
			{/if}
		{:else if activeTab === 'performance'}
			{#if performance}
				<div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
					<div class="bg-white p-6 rounded-lg shadow">
						<div class="text-sm text-gray-600 mb-1">Today's Calls</div>
						<div class="text-3xl font-bold">{performance.total_calls}</div>
					</div>
					<div class="bg-white p-6 rounded-lg shadow">
						<div class="text-sm text-gray-600 mb-1">Service Level</div>
						<div class="text-3xl font-bold">
							{formatPercentage(performance.service_level_percentage)}
						</div>
					</div>
					<div class="bg-white p-6 rounded-lg shadow">
						<div class="text-sm text-gray-600 mb-1">Avg CSAT</div>
						<div class="text-3xl font-bold">{formatScore(performance.average_csat)}</div>
					</div>
				</div>

				<div class="bg-white p-6 rounded-lg shadow">
					<h3 class="text-lg font-semibold mb-4">Detailed Metrics</h3>
					<dl class="grid grid-cols-2 gap-4">
						<div>
							<dt class="text-sm text-gray-600">Average Wait Time</dt>
							<dd class="text-lg font-semibold">
								{formatTime(performance.average_wait_time_seconds)}
							</dd>
						</div>
						<div>
							<dt class="text-sm text-gray-600">Average Handle Time</dt>
							<dd class="text-lg font-semibold">
								{formatTime(performance.average_handle_time_seconds)}
							</dd>
						</div>
						<div>
							<dt class="text-sm text-gray-600">Active Agents Today</dt>
							<dd class="text-lg font-semibold">{performance.active_agents}</dd>
						</div>
					</dl>
				</div>
			{:else}
				<div class="text-center py-12 bg-gray-50 rounded-lg">
					<p class="text-gray-600">No performance data available for today</p>
				</div>
			{/if}
		{/if}
	{/if}
</div>
