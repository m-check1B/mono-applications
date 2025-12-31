<script lang="ts">
	import { onMount } from 'svelte';
	import { X, LayoutTemplate, ArrowRight, Loader2 } from 'lucide-svelte';
	import { projectsStore } from '$lib/stores/projects';

	interface Props {
		isOpen?: boolean;
		onclose?: () => void;
		oncreated?: (project: any) => void;
	}

	let {
		isOpen = false,
		onclose,
		oncreated
	}: Props = $props();

	let selectedTemplateId = $state<string | null>(null);
	let customName = $state('');
	let isSubmitting = $state(false);

	let templates = $derived($projectsStore.templates);
	let isLoading = $derived($projectsStore.isLoading);

	onMount(() => {
		projectsStore.loadTemplates();
	});

	function close() {
		onclose?.();
		selectedTemplateId = null;
		customName = '';
	}

	async function handleSubmit() {
		if (!selectedTemplateId) return;

		isSubmitting = true;
		const result = await projectsStore.createFromTemplate(selectedTemplateId, customName || undefined);
		isSubmitting = false;

		if (result.success) {
			close();
			oncreated?.(result.project);
		}
	}
</script>

{#if isOpen}
	<div class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
		<div class="w-full max-w-2xl bg-background border-2 border-black dark:border-white shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] dark:shadow-[8px_8px_0px_0px_rgba(255,255,255,1)] flex flex-col max-h-[90vh]">
			<!-- Header -->
			<div class="flex items-center justify-between p-6 border-b-2 border-black dark:border-white bg-secondary">
				<div class="flex items-center gap-3">
					<LayoutTemplate class="w-6 h-6" />
					<h2 class="text-xl font-black uppercase tracking-tighter">Start from Template</h2>
				</div>
				<button onclick={close} class="p-1 hover:bg-black/10 dark:hover:bg-white/10 transition-colors">
					<X class="w-6 h-6" />
				</button>
			</div>

			<!-- Content -->
			<div class="flex-1 overflow-y-auto p-6 space-y-6">
				<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
					{#each templates as template}
						<button
							class="text-left p-4 border-2 transition-all relative group {selectedTemplateId === template.id ? 'border-primary bg-primary/5' : 'border-black dark:border-white hover:translate-x-[2px] hover:translate-y-[2px] hover:shadow-none'}"
							onclick={() => selectedTemplateId = template.id}
						>
							<div class="flex items-start justify-between mb-2">
								<span class="text-xs font-bold uppercase bg-secondary px-2 py-0.5 border border-black dark:border-white">{template.category}</span>
								{#if selectedTemplateId === template.id}
									<div class="w-4 h-4 bg-primary rounded-full border border-black dark:border-white"></div>
								{/if}
							</div>
							<h3 class="font-black uppercase tracking-tight mb-1">{template.name}</h3>
							<p class="text-sm text-muted-foreground line-clamp-2 mb-3">{template.description}</p>
							<div class="flex items-center gap-3 text-xs font-bold text-muted-foreground">
								<span>{template.taskCount} Tasks</span>
								<span>•</span>
								<span>{template.estimatedDuration}</span>
							</div>
						</button>
					{/each}
				</div>

				{#if selectedTemplateId}
					<div class="space-y-2 pt-4 border-t-2 border-black dark:border-white">
						<label for="custom-name" class="text-xs font-black uppercase">Project Name (Optional)</label>
						<input
							id="custom-name"
							type="text"
							bind:value={customName}
							placeholder="My Awesome Project"
							class="w-full border-2 border-black dark:border-white px-3 py-2 text-sm focus:outline-none focus:shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] dark:focus:shadow-[4px_4px_0px_0px_rgba(255,255,255,1)] transition-all font-bold"
						/>
					</div>
				{/if}
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
					disabled={!selectedTemplateId || isSubmitting}
					onclick={handleSubmit}
				>
					{#if isSubmitting}
						<Loader2 class="w-4 h-4 animate-spin" />
						Creating...
					{:else}
						Create Project
						<ArrowRight class="w-4 h-4" />
					{/if}
				</button>
			</div>
		</div>
	</div>
{/if}
