<script lang="ts">
	import Header from '$lib/components/layout/Header.svelte';
	import BottomNav from '$lib/components/layout/BottomNav.svelte';
	import OnboardingModal from '$lib/components/onboarding/OnboardingModal.svelte';
	import { authStore } from '$lib/stores';
	import { goto } from '$app/navigation';
	import { onDestroy, onMount } from 'svelte';
	import { t } from '$lib/i18n';

	const { children } = $props<{ children: () => unknown }>();

	let isAuthorized = $state(false);
	let unsubscribe: (() => void) | null = null;

	onMount(() => {
		const initial = authStore.getSnapshot();
		if (initial.status === 'authenticated' || initial.status === 'refreshing') {
			isAuthorized = true;
		} else {
			goto('/auth/login', { replaceState: true });
		}

		unsubscribe = authStore.subscribe((state) => {
			if (state.status === 'authenticated') {
				isAuthorized = true;
				return;
			}

			if (state.status === 'refreshing') {
				return;
			}

			isAuthorized = false;
			goto('/auth/login', { replaceState: true });
		});
	});

	onDestroy(() => {
		unsubscribe?.();
	});
</script>

{#if isAuthorized}
		<div class="flex min-h-screen flex-col bg-background text-foreground">
			<Header />
			<main class="flex-1 px-4 pb-[calc(var(--touch-target)+16px)] pt-6 md:px-6 lg:px-8">
				{@render children()}
			</main>

			<footer class="hidden md:block border-t border-divider py-4 px-6 text-center text-sm text-text-muted">
				<div class="flex items-center justify-center gap-4">
					<span>{$t('common.footer_company')}</span>
					<a href="/privacy" class="hover:text-foreground transition-colors">{$t('legal.privacy')}</a>
				</div>
			</footer>

			<div class="sticky bottom-0 z-30 border-t-2 border-divider bg-card md:hidden">
				<BottomNav />
			</div>

			<!-- Onboarding for new users -->
			<OnboardingModal />
		</div>
{:else}
	<div class="flex min-h-screen items-center justify-center bg-background text-text-muted">
		<span class="text-sm">{$t('common.redirecting_sign_in')}</span>
	</div>
{/if}
