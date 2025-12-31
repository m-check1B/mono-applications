<script lang="ts">
  interface Props {
    class?: string;
    header?: import('svelte').Snippet;
    children?: import('svelte').Snippet;
    footer?: import('svelte').Snippet;
  }

  let { class: className = '', header, children, footer }: Props = $props();
</script>

<div class="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700 {className}">
  {#if header}
    <div class="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
      {@render header()}
    </div>
  {/if}

  <div class="px-6 py-4">
    {@render children?.()}
  </div>

  {#if footer}
    <div class="px-6 py-4 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900">
      {@render footer()}
    </div>
  {/if}
</div>
