<!--
Panel Redirect Component
Part of Gap #8: Route architecture fix
Redirects CRUD routes to main dashboard + opens panel
-->
<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { contextPanelStore, type PanelType } from '$lib/stores/contextPanel';

	interface Props {
		panel: PanelType;
		deepLink?: boolean; // If true, use query param instead of direct panel open
	}

	let { panel, deepLink = false }: Props = $props();

	onMount(() => {
		if (deepLink) {
			// Use query param for deep linking (better for sharing URLs)
			goto(`/dashboard?panel=${panel}`, { replaceState: true });
		} else {
			// Direct panel open + redirect
			contextPanelStore.open(panel);
			goto('/dashboard', { replaceState: true });
		}
	});
</script>

<!-- Show nothing while redirecting -->
<div class="min-h-screen bg-background flex items-center justify-center">
	<div class="text-center">
		<div class="animate-spin w-8 h-8 border-4 border-primary border-t-transparent rounded-full mx-auto mb-4"></div>
		<p class="text-sm text-muted-foreground uppercase font-bold tracking-wide">
			Opening {panel}...
		</p>
	</div>
</div>
