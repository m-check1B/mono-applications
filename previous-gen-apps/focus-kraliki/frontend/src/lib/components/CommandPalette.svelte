<script lang="ts">
	import { onMount } from "svelte";
	import { contextPanelStore } from "$lib/stores/contextPanel";
	import { goto } from "$app/navigation";
	import {
		Search,
		CheckSquare,
		Book,
		Calendar,
		Folder,
		Settings,
		BarChart3,
		Clock,
		Sparkles,
		Workflow,
		User,
		Shield,
		Database,
	} from "lucide-svelte";

	let isOpen = $state(false);
	let searchQuery = $state("");
	let selectedIndex = $state(0);
	let searchInput: HTMLInputElement | undefined = $state();

	interface Command {
		id: string;
		label: string;
		icon: any;
		action: () => void;
		keywords: string[];
		category: "panel" | "navigation" | "settings";
	}

	const commands: Command[] = [
		// Panels
		{
			id: "open-tasks",
			label: "Open Tasks",
			icon: CheckSquare,
			action: () => contextPanelStore.open("tasks"),
			keywords: ["tasks", "todo", "action items", "work"],
			category: "panel",
		},
		{
			id: "open-knowledge",
			label: "Open Knowledge Base",
			icon: Book,
			action: () => contextPanelStore.open("knowledge"),
			keywords: ["knowledge", "notes", "documents", "resources"],
			category: "panel",
		},
		{
			id: "open-calendar",
			label: "Open Calendar",
			icon: Calendar,
			action: () => contextPanelStore.open("calendar"),
			keywords: ["calendar", "events", "schedule", "appointments"],
			category: "panel",
		},
		{
			id: "open-projects",
			label: "Open Projects",
			icon: Folder,
			action: () => contextPanelStore.open("projects"),
			keywords: ["projects", "initiatives", "work"],
			category: "panel",
		},
		{
			id: "open-analytics",
			label: "Open Analytics",
			icon: BarChart3,
			action: () => contextPanelStore.open("analytics"),
			keywords: ["analytics", "stats", "metrics", "reports"],
			category: "panel",
		},
		{
			id: "open-time",
			label: "Open Time Tracking",
			icon: Clock,
			action: () => contextPanelStore.open("time"),
			keywords: ["time", "tracking", "timer", "hours"],
			category: "panel",
		},
		{
			id: "open-n8n",
			label: "Workflow Orchestration (n8n)",
			icon: Workflow,
			action: () => contextPanelStore.open("n8n"),
			keywords: ["workflow", "automation", "n8n", "orchestration"],
			category: "panel",
		},
		{
			id: "open-voice",
			label: "Open Voice by Kraliki Remote",
			icon: Sparkles,
			action: () => contextPanelStore.open("voice"),
			keywords: ["voice", "remote", "mobile", "scenario", "call center"],
			category: "panel",
		},
		{
			id: "open-shadow",
			label: "Open Shadow Work",
			icon: Sparkles,
			action: () => contextPanelStore.open("shadow"),
			keywords: ["shadow", "psychology", "insights", "analysis"],
			category: "panel",
		},
		{
			id: "open-infra",
			label: "Open Infrastructure",
			icon: Database,
			action: () => contextPanelStore.open("infra"),
			keywords: ["infrastructure", "system", "admin"],
			category: "panel",
		},
		{
			id: "open-settings",
			label: "Open Settings",
			icon: Settings,
			action: () => contextPanelStore.open("settings"),
			keywords: ["settings", "preferences", "config", "configuration"],
			category: "settings",
		},
		// Navigation
		{
			id: "go-dashboard",
			label: "Go to Dashboard",
			icon: Sparkles,
			action: () => goto("/dashboard"),
			keywords: ["dashboard", "home", "main"],
			category: "navigation",
		},
		{
			id: "go-voice",
			label: "Go to Voice",
			icon: Sparkles,
			action: () => goto("/dashboard/voice"),
			keywords: ["voice", "audio", "speech"],
			category: "navigation",
		},
	];

	let filteredCommands = $derived(
		searchQuery.trim()
			? commands.filter((cmd) => {
					const query = searchQuery.toLowerCase();
					return (
						cmd.label.toLowerCase().includes(query) ||
						cmd.keywords.some((kw) =>
							kw.toLowerCase().includes(query),
						)
					);
				})
			: commands,
	);

	// Reset selected index when filtered commands change
	$effect(() => {
		if (filteredCommands) {
			selectedIndex = Math.min(
				selectedIndex,
				filteredCommands.length - 1,
			);
		}
	});

	function handleKeydown(event: KeyboardEvent) {
		// Open/close with Ctrl+K or Cmd+K
		if ((event.ctrlKey || event.metaKey) && event.key === "k") {
			event.preventDefault();
			togglePalette();
			return;
		}

		if (!isOpen) return;

		// Close with Escape
		if (event.key === "Escape") {
			event.preventDefault();
			close();
			return;
		}

		// Navigate with Arrow keys
		if (event.key === "ArrowDown") {
			event.preventDefault();
			selectedIndex = Math.min(
				selectedIndex + 1,
				filteredCommands.length - 1,
			);
			return;
		}

		if (event.key === "ArrowUp") {
			event.preventDefault();
			selectedIndex = Math.max(selectedIndex - 1, 0);
			return;
		}

		// Execute with Enter
		if (event.key === "Enter") {
			event.preventDefault();
			executeSelected();
			return;
		}
	}

	function togglePalette() {
		isOpen = !isOpen;
		if (isOpen) {
			searchQuery = "";
			selectedIndex = 0;
			// Focus input after DOM update
			setTimeout(() => searchInput?.focus(), 10);
		}
	}

	function close() {
		isOpen = false;
		searchQuery = "";
		selectedIndex = 0;
	}

	function executeSelected() {
		if (filteredCommands[selectedIndex]) {
			filteredCommands[selectedIndex].action();
			close();
		}
	}

	function executeCommand(cmd: Command) {
		cmd.action();
		close();
	}

	onMount(() => {
		document.addEventListener("keydown", handleKeydown);
		return () => {
			document.removeEventListener("keydown", handleKeydown);
		};
	});
</script>

{#if isOpen}
	<!-- Backdrop -->
	<div
		class="fixed inset-0 bg-black/40 z-50 transition-opacity duration-300"
		onclick={close}
		onkeydown={(e) => e.key === "Enter" && close()}
		role="button"
		tabindex="-1"
		aria-label="Close command palette"
	></div>

	<!-- Command Palette -->
	<div
		class="fixed top-[20%] left-1/2 -translate-x-1/2 w-full max-w-2xl z-50 p-4"
	>
		<div
			class="bg-background border-2 border-black dark:border-white shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] dark:shadow-[8px_8px_0px_0px_rgba(255,255,255,1)]"
		>
			<!-- Search Input -->
			<div class="p-4 border-b-2 border-black dark:border-white">
				<div class="relative">
					<Search
						class="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground"
					/>
					<input
						bind:this={searchInput}
						bind:value={searchQuery}
						type="text"
						placeholder="TYPE A COMMAND OR SEARCH..."
						class="w-full pl-11 pr-4 py-3 bg-white dark:bg-black border-2 border-black dark:border-white focus:outline-none focus:shadow-[4px_4px_0px_0px_var(--color-terminal-green)] transition-all font-display uppercase text-sm placeholder:font-mono placeholder:text-muted-foreground"
					/>
				</div>
			</div>

			<!-- Commands List -->
			<div class="max-h-[400px] overflow-y-auto">
				{#if filteredCommands.length === 0}
					<div class="p-8 text-center">
						<p
							class="text-sm font-bold uppercase text-muted-foreground"
						>
							No commands found
						</p>
					</div>
				{:else}
					{#each filteredCommands as cmd, index (cmd.id)}
						{@const CmdIcon = cmd.icon}
						<button
							class="w-full p-4 flex items-center gap-4 text-left hover:bg-secondary transition-colors border-b-2 border-black dark:border-white last:border-b-0 {selectedIndex ===
							index
								? 'bg-black text-white dark:bg-white dark:text-black'
								: ''}"
							onclick={() => executeCommand(cmd)}
							onmouseenter={() => (selectedIndex = index)}
						>
							<div
								class="p-2 border-2 border-black dark:border-white bg-secondary flex-shrink-0 {selectedIndex ===
								index
									? 'bg-white text-black dark:bg-black dark:text-white'
									: ''}"
							>
								<CmdIcon class="w-5 h-5" />
							</div>
							<div class="flex-1 min-w-0">
								<p
									class="font-black uppercase text-sm tracking-tight"
								>
									{cmd.label}
								</p>
								<p
									class="text-xs font-bold text-muted-foreground uppercase mt-0.5 {selectedIndex ===
									index
										? 'text-white/70 dark:text-black/70'
										: ''}"
								>
									{cmd.category}
								</p>
							</div>
							{#if selectedIndex === index}
								<span
									class="text-xs font-mono font-bold px-2 py-1 border border-white dark:border-black"
									>Enter</span
								>
							{/if}
						</button>
					{/each}
				{/if}
			</div>

			<!-- Footer -->
			<div
				class="p-3 border-t-2 border-black dark:border-white bg-secondary/20 flex items-center justify-between text-[10px] font-bold uppercase text-muted-foreground"
			>
				<div class="flex items-center gap-4">
					<span class="flex items-center gap-1">
						<kbd
							class="px-1.5 py-0.5 border border-black dark:border-white bg-background"
							>Up/Down</kbd
						>
						Navigate
					</span>
					<span class="flex items-center gap-1">
						<kbd
							class="px-1.5 py-0.5 border border-black dark:border-white bg-background"
							>Enter</kbd
						>
						Select
					</span>
					<span class="flex items-center gap-1">
						<kbd
							class="px-1.5 py-0.5 border border-black dark:border-white bg-background"
							>Esc</kbd
						>
						Close
					</span>
				</div>
				<span>Ctrl+K to open</span>
			</div>
		</div>
	</div>
{/if}
