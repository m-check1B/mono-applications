<script lang="ts">
	import { onMount } from 'svelte';
	import { fly } from 'svelte/transition';
	import { Download, X, Smartphone } from 'lucide-svelte';
	import { browser } from '$app/environment';
	import { logger } from '$lib/utils/logger';

	interface BeforeInstallPromptEvent extends Event {
		prompt(): Promise<void>;
		userChoice: Promise<{ outcome: 'accepted' | 'dismissed' }>;
	}

	let showPrompt = $state(false);
	let deferredPrompt = $state<BeforeInstallPromptEvent | null>(null);
	let isIOS = $state(false);
	let isStandalone = $state(false);

	onMount(() => {
		if (!browser) return;

		// Check if already installed (standalone mode)
		isStandalone = window.matchMedia('(display-mode: standalone)').matches ||
			(window.navigator as any).standalone === true;

		if (isStandalone) return;

		// Check if iOS (Safari doesn't support beforeinstallprompt)
		isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent) && !(window as any).MSStream;

		// Check if dismissed recently (24 hours)
		const dismissedAt = localStorage.getItem('pwa-prompt-dismissed');
		if (dismissedAt) {
			const dismissedTime = parseInt(dismissedAt, 10);
			if (Date.now() - dismissedTime < 24 * 60 * 60 * 1000) {
				return;
			}
		}

		// For iOS, show manual install instructions after delay
		if (isIOS) {
			setTimeout(() => {
				showPrompt = true;
			}, 5000);
			return;
		}

		// Listen for beforeinstallprompt event (Chrome, Edge, etc.)
		const handlePrompt = (e: Event) => {
			e.preventDefault();
			deferredPrompt = e as BeforeInstallPromptEvent;
			setTimeout(() => {
				showPrompt = true;
			}, 3000);
		};

		window.addEventListener('beforeinstallprompt', handlePrompt);

		// Hide prompt when installed
		window.addEventListener('appinstalled', () => {
			showPrompt = false;
			deferredPrompt = null;
		});

		return () => {
			window.removeEventListener('beforeinstallprompt', handlePrompt);
		};
	});

	async function handleInstall() {
		if (!deferredPrompt) return;

		try {
			await deferredPrompt.prompt();
			const { outcome } = await deferredPrompt.userChoice;

			if (outcome === 'accepted') {
				showPrompt = false;
			}
		} catch (error) {
			logger.error('[PWA] Install prompt error', error);
		}

		deferredPrompt = null;
	}

	function dismiss() {
		showPrompt = false;
		localStorage.setItem('pwa-prompt-dismissed', Date.now().toString());
	}
</script>

{#if showPrompt}
	<div
		class="fixed bottom-4 left-4 right-4 z-50 max-w-md mx-auto"
		transition:fly={{ y: 100, duration: 300 }}
	>
		<div
			class="flex flex-col gap-3 p-4 border-2 border-black dark:border-white bg-card shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] dark:shadow-[4px_4px_0px_0px_rgba(255,255,255,0.3)]"
		>
			<div class="flex items-start gap-3">
				<div class="p-2 bg-primary text-primary-foreground">
					<Smartphone class="w-5 h-5" />
				</div>
				<div class="flex-1">
					<h3 class="text-sm font-black uppercase tracking-wider">Install Focus</h3>
					{#if isIOS}
						<p class="text-xs text-muted-foreground mt-1">
							Tap <span class="inline-block px-1 bg-muted">Share</span> then <span class="inline-block px-1 bg-muted">Add to Home Screen</span>
						</p>
					{:else}
						<p class="text-xs text-muted-foreground mt-1">
							Install for quick access and offline use
						</p>
					{/if}
				</div>
				<button
					class="p-1 hover:bg-muted transition-colors"
					onclick={dismiss}
					aria-label="Dismiss"
				>
					<X class="w-4 h-4" />
				</button>
			</div>

			{#if !isIOS && deferredPrompt}
				<div class="flex gap-2">
					<button
						class="flex-1 px-4 py-2 text-xs font-black uppercase tracking-wider border-2 border-black dark:border-white hover:bg-muted transition-colors"
						onclick={dismiss}
					>
						Not now
					</button>
					<button
						class="flex-1 px-4 py-2 text-xs font-black uppercase tracking-wider bg-primary text-primary-foreground border-2 border-black dark:border-white hover:opacity-90 transition-opacity flex items-center justify-center gap-2"
						onclick={handleInstall}
					>
						<Download class="w-4 h-4" />
						Install
					</button>
				</div>
			{/if}
		</div>
	</div>
{/if}
