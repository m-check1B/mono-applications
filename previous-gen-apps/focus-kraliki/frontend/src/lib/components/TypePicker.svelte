<script lang="ts">
  import { knowledgeStore } from '$lib/stores/knowledge';
  import { onMount } from 'svelte';

  interface Props {
    label?: string;
    selectedId?: string | null;
    onSelect?: (typeId: string) => void;
  }

  let {
    label = 'Choose type',
    selectedId = null,
    onSelect = () => {}
  }: Props = $props();

  onMount(() => {
    // Load types if not present
    if ($knowledgeStore.itemTypes.length === 0) {
      knowledgeStore.loadItemTypes();
    }
  });

  let itemTypes = $derived($knowledgeStore.itemTypes);
</script>

<div class="space-y-2">
  <p class="text-xs font-bold uppercase text-muted-foreground">{label}</p>
  <div class="flex flex-wrap gap-2">
    {#each itemTypes as type}
      <button
        class="px-3 py-1 border-2 border-black dark:border-white text-xs font-bold uppercase transition-colors
        {selectedId === type.id ? 'bg-black text-white dark:bg-white dark:text-black' : 'bg-background hover:bg-secondary'}"
        onclick={() => onSelect(type.id)}
      >
        {type.name}
      </button>
    {/each}
  </div>
  {#if itemTypes.length === 0}
    <p class="text-xs text-muted-foreground">Loading types…</p>
  {/if}
</div>
