<script lang="ts">
	import { aiFileSearchQuery, type FileSearchCitation } from '$lib/api/ai_file_search';
	import { Search, Sparkles, AlertCircle, FileText, ExternalLink } from 'lucide-svelte';
	import MarkdownRenderer from '$lib/components/MarkdownRenderer.svelte';

	let query = '';
	let searching = false;
	let result: { answer: string; citations: FileSearchCitation[] } | null = null;
	let error: string | null = null;

	async function handleSearch() {
		if (!query.trim()) return;

		searching = true;
		error = null;
		result = null;

		try {
			result = await aiFileSearchQuery(query.trim());
		} catch (e: any) {
			error = e.message || 'An unexpected error occurred';
		} finally {
			searching = false;
		}
	}

	function handleKeyPress(event: KeyboardEvent) {
		if (event.key === 'Enter' && !event.shiftKey) {
			event.preventDefault();
			handleSearch();
		}
	}

	function clearResults() {
		result = null;
		error = null;
		query = '';
	}
</script>

<div class="ai-search-panel bg-card border border-border rounded-lg shadow-sm">
	<!-- Header -->
	<div class="flex items-center gap-2 p-4 border-b border-border">
		<Sparkles class="w-5 h-5 text-primary" />
		<h3 class="font-semibold">AI Knowledge Search</h3>
		<span class="ml-auto text-xs px-2 py-1 bg-primary/10 text-primary rounded-full">
			Powered by Gemini
		</span>
	</div>

	<!-- Search Input -->
	<div class="p-4 space-y-4">
		<div class="flex gap-2">
			<div class="flex-1 relative">
				<Search
					class="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground"
				/>
				<input
					type="text"
					bind:value={query}
					onkeypress={handleKeyPress}
					placeholder="Ask about your knowledge base..."
					disabled={searching}
					class="w-full pl-10 pr-4 py-2 bg-background border border-input rounded-lg focus:outline-none focus:ring-2 focus:ring-ring disabled:opacity-50 disabled:cursor-not-allowed text-sm"
				/>
			</div>
			<button
				onclick={handleSearch}
				disabled={searching || !query.trim()}
				class="px-6 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2 font-medium"
			>
				{#if searching}
					<div class="w-4 h-4 border-2 border-primary-foreground border-t-transparent rounded-full animate-spin"></div>
					<span>Searching...</span>
				{:else}
					<Search class="w-4 h-4" />
					<span>Search</span>
				{/if}
			</button>
		</div>

		<p class="text-xs text-muted-foreground">
			Try asking: "What are my project ideas?" or "Show me tasks related to documentation"
		</p>
	</div>

	<!-- Error Display -->
	{#if error}
		<div class="mx-4 mb-4 p-4 bg-destructive/10 border border-destructive/20 text-destructive rounded-lg flex items-start gap-3">
			<AlertCircle class="w-5 h-5 flex-shrink-0 mt-0.5" />
			<div class="flex-1">
				<p class="font-medium mb-1">Search Failed</p>
				<p class="text-sm opacity-90">{error}</p>
			</div>
			<button
				onclick={() => (error = null)}
				class="text-destructive hover:text-destructive/80 text-sm font-medium"
			>
				Dismiss
			</button>
		</div>
	{/if}

	<!-- Results Display -->
	{#if result}
		<div class="p-4 space-y-4 border-t border-border">
			<!-- Answer Section -->
			<div class="space-y-2">
				<div class="flex items-center justify-between">
					<h4 class="font-semibold flex items-center gap-2">
						<Sparkles class="w-4 h-4 text-primary" />
						Answer
					</h4>
					<button
						onclick={clearResults}
						class="text-xs text-muted-foreground hover:text-foreground transition-colors"
					>
						Clear
					</button>
				</div>
				<div
					class="p-4 bg-primary/5 dark:bg-primary/10 border border-primary/20 rounded-lg prose prose-sm max-w-none dark:prose-invert"
				>
					<MarkdownRenderer content={result.answer} />
				</div>
			</div>

			<!-- Sources/Citations Section -->
			{#if result.citations && result.citations.length > 0}
				<div class="space-y-3">
					<h4 class="font-semibold flex items-center gap-2">
						<FileText class="w-4 h-4" />
						Sources ({result.citations.length})
					</h4>
					<div class="space-y-2">
						{#each result.citations as citation, index}
							<div
								class="p-3 bg-accent/50 hover:bg-accent border border-border rounded-lg transition-colors group"
							>
								<div class="flex items-start gap-3">
									<div
										class="w-6 h-6 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0 text-xs font-medium text-primary"
									>
										{index + 1}
									</div>
									<div class="flex-1 min-w-0">
										{#if citation.knowledgeItemId}
											<a
												href="/dashboard/knowledge?highlight={citation.knowledgeItemId}"
												class="font-medium text-primary hover:text-primary/80 transition-colors flex items-center gap-2 group"
											>
												<span class="truncate">{citation.documentName || citation.knowledgeItemId}</span>
												<ExternalLink class="w-3 h-3 opacity-0 group-hover:opacity-100 transition-opacity flex-shrink-0" />
											</a>
										{:else}
											<span class="font-medium text-foreground">{citation.documentName}</span>
										{/if}
										{#if citation.excerpt}
											<p class="text-xs text-muted-foreground mt-1 line-clamp-2">
												{citation.excerpt}
											</p>
										{/if}
									</div>
								</div>
							</div>
						{/each}
					</div>
				</div>
			{/if}
		</div>
	{/if}

	<!-- Empty State (when no search performed) -->
	{#if !result && !error && !searching}
		<div class="p-8 text-center">
			<div class="w-16 h-16 mx-auto mb-4 rounded-2xl bg-primary/10 flex items-center justify-center">
				<Search class="w-8 h-8 text-primary" />
			</div>
			<h4 class="font-semibold mb-2">Search Your Knowledge Base</h4>
			<p class="text-sm text-muted-foreground max-w-sm mx-auto">
				Use AI-powered search to find answers across all your notes, tasks, and documents instantly.
			</p>
		</div>
	{/if}
</div>

<style>
	/* Ensure markdown content doesn't overflow */
	:global(.ai-search-panel .prose) {
		overflow-wrap: break-word;
		word-break: break-word;
	}

	/* Custom scrollbar for results */
	.ai-search-panel {
		max-height: 600px;
		overflow-y: auto;
	}

	.ai-search-panel::-webkit-scrollbar {
		width: 6px;
	}

	.ai-search-panel::-webkit-scrollbar-track {
		background: transparent;
	}

	.ai-search-panel::-webkit-scrollbar-thumb {
		background: hsl(var(--muted-foreground) / 0.3);
		border-radius: 3px;
	}

	.ai-search-panel::-webkit-scrollbar-thumb:hover {
		background: hsl(var(--muted-foreground) / 0.5);
	}
</style>
