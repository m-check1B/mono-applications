<script lang="ts">
  import Card from '../shared/Card.svelte';
  import Badge from '../shared/Badge.svelte';
  import Button from '../shared/Button.svelte';

  type QueuedCall = {
    id: string;
    customerName: string;
    customerPhone: string;
    waitTime: number;
    priority: 'high' | 'normal' | 'low';
    campaignName?: string;
  };

  let { calls = [] }: { calls?: QueuedCall[] } = $props();

  const formatWaitTime = (seconds: number): string => {
    if (seconds < 60) return `${seconds}s`;
    const mins = Math.floor(seconds / 60);
    return `${mins}m ${seconds % 60}s`;
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'danger';
      case 'normal': return 'primary';
      case 'low': return 'gray';
      default: return 'gray';
    }
  };

  const handleAnswer = (callId: string) => {
    console.log('Answer call', callId);
    // TODO: Call tRPC mutation to accept call
  };
</script>

<Card>
  {#snippet header()}
    <div class="flex items-center justify-between">
      <h2 class="text-lg font-semibold text-gray-900 dark:text-white">Call Queue</h2>
      <Badge variant="primary">{calls.length} waiting</Badge>
    </div>
  {/snippet}

  {#if calls.length > 0}
    <div class="space-y-3">
      {#each calls as call (call.id)}
        <div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-4 hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors">
          <div class="flex items-center justify-between mb-2">
            <div>
              <div class="font-semibold text-gray-900 dark:text-white">{call.customerName}</div>
              <div class="text-sm text-gray-600 dark:text-gray-400">{call.customerPhone}</div>
            </div>
            <Badge variant={getPriorityColor(call.priority)}>
              {call.priority.toUpperCase()}
            </Badge>
          </div>

          <div class="flex items-center justify-between">
            <div class="flex items-center gap-4 text-sm text-gray-600 dark:text-gray-400">
              <div class="flex items-center gap-1">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
                <span>{formatWaitTime(call.waitTime)}</span>
              </div>
              {#if call.campaignName}
                <div class="flex items-center gap-1">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z"></path>
                  </svg>
                  <span>{call.campaignName}</span>
                </div>
              {/if}
            </div>

            <Button
              variant="success"
              size="sm"
              onclick={() => handleAnswer(call.id)}
            >
              <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"></path>
              </svg>
              Answer
            </Button>
          </div>
        </div>
      {/each}
    </div>
  {:else}
    <div class="text-center py-8">
      <svg class="w-16 h-16 mx-auto text-gray-300 dark:text-gray-600 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"></path>
      </svg>
      <p class="text-gray-600 dark:text-gray-400">Queue is empty</p>
      <p class="text-sm text-gray-500 dark:text-gray-500 mt-1">No calls waiting</p>
    </div>
  {/if}
</Card>
