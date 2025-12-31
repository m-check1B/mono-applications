<script lang="ts">
	import '../app.css';
	import { onMount, setContext } from 'svelte';
	import { QueryClientProvider } from '@tanstack/svelte-query';
	import { queryClient, themeStore } from '$lib/stores';
	import type { LayoutData } from './$types';
	import { APP_CONFIG_KEY, type AppConfig } from '$lib/config/app';
	import ErrorBoundary from '$lib/components/ErrorBoundary.svelte';
	import { initAnalytics } from '$lib/analytics';

	const { children, data } = $props<{ children: () => unknown; data: LayoutData }>();

	const config = data.config satisfies AppConfig;
	setContext(APP_CONFIG_KEY, config);

	onMount(() => {
		// Initialize privacy-first analytics (Plausible)
		const cleanupAnalytics = initAnalytics();

		themeStore.init();

		return cleanupAnalytics;
	});
</script>

<QueryClientProvider client={queryClient}>
	<div class="min-h-screen bg-background bg-grid-pattern text-foreground font-mono">
		<div class="scanline"></div>
		<ErrorBoundary>
			{@render children()}
		</ErrorBoundary>
	</div>
</QueryClientProvider>
