<script lang="ts">
	import { knowledgeStore, type KnowledgeItem } from '$lib/stores/knowledge';
	import { X } from 'lucide-svelte';

	interface Props {
		open?: boolean;
		item?: KnowledgeItem | null;
		onClose?: () => void;
		defaultTypeId?: string | null;
	}

	let {
		open = false,
		item = null,
		onClose = () => {},
		defaultTypeId = null
	}: Props = $props();

	let itemTypes = $derived($knowledgeStore.itemTypes);

	let formData = $state({
		typeId: '',
		title: '',
		content: '',
		completed: false
	});

	let isPending = $state(false);

	$effect(() => {
		if (open && item) {
			formData = {
				typeId: item.typeId,
				title: item.title,
				content: item.content,
				completed: item.completed || false
			};
		} else if (open && !item && itemTypes.length > 0) {
			formData = {
				typeId: defaultTypeId || itemTypes[0]?.id || '',
				title: '',
				content: '',
				completed: false
			};
		}
	});

	function handleClose() {
		formData = {
			typeId: itemTypes[0]?.id || '',
			title: '',
			content: '',
			completed: false
		};
		onClose?.();
	}

	async function handleSubmit() {
		if (!formData.title.trim() || !formData.content.trim()) return;

		isPending = true;

		let result;
		if (item) {
			result = await knowledgeStore.updateKnowledgeItem(item.id, formData);
		} else {
			result = await knowledgeStore.createKnowledgeItem(formData);
		}

		isPending = false;

		if (result.success) {
			handleClose();
		}
	}
</script>

{#if open}
	<div class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
		<div class="bg-card border border-border rounded-lg max-w-2xl w-full p-6">
			<div class="flex items-center justify-between mb-6">
				<h2 class="text-2xl font-bold">{item ? 'Edit Item' : 'Create Item'}</h2>
				<button onclick={handleClose} class="p-2 hover:bg-accent rounded-md transition-colors">
					<X class="w-5 h-5" />
				</button>
			</div>

			<form onsubmit={(e: Event) => { e.preventDefault(); handleSubmit(); }} class="space-y-4">
				<div class="space-y-2">
					<label for="typeId" class="text-sm font-medium">Type</label>
					<select
						id="typeId"
						bind:value={formData.typeId}
						required
						class="w-full px-3 py-2 bg-background border border-input rounded-md focus:outline-none focus:ring-2 focus:ring-ring"
					>
						{#each itemTypes as type (type.id)}
							<option value={type.id}>{type.name}</option>
						{/each}
					</select>
				</div>

				<div class="space-y-2">
					<label for="title" class="text-sm font-medium">Title</label>
					<input
						id="title"
						type="text"
						bind:value={formData.title}
						placeholder="Enter title"
						required
						class="w-full px-3 py-2 bg-background border border-input rounded-md focus:outline-none focus:ring-2 focus:ring-ring"
					/>
				</div>

				<div class="space-y-2">
					<label for="content" class="text-sm font-medium">Content</label>
					<textarea
						id="content"
						bind:value={formData.content}
						placeholder="Enter content"
						required
						rows="6"
						class="w-full px-3 py-2 bg-background border border-input rounded-md focus:outline-none focus:ring-2 focus:ring-ring resize-none"
					></textarea>
				</div>

				<div class="flex gap-2 justify-end pt-4">
					<button
						type="button"
						onclick={handleClose}
						disabled={isPending}
						class="px-4 py-2 bg-accent text-accent-foreground rounded-md hover:bg-accent/80 disabled:opacity-50 transition-colors"
					>
						Cancel
					</button>
					<button
						type="submit"
						disabled={isPending || !formData.title.trim() || !formData.content.trim()}
						class="px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
					>
						{isPending ? 'Saving...' : item ? 'Update' : 'Create'}
					</button>
				</div>
			</form>
		</div>
	</div>
{/if}
