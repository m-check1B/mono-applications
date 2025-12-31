<script lang="ts">
	import { Globe } from 'lucide-svelte';
	import { locale, setLocale, SUPPORTED_LOCALES, LOCALE_NAMES, type Locale, t } from '$lib/i18n';
	import { onMount } from 'svelte';

	let currentLocale: Locale = 'en';
	let showDropdown = false;

	// Subscribe to locale changes
	const unsubscribe = locale.subscribe((value) => {
		currentLocale = value;
	});

	onMount(() => {
		return unsubscribe;
	});

	function changeLanguage(newLocale: Locale) {
		setLocale(newLocale);
		showDropdown = false;
	}

	function toggleDropdown() {
		showDropdown = !showDropdown;
	}

	// Close dropdown when clicking outside
	function handleClickOutside(event: MouseEvent) {
		const target = event.target as HTMLElement;
		if (!target.closest('.language-switcher')) {
			showDropdown = false;
		}
	}

	onMount(() => {
		document.addEventListener('click', handleClickOutside);
		return () => {
			document.removeEventListener('click', handleClickOutside);
		};
	});
</script>

<div class="language-switcher relative">
	<button
		type="button"
		onclick={toggleDropdown}
		class="flex items-center gap-2 px-3 py-2 rounded-xl border border-divider-subtle bg-secondary hover:bg-secondary-hover transition-colors"
		aria-label={$t('common.language')}
	>
		<Globe class="size-4 text-text-secondary" />
		<span class="text-sm font-medium text-text-primary uppercase">{currentLocale}</span>
	</button>

	{#if showDropdown}
		<div
			class="absolute right-0 mt-2 w-48 rounded-lg border border-divider-subtle bg-background shadow-lg z-50"
		>
			<div class="py-1">
				{#each SUPPORTED_LOCALES as locale}
					<button
						type="button"
						onclick={() => changeLanguage(locale)}
						class="w-full text-left px-4 py-2 text-sm hover:bg-secondary-hover transition-colors flex items-center justify-between"
						class:bg-secondary-hover={locale === currentLocale}
					>
						<span class="text-text-primary">{LOCALE_NAMES[locale]}</span>
						{#if locale === currentLocale}
							<span class="text-primary">✓</span>
						{/if}
					</button>
				{/each}
			</div>
		</div>
	{/if}
</div>

<style>
	.language-switcher {
		position: relative;
	}
</style>
