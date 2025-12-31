<script lang="ts">
  import Card from '../shared/Card.svelte';
  import Badge from '../shared/Badge.svelte';
  import { onMount } from 'svelte';

  type TranscriptEntry = {
    id: string;
    speaker: 'agent' | 'customer';
    text: string;
    timestamp: Date;
    sentiment?: 'positive' | 'neutral' | 'negative';
  };

  let { entries = [] }: { entries?: TranscriptEntry[] } = $props();

  let scrollContainer: HTMLDivElement;

  const formatTime = (date: Date): string => {
    return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
  };

  const getSentimentEmoji = (sentiment?: string) => {
    switch (sentiment) {
      case 'positive': return '😊';
      case 'negative': return '😞';
      case 'neutral': return '😐';
      default: return '';
    }
  };

  // Auto-scroll to bottom when new entries arrive
  $effect(() => {
    if (scrollContainer && entries.length > 0) {
      scrollContainer.scrollTop = scrollContainer.scrollHeight;
    }
  });
</script>

<Card>
  {#snippet header()}
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-2">
        <svg class="w-5 h-5 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z"></path>
        </svg>
        <h2 class="text-lg font-semibold text-gray-900 dark:text-white">Live Transcription</h2>
      </div>
      <Badge variant="success" class="animate-pulse">RECORDING</Badge>
    </div>
  {/snippet}

  <div
    bind:this={scrollContainer}
    class="space-y-3 max-h-96 overflow-y-auto pr-2 custom-scrollbar"
  >
    {#if entries.length > 0}
      {#each entries as entry (entry.id)}
        <div class={`flex ${entry.speaker === 'agent' ? 'justify-end' : 'justify-start'}`}>
          <div class={`max-w-[80%] rounded-lg p-3 ${
            entry.speaker === 'agent'
              ? 'bg-primary-100 dark:bg-primary-900/30 text-gray-900 dark:text-white'
              : 'bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-white'
          }`}>
            <div class="flex items-center gap-2 mb-1">
              <span class="text-xs font-semibold uppercase tracking-wide">
                {entry.speaker === 'agent' ? 'You' : 'Customer'}
              </span>
              {#if entry.sentiment}
                <span class="text-xs">{getSentimentEmoji(entry.sentiment)}</span>
              {/if}
              <span class="text-xs text-gray-500 dark:text-gray-400 ml-auto">
                {formatTime(entry.timestamp)}
              </span>
            </div>
            <p class="text-sm">{entry.text}</p>
          </div>
        </div>
      {/each}
    {:else}
      <div class="text-center py-12">
        <svg class="w-16 h-16 mx-auto text-gray-300 dark:text-gray-600 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"></path>
        </svg>
        <p class="text-gray-600 dark:text-gray-400">Transcription will appear here</p>
        <p class="text-sm text-gray-500 dark:text-gray-500 mt-1">Real-time speech-to-text</p>
      </div>
    {/if}
  </div>
</Card>

<style>
  .custom-scrollbar::-webkit-scrollbar {
    width: 8px;
  }

  .custom-scrollbar::-webkit-scrollbar-track {
    background: rgb(243 244 246 / 1);
    border-radius: 4px;
  }

  .dark .custom-scrollbar::-webkit-scrollbar-track {
    background: rgb(55 65 81 / 1);
  }

  .custom-scrollbar::-webkit-scrollbar-thumb {
    background: rgb(209 213 219 / 1);
    border-radius: 4px;
  }

  .dark .custom-scrollbar::-webkit-scrollbar-thumb {
    background: rgb(107 114 128 / 1);
  }

  .custom-scrollbar::-webkit-scrollbar-thumb:hover {
    background: rgb(156 163 175 / 1);
  }

  .dark .custom-scrollbar::-webkit-scrollbar-thumb:hover {
    background: rgb(75 85 99 / 1);
  }
</style>
