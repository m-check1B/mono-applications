<script lang="ts">
	import { onMount } from 'svelte';

	interface Channel {
		id: string;
		name: string;
		icon: string;
		status: 'active' | 'inactive' | 'coming';
		provider: string;
		inbound: number;
		outbound: number;
	}

	interface Campaign {
		id: string;
		name: string;
		type: 'inbound' | 'outbound';
		status: 'active' | 'paused' | 'completed' | 'draft';
		channel: string;
		progress?: number;
	}

	interface Agent {
		id: string;
		name: string;
		type: 'voice' | 'chat' | 'email';
		status: 'available' | 'busy' | 'offline';
		callsToday: number;
		successRate: number;
	}

	interface QueueItem {
		id: string;
		channel: string;
		status: string;
		caller?: string;
		waitTime: number;
		startedAt: string;
	}

	const channelIcons: Record<string, string> = {
		voice: '📞',
		sms: '💬',
		email: '📧',
		chat: '🗨️',
		social: '🌐'
	};

	let voiceStatus = $state<'online' | 'offline' | 'checking'>('checking');
	const isDevHost =
		typeof window !== 'undefined' && window.location.hostname.endsWith('verduona.dev');
	let voiceUrl = isDevHost ? 'https://voice.verduona.dev' : 'https://voice.kraliki.com';
	let localVoiceUrl = 'http://127.0.0.1:5000';

	let channels = $state<Channel[]>([]);
	let campaigns = $state<Campaign[]>([]);
	let agents = $state<Agent[]>([]);
	let queueItems = $state<QueueItem[]>([]);

	let loading = $state(true);
	let activeTab = $state<'overview' | 'inbound' | 'outbound' | 'agents'>('overview');

	async function fetchReachStats() {
		voiceStatus = 'checking';
		try {
			const res = await fetch('/api/reach', {
				signal: AbortSignal.timeout(5000)
			});
			if (res.ok) {
				const data = await res.json();
				voiceStatus = data.voiceStatus;
				channels = data.channels.map((c: { id: string; name: string; status: string; provider: string; inbound: number; outbound: number }) => ({
					...c,
					icon: channelIcons[c.id] || '📡'
				}));
			} else {
				voiceStatus = 'offline';
			}
		} catch {
			voiceStatus = 'offline';
		}
		loading = false;
	}

	async function fetchCampaigns() {
		try {
			const res = await fetch('/api/reach/campaigns', {
				signal: AbortSignal.timeout(5000)
			});
			if (res.ok) {
				const data = await res.json();
				campaigns = data.campaigns || [];
			}
		} catch {
			// Silent fail
		}
	}

	async function fetchAgents() {
		try {
			const res = await fetch('/api/reach/agents', {
				signal: AbortSignal.timeout(5000)
			});
			if (res.ok) {
				const data = await res.json();
				agents = data.agents || [];
			}
		} catch {
			// Silent fail
		}
	}

	async function fetchQueue() {
		try {
			const res = await fetch('/api/reach/queue', {
				signal: AbortSignal.timeout(5000)
			});
			if (res.ok) {
				const data = await res.json();
				queueItems = data.items || [];
			}
		} catch {
			// Silent fail
		}
	}

	async function refreshAll() {
		await Promise.all([
			fetchReachStats(),
			fetchCampaigns(),
			fetchAgents(),
			fetchQueue()
		]);
	}

	onMount(() => {
		refreshAll();
		const interval = setInterval(refreshAll, 30000);
		return () => clearInterval(interval);
	});

	const totalInbound = $derived(channels.reduce((sum, c) => sum + c.inbound, 0));
	const totalOutbound = $derived(channels.reduce((sum, c) => sum + c.outbound, 0));
	const activeChannels = $derived(channels.filter(c => c.status === 'active').length);
	const activeCampaigns = $derived(campaigns.filter(c => c.status === 'active').length);
	const availableAgents = $derived(agents.filter(a => a.status === 'available').length);
	const waitingQueue = $derived(queueItems.filter(q => q.status === 'waiting').length);
</script>

<div class="page">
	<div class="page-header">
		<h2 class="glitch">Reach // Unified Communication</h2>
		<div class="header-badges">
			<span class="status-badge">{activeChannels}/{channels.length} CHANNELS</span>
			<span class="voice-badge {voiceStatus}">
				{#if voiceStatus === 'checking'}
					VOICE: CHECKING...
				{:else if voiceStatus === 'online'}
					VOICE: ONLINE
				{:else}
					VOICE: OFFLINE
				{/if}
			</span>
		</div>
	</div>

	<!-- Voice by Kraliki Integration Banner -->
	<div class="integration-banner" class:online={voiceStatus === 'online'}>
		<div class="banner-content">
			<span class="banner-icon">📞</span>
			<div class="banner-text">
				<strong>Voice Engine: Voice by Kraliki</strong>
				<span>AI-powered call center for inbound/outbound voice communication</span>
			</div>
			<div class="banner-actions">
				<a href={voiceUrl} target="_blank" class="brutal-btn small">OPEN VOICE</a>
				{#if voiceStatus === 'online'}
					<a href={localVoiceUrl} target="_blank" class="brutal-btn small outline">LOCAL</a>
				{/if}
			</div>
		</div>
	</div>

	<!-- Tab Navigation -->
	<div class="reach-tabs">
		<button class="reach-tab" class:active={activeTab === 'overview'} onclick={() => activeTab = 'overview'}>
			OVERVIEW
		</button>
		<button class="reach-tab" class:active={activeTab === 'inbound'} onclick={() => activeTab = 'inbound'}>
			INBOUND
		</button>
		<button class="reach-tab" class:active={activeTab === 'outbound'} onclick={() => activeTab = 'outbound'}>
			OUTBOUND
		</button>
		<button class="reach-tab" class:active={activeTab === 'agents'} onclick={() => activeTab = 'agents'}>
			AI_AGENTS
		</button>
	</div>

	{#if activeTab === 'overview'}
		<!-- Stats Overview -->
		<div class="stats-row">
			<div class="stat-card">
				<span class="stat-value">{totalInbound}</span>
				<span class="stat-label">INBOUND_TODAY</span>
			</div>
			<div class="stat-card">
				<span class="stat-value">{totalOutbound}</span>
				<span class="stat-label">OUTBOUND_TODAY</span>
			</div>
			<div class="stat-card">
				<span class="stat-value">{activeChannels}</span>
				<span class="stat-label">ACTIVE_CHANNELS</span>
			</div>
			<div class="stat-card">
				<span class="stat-value">--</span>
				<span class="stat-label">RESPONSE_RATE</span>
			</div>
		</div>

		<!-- Channel Status -->
		<div class="section">
			<h3>CHANNELS</h3>
			<div class="channels-grid">
				{#each channels as channel}
					<div class="channel-card" class:coming={channel.status === 'coming'} class:active={channel.status === 'active'}>
						<div class="channel-header">
							<span class="channel-icon">{channel.icon}</span>
							<span class="channel-name">{channel.name}</span>
							<span class="channel-status" class:active={channel.status === 'active'} class:coming={channel.status === 'coming'}>
								{channel.status.toUpperCase()}
							</span>
						</div>
						<div class="channel-provider">
							via {channel.provider}
						</div>
						<div class="channel-stats">
							<div class="channel-stat">
								<span class="stat-num">{channel.inbound}</span>
								<span class="stat-lbl">IN</span>
							</div>
							<div class="channel-stat">
								<span class="stat-num">{channel.outbound}</span>
								<span class="stat-lbl">OUT</span>
							</div>
						</div>
					</div>
				{/each}
			</div>
		</div>

		<!-- Architecture -->
		<div class="section">
			<h3>ARCHITECTURE</h3>
			<div class="arch-diagram">
				<div class="arch-box kraliki">
					<div class="arch-title">KRALIKI</div>
					<div class="arch-content">
						<div class="arch-item">Reach UI (this page)</div>
						<div class="arch-item">Orchestration</div>
						<div class="arch-item">Multi-call flows</div>
					</div>
				</div>
				<div class="arch-arrow">→ uses →</div>
				<div class="arch-box voice">
					<div class="arch-title">VOICE BY KRALIKI</div>
					<div class="arch-content">
						<div class="arch-item">Voice Engine</div>
						<div class="arch-item">Call Handling</div>
						<div class="arch-item">Voice AI Agents</div>
					</div>
				</div>
			</div>
		</div>

		<!-- Integration Status -->
		<div class="section">
			<h3>INTEGRATION STATUS</h3>
			<div class="checklist">
				<div class="check-item {voiceStatus === 'online' ? 'done' : 'pending'}">
					Voice by Kraliki Voice Integration
				</div>
				<div class="check-item pending">SMS Gateway</div>
				<div class="check-item pending">Email Integration</div>
				<div class="check-item pending">Chat Widget</div>
				<div class="check-item pending">Social APIs</div>
				<div class="check-item pending">Multi-call Orchestration</div>
			</div>
		</div>

	{:else if activeTab === 'inbound'}
		<!-- Inbound Stats -->
		<div class="stats-row mini">
			<div class="stat-card">
				<span class="stat-value">{waitingQueue}</span>
				<span class="stat-label">WAITING</span>
			</div>
			<div class="stat-card">
				<span class="stat-value">{totalInbound}</span>
				<span class="stat-label">TODAY</span>
			</div>
			<div class="stat-card">
				<span class="stat-value">{availableAgents}</span>
				<span class="stat-label">AGENTS_READY</span>
			</div>
		</div>

		<div class="section">
			<h3>INBOUND // Queue</h3>
			{#if queueItems.length > 0}
				<div class="queue-list">
					{#each queueItems as item}
						<div class="queue-item" class:waiting={item.status === 'waiting'}>
							<span class="queue-channel">{channelIcons[item.channel] || '📡'}</span>
							<div class="queue-info">
								<span class="queue-caller">{item.caller || 'Unknown'}</span>
								<span class="queue-time">{new Date(item.startedAt).toLocaleTimeString()}</span>
							</div>
							<span class="queue-status {item.status}">{item.status.toUpperCase()}</span>
						</div>
					{/each}
				</div>
			{:else}
				<div class="empty-state">
					<div class="empty-icon">📥</div>
					<p>No items in queue</p>
					<p class="hint">Inbound calls, messages, and emails will appear here</p>
					{#if voiceStatus === 'online'}
						<a href={voiceUrl} target="_blank" class="brutal-btn">MANAGE IN VOICE</a>
					{/if}
				</div>
			{/if}
		</div>

	{:else if activeTab === 'outbound'}
		<!-- Outbound Stats -->
		<div class="stats-row mini">
			<div class="stat-card">
				<span class="stat-value">{activeCampaigns}</span>
				<span class="stat-label">ACTIVE</span>
			</div>
			<div class="stat-card">
				<span class="stat-value">{campaigns.length}</span>
				<span class="stat-label">TOTAL</span>
			</div>
			<div class="stat-card">
				<span class="stat-value">{totalOutbound}</span>
				<span class="stat-label">SENT_TODAY</span>
			</div>
		</div>

		<div class="section">
			<h3>OUTBOUND // Campaigns</h3>
			{#if campaigns.length > 0}
				<div class="campaigns-list">
					{#each campaigns as campaign}
						<div class="campaign-card" class:active={campaign.status === 'active'}>
							<div class="campaign-header">
								<span class="campaign-name">{campaign.name}</span>
								<span class="campaign-status {campaign.status}">{campaign.status.toUpperCase()}</span>
							</div>
							<div class="campaign-meta">
								<span class="campaign-channel">{channelIcons[campaign.channel] || '📡'} {campaign.channel}</span>
								<span class="campaign-type">{campaign.type}</span>
							</div>
							{#if campaign.progress !== undefined}
								<div class="campaign-progress">
									<div class="progress-bar">
										<div class="progress-fill" style="width: {campaign.progress}%"></div>
									</div>
									<span class="progress-text">{campaign.progress}%</span>
								</div>
							{/if}
						</div>
					{/each}
				</div>
			{:else}
				<div class="empty-state">
					<div class="empty-icon">📤</div>
					<p>No campaigns configured</p>
					<p class="hint">Create campaigns in Voice by Kraliki to manage outbound calls</p>
					{#if voiceStatus === 'online'}
						<a href={voiceUrl} target="_blank" class="brutal-btn">CREATE CAMPAIGN</a>
					{/if}
				</div>
			{/if}
		</div>

	{:else if activeTab === 'agents'}
		<!-- Agents Stats -->
		<div class="stats-row mini">
			<div class="stat-card">
				<span class="stat-value">{availableAgents}</span>
				<span class="stat-label">AVAILABLE</span>
			</div>
			<div class="stat-card">
				<span class="stat-value">{agents.filter(a => a.status === 'busy').length}</span>
				<span class="stat-label">BUSY</span>
			</div>
			<div class="stat-card">
				<span class="stat-value">{agents.length}</span>
				<span class="stat-label">TOTAL</span>
			</div>
		</div>

		<div class="section">
			<h3>AI_AGENTS // Communication Agents</h3>
			<div class="agents-preview">
				{#each agents as agent}
					<div class="agent-type" class:active={agent.status === 'available'} class:busy={agent.status === 'busy'}>
						<span class="agent-icon">{agent.type === 'voice' ? '🗣️' : agent.type === 'chat' ? '💬' : '📧'}</span>
						<span class="agent-name">{agent.name}</span>
						<span class="agent-desc">
							{agent.callsToday} calls today | {agent.successRate}% success
						</span>
						<span class="agent-status {agent.status}">
							{agent.status.toUpperCase()}
						</span>
					</div>
				{/each}
				{#if agents.length === 0}
					<div class="agent-type" class:active={voiceStatus === 'online'}>
						<span class="agent-icon">🗣️</span>
						<span class="agent-name">Voice Agent</span>
						<span class="agent-desc">Powered by Voice by Kraliki</span>
						<span class="agent-status {voiceStatus === 'online' ? 'active' : 'coming'}">
							{voiceStatus === 'online' ? 'AVAILABLE' : 'OFFLINE'}
						</span>
					</div>
					<div class="agent-type">
						<span class="agent-icon">💬</span>
						<span class="agent-name">Chat Agent</span>
						<span class="agent-desc">Website chat, support tickets</span>
						<span class="agent-status coming">COMING</span>
					</div>
					<div class="agent-type">
						<span class="agent-icon">📧</span>
						<span class="agent-name">Email Agent</span>
						<span class="agent-desc">Email responses, follow-ups</span>
						<span class="agent-status coming">COMING</span>
					</div>
				{/if}
			</div>
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
		border-bottom: 2px solid var(--border);
		padding-bottom: 16px;
	}

	.header-badges {
		display: flex;
		gap: 12px;
		align-items: center;
	}

	.status-badge {
		padding: 8px 16px;
		font-family: 'JetBrains Mono', monospace;
		font-size: 11px;
		font-weight: 700;
		background: var(--surface);
		border: 2px solid var(--border);
		color: var(--text-muted);
	}

	.voice-badge {
		padding: 8px 16px;
		font-family: 'JetBrains Mono', monospace;
		font-size: 10px;
		font-weight: 700;
		border: 2px solid var(--border);
	}

	.voice-badge.checking {
		color: var(--text-muted);
	}

	.voice-badge.online {
		color: var(--terminal-green);
		border-color: var(--terminal-green);
		background: rgba(51, 255, 0, 0.1);
	}

	.voice-badge.offline {
		color: var(--text-muted);
		border-style: dashed;
	}

	/* Integration Banner */
	.integration-banner {
		background: var(--surface);
		border: 2px solid var(--border);
		padding: 16px 20px;
	}

	.integration-banner.online {
		border-color: var(--terminal-green);
	}

	.banner-content {
		display: flex;
		align-items: center;
		gap: 16px;
	}

	.banner-icon {
		font-size: 32px;
	}

	.banner-text {
		flex: 1;
		display: flex;
		flex-direction: column;
		gap: 4px;
	}

	.banner-text strong {
		font-size: 14px;
		color: var(--text-main);
	}

	.banner-text span {
		font-size: 12px;
		color: var(--text-muted);
	}

	.banner-actions {
		display: flex;
		gap: 8px;
	}

	/* Tabs */
	.reach-tabs {
		display: flex;
		gap: 8px;
		border-bottom: 2px solid var(--border);
		padding-bottom: 12px;
	}

	.reach-tab {
		padding: 10px 20px;
		background: var(--surface);
		border: 2px solid var(--border);
		color: var(--text-muted);
		font-family: 'JetBrains Mono', monospace;
		font-size: 11px;
		font-weight: 700;
		cursor: pointer;
		transition: all 0.1s ease;
	}

	.reach-tab:hover {
		border-color: var(--terminal-green);
		color: var(--terminal-green);
	}

	.reach-tab.active {
		background: var(--terminal-green);
		border-color: var(--terminal-green);
		color: var(--void);
	}

	/* Stats Row */
	.stats-row {
		display: grid;
		grid-template-columns: repeat(4, 1fr);
		gap: 16px;
	}

	.stat-card {
		background: var(--surface);
		border: 2px solid var(--border);
		padding: 20px;
		text-align: center;
		box-shadow: 4px 4px 0 0 var(--border);
	}

	.stat-value {
		display: block;
		font-family: 'JetBrains Mono', monospace;
		font-size: 32px;
		font-weight: 700;
		color: var(--terminal-green);
	}

	.stat-label {
		font-size: 10px;
		color: var(--text-muted);
		letter-spacing: 0.05em;
	}

	/* Sections */
	.section {
		background: var(--surface);
		border: 2px solid var(--border);
		padding: 20px;
		box-shadow: 4px 4px 0 0 var(--border);
	}

	.section h3 {
		font-size: 12px;
		font-weight: 700;
		margin: 0 0 16px 0;
		text-transform: uppercase;
		letter-spacing: 0.05em;
		color: var(--text-muted);
	}

	/* Channels Grid */
	.channels-grid {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
		gap: 12px;
	}

	.channel-card {
		padding: 16px;
		background: rgba(255, 255, 255, 0.02);
		border: 2px solid var(--border);
		transition: all 0.1s ease;
	}

	.channel-card:hover {
		border-color: var(--terminal-green);
	}

	.channel-card.coming {
		opacity: 0.6;
	}

	.channel-card.active {
		border-color: var(--terminal-green);
	}

	.channel-header {
		display: flex;
		align-items: center;
		gap: 8px;
		margin-bottom: 8px;
	}

	.channel-icon {
		font-size: 20px;
	}

	.channel-name {
		flex: 1;
		font-size: 12px;
		font-weight: 700;
	}

	.channel-status {
		font-size: 9px;
		padding: 2px 6px;
		border: 1px solid var(--border);
		color: var(--text-muted);
	}

	.channel-status.active {
		background: var(--terminal-green);
		border-color: var(--terminal-green);
		color: var(--void);
	}

	.channel-status.coming {
		border-color: var(--warning, #ffaa00);
		color: var(--warning, #ffaa00);
	}

	.channel-provider {
		font-size: 10px;
		color: var(--text-muted);
		margin-bottom: 12px;
	}

	.channel-stats {
		display: flex;
		gap: 16px;
	}

	.channel-stat {
		display: flex;
		align-items: baseline;
		gap: 4px;
	}

	.stat-num {
		font-family: 'JetBrains Mono', monospace;
		font-size: 18px;
		font-weight: 700;
		color: var(--terminal-green);
	}

	.stat-lbl {
		font-size: 9px;
		color: var(--text-muted);
	}

	/* Architecture Diagram */
	.arch-diagram {
		display: flex;
		align-items: center;
		justify-content: center;
		gap: 24px;
		padding: 24px;
	}

	.arch-box {
		border: 2px solid var(--border);
		padding: 20px;
		min-width: 180px;
	}

	.arch-box.kraliki {
		border-color: var(--terminal-green);
	}

	.arch-box.voice {
		border-color: var(--cyan-data, #00d4ff);
	}

	.arch-title {
		font-size: 12px;
		font-weight: 700;
		margin-bottom: 12px;
		color: var(--text-main);
	}

	.arch-content {
		display: flex;
		flex-direction: column;
		gap: 4px;
	}

	.arch-item {
		font-size: 10px;
		color: var(--text-muted);
	}

	.arch-arrow {
		font-family: 'JetBrains Mono', monospace;
		font-size: 12px;
		color: var(--text-muted);
	}

	/* Checklist */
	.checklist {
		display: flex;
		flex-wrap: wrap;
		gap: 8px;
	}

	.check-item {
		padding: 8px 16px;
		font-size: 11px;
		font-family: 'JetBrains Mono', monospace;
		border: 1px solid var(--border);
		color: var(--text-muted);
	}

	.check-item.pending::before {
		content: '○ ';
		color: var(--warning, #ffaa00);
	}

	.check-item.done {
		border-color: var(--terminal-green);
		color: var(--terminal-green);
	}

	.check-item.done::before {
		content: '✓ ';
	}

	/* Empty State */
	.empty-state {
		text-align: center;
		padding: 48px;
	}

	.empty-icon {
		font-size: 48px;
		margin-bottom: 16px;
	}

	.empty-state p {
		color: var(--text-main);
		margin-bottom: 8px;
	}

	.hint {
		font-size: 11px;
		color: var(--text-muted);
	}

	/* Agents Preview */
	.agents-preview {
		display: flex;
		flex-direction: column;
		gap: 12px;
	}

	.agent-type {
		display: flex;
		align-items: center;
		gap: 12px;
		padding: 16px;
		background: rgba(255, 255, 255, 0.02);
		border: 2px solid var(--border);
	}

	.agent-type.active {
		border-color: var(--terminal-green);
	}

	.agent-icon {
		font-size: 24px;
	}

	.agent-name {
		font-size: 14px;
		font-weight: 700;
		min-width: 120px;
	}

	.agent-desc {
		flex: 1;
		font-size: 12px;
		color: var(--text-muted);
	}

	.agent-status {
		font-size: 9px;
		padding: 4px 8px;
		font-weight: 700;
		border: 1px solid;
	}

	.agent-status.coming {
		border-color: var(--warning, #ffaa00);
		color: var(--warning, #ffaa00);
	}

	.agent-status.active {
		border-color: var(--terminal-green);
		color: var(--terminal-green);
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

	.brutal-btn:hover {
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

	/* Mini Stats Row */
	.stats-row.mini {
		grid-template-columns: repeat(3, 1fr);
		margin-bottom: 16px;
	}

	.stats-row.mini .stat-card {
		padding: 12px;
	}

	.stats-row.mini .stat-value {
		font-size: 24px;
	}

	/* Queue List */
	.queue-list {
		display: flex;
		flex-direction: column;
		gap: 8px;
	}

	.queue-item {
		display: flex;
		align-items: center;
		gap: 12px;
		padding: 12px 16px;
		background: rgba(255, 255, 255, 0.02);
		border: 2px solid var(--border);
		transition: all 0.1s ease;
	}

	.queue-item.waiting {
		border-color: var(--warning, #ffaa00);
		animation: pulse 2s infinite;
	}

	@keyframes pulse {
		0%, 100% { opacity: 1; }
		50% { opacity: 0.7; }
	}

	.queue-channel {
		font-size: 20px;
	}

	.queue-info {
		flex: 1;
		display: flex;
		flex-direction: column;
		gap: 2px;
	}

	.queue-caller {
		font-size: 13px;
		font-weight: 600;
	}

	.queue-time {
		font-size: 10px;
		color: var(--text-muted);
		font-family: 'JetBrains Mono', monospace;
	}

	.queue-status {
		font-size: 9px;
		padding: 4px 8px;
		font-weight: 700;
		font-family: 'JetBrains Mono', monospace;
		border: 1px solid var(--border);
	}

	.queue-status.waiting {
		color: var(--warning, #ffaa00);
		border-color: var(--warning, #ffaa00);
	}

	.queue-status.in_progress {
		color: var(--terminal-green);
		border-color: var(--terminal-green);
	}

	/* Campaigns List */
	.campaigns-list {
		display: flex;
		flex-direction: column;
		gap: 12px;
	}

	.campaign-card {
		padding: 16px;
		background: rgba(255, 255, 255, 0.02);
		border: 2px solid var(--border);
		transition: all 0.1s ease;
	}

	.campaign-card.active {
		border-color: var(--terminal-green);
	}

	.campaign-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 8px;
	}

	.campaign-name {
		font-size: 14px;
		font-weight: 700;
	}

	.campaign-status {
		font-size: 9px;
		padding: 4px 8px;
		font-weight: 700;
		font-family: 'JetBrains Mono', monospace;
		border: 1px solid var(--border);
	}

	.campaign-status.active {
		color: var(--terminal-green);
		border-color: var(--terminal-green);
	}

	.campaign-status.paused {
		color: var(--warning, #ffaa00);
		border-color: var(--warning, #ffaa00);
	}

	.campaign-status.completed {
		color: var(--text-muted);
	}

	.campaign-meta {
		display: flex;
		gap: 16px;
		font-size: 11px;
		color: var(--text-muted);
		margin-bottom: 12px;
	}

	.campaign-progress {
		display: flex;
		align-items: center;
		gap: 12px;
	}

	.progress-bar {
		flex: 1;
		height: 8px;
		background: var(--surface);
		border: 1px solid var(--border);
		overflow: hidden;
	}

	.progress-fill {
		height: 100%;
		background: var(--terminal-green);
		transition: width 0.3s ease;
	}

	.progress-text {
		font-size: 11px;
		font-family: 'JetBrains Mono', monospace;
		color: var(--terminal-green);
		min-width: 40px;
	}

	/* Agent Status Colors */
	.agent-type.busy {
		border-color: var(--warning, #ffaa00);
	}

	.agent-status.busy {
		color: var(--warning, #ffaa00);
		border-color: var(--warning, #ffaa00);
	}

	.agent-status.available {
		color: var(--terminal-green);
		border-color: var(--terminal-green);
	}

	.agent-status.offline {
		color: var(--text-muted);
		border-color: var(--border);
	}

	@media (max-width: 768px) {
		.stats-row {
			grid-template-columns: repeat(2, 1fr);
		}

		.stats-row.mini {
			grid-template-columns: repeat(3, 1fr);
		}

		.channels-grid {
			grid-template-columns: 1fr;
		}

		.arch-diagram {
			flex-direction: column;
		}

		.banner-content {
			flex-direction: column;
			text-align: center;
		}
	}
</style>
