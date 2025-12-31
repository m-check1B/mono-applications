<script lang="ts">
  import Badge from '../shared/Badge.svelte';
  import Button from '../shared/Button.svelte';

  interface Props {
    call: {
      id: string;
      fromNumber: string;
      toNumber: string;
      status: string;
      startTime: string;
      agentId?: string;
      agent?: {
        firstName: string;
        lastName: string;
      };
    };
    onListen?: (callId: string) => void;
    onBarge?: (callId: string) => void;
    onWhisper?: (callId: string) => void;
  }

  let { call, onListen, onBarge, onWhisper }: Props = $props();

  function formatPhoneNumber(number: string) {
    return number.replace(/(\d{3})(\d{3})(\d{4})/, '($1) $2-$3');
  }

  function getCallDuration(startTime: string) {
    const start = new Date(startTime);
    const now = new Date();
    const diff = Math.floor((now.getTime() - start.getTime()) / 1000);
    const minutes = Math.floor(diff / 60);
    const seconds = diff % 60;
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
  }

  function getStatusVariant(status: string) {
    switch (status) {
      case 'IN_PROGRESS': return 'success';
      case 'RINGING': return 'warning';
      case 'ON_HOLD': return 'primary';
      default: return 'gray';
    }
  }
</script>

<div class="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700 p-4">
  <div class="flex items-start justify-between mb-3">
    <div class="flex-1">
      <div class="flex items-center space-x-2 mb-1">
        <span class="text-lg font-semibold text-gray-900 dark:text-white">
          {formatPhoneNumber(call.fromNumber)}
        </span>
        <Badge variant={getStatusVariant(call.status)}>{call.status}</Badge>
      </div>
      {#if call.agent}
        <p class="text-sm text-gray-600 dark:text-gray-400">
          Agent: {call.agent.firstName} {call.agent.lastName}
        </p>
      {/if}
      <p class="text-xs text-gray-500 dark:text-gray-500 mt-1">
        Duration: {getCallDuration(call.startTime)}
      </p>
    </div>
  </div>

  <div class="flex space-x-2">
    <Button size="sm" variant="secondary" onclick={() => onListen?.(call.id)}>
      🎧 Listen
    </Button>
    <Button size="sm" variant="primary" onclick={() => onWhisper?.(call.id)}>
      💬 Whisper
    </Button>
    <Button size="sm" variant="danger" onclick={() => onBarge?.(call.id)}>
      📞 Barge In
    </Button>
  </div>
</div>
