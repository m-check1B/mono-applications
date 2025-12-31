<script lang="ts">
	import Terminal from '$lib/Terminal.svelte';
	import { activeTerminals } from '$lib/stores/terminal';

	const MAX_TERMINALS = 4; // Increased max terminals since they are persistent

	function addTerminal() {
		const current = $activeTerminals;
		if (current.length < MAX_TERMINALS) {
			const nextId = current.length > 0 ? Math.max(...current) + 1 : 1;
			activeTerminals.add(nextId);
		}
	}

	function removeTerminal(id: number) {
		activeTerminals.remove(id);
	}
</script>

<svelte:head>
	<title>Terminal - Kraliki Swarm</title>
	<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/xterm@5.3.0/css/xterm.css" />
</svelte:head>

<div class="terminal-page">
	<div class="page-header">
		<h2>Terminal</h2>
		<div class="controls">
			<button 
				class="brutal-btn" 
				disabled={$activeTerminals.length >= MAX_TERMINALS}
				onclick={addTerminal}
			>
				+ Add Terminal ({$activeTerminals.length}/{MAX_TERMINALS})
			</button>
		</div>
	</div>

	<div class="terminals-grid">
		{#each $activeTerminals as id (id)}
			<div class="terminal-slot">
				<Terminal id={id} onDestroy={() => removeTerminal(id)} />
			</div>
		{/each}
	</div>

	<div class="terminal-info">
		<p><strong>Status:</strong> Terminals are persistent. Navigating away will NOT close your sessions.</p>
		<p><strong>Persistence:</strong> Use the "KILL" button to permanently end a session and its background process.</p>
		<p><strong>Shortcuts:</strong> Ctrl+C (interrupt), Ctrl+D (exit), Ctrl+L (clear)</p>
		<p><strong>Max terminals:</strong> {MAX_TERMINALS}</p>
	</div>
</div>

<style>
	.terminal-page {
		display: flex;
		flex-direction: column;
		height: calc(100vh - 200px);
		gap: 16px;
	}

	.page-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding-bottom: 12px;
		border-bottom: 2px solid var(--border);
	}

	.page-header h2 {
		margin: 0;
		font-size: 24px;
		font-weight: 700;
		color: var(--terminal-green);
		text-transform: uppercase;
		letter-spacing: 0.05em;
	}

	.controls {
		display: flex;
		gap: 12px;
	}

	.terminals-grid {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
		gap: 16px;
		flex: 1;
		min-height: 0;
	}

	.terminal-slot {
		min-height: 0;
		display: flex;
		flex-direction: column;
	}

	.terminal-info {
		padding: 12px;
		background: var(--surface);
		border: 2px solid var(--border);
		font-size: 11px;
		color: var(--text-dim);
	}

	.terminal-info p {
		margin: 4px 0;
	}

	.terminal-info strong {
		color: var(--terminal-green);
		font-weight: 700;
	}
</style>
