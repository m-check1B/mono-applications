<!--
✨ AI-First Route Architecture (Gap #8)
Redirects to main dashboard + opens knowledge panel
Original CRUD view moved to context panel
-->
<script lang="ts">
	import PanelRedirect from '$lib/components/PanelRedirect.svelte';
</script>

<PanelRedirect panel="knowledge" deepLink={true} />
