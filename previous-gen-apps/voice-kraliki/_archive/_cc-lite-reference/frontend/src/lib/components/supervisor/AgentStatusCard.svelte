<script lang="ts">
  import Badge from '../shared/Badge.svelte';

  interface Props {
    agent: {
      id: string;
      firstName: string;
      lastName: string;
      email: string;
      status: 'AVAILABLE' | 'BUSY' | 'BREAK' | 'OFFLINE';
      currentCallId?: string;
    };
  }

  let { agent }: Props = $props();

  function getStatusVariant(status: string) {
    switch (status) {
      case 'AVAILABLE': return 'success';
      case 'BUSY': return 'warning';
      case 'BREAK': return 'primary';
      case 'OFFLINE': return 'gray';
      default: return 'gray';
    }
  }

  function getStatusIcon(status: string) {
    switch (status) {
      case 'AVAILABLE': return '✅';
      case 'BUSY': return '📞';
      case 'BREAK': return '☕';
      case 'OFFLINE': return '⭕';
      default: return '•';
    }
  }
</script>

<div class="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700 p-4">
  <div class="flex items-center space-x-3">
    <div class="flex-shrink-0">
      <div class="w-12 h-12 rounded-full bg-primary-100 dark:bg-primary-900/30 flex items-center justify-center text-2xl">
        {getStatusIcon(agent.status)}
      </div>
    </div>
    <div class="flex-1 min-w-0">
      <p class="text-sm font-semibold text-gray-900 dark:text-white truncate">
        {agent.firstName} {agent.lastName}
      </p>
      <p class="text-xs text-gray-500 dark:text-gray-400 truncate">
        {agent.email}
      </p>
      <div class="mt-1">
        <Badge variant={getStatusVariant(agent.status)}>{agent.status}</Badge>
      </div>
    </div>
  </div>
</div>
