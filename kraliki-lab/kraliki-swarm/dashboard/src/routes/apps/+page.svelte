<script lang="ts">
	import { onMount } from 'svelte';

	interface App {
		id: string;
		name: string;
		tagline: string;
		description: string;
		icon: string;
		status: 'live' | 'beta' | 'coming_soon' | 'internal';
		tier: 'free' | 'starter' | 'pro' | 'enterprise';
		category: 'productivity' | 'communication' | 'ai_tools' | 'education' | 'business';
		url?: string;
		features: string[];
		price?: string;
	}

	interface IntegrationStatus {
		name: string;
		status: 'online' | 'offline' | 'unknown';
	}

	const isDevHost =
		typeof window !== 'undefined' && window.location.hostname.endsWith('verduona.dev');
	const appDomain = isDevHost ? 'verduona.dev' : 'kraliki.com';
	const kralikiUrl = isDevHost ? 'https://kraliki.verduona.dev' : 'https://kraliki.com';

	const apps: App[] = [
		// THE PLATFORM
		{
			id: 'kraliki',
			name: 'Kraliki',
			tagline: 'AI Swarm Automation Platform',
			description: 'Self-organizing AI agent swarm that runs your business 24/7. 41 specialized agents across 4 CLI engines coordinate via blackboard, execute tasks autonomously, and continuously improve. This dashboard is the control center.',
			icon: '🐰',
			status: 'live',
			tier: 'enterprise',
			category: 'ai_tools',
			url: kralikiUrl,
			features: ['41 Agent Swarm', 'Autonomous Task Execution', 'Multi-CLI Coordination', 'Self-Organizing System', 'Real-Time Monitoring'],
			price: 'Platform Foundation'
		},

		// CUSTOMER-FACING APPS (by customer journey)
		{
			id: 'focus',
			name: 'Focus by Kraliki',
			tagline: 'AI-First Project Management',
			description: 'Pomodoro timer, task management, AI-powered calendar, and execution insights. Turn strategy into action with focus sessions and Linear sync.',
			icon: '🎯',
			status: 'beta',
			tier: 'free',
			category: 'productivity',
			url: `https://focus.${appDomain}`,
			features: ['Pomodoro Timer', 'Task Management', 'AI Calendar', 'Linear Integration', 'Voice Commands'],
			price: 'Free / Pro €9.99/mo'
		},
		{
			id: 'voice',
			name: 'Voice by Kraliki',
			tagline: 'AI Call Center Platform',
			description: 'AI-powered voice and chat support platform. Handle customer calls, chat sessions, and gain real-time insights. Scale your support without scaling headcount.',
			icon: '📞',
			status: 'beta',
			tier: 'pro',
			category: 'communication',
			url: `https://voice.${appDomain}`,
			features: ['Voice Calls', 'AI Transcription', 'Chat Sessions', 'Call Analytics', 'Team Management'],
			price: 'From €29/mo'
		},
		{
			id: 'speak',
			name: 'Speak by Kraliki',
			tagline: 'Employee Feedback & Surveys',
			description: 'Collect voice and text feedback from employees and customers. AI-powered sentiment analysis extracts insights automatically. Know what your team really thinks.',
			icon: '🗣️',
			status: 'beta',
			tier: 'starter',
			category: 'business',
			url: `https://speak.${appDomain}`,
			features: ['Voice Surveys', 'Text Feedback', 'Sentiment Analysis', 'Real-time Dashboard', 'Export Reports'],
			price: 'From €19/mo'
		},
		{
			id: 'lab',
			name: 'Lab by Kraliki',
			tagline: 'Private AI Workstation',
			description: 'VM fleet management platform. Deploy private AI workstations with Claude, GPT-4, Gemini orchestration for teams. Your own AI infrastructure.',
			icon: '⚡',
			status: 'beta',
			tier: 'enterprise',
			category: 'ai_tools',
			url: `https://lab.${appDomain}`,
			features: ['VM Fleet Management', 'Multi-Model Access', 'Usage Monitoring', 'Team Workspaces', 'One-Click Deploy'],
			price: 'From €49/mo per seat'
		},
		{
			id: 'learn',
			name: 'Learn by Kraliki',
			tagline: 'AI Academy & Client Onboarding',
			description: 'Business-focused learning platform. Client onboarding courses, AI Academy L1-L4 certification, and product tutorials. Your team learns AI while they work.',
			icon: '📚',
			status: 'beta',
			tier: 'starter',
			category: 'education',
			url: `https://learn.${appDomain}`,
			features: ['AI Academy L1-L4', 'Client Onboarding', 'Progress Tracking', 'Certifications', 'Team Training'],
			price: 'L1 Free / L2-L4 from €197'
		},
		{
			id: 'sense',
			name: 'Sense by Kraliki',
			tagline: 'AI Readiness Assessment',
			description: 'Comprehensive AI audit for your organization. Get AI readiness scores, automation opportunities, ROI calculations, and implementation roadmaps. Know where you stand.',
			icon: '🔍',
			status: 'beta',
			tier: 'enterprise',
			category: 'business',
			url: `https://sense.${appDomain}`,
			features: ['AI Readiness Score', 'Automation Opportunities', 'ROI Calculator', 'Implementation Roadmap', 'Expert Consultation'],
			price: 'From €499 (one-time)'
		}
	];

	let integrations = $state<IntegrationStatus[]>([]);
	let loading = $state(true);
	let selectedCategory = $state<string>('all');
	let selectedTier = $state<string>('all');

	const categories = [
		{ id: 'all', label: 'All Apps', icon: '📱' },
		{ id: 'productivity', label: 'Productivity', icon: '🎯' },
		{ id: 'communication', label: 'Communication', icon: '💬' },
		{ id: 'ai_tools', label: 'AI Tools', icon: '🤖' },
		{ id: 'education', label: 'Education', icon: '📚' },
		{ id: 'business', label: 'Business', icon: '💼' },
	];

	const tiers = [
		{ id: 'all', label: 'All Tiers' },
		{ id: 'free', label: 'Free' },
		{ id: 'starter', label: 'Starter' },
		{ id: 'pro', label: 'Pro' },
		{ id: 'enterprise', label: 'Enterprise' },
	];

	async function checkIntegrations() {
		try {
			const res = await fetch('/api/integrations');
			if (res.ok) {
				const data = await res.json();
				integrations = data.integrations || [];
			}
		} catch {
			// Ignore errors
		} finally {
			loading = false;
		}
	}

	function getAppStatus(appId: string): 'online' | 'offline' | 'unknown' {
		const mapping: Record<string, string> = {
			'focus': 'Focus by Kraliki',
			'voice': 'Voice by Kraliki',
			'speak': 'Speak by Kraliki',
			'learn': 'Learn by Kraliki',
			'lab': 'Lab by Kraliki',
			'sense': 'Sense by Kraliki',
		};
		const integration = integrations.find(i => i.name === mapping[appId]);
		return integration?.status || 'unknown';
	}

	onMount(() => {
		checkIntegrations();
	});

	const filteredApps = $derived(
		apps.filter(app => {
			if (selectedCategory !== 'all' && app.category !== selectedCategory) return false;
			if (selectedTier !== 'all' && app.tier !== selectedTier) return false;
			return true;
		})
	);

	function getStatusBadgeClass(status: string): string {
		switch (status) {
			case 'live': return 'status-live';
			case 'beta': return 'status-beta';
			case 'coming_soon': return 'status-soon';
			case 'internal': return 'status-internal';
			default: return '';
		}
	}

	function getTierBadgeClass(tier: string): string {
		switch (tier) {
			case 'free': return 'tier-free';
			case 'starter': return 'tier-starter';
			case 'pro': return 'tier-pro';
			case 'enterprise': return 'tier-enterprise';
			default: return '';
		}
	}
</script>

<div class="page">
	<div class="page-header">
		<div>
			<h2 class="glitch">Apps // Verduona Portfolio</h2>
			<p class="subtitle">AI-powered tools for modern businesses</p>
		</div>
		<div class="header-stats">
			<span class="stat-pill">{apps.filter(a => a.status === 'beta' || a.status === 'live').length} LIVE</span>
			<span class="stat-pill">{apps.filter(a => a.status === 'coming_soon').length} COMING SOON</span>
		</div>
	</div>

	<!-- Category Filters -->
	<div class="filter-section">
		<div class="filter-group">
			<span class="filter-label">CATEGORY:</span>
			{#each categories as cat}
				<button
					class="filter-btn"
					class:active={selectedCategory === cat.id}
					onclick={() => selectedCategory = cat.id}
				>
					<span>{cat.icon}</span> {cat.label}
				</button>
			{/each}
		</div>
		<div class="filter-group">
			<span class="filter-label">TIER:</span>
			{#each tiers as tier}
				<button
					class="filter-btn small"
					class:active={selectedTier === tier.id}
					onclick={() => selectedTier = tier.id}
				>
					{tier.label}
				</button>
			{/each}
		</div>
	</div>

	<!-- Apps Grid -->
	<div class="apps-grid">
		{#each filteredApps as app}
			<div class="app-card" class:internal={app.status === 'internal'}>
				<div class="app-header">
					<span class="app-icon">{app.icon}</span>
					<div class="app-badges">
						<span class="status-badge {getStatusBadgeClass(app.status)}">
							{app.status.replace('_', ' ').toUpperCase()}
						</span>
						<span class="tier-badge {getTierBadgeClass(app.tier)}">
							{app.tier.toUpperCase()}
						</span>
					</div>
				</div>

				<h3 class="app-name">{app.name}</h3>
				<p class="app-tagline">{app.tagline}</p>
				<p class="app-description">{app.description}</p>

				<div class="app-features">
					{#each app.features.slice(0, 3) as feature}
						<span class="feature-tag">{feature}</span>
					{/each}
					{#if app.features.length > 3}
						<span class="feature-more">+{app.features.length - 3} more</span>
					{/if}
				</div>

				<div class="app-footer">
					<span class="app-price">{app.price || 'Contact Us'}</span>
					<div class="app-actions">
						{#if app.status === 'beta' || app.status === 'live'}
							{#if app.url}
								<a href={app.url} target="_blank" class="brutal-btn small">
									OPEN APP
								</a>
							{/if}
						{:else if app.status === 'coming_soon'}
							<button class="brutal-btn small disabled" disabled>
								NOTIFY ME
							</button>
						{:else}
							<span class="internal-label">INTERNAL</span>
						{/if}
					</div>
				</div>

				{#if app.status === 'beta' || app.status === 'live'}
					{@const status = getAppStatus(app.id)}
					{#if status === 'online'}
						<div class="app-status-bar online">● SERVICE ONLINE</div>
					{:else if status === 'offline'}
						<div class="app-status-bar offline">○ SERVICE OFFLINE</div>
					{/if}
				{/if}
			</div>
		{/each}
	</div>

	<!-- Upgrade CTA -->
	<div class="upgrade-section">
		<div class="upgrade-content">
			<h3>Unlock the Full Kraliki Suite</h3>
			<p>Get access to all apps with a Pro or Enterprise subscription. One login, all tools.</p>
			<div class="upgrade-tiers">
				<div class="tier-card">
					<h4>Starter</h4>
					<p class="tier-price">€29/mo</p>
					<ul>
						<li>3 Apps</li>
						<li>Basic Support</li>
						<li>5 Team Members</li>
					</ul>
				</div>
				<div class="tier-card featured">
					<span class="featured-badge">POPULAR</span>
					<h4>Pro</h4>
					<p class="tier-price">€99/mo</p>
					<ul>
						<li>All Apps</li>
						<li>Priority Support</li>
						<li>Unlimited Team</li>
						<li>API Access</li>
					</ul>
				</div>
				<div class="tier-card">
					<h4>Enterprise</h4>
					<p class="tier-price">Custom</p>
					<ul>
						<li>All Apps + Kraliki</li>
						<li>Dedicated Support</li>
						<li>Custom Integrations</li>
						<li>On-Premise Option</li>
					</ul>
				</div>
			</div>
		</div>
	</div>
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
		align-items: flex-start;
		border-bottom: 2px solid var(--border);
		padding-bottom: 16px;
	}

	.subtitle {
		color: var(--text-muted);
		font-size: 12px;
		margin-top: 4px;
	}

	.header-stats {
		display: flex;
		gap: 8px;
	}

	.stat-pill {
		padding: 6px 12px;
		font-size: 10px;
		font-weight: 700;
		border: 2px solid var(--border);
		font-family: 'JetBrains Mono', monospace;
	}

	/* Filters */
	.filter-section {
		display: flex;
		flex-direction: column;
		gap: 12px;
	}

	.filter-group {
		display: flex;
		align-items: center;
		gap: 8px;
		flex-wrap: wrap;
	}

	.filter-label {
		font-size: 10px;
		color: var(--text-muted);
		font-weight: 700;
		min-width: 80px;
	}

	.filter-btn {
		padding: 8px 16px;
		font-size: 11px;
		font-family: 'JetBrains Mono', monospace;
		background: var(--surface);
		border: 2px solid var(--border);
		color: var(--text-muted);
		cursor: pointer;
		display: flex;
		align-items: center;
		gap: 6px;
		transition: all 0.1s ease;
	}

	.filter-btn.small {
		padding: 6px 12px;
		font-size: 10px;
	}

	.filter-btn:hover, .filter-btn.active {
		border-color: var(--terminal-green);
		color: var(--terminal-green);
	}

	/* Apps Grid */
	.apps-grid {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
		gap: 20px;
	}

	.app-card {
		background: var(--surface);
		border: 2px solid var(--border);
		padding: 24px;
		position: relative;
		transition: all 0.1s ease;
		box-shadow: 4px 4px 0 0 var(--border);
	}

	.app-card:hover {
		border-color: var(--terminal-green);
		transform: translate(-2px, -2px);
		box-shadow: 6px 6px 0 0 var(--terminal-green);
	}

	.app-card.internal {
		border-style: dashed;
		opacity: 0.8;
	}

	.app-header {
		display: flex;
		justify-content: space-between;
		align-items: flex-start;
		margin-bottom: 12px;
	}

	.app-icon {
		font-size: 40px;
	}

	.app-badges {
		display: flex;
		gap: 6px;
	}

	.status-badge, .tier-badge {
		font-size: 9px;
		padding: 4px 8px;
		font-weight: 700;
		font-family: 'JetBrains Mono', monospace;
	}

	.status-badge.status-live {
		background: var(--terminal-green);
		color: var(--void);
	}

	.status-badge.status-beta {
		background: var(--cyan-data, #00d4ff);
		color: var(--void);
	}

	.status-badge.status-soon {
		background: var(--warning, #ffaa00);
		color: var(--void);
	}

	.status-badge.status-internal {
		background: var(--border);
		color: var(--text-main);
	}

	.tier-badge.tier-free {
		border: 1px solid var(--terminal-green);
		color: var(--terminal-green);
	}

	.tier-badge.tier-starter {
		border: 1px solid var(--cyan-data, #00d4ff);
		color: var(--cyan-data, #00d4ff);
	}

	.tier-badge.tier-pro {
		border: 1px solid var(--magenta-pulse, #ff00ff);
		color: var(--magenta-pulse, #ff00ff);
	}

	.tier-badge.tier-enterprise {
		border: 1px solid var(--warning, #ffaa00);
		color: var(--warning, #ffaa00);
	}

	.app-name {
		font-size: 18px;
		font-weight: 700;
		margin: 0 0 4px 0;
		color: var(--text-main);
	}

	.app-tagline {
		font-size: 12px;
		color: var(--terminal-green);
		margin: 0 0 12px 0;
		font-weight: 600;
	}

	.app-description {
		font-size: 12px;
		color: var(--text-muted);
		line-height: 1.5;
		margin: 0 0 16px 0;
	}

	.app-features {
		display: flex;
		flex-wrap: wrap;
		gap: 6px;
		margin-bottom: 16px;
	}

	.feature-tag {
		font-size: 9px;
		padding: 4px 8px;
		background: rgba(255, 255, 255, 0.05);
		border: 1px solid var(--border);
		color: var(--text-muted);
	}

	.feature-more {
		font-size: 9px;
		padding: 4px 8px;
		color: var(--text-muted);
		font-style: italic;
	}

	.app-footer {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding-top: 16px;
		border-top: 1px solid var(--border);
	}

	.app-price {
		font-size: 11px;
		color: var(--text-muted);
		font-family: 'JetBrains Mono', monospace;
	}

	.app-actions {
		display: flex;
		gap: 8px;
	}

	.app-status-bar {
		position: absolute;
		bottom: 0;
		left: 0;
		right: 0;
		padding: 4px;
		font-size: 9px;
		font-weight: 700;
		text-align: center;
		font-family: 'JetBrains Mono', monospace;
	}

	.app-status-bar.online {
		background: var(--terminal-green);
		color: var(--void);
	}

	.app-status-bar.offline {
		background: var(--border);
		color: var(--text-muted);
	}

	.internal-label {
		font-size: 10px;
		color: var(--text-muted);
		font-style: italic;
	}

	/* Buttons */
	.brutal-btn {
		background: var(--surface);
		border: 2px solid var(--terminal-green);
		color: var(--terminal-green);
		padding: 10px 20px;
		font-family: 'JetBrains Mono', monospace;
		font-size: 11px;
		font-weight: 700;
		text-transform: uppercase;
		cursor: pointer;
		text-decoration: none;
		display: inline-block;
		transition: all 0.1s ease;
	}

	.brutal-btn:hover:not(:disabled) {
		background: var(--terminal-green);
		color: var(--void);
	}

	.brutal-btn.small {
		padding: 6px 12px;
		font-size: 10px;
	}

	.brutal-btn.outline {
		border-style: dashed;
	}

	.brutal-btn.outline.offline {
		border-color: var(--text-muted);
		color: var(--text-muted);
	}

	.brutal-btn.disabled, .brutal-btn:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}

	/* Upgrade Section */
	.upgrade-section {
		background: var(--surface);
		border: 2px solid var(--terminal-green);
		padding: 32px;
		margin-top: 24px;
		box-shadow: 4px 4px 0 0 var(--terminal-green);
	}

	.upgrade-content {
		text-align: center;
	}

	.upgrade-content h3 {
		font-size: 20px;
		margin: 0 0 8px 0;
		color: var(--terminal-green);
	}

	.upgrade-content > p {
		color: var(--text-muted);
		font-size: 12px;
		margin: 0 0 24px 0;
	}

	.upgrade-tiers {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
		gap: 20px;
		max-width: 800px;
		margin: 0 auto;
	}

	.tier-card {
		background: rgba(255, 255, 255, 0.02);
		border: 2px solid var(--border);
		padding: 24px;
		text-align: center;
		position: relative;
	}

	.tier-card.featured {
		border-color: var(--terminal-green);
		box-shadow: 0 0 20px rgba(51, 255, 0, 0.1);
	}

	.featured-badge {
		position: absolute;
		top: -12px;
		left: 50%;
		transform: translateX(-50%);
		background: var(--terminal-green);
		color: var(--void);
		font-size: 9px;
		font-weight: 700;
		padding: 4px 12px;
	}

	.tier-card h4 {
		font-size: 16px;
		margin: 0 0 8px 0;
		color: var(--text-main);
	}

	.tier-price {
		font-size: 24px;
		font-weight: 700;
		color: var(--terminal-green);
		margin: 0 0 16px 0;
		font-family: 'JetBrains Mono', monospace;
	}

	.tier-card ul {
		list-style: none;
		padding: 0;
		margin: 0;
	}

	.tier-card li {
		font-size: 11px;
		color: var(--text-muted);
		padding: 6px 0;
		border-bottom: 1px solid var(--border);
	}

	.tier-card li:last-child {
		border-bottom: none;
	}

	@media (max-width: 768px) {
		.apps-grid {
			grid-template-columns: 1fr;
		}

		.page-header {
			flex-direction: column;
			gap: 12px;
		}

		.filter-group {
			flex-direction: column;
			align-items: flex-start;
		}

		.filter-label {
			min-width: auto;
		}
	}
</style>
