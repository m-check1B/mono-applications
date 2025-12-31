<script lang="ts">
	import { onDestroy } from 'svelte';
	import { themeStore, type ThemeMode } from '$lib/stores/theme';
	import { Moon, Sun } from 'lucide-svelte';

let theme = $state<ThemeMode>('dark');

const unsubscribe = themeStore.subscribe((value) => {
	theme = value;
});

	onDestroy(() => {
		unsubscribe();
	});

	function toggleTheme() {
		themeStore.toggle();
	}
</script>

<button
	class="inline-flex min-h-[var(--touch-target)] w-[var(--touch-target)] items-center justify-center rounded-full border border-divider bg-secondary text-text-secondary transition hover:bg-secondary-hover hover:text-text-primary"
	type="button"
	onclick={toggleTheme}
	aria-label={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
>
	{#if theme === 'dark'}
		<Sun class="size-5 text-text-secondary" />
	{:else}
		<Moon class="size-5 text-text-secondary" />
	{/if}
</button>
