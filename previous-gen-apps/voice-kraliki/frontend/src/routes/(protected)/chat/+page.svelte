<script lang="ts">
	import { onMount } from 'svelte';
	import ChatInterface from '$lib/components/chat/ChatInterface.svelte';
	import ConnectionStatus from '$lib/components/chat/ConnectionStatus.svelte';
	import { chatStore } from '$lib/stores/chat';
	import type { PageData } from './$types';
	import type { Load } from '@sveltejs/kit';

	export let data: PageData;

	onMount(() => {
		// Initialize chat session
		chatStore.initializeSession({
			sessionId: data.sessionId,
			userId: data.userId,
			companyId: data.companyId
		});
	});
</script>

<div class="flex h-full flex-col">
	<div class="mb-4">
		<h1 class="text-2xl font-bold text-text-primary">Web Chat</h1>
		<p class="text-text-secondary">AI-powered customer engagement</p>
	</div>

	<ChatInterface />
	
	<!-- Global connection status indicator -->
	<ConnectionStatus />
</div>