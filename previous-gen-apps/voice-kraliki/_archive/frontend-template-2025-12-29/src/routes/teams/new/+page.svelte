<script lang="ts">
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';

	interface Team {
		id: number;
		name: string;
	}

	let formData = {
		name: '',
		description: '',
		parent_team_id: null as number | null,
		timezone: 'UTC',
		working_hours: { start: '09:00', end: '17:00' },
		working_days: [1, 2, 3, 4, 5], // Monday-Friday
		tags: [] as string[],
		metadata: {}
	};

	let teams: Team[] = [];
	let saving = false;
	let error = '';
	let tagInput = '';

	const timezones = [
		'UTC',
		'America/New_York',
		'America/Chicago',
		'America/Denver',
		'America/Los_Angeles',
		'Europe/London',
		'Europe/Paris',
		'Asia/Tokyo',
		'Asia/Shanghai',
		'Australia/Sydney'
	];

	const daysOfWeek = [
		{ value: 1, label: 'Mon' },
		{ value: 2, label: 'Tue' },
		{ value: 3, label: 'Wed' },
		{ value: 4, label: 'Thu' },
		{ value: 5, label: 'Fri' },
		{ value: 6, label: 'Sat' },
		{ value: 0, label: 'Sun' }
	];

	onMount(async () => {
		await loadTeams();
	});

	async function loadTeams() {
		try {
			const token = localStorage.getItem('token');
			const response = await fetch('/api/team-management/teams', {
				headers: { Authorization: `Bearer ${token}` }
			});

			if (response.ok) {
				teams = await response.json();
			}
		} catch (err) {
			console.error('Error loading teams:', err);
		}
	}

	function toggleDay(day: number) {
		const index = formData.working_days.indexOf(day);
		if (index > -1) {
			formData.working_days = formData.working_days.filter((d) => d !== day);
		} else {
			formData.working_days = [...formData.working_days, day];
		}
	}

	function addTag() {
		const tag = tagInput.trim();
		if (tag && !formData.tags.includes(tag)) {
			formData.tags = [...formData.tags, tag];
			tagInput = '';
		}
	}

	function removeTag(tag: string) {
		formData.tags = formData.tags.filter((t) => t !== tag);
	}

	async function handleSubmit() {
		if (!formData.name.trim()) {
			error = 'Team name is required';
			return;
		}

		if (formData.working_days.length === 0) {
			error = 'Select at least one working day';
			return;
		}

		try {
			saving = true;
			error = '';

			const token = localStorage.getItem('token');

			const payload = {
				...formData,
				parent_team_id: formData.parent_team_id || undefined
			};

			const response = await fetch('/api/team-management/teams', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
					Authorization: `Bearer ${token}`
				},
				body: JSON.stringify(payload)
			});

			if (!response.ok) {
				const data = await response.json();
				throw new Error(data.detail || 'Failed to create team');
			}

			const team = await response.json();
			goto(`/teams/${team.id}`);
		} catch (err) {
			error = `Error: ${err}`;
		} finally {
			saving = false;
		}
	}
</script>

<div class="container mx-auto p-6 max-w-4xl">
	<div class="mb-6">
		<button onclick={() => goto('/teams')} class="text-gray-600 hover:text-gray-900 mb-2">
			← Back to Teams
		</button>
		<h1 class="text-3xl font-bold">Create New Team</h1>
		<p class="text-gray-600 mt-1">Set up a new team with working hours and structure</p>
	</div>

	{#if error}
		<div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
			{error}
		</div>
	{/if}

	<form onsubmit={(e) => { e.preventDefault(); handleSubmit(e); }} class="bg-white rounded-lg shadow-lg p-6 space-y-6">
		<!-- Basic Information -->
		<div>
			<h2 class="text-xl font-semibold mb-4">Basic Information</h2>

			<div class="space-y-4">
				<div>
					<label for="name" class="block text-sm font-medium text-gray-700 mb-1">
						Team Name *
					</label>
					<input
						type="text"
						id="name"
						bind:value={formData.name}
						required
						class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
						placeholder="e.g., Sales Team, Support Team"
					/>
				</div>

				<div>
					<label for="description" class="block text-sm font-medium text-gray-700 mb-1">
						Description
					</label>
					<textarea
						id="description"
						bind:value={formData.description}
						rows="3"
						class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
						placeholder="Describe the team's purpose and responsibilities"
					></textarea>
				</div>

				<div>
					<label for="parent_team" class="block text-sm font-medium text-gray-700 mb-1">
						Parent Team (Optional)
					</label>
					<select
						id="parent_team"
						bind:value={formData.parent_team_id}
						class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
					>
						<option value={null}>None (Top-level team)</option>
						{#each teams as team}
							<option value={team.id}>{team.name}</option>
						{/each}
					</select>
					<p class="mt-1 text-sm text-gray-500">
						Create a hierarchical structure by selecting a parent team
					</p>
				</div>
			</div>
		</div>

		<!-- Working Schedule -->
		<div class="border-t pt-6">
			<h2 class="text-xl font-semibold mb-4">Working Schedule</h2>

			<div class="space-y-4">
				<div>
					<label for="timezone" class="block text-sm font-medium text-gray-700 mb-1">
						Timezone *
					</label>
					<select
						id="timezone"
						bind:value={formData.timezone}
						class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
					>
						{#each timezones as tz}
							<option value={tz}>{tz}</option>
						{/each}
					</select>
				</div>

				<div class="grid grid-cols-2 gap-4">
					<div>
						<label for="start_time" class="block text-sm font-medium text-gray-700 mb-1">
							Start Time
						</label>
						<input
							type="time"
							id="start_time"
							bind:value={formData.working_hours.start}
							class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
						/>
					</div>

					<div>
						<label for="end_time" class="block text-sm font-medium text-gray-700 mb-1">
							End Time
						</label>
						<input
							type="time"
							id="end_time"
							bind:value={formData.working_hours.end}
							class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
						/>
					</div>
				</div>

				<div>
					<label class="block text-sm font-medium text-gray-700 mb-2">
						Working Days *
					</label>
					<div class="flex gap-2">
						{#each daysOfWeek as day}
							<button
								type="button"
								onclick={() => toggleDay(day.value)}
								class="px-4 py-2 rounded-md font-medium {formData.working_days.includes(
									day.value
								)
									? 'bg-blue-600 text-white'
									: 'bg-gray-200 text-gray-700 hover:bg-gray-300'}"
							>
								{day.label}
							</button>
						{/each}
					</div>
				</div>
			</div>
		</div>

		<!-- Tags -->
		<div class="border-t pt-6">
			<h2 class="text-xl font-semibold mb-4">Tags (Optional)</h2>

			<div class="space-y-3">
				<div class="flex gap-2">
					<input
						type="text"
						bind:value={tagInput}
						onkeypress={(e) => e.key === 'Enter' && (e.preventDefault(), addTag())}
						class="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
						placeholder="Add tags (e.g., sales, support, tier1)"
					/>
					<button
						type="button"
						onclick={addTag}
						class="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700"
					>
						Add Tag
					</button>
				</div>

				{#if formData.tags.length > 0}
					<div class="flex flex-wrap gap-2">
						{#each formData.tags as tag}
							<span
								class="inline-flex items-center gap-1 px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm"
							>
								{tag}
								<button
									type="button"
									onclick={() => removeTag(tag)}
									class="text-blue-600 hover:text-blue-800"
								>
									×
								</button>
							</span>
						{/each}
					</div>
				{/if}
			</div>
		</div>

		<!-- Actions -->
		<div class="flex justify-end gap-3 pt-4 border-t">
			<button
				type="button"
				onclick={() => goto('/teams')}
				class="px-6 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
			>
				Cancel
			</button>
			<button
				type="submit"
				disabled={saving}
				class="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
			>
				{saving ? 'Creating...' : 'Create Team'}
			</button>
		</div>
	</form>
</div>
