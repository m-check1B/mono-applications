<script lang="ts">
	import { onMount } from 'svelte';
	import '../app.css';
	import favicon from '$lib/assets/favicon.svg';
	import { ws } from '$lib/stores/websocket.svelte';
	import { auth } from '$lib/stores/auth.svelte';
	import { initLocale, loadTranslations } from '$lib/i18n';

	let { children } = $props();

	onMount(() => {
		// Initialize i18n
		const initialLocale = initLocale();
		loadTranslations(initialLocale);

		// Register Service Worker for PWA
		if ('serviceWorker' in navigator) {
			navigator.serviceWorker.register('/service-worker.js')
				.then(registration => {
					console.log('✅ Service Worker registered:', registration.scope);
				})
				.catch(error => {
					console.error('❌ Service Worker registration failed:', error);
				});
		}

		// Initialize WebSocket connection when app loads
		// Wait a moment for auth to initialize
		setTimeout(() => {
			if (auth.isAuthenticated) {
				console.log('🔌 Initializing WebSocket connection...');
				ws.connect();
			}
		}, 1000);

		// Cleanup on unmount
		return () => {
			ws.disconnect();
		};
	});
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
	<link rel="manifest" href="/manifest.json" />
	<meta name="theme-color" content="#3b82f6" />
	<meta name="mobile-web-app-capable" content="yes" />
	<meta name="apple-mobile-web-app-capable" content="yes" />
	<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent" />
	<meta name="apple-mobile-web-app-title" content="Voice by Kraliki" />
	<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no, viewport-fit=cover" />
</svelte:head>

{@render children?.()}
