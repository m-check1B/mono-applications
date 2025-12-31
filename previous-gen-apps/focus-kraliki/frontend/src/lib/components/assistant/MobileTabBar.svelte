<script lang="ts">
	import type { AssistantNavItem } from './types';

	interface Props {
		navItems?: AssistantNavItem[];
		currentPath?: string;
	}

	let {
		navItems = [],
		currentPath = ''
	}: Props = $props();

	const columnsClass = {
		3: 'grid-cols-3',
		4: 'grid-cols-4',
		5: 'grid-cols-5',
		6: 'grid-cols-6'
	};

	function resolveColumnsClass(count: number): string {
		return columnsClass[count as keyof typeof columnsClass] ?? 'grid-cols-4';
	}

	let activeColumnsClass = $derived(resolveColumnsClass(navItems.length));
</script>

<nav class="fixed bottom-0 left-0 right-0 border-t-2 border-black dark:border-white bg-background z-40">
	<div class={`grid ${activeColumnsClass}`}>
		{#each navItems as item}
			{#if item.href && !item.disabled}
				<a
					href={item.href}
					class="flex flex-col items-center justify-center py-3 transition-colors border-r border-black dark:border-white last:border-r-0 {currentPath === item.href
						? 'bg-primary text-primary-foreground font-bold'
						: 'text-muted-foreground hover:bg-accent hover:text-accent-foreground'}"
					aria-label={item.label}
				>
					<item.icon class="w-5 h-5" />
					<span class="text-[10px] mt-1 uppercase tracking-wide font-bold">{item.label}</span>
				</a>
			{:else}
				<button
					class="flex flex-col items-center justify-center py-3 text-muted-foreground/40 cursor-not-allowed border-r border-black dark:border-white last:border-r-0"
					disabled
					type="button"
					aria-label={`${item.label} (coming soon)`}
				>
					<item.icon class="w-5 h-5" />
					<span class="text-[10px] mt-1 uppercase tracking-wide font-bold">{item.label}</span>
				</button>
			{/if}
		{/each}
	</div>
</nav>
