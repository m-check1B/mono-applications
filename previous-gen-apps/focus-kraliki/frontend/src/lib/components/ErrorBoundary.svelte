<script lang="ts">
	import { onMount, onDestroy, type Snippet } from "svelte";
	import { browser } from "$app/environment";
	import { AlertTriangle, RefreshCcw } from "lucide-svelte";
	import { logger } from "$lib/utils/logger";

	interface Props {
		fallback?: string;
		showDetails?: boolean;
		children: Snippet;
	}

	let {
		fallback = "An error occurred",
		showDetails = false,
		children,
	}: Props = $props();

	let error: Error | null = $state(null);
	let errorInfo = $state("");
	let hasError = $state(false);

	function handleError(event: ErrorEvent) {
		error = event.error;
		errorInfo = event.error?.stack || "";
		hasError = true;
		logger.error("ErrorBoundary caught error", event.error);
		event.preventDefault();
	}

	function handleRejection(event: PromiseRejectionEvent) {
		error = event.reason;
		errorInfo = event.reason?.stack || "";
		hasError = true;
		logger.error("ErrorBoundary caught rejection", event.reason);
		event.preventDefault();
	}

	function reset() {
		hasError = false;
		error = null;
		errorInfo = "";
	}

	function reload() {
		if (browser && typeof window !== 'undefined') {
			window.location.reload();
		}
	}

	onMount(() => {
		if (browser && typeof window !== 'undefined') {
			window.addEventListener("error", handleError);
			window.addEventListener("unhandledrejection", handleRejection);
		}
	});

	onDestroy(() => {
		if (browser && typeof window !== 'undefined') {
			window.removeEventListener("error", handleError);
			window.removeEventListener("unhandledrejection", handleRejection);
		}
	});
</script>

{#if hasError}
	<div
		class="flex items-center justify-center min-h-screen bg-background p-6 font-mono uppercase"
	>
		<div
			class="max-w-2xl w-full bg-card border-2 border-black dark:border-white p-8 shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] dark:shadow-[8px_8px_0px_0px_rgba(255,255,255,1)]"
		>
			<div class="flex items-start gap-6">
				<div
					class="p-4 border-2 border-black dark:border-white bg-destructive text-destructive-foreground"
				>
					<AlertTriangle class="w-8 h-8" />
				</div>
				<div class="flex-1">
					<h2
						class="text-2xl font-display tracking-tighter mb-4 border-b-2 border-black dark:border-white inline-block"
					>
						System Failure
					</h2>
					<p class="text-sm font-bold mb-6">
						{fallback}
					</p>

					{#if showDetails && error}
						<details class="mb-6 group">
							<summary
								class="text-xs font-bold cursor-pointer hover:bg-terminal-green hover:text-black p-2 border-2 border-transparent hover:border-black dark:hover:border-white transition-all inline-block uppercase"
							>
								Technical Details
							</summary>
							<div
								class="mt-4 p-4 bg-black text-terminal-green border-2 border-black dark:border-white text-[10px] font-mono overflow-x-auto shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]"
							>
								<p class="font-bold underline mb-2">
									{error.message}
								</p>
								{#if errorInfo}
									<pre
										class="whitespace-pre-wrap">{errorInfo}</pre>
								{/if}
							</div>
						</details>
					{/if}

					<div class="flex gap-4">
						<button
							onclick={reset}
							class="px-6 py-3 border-2 border-black dark:border-white bg-terminal-green text-black font-black uppercase text-xs hover:shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] active:translate-x-1 active:translate-y-1 transition-all"
						>
							Return to Protocol
						</button>
						<button
							onclick={reload}
							class="px-6 py-3 border-2 border-black dark:border-white bg-background text-foreground font-black uppercase text-xs hover:shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] active:translate-x-1 active:translate-y-1 transition-all flex items-center gap-2"
						>
							<RefreshCcw class="w-4 h-4" />
							Hard Restart
						</button>
					</div>
				</div>
			</div>
		</div>
	</div>
{:else}
	{@render children()}
{/if}
