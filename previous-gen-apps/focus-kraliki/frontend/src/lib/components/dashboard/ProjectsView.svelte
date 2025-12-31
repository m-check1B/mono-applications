<script lang="ts">
	import { onMount } from 'svelte';
	import { Folder, MoreVertical, Calendar, CheckCircle2, Loader2 } from 'lucide-svelte';
	import { projectsStore } from '$lib/stores/projects';
	import ProjectDetailDrawer from './ProjectDetailDrawer.svelte';

	let showDetailDrawer = $state(false);
	let selectedProject: any = $state(null);

	let projects = $derived($projectsStore.projects);
	let isLoading = $derived($projectsStore.isLoading);

	onMount(() => {
		projectsStore.loadProjects();
	});

	function handleProjectClick(project: any) {
		selectedProject = project;
		showDetailDrawer = true;
	}
</script>

<div class="h-full flex flex-col relative overflow-hidden">
	<!-- Header -->
	<div class="flex-shrink-0 p-6 border-b-2 border-black dark:border-white bg-background z-10">
		<div class="flex items-center gap-3">
			<div class="p-2 border-2 border-black dark:border-white bg-secondary text-secondary-foreground">
				<Folder class="w-6 h-6" />
			</div>
			<div>
				<h2 class="text-2xl font-black uppercase tracking-tighter">Projects</h2>
				<p class="text-sm font-bold text-muted-foreground">Create via AI · Manage via gestures</p>
			</div>
		</div>
	</div>

	<!-- Content -->
	<div class="flex-1 overflow-y-auto p-6">
		{#if isLoading && projects.length === 0}
			<div class="h-full flex items-center justify-center">
				<Loader2 class="w-8 h-8 animate-spin" />
			</div>
		{:else if projects.length === 0}
			<div class="h-full flex flex-col items-center justify-center text-center space-y-4 opacity-60">
				<Folder class="w-16 h-16 text-muted-foreground" />
				<p class="text-lg font-bold uppercase text-muted-foreground">No projects yet</p>
				<p class="text-sm text-muted-foreground">Ask the AI to create a project</p>
			</div>
		{:else}
			<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
				{#each projects as project}
					<button
						class="brutal-card p-0 flex flex-col h-full hover:translate-x-[4px] hover:translate-y-[4px] hover:shadow-none transition-all cursor-pointer group text-left w-full"
						onclick={() => handleProjectClick(project)}
					>
						<div class="p-5 flex-1 space-y-4 w-full">
							<div class="flex items-start justify-between w-full">
								<div class="space-y-1">
									<h3 class="text-lg font-black uppercase tracking-tight group-hover:underline decoration-2">{project.name}</h3>
									<span class="inline-block px-2 py-0.5 text-xs font-bold uppercase border border-black dark:border-white bg-secondary">
										{project.status || 'Active'}
									</span>
								</div>
								<div class="p-1 hover:bg-accent border border-transparent hover:border-black dark:hover:border-white transition-colors">
									<MoreVertical class="w-4 h-4" />
								</div>
							</div>
							<p class="text-sm font-medium text-muted-foreground line-clamp-2">
								{project.description || 'No description provided.'}
							</p>
						</div>
						<div class="p-4 border-t-2 border-black dark:border-white bg-secondary/10 flex items-center justify-between text-xs font-bold uppercase text-muted-foreground w-full">
							<div class="flex items-center gap-2">
								<Calendar class="w-3.5 h-3.5" />
								<span>{new Date(project.createdAt || Date.now()).toLocaleDateString()}</span>
							</div>
							<div class="flex items-center gap-2">
								<CheckCircle2 class="w-3.5 h-3.5" />
								<span>{project.taskCount || 0} Tasks</span>
							</div>
						</div>
					</button>
				{/each}
			</div>
		{/if}
	</div>

	<ProjectDetailDrawer
		isOpen={showDetailDrawer}
		project={selectedProject}
		onclose={() => showDetailDrawer = false}
	/>
</div>
