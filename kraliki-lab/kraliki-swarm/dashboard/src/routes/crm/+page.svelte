<script lang="ts">
	import { onMount } from 'svelte';

	interface CRMStats {
		contacts: number;
		leads: number;
		opportunities: number;
		accounts: number;
		tasks: number;
		meetings: number;
	}

	interface Lead {
		id: string;
		name: string;
		status: string;
		source: string;
		createdAt: string;
		assignedUserName?: string;
	}

	interface Opportunity {
		id: string;
		name: string;
		stage: string;
		amount: number;
		probability: number;
		accountName?: string;
		closeDate?: string;
	}

	interface Task {
		id: string;
		name: string;
		status: string;
		priority: string;
		dateEnd?: string;
		parentType?: string;
		parentName?: string;
	}

	let online = $state(false);
	let stats = $state<CRMStats | null>(null);
	let leads = $state<Lead[]>([]);
	let opportunities = $state<Opportunity[]>([]);
	let tasks = $state<Task[]>([]);
	let loading = $state(true);
	let error = $state<string | null>(null);
	let lastUpdated = $state<string | null>(null);

	const CRM_URL = 'http://127.0.0.1:8080';

	const statusColors: Record<string, string> = {
		'New': 'var(--cyan-data, #00d4ff)',
		'Assigned': 'var(--terminal-green)',
		'In Process': 'var(--warning, #ffaa00)',
		'Converted': 'var(--terminal-green)',
		'Dead': 'var(--text-muted)',
		'Recycled': '#888'
	};

	const stageColors: Record<string, string> = {
		'Prospecting': 'var(--cyan-data, #00d4ff)',
		'Qualification': 'var(--cyan-data, #00d4ff)',
		'Proposal': 'var(--warning, #ffaa00)',
		'Negotiation': 'var(--warning, #ffaa00)',
		'Closed Won': 'var(--terminal-green)',
		'Closed Lost': '#ff5555'
	};

	const priorityColors: Record<string, string> = {
		'Low': 'var(--text-muted)',
		'Normal': 'var(--text-main)',
		'High': 'var(--warning, #ffaa00)',
		'Urgent': '#ff5555'
	};

	async function fetchData() {
		loading = true;
		error = null;

		try {
			const res = await fetch('/api/crm');
			if (!res.ok) throw new Error('Failed to fetch CRM data');

			const data = await res.json();
			online = data.online;
			stats = data.stats;
			leads = data.leads || [];
			opportunities = data.opportunities || [];
			tasks = data.tasks || [];
			lastUpdated = data.lastUpdated;

			if (data.error) {
				error = data.error;
			}
		} catch (e) {
			error = e instanceof Error ? e.message : 'Unknown error';
			online = false;
		} finally {
			loading = false;
		}
	}

	function formatDate(dateStr: string | undefined): string {
		if (!dateStr) return '-';
		return new Date(dateStr).toLocaleDateString();
	}

	function formatCurrency(amount: number): string {
		return new Intl.NumberFormat('en-US', {
			style: 'currency',
			currency: 'EUR',
			minimumFractionDigits: 0
		}).format(amount);
	}

	const pipelineValue = $derived(
		opportunities.reduce((sum, opp) => sum + (opp.amount * opp.probability / 100), 0)
	);

	onMount(() => {
		fetchData();
		const interval = setInterval(fetchData, 60000); // Refresh every minute
		return () => clearInterval(interval);
	});
</script>

<div class="page">
	<div class="page-header">
		<h2 class="glitch">CRM // Customer Relations</h2>
		<div style="display: flex; gap: 12px; align-items: center;">
			<span class="status-badge" class:online class:offline={!online}>
				{online ? 'ESPOCRM ONLINE' : 'ESPOCRM OFFLINE'}
			</span>
			<a href={CRM_URL} target="_blank" class="brutal-btn">
				OPEN CRM
			</a>
			<button class="brutal-btn" onclick={fetchData} disabled={loading}>
				{loading ? 'LOADING...' : 'REFRESH'}
			</button>
		</div>
	</div>

	{#if loading && !stats}
		<div class="loading">LOADING_CRM_DATA...</div>
	{:else if !online}
		<div class="offline-notice">
			<h3>ESPOCRM IS OFFLINE</h3>
			<p>Start EspoCRM to see customer data:</p>
			<code>cd /github/tools/crm && docker compose up -d</code>
			{#if error}
				<p class="error-detail">{error}</p>
			{/if}
		</div>
	{:else}
		<div class="crm-grid">
			<!-- Stats Overview -->
			{#if stats}
				<div class="card span-2">
					<h3>OVERVIEW</h3>
					<div class="stats-grid">
						<div class="stat-item">
							<span class="stat-value">{stats.leads}</span>
							<span class="stat-label">LEADS</span>
						</div>
						<div class="stat-item">
							<span class="stat-value">{stats.contacts}</span>
							<span class="stat-label">CONTACTS</span>
						</div>
						<div class="stat-item">
							<span class="stat-value">{stats.accounts}</span>
							<span class="stat-label">ACCOUNTS</span>
						</div>
						<div class="stat-item">
							<span class="stat-value">{stats.opportunities}</span>
							<span class="stat-label">OPPORTUNITIES</span>
						</div>
						<div class="stat-item">
							<span class="stat-value">{stats.tasks}</span>
							<span class="stat-label">TASKS</span>
						</div>
						<div class="stat-item">
							<span class="stat-value green">{formatCurrency(pipelineValue)}</span>
							<span class="stat-label">PIPELINE VALUE</span>
						</div>
					</div>
				</div>
			{/if}

			<!-- Recent Leads -->
			<div class="card">
				<h3>RECENT LEADS</h3>
				{#if leads.length === 0}
					<div class="empty">NO LEADS</div>
				{:else}
					<div class="list">
						{#each leads as lead}
							<a href="{CRM_URL}/#Lead/view/{lead.id}" target="_blank" class="list-item">
								<div class="item-main">
									<span class="item-name">{lead.name}</span>
									<span class="item-meta">{lead.source || 'Unknown source'}</span>
								</div>
								<span class="status-tag" style="background: {statusColors[lead.status] || '#888'}">
									{lead.status}
								</span>
							</a>
						{/each}
					</div>
				{/if}
				<a href="{CRM_URL}/#Lead" target="_blank" class="brutal-btn view-all">VIEW ALL LEADS</a>
			</div>

			<!-- Open Opportunities -->
			<div class="card">
				<h3>OPEN OPPORTUNITIES</h3>
				{#if opportunities.length === 0}
					<div class="empty">NO OPEN OPPORTUNITIES</div>
				{:else}
					<div class="list">
						{#each opportunities as opp}
							<a href="{CRM_URL}/#Opportunity/view/{opp.id}" target="_blank" class="list-item">
								<div class="item-main">
									<span class="item-name">{opp.name}</span>
									<span class="item-meta">{opp.accountName || 'No account'} - {formatDate(opp.closeDate)}</span>
								</div>
								<div class="opp-values">
									<span class="opp-amount">{formatCurrency(opp.amount)}</span>
									<span class="status-tag" style="background: {stageColors[opp.stage] || '#888'}">
										{opp.stage}
									</span>
								</div>
							</a>
						{/each}
					</div>
				{/if}
				<a href="{CRM_URL}/#Opportunity" target="_blank" class="brutal-btn view-all">VIEW ALL OPPORTUNITIES</a>
			</div>

			<!-- Pending Tasks -->
			<div class="card span-2">
				<h3>PENDING TASKS</h3>
				{#if tasks.length === 0}
					<div class="empty">NO PENDING TASKS</div>
				{:else}
					<div class="task-list">
						{#each tasks as task}
							<a href="{CRM_URL}/#Task/view/{task.id}" target="_blank" class="task-item">
								<span class="task-priority" style="background: {priorityColors[task.priority] || '#888'}">
									{task.priority}
								</span>
								<div class="task-main">
									<span class="task-name">{task.name}</span>
									{#if task.parentName}
										<span class="task-parent">{task.parentType}: {task.parentName}</span>
									{/if}
								</div>
								<div class="task-due">
									{formatDate(task.dateEnd)}
								</div>
								<span class="task-status">{task.status}</span>
							</a>
						{/each}
					</div>
				{/if}
				<a href="{CRM_URL}/#Task" target="_blank" class="brutal-btn view-all">VIEW ALL TASKS</a>
			</div>

			<!-- Quick Actions -->
			<div class="card span-2">
				<h3>QUICK ACTIONS</h3>
				<div class="actions-grid">
					<a href="{CRM_URL}/#Lead/create" target="_blank" class="action-btn">
						<span class="action-icon">+</span>
						<span>NEW LEAD</span>
					</a>
					<a href="{CRM_URL}/#Contact/create" target="_blank" class="action-btn">
						<span class="action-icon">+</span>
						<span>NEW CONTACT</span>
					</a>
					<a href="{CRM_URL}/#Opportunity/create" target="_blank" class="action-btn">
						<span class="action-icon">+</span>
						<span>NEW OPPORTUNITY</span>
					</a>
					<a href="{CRM_URL}/#Task/create" target="_blank" class="action-btn">
						<span class="action-icon">+</span>
						<span>NEW TASK</span>
					</a>
					<a href="{CRM_URL}/#Meeting/create" target="_blank" class="action-btn">
						<span class="action-icon">+</span>
						<span>NEW MEETING</span>
					</a>
					<a href="{CRM_URL}/#Email" target="_blank" class="action-btn">
						<span class="action-icon">@</span>
						<span>EMAILS</span>
					</a>
				</div>
			</div>
		</div>

		{#if lastUpdated}
			<div class="last-updated">
				Last updated: {new Date(lastUpdated).toLocaleString()}
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
		gap: 12px;
	}

	.status-badge {
		padding: 6px 12px;
		font-size: 10px;
		font-weight: 700;
		font-family: 'JetBrains Mono', monospace;
	}

	.status-badge.online {
		background: var(--terminal-green);
		color: var(--void);
	}

	.status-badge.offline {
		background: #ff5555;
		color: var(--void);
	}

	.loading {
		padding: 40px;
		text-align: center;
		color: var(--text-muted);
		font-size: 12px;
		text-transform: uppercase;
		letter-spacing: 0.1em;
	}

	.offline-notice {
		text-align: center;
		padding: 60px 20px;
		border: 2px dashed #ff5555;
		background: rgba(255, 85, 85, 0.05);
	}

	.offline-notice h3 {
		color: #ff5555;
		margin-bottom: 16px;
	}

	.offline-notice code {
		display: block;
		margin-top: 16px;
		padding: 12px;
		background: var(--surface);
		border: 1px solid var(--border);
		font-family: 'JetBrains Mono', monospace;
		font-size: 12px;
	}

	.error-detail {
		margin-top: 16px;
		color: var(--text-muted);
		font-size: 11px;
	}

	.crm-grid {
		display: grid;
		grid-template-columns: repeat(2, 1fr);
		gap: 20px;
	}

	.card {
		background: var(--surface);
		border: 2px solid var(--border);
		padding: 20px;
		box-shadow: 4px 4px 0 0 var(--border);
	}

	.card h3 {
		font-size: 12px;
		font-weight: 700;
		margin: 0 0 16px 0;
		text-transform: uppercase;
		letter-spacing: 0.05em;
	}

	.span-2 {
		grid-column: span 2;
	}

	/* Stats */
	.stats-grid {
		display: grid;
		grid-template-columns: repeat(6, 1fr);
		gap: 16px;
	}

	.stat-item {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 4px;
	}

	.stat-value {
		font-family: 'JetBrains Mono', monospace;
		font-size: 24px;
		font-weight: 700;
		color: var(--terminal-green);
	}

	.stat-value.green {
		color: var(--terminal-green);
	}

	.stat-label {
		font-size: 10px;
		color: var(--text-muted);
		text-transform: uppercase;
	}

	/* Lists */
	.list {
		display: flex;
		flex-direction: column;
		gap: 8px;
		margin-bottom: 16px;
	}

	.list-item {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 10px 12px;
		background: rgba(255, 255, 255, 0.02);
		border: 1px solid var(--border);
		text-decoration: none;
		color: var(--text-main);
		transition: all 0.1s ease;
	}

	.list-item:hover {
		border-color: var(--terminal-green);
		background: rgba(51, 255, 0, 0.05);
	}

	.item-main {
		display: flex;
		flex-direction: column;
		gap: 2px;
	}

	.item-name {
		font-size: 12px;
		font-weight: 600;
	}

	.item-meta {
		font-size: 10px;
		color: var(--text-muted);
	}

	.status-tag {
		font-size: 9px;
		padding: 3px 8px;
		font-weight: 700;
		color: var(--void);
		text-transform: uppercase;
	}

	.opp-values {
		display: flex;
		flex-direction: column;
		align-items: flex-end;
		gap: 4px;
	}

	.opp-amount {
		font-family: 'JetBrains Mono', monospace;
		font-size: 12px;
		font-weight: 700;
		color: var(--terminal-green);
	}

	.empty {
		padding: 30px;
		text-align: center;
		color: var(--text-muted);
		border: 2px dashed var(--border);
		font-size: 11px;
	}

	.view-all {
		width: 100%;
		text-align: center;
	}

	/* Tasks */
	.task-list {
		display: flex;
		flex-direction: column;
		gap: 8px;
		margin-bottom: 16px;
	}

	.task-item {
		display: grid;
		grid-template-columns: 60px 1fr 100px 80px;
		gap: 12px;
		align-items: center;
		padding: 10px 12px;
		background: rgba(255, 255, 255, 0.02);
		border: 1px solid var(--border);
		text-decoration: none;
		color: var(--text-main);
		transition: all 0.1s ease;
	}

	.task-item:hover {
		border-color: var(--terminal-green);
		background: rgba(51, 255, 0, 0.05);
	}

	.task-priority {
		font-size: 9px;
		padding: 3px 6px;
		font-weight: 700;
		color: var(--void);
		text-transform: uppercase;
		text-align: center;
	}

	.task-main {
		display: flex;
		flex-direction: column;
		gap: 2px;
	}

	.task-name {
		font-size: 12px;
		font-weight: 600;
	}

	.task-parent {
		font-size: 10px;
		color: var(--text-muted);
	}

	.task-due {
		font-size: 11px;
		color: var(--text-muted);
		text-align: right;
	}

	.task-status {
		font-size: 10px;
		color: var(--text-muted);
		text-align: right;
	}

	/* Actions */
	.actions-grid {
		display: grid;
		grid-template-columns: repeat(6, 1fr);
		gap: 12px;
	}

	.action-btn {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 8px;
		padding: 16px;
		background: var(--surface);
		border: 2px solid var(--border);
		text-decoration: none;
		color: var(--text-main);
		font-size: 10px;
		font-weight: 700;
		text-transform: uppercase;
		transition: all 0.1s ease;
	}

	.action-btn:hover {
		background: var(--terminal-green);
		border-color: var(--terminal-green);
		color: var(--void);
	}

	.action-icon {
		font-size: 20px;
		font-weight: 700;
	}

	.last-updated {
		text-align: right;
		font-size: 10px;
		color: var(--text-muted);
	}

	@media (max-width: 768px) {
		.crm-grid {
			grid-template-columns: 1fr;
		}

		.span-2 {
			grid-column: span 1;
		}

		.stats-grid {
			grid-template-columns: repeat(3, 1fr);
		}

		.actions-grid {
			grid-template-columns: repeat(3, 1fr);
		}

		.task-item {
			grid-template-columns: 1fr;
			gap: 8px;
		}
	}
</style>
