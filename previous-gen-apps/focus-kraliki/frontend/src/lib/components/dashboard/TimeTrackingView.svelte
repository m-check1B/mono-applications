<script lang="ts">
    import { onMount, onDestroy } from 'svelte';
    import { timeStore } from '$lib/stores/time';
    import { projectsStore } from '$lib/stores/projects';
    import { Play, Square, Trash2, Clock, DollarSign, Briefcase } from 'lucide-svelte';

    let description = $state('');
    let selectedProjectId = $state('');
    let isBillable = $state(false);
    let elapsedTime = $state('00:00:00');
    let timerInterval = $state<any>(null);

    let activeEntry = $derived($timeStore.activeEntry);

    onMount(() => {
        timeStore.loadEntries();
        timeStore.loadActiveEntry();
        projectsStore.loadProjects();
    });

    onDestroy(() => {
        if (timerInterval) clearInterval(timerInterval);
    });

    // Update elapsed time counter
    $effect(() => {
        if (activeEntry) {
            if (timerInterval) clearInterval(timerInterval);
            updateElapsed();
            timerInterval = setInterval(updateElapsed, 1000);
        } else {
            if (timerInterval) clearInterval(timerInterval);
            elapsedTime = '00:00:00';
        }
    });

    function updateElapsed() {
        if (!activeEntry) return;
        const start = new Date(activeEntry.startTime).getTime();
        const now = new Date().getTime();
        const diff = Math.floor((now - start) / 1000);
        
        const h = Math.floor(diff / 3600).toString().padStart(2, '0');
        const m = Math.floor((diff % 3600) / 60).toString().padStart(2, '0');
        const s = (diff % 60).toString().padStart(2, '0');
        elapsedTime = `${h}:${m}:${s}`;
    }

    async function handleStart() {
        if (!description) return;
        
        const result = await timeStore.startTimer({
            description,
            projectId: selectedProjectId || undefined,
            billable: isBillable
        });

        if (result.success) {
            description = '';
            selectedProjectId = '';
            isBillable = false;
        }
    }

    async function handleStop() {
        if (activeEntry) {
            await timeStore.stopTimer(activeEntry.id);
        }
    }

    async function handleDelete(entryId: string) {
        if (confirm('Delete this time entry?')) {
            await timeStore.deleteEntry(entryId);
        }
    }

    function formatDuration(seconds?: number) {
        if (!seconds) return '00:00:00';
        const h = Math.floor(seconds / 3600).toString().padStart(2, '0');
        const m = Math.floor((seconds % 3600) / 60).toString().padStart(2, '0');
        const s = (seconds % 60).toString().padStart(2, '0');
        return `${h}:${m}:${s}`;
    }

    function formatTime(dateStr: string) {
        return new Date(dateStr).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }
</script>

<div class="space-y-6">
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
            <h2 class="text-3xl font-black uppercase tracking-tighter">Time Tracking</h2>
            <p class="text-muted-foreground font-mono text-sm mt-1">Track your work hours and billable time.</p>
        </div>
    </div>

    <!-- Timer Control -->
    <div class="brutal-card bg-white dark:bg-black p-6 border-2 border-black dark:border-white shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] dark:shadow-[8px_8px_0px_0px_rgba(255,255,255,1)]">
        {#if activeEntry}
            <div class="flex flex-col md:flex-row items-center justify-between gap-6">
                <div class="flex-1 text-center md:text-left">
                    <p class="text-sm font-bold uppercase text-muted-foreground mb-1">Current Task</p>
                    <h3 class="text-xl font-black uppercase">{activeEntry.description || 'No description'}</h3>
                    {#if activeEntry.projectId}
                        {@const project = $projectsStore.projects.find(p => p.id === activeEntry.projectId)}
                        <div class="inline-block mt-2 px-2 py-1 bg-secondary border border-black dark:border-white text-xs font-bold uppercase">
                            {project?.name || 'Unknown Project'}
                        </div>
                    {/if}
                </div>
                
                <div class="text-4xl font-mono font-black tracking-widest">
                    {elapsedTime}
                </div>

                <button
                    class="brutal-btn bg-red-500 text-white border-black w-full md:w-auto flex items-center justify-center gap-2 py-3 px-6"
                    onclick={handleStop}
                >
                    <Square class="w-5 h-5 fill-current" />
                    Stop Timer
                </button>
            </div>
        {:else}
            <div class="flex flex-col md:flex-row gap-4 items-end">
                <div class="flex-1 w-full space-y-2">
                    <label for="timeDescription" class="text-xs font-bold uppercase">Description</label>
                    <input
                        id="timeDescription"
                        type="text"
                        bind:value={description}
                        placeholder="What are you working on?"
                        class="w-full p-3 bg-secondary border-2 border-black dark:border-white font-mono text-sm focus:outline-none focus:ring-2 focus:ring-primary"
                    />
                </div>

                <div class="w-full md:w-64 space-y-2">
                    <label for="timeProject" class="text-xs font-bold uppercase">Project</label>
                    <select
                        id="timeProject"
                        bind:value={selectedProjectId}
                        class="w-full p-3 bg-white dark:bg-black border-2 border-black dark:border-white font-mono text-sm focus:outline-none focus:ring-2 focus:ring-primary appearance-none"
                    >
                        <option value="">No Project</option>
                        {#each $projectsStore.projects as project}
                            <option value={project.id}>{project.name}</option>
                        {/each}
                    </select>
                </div>

                <div class="flex items-center gap-2 pb-3">
                    <input
                        type="checkbox"
                        id="billable"
                        bind:checked={isBillable}
                        class="w-5 h-5 border-2 border-black dark:border-white rounded-none focus:ring-0 checked:bg-black dark:checked:bg-white"
                    />
                    <label for="billable" class="text-sm font-bold uppercase cursor-pointer select-none">Billable</label>
                </div>

                <button
                    class="brutal-btn bg-primary text-primary-foreground border-black w-full md:w-auto flex items-center justify-center gap-2 py-3 px-6"
                    onclick={handleStart}
                    disabled={!description}
                >
                    <Play class="w-5 h-5 fill-current" />
                    Start
                </button>
            </div>
        {/if}
    </div>

    <!-- Recent Entries -->
    <div class="space-y-4">
        <h3 class="text-xl font-black uppercase tracking-tight border-b-2 border-black dark:border-white pb-2">
            Recent Entries
        </h3>

        {#if $timeStore.isLoading && $timeStore.entries.length === 0}
            <div class="flex justify-center py-8">
                <div class="animate-spin w-8 h-8 border-4 border-black border-t-transparent rounded-full"></div>
            </div>
        {:else if $timeStore.entries.length === 0}
            <div class="text-center py-8 text-muted-foreground font-mono">
                No time entries found.
            </div>
        {:else}
            <div class="space-y-3">
                {#each $timeStore.entries as entry (entry.id)}
                    <div class="brutal-card p-4 bg-white dark:bg-black flex flex-col md:flex-row md:items-center justify-between gap-4 hover:translate-x-[2px] hover:translate-y-[2px] transition-transform">
                        <div class="flex-1">
                            <div class="flex items-center gap-2 mb-1">
                                <span class="font-bold uppercase">{entry.description || 'No description'}</span>
                                {#if entry.billable}
                                    <DollarSign class="w-3 h-3 text-green-600" />
                                {/if}
                            </div>
                            <div class="flex items-center gap-3 text-xs text-muted-foreground font-mono">
                                {#if entry.projectId}
                                    {@const project = $projectsStore.projects.find(p => p.id === entry.projectId)}
                                    <span class="flex items-center gap-1">
                                        <Briefcase class="w-3 h-3" />
                                        {project?.name || 'Unknown'}
                                    </span>
                                {/if}
                                <span class="flex items-center gap-1">
                                    <Clock class="w-3 h-3" />
                                    {formatTime(entry.startTime)} - {entry.endTime ? formatTime(entry.endTime) : 'Now'}
                                </span>
                            </div>
                        </div>

                        <div class="flex items-center justify-between md:justify-end gap-4">
                            <span class="font-mono font-black text-lg">
                                {formatDuration(entry.durationSeconds)}
                            </span>
                            <button
                                class="p-2 hover:text-red-500 transition-colors"
                                onclick={() => handleDelete(entry.id)}
                            >
                                <Trash2 class="w-4 h-4" />
                            </button>
                        </div>
                    </div>
                {/each}
            </div>
        {/if}
    </div>
</div>
