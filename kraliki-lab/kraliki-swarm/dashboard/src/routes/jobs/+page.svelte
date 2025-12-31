<script lang="ts">
	import { onMount } from 'svelte';

	interface LinearIssue {
		id: string;
		identifier: string;
		title: string;
		state: { name: string; color: string };
		priority: number;
		labels: { name: string }[];
		assignee?: { name: string };
		createdAt: string;
		updatedAt: string;
	}

	interface HumanBlocker {
		id: string;
		task: string;
		priority: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
		time: string;
		notes: string;
	}

	let issues = $state<LinearIssue[]>([]);
	let blockers = $state<HumanBlocker[]>([]);
	let loading = $state(true);
	let blockersLoading = $state(true);
	let error = $state<string | null>(null);
	let activeTab = $state<'linear' | 'blockers'>('blockers');
	let markingDone = $state<string | null>(null);

	const priorityLabels: Record<number, string> = {
		0: 'No priority',
		1: 'Urgent',
		2: 'High',
		3: 'Medium',
		4: 'Low'
	};

	const priorityColors: Record<number, string> = {
		0: '#666',
		1: '#ff5555',
		2: '#ffaa00',
		3: '#33ff00',
		4: '#888'
	};

	const blockerColors: Record<string, string> = {
		CRITICAL: '#ff5555',
		HIGH: '#ffaa00',
		MEDIUM: '#33ff00',
		LOW: '#888'
	};

	async function fetchIssues() {
		loading = true;
		error = null;
		try {
			const res = await fetch('/api/jobs');
			if (!res.ok) throw new Error('Failed to fetch');
			const data = await res.json();
			issues = data.issues || [];
		} catch (e) {
			error = 'Failed to load Linear issues';
			console.error(e);
		} finally {
			loading = false;
		}
	}

	async function fetchBlockers() {
		blockersLoading = true;
		try {
			const res = await fetch('/api/human-blockers');
			if (res.ok) {
				const data = await res.json();
				blockers = data.blockers || [];
			}
		} catch (e) {
			console.error('Failed to fetch blockers:', e);
		} finally {
			blockersLoading = false;
		}
	}

	async function markDone(id: string) {
		markingDone = id;
		try {
			const res = await fetch('/api/human-blockers', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ action: 'mark_done', id })
			});
			if (res.ok) {
				await fetchBlockers();
			}
		} catch (e) {
			console.error('Failed to mark done:', e);
		} finally {
			markingDone = null;
		}
	}

	onMount(() => {
		fetchIssues();
		fetchBlockers();
		const interval = setInterval(() => {
			fetchIssues();
			fetchBlockers();
		}, 60000);
		return () => clearInterval(interval);
	});

	const linearUrl = 'https://linear.app/verduona/team/VD/active';
	const criticalCount = $derived(blockers.filter(b => b.priority === 'CRITICAL').length);
</script>

<div class="page">
	<div class="page-header">
		<h2 class="glitch">Jobs // Work Queue</h2>
		<div style="display: flex; gap: 12px;">
			<button class="brutal-btn" onclick={() => { fetchIssues(); fetchBlockers(); }} disabled={loading || blockersLoading}>
				{loading || blockersLoading ? 'LOADING...' : 'REFRESH'}
			</button>
			<a href={linearUrl} target="_blank" class="brutal-btn">OPEN_LINEAR</a>
		</div>
	</div>

	<!-- Tab Navigation -->
	<div class="tabs">
		<button
			class="tab-btn"
			class:active={activeTab === 'blockers'}
			onclick={() => activeTab = 'blockers'}
		>
			HUMAN_BLOCKERS
			{#if criticalCount > 0}
				<span class="critical-badge">{criticalCount} CRITICAL</span>
			{/if}
		</button>
		<button
			class="tab-btn"
			class:active={activeTab === 'linear'}
			onclick={() => activeTab = 'linear'}
		>
			LINEAR_ISSUES ({issues.length})
		</button>
	</div>

	<!-- Human Blockers Tab -->
	{#if activeTab === 'blockers'}
		{#if blockersLoading && blockers.length === 0}
			<div class="loading">LOADING_HUMAN_BLOCKERS...</div>
		{:else if blockers.length === 0}
			<div class="empty success">NO_BLOCKERS - All clear for human work queue!</div>
		{:else}
			<div class="blockers-list">
				{#each blockers as blocker}
					<div class="blocker-card" class:critical={blocker.priority === 'CRITICAL'} class:high={blocker.priority === 'HIGH'}>
						<div class="blocker-header">
							<span class="blocker-id">{blocker.id}</span>
							<span class="blocker-priority" style="color: {blockerColors[blocker.priority]}">
								{blocker.priority}
							</span>
						</div>
						<div class="blocker-task">{blocker.task}</div>
						<div class="blocker-meta">
							{#if blocker.time}
								<span class="blocker-time">EST: {blocker.time}</span>
							{/if}
							{#if blocker.notes}
								<span class="blocker-notes">{blocker.notes}</span>
							{/if}
						</div>
						<div class="blocker-actions">
							<button
								class="brutal-btn done-btn"
								onclick={() => markDone(blocker.id)}
								disabled={markingDone === blocker.id}
							>
								{markingDone === blocker.id ? 'MARKING...' : 'MARK_DONE'}
							</button>
						</div>
					</div>
				{/each}
			</div>
		{/if}
	{/if}

	<!-- Linear Issues Tab -->
	{#if activeTab === 'linear'}
		{#if loading && issues.length === 0}
			<div class="loading">FETCHING_LINEAR_ISSUES...</div>
		{:else if error}
			<div class="error">{error}</div>
		{:else if issues.length === 0}
			<div class="empty">No active issues found</div>
		{:else}
			<div class="issues-grid">
				{#each issues as issue}
					<div class="issue-card">
						<div class="issue-header">
							<span class="issue-id">{issue.identifier}</span>
							<span class="issue-priority" style="color: {priorityColors[issue.priority] || '#666'}">
								{priorityLabels[issue.priority] || 'Unknown'}
							</span>
						</div>
						<h3 class="issue-title">{issue.title}</h3>
						<div class="issue-meta">
							<span class="issue-state" style="background: {issue.state?.color || '#333'}">
								{issue.state?.name || 'Unknown'}
							</span>
							{#if issue.labels?.length}
								{#each issue.labels.slice(0, 3) as label}
									<span class="issue-label">{label.name}</span>
								{/each}
							{/if}
						</div>
						{#if issue.assignee}
							<div class="issue-assignee">ASSIGNED: {issue.assignee.name}</div>
						{/if}
					</div>
				{/each}
			</div>
		{/if}
	{/if}
</div>

<style>
	.page {
		display: flex;
		flex-direction: column;
		gap: 20px;
	}

	.page-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		border-bottom: 2px solid var(--border);
		padding-bottom: 16px;
		flex-wrap: wrap;
		gap: 16px;
	}

	/* Tabs */
	.tabs {
		display: flex;
		gap: 8px;
		margin-bottom: 16px;
		flex-wrap: wrap;
	}

	.tab-btn {
		padding: 12px 24px;
		font-family: 'JetBrains Mono', monospace;
		font-size: 11px;
		font-weight: 700;
		text-transform: uppercase;
		background: var(--surface);
		border: 2px solid var(--border);
		color: var(--text-muted);
		cursor: pointer;
		box-shadow: 4px 4px 0 0 var(--border);
		transition: all 0.1s ease;
		display: flex;
		align-items: center;
		gap: 8px;
	}

	.tab-btn:hover {
		color: var(--text-main);
		transform: translate(-2px, -2px);
		box-shadow: 6px 6px 0 0 var(--border);
	}

	.tab-btn.active {
		background: var(--terminal-green);
		color: var(--void);
		border-color: var(--terminal-green);
		box-shadow: 2px 2px 0 0 var(--void);
		transform: translate(2px, 2px);
	}

	.critical-badge {
		background: #ff5555;
		color: #000;
		padding: 2px 6px;
		font-size: 9px;
		animation: pulse 1s ease-in-out infinite;
	}

	@keyframes pulse {
		0%, 100% { opacity: 1; }
		50% { opacity: 0.6; }
	}

	/* Blockers */
	.blockers-list {
		display: flex;
		flex-direction: column;
		gap: 12px;
	}

	.blocker-card {
		background: var(--surface);
		border: 2px solid var(--border);
		padding: 16px;
		box-shadow: 4px 4px 0 0 var(--border);
		transition: all 0.1s ease;
	}

	.blocker-card.critical {
		border-color: #ff5555;
		box-shadow: 4px 4px 0 0 #ff5555;
		background: rgba(255, 85, 85, 0.05);
	}

	.blocker-card.high {
		border-color: #ffaa00;
		box-shadow: 4px 4px 0 0 #ffaa00;
	}

	.blocker-card:hover {
		transform: translate(-2px, -2px);
		box-shadow: 6px 6px 0 0 var(--terminal-green);
	}

	.blocker-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 8px;
	}

	.blocker-id {
		font-family: 'JetBrains Mono', monospace;
		font-size: 12px;
		color: var(--terminal-green);
		font-weight: 700;
	}

	.blocker-priority {
		font-size: 11px;
		text-transform: uppercase;
		font-weight: 700;
	}

	.blocker-task {
		font-size: 14px;
		font-weight: 600;
		color: var(--text-main);
		margin-bottom: 12px;
	}

	.blocker-meta {
		display: flex;
		gap: 16px;
		font-size: 11px;
		color: var(--text-muted);
		margin-bottom: 12px;
	}

	.blocker-time {
		color: var(--cyan-data, #00d4ff);
	}

	.blocker-actions {
		display: flex;
		gap: 8px;
	}

	.done-btn {
		background: var(--terminal-green);
		color: var(--void);
		padding: 6px 12px;
		font-size: 10px;
	}

	.done-btn:hover {
		background: #44ff00;
	}

	/* Loading states */
	.loading, .error, .empty {
		padding: 40px;
		text-align: center;
		color: var(--text-muted);
		font-size: 12px;
		text-transform: uppercase;
		letter-spacing: 0.1em;
	}

	.error {
		color: #ff5555;
	}

	.empty.success {
		color: var(--terminal-green);
		border: 2px dashed var(--terminal-green);
	}

	/* Issues grid */
	.issues-grid {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
		gap: 16px;
	}

	.issue-card {
		background: var(--surface);
		border: 2px solid var(--border);
		padding: 16px;
		box-shadow: 4px 4px 0 0 var(--border);
		transition: all 0.1s ease;
	}

	.issue-card:hover {
		transform: translate(-2px, -2px);
		box-shadow: 6px 6px 0 0 var(--terminal-green);
		border-color: var(--terminal-green);
	}

	.issue-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 8px;
	}

	.issue-id {
		font-family: 'JetBrains Mono', monospace;
		font-size: 11px;
		color: var(--terminal-green);
		font-weight: 700;
	}

	.issue-priority {
		font-size: 10px;
		text-transform: uppercase;
		font-weight: 700;
	}

	.issue-title {
		font-size: 13px;
		font-weight: 600;
		margin: 0 0 12px 0;
		color: var(--text-main);
		line-height: 1.4;
	}

	.issue-meta {
		display: flex;
		flex-wrap: wrap;
		gap: 6px;
		margin-bottom: 8px;
	}

	.issue-state {
		font-size: 9px;
		padding: 2px 6px;
		text-transform: uppercase;
		font-weight: 700;
		color: #000;
	}

	.issue-label {
		font-size: 9px;
		padding: 2px 6px;
		background: rgba(51, 255, 0, 0.2);
		border: 1px solid var(--terminal-green);
		color: var(--terminal-green);
		text-transform: uppercase;
	}

	.issue-assignee {
		font-size: 10px;
		color: var(--text-muted);
		margin-top: 8px;
	}
</style>
