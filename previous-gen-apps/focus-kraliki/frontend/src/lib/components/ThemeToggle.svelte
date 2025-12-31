<script lang="ts">
	import { mode, setMode } from "mode-watcher";
	import { Sun, Moon, Monitor } from "lucide-svelte";

	let isOpen = $state(false);

	function toggleOpen() {
		isOpen = !isOpen;
	}

	function handleModeChange(newMode: "light" | "dark" | "system") {
		setMode(newMode);
		isOpen = false;
	}
</script>

<div class="relative">
	<button
		class="p-2 hover:bg-accent border-2 border-transparent hover:border-black dark:hover:border-white flex items-center justify-center"
		onclick={toggleOpen}
		title="Toggle Theme"
	>
		{#if $mode === "light"}
			<Sun class="w-5 h-5" />
		{:else if $mode === "dark"}
			<Moon class="w-5 h-5" />
		{:else}
			<Monitor class="w-5 h-5" />
		{/if}
	</button>

	{#if isOpen}
		<div
			class="absolute right-0 top-full mt-2 z-50 min-w-[160px] bg-background border-2 border-black dark:border-white shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] dark:shadow-[4px_4px_0px_0px_rgba(255,255,255,1)] flex flex-col p-1"
		>
			<button
				class="flex items-center gap-3 px-3 py-2 hover:bg-terminal-green hover:text-black text-xs font-display text-left uppercase transition-colors"
				onclick={() => handleModeChange("light")}
			>
				<Sun class="w-4 h-4" />
				Light
			</button>
			<button
				class="flex items-center gap-3 px-3 py-2 hover:bg-terminal-green hover:text-black text-xs font-display text-left uppercase transition-colors"
				onclick={() => handleModeChange("dark")}
			>
				<Moon class="w-4 h-4" />
				Dark
			</button>
			<button
				class="flex items-center gap-3 px-3 py-2 hover:bg-terminal-green hover:text-black text-xs font-display text-left uppercase transition-colors"
				onclick={() => handleModeChange("system")}
			>
				<Monitor class="w-4 h-4" />
				System
			</button>
		</div>
	{/if}
</div>
