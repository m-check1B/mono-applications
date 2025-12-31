<script lang="ts">
	import { captureItem, getCategories, type CaptureResponse } from '$lib/api';
	import { onMount } from 'svelte';

	let content = '';
	let category = '';
	let tags = '';
	let autoCategorize = true;
	let autoLink = true;

	let loading = false;
	let error = '';
	let success: CaptureResponse | null = null;
	let categories: string[] = [];

	onMount(async () => {
		try {
			const response = await getCategories();
			categories = response.categories;
		} catch (e) {
			console.error('Failed to load categories:', e);
		}
	});

	async function handleCapture() {
		if (!content.trim()) return;

		loading = true;
		error = '';
		success = null;

		try {
			const tagList = tags
				.split(',')
				.map((t) => t.trim())
				.filter((t) => t);

			const response = await captureItem({
				content,
				category: category || undefined,
				tags: tagList.length > 0 ? tagList : undefined,
				auto_categorize: autoCategorize,
				auto_link: autoLink
			});

			success = response;

			// Reset form
			content = '';
			category = '';
			tags = '';
		} catch (e) {
			error = e instanceof Error ? e.message : 'Capture failed';
		} finally {
			loading = false;
		}
	}
</script>

<svelte:head>
	<title>Capture • RECALL-KRALIKI</title>
</svelte:head>

<div class="max-w-4xl mx-auto">
	<div class="mb-10">
		<h1 class="text-4xl font-display mb-2">CAPTURE_KNOWLEDGE</h1>
		<div class="flex items-center gap-2 text-xs font-mono font-bold text-muted-foreground uppercase tracking-wider">
			<span class="text-terminal-green">&gt;&gt; STATUS:</span> INPUT_STREAM_OPEN
		</div>
	</div>

	<!-- Capture Form -->
	<div class="brutal-card p-6 mb-8 bg-card relative overflow-hidden">
		<div class="absolute top-0 right-0 p-2 opacity-10 font-mono text-[80px] leading-none pointer-events-none select-none">CAPTURE</div>
		
		<div class="mb-6">
			<label for="content" class="block text-xs font-bold uppercase tracking-widest mb-2 opacity-70">
				Content Stream (Markdown)
			</label>
			<textarea
				id="content"
				bind:value={content}
				placeholder="# Decision: Use GLM 4.6 for AI features..."
				rows={12}
				class="brutal-input font-mono text-sm leading-relaxed min-h-[300px]"
			></textarea>
		</div>

		<div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
			<div>
				<label for="category" class="block text-xs font-bold uppercase tracking-widest mb-2 opacity-70">
					Target: Category {autoCategorize ? '(OPTIONAL - AI_ENABLED)' : ''}
				</label>
				<select
					id="category"
					bind:value={category}
					class="brutal-input appearance-none cursor-pointer"
				>
					<option value="">AUTO_CATEGORIZE</option>
					{#each categories as cat}
						<option value={cat}>{cat.toUpperCase()}</option>
					{/each}
				</select>
			</div>

			<div>
				<label for="tags" class="block text-xs font-bold uppercase tracking-widest mb-2 opacity-70">
					Metadata: Tags (comma-separated)
				</label>
				<input
					id="tags"
					type="text"
					bind:value={tags}
					placeholder="ai, infra, pricing..."
					class="brutal-input"
				/>
			</div>
		</div>

		<div class="flex flex-wrap items-center gap-8 mb-8 border-t border-border pt-6">
			<label class="flex items-center gap-3 cursor-pointer group">
				<div class="w-6 h-6 border-2 border-border flex items-center justify-center transition-colors group-hover:border-terminal-green">
					{#if autoCategorize}
						<div class="w-3 h-3 bg-terminal-green"></div>
					{/if}
				</div>
				<input type="checkbox" bind:checked={autoCategorize} class="hidden" />
				<span class="text-xs font-bold uppercase tracking-widest">AI_CATEGORIZATION</span>
			</label>

			<label class="flex items-center gap-3 cursor-pointer group">
				<div class="w-6 h-6 border-2 border-border flex items-center justify-center transition-colors group-hover:border-terminal-green">
					{#if autoLink}
						<div class="w-3 h-3 bg-terminal-green"></div>
					{/if}
				</div>
				<input type="checkbox" bind:checked={autoLink} class="hidden" />
				<span class="text-xs font-bold uppercase tracking-widest">AUTO_WIKILINKS</span>
			</label>
		</div>

		<button
			on:click={handleCapture}
			disabled={loading || !content.trim()}
			class="brutal-btn w-full !bg-primary text-primary-foreground disabled:opacity-50 disabled:cursor-not-allowed"
		>
			{loading ? 'PROCESSING_STREAM...' : 'COMMIT_TO_MEMORY'}
		</button>
	</div>

	<!-- Success Message -->
	{#if success}
		<div class="brutal-card border-terminal-green bg-terminal-green/5 p-6 mb-8 relative">
			<div class="absolute top-0 right-0 bg-terminal-green text-void font-bold text-[10px] px-2 py-1 uppercase">Success</div>
			
			<h3 class="text-2xl font-display text-terminal-green mb-4">COMMIT_SUCCESSFUL</h3>

			<div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs font-mono font-bold uppercase">
				<div class="stat-row border-b border-terminal-green/20 py-2 flex justify-between">
					<span class="opacity-50">RECORD_ID:</span>
					<span>{success.id}</span>
				</div>
				<div class="stat-row border-b border-terminal-green/20 py-2 flex justify-between">
					<span class="opacity-50">CATEGORY:</span>
					<span class="text-terminal-green">{success.category}</span>
				</div>
				<div class="stat-row border-b border-terminal-green/20 py-2 flex justify-between">
					<span class="opacity-50">TAG_COUNT:</span>
					<span>{success.tags.length}</span>
				</div>
				<div class="stat-row border-b border-terminal-green/20 py-2 flex justify-between">
					<span class="opacity-50">RELATIONS:</span>
					<span>{success.related_items.length} FOUND</span>
				</div>
			</div>

			<div class="mt-8">
				<a href="/item/{success.category}/{success.id}" class="brutal-btn !px-4 !py-2 text-xs">
					OPEN_RECORD_DETAILS
				</a>
			</div>
		</div>
	{/if}

	<!-- Error Message -->
	{#if error}
		<div class="brutal-card border-system-red bg-system-red/10 text-system-red p-4 mb-8 font-mono text-sm">
			<span class="font-bold uppercase">[ ERROR ]</span> {error}
		</div>
	{/if}
</div>