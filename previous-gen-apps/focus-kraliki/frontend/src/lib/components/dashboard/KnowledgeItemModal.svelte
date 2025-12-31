<script lang="ts">
	import { onMount } from 'svelte';
	import { X, Save, Loader2, Sparkles, Wand2 } from 'lucide-svelte';
	import { knowledgeStore } from '$lib/stores/knowledge';
	import { enqueueAssistantCommand } from '$lib/utils/assistantQueue';

	interface Props {
		isOpen?: boolean;
		item?: any;
		onclose?: () => void;
		onsaved?: () => void;
	}

	let {
		isOpen = false,
		item = null,
		onclose,
		onsaved
	}: Props = $props();

	let title = $state('');
	let content = $state('');
	let typeId = $state('');
	let isSubmitting = $state(false);
	let isAiGenerating = $state(false); // ✨ Gap #11: AI affordance state

	let itemTypes = $derived($knowledgeStore.itemTypes);

	$effect(() => {
		if (isOpen) {
			if (item) {
				title = item.title;
				content = item.content;
				typeId = item.typeId;
			} else {
				title = '';
				content = '';
				typeId = itemTypes.length > 0 ? itemTypes[0].id : '';
			}
		}
	});

	onMount(() => {
		knowledgeStore.loadItemTypes();
	});

	function close() {
		onclose?.();
	}

	async function handleSubmit() {
		if (!title.trim() || !content.trim() || !typeId) return;

		isSubmitting = true;
		let result;

		if (item) {
			result = await knowledgeStore.updateKnowledgeItem(item.id, { title, content, typeId });
		} else {
			result = await knowledgeStore.createKnowledgeItem({ title, content, typeId });
		}

		isSubmitting = false;

		if (result.success) {
			close();
			onsaved?.();
		}
	}

	// ✨ Gap #11: AI affordance - Improve title
	function askAiImproveTitle() {
		if (!title.trim()) return;
		enqueueAssistantCommand({
			prompt: `Improve this title to be more clear and actionable: "${title}"\n\nProvide only the improved title, no explanation.`,
			context: { action: 'improve_title', currentTitle: title }
		});
	}

	// ✨ Gap #11: AI affordance - Generate content
	function askAiGenerateContent() {
		if (!title.trim()) return;
		isAiGenerating = true;
		enqueueAssistantCommand({
			prompt: `Generate detailed content for an item titled "${title}". The item is of type "${itemTypes.find(t => t.id === typeId)?.name || 'General'}". Provide actionable details, context, and next steps. Use markdown formatting.`,
			context: { action: 'generate_content', title, typeId }
		});
		// User will see response in AI canvas and can copy it
		setTimeout(() => { isAiGenerating = false; }, 1000);
	}

	// ✨ Gap #11: AI affordance - Expand content
	function askAiExpandContent() {
		if (!content.trim()) return;
		enqueueAssistantCommand({
			prompt: `Expand and improve this content:\n\n${content}\n\nAdd more detail, clarity, and structure. Use markdown formatting.`,
			context: { action: 'expand_content', currentContent: content }
		});
	}
</script>

{#if isOpen}
	<div class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
		<div class="w-full max-w-2xl bg-background border-2 border-black dark:border-white shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] dark:shadow-[8px_8px_0px_0px_rgba(255,255,255,1)] flex flex-col max-h-[90vh]">
			<!-- Header -->
			<div class="flex items-center justify-between p-6 border-b-2 border-black dark:border-white bg-secondary">
				<div class="flex items-center gap-3">
					<h2 class="text-xl font-black uppercase tracking-tighter">{item ? 'Edit Item' : 'New Knowledge Item'}</h2>
				</div>
				<button onclick={close} class="p-1 hover:bg-black/10 dark:hover:bg-white/10 transition-colors">
					<X class="w-6 h-6" />
				</button>
			</div>

			<!-- Content -->
			<div class="flex-1 overflow-y-auto p-6 space-y-6">
				<!-- ✨ Gap #11: AI affordance - Title field with AI assist -->
				<div class="space-y-2">
					<div class="flex items-center justify-between">
						<label for="title" class="text-xs font-black uppercase">Title</label>
						<button
							type="button"
							onclick={askAiImproveTitle}
							disabled={!title.trim()}
							class="text-[10px] uppercase font-bold tracking-wide px-2 py-1 border-2 border-primary text-primary hover:bg-primary hover:text-primary-foreground transition-colors disabled:opacity-30 disabled:cursor-not-allowed flex items-center gap-1"
							title="Ask AI to improve title"
						>
							<Sparkles class="w-3 h-3" />
							AI Improve
						</button>
					</div>
					<input
						id="title"
						type="text"
						bind:value={title}
						placeholder="Item Title"
						class="w-full border-2 border-black dark:border-white px-3 py-2 text-sm focus:outline-none focus:shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] dark:focus:shadow-[4px_4px_0px_0px_rgba(255,255,255,1)] transition-all font-bold"
					/>
				</div>

				<div class="space-y-2">
					<label for="type" class="text-xs font-black uppercase">Type</label>
					<select
						id="type"
						bind:value={typeId}
						class="w-full border-2 border-black dark:border-white px-3 py-2 text-sm focus:outline-none focus:shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] dark:focus:shadow-[4px_4px_0px_0px_rgba(255,255,255,1)] transition-all font-bold bg-background"
					>
						{#each itemTypes as type}
							<option value={type.id}>{type.name}</option>
						{/each}
					</select>
				</div>

				<!-- ✨ Gap #11: AI affordance - Content field with AI assist -->
				<div class="space-y-2">
					<div class="flex items-center justify-between">
						<label for="content" class="text-xs font-black uppercase">Content</label>
						<div class="flex gap-2">
							<button
								type="button"
								onclick={askAiGenerateContent}
								disabled={!title.trim() || isAiGenerating}
								class="text-[10px] uppercase font-bold tracking-wide px-2 py-1 border-2 border-accent text-accent-foreground bg-accent hover:bg-accent/80 transition-colors disabled:opacity-30 disabled:cursor-not-allowed flex items-center gap-1"
								title="Ask AI to generate content"
							>
								<Wand2 class="w-3 h-3" />
								{isAiGenerating ? 'Generating...' : 'AI Generate'}
							</button>
							{#if content.trim()}
								<button
									type="button"
									onclick={askAiExpandContent}
									class="text-[10px] uppercase font-bold tracking-wide px-2 py-1 border-2 border-primary text-primary hover:bg-primary hover:text-primary-foreground transition-colors flex items-center gap-1"
									title="Ask AI to expand content"
								>
									<Sparkles class="w-3 h-3" />
									AI Expand
								</button>
							{/if}
						</div>
					</div>
					<textarea
						id="content"
						bind:value={content}
						rows="10"
						placeholder="Markdown content..."
						class="w-full border-2 border-black dark:border-white px-3 py-2 text-sm focus:outline-none focus:shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] dark:focus:shadow-[4px_4px_0px_0px_rgba(255,255,255,1)] transition-all font-mono"
					></textarea>
					<p class="text-[10px] text-muted-foreground uppercase font-bold tracking-wide">
						✨ AI responses appear in the main conversation - copy & paste them here
					</p>
				</div>
			</div>

			<!-- Footer -->
			<div class="p-6 border-t-2 border-black dark:border-white bg-secondary/10 flex justify-end gap-3">
				<button 
					class="brutal-btn bg-white text-black"
					onclick={close}
					disabled={isSubmitting}
				>
					Cancel
				</button>
				<button 
					class="brutal-btn bg-primary text-primary-foreground flex items-center gap-2"
					disabled={!title.trim() || !content.trim() || !typeId || isSubmitting}
					onclick={handleSubmit}
				>
					{#if isSubmitting}
						<Loader2 class="w-4 h-4 animate-spin" />
						Saving...
					{:else}
						<Save class="w-4 h-4" />
						Save Item
					{/if}
				</button>
			</div>
		</div>
	</div>
{/if}
