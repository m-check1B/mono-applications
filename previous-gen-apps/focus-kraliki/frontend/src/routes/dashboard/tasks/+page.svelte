<!--
✨ AI-First Route Architecture (Gap #8)
Redirects to main dashboard + opens tasks panel
Original CRUD view moved to context panel
-->
<script lang="ts">
	import PanelRedirect from '$lib/components/PanelRedirect.svelte';
</script>

<PanelRedirect panel="tasks" deepLink={true} />
