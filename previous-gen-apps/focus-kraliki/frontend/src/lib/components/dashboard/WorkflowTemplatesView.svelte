<script lang="ts">
    import { onMount } from 'svelte';
    import { workflowStore } from '$lib/stores/workflow';
    import { Plus, Play, Trash2, Sparkles, Search, Filter, Clock, ArrowRight } from 'lucide-svelte';
    import { fade, slide } from 'svelte/transition';

    let searchQuery = $state('');
    let selectedCategory = $state('all');
    let isGenerating = $state(false);
    let generationPrompt = $state('');
    let showGenerateModal = $state(false);

    let filteredTemplates = $derived($workflowStore.templates.filter(t => {
        const matchesSearch = t.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                            t.description.toLowerCase().includes(searchQuery.toLowerCase());
        const matchesCategory = selectedCategory === 'all' || t.category === selectedCategory;
        return matchesSearch && matchesCategory;
    }));

    onMount(() => {
        workflowStore.loadTemplates();
        workflowStore.loadCategories();
    });

    async function handleGenerate() {
        if (!generationPrompt) return;
        isGenerating = true;
        const result = await workflowStore.generateTemplate(generationPrompt);
        isGenerating = false;
        if (result.success) {
            showGenerateModal = false;
            generationPrompt = '';
        }
    }

    async function handleExecute(templateId: string) {
        // For now, simple execution with defaults. 
        // In a real app, we'd show a configuration modal for start date, etc.
        if (confirm('Start this workflow? This will create tasks in your project.')) {
            const result = await workflowStore.executeWorkflow(templateId, {
                startDate: new Date().toISOString()
            });
            if (result.success) {
                alert('Workflow started successfully!');
            } else {
                alert('Failed to start workflow: ' + result.error);
            }
        }
    }

    async function handleDelete(templateId: string) {
        if (confirm('Are you sure you want to delete this template?')) {
            await workflowStore.deleteTemplate(templateId);
        }
    }
</script>

<div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
            <h2 class="text-3xl font-black uppercase tracking-tighter">Workflow Templates</h2>
            <p class="text-muted-foreground font-mono text-sm mt-1">Automate your processes with AI-generated workflows.</p>
        </div>
        <button 
            class="brutal-btn bg-black text-white dark:bg-white dark:text-black flex items-center gap-2"
            onclick={() => showGenerateModal = true}
        >
            <Sparkles class="w-4 h-4" />
            Generate New
        </button>
    </div>

    <!-- Filters -->
    <div class="flex flex-col md:flex-row gap-4">
        <div class="relative flex-1">
            <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <input
                type="text"
                bind:value={searchQuery}
                placeholder="Search templates..."
                class="w-full pl-9 pr-4 py-2 bg-white dark:bg-black border-2 border-black dark:border-white font-mono text-sm focus:outline-none focus:ring-0"
            />
        </div>
        <div class="flex gap-2 overflow-x-auto pb-2 md:pb-0">
            <button
                class="px-4 py-2 border-2 border-black dark:border-white text-sm font-bold uppercase whitespace-nowrap transition-all
                {selectedCategory === 'all' ? 'bg-black text-white dark:bg-white dark:text-black' : 'bg-white text-black dark:bg-black dark:text-white hover:bg-secondary'}"
                onclick={() => selectedCategory = 'all'}
            >
                All
            </button>
            {#each $workflowStore.categories as category}
                <button
                    class="px-4 py-2 border-2 border-black dark:border-white text-sm font-bold uppercase whitespace-nowrap transition-all
                    {selectedCategory === category ? 'bg-black text-white dark:bg-white dark:text-black' : 'bg-white text-black dark:bg-black dark:text-white hover:bg-secondary'}"
                    onclick={() => selectedCategory = category}
                >
                    {category}
                </button>
            {/each}
        </div>
    </div>

    <!-- Grid -->
    {#if $workflowStore.isLoading}
        <div class="flex items-center justify-center py-12">
            <div class="animate-spin w-8 h-8 border-4 border-black border-t-transparent rounded-full"></div>
        </div>
    {:else if filteredTemplates.length === 0}
        <div class="text-center py-12 border-2 border-dashed border-black/20 dark:border-white/20">
            <p class="text-muted-foreground font-mono">No templates found.</p>
        </div>
    {:else}
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {#each filteredTemplates as template (template.id)}
                <div class="brutal-card group flex flex-col h-full bg-white dark:bg-black p-6 transition-all hover:-translate-y-1 hover:shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] dark:hover:shadow-[8px_8px_0px_0px_rgba(255,255,255,1)]">
                    <div class="flex items-start justify-between mb-4">
                        <div class="px-2 py-1 bg-secondary border border-black dark:border-white text-xs font-bold uppercase">
                            {template.category}
                        </div>
                        {#if !template.isSystem}
                            <button 
                                class="text-muted-foreground hover:text-red-500 transition-colors"
                                onclick={() => handleDelete(template.id)}
                            >
                                <Trash2 class="w-4 h-4" />
                            </button>
                        {/if}
                    </div>

                    <h3 class="text-xl font-black uppercase leading-tight mb-2">{template.name}</h3>
                    <p class="text-sm text-muted-foreground line-clamp-3 mb-4 flex-1">
                        {template.description}
                    </p>

                    <div class="space-y-4">
                        <div class="flex items-center gap-4 text-xs font-mono border-t border-black/10 dark:border-white/10 pt-4">
                            <div class="flex items-center gap-1">
                                <Clock class="w-3 h-3" />
                                {template.totalEstimatedMinutes}m
                            </div>
                            <div class="flex items-center gap-1">
                                <ArrowRight class="w-3 h-3" />
                                {template.steps.length} steps
                            </div>
                        </div>

                        <button
                            class="w-full brutal-btn bg-primary text-primary-foreground flex items-center justify-center gap-2 py-2"
                            onclick={() => handleExecute(template.id)}
                        >
                            <Play class="w-4 h-4" />
                            Start Workflow
                        </button>
                    </div>
                </div>
            {/each}
        </div>
    {/if}
</div>

<!-- Generate Modal -->
{#if showGenerateModal}
    <div class="fixed inset-0 bg-black/80 z-50 flex items-center justify-center p-4 backdrop-blur-sm" transition:fade>
        <div class="brutal-card w-full max-w-lg bg-white dark:bg-black p-6 space-y-6" transition:slide>
            <div class="flex items-center justify-between">
                <h3 class="text-xl font-black uppercase">Generate Workflow</h3>
                <button onclick={() => showGenerateModal = false}>
                    <Trash2 class="w-5 h-5 rotate-45" /> <!-- Using Trash icon rotated as close icon for brutalist vibe -->
                </button>
            </div>

            <div class="space-y-2">
                <label for="generationPrompt" class="text-sm font-bold uppercase">Description</label>
                <textarea
                    id="generationPrompt"
                    bind:value={generationPrompt}
                    class="w-full h-32 p-3 bg-secondary border-2 border-black dark:border-white font-mono text-sm focus:outline-none focus:ring-2 focus:ring-primary resize-none"
                    placeholder="Describe the workflow you want to create (e.g., 'A content creation pipeline for YouTube videos including research, scripting, filming, and editing')"
                ></textarea>
            </div>

            <div class="flex justify-end gap-3">
                <button
                    class="brutal-btn bg-white text-black border-black"
                    onclick={() => showGenerateModal = false}
                >
                    Cancel
                </button>
                <button
                    class="brutal-btn bg-black text-white dark:bg-white dark:text-black flex items-center gap-2"
                    disabled={isGenerating || !generationPrompt}
                    onclick={handleGenerate}
                >
                    {#if isGenerating}
                        <div class="animate-spin w-4 h-4 border-2 border-current border-t-transparent rounded-full"></div>
                        Generating...
                    {:else}
                        <Sparkles class="w-4 h-4" />
                        Generate
                    {/if}
                </button>
            </div>
        </div>
    </div>
{/if}
