<script lang="ts">
	import { onMount } from "svelte";

	interface RecallEntry {
		id: string;
		agent: string;
		action: 'store' | 'retrieve';
		key: string;
		timestamp: string;
		size?: number;
		text?: string;
	}

	interface RecallStats {
		total_entries: number;
		total_stores: number;
		total_retrieves: number;
		by_agent: Record<string, { stores: number; retrieves: number }>;
	}

	interface ConsolidationPlan {
		ephemeral_files: number;
		memories_to_move: number;
		target_files: number;
		consolidations: Array<{
			target: string;
			sources: number;
			memories: number;
		}>;
	}

	let entries = $state<RecallEntry[]>([]);
	let stats = $state<RecallStats | null>(null);
	let inactiveAgents = $state<string[]>([]);
	let knownAgentsCount = $state(0);
	let loading = $state(true);
	let error = $state<string | null>(null);
	let searchQuery = $state('');

	// Consolidation state
	let consolidationPlan = $state<ConsolidationPlan | null>(null);
	let consolidationLoading = $state(false);
	let consolidationResult = $state<{ success: boolean; message: string } | null>(null);
	let showConsolidationDetails = $state(false);

	// Recall API
	const MEMORY_API = '/api/memory';
	const CONSOLIDATION_API = '/api/memory/consolidate';

	async function fetchData() {
		try {
			const res = await fetch(MEMORY_API);
			if (res.ok) {
				const data = await res.json();
				entries = data.entries || [];
				stats = data.stats || null;
				inactiveAgents = data.inactiveAgents || [];
				knownAgentsCount = data.knownAgents?.length || 0;
				error = data.error || null;
			} else {
				error = 'Failed to fetch recall data';
			}
		} catch (e) {
			error = 'Recall by Kraliki service unavailable';
		} finally {
			loading = false;
		}
	}

	async function fetchConsolidationPlan() {
		try {
			const res = await fetch(CONSOLIDATION_API);
			if (res.ok) {
				const data = await res.json();
				if (data.success) {
					consolidationPlan = data.plan;
				}
			}
		} catch {
			// Silently fail - consolidation is optional
		}
	}

	async function executeConsolidation() {
		consolidationLoading = true;
		consolidationResult = null;
		try {
			const res = await fetch(CONSOLIDATION_API, { method: 'POST' });
			const data = await res.json();
			consolidationResult = data;
			if (data.success) {
				// Refresh data after successful consolidation
				await fetchData();
				await fetchConsolidationPlan();
			}
		} catch (e) {
			consolidationResult = {
				success: false,
				message: 'Failed to execute consolidation'
			};
		} finally {
			consolidationLoading = false;
		}
	}

	function dismissResult() {
		consolidationResult = null;
	}

	// Computed: filtered entries based on search
	let filteredEntries = $derived(
		searchQuery.trim() === ''
			? entries
			: entries.filter(entry => {
				const query = searchQuery.toLowerCase();
				return (
					entry.agent.toLowerCase().includes(query) ||
					entry.key.toLowerCase().includes(query) ||
					(entry.text && entry.text.toLowerCase().includes(query))
				);
			})
	);

	onMount(() => {
		fetchData();
		fetchConsolidationPlan();
		const interval = setInterval(fetchData, 30000);
		return () => clearInterval(interval);
	});
</script>

<div class="page">
	<div class="page-header">
		<h2 class="glitch">Recall // Agent Knowledge Base</h2>
		{#if stats}
			<div style="display: flex; gap: 12px; align-items: center;">
				<span class="pulse-dot green"></span>
				<span class="updated">{stats.total_entries} ENTRIES_STORED</span>
			</div>
		{/if}
	</div>

	{#if loading}
		<div class="loading">RETRIEVING_NEURAL_PATTERNS...</div>
	{:else if error}
		<div class="card error-card">
			<h2 style="color: var(--system-red);">CONNECTION_FAILED</h2>
			<p>{error}</p>
			<p class="hint">Ensure Recall service is active on port 3020.</p>
		</div>
	{:else}
		<!-- Stats Overview -->
		<div class="stats-grid">
			{#if stats}
				<div class="stat-card">
					<span class="stat-value">{stats.total_stores}</span>
					<span class="stat-label">STORES</span>
				</div>
				<div class="stat-card">
					<span class="stat-value">{stats.total_retrieves}</span>
					<span class="stat-label">RETRIEVES</span>
				</div>
				<div class="stat-card">
					<span class="stat-value">{Object.keys(stats.by_agent).length}</span>
					<span class="stat-label">ACTIVE_AGENTS</span>
				</div>
			{/if}
			{#if consolidationPlan}
				<div class="stat-card" class:alert={consolidationPlan.ephemeral_files > 5}>
					<span class="stat-value" class:yellow={consolidationPlan.ephemeral_files > 5}>{consolidationPlan.ephemeral_files}</span>
					<span class="stat-label">EPHEMERAL_FILES</span>
				</div>
			{/if}
		</div>

		<!-- Recall Consolidation Card -->
		{#if consolidationPlan && consolidationPlan.ephemeral_files > 0}
			<div class="card consolidation-card">
				<div class="consolidation-header">
					<div>
						<h2>RECALL_CONSOLIDATION // {consolidationPlan.ephemeral_files} FILES_TO_MERGE</h2>
						<p class="hint">Merge ephemeral agent memories (CC-builder-08:30.26.12.AA) into role-based files (CC-builder) for better recall.</p>
					</div>
					<div class="consolidation-actions">
						<button
							class="brutal-btn toggle-btn"
							onclick={() => showConsolidationDetails = !showConsolidationDetails}
						>
							{showConsolidationDetails ? 'HIDE' : 'SHOW'} PLAN
						</button>
						<button
							class="brutal-btn execute-btn"
							onclick={executeConsolidation}
							disabled={consolidationLoading}
						>
							{consolidationLoading ? 'CONSOLIDATING...' : 'CONSOLIDATE_NOW'}
						</button>
					</div>
				</div>

				{#if consolidationResult}
					<div class="result-banner" class:success={consolidationResult.success} class:failure={!consolidationResult.success}>
						<span>{consolidationResult.message}</span>
						<button class="dismiss-btn" onclick={dismissResult}>DISMISS</button>
					</div>
				{/if}

				{#if showConsolidationDetails}
					<div class="consolidation-details">
						<div class="detail-summary">
							<span class="detail-item">
								<span class="detail-value">{consolidationPlan.memories_to_move}</span>
								<span class="detail-label">MEMORIES_TO_MOVE</span>
							</span>
							<span class="detail-item">
								<span class="detail-value">{consolidationPlan.target_files}</span>
								<span class="detail-label">TARGET_FILES</span>
							</span>
						</div>
						<div class="consolidation-list">
							<h3>MERGE_TARGETS:</h3>
							{#each consolidationPlan.consolidations.slice(0, 10) as item}
								<div class="merge-item">
									<span class="merge-target">{item.target}</span>
									<span class="merge-info">{item.sources} sources / {item.memories} memories</span>
								</div>
							{/each}
							{#if consolidationPlan.consolidations.length > 10}
								<div class="merge-item more">
									... and {consolidationPlan.consolidations.length - 10} more targets
								</div>
							{/if}
						</div>
					</div>
				{/if}
			</div>
		{/if}

		<!-- By Agent -->
		{#if stats}
			<div class="card">
				<h2>RECALL_USAGE // BY_AGENT</h2>
				<div class="agent-stats">
					{#each Object.entries(stats.by_agent).sort((a, b) => (b[1].stores + b[1].retrieves) - (a[1].stores + a[1].retrieves)) as [agent, data]}
						<div class="agent-row-recall">
							<span class="agent-name">{agent.toUpperCase()}</span>
							<div class="agent-ops">
								<span class="store-count">{data.stores} STORES</span>
								<span class="retrieve-count">{data.retrieves} RETRIEVES</span>
							</div>
						</div>
					{/each}
				</div>
			</div>
		{/if}

		<!-- Recent Operations -->
		<div class="card">
			<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
				<h2 style="margin: 0;">RECENT_OPERATIONS // RECALL_STREAM</h2>
				<input
					type="text"
					bind:value={searchQuery}
					placeholder="SEARCH_RECALL..."
					class="search-input"
				/>
			</div>
			{#if filteredEntries.length === 0 && searchQuery.trim() !== ''}
				<p class="hint">No recall entries found matching "{searchQuery}"</p>
			{:else if entries.length === 0}
				<p class="hint">No recent recall operations detected in this sector.</p>
			{:else}
				<div class="entries-list">
					{#each filteredEntries as entry}
						<div class="entry" class:store={entry.action === 'store'} class:retrieve={entry.action === 'retrieve'}>
							<div class="entry-header">
								<span class="entry-action" class:store={entry.action === 'store'} class:retrieve={entry.action === 'retrieve'}>
									{entry.action.toUpperCase()}
								</span>
								<span class="entry-agent">{entry.agent.toUpperCase()}</span>
								<span class="entry-time">[{entry.timestamp.slice(11, 19)}]</span>
							</div>
							<div class="entry-key">{entry.key}</div>
							{#if entry.text}
								<div class="entry-text">{entry.text}</div>
							{/if}
							{#if entry.size}
								<div class="entry-size">{entry.size} BYTES_COMMITTED</div>
							{/if}
						</div>
					{/each}
				</div>
			{/if}
		</div>
	{/if}
</div>

<style>
	.page {
		display: flex;
		flex-direction: column;
		gap: 24px;
	}

	.page-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 8px;
		border-bottom: 2px solid var(--border);
		padding-bottom: 16px;
	}

	.hint {
		color: var(--text-muted);
		font-size: 10px;
		text-transform: uppercase;
		margin-top: 8px;
		letter-spacing: 0.1em;
	}

	.error-card {
		border: 2px solid var(--system-red);
		box-shadow: 4px 4px 0 0 var(--system-red);
	}

	.stats-grid {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
		gap: 16px;
	}

	.stat-card {
		background: var(--surface);
		padding: 20px;
		border: 2px solid var(--border);
		text-align: center;
		box-shadow: 4px 4px 0 0 var(--border);
	}

	.stat-value {
		display: block;
		font-size: 32px;
		font-weight: 700;
		color: var(--terminal-green);
		font-family: 'Archivo Black', sans-serif;
		margin-bottom: 4px;
	}

	.stat-label {
		font-size: 10px;
		color: var(--text-muted);
		text-transform: uppercase;
		letter-spacing: 0.1em;
		font-weight: 700;
	}

	.agent-stats {
		display: flex;
		flex-direction: column;
		gap: 12px;
	}

	.agent-row-recall {
		display: flex;
		justify-content: space-between;
		padding: 12px 16px;
		background: rgba(240, 240, 240, 0.02);
		border: 2px solid var(--border);
		align-items: center;
		transition: all 0.1s ease;
	}

	.agent-row-recall:hover {
		border-color: var(--terminal-green);
		background: rgba(51, 255, 0, 0.05);
		transform: translateX(4px);
	}

	.agent-name {
		font-family: 'JetBrains Mono', monospace;
		font-size: 13px;
		color: var(--terminal-green);
		font-weight: 700;
	}

	.agent-ops {
		display: flex;
		gap: 16px;
		font-size: 11px;
		text-transform: uppercase;
		font-weight: 700;
		font-family: 'JetBrains Mono', monospace;
	}

	.store-count {
		color: var(--cyan-data);
	}

	.retrieve-count {
		color: var(--warning);
	}

	.entries-list {
		display: flex;
		flex-direction: column;
		gap: 12px;
		max-height: 600px;
		overflow-y: auto;
		padding-right: 12px;
		scrollbar-width: thin;
		scrollbar-color: var(--border) var(--surface);
	}

	.entry {
		padding: 16px;
		background: var(--surface);
		border: 2px solid var(--border);
		border-left: 6px solid var(--border);
		transition: all 0.1s ease;
	}

	.entry:hover {
		border-color: var(--terminal-green);
		background: rgba(51, 255, 0, 0.05);
		transform: translate(-2px, -2px);
		box-shadow: 4px 4px 0 var(--terminal-green);
	}

	.entry.store {
		border-left-color: var(--cyan-data);
	}

	.entry.retrieve {
		border-left-color: var(--warning);
	}

	.entry-header {
		display: flex;
		flex-wrap: wrap;
		gap: 16px;
		margin-bottom: 12px;
		font-size: 11px;
		align-items: center;
		font-family: 'JetBrains Mono', monospace;
	}

	.entry-action {
		font-weight: 700;
		padding: 2px 8px;
		border: 2px solid;
		font-size: 9px;
	}

	.entry-action.store {
		border-color: var(--cyan-data);
		color: var(--cyan-data);
	}

	.entry-action.retrieve {
		border-color: var(--warning);
		color: var(--warning);
	}

	.entry-agent {
		color: var(--terminal-green);
		text-transform: uppercase;
		font-weight: 700;
	}

	.entry-time {
		color: var(--text-muted);
		margin-left: auto;
	}

	.entry-key {
		font-family: 'JetBrains Mono', monospace;
		font-size: 13px;
		word-break: break-all;
		color: var(--text-main);
	}

	.entry-text {
		font-family: 'JetBrains Mono', monospace;
		font-size: 12px;
		line-height: 1.6;
		color: var(--text-muted);
		margin-top: 8px;
		padding: 12px;
		background: rgba(51, 255, 0, 0.03);
		border-left: 2px solid var(--terminal-green);
		white-space: pre-wrap;
		word-break: break-word;
	}

	.entry-size {
		font-size: 10px;
		color: var(--text-muted);
		margin-top: 8px;
		text-transform: uppercase;
		font-weight: 700;
	}

	.card {
		background: var(--surface);
		border: 2px solid var(--border);
		padding: 20px;
		box-shadow: 4px 4px 0 0 var(--border);
	}

	.card h2 {
		font-size: 12px;
		font-weight: 700;
		margin: 0 0 16px 0;
		text-transform: uppercase;
	}

	.stat-card.alert {
		border-color: var(--system-red);
		box-shadow: 4px 4px 0 0 var(--system-red);
	}

	/* Consolidation Card Styles */
	.consolidation-card {
		border: 2px solid var(--warning);
		box-shadow: 4px 4px 0 0 var(--warning);
	}

	.consolidation-header {
		display: flex;
		justify-content: space-between;
		align-items: flex-start;
		gap: 16px;
		flex-wrap: wrap;
	}

	.consolidation-header h2 {
		color: var(--warning);
		margin-bottom: 8px;
	}

	.consolidation-actions {
		display: flex;
		gap: 8px;
	}

	.toggle-btn {
		font-size: 10px;
		padding: 8px 12px;
	}

	.execute-btn {
		font-size: 10px;
		padding: 8px 16px;
		background: var(--warning);
		color: var(--void);
		border-color: var(--warning);
	}

	.execute-btn:hover:not(:disabled) {
		background: var(--terminal-green);
		border-color: var(--terminal-green);
	}

	.execute-btn:disabled {
		opacity: 0.6;
		cursor: not-allowed;
	}

	.result-banner {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 12px 16px;
		margin-top: 16px;
		font-family: 'JetBrains Mono', monospace;
		font-size: 11px;
		font-weight: 700;
	}

	.result-banner.success {
		background: rgba(51, 255, 0, 0.15);
		border: 2px solid var(--terminal-green);
		color: var(--terminal-green);
	}

	.result-banner.failure {
		background: rgba(255, 85, 85, 0.15);
		border: 2px solid var(--system-red);
		color: var(--system-red);
	}

	.dismiss-btn {
		background: transparent;
		border: 1px solid currentColor;
		color: inherit;
		padding: 4px 8px;
		font-size: 9px;
		font-family: 'JetBrains Mono', monospace;
		font-weight: 700;
		cursor: pointer;
	}

	.dismiss-btn:hover {
		background: currentColor;
		color: var(--void);
	}

	.consolidation-details {
		margin-top: 20px;
		padding-top: 16px;
		border-top: 1px solid var(--border);
	}

	.detail-summary {
		display: flex;
		gap: 32px;
		margin-bottom: 16px;
	}

	.detail-item {
		display: flex;
		flex-direction: column;
		gap: 4px;
	}

	.detail-value {
		font-family: 'JetBrains Mono', monospace;
		font-size: 24px;
		font-weight: 700;
		color: var(--warning);
	}

	.detail-label {
		font-family: 'JetBrains Mono', monospace;
		font-size: 9px;
		text-transform: uppercase;
		color: var(--text-muted);
		letter-spacing: 0.1em;
	}

	.consolidation-list h3 {
		font-family: 'JetBrains Mono', monospace;
		font-size: 10px;
		text-transform: uppercase;
		color: var(--text-muted);
		letter-spacing: 0.1em;
		margin-bottom: 12px;
	}

	.merge-item {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 8px 12px;
		background: rgba(255, 149, 0, 0.05);
		border: 1px solid var(--border);
		margin-bottom: 4px;
	}

	.merge-item:hover {
		border-color: var(--warning);
	}

	.merge-target {
		font-family: 'JetBrains Mono', monospace;
		font-size: 12px;
		font-weight: 700;
		color: var(--warning);
	}

	.merge-info {
		font-family: 'JetBrains Mono', monospace;
		font-size: 10px;
		color: var(--text-muted);
	}

	.merge-item.more {
		font-style: italic;
		color: var(--text-muted);
		justify-content: center;
	}

	.stat-value.yellow {
		color: var(--warning) !important;
	}

	.search-input {
		padding: 8px 12px;
		font-family: 'JetBrains Mono', monospace;
		font-size: 11px;
		background: var(--surface);
		border: 2px solid var(--border);
		color: var(--text-main);
		text-transform: uppercase;
		letter-spacing: 0.05em;
		min-width: 300px;
		transition: all 0.15s ease;
	}

	.search-input:focus {
		outline: none;
		border-color: var(--terminal-green);
		box-shadow: 0 0 0 2px rgba(51, 255, 0, 0.1);
	}

	.search-input::placeholder {
		color: var(--text-muted);
		opacity: 0.6;
	}
</style>
