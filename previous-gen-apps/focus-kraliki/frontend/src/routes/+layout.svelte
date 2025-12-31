<script lang="ts">
	import '../app.css';
	import { onMount, type Snippet } from 'svelte';
	import { ModeWatcher } from 'mode-watcher';
	import { authStore } from '$lib/stores/auth';
	import { websocketStore } from '$lib/stores/websocket';
	import { initAnalytics } from '$lib/analytics';
	import { api } from '$lib/api/client';
	import {
		OFFLINE_STORES,
		clearOfflineStore,
		isOnline,
		offlineKnowledge,
		offlineKnowledgeTypes,
		offlineProjects,
		offlineTasks,
		offlineTimeEntries,
		syncWithServer
	} from '$lib/utils/offlineStorage';
	import { browser } from '$app/environment';
	import PWAInstallPrompt from '$lib/components/PWAInstallPrompt.svelte';
	import { logger } from '$lib/utils/logger';

	let { children }: { children: Snippet } = $props();
	let onlineStatus = $state(true);
	let isSyncing = $state(false);
	let lastSyncAt = $state<string | null>(null);
	let syncError = $state<string | null>(null);

	async function refreshOfflineCaches() {
		if (!api.getToken()) {
			return;
		}

		const [tasksResponse, projectsResponse, knowledgeResponse, typesResponse, timeResponse] =
			await Promise.all([
				api.tasks.list(),
				api.projects.list(),
				api.knowledge.listKnowledgeItems(),
				api.knowledge.listItemTypes(),
				api.timeEntries.list({ limit: 100 })
			]) as [
				{ tasks?: any[] },
				{ projects?: any[] },
				{ items?: any[] },
				{ itemTypes?: any[] },
				{ entries?: any[] }
			];

		await clearOfflineStore(OFFLINE_STORES.TASKS);
		for (const task of tasksResponse.tasks || []) {
			await offlineTasks.save(task);
		}

		await clearOfflineStore(OFFLINE_STORES.PROJECTS);
		for (const project of projectsResponse.projects || []) {
			await offlineProjects.save(project);
		}

		await clearOfflineStore(OFFLINE_STORES.KNOWLEDGE);
		for (const item of knowledgeResponse.items || []) {
			await offlineKnowledge.save(item);
		}

		await clearOfflineStore(OFFLINE_STORES.KNOWLEDGE_TYPES);
		for (const itemType of typesResponse.itemTypes || []) {
			await offlineKnowledgeTypes.save(itemType);
		}

		await clearOfflineStore(OFFLINE_STORES.TIME_ENTRIES);
		for (const entry of timeResponse.entries || []) {
			await offlineTimeEntries.save(entry);
		}
	}

	async function syncOfflineChanges() {
		if (!isOnline() || isSyncing) {
			return;
		}

		if (!api.getToken()) {
			return;
		}

		isSyncing = true;
		syncError = null;
		try {
			const result = await syncWithServer(api);
			if (result.failed === 0) {
				await refreshOfflineCaches();
				lastSyncAt = new Date().toISOString();
			} else {
				syncError = `${result.failed} offline changes failed to sync.`;
			}
		} catch (error: any) {
			syncError = error?.message || 'Failed to sync offline changes.';
		} finally {
			isSyncing = false;
		}
	}

	onMount(() => {
		// Initialize privacy-first analytics (Plausible)
		const cleanupAnalytics = initAnalytics();

		// Restore session from localStorage on mount
		const token = localStorage.getItem('token');
		if (token) {
			void authStore.restoreSession(token).then(() => {
				if (isOnline()) {
					void syncOfflineChanges();
				}
			});
		}

		onlineStatus = isOnline();

		// Register service worker for PWA support
		if (browser && 'serviceWorker' in navigator) {
			navigator.serviceWorker
				.register('/service-worker.js')
				.then((registration) => {
					logger.info('[PWA] Service worker registered:', { scope: registration.scope });

					// Check for updates periodically
					setInterval(() => {
						registration.update();
					}, 60 * 60 * 1000); // Check every hour
				})
				.catch((error) => {
					logger.error('[PWA] Service worker registration failed', error);
				});

			// Handle app install prompt
			let deferredPrompt: BeforeInstallPromptEvent | null = null;

			window.addEventListener('beforeinstallprompt', (e) => {
				e.preventDefault();
				deferredPrompt = e as BeforeInstallPromptEvent;
				logger.info('[PWA] Install prompt available');
			});

			// Notify when app is installed
			window.addEventListener('appinstalled', () => {
				logger.info('[PWA] App installed successfully');
				deferredPrompt = null;
			});
		}

		const handleOnline = () => {
			onlineStatus = true;
			void syncOfflineChanges();
		};

		const handleOffline = () => {
			onlineStatus = false;
		};

		window.addEventListener('online', handleOnline);
		window.addEventListener('offline', handleOffline);

		if (onlineStatus && api.getToken()) {
			void syncOfflineChanges();
		}

		return () => {
			cleanupAnalytics();
			window.removeEventListener('online', handleOnline);
			window.removeEventListener('offline', handleOffline);
		};
	});

	// Type definition for BeforeInstallPromptEvent
	interface BeforeInstallPromptEvent extends Event {
		prompt(): Promise<void>;
		userChoice: Promise<{ outcome: 'accepted' | 'dismissed' }>;
	}

	$effect(() => {
		if ($authStore.isAuthenticated) {
			websocketStore.connect();
		} else {
			websocketStore.disconnect();
		}
	});
</script>

<ModeWatcher />

<div class="min-h-screen flex flex-col bg-background bg-grid-pattern text-foreground font-mono">
	<div class="scanline"></div>
	{#if !onlineStatus || isSyncing || syncError}
		<div class="border-b border-border bg-card px-4 py-2 text-xs uppercase tracking-[0.3em] text-muted-foreground">
			{#if !onlineStatus}
				Offline mode: changes will sync when connected.
			{:else if isSyncing}
				Syncing offline changes...
			{:else}
				{syncError}
			{/if}
		</div>
	{/if}
	<div class="flex-1">
		{@render children()}
	</div>
	<footer class="border-t border-border py-4 px-6 text-center text-sm text-muted-foreground">
		<div class="flex items-center justify-center gap-4">
			<span>&copy; 2026 Verduona s.r.o.</span>
			<a href="/privacy" class="hover:text-foreground transition-colors">Privacy</a>
		</div>
	</footer>
	<PWAInstallPrompt />
</div>
