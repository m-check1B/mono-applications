<script lang="ts">
	import { onMount } from 'svelte';

	interface Voicemail {
		id: number;
		caller_phone: string;
		caller_name: string | null;
		status: string;
		recording_url: string;
		recording_duration_seconds: number;
		has_transcription: boolean;
		transcription_text: string | null;
		play_count: number;
		created_at: string;
		priority: number;
	}

	interface VoicemailStats {
		total_messages: number;
		new_messages: number;
		heard_messages: number;
		saved_messages: number;
		archived_messages: number;
		average_duration_seconds: number;
	}

	let voicemails: Voicemail[] = [];
	let stats: VoicemailStats | null = null;
	let loading = true;
	let error = '';
	let selectedStatus = '';
	let currentAgentId = 1; // In production, get from auth context
	let selectedVoicemails: Set<number> = new Set();

	const statusColors: Record<string, string> = {
		new: 'bg-blue-100 text-blue-800 font-semibold',
		heard: 'bg-gray-100 text-gray-800',
		saved: 'bg-green-100 text-green-800',
		archived: 'bg-yellow-100 text-yellow-800',
		deleted: 'bg-red-100 text-red-600'
	};

	const priorityIcons: Record<number, string> = {
		0: '',  // Normal - no icon
		1: '⚠️'  // Urgent
	};

	onMount(async () => {
		await loadVoicemails();
		await loadStats();
	});

	async function loadVoicemails() {
		try {
			const token = localStorage.getItem('token');
			const params = new URLSearchParams({
				agent_id: currentAgentId.toString()
			});

			if (selectedStatus) params.append('status', selectedStatus);

			const response = await fetch(`http://localhost:8000/api/voicemails?${params}`, {
				headers: {
					'Authorization': `Bearer ${token}`,
					'Content-Type': 'application/json'
				}
			});

			if (!response.ok) throw new Error('Failed to load voicemails');

			voicemails = await response.json();
			loading = false;
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to load voicemails';
			loading = false;
		}
	}

	async function loadStats() {
		try {
			const token = localStorage.getItem('token');

			const response = await fetch(`http://localhost:8000/api/voicemails/agent/${currentAgentId}/stats`, {
				headers: {
					'Authorization': `Bearer ${token}`,
					'Content-Type': 'application/json'
				}
			});

			if (!response.ok) throw new Error('Failed to load stats');

			stats = await response.json();
		} catch (e) {
			console.error('Failed to load stats:', e);
		}
	}

	async function playVoicemail(voicemail: Voicemail) {
		try {
			const token = localStorage.getItem('token');

			// Mark as heard
			await fetch(`http://localhost:8000/api/voicemails/${voicemail.id}/heard`, {
				method: 'POST',
				headers: {
					'Authorization': `Bearer ${token}`,
					'Content-Type': 'application/json'
				}
			});

			// In production, implement audio player
			alert(`Playing voicemail from ${voicemail.caller_phone}\nDuration: ${formatDuration(voicemail.recording_duration_seconds)}\nURL: ${voicemail.recording_url}`);

			// Reload to update status
			await loadVoicemails();
			await loadStats();
		} catch (e) {
			alert(e instanceof Error ? e.message : 'Failed to play voicemail');
		}
	}

	async function viewTranscript(voicemail: Voicemail) {
		if (voicemail.transcription_text) {
			alert(`Transcript from ${voicemail.caller_phone}:\n\n${voicemail.transcription_text}`);
		} else {
			alert('No transcript available for this voicemail');
		}
	}

	async function deleteVoicemail(voicemailId: number) {
		if (!confirm('Are you sure you want to delete this voicemail?')) return;

		try {
			const token = localStorage.getItem('token');

			const response = await fetch(`http://localhost:8000/api/voicemails/${voicemailId}`, {
				method: 'DELETE',
				headers: {
					'Authorization': `Bearer ${token}`,
					'Content-Type': 'application/json'
				}
			});

			if (!response.ok) throw new Error('Failed to delete voicemail');

			await loadVoicemails();
			await loadStats();
		} catch (e) {
			alert(e instanceof Error ? e.message : 'Failed to delete voicemail');
		}
	}

	async function bulkMarkAs(status: string) {
		if (selectedVoicemails.size === 0) {
			alert('Please select voicemails first');
			return;
		}

		try {
			const token = localStorage.getItem('token');

			const response = await fetch(`http://localhost:8000/api/voicemails/bulk-mark?agent_id=${currentAgentId}`, {
				method: 'POST',
				headers: {
					'Authorization': `Bearer ${token}`,
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({
					voicemail_ids: Array.from(selectedVoicemails),
					status: status
				})
			});

			if (!response.ok) throw new Error('Failed to update voicemails');

			selectedVoicemails.clear();
			await loadVoicemails();
			await loadStats();
		} catch (e) {
			alert(e instanceof Error ? e.message : 'Failed to update voicemails');
		}
	}

	function toggleSelection(voicemailId: number) {
		if (selectedVoicemails.has(voicemailId)) {
			selectedVoicemails.delete(voicemailId);
		} else {
			selectedVoicemails.add(voicemailId);
		}
		selectedVoicemails = selectedVoicemails; // Trigger reactivity
	}

	function selectAll() {
		if (selectedVoicemails.size === voicemails.length) {
			selectedVoicemails.clear();
		} else {
			voicemails.forEach(vm => selectedVoicemails.add(vm.id));
		}
		selectedVoicemails = selectedVoicemails; // Trigger reactivity
	}

	function formatDuration(seconds: number): string {
		const mins = Math.floor(seconds / 60);
		const secs = seconds % 60;
		return `${mins}:${secs.toString().padStart(2, '0')}`;
	}

	function formatDate(dateString: string): string {
		const date = new Date(dateString);
		const now = new Date();
		const diffMs = now.getTime() - date.getTime();
		const diffMins = Math.floor(diffMs / 60000);

		if (diffMins < 60) return `${diffMins}m ago`;
		const diffHours = Math.floor(diffMins / 60);
		if (diffHours < 24) return `${diffHours}h ago`;
		const diffDays = Math.floor(diffHours / 24);
		if (diffDays < 7) return `${diffDays}d ago`;

		return date.toLocaleDateString();
	}
</script>

<div class="container mx-auto px-4 py-8">
	<div class="mb-8">
		<h1 class="text-3xl font-bold text-gray-900 mb-2">Voicemail Inbox</h1>
		<p class="text-gray-600">Manage your voicemail messages</p>
	</div>

	<!-- Statistics Cards -->
	{#if stats}
		<div class="grid grid-cols-2 md:grid-cols-5 gap-4 mb-8">
			<div class="bg-white rounded-lg shadow p-6">
				<div class="text-sm text-gray-500 mb-1">Total</div>
				<div class="text-3xl font-bold text-gray-900">{stats.total_messages}</div>
			</div>
			<div class="bg-white rounded-lg shadow p-6">
				<div class="text-sm text-gray-500 mb-1">New</div>
				<div class="text-3xl font-bold text-blue-600">{stats.new_messages}</div>
			</div>
			<div class="bg-white rounded-lg shadow p-6">
				<div class="text-sm text-gray-500 mb-1">Heard</div>
				<div class="text-3xl font-bold text-gray-600">{stats.heard_messages}</div>
			</div>
			<div class="bg-white rounded-lg shadow p-6">
				<div class="text-sm text-gray-500 mb-1">Saved</div>
				<div class="text-3xl font-bold text-green-600">{stats.saved_messages}</div>
			</div>
			<div class="bg-white rounded-lg shadow p-6">
				<div class="text-sm text-gray-500 mb-1">Avg Duration</div>
				<div class="text-3xl font-bold text-purple-600">{formatDuration(Math.round(stats.average_duration_seconds))}</div>
			</div>
		</div>
	{/if}

	<!-- Filters and Actions -->
	<div class="bg-white rounded-lg shadow mb-6 p-6">
		<div class="flex flex-wrap items-center gap-4">
			<div class="flex-1">
				<select
					bind:value={selectedStatus}
					onchange={loadVoicemails}
					class="w-full md:w-auto px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
				>
					<option value="">All Messages</option>
					<option value="new">New</option>
					<option value="heard">Heard</option>
					<option value="saved">Saved</option>
					<option value="archived">Archived</option>
				</select>
			</div>

			{#if selectedVoicemails.size > 0}
				<div class="flex gap-2">
					<button
						onclick={() => bulkMarkAs('heard')}
						class="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
					>
						Mark as Heard
					</button>
					<button
						onclick={() => bulkMarkAs('saved')}
						class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
					>
						Save
					</button>
					<button
						onclick={() => bulkMarkAs('archived')}
						class="px-4 py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 transition-colors"
					>
						Archive
					</button>
				</div>
			{/if}

			<button
				onclick={loadVoicemails}
				class="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
			>
				Refresh
			</button>
		</div>
	</div>

	<!-- Voicemails List -->
	<div class="bg-white rounded-lg shadow overflow-hidden">
		{#if loading}
			<div class="p-8 text-center text-gray-500">
				<div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
				Loading voicemails...
			</div>
		{:else if error}
			<div class="p-8 text-center text-red-600">
				<p class="text-lg font-semibold mb-2">Error</p>
				<p>{error}</p>
			</div>
		{:else if voicemails.length === 0}
			<div class="p-8 text-center text-gray-500">
				<p class="text-lg mb-2">No voicemails</p>
				<p class="text-sm">Your voicemail inbox is empty</p>
			</div>
		{:else}
			<div class="overflow-x-auto">
				<table class="min-w-full divide-y divide-gray-200">
					<thead class="bg-gray-50">
						<tr>
							<th class="px-6 py-3 text-left">
								<input
									type="checkbox"
									checked={selectedVoicemails.size === voicemails.length}
									onchange={selectAll}
									class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
								/>
							</th>
							<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">From</th>
							<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
							<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Duration</th>
							<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Received</th>
							<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
						</tr>
					</thead>
					<tbody class="bg-white divide-y divide-gray-200">
						{#each voicemails as voicemail}
							<tr class="hover:bg-gray-50 {voicemail.status === 'new' ? 'bg-blue-50' : ''}">
								<td class="px-6 py-4 whitespace-nowrap">
									<input
										type="checkbox"
										checked={selectedVoicemails.has(voicemail.id)}
										onchange={() => toggleSelection(voicemail.id)}
										class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
									/>
								</td>
								<td class="px-6 py-4 whitespace-nowrap">
									<div class="flex items-center">
										{#if voicemail.priority === 1}
											<span class="mr-2">{priorityIcons[1]}</span>
										{/if}
										<div>
											<div class="text-sm font-medium text-gray-900">
												{voicemail.caller_name || 'Unknown'}
											</div>
											<div class="text-sm text-gray-500">{voicemail.caller_phone}</div>
										</div>
									</div>
								</td>
								<td class="px-6 py-4 whitespace-nowrap">
									<span class="px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full {statusColors[voicemail.status] || 'bg-gray-100 text-gray-800'}">
										{voicemail.status}
									</span>
									{#if voicemail.has_transcription}
										<span class="ml-2" title="Has transcript">📝</span>
									{/if}
								</td>
								<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
									{formatDuration(voicemail.recording_duration_seconds)}
								</td>
								<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
									{formatDate(voicemail.created_at)}
								</td>
								<td class="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2">
									<button
										onclick={() => playVoicemail(voicemail)}
										class="text-blue-600 hover:text-blue-900"
									>
										▶ Play
									</button>
									{#if voicemail.has_transcription}
										<button
											onclick={() => viewTranscript(voicemail)}
											class="text-green-600 hover:text-green-900"
										>
											Transcript
										</button>
									{/if}
									<button
										onclick={() => deleteVoicemail(voicemail.id)}
										class="text-red-600 hover:text-red-900"
									>
										Delete
									</button>
								</td>
							</tr>
						{/each}
					</tbody>
				</table>
			</div>
		{/if}
	</div>
</div>
