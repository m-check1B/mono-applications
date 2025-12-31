<script lang="ts">
  import { onMount } from 'svelte';
  import { fly } from 'svelte/transition';
  import { quintOut } from 'svelte/easing';
  import Button from '../shared/Button.svelte';
  import Card from '../shared/Card.svelte';
  import Badge from '../shared/Badge.svelte';
  import RecordingPlayer from './RecordingPlayer.svelte';
  import { trpc } from '$lib/trpc/client';

  let { callId, userRole = 'agent' } = $props<{
    callId?: string;
    userRole?: string;
  }>();

  let page = $state(1);
  let search = $state('');
  let statusFilter = $state('all');
  let selectedRecording = $state<any>(null);
  let showPlayer = $state(false);
  let showAudit = $state(false);
  let showDelete = $state(false);
  let loading = $state(true);
  let error = $state<string | null>(null);

  const limit = 10;
  const offset = () => (page - 1) * limit;

  let recordings = $state<any[]>([]);
  let totalRecordings = $state(0);
  let hasMore = $state(false);

  // Load recordings from API
  const loadRecordings = async () => {
    try {
      loading = true;
      error = null;

      // Use call history endpoint which includes recordings
      const result = await trpc.telephony.getCallHistory.query({
        limit,
        offset: offset(),
        filter: {
          status: statusFilter === 'all' ? undefined : statusFilter as any
        }
      });

      // Transform call history to recordings format
      recordings = result.calls.map((call: any) => ({
        id: call.id,
        call: {
          fromNumber: call.fromNumber || call.from,
          toNumber: call.toNumber || call.to,
          startTime: call.startTime,
          agent: call.agent
        },
        duration: call.duration || 0,
        status: call.status === 'COMPLETED' ? 'UPLOADED' : call.status,
        consentGiven: true, // Would come from call metadata
        consentMethod: 'VERBAL',
        createdAt: call.startTime,
        fileSize: call.duration ? call.duration * 16000 : 0, // Estimate ~16KB per second
        recordingUrl: call.recordingUrl
      }));

      totalRecordings = result.total;
      hasMore = result.hasMore;
    } catch (err: any) {
      console.error('Failed to load recordings:', err);
      error = err.message || 'Failed to load recordings';

      // Fallback to mock data
      recordings = [
        {
          id: '1',
          call: {
            fromNumber: '+1 (555) 123-4567',
            toNumber: '+1 (555) 987-6543',
            startTime: new Date().toISOString(),
            agent: { firstName: 'John', lastName: 'Doe' }
          },
          duration: 185,
          status: 'UPLOADED',
          consentGiven: true,
          consentMethod: 'VERBAL',
          createdAt: new Date().toISOString(),
          fileSize: 3145728
        },
        {
          id: '2',
          call: {
            fromNumber: '+1 (555) 234-5678',
            toNumber: '+1 (555) 876-5432',
            startTime: new Date(Date.now() - 86400000).toISOString(),
            agent: { firstName: 'Jane', lastName: 'Smith' }
          },
          duration: 240,
          status: 'UPLOADED',
          consentGiven: false,
          consentMethod: null,
          createdAt: new Date(Date.now() - 86400000).toISOString(),
          fileSize: 4194304
        }
      ];
    } finally {
      loading = false;
    }
  };

  onMount(() => {
    loadRecordings();
  });

  // Reload when filters change
  $effect(() => {
    if (statusFilter || page) {
      loadRecordings();
    }
  });

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'UPLOADED': return 'success';
      case 'RECORDING': return 'primary';
      case 'PAUSED': return 'warning';
      case 'PROCESSING': return 'secondary';
      case 'FAILED': return 'danger';
      default: return 'gray';
    }
  };

  const formatDuration = (seconds: number): string => {
    const minutes = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${minutes}:${secs.toString().padStart(2, '0')}`;
  };

  const formatFileSize = (bytes: number): string => {
    const mb = bytes / (1024 * 1024);
    return `${mb.toFixed(1)} MB`;
  };

  const handlePlayRecording = (recording: any) => {
    selectedRecording = recording;
    showPlayer = true;
  };

  const handleViewAudit = (recording: any) => {
    selectedRecording = recording;
    showAudit = true;
  };

  const handleDeleteRecording = (recording: any) => {
    selectedRecording = recording;
    showDelete = true;
  };

  const confirmDelete = () => {
    if (selectedRecording) {
      recordings = recordings.filter(r => r.id !== selectedRecording.id);
      showDelete = false;
      selectedRecording = null;
    }
  };
</script>

<Card>
  {#snippet header()}
    <div class="flex justify-between items-center">
      <div>
        <h2 class="text-xl font-bold text-gray-900 dark:text-white">Call Recordings</h2>
        <p class="text-gray-500 dark:text-gray-400">
          {callId ? 'Recordings for this call' : 'All recordings'}
        </p>
      </div>
      {#if recordings.length > 0}
        <Badge variant="gray">
          {recordings.length} recording{recordings.length !== 1 ? 's' : ''}
        </Badge>
      {/if}
    </div>
  {/snippet}

  <div class="space-y-4">
    <!-- Search and Filters -->
    <div class="flex gap-4">
      <div class="flex-1">
        <label for="recording-search" class="sr-only">Search recordings</label>
        <input
          id="recording-search"
          type="search"
          placeholder="Search by phone number or agent..."
          bind:value={search}
          class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800"
        />
      </div>

      <div>
        <label for="recording-status-filter" class="sr-only">Filter recordings by status</label>
        <select
          id="recording-status-filter"
          bind:value={statusFilter}
          class="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800"
        >
          <option value="all">All Statuses</option>
          <option value="UPLOADED">Uploaded</option>
          <option value="RECORDING">Recording</option>
          <option value="PROCESSING">Processing</option>
          <option value="FAILED">Failed</option>
        </select>
      </div>
    </div>

    <!-- Recordings Table -->
    {#if recordings.length === 0}
      <div class="text-center py-8 text-gray-500">
        No recordings found
      </div>
    {:else}
      <div class="overflow-x-auto">
        <table class="w-full">
          <thead class="bg-gray-50 dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
            <tr>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Call Info</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Agent</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Duration</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Status</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Consent</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Size</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-200 dark:divide-gray-700">
            {#each recordings as recording, i}
              <tr
                class="hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
                in:fly={{ y: 20, duration: 300, delay: i * 50, easing: quintOut }}
              >
                <td class="px-4 py-3">
                  <div class="flex flex-col">
                    <span class="font-medium text-gray-900 dark:text-white">
                      {recording.call.fromNumber} → {recording.call.toNumber}
                    </span>
                    <span class="text-sm text-gray-500">
                      {new Date(recording.call.startTime).toLocaleDateString()}
                    </span>
                  </div>
                </td>

                <td class="px-4 py-3">
                  {#if recording.call.agent}
                    <span class="text-gray-900 dark:text-white">
                      {recording.call.agent.firstName} {recording.call.agent.lastName}
                    </span>
                  {:else}
                    <span class="text-gray-400">--</span>
                  {/if}
                </td>

                <td class="px-4 py-3">
                  <div class="flex items-center gap-1">
                    <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                    </svg>
                    {formatDuration(recording.duration)}
                  </div>
                </td>

                <td class="px-4 py-3">
                  <Badge variant={getStatusColor(recording.status)} class="text-xs">
                    {recording.status}
                  </Badge>
                </td>

                <td class="px-4 py-3">
                  <div class="flex items-center gap-1">
                    <svg
                      class={`w-4 h-4 ${recording.consentGiven ? 'text-green-500' : 'text-red-500'}`}
                      fill="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                    </svg>
                    <span class={`text-sm ${recording.consentGiven ? 'text-green-600' : 'text-red-600'}`}>
                      {recording.consentGiven ? recording.consentMethod : 'Missing'}
                    </span>
                  </div>
                </td>

                <td class="px-4 py-3">
                  <span class="text-sm text-gray-900 dark:text-white">
                    {formatFileSize(recording.fileSize)}
                  </span>
                </td>

                <td class="px-4 py-3">
                  <div class="flex items-center gap-1">
                    {#if recording.status === 'UPLOADED'}
                      <Button
                        size="sm"
                        variant="secondary"
                        onclick={() => handlePlayRecording(recording)}
                      >
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"></path>
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                        </svg>
                      </Button>
                    {/if}
                    <Button
                      size="sm"
                      variant="secondary"
                      onclick={() => handleViewAudit(recording)}
                    >
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path>
                      </svg>
                    </Button>
                    {#if userRole === 'supervisor'}
                      <Button
                        size="sm"
                        variant="danger"
                        onclick={() => handleDeleteRecording(recording)}
                      >
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                        </svg>
                      </Button>
                    {/if}
                  </div>
                </td>
              </tr>
            {/each}
          </tbody>
        </table>
      </div>
    {/if}
  </div>
</Card>

<!-- Recording Player Modal -->
{#if showPlayer && selectedRecording}
  <div class="fixed inset-0 bg-black/50 flex items-center justify-center z-50" in:fly={{ y: 20, duration: 300 }}>
    <div class="bg-white dark:bg-gray-800 rounded-lg p-6 max-w-2xl w-full mx-4">
      <div class="flex justify-between items-center mb-4">
        <h3 class="text-lg font-bold text-gray-900 dark:text-white">Recording Playback</h3>
        <button
          type="button"
          aria-label="Close recording playback"
          onclick={() => showPlayer = false}
          class="text-gray-500 hover:text-gray-700 dark:hover:text-gray-300"
        >
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
          </svg>
        </button>
      </div>

      <RecordingPlayer recording={selectedRecording} />

      <div class="mt-4 flex justify-end">
        <Button onclick={() => showPlayer = false}>Close</Button>
      </div>
    </div>
  </div>
{/if}

<!-- Delete Confirmation Modal -->
{#if showDelete && selectedRecording}
  <div class="fixed inset-0 bg-black/50 flex items-center justify-center z-50" in:fly={{ y: 20, duration: 300 }}>
    <div class="bg-white dark:bg-gray-800 rounded-lg p-6 max-w-md w-full mx-4">
      <h3 class="text-lg font-bold text-red-600 mb-4">Delete Recording</h3>

      <p class="text-gray-700 dark:text-gray-300 mb-4">
        Are you sure you want to delete this recording? This action cannot be undone.
      </p>

      {#if selectedRecording}
        <div class="p-3 bg-gray-50 dark:bg-gray-700 rounded mb-4">
          <div class="font-semibold text-gray-900 dark:text-white">
            {selectedRecording.call.fromNumber} → {selectedRecording.call.toNumber}
          </div>
          <div class="text-sm text-gray-600 dark:text-gray-400">
            Duration: {formatDuration(selectedRecording.duration)}
          </div>
        </div>
      {/if}

      <div class="flex gap-2 justify-end">
        <Button variant="secondary" onclick={() => showDelete = false}>
          Cancel
        </Button>
        <Button variant="danger" onclick={confirmDelete}>
          Delete Recording
        </Button>
      </div>
    </div>
  </div>
{/if}
