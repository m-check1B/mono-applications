<!--
Toast Stack: Enhanced Feedback & Visibility (Gap #12)
Supports undo/retry actions for better error recovery
-->
<script lang="ts">
  import { toast, type ToastMessage } from '$lib/stores/toast';
  import { X } from 'lucide-svelte';

  let toasts = $derived($toast);

  function getBg(type: ToastMessage['type']) {
    switch (type) {
      case 'success': return 'bg-green-500 text-white';
      case 'warning': return 'bg-amber-500 text-black';
      case 'error': return 'bg-red-600 text-white';
      default: return 'bg-black text-white';
    }
  }

  // Gap #12: Handle action button clicks
  async function handleAction(t: ToastMessage) {
    if (t.action?.onClick) {
      await t.action.onClick();
      toast.dismiss(t.id);
    }
  }
</script>

<div class="fixed right-4 top-4 z-[200] flex flex-col gap-3 max-w-sm">
  {#each toasts as t (t.id)}
    <div class={`flex items-start gap-3 p-3 brutal-border brutal-shadow ${getBg(t.type)} animate-in slide-in-from-right duration-200`}>
      <div class="flex-1 space-y-2">
        <div class="text-sm font-bold leading-snug uppercase tracking-wide">{t.message}</div>

        <!-- Gap #12: Action button (Undo/Retry) -->
        {#if t.action}
          <button
            type="button"
            onclick={() => handleAction(t)}
            class="text-[11px] font-black uppercase tracking-wider px-2 py-1 border-2 border-current hover:bg-white hover:text-black dark:hover:bg-black dark:hover:text-white transition-colors"
          >
            {t.action.label}
          </button>
        {/if}
      </div>

      <button
        type="button"
        class="p-1 border-2 border-current hover:bg-white hover:text-black dark:hover:bg-black dark:hover:text-white transition-colors flex-shrink-0"
        onclick={() => toast.dismiss(t.id)}
        aria-label="Dismiss"
      >
        <X class="w-4 h-4" />
      </button>
    </div>
  {/each}
</div>
