<script lang="ts">
  interface Props {
    current: number;
    total: number;
    label?: string;
  }

  let { current, total, label = '' }: Props = $props();

  const percent = $derived(Math.round((current / total) * 100));
</script>

<div class="mt-8 pt-6 border-t-2 border-gray-200">
  {#if label}
    <div class="text-sm font-bold text-gray-500 mb-2">{label}</div>
  {/if}
  <div class="progress-bar">
    <div class="progress-bar-fill" style="width: {percent}%"></div>
  </div>
  <div class="text-sm text-gray-500 mt-1">
    {current} / {total} lessons ({percent}%)
  </div>
</div>
