<script lang="ts">
	import { page } from '$app/stores';
	import { onMount } from 'svelte';
	import { getItem, type MemoryItem } from '$lib/api';

	let item: MemoryItem | null = null;
	let loading = true;
	let error = '';

	$: category = $page.params.category;
	$: id = $page.params.id;

	async function loadItem() {
		if (!category || !id) return;

		loading = true;
		error = '';
		item = null;

		try {
			item = await getItem(category, id);
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to load item';
		} finally {
			loading = false;
		}
	}

	onMount(() => {
		loadItem();
	});

	$: if (category && id) {
		loadItem();
	}

	function parseWikilinks(content: string): string {
		// Convert [[category/id|label]] or [[category/id]] to links
		return content.replace(/\[\[([^\]|]+)(\|([^\]]+))?\]\]/g, (match, target, _, label) => {
			const displayText = label || target;
			return `<a href="/item/${target}" class="text-primary hover:text-terminal-green font-bold underline decoration-2 underline-offset-4 decoration-primary/30 transition-colors">${displayText}</a>`;
		});
	}
</script>

<svelte:head>
	<title>{item?.title || 'RECORD'} • RECALL-KRALIKI</title>
</svelte:head>

<div class="max-w-4xl mx-auto">
	{#if loading}
		<div class="brutal-card text-center py-20 bg-card">
			<div class="text-2xl font-display text-terminal-green animate-pulse">ACCESSING_MEMORY_OBJECT...</div>
			<div class="mt-4 font-mono text-[10px] opacity-40 uppercase tracking-[0.3em]">Address: {category}/{id}</div>
		</div>
	{:else if error}
		<div class="brutal-card border-system-red bg-system-red/10 text-system-red p-4 font-mono text-sm">
			<span class="font-bold uppercase">[ ACCESS_DENIED ]</span> {error}
		</div>
	{:else if item}
		<!-- Header -->
		<div class="mb-8 border-b-2 border-border pb-6 relative">
			<div class="absolute -top-4 -left-4 bg-void text-terminal-green font-bold text-[10px] px-2 py-1 uppercase border border-terminal-green shadow-brutal">RECORD_ACTIVE</div>
			
			<div class="flex flex-wrap items-center gap-3 mb-4">
				<span class="text-xs font-bold px-3 py-1 bg-void text-terminal-green border-2 border-terminal-green uppercase tracking-widest">
					{item.category}
				</span>
				<h1 class="text-4xl font-display tracking-tight">{item.title}</h1>
			</div>

			{#if item.tags && item.tags.length > 0}
				<div class="flex flex-wrap gap-2">
					{#each item.tags as tag}
						<span class="text-[10px] font-bold px-2 py-0.5 border border-border opacity-70 uppercase tracking-tighter">
							#{tag}
						</span>
					{/each}
				</div>
			{/if}
		</div>

		<!-- Content -->
		<div class="brutal-card p-8 bg-card mb-8 relative">
			<div class="absolute top-0 right-0 p-2 opacity-10 font-mono text-[60px] leading-none pointer-events-none select-none">CONTENT</div>
			<div class="markdown relative z-10">
				{@html parseWikilinks(item.content)}
			</div>
		</div>

		<div class="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
			<!-- Related Items -->
			{#if item.related && item.related.length > 0}
				<div class="brutal-card p-6 bg-card relative">
					<div class="absolute top-0 right-0 p-2 opacity-10 font-mono text-[40px] leading-none pointer-events-none select-none">LINKS</div>
					<h3 class="font-display text-sm border-b border-border pb-2 mb-4">🔗 RELATED_ITEMS ({item.related.length})</h3>

					<div class="space-y-3">
						{#each item.related as relatedId}
							{#if relatedId.includes('/')}
								{@const [cat, rid] = relatedId.split('/')}
								<a
									href="/item/{cat}/{rid}"
									class="block p-3 border-2 border-transparent hover:border-terminal-green bg-void/5 hover:bg-terminal-green/5 transition-all group"
								>
									<div class="flex items-center justify-between">
										<span class="text-[9px] font-bold px-1.5 py-0.5 bg-void text-terminal-green uppercase tracking-widest">{cat}</span>
										<span class="text-[10px] font-mono opacity-50">>> OPEN</span>
									</div>
									<div class="text-xs font-bold mt-1 group-hover:text-terminal-green">{rid}</div>
								</a>
							{/if}
						{/each}
					</div>
				</div>
			{/if}

			<!-- Wikilinks -->
			{#if item.wikilinks && item.wikilinks.length > 0}
				<div class="brutal-card p-6 bg-card relative">
					<div class="absolute top-0 right-0 p-2 opacity-10 font-mono text-[40px] leading-none pointer-events-none select-none">REFS</div>
					<h3 class="font-display text-sm border-b border-border pb-2 mb-4">📎 WIKILINKS ({item.wikilinks.length})</h3>

					<div class="space-y-3">
						{#each item.wikilinks as wikilink}
							{@const parsed = wikilink.match(/\[\[([^\]|]+)(\|([^\]]+))?\]\]/)}
							{#if parsed}
								{@const target = parsed[1]}
								{@const label = parsed[3] || target}
								<a
									href="/item/{target}"
									class="block p-3 border-2 border-transparent hover:border-cyan-data bg-void/5 hover:bg-cyan-data/5 transition-all group"
								>
									<div class="flex items-center justify-between">
										<span class="text-xs font-bold group-hover:text-cyan-data">{label}</span>
										<span class="text-[10px] font-mono opacity-50">-> {target}</span>
									</div>
								</a>
							{/if}
						{/each}
					</div>
				</div>
			{/if}
		</div>

		<!-- Metadata -->
		<div class="brutal-card p-6 bg-void text-concrete mb-10">
			<h3 class="font-display text-sm border-b border-concrete/20 pb-2 mb-4 text-terminal-green">ℹ️ OBJECT_METADATA</h3>

			<div class="space-y-3 text-[11px] font-mono uppercase tracking-wider">
				<div class="flex justify-between border-b border-concrete/10 pb-1">
					<span class="opacity-50">UNIQUE_ID:</span>
					<span class="font-bold">{item.id}</span>
				</div>
				<div class="flex justify-between border-b border-concrete/10 pb-1">
					<span class="opacity-50">CLASS_TYPE:</span>
					<span class="text-terminal-green font-bold">{item.category}</span>
				</div>
				<div class="flex justify-between border-b border-concrete/10 pb-1">
					<span class="opacity-50">SOURCE_FILE:</span>
					<span class="text-cyan-data font-bold truncate max-w-[200px]">{item.file_path}</span>
				</div>
			</div>
		</div>

		<!-- Actions -->
		<div class="flex flex-wrap gap-4">
			<a href="/" class="brutal-btn !bg-secondary !text-secondary-foreground !py-2 !px-4 text-xs">
				&lt;&lt; RETURN_TO_SEARCH
			</a>

			<a href="/recent" class="brutal-btn !bg-void !text-concrete !py-2 !px-4 text-xs border-concrete/20">
				VIEW_RECENT_STREAM
			</a>
		</div>
	{/if}
</div>