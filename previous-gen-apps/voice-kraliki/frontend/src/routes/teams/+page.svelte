<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';

	interface Team {
		id: number;
		name: string;
		description: string;
		parent_team_id: number | null;
		manager_id: number | null;
		total_agents: number;
		active_agents: number;
		total_calls_handled: number;
		is_active: boolean;
		created_at: string;
		child_teams?: Team[];
	}

	let teams: Team[] = [];
	let hierarchyView: Team[] = [];
	let loading = true;
	let error = '';
	let viewMode: 'list' | 'hierarchy' = 'hierarchy';
	let expandedTeams = new Set<number>();

	onMount(async () => {
		await loadTeams();
	});

	async function loadTeams() {
		try {
			loading = true;
			const token = localStorage.getItem('token');

			if (viewMode === 'hierarchy') {
				const response = await fetch('/api/team-management/teams/hierarchy', {
					headers: { Authorization: `Bearer ${token}` }
				});

				if (response.ok) {
					hierarchyView = await response.json();
				}
			} else {
				const response = await fetch('/api/team-management/teams', {
					headers: { Authorization: `Bearer ${token}` }
				});

				if (response.ok) {
					teams = await response.json();
				}
			}
		} catch (err) {
			error = `Error loading teams: ${err}`;
		} finally {
			loading = false;
		}
	}

	function toggleExpand(teamId: number) {
		if (expandedTeams.has(teamId)) {
			expandedTeams.delete(teamId);
		} else {
			expandedTeams.add(teamId);
		}
		expandedTeams = expandedTeams; // Trigger reactivity
	}

	async function toggleViewMode() {
		viewMode = viewMode === 'list' ? 'hierarchy' : 'list';
		await loadTeams();
	}

	async function toggleTeamStatus(teamId: number, currentStatus: boolean) {
		try {
			const token = localStorage.getItem('token');
			const response = await fetch(`/api/team-management/teams/${teamId}`, {
				method: 'PUT',
				headers: {
					'Content-Type': 'application/json',
					Authorization: `Bearer ${token}`
				},
				body: JSON.stringify({ is_active: !currentStatus })
			});

			if (response.ok) {
				await loadTeams();
			} else {
				alert('Failed to update team status');
			}
		} catch (err) {
			alert(`Error updating team: ${err}`);
		}
	}
</script>

<div class="container mx-auto p-6">
	<div class="mb-6 flex items-center justify-between">
		<div>
			<h1 class="text-3xl font-bold">Teams</h1>
			<p class="text-gray-600 mt-1">Manage team hierarchy and structure</p>
		</div>

		<div class="flex gap-3">
			<button
				onclick={toggleViewMode}
				class="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
			>
				{viewMode === 'hierarchy' ? '📋 List View' : '🌳 Hierarchy View'}
			</button>
			<button
				onclick={() => goto('/teams/new')}
				class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
			>
				+ New Team
			</button>
		</div>
	</div>

	{#if error}
		<div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
			{error}
		</div>
	{/if}

	{#if loading}
		<div class="text-center py-12">
			<div
				class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"
			></div>
			<p class="mt-4 text-gray-600">Loading teams...</p>
		</div>
	{:else if viewMode === 'hierarchy'}
		<!-- Hierarchy View -->
		{#if hierarchyView.length === 0}
			<div class="text-center py-12 bg-gray-50 rounded-lg">
				<p class="text-gray-600 mb-4">No teams yet</p>
				<button
					onclick={() => goto('/teams/new')}
					class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
				>
					Create First Team
				</button>
			</div>
		{:else}
			<div class="space-y-2">
				{#each hierarchyView as team}
					<div class="bg-white rounded-lg shadow">

						<div class="p-4 flex items-center justify-between hover:bg-gray-50">
							<div class="flex items-center gap-3 flex-1">
								{#if team.child_teams && team.child_teams.length > 0}
									<button
										onclick={() => toggleExpand(team.id)}
										class="text-gray-500 hover:text-gray-700 w-6"
									>
										{expandedTeams.has(team.id) ? '▼' : '▶'}
									</button>
								{:else}
									<div class="w-6"></div>
								{/if}

								<button
									onclick={() => goto(`/teams/${team.id}`)}
									class="flex-1 text-left"
								>
									<div class="flex items-center gap-3">
										<h3 class="text-lg font-semibold">{team.name}</h3>
										<span
											class="px-2 py-1 text-xs rounded-full {team.is_active
												? 'bg-green-100 text-green-800'
												: 'bg-gray-100 text-gray-800'}"
										>
											{team.is_active ? 'Active' : 'Inactive'}
										</span>
									</div>
									{#if team.description}
										<p class="text-sm text-gray-600 mt-1">{team.description}</p>
									{/if}
								</button>
							</div>

							<div class="flex items-center gap-6 text-sm text-gray-600">
								<div class="text-center">
									<div class="font-semibold text-gray-900">{team.total_agents}</div>
									<div>Agents</div>
								</div>
								<div class="text-center">
									<div class="font-semibold text-green-600">{team.active_agents}</div>
									<div>Active</div>
								</div>
								<div class="text-center">
									<div class="font-semibold text-gray-900">{team.total_calls_handled}</div>
									<div>Calls</div>
								</div>

								<button
									onclick={() => goto(`/teams/${team.id}`)}
									class="px-3 py-1 text-blue-600 hover:bg-blue-50 rounded"
								>
									View
								</button>
							</div>
						</div>

						<!-- Child Teams -->
						{#if expandedTeams.has(team.id) && team.child_teams && team.child_teams.length > 0}
							<div class="pl-12 pr-4 pb-4 space-y-2">
								{#each team.child_teams as childTeam}
									<div class="bg-gray-50 rounded-lg p-3 flex items-center justify-between">
										<button
											onclick={() => goto(`/teams/${childTeam.id}`)}
											class="flex-1 text-left"
										>
											<div class="flex items-center gap-2">
												<span class="text-gray-400">└─</span>
												<h4 class="font-medium">{childTeam.name}</h4>
												<span
													class="px-2 py-1 text-xs rounded-full {childTeam.is_active
														? 'bg-green-100 text-green-800'
														: 'bg-gray-100 text-gray-800'}"
												>
													{childTeam.is_active ? 'Active' : 'Inactive'}
												</span>
											</div>
										</button>

										<div class="flex items-center gap-4 text-sm text-gray-600">
											<div>{childTeam.total_agents} agents</div>
											<button
												onclick={() => goto(`/teams/${childTeam.id}`)}
												class="px-3 py-1 text-blue-600 hover:bg-blue-100 rounded"
											>
												View
											</button>
										</div>
									</div>
								{/each}
							</div>
						{/if}
					</div>
				{/each}
			</div>
		{/if}
	{:else}
		<!-- List View -->
		{#if teams.length === 0}
			<div class="text-center py-12 bg-gray-50 rounded-lg">
				<p class="text-gray-600 mb-4">No teams yet</p>
				<button
					onclick={() => goto('/teams/new')}
					class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
				>
					Create First Team
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
								Team Name
							</th>
							<th
								class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
							>
								Status
							</th>
							<th
								class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
							>
								Total Agents
							</th>
							<th
								class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
							>
								Active Agents
							</th>
							<th
								class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
							>
								Total Calls
							</th>
							<th
								class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider"
							>
								Actions
							</th>
						</tr>
					</thead>
					<tbody class="bg-white divide-y divide-gray-200">
						{#each teams as team}
							<tr class="hover:bg-gray-50">
								<td class="px-6 py-4 whitespace-nowrap">
									<div class="text-sm font-medium text-gray-900">{team.name}</div>
									{#if team.description}
										<div class="text-sm text-gray-500">{team.description}</div>
									{/if}
								</td>
								<td class="px-6 py-4 whitespace-nowrap">
									<button
										onclick={() => toggleTeamStatus(team.id, team.is_active)}
										class="px-2 text-xs font-semibold rounded-full {team.is_active
											? 'bg-green-100 text-green-800 hover:bg-green-200'
											: 'bg-gray-100 text-gray-800 hover:bg-gray-200'}"
									>
										{team.is_active ? 'Active' : 'Inactive'}
									</button>
								</td>
								<td class="px-6 py-4 whitespace-nowrap">
									<div class="text-sm text-gray-900">{team.total_agents}</div>
								</td>
								<td class="px-6 py-4 whitespace-nowrap">
									<div class="text-sm text-green-600 font-medium">{team.active_agents}</div>
								</td>
								<td class="px-6 py-4 whitespace-nowrap">
									<div class="text-sm text-gray-900">{team.total_calls_handled}</div>
								</td>
								<td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
									<button
										onclick={() => goto(`/teams/${team.id}`)}
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
		{/if}
	{/if}
</div>
