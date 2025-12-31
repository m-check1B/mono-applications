<script lang="ts">
	import { searchItems, type SearchResult } from '$lib/api';

	let query = '';
	let category = '';
	let searchType: 'keyword' | 'semantic' | 'hybrid' = 'hybrid';
	let results: SearchResult[] = [];
	let loading = false;
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

	async function handleSearch() {
		if (!query.trim()) return;

		loading = true;
		error = '';
		results = [];

		try {
			const response = await searchItems({
				query,
				category: category === 'all' ? undefined : category,
				search_type: searchType,
				limit: 20
			});

			results = response.results;
		} catch (e) {
			error = e instanceof Error ? e.message : 'Search failed';
		} finally {
			loading = false;
		}
	}

	function handleKeydown(e: KeyboardEvent) {
		if (e.key === 'Enter') {
			handleSearch();
		}
	}
</script>

<svelte:head>
	<title>Search • RECALL-KRALIKI</title>
</svelte:head>

<div class="max-w-4xl mx-auto">
	<div class="mb-10">
		<h1 class="text-4xl font-display mb-2">SEARCH_KNOWLEDGE_BASE</h1>
		<div class="flex items-center gap-2 text-xs font-mono font-bold text-muted-foreground uppercase tracking-wider">
			<span class="text-terminal-green">&gt;&gt; STATUS:</span> READY_FOR_QUERY
		</div>
	</div>

	<!-- Search Form -->
	<div class="brutal-card p-6 mb-8 bg-card relative overflow-hidden">
		<div class="absolute top-0 right-0 p-2 opacity-10 font-mono text-[80px] leading-none pointer-events-none select-none">SEARCH</div>
		
		<div class="mb-6">
			<label for="query" class="block text-xs font-bold uppercase tracking-widest mb-2 opacity-70">Query String</label>
			<input
				id="query"
				type="text"
				bind:value={query}
				on:keydown={handleKeydown}
				placeholder="Find decisions, insights, learnings..."
				class="brutal-input text-lg"
			/>
		</div>

		<div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
			<div>
				<label for="category" class="block text-xs font-bold uppercase tracking-widest mb-2 opacity-70">Filter: Category</label>
				<select
					id="category"
					bind:value={category}
					class="brutal-input appearance-none cursor-pointer"
				>
					{#each categories as cat}
						<option value={cat === 'all' ? '' : cat}>{cat.toUpperCase()}</option>
					{/each}
				</select>
			</div>

			<div>
				<label for="searchType" class="block text-xs font-bold uppercase tracking-widest mb-2 opacity-70">Engine: Search Type</label>
				<select
					id="searchType"
					bind:value={searchType}
					class="brutal-input appearance-none cursor-pointer"
				>
					<option value="hybrid">HYBRID (KEYWORD + SEMANTIC)</option>
					<option value="keyword">KEYWORD_ONLY</option>
					<option value="semantic">SEMANTIC_ONLY</option>
				</select>
			</div>
		</div>

		<button
			on:click={handleSearch}
			disabled={loading || !query.trim()}
			class="brutal-btn w-full !bg-primary text-primary-foreground disabled:opacity-50 disabled:cursor-not-allowed"
		>
			{loading ? 'EXECUTING_SEARCH...' : 'EXECUTE_QUERY'}
		</button>
	</div>

	<!-- Error -->
	{#if error}
		<div class="brutal-card border-system-red bg-system-red/10 text-system-red p-4 mb-8 font-mono text-sm">
			<span class="font-bold uppercase">[ ERROR ]</span> {error}
		</div>
	{/if}

	<!-- Results -->
	{#if results.length > 0}
		<div class="mb-4 flex items-center justify-between border-b-2 border-border pb-2">
			<div class="text-[10px] font-mono font-bold uppercase tracking-widest">
				QUERY_RESULTS: {results.length} ITEMS_FOUND
			</div>
			<div class="text-[10px] font-mono font-bold text-terminal-green uppercase tracking-widest">
				TIME: {new Date().toLocaleTimeString()}
			</div>
		</div>

		<div class="space-y-6">
			{#each results as result}
				<div class="brutal-card p-6 bg-card group hover:border-terminal-green transition-colors">
					<div class="flex items-start justify-between mb-4">
						<div class="flex-1">
							<div class="flex flex-wrap items-center gap-3 mb-3">
								<span class="text-[10px] font-bold px-2 py-0.5 bg-void text-terminal-green border border-terminal-green uppercase tracking-widest">
									{result.category}
								</span>
								<h2 class="text-xl font-display group-hover:text-terminal-green transition-colors">{result.title}</h2>
							</div>

							{#if result.tags.length > 0}
								<div class="flex flex-wrap gap-2 mb-4">
									{#each result.tags as tag}
										<span class="text-[9px] font-bold px-2 py-0.5 border border-border opacity-60 uppercase tracking-tighter">
											#{tag}
										</span>
									{/each}
								</div>
							{/if}

							<p class="text-sm font-mono opacity-80 mb-6 line-clamp-3 leading-relaxed">{result.content}</p>

							<a
								href="/item/{result.category}/{result.id}"
								class="inline-flex items-center text-xs font-bold uppercase tracking-widest text-primary hover:text-terminal-green transition-colors"
							>
								<span class="mr-1">&gt;&gt;</span> VIEW_FULL_ITEM
							</a>
						</div>
					</div>
				</div>
			{/each}
		</div>
	{:else if !loading && query}
		<div class="brutal-card text-center py-16 bg-card/50">
			<div class="text-4xl mb-4 opacity-20 font-display">NULL_RESULTS</div>
			<p class="font-mono text-sm uppercase tracking-widest opacity-50">No memory matches found for "{query}"</p>
			<button on:click={() => {query = ''; results = []}} class="brutal-btn mt-8 text-xs">RESET_QUERY</button>
		</div>
	{/if}
</div>
