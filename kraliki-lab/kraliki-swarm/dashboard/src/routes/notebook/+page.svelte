<script lang="ts">
	import { onMount } from 'svelte';

	let content = $state('');
	let status = $state('');
	let textarea: HTMLTextAreaElement;

	onMount(() => {
		const saved = localStorage.getItem('kraliki_notebook_content');
		if (saved) {
			content = saved;
		}
	});

	function save() {
		localStorage.setItem('kraliki_notebook_content', content);
		status = 'SAVED';
		setTimeout(() => {
			status = '';
		}, 2000);
	}

	function handleInput() {
		save();
	}

	function clear() {
		if (confirm('CLEAR_NOTEBOOK? // CONFIRM')) {
			content = '';
			save();
			status = 'CLEARED';
		}
	}
</script>

<svelte:head>
	<title>Notebook // Kraliki Swarm</title>
</svelte:head>

<div class="notebook-container">
	<div class="card brutal-pulse-on-load">
		<div class="header-row">
			<h2 class="glitch">NOTEBOOK // SCRATCHPAD</h2>
			<div class="controls">
				<span class="status-indicator" class:visible={status !== ''}>{status}</span>
				<button class="brutal-btn small red-btn" onclick={clear}>CLEAR</button>
			</div>
		</div>

		<textarea
			bind:this={textarea}
			bind:value={content}
			oninput={handleInput}
			class="brutal-textarea"
			placeholder="ENTER_DATA_STREAM..."
			spellcheck="false"
		></textarea>

		<div class="footer-info">
			LOCAL_STORAGE_PERSISTENCE // ENABLED
		</div>
	</div>
</div>

<style>
	.notebook-container {
		max-width: 1000px;
		margin: 0 auto;
		height: calc(100vh - 200px);
	}

	.card {
		height: 100%;
		display: flex;
		flex-direction: column;
	}

	.header-row {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 16px;
		padding-bottom: 8px;
		border-bottom: 2px solid var(--border);
	}

	h2 {
		margin-bottom: 0;
		border-bottom: none;
	}

	.controls {
		display: flex;
		gap: 12px;
		align-items: center;
	}

	.status-indicator {
		font-family: 'JetBrains Mono', monospace;
		font-size: 10px;
		color: var(--terminal-green);
		opacity: 0;
		transition: opacity 0.3s ease;
		font-weight: 700;
	}

	.status-indicator.visible {
		opacity: 1;
	}

	.brutal-textarea {
		flex: 1;
		width: 100%;
		background: var(--background);
		color: var(--foreground);
		border: 2px solid var(--border);
		padding: 16px;
		font-family: 'JetBrains Mono', monospace;
		font-size: 14px;
		line-height: 1.6;
		resize: none;
		outline: none;
		box-shadow: inset 4px 4px 0 0 rgba(0,0,0,0.05);
	}

	.brutal-textarea:focus {
		border-color: var(--terminal-green);
		box-shadow: inset 4px 4px 0 0 rgba(51, 255, 0, 0.05);
	}

	.footer-info {
		margin-top: 8px;
		font-size: 10px;
		color: var(--muted-foreground);
		font-family: 'JetBrains Mono', monospace;
		text-align: right;
	}

	.brutal-pulse-on-load {
		animation: brutal-pulse 0.5s ease-out;
	}
</style>
