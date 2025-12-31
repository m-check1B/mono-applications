<script lang="ts">
	import { onMount } from 'svelte';
	import { getRecentItems, type MemoryItem } from '$lib/api';

	let category = '';
	let items: MemoryItem[] = [];
	let loading = true;
	let error = '';

	const categories = [
		'all',
		'decisions',
		'insights',
		'ideas',
		'learnings',
		'customers',
		'competitors',
		'research',
		'sessions'
	];

	async function loadItems() {
		loading = true;
		error = '';

		try {
			const response = await getRecentItems(category === 'all' ? undefined : category, 50);
			items = response.items;
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to load items';
		} finally {
			loading = false;
		}
	}

	onMount(() => {
		loadItems();
	});

	$: if (category !== undefined) {
		loadItems();
	}
</script>

<svelte:head>
	<title>Recent • RECALL-KRALIKI</title>
</svelte:head>

<div class="max-w-4xl mx-auto">
	<div class="mb-10">
		<h1 class="text-4xl font-display mb-2">RECENT_MEMORY_STREAM</h1>
		<div class="flex items-center gap-2 text-xs font-mono font-bold text-muted-foreground uppercase tracking-wider">
			<span class="text-terminal-green">&gt;&gt; STATUS:</span> PULLING_CHRONOLOGICAL_LOGS
		</div>
	</div>

	<!-- Category Filter -->
	<div class="brutal-card p-4 mb-8 bg-card flex flex-col md:flex-row items-center gap-4">
		<div class="text-[10px] font-mono font-bold uppercase tracking-widest opacity-60">Filter_By_Category:</div>
		<div class="flex-1 w-full">
			<select
				bind:value={category}
				class="brutal-input !py-2 appearance-none cursor-pointer"
			>
				{#each categories as cat}
					<option value={cat === 'all' ? '' : cat}>{cat.toUpperCase()}</option>
				{/each}
			</select>
		</div>
	</div>

	<!-- Loading -->
	{#if loading}
		<div class="brutal-card text-center py-20 bg-card">
			<div class="text-2xl font-display text-terminal-green animate-pulse">SCANNING_MEMORY_CELLS...</div>
			<div class="mt-4 font-mono text-[10px] opacity-40 uppercase tracking-[0.3em]">Sector 7G-12 // Retrieval in progress</div>
		</div>
	{:else if error}
		<!-- Error -->
		<div class="brutal-card border-system-red bg-system-red/10 text-system-red p-4 font-mono text-sm">
			<span class="font-bold uppercase">[ RETRIEVAL_ERROR ]</span> {error}
		</div>
	{:else if items.length === 0}
		<!-- Empty State -->
		<div class="brutal-card text-center py-20 bg-card">
			<div class="text-4xl mb-4 opacity-20 font-display">EMPTY_STREAM</div>
			<p class="font-mono text-sm uppercase tracking-widest opacity-50 mb-8">No records found in this category</p>
			<a href="/capture" class="brutal-btn text-xs">INITIALIZE_FIRST_CAPTURE</a>
		</div>
	{:else}
		<!-- Items List -->
		<div class="mb-4 flex items-center justify-between border-b-2 border-border pb-2">
			<div class="text-[10px] font-mono font-bold uppercase tracking-widest">
				STREAM_ITEMS: {items.length}
			</div>
			<div class="text-[10px] font-mono font-bold text-cyan-data uppercase tracking-widest">
				MODE: CHRONOLOGICAL_DESC
			</div>
		</div>

		<div class="space-y-6">
			{#each items as item}
				<div class="brutal-card p-6 bg-card group hover:border-terminal-green transition-colors relative overflow-hidden">
					<div class="absolute top-0 right-0 p-1 bg-border text-void font-bold text-[8px] uppercase">{item.id.substring(0,8)}</div>
					
					<div class="flex items-start justify-between mb-4">
						<div class="flex-1">
							<div class="flex flex-wrap items-center gap-3 mb-3">
								<span class="text-[10px] font-bold px-2 py-0.5 bg-void text-terminal-green border border-terminal-green uppercase tracking-widest">
									{item.category}
								</span>
								<h3 class="text-xl font-display group-hover:text-terminal-green transition-colors">{item.title}</h3>
							</div>

							{#if item.tags && item.tags.length > 0}
								<div class="flex flex-wrap gap-2 mb-4">
									{#each item.tags as tag}
										<span class="text-[9px] font-bold px-2 py-0.5 border border-border opacity-60 uppercase tracking-tighter">
											#{tag}
										</span>
									{/each}
								</div>
							{/if}

							<p class="text-sm font-mono opacity-80 mb-6 line-clamp-2 leading-relaxed italic">
								"{item.content.length > 200
									? item.content.substring(0, 200) + '...'
									: item.content}"
							</p>

							<a
								href="/item/{item.category}/{item.id}"
								class="inline-flex items-center text-xs font-bold uppercase tracking-widest text-primary hover:text-terminal-green transition-colors"
							>
								<span class="mr-1">&gt;&gt;</span> OPEN_FULL_RECORD
							</a>
						</div>
					</div>
				</div>
			{/each}
		</div>
	{/if}
</div>
