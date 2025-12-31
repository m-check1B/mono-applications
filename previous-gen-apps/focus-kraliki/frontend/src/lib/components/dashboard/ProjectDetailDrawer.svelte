<script lang="ts">
	import { X, Calendar, CheckCircle2, Clock, TrendingUp, AlertCircle, MoreVertical, Trash2 } from 'lucide-svelte';
	import { projectsStore } from '$lib/stores/projects';
	import { fade, fly } from 'svelte/transition';

	interface Props {
		isOpen?: boolean;
		project?: any;
		onclose?: () => void;
	}

	let {
		isOpen = false,
		project = null,
		onclose
	}: Props = $props();

	let isLoadingProgress = $state(false);

	let progress = $derived($projectsStore.currentProjectProgress);

	$effect(() => {
		if (isOpen && project) {
			loadProgress();
		}
	});

	async function loadProgress() {
		isLoadingProgress = true;
		await projectsStore.getProjectProgress(project.id);
		isLoadingProgress = false;
	}

	function close() {
		onclose?.();
	}

	function handleDelete() {
		if (confirm('Are you sure you want to delete this project? This cannot be undone.')) {
			projectsStore.deleteProject(project.id);
			close();
		}
	}
</script>

{#if isOpen && project}
	<div 
		class="absolute inset-y-0 right-0 w-full md:w-[600px] bg-background border-l-2 border-black dark:border-white shadow-[-8px_0px_0px_0px_rgba(0,0,0,1)] dark:shadow-[-8px_0px_0px_0px_rgba(255,255,255,1)] z-40 flex flex-col"
		transition:fly={{ x: 100, duration: 300 }}
	>
		<!-- Header -->
		<div class="flex-shrink-0 p-6 border-b-2 border-black dark:border-white bg-secondary flex items-start justify-between">
			<div class="space-y-2">
				<div class="flex items-center gap-2">
					<span class="text-xs font-bold uppercase bg-primary text-primary-foreground px-2 py-0.5 border border-black dark:border-white">
						{project.status || 'Active'}
					</span>
					<span class="text-xs font-bold uppercase text-muted-foreground">
						Created {new Date(project.createdAt || Date.now()).toLocaleDateString()}
					</span>
				</div>
				<h2 class="text-2xl font-black uppercase tracking-tighter">{project.name}</h2>
			</div>
			<div class="flex items-center gap-2">
				<button 
					class="p-2 hover:bg-red-500 hover:text-white border border-transparent hover:border-black dark:hover:border-white transition-all"
					onclick={handleDelete}
					title="Delete Project"
				>
					<Trash2 class="w-5 h-5" />
				</button>
				<button 
					class="p-2 hover:bg-black/10 dark:hover:bg-white/10 border border-transparent hover:border-black dark:hover:border-white transition-all"
					onclick={close}
				>
					<X class="w-6 h-6" />
				</button>
			</div>
		</div>

		<!-- Content -->
		<div class="flex-1 overflow-y-auto p-6 space-y-8">
			<!-- Description -->
			<div class="brutal-card p-6 bg-white dark:bg-zinc-900">
				<h3 class="text-sm font-black uppercase text-muted-foreground mb-2">Description</h3>
				<p class="text-lg font-medium leading-relaxed">
					{project.description || 'No description provided for this project.'}
				</p>
			</div>

			<!-- Progress Stats -->
			<div>
				<h3 class="text-lg font-black uppercase tracking-tight mb-4 flex items-center gap-2">
					<TrendingUp class="w-5 h-5" />
					Progress Overview
				</h3>
				
				{#if isLoadingProgress}
					<div class="h-32 flex items-center justify-center border-2 border-black dark:border-white bg-secondary/10 animate-pulse">
						<span class="font-bold uppercase">Loading stats...</span>
					</div>
				{:else if progress}
					<div class="grid grid-cols-2 gap-4 mb-6">
						<div class="brutal-card p-4 flex flex-col items-center justify-center text-center">
							<span class="text-3xl font-black">{progress.total_tasks || 0}</span>
							<span class="text-xs font-bold uppercase text-muted-foreground">Total Tasks</span>
						</div>
						<div class="brutal-card p-4 flex flex-col items-center justify-center text-center bg-green-100 dark:bg-green-900/20">
							<span class="text-3xl font-black text-green-600 dark:text-green-400">{progress.completed_tasks || 0}</span>
							<span class="text-xs font-bold uppercase text-muted-foreground">Completed</span>
						</div>
						<div class="brutal-card p-4 flex flex-col items-center justify-center text-center bg-blue-100 dark:bg-blue-900/20">
							<span class="text-3xl font-black text-blue-600 dark:text-blue-400">{progress.in_progress_tasks || 0}</span>
							<span class="text-xs font-bold uppercase text-muted-foreground">In Progress</span>
						</div>
						<div class="brutal-card p-4 flex flex-col items-center justify-center text-center bg-orange-100 dark:bg-orange-900/20">
							<span class="text-3xl font-black text-orange-600 dark:text-orange-400">{progress.overdue_tasks || 0}</span>
							<span class="text-xs font-bold uppercase text-muted-foreground">Overdue</span>
						</div>
					</div>

					<!-- Progress Bar -->
					<div class="space-y-2">
						<div class="flex justify-between text-sm font-bold uppercase">
							<span>Completion</span>
							<span>{Math.round(progress.completion_percentage || 0)}%</span>
						</div>
						<div class="h-4 w-full border-2 border-black dark:border-white bg-secondary p-0.5">
							<div 
								class="h-full bg-primary transition-all duration-500"
								style="width: {progress.completion_percentage || 0}%"
							></div>
						</div>
					</div>
				{:else}
					<div class="p-6 border-2 border-black dark:border-white border-dashed text-center">
						<p class="font-bold uppercase text-muted-foreground">No progress data available</p>
					</div>
				{/if}
			</div>

			<!-- Recent Activity Placeholder (could be real later) -->
			<div>
				<h3 class="text-lg font-black uppercase tracking-tight mb-4 flex items-center gap-2">
					<Clock class="w-5 h-5" />
					Recent Activity
				</h3>
				<div class="space-y-3">
					{#if progress && progress.recent_tasks && progress.recent_tasks.length > 0}
						{#each progress.recent_tasks as task}
							<div class="flex items-center justify-between p-3 border-2 border-black dark:border-white bg-white dark:bg-zinc-900">
								<span class="font-bold truncate flex-1 mr-4">{task.title}</span>
								<span class="text-xs font-bold uppercase px-2 py-1 bg-secondary border border-black dark:border-white">
									{task.status}
								</span>
							</div>
						{/each}
					{:else}
						<div class="p-4 border-2 border-black dark:border-white border-dashed text-center text-sm font-bold text-muted-foreground">
							No recent activity
						</div>
					{/if}
				</div>
			</div>
		</div>
	</div>
{/if}
