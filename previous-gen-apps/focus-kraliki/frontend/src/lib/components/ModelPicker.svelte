<script lang="ts">
	import { onMount } from 'svelte';
	import { api } from '$lib/api/client';
	import { logger } from '$lib/utils/logger';
	import { ChevronDown, Sparkles, Zap, DollarSign } from 'lucide-svelte';

	interface Props {
		selectedModel?: string;
		onModelChange?: (modelId: string) => void;
		compact?: boolean;
	}

	let {
		selectedModel = $bindable('google/gemini-3-flash-preview'),
		onModelChange = () => {},
		compact = false
	}: Props = $props();

	interface AIModel {
		id: string;
		name: string;
		provider: string;
		description: string;
		inputPrice: number;
		outputPrice: number;
		contextWindow: number;
		recommended?: boolean;
		features: string[];
	}

	let models = $state<AIModel[]>([]);
	let isOpen = $state(false);
	let isLoading = $state(false);
	const dropdownRootClass = 'model-picker-root';

	let selectedModelData = $derived(models.find((m) => m.id === selectedModel));

	onMount(async () => {
		await loadModels();
	});

	async function loadModels() {
		isLoading = true;
		try {
			const response: any = await api.pricing.listModels();
			models = response.models || [];
		} catch (error) {
			logger.error('Failed to load models', error);
			// Fallback to default models
			models = [
				{
					id: 'google/gemini-3-flash-preview',
					name: 'Gemini 3 Flash',
					provider: 'Google',
					description: 'Multimodal general-purpose model',
					inputPrice: 0.5,
					outputPrice: 3.0,
					contextWindow: 1048576,
					recommended: true,
					features: ['Multimodal', 'Fast', 'Huge context']
				},
				{
					id: 'z-ai/glm-4.7',
					name: 'GLM-4.7',
					provider: 'Z.AI',
					description: 'Best-in-class coding and reasoning',
					inputPrice: 0.6,
					outputPrice: 2.2,
					contextWindow: 202752,
					recommended: true,
					features: ['Coding', 'Reasoning', 'SWE-bench 73.8%']
				},
				{
					id: 'meta-llama/llama-4-scout',
					name: 'Llama 4 Scout',
					provider: 'Groq',
					description: 'Real-time ultra-low latency',
					inputPrice: 0.11,
					outputPrice: 0.34,
					contextWindow: 327680,
					recommended: false,
					features: ['275+ t/s', 'Realtime', 'Low cost']
				},
				{
					id: 'meta-llama/llama-3.3-70b-instruct',
					name: 'Llama 3.3 70B',
					provider: 'Groq',
					description: 'Quality + speed balance',
					inputPrice: 0.59,
					outputPrice: 0.79,
					contextWindow: 131072,
					recommended: false,
					features: ['Balanced', 'Fast', 'Large model']
				},
				{
					id: 'deepseek/deepseek-v3.2',
					name: 'DeepSeek V3.2',
					provider: 'DeepSeek',
					description: 'Budget option for bulk processing',
					inputPrice: 0.22,
					outputPrice: 0.32,
					contextWindow: 163840,
					recommended: false,
					features: ['Budget', 'Bulk', 'Efficient']
				}
			];
		} finally {
			isLoading = false;
		}
	}

	function handleSelect(modelId: string) {
		selectedModel = modelId;
		isOpen = false;
		onModelChange(modelId);
	}

	function toggleDropdown() {
		isOpen = !isOpen;
	}

	function formatPrice(price: number): string {
		return price < 1 ? `$${price.toFixed(2)}` : `$${price.toFixed(0)}`;
	}

	function handleWindowClick(event: MouseEvent) {
		if (!isOpen) return;
		const target = event.target;
		if (target instanceof Element && !target.closest(`.${dropdownRootClass}`)) {
			isOpen = false;
		}
	}
</script>

{#if compact}
	<!-- Compact Mode (for chat sidebars) -->
	<div class={`relative ${dropdownRootClass}`}>
		<button
			onclick={toggleDropdown}
			class="w-full flex items-center justify-between gap-2 px-3 py-2 text-sm bg-accent text-accent-foreground border-2 border-black dark:border-white hover:translate-x-[2px] hover:translate-y-[2px] hover:shadow-none shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] dark:shadow-[4px_4px_0px_0px_rgba(255,255,255,1)] transition-all"
		>
			<div class="flex items-center gap-2 min-w-0">
				<Sparkles class="w-3 h-3 flex-shrink-0 text-primary" />
				<span class="truncate font-bold uppercase">{selectedModelData?.name || 'Select Model'}</span>
			</div>
			<ChevronDown class="w-4 h-4 flex-shrink-0 {isOpen ? 'rotate-180' : ''} transition-transform" />
		</button>

		{#if isOpen}
			<div
				class="absolute z-50 mt-2 w-full min-w-[280px] bg-card border-2 border-black dark:border-white shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] dark:shadow-[8px_8px_0px_0px_rgba(255,255,255,1)] max-h-[400px] overflow-y-auto"
			>
				{#each models as model (model.id)}
					<button
						onclick={() => handleSelect(model.id)}
						class="w-full text-left px-3 py-3 hover:bg-accent transition-colors border-b border-black dark:border-white last:border-b-0 {selectedModel ===
						model.id
							? 'bg-accent text-accent-foreground'
							: ''}"
					>
						<div class="flex items-start justify-between gap-2">
							<div class="min-w-0 flex-1">
								<div class="font-bold text-sm flex items-center gap-2 uppercase">
									{model.name}
									{#if model.recommended}
										<span
											class="text-[10px] px-1.5 py-0.5 bg-primary text-primary-foreground border border-black dark:border-white"
										>
											REC
										</span>
									{/if}
								</div>
								<div class="text-xs text-muted-foreground truncate font-medium">{model.description}</div>
							</div>
							<div class="text-xs text-muted-foreground flex items-center gap-1 flex-shrink-0 font-mono">
								<DollarSign class="w-3 h-3" />
								{formatPrice(model.inputPrice)}
							</div>
						</div>
					</button>
				{/each}
			</div>
		{/if}
	</div>
{:else}
	<!-- Full Mode (for settings pages) -->
	<div class="space-y-4">
		<div class="flex items-center justify-between">
			<span class="text-sm font-black uppercase">AI Model</span>
			{#if selectedModelData}
				<span class="text-xs text-muted-foreground font-mono">
					{formatPrice(selectedModelData.inputPrice)}/1M input •
					{formatPrice(selectedModelData.outputPrice)}/1M output
				</span>
			{/if}
		</div>

		<div class="grid grid-cols-1 gap-3">
			{#each models as model (model.id)}
				<button
					onclick={() => handleSelect(model.id)}
					class="text-left p-4 bg-card border-2 transition-all shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] dark:shadow-[4px_4px_0px_0px_rgba(255,255,255,1)] hover:translate-x-[2px] hover:translate-y-[2px] hover:shadow-none {selectedModel ===
					model.id
						? 'border-primary bg-primary/5'
						: 'border-black dark:border-white'}"
				>
					<div class="flex items-start justify-between gap-3">
						<div class="flex-1 min-w-0">
							<div class="flex items-center gap-2 mb-1">
								<h4 class="font-black uppercase">{model.name}</h4>
								{#if model.recommended}
									<span
										class="text-xs px-2 py-0.5 bg-primary text-primary-foreground border border-black dark:border-white flex items-center gap-1 font-bold uppercase"
									>
										<Zap class="w-3 h-3" />
										Recommended
									</span>
								{/if}
							</div>
							<p class="text-sm text-muted-foreground mb-2 font-medium">{model.description}</p>
							<div class="flex flex-wrap gap-1.5">
								{#each model.features as feature}
									<span class="text-xs px-2 py-0.5 bg-secondary border border-black dark:border-white font-bold uppercase">{feature}</span>
								{/each}
							</div>
						</div>
						<div class="text-right flex-shrink-0">
							<div class="text-sm font-bold text-muted-foreground mb-1 uppercase">{model.provider}</div>
							<div class="text-xs text-muted-foreground font-mono">
								{(model.contextWindow / 1000).toFixed(0)}K context
							</div>
						</div>
					</div>
				</button>
			{/each}
		</div>
	</div>
{/if}

<svelte:window onclick={handleWindowClick} />
