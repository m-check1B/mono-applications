<script lang="ts">
	import { onMount } from 'svelte';

	interface Recording {
		id: number;
		call_sid: string;
		agent_id: number | null;
		caller_phone: string | null;
		status: string;
		started_at: string;
		ended_at: string | null;
		duration_seconds: number | null;
		file_size_bytes: number | null;
		file_format: string;
		storage_provider: string;
		has_transcription: boolean;
		created_at: string;
	}

	interface RecordingStats {
		total_recordings: number;
		completed_recordings: number;
		total_duration_seconds: number;
		average_duration_seconds: number;
		total_storage_bytes: number;
		transcribed_count: number;
		transcription_rate: number;
	}

	let recordings: Recording[] = [];
	let stats: RecordingStats | null = null;
	let loading = true;
	let error = '';
	let selectedStatus = '';
	let selectedAgent: number | null = null;
	let searchQuery = '';

	const statusColors: Record<string, string> = {
		pending: 'bg-gray-100 text-gray-800',
		recording: 'bg-blue-100 text-blue-800',
		processing: 'bg-yellow-100 text-yellow-800',
		completed: 'bg-green-100 text-green-800',
		failed: 'bg-red-100 text-red-800',
		deleted: 'bg-gray-100 text-gray-600'
	};

	onMount(async () => {
		await loadRecordings();
		await loadStats();
	});

	async function loadRecordings() {
		try {
			const token = localStorage.getItem('token');
			const params = new URLSearchParams();

			if (selectedStatus) params.append('status', selectedStatus);
			if (selectedAgent) params.append('agent_id', selectedAgent.toString());

			const response = await fetch(`http://localhost:8000/api/recordings?${params}`, {
				headers: {
					'Authorization': `Bearer ${token}`,
					'Content-Type': 'application/json'
				}
			});

			if (!response.ok) throw new Error('Failed to load recordings');

			recordings = await response.json();
			loading = false;
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to load recordings';
			loading = false;
		}
	}

	async function loadStats() {
		try {
			const token = localStorage.getItem('token');

			const response = await fetch('http://localhost:8000/api/recordings/stats', {
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

	async function generateDownloadUrl(recordingId: number) {
		try {
			const token = localStorage.getItem('token');

			const response = await fetch(`http://localhost:8000/api/recordings/${recordingId}/download-url`, {
				method: 'POST',
				headers: {
					'Authorization': `Bearer ${token}`,
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({
					recording_id: recordingId,
					expires_in_seconds: 3600
				})
			});

			if (!response.ok) throw new Error('Failed to generate download URL');

			const data = await response.json();
			window.open(data.download_url, '_blank');
		} catch (e) {
			alert(e instanceof Error ? e.message : 'Failed to generate download URL');
		}
	}

	async function viewTranscript(recordingId: number) {
		try {
			const token = localStorage.getItem('token');

			const response = await fetch(`http://localhost:8000/api/recordings/${recordingId}/transcript`, {
				headers: {
					'Authorization': `Bearer ${token}`,
					'Content-Type': 'application/json'
				}
			});

			if (!response.ok) throw new Error('No transcript available');

			const transcript = await response.json();
			alert(`Transcript:\n\n${transcript.text || 'No text available'}`);
		} catch (e) {
			alert(e instanceof Error ? e.message : 'Failed to load transcript');
		}
	}

	function formatDuration(seconds: number | null): string {
		if (!seconds) return 'N/A';
		const mins = Math.floor(seconds / 60);
		const secs = seconds % 60;
		return `${mins}:${secs.toString().padStart(2, '0')}`;
	}

	function formatFileSize(bytes: number | null): string {
		if (!bytes) return 'N/A';
		const mb = bytes / (1024 * 1024);
		return `${mb.toFixed(2)} MB`;
	}

	function formatDate(dateString: string): string {
		const date = new Date(dateString);
		return date.toLocaleString();
	}
</script>

<div class="container mx-auto px-4 py-8">
	<div class="mb-8">
		<h1 class="text-3xl font-bold text-gray-900 mb-2">Call Recordings</h1>
		<p class="text-gray-600">Manage and review call recordings</p>
	</div>

	<!-- Statistics Cards -->
	{#if stats}
		<div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
			<div class="bg-white rounded-lg shadow p-6">
				<div class="text-sm text-gray-500 mb-1">Total Recordings</div>
				<div class="text-3xl font-bold text-gray-900">{stats.total_recordings}</div>
			</div>
			<div class="bg-white rounded-lg shadow p-6">
				<div class="text-sm text-gray-500 mb-1">Completed</div>
				<div class="text-3xl font-bold text-green-600">{stats.completed_recordings}</div>
			</div>
			<div class="bg-white rounded-lg shadow p-6">
				<div class="text-sm text-gray-500 mb-1">Avg Duration</div>
				<div class="text-3xl font-bold text-blue-600">{formatDuration(Math.round(stats.average_duration_seconds))}</div>
			</div>
			<div class="bg-white rounded-lg shadow p-6">
				<div class="text-sm text-gray-500 mb-1">Storage Used</div>
				<div class="text-3xl font-bold text-purple-600">{formatFileSize(stats.total_storage_bytes)}</div>
			</div>
		</div>
	{/if}

	<!-- Filters -->
	<div class="bg-white rounded-lg shadow mb-6 p-6">
		<div class="grid grid-cols-1 md:grid-cols-3 gap-4">
			<div>
				<label class="block text-sm font-medium text-gray-700 mb-2">Status</label>
				<select
					bind:value={selectedStatus}
					onchange={loadRecordings}
					class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
				>
					<option value="">All Statuses</option>
					<option value="pending">Pending</option>
					<option value="recording">Recording</option>
					<option value="processing">Processing</option>
					<option value="completed">Completed</option>
					<option value="failed">Failed</option>
				</select>
			</div>

			<div>
				<label class="block text-sm font-medium text-gray-700 mb-2">Search</label>
				<input
					type="text"
					bind:value={searchQuery}
					placeholder="Search by call SID or phone..."
					class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
				/>
			</div>

			<div class="flex items-end">
				<button
					onclick={loadRecordings}
					class="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
				>
					Refresh
				</button>
			</div>
		</div>
	</div>

	<!-- Recordings Table -->
	<div class="bg-white rounded-lg shadow overflow-hidden">
		{#if loading}
			<div class="p-8 text-center text-gray-500">
				<div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
				Loading recordings...
			</div>
		{:else if error}
			<div class="p-8 text-center text-red-600">
				<p class="text-lg font-semibold mb-2">Error</p>
				<p>{error}</p>
			</div>
		{:else if recordings.length === 0}
			<div class="p-8 text-center text-gray-500">
				<p class="text-lg mb-2">No recordings found</p>
				<p class="text-sm">Recordings will appear here once calls are recorded</p>
			</div>
		{:else}
			<div class="overflow-x-auto">
				<table class="min-w-full divide-y divide-gray-200">
					<thead class="bg-gray-50">
						<tr>
							<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Call SID</th>
							<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Caller</th>
							<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
							<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Duration</th>
							<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Size</th>
							<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date</th>
							<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
						</tr>
					</thead>
					<tbody class="bg-white divide-y divide-gray-200">
						{#each recordings as recording}
							<tr class="hover:bg-gray-50">
								<td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
									{recording.call_sid}
								</td>
								<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
									{recording.caller_phone || 'Unknown'}
								</td>
								<td class="px-6 py-4 whitespace-nowrap">
									<span class="px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full {statusColors[recording.status] || 'bg-gray-100 text-gray-800'}">
										{recording.status}
									</span>
								</td>
								<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
									{formatDuration(recording.duration_seconds)}
								</td>
								<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
									{formatFileSize(recording.file_size_bytes)}
								</td>
								<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
									{formatDate(recording.started_at)}
								</td>
								<td class="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2">
									{#if recording.status === 'completed'}
										<button
											onclick={() => generateDownloadUrl(recording.id)}
											class="text-blue-600 hover:text-blue-900"
										>
											Download
										</button>
										{#if recording.has_transcription}
											<button
												onclick={() => viewTranscript(recording.id)}
												class="text-green-600 hover:text-green-900"
											>
												Transcript
											</button>
										{/if}
									{/if}
								</td>
							</tr>
						{/each}
					</tbody>
				</table>
			</div>
		{/if}
	</div>
</div>
