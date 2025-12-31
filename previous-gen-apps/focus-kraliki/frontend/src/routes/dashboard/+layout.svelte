<script lang="ts">
	import { onMount, onDestroy, type Snippet } from "svelte";
	import { authStore } from "$lib/stores/auth";
	import { goto } from "$app/navigation";
	import { connectWebSocket, disconnectWebSocket } from "$lib/api/websocket";
	import AssistantShell from "$lib/components/assistant/AssistantShell.svelte";
	import ContextPanel from "$lib/components/ContextPanel.svelte";
	import ToastStack from "$lib/components/ToastStack.svelte";
	import OnboardingModal from "$lib/components/onboarding/OnboardingModal.svelte";
	import ErrorBoundary from "$lib/components/ErrorBoundary.svelte";
	import { logger } from "$lib/utils/logger";

	let { children }: { children: Snippet } = $props();

	async function handleLogout() {
		await authStore.logout();
		goto("/login");
	}

	let user = $derived($authStore.user);

	// ✨ WebSocket real-time updates (Gap #6)
	onMount(() => {
		if ($authStore.token) {
			connectWebSocket();
			logger.info("[Dashboard] WebSocket connection initiated");
		}
	});

	onDestroy(() => {
		disconnectWebSocket();
		logger.info("[Dashboard] WebSocket connection closed");
	});
</script>

<ErrorBoundary fallback="Critical Failure in Dashboard Kernel">
	<AssistantShell {user} onLogout={handleLogout}>
		{@render children()}
	</AssistantShell>
</ErrorBoundary>

<!-- Context Panel (slides in from right) -->
<ErrorBoundary fallback="Panel Protocol Error">
	<ContextPanel />
</ErrorBoundary>

<!-- Global Toaster -->
<ToastStack />

<!-- Onboarding for new users -->
<OnboardingModal />
