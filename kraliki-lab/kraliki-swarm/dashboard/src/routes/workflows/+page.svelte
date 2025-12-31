<script lang="ts">
	import { onMount } from 'svelte';

	interface Workflow {
		name: string;
		category: string;
		description: string;
		trigger: string;
		status: 'active' | 'ready' | 'planned';
		lastRun?: string;
		mcpsRequired: string[];
	}

	interface Service {
		name: string;
		status: 'online' | 'offline' | 'planned';
		url?: string;
		note: string;
	}

	let loading = $state(true);
	let workflows = $state<Workflow[]>([]);
	let windmillStatus = $state<{status: string, version?: string}>({status: 'checking'});

	const workflowsData: Workflow[] = [
		// SALES
		{
			name: 'lead-capture',
			category: 'sales',
			description: 'Webhook -> validate -> dedupe -> enrich -> CRM -> notify',
			trigger: 'webhook',
			status: 'ready',
			mcpsRequired: ['crm', 'telegram', 'linear']
		},
		{
			name: 'cold-outreach',
			category: 'sales',
			description: 'Load prospects -> personalize -> send emails -> track replies',
			trigger: 'cron (weekdays 9AM)',
			status: 'ready',
			mcpsRequired: ['crm', 'email', 'linear']
		},
		// CUSTOMER
		{
			name: 'customer-onboarding',
			category: 'customer',
			description: 'Stripe payment -> provision -> welcome email -> check-in',
			trigger: 'stripe_webhook',
			status: 'ready',
			mcpsRequired: ['stripe', 'email', 'linear']
		},
		{
			name: 'churn-prevention',
			category: 'customer',
			description: 'Weekly health check -> score -> alert CSM -> re-engage at-risk',
			trigger: 'cron (Monday 10AM)',
			status: 'ready',
			mcpsRequired: ['analytics', 'email', 'linear', 'crm']
		},
		// MARKETING
		{
			name: 'linkedin-scheduler',
			category: 'marketing',
			description: 'Queue content -> schedule -> post -> track engagement',
			trigger: 'cron (Tue/Thu 8AM)',
			status: 'ready',
			mcpsRequired: ['linkedin', 'telegram']
		},
		{
			name: 'content-pipeline',
			category: 'marketing',
			description: 'Idea -> LLM draft -> review -> publish -> distribute',
			trigger: 'manual / weekly',
			status: 'ready',
			mcpsRequired: ['ai', 'telegram', 'cms']
		},
		// OPS
		{
			name: 'weekly-metrics',
			category: 'ops',
			description: 'Pull metrics -> compute deltas -> generate CEO summary',
			trigger: 'cron (Sunday 18:00)',
			status: 'ready',
			mcpsRequired: ['stripe', 'linear', 'telegram']
		},
		// FINANCE
		{
			name: 'payment-notification',
			category: 'finance',
			description: 'Stripe webhook -> notify team -> update CRM -> track MRR',
			trigger: 'stripe_webhook',
			status: 'ready',
			mcpsRequired: ['stripe', 'crm', 'telegram', 'linear']
		},
		// SERVICE
		{
			name: 'audit-delivery',
			category: 'service',
			description: 'Reality Check intake -> analysis -> report -> delivery -> follow-up',
			trigger: 'stripe_webhook',
			status: 'ready',
			mcpsRequired: ['stripe', 'email', 'linear', 'ai']
		},
		{
			name: 'academy-enrollment',
			category: 'service',
			description: 'Payment -> access provision -> welcome -> progress tracking',
			trigger: 'stripe_webhook',
			status: 'ready',
			mcpsRequired: ['stripe', 'skool', 'email', 'linear']
		}
	];

	const mcpServers: Service[] = [
		{ name: 'Linear MCP', status: 'online', url: 'https://mcp.linear.app', note: 'Issue tracking' },
		{ name: 'Stripe MCP', status: 'planned', note: 'Payments' },
		{ name: 'Telegram MCP', status: 'planned', note: 'Notifications' },
		{ name: 'Email MCP', status: 'planned', note: 'Transactional email' },
		{ name: 'CRM MCP', status: 'planned', note: 'EspoCRM integration' },
	];

	const externalServices: Service[] = [
		{ name: 'EspoCRM', status: 'online', url: 'http://127.0.0.1:8080', note: 'CRM' },
		{ name: 'Zitadel', status: 'online', url: 'http://127.0.0.1:8085', note: 'Identity' },
		{ name: 'mgrep', status: 'online', url: 'http://127.0.0.1:8001', note: 'Semantic search' },
		{ name: 'Stripe', status: 'online', url: 'https://dashboard.stripe.com', note: 'Payments' },
	];

	async function checkWindmill() {
		try {
			const res = await fetch('/api/windmill/health');
			if (res.ok) {
				const data = await res.json();
				windmillStatus = {
					status: data.status === 'healthy' ? 'online' : 'offline',
					version: data.windmill_version?.version
				};
			} else {
				windmillStatus = {status: 'offline'};
			}
		} catch {
			windmillStatus = {status: 'offline'};
		}
	}

	onMount(async () => {
		workflows = workflowsData;
		await checkWindmill();
		loading = false;
	});

	function getStatusColor(status: string) {
		switch (status) {
			case 'active': return 'var(--terminal-green)';
			case 'online': return 'var(--terminal-green)';
			case 'ready': return 'var(--cyan-data, #00d4ff)';
			case 'planned': return 'var(--text-muted)';
			case 'offline': return 'var(--neon-pink)';
			default: return 'var(--text-muted)';
		}
	}

	const categories = ['sales', 'customer', 'marketing', 'ops', 'finance', 'service'];
</script>

<div class="page">
	<div class="page-header">
		<h2 class="glitch">Workflows // Integrations</h2>
		<div class="header-meta">
			<span class="meta-item">Skills + MCPs</span>
			<span class="meta-item">No n8n</span>
		</div>
	</div>

	{#if loading}
		<div class="loading">LOADING...</div>
	{:else}
		<div class="grid-2col">
			<!-- Left Column: Integrations -->
			<div class="column">
				<!-- MCP Servers -->
				<div class="section">
					<h3>MCP_SERVERS</h3>
					<p class="hint">Model Context Protocol integrations</p>
					<div class="services-list">
						{#each mcpServers as service}
							<div class="service-item" style="border-left-color: {getStatusColor(service.status)}">
								<div class="service-info">
									<span class="service-name">{service.name}</span>
									<span class="service-note">{service.note}</span>
								</div>
								<span class="service-status" style="background: {getStatusColor(service.status)}">{service.status.toUpperCase()}</span>
							</div>
						{/each}
					</div>
				</div>

				<!-- External Services -->
				<div class="section">
					<h3>EXTERNAL_SERVICES</h3>
					<p class="hint">Third-party systems</p>
					<div class="services-list">
						{#each externalServices as service}
							<a href={service.url} target="_blank" class="service-item" style="border-left-color: {getStatusColor(service.status)}">
								<div class="service-info">
									<span class="service-name">{service.name}</span>
									<span class="service-note">{service.note}</span>
								</div>
								<span class="service-status" style="background: {getStatusColor(service.status)}">{service.status.toUpperCase()}</span>
							</a>
						{/each}
					</div>
				</div>

				<!-- Windmill Workflow Engine -->
				<div class="section" style="border-color: var(--cyan-data, #00d4ff)">
					<h3>WINDMILL</h3>
					<p class="hint">Open-source workflow automation engine</p>
					<div class="windmill-status">
						<div class="service-item" style="border-left-color: {getStatusColor(windmillStatus.status)}">
							<div class="service-info">
								<span class="service-name">Windmill Engine</span>
								<span class="service-note">{windmillStatus.version || 'Checking...'}</span>
							</div>
							<span class="service-status" style="background: {getStatusColor(windmillStatus.status)}">
								{windmillStatus.status.toUpperCase()}
							</span>
						</div>
					</div>
					<div class="windmill-links">
						<code>API: http://127.0.0.1:8101</code>
						<code>UI: http://127.0.0.1:8100</code>
					</div>
					<p class="hint" style="margin-top: 8px">Access via SSH tunnel or local browser</p>
				</div>

				<!-- Strategy -->
				<div class="section strategy">
					<h3>STRATEGY</h3>
					<div class="strategy-content">
						<p><strong>Skills</strong> = workflow definitions</p>
						<p><strong>MCPs</strong> = integrations</p>
						<p><strong>Agents</strong> = execution</p>
					</div>
					<code>/github/.claude/skills/workflows/</code>
				</div>
			</div>

			<!-- Right Column: Workflows -->
			<div class="column">
				{#each categories as category}
					{@const categoryWorkflows = workflows.filter(w => w.category === category)}
					{#if categoryWorkflows.length > 0}
						<div class="section">
							<h3>{category.toUpperCase()}</h3>
							<div class="workflows-list">
								{#each categoryWorkflows as workflow}
									<div class="workflow-card" style="border-left-color: {getStatusColor(workflow.status)}">
										<div class="workflow-header">
											<span class="workflow-name">{workflow.name}</span>
											<span class="workflow-status" style="background: {getStatusColor(workflow.status)}">
												{workflow.status.toUpperCase()}
											</span>
										</div>
										<p class="workflow-desc">{workflow.description}</p>
										<div class="workflow-meta">
											<span class="trigger">{workflow.trigger}</span>
										</div>
									</div>
								{/each}
							</div>
						</div>
					{/if}
				{/each}
			</div>
		</div>
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
	}

	.header-meta {
		display: flex;
		gap: 12px;
	}

	.meta-item {
		font-size: 10px;
		padding: 4px 8px;
		background: var(--terminal-green);
		color: var(--void);
		font-weight: 700;
	}

	.loading {
		padding: 40px;
		text-align: center;
		color: var(--text-muted);
		font-size: 12px;
		text-transform: uppercase;
	}

	.grid-2col {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 20px;
	}

	.column {
		display: flex;
		flex-direction: column;
		gap: 16px;
	}

	.section {
		background: var(--surface);
		border: 2px solid var(--border);
		padding: 16px;
		box-shadow: 4px 4px 0 0 var(--border);
	}

	.section h3 {
		font-size: 11px;
		font-weight: 700;
		margin: 0 0 12px 0;
		text-transform: uppercase;
	}

	.hint {
		font-size: 10px;
		color: var(--text-muted);
		margin-bottom: 12px;
	}

	.services-list {
		display: flex;
		flex-direction: column;
		gap: 8px;
	}

	.service-item {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 10px 12px;
		background: rgba(255, 255, 255, 0.02);
		border: 1px solid var(--border);
		border-left-width: 3px;
		text-decoration: none;
		color: inherit;
		transition: all 0.1s ease;
	}

	.service-item:hover {
		border-color: var(--terminal-green);
		background: rgba(51, 255, 0, 0.05);
	}

	.service-info {
		display: flex;
		flex-direction: column;
		gap: 2px;
	}

	.service-name {
		font-size: 11px;
		font-weight: 600;
	}

	.service-note {
		font-size: 9px;
		color: var(--text-muted);
	}

	.service-status {
		font-size: 9px;
		font-weight: 700;
		padding: 2px 6px;
		color: var(--void);
	}

	.strategy {
		border-color: var(--terminal-green);
	}

	.strategy-content {
		font-size: 10px;
		line-height: 1.6;
		margin-bottom: 12px;
	}

	.strategy-content p {
		margin: 2px 0;
	}

	.section code {
		display: block;
		padding: 8px;
		background: rgba(0, 0, 0, 0.3);
		font-size: 9px;
		color: var(--cyan-data, #00d4ff);
		border: 1px solid var(--border);
	}

	.windmill-links {
		display: flex;
		flex-direction: column;
		gap: 4px;
		margin-top: 12px;
	}

	.windmill-links code {
		margin: 0;
	}

	.workflows-list {
		display: flex;
		flex-direction: column;
		gap: 10px;
	}

	.workflow-card {
		padding: 12px;
		background: rgba(255, 255, 255, 0.02);
		border: 1px solid var(--border);
		border-left-width: 3px;
	}

	.workflow-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 6px;
	}

	.workflow-name {
		font-size: 11px;
		font-weight: 700;
		font-family: 'JetBrains Mono', monospace;
	}

	.workflow-status {
		font-size: 9px;
		font-weight: 700;
		padding: 2px 6px;
		color: var(--void);
	}

	.workflow-desc {
		font-size: 10px;
		color: var(--text-muted);
		margin: 0 0 8px 0;
	}

	.workflow-meta {
		font-size: 9px;
		color: var(--text-muted);
	}

	@media (max-width: 900px) {
		.grid-2col {
			grid-template-columns: 1fr;
		}
	}
</style>
