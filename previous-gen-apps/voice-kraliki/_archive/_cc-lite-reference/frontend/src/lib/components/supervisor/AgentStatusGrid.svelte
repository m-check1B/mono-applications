<script lang="ts">
  import Card from '../shared/Card.svelte';
  import Badge from '../shared/Badge.svelte';

  type Agent = {
    id: string;
    name: string;
    email: string;
    status: 'available' | 'on-call' | 'break' | 'offline';
    currentCall?: {
      customerName: string;
      duration: number;
    };
    stats: {
      callsToday: number;
      avgDuration: number;
      satisfaction: number;
    };
  };

  let { agents = [] }: { agents?: Agent[] } = $props();

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'available': return 'success';
      case 'on-call': return 'primary';
      case 'break': return 'warning';
      case 'offline': return 'gray';
      default: return 'gray';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'available': return '🟢';
      case 'on-call': return '📞';
      case 'break': return '☕';
      case 'offline': return '⚫';
      default: return '⚪';
    }
  };

  const formatDuration = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    return `${mins}:${(seconds % 60).toString().padStart(2, '0')}`;
  };
</script>

<Card>
  {#snippet header()}
    <h2 class="text-lg font-semibold text-gray-900 dark:text-white">Team Status</h2>
  {/snippet}

  {#if agents.length > 0}
    <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
      {#each agents as agent (agent.id)}
        <div class="border border-gray-200 dark:border-gray-700 rounded-lg p-4 hover:shadow-md transition-shadow">
          <!-- Agent Header -->
          <div class="flex items-start justify-between mb-3">
            <div class="flex-1">
              <div class="font-semibold text-gray-900 dark:text-white">{agent.name}</div>
              <div class="text-xs text-gray-600 dark:text-gray-400">{agent.email}</div>
            </div>
            <Badge variant={getStatusColor(agent.status)}>
              {getStatusIcon(agent.status)} {agent.status.toUpperCase()}
            </Badge>
          </div>

          <!-- Current Call (if on call) -->
          {#if agent.currentCall}
            <div class="bg-primary-50 dark:bg-primary-900/20 rounded p-2 mb-3">
              <div class="flex items-center justify-between">
                <div class="text-xs text-gray-700 dark:text-gray-300">
                  <div class="font-medium">{agent.currentCall.customerName}</div>
                </div>
                <div class="text-xs font-mono font-semibold text-primary-600 dark:text-primary-400">
                  {formatDuration(agent.currentCall.duration)}
                </div>
              </div>
            </div>
          {/if}

          <!-- Stats -->
          <div class="grid grid-cols-3 gap-2">
            <div class="text-center">
              <div class="text-lg font-bold text-gray-900 dark:text-white">{agent.stats.callsToday}</div>
              <div class="text-xs text-gray-600 dark:text-gray-400">Calls</div>
            </div>
            <div class="text-center">
              <div class="text-lg font-bold text-gray-900 dark:text-white">{formatDuration(agent.stats.avgDuration)}</div>
              <div class="text-xs text-gray-600 dark:text-gray-400">Avg</div>
            </div>
            <div class="text-center">
              <div class="text-lg font-bold text-gray-900 dark:text-white">{agent.stats.satisfaction}%</div>
              <div class="text-xs text-gray-600 dark:text-gray-400">CSAT</div>
            </div>
          </div>
        </div>
      {/each}
    </div>
  {:else}
    <div class="text-center py-12">
      <svg class="w-20 h-20 mx-auto text-gray-300 dark:text-gray-600 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"></path>
      </svg>
      <p class="text-gray-600 dark:text-gray-400">No agents found</p>
      <p class="text-sm text-gray-500 dark:text-gray-500 mt-2">Agent status will appear here</p>
    </div>
  {/if}
</Card>
