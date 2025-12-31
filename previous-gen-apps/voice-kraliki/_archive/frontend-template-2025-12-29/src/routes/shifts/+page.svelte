<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';

	interface Shift {
		id: number;
		agent_id: number;
		team_id: number | null;
		shift_date: string;
		start_time: string;
		end_time: string;
		timezone: string;
		status: string;
		actual_start_time: string | null;
		actual_end_time: string | null;
		clock_in_time: string | null;
		clock_out_time: string | null;
		break_duration_minutes: number;
		actual_break_minutes: number;
		is_recurring: boolean;
		notes: string | null;
		agent?: {
			display_name: string;
			employee_id: string;
		};
	}

	let shifts: Shift[] = [];
	let filteredShifts: Shift[] = [];
	let loading = true;
	let error = '';
	let viewMode: 'today' | 'week' | 'all' = 'today';
	let statusFilter = 'all';
	let selectedDate = new Date().toISOString().split('T')[0];

	const statusColors: Record<string, string> = {
		scheduled: 'bg-blue-100 text-blue-800',
		in_progress: 'bg-green-100 text-green-800',
		completed: 'bg-gray-100 text-gray-800',
		cancelled: 'bg-red-100 text-red-800',
		no_show: 'bg-red-100 text-red-800'
	};

	const statusOptions = ['all', 'scheduled', 'in_progress', 'completed', 'cancelled', 'no_show'];

	onMount(async () => {
		await loadShifts();
	});

	async function loadShifts() {
		try {
			loading = true;
			const token = localStorage.getItem('token');

			let url = '/api/team-management/shifts';
			if (viewMode === 'today') {
				url += `?date=${selectedDate}`;
			}

			const response = await fetch(url, {
				headers: { Authorization: `Bearer ${token}` }
			});

			if (response.ok) {
				shifts = await response.json();
				filterShifts();
			}
		} catch (err) {
			error = `Error loading shifts: ${err}`;
		} finally {
			loading = false;
		}
	}

	function filterShifts() {
		const today = new Date().toISOString().split('T')[0];
		const weekAgo = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0];

		filteredShifts = shifts.filter((shift) => {
			const matchesStatus = statusFilter === 'all' || shift.status === statusFilter;

			let matchesDate = true;
			if (viewMode === 'today') {
				matchesDate = shift.shift_date === selectedDate;
			} else if (viewMode === 'week') {
				matchesDate = shift.shift_date >= weekAgo && shift.shift_date <= today;
			}

			return matchesStatus && matchesDate;
		});

		// Sort by date and time
		filteredShifts.sort((a, b) => {
			const dateCompare = a.shift_date.localeCompare(b.shift_date);
			if (dateCompare !== 0) return dateCompare;
			return a.start_time.localeCompare(b.start_time);
		});
	}

	async function handleViewModeChange(mode: 'today' | 'week' | 'all') {
		viewMode = mode;
		await loadShifts();
	}

	function handleStatusFilter(status: string) {
		statusFilter = status;
		filterShifts();
	}

	async function handleDateChange(event: Event) {
		selectedDate = (event.target as HTMLInputElement).value;
		await loadShifts();
	}

	async function clockIn(shiftId: number) {
		try {
			const token = localStorage.getItem('token');
			const response = await fetch(`/api/team-management/shifts/${shiftId}/clock-in`, {
				method: 'POST',
				headers: { Authorization: `Bearer ${token}` }
			});

			if (response.ok) {
				await loadShifts();
			} else {
				alert('Failed to clock in');
			}
		} catch (err) {
			alert(`Error: ${err}`);
		}
	}

	async function clockOut(shiftId: number) {
		try {
			const token = localStorage.getItem('token');
			const response = await fetch(`/api/team-management/shifts/${shiftId}/clock-out`, {
				method: 'POST',
				headers: { Authorization: `Bearer ${token}` }
			});

			if (response.ok) {
				await loadShifts();
			} else {
				alert('Failed to clock out');
			}
		} catch (err) {
			alert(`Error: ${err}`);
		}
	}

	function formatDate(dateString: string) {
		return new Date(dateString).toLocaleDateString();
	}

	function formatDateTime(dateString: string | null) {
		if (!dateString) return '-';
		return new Date(dateString).toLocaleTimeString();
	}

	function canClockIn(shift: Shift) {
		return shift.status === 'scheduled' && !shift.clock_in_time;
	}

	function canClockOut(shift: Shift) {
		return shift.status === 'in_progress' && shift.clock_in_time && !shift.clock_out_time;
	}
</script>

<div class="container mx-auto p-6">
	<div class="mb-6 flex items-center justify-between">
		<div>
			<h1 class="text-3xl font-bold">Shift Management</h1>
			<p class="text-gray-600 mt-1">View and manage agent schedules</p>
		</div>

		<button
			onclick={() => goto('/shifts/new')}
			class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
		>
			+ Schedule Shift
		</button>
	</div>

	{#if error}
		<div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
			{error}
		</div>
	{/if}

	<!-- Filters -->
	<div class="mb-6 bg-white rounded-lg shadow p-4">
		<div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
			<!-- View Mode -->
			<div>
				<label class="block text-sm font-medium text-gray-700 mb-2">View Mode</label>
				<div class="flex gap-2">
					{#each ['today', 'week', 'all'] as mode}
						<button
							onclick={() => handleViewModeChange(mode as 'today' | 'week' | 'all')}
							class="px-4 py-2 rounded-md capitalize {viewMode === mode
								? 'bg-blue-600 text-white'
								: 'bg-gray-200 text-gray-700 hover:bg-gray-300'}"
						>
							{mode}
						</button>
					{/each}
				</div>
			</div>

			<!-- Date Selector (for Today view) -->
			{#if viewMode === 'today'}
				<div>
					<label for="date" class="block text-sm font-medium text-gray-700 mb-2">
						Select Date
					</label>
					<input
						type="date"
						id="date"
						value={selectedDate}
						onchange={handleDateChange}
						class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
					/>
				</div>
			{/if}

			<!-- Status Filter -->
			<div>
				<label class="block text-sm font-medium text-gray-700 mb-2">Status</label>
				<select
					bind:value={statusFilter}
					onchange={() => filterShifts()}
					class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 capitalize"
				>
					{#each statusOptions as status}
						<option value={status} class="capitalize">
							{status === 'all' ? 'All Statuses' : status.replace('_', ' ')}
						</option>
					{/each}
				</select>
			</div>
		</div>
	</div>

	<!-- Shifts List -->
	{#if loading}
		<div class="text-center py-12">
			<div
				class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"
			></div>
			<p class="mt-4 text-gray-600">Loading shifts...</p>
		</div>
	{:else if filteredShifts.length === 0}
		<div class="text-center py-12 bg-gray-50 rounded-lg">
			<p class="text-gray-600 mb-4">
				{shifts.length === 0 ? 'No shifts scheduled' : 'No shifts match your filters'}
			</p>
			{#if shifts.length === 0}
				<button
					onclick={() => goto('/shifts/new')}
					class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
				>
					Schedule First Shift
				</button>
			{/if}
		</div>
	{:else}
		<!-- Summary Stats -->
		<div class="grid grid-cols-1 md:grid-cols-5 gap-4 mb-6">
			<div class="bg-white p-4 rounded-lg shadow">
				<div class="text-sm text-gray-600 mb-1">Total</div>
				<div class="text-2xl font-bold">{filteredShifts.length}</div>
			</div>
			<div class="bg-white p-4 rounded-lg shadow">
				<div class="text-sm text-gray-600 mb-1">Scheduled</div>
				<div class="text-2xl font-bold text-blue-600">
					{filteredShifts.filter((s) => s.status === 'scheduled').length}
				</div>
			</div>
			<div class="bg-white p-4 rounded-lg shadow">
				<div class="text-sm text-gray-600 mb-1">In Progress</div>
				<div class="text-2xl font-bold text-green-600">
					{filteredShifts.filter((s) => s.status === 'in_progress').length}
				</div>
			</div>
			<div class="bg-white p-4 rounded-lg shadow">
				<div class="text-sm text-gray-600 mb-1">Completed</div>
				<div class="text-2xl font-bold text-gray-600">
					{filteredShifts.filter((s) => s.status === 'completed').length}
				</div>
			</div>
			<div class="bg-white p-4 rounded-lg shadow">
				<div class="text-sm text-gray-600 mb-1">Issues</div>
				<div class="text-2xl font-bold text-red-600">
					{filteredShifts.filter((s) => s.status === 'no_show' || s.status === 'cancelled')
						.length}
				</div>
			</div>
		</div>

		<!-- Shifts Table -->
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
						<th
							class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider"
						>
							Actions
						</th>
					</tr>
				</thead>
				<tbody class="bg-white divide-y divide-gray-200">
					{#each filteredShifts as shift}
						<tr class="hover:bg-gray-50">
							<td class="px-6 py-4 whitespace-nowrap">
								<div class="text-sm font-medium text-gray-900">
									{shift.agent?.display_name || 'Unknown'}
								</div>
								{#if shift.agent?.employee_id}
									<div class="text-sm text-gray-500">ID: {shift.agent.employee_id}</div>
								{/if}
							</td>
							<td class="px-6 py-4 whitespace-nowrap">
								<div class="text-sm text-gray-900">{formatDate(shift.shift_date)}</div>
							</td>
							<td class="px-6 py-4 whitespace-nowrap">
								<div class="text-sm text-gray-900">
									{shift.start_time} - {shift.end_time}
								</div>
								<div class="text-xs text-gray-500">{shift.timezone}</div>
							</td>
							<td class="px-6 py-4 whitespace-nowrap">
								<div class="text-sm text-gray-900">{formatDateTime(shift.clock_in_time)}</div>
							</td>
							<td class="px-6 py-4 whitespace-nowrap">
								<div class="text-sm text-gray-900">{formatDateTime(shift.clock_out_time)}</div>
							</td>
							<td class="px-6 py-4 whitespace-nowrap">
								<span
									class="px-2 text-xs font-semibold rounded-full capitalize {statusColors[
										shift.status
									]}"
								>
									{shift.status.replace('_', ' ')}
								</span>
								{#if shift.is_recurring}
									<span class="ml-1 text-xs text-gray-500">🔄</span>
								{/if}
							</td>
							<td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
								<div class="flex justify-end gap-2">
									{#if canClockIn(shift)}
										<button
											onclick={() => clockIn(shift.id)}
											class="text-green-600 hover:text-green-900"
										>
											Clock In
										</button>
									{/if}
									{#if canClockOut(shift)}
										<button
											onclick={() => clockOut(shift.id)}
											class="text-orange-600 hover:text-orange-900"
										>
											Clock Out
										</button>
									{/if}
									<button
										onclick={() => goto(`/shifts/${shift.id}`)}
										class="text-blue-600 hover:text-blue-900"
									>
										View
									</button>
								</div>
							</td>
						</tr>
					{/each}
				</tbody>
			</table>
		</div>

		<div class="mt-4 text-sm text-gray-600">
			Showing {filteredShifts.length} of {shifts.length} shifts
		</div>
	{/if}
</div>
