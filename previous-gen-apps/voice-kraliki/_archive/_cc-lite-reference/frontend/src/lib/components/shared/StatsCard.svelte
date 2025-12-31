<script lang="ts">
  import Sparkline from './Sparkline.svelte';

  interface Props {
    title: string;
    value: string | number;
    subtitle?: string;
    icon?: import('svelte').Snippet;
    trend?: any[];
    trendColor?: string;
  }

  let { title, value, subtitle, icon, trend, trendColor = '#3b82f6' }: Props = $props();
</script>

<div class="bg-white dark:bg-gray-800 rounded-xl shadow border border-gray-200 dark:border-gray-700 p-6 relative overflow-hidden">
  {#if trend && trend.length > 0}
    <div class="absolute inset-0 opacity-10 dark:opacity-5">
      <Sparkline data={trend} color={trendColor} height={80} />
    </div>
  {/if}

  <div class="flex items-center justify-between relative z-10">
    <div class="flex-1">
      <p class="text-sm font-medium text-gray-600 dark:text-gray-400">{title}</p>
      <p class="mt-2 text-3xl font-bold text-gray-900 dark:text-white">{value}</p>
      {#if subtitle}
        <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">{subtitle}</p>
      {/if}
    </div>
    {#if icon}
      <div class="flex-shrink-0 ml-4">
        {@render icon()}
      </div>
    {/if}
  </div>
</div>
