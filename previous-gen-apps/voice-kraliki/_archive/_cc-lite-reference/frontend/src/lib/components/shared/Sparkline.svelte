<script lang="ts">
  import { onMount } from 'svelte';
  import { createChart } from 'lightweight-charts';

  let { data = [], color = '#3b82f6', height = 40 } = $props();

  let chartContainer: HTMLDivElement;
  let chart: ReturnType<typeof createChart> | null = null;
  let series: any = null;

  onMount(() => {
    if (!chartContainer || !data.length) return;

    // Create chart with minimal styling
    chart = createChart(chartContainer, {
      width: chartContainer.clientWidth,
      height,
      layout: {
        background: { color: 'transparent' },
        textColor: 'transparent',
      },
      grid: {
        vertLines: { visible: false },
        horzLines: { visible: false },
      },
      leftPriceScale: { visible: false },
      rightPriceScale: { visible: false },
      timeScale: {
        visible: false,
        borderVisible: false,
      },
      crosshair: {
        vertLine: { visible: false },
        horzLine: { visible: false },
      },
      handleScroll: false,
      handleScale: false,
    });

    // Add area series
    series = (chart as any).addAreaSeries({
      lineColor: color,
      topColor: `${color}40`,
      bottomColor: `${color}00`,
      lineWidth: 2,
      priceLineVisible: false,
      lastValueVisible: false,
    });

    series.setData(data);

    // Fit content
    chart.timeScale().fitContent();

    // Handle resize
    const resizeObserver = new ResizeObserver(() => {
      if (chart && chartContainer) {
        chart.resize(chartContainer.clientWidth, height);
      }
    });

    resizeObserver.observe(chartContainer);

    return () => {
      resizeObserver.disconnect();
      chart?.remove();
    };
  });

  // Update data when it changes
  $effect(() => {
    if (series && data.length) {
      series.setData(data);
      chart?.timeScale().fitContent();
    }
  });
</script>

<div bind:this={chartContainer} class="w-full" style="height: {height}px;"></div>
