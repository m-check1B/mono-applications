<script lang="ts">
  import Card from '../shared/Card.svelte';
  import Badge from '../shared/Badge.svelte';
  import Button from '../shared/Button.svelte';

  type LiveCall = {
    id: string;
    agentName: string;
    agentId: string;
    customerName: string;
    customerPhone: string;
    duration: number;
    sentiment: 'positive' | 'neutral' | 'negative';
    status: 'active' | 'on-hold';
  };

  let { calls = [] }: { calls?: LiveCall[] } = $props();

  const formatDuration = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const getSentimentColor = (sentiment: string) => {
    switch (sentiment) {
      case 'positive': return 'success';
      case 'negative': return 'danger';
      default: return 'gray';
    }
  };

  const handleListen = (callId: string) => {
    console.log('Listen to call', callId);
    // TODO: tRPC mutation to join call in listen mode
  };

  const handleWhisper = (callId: string) => {
    console.log('Whisper to agent', callId);
    // TODO: tRPC mutation to enable whisper mode
  };

  const handleBarge = (callId: string) => {
    console.log('Barge into call', callId);
    // TODO: tRPC mutation to join call fully
  };
</script>

<Card>
  {#snippet header()}
    <div class="flex items-center justify-between">
      <h2 class="text-lg font-semibold text-gray-900 dark:text-white">Live Calls</h2>
      <Badge variant="success">{calls.length} active</Badge>
    </div>
  {/snippet}

  {#if calls.length > 0}
    <div class="grid grid-cols-1 xl:grid-cols-2 gap-4">
      {#each calls as call (call.id)}
        <div class="border border-gray-200 dark:border-gray-700 rounded-lg p-4 hover:shadow-md transition-shadow">
          <!-- Header -->
          <div class="flex items-center justify-between mb-3">
            <div>
              <div class="text-sm font-medium text-gray-900 dark:text-white">{call.agentName}</div>
              <div class="text-xs text-gray-600 dark:text-gray-400">Agent ID: {call.agentId}</div>
            </div>
            <Badge variant={call.status === 'active' ? 'success' : 'warning'}>
              {call.status === 'active' ? 'ACTIVE' : 'ON HOLD'}
            </Badge>
          </div>

          <!-- Customer Info -->
          <div class="bg-gray-50 dark:bg-gray-700/50 rounded p-3 mb-3">
            <div class="flex items-center justify-between mb-2">
              <span class="text-sm font-medium text-gray-700 dark:text-gray-300">Customer</span>
              <Badge variant={getSentimentColor(call.sentiment)}>
                {call.sentiment === 'positive' ? '😊' : call.sentiment === 'negative' ? '😞' : '😐'}
              </Badge>
            </div>
            <div class="text-sm font-semibold text-gray-900 dark:text-white">{call.customerName}</div>
            <div class="text-xs text-gray-600 dark:text-gray-400">{call.customerPhone}</div>
          </div>

          <!-- Duration & Actions -->
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-2">
              <svg class="w-4 h-4 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
              </svg>
              <span class="text-sm font-mono font-semibold text-gray-900 dark:text-white">
                {formatDuration(call.duration)}
              </span>
            </div>

            <div class="flex gap-1">
              <Button
                variant="secondary"
                size="sm"
                onclick={() => handleListen(call.id)}
                title="Listen to call"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M5.586 15.536a5 5 0 001.414 1.414m2.828-9.9a9 9 0 000 12.728"></path>
                </svg>
              </Button>

              <Button
                variant="secondary"
                size="sm"
                onclick={() => handleWhisper(call.id)}
                title="Whisper to agent"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"></path>
                </svg>
              </Button>

              <Button
                variant="primary"
                size="sm"
                onclick={() => handleBarge(call.id)}
                title="Join call"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8h2a2 2 0 012 2v6a2 2 0 01-2 2h-2v4l-4-4H9a1.994 1.994 0 01-1.414-.586m0 0L11 14h4a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2v4l.586-.586z"></path>
                </svg>
              </Button>
            </div>
          </div>
        </div>
      {/each}
    </div>
  {:else}
    <div class="text-center py-12">
      <svg class="w-20 h-20 mx-auto text-gray-300 dark:text-gray-600 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"></path>
      </svg>
      <p class="text-gray-600 dark:text-gray-400">No active calls</p>
      <p class="text-sm text-gray-500 dark:text-gray-500 mt-2">Calls will appear here when agents are on calls</p>
    </div>
  {/if}
</Card>
