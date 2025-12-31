<script lang="ts">
  import MobileCard from './MobileCard.svelte';
  import FloatingActionButton from './FloatingActionButton.svelte';

  type QueuedCall = {
    id: string;
    customer: string;
    phone: string;
    wait_time: string;
    status: string;
    priority?: 'high' | 'normal' | 'low';
  };

  let { calls = [] }: { calls?: QueuedCall[] } = $props();

  const handleCallClick = (callId: string) => {
    console.log('Call clicked:', callId);
    // TODO: Navigate to call detail or trigger action
  };

  const handleNewCall = () => {
    console.log('New call FAB clicked');
    // TODO: Navigate to new call form
  };

  const getStatusBadgeColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'waiting':
        return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400';
      case 'active':
        return 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400';
      case 'priority':
        return 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400';
      default:
        return 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400';
    }
  };
</script>

<!-- Mobile-first card layout (no tables) -->
<div class="call-queue-mobile space-y-3 pb-20">
  {#if calls.length > 0}
    {#each calls as call (call.id)}
      <MobileCard
        onclick={() => handleCallClick(call.id)}
        variant={call.priority === 'high' ? 'highlighted' : 'default'}
        padding="md"
      >
        <div class="flex justify-between items-start">
          <div class="flex-1">
            <h3 class="font-semibold text-base text-gray-900 dark:text-white">
              {call.customer}
            </h3>
            <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">
              {call.phone}
            </p>
          </div>
          <div class="text-right">
            <span class="text-xs font-medium px-2 py-1 rounded {getStatusBadgeColor(call.status)}">
              {call.status}
            </span>
            <p class="text-xs text-gray-500 dark:text-gray-500 mt-1">
              ⏱️ {call.wait_time}
            </p>
          </div>
        </div>
      </MobileCard>
    {/each}
  {:else}
    <div class="flex flex-col items-center justify-center py-16 text-center">
      <div class="text-6xl mb-4">📞</div>
      <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-2">
        No Calls in Queue
      </h3>
      <p class="text-sm text-gray-600 dark:text-gray-400 max-w-xs">
        All caught up! New calls will appear here.
      </p>
    </div>
  {/if}
</div>

<!-- Floating Action Button (FAB) for new call -->
<FloatingActionButton
  icon="📞"
  label="New Call"
  onclick={handleNewCall}
  variant="primary"
  size="md"
  position="bottom-right"
/>

<style>
  /* Prevent text selection on mobile */
  .call-queue-mobile {
    user-select: none;
    -webkit-user-select: none;
  }

  /* Smooth scrolling */
  .call-queue-mobile {
    scroll-behavior: smooth;
  }

  /* Safe area for mobile devices */
  @supports (padding: env(safe-area-inset-bottom)) {
    .call-queue-mobile {
      padding-bottom: calc(5rem + env(safe-area-inset-bottom));
    }
  }
</style>
