<script lang="ts">
	import { onMount } from 'svelte';

	interface HealthCheck {
		service: string;
		status: 'healthy' | 'unhealthy' | 'unknown';
		message?: string;
	}

	interface EndpointHealth {
		name: string;
		url: string;
		status: string;
		status_code: number;
		error?: string | null;
		timestamp?: string;
	}

	interface PM2Process {
		name: string;
		status: string;
		restarts: number;
		uptime: number;
		memory: number;
		cpu: number;
	}

	interface PM2Issue {
		name: string;
		status: string;
		restarts: number;
	}

	interface SystemInfo {
		uptime_seconds?: number;
		load_avg: number[];
		memory: {
			total_kb: number;
			used_kb: number;
			percent_used: number;
		};
	}

	interface CircuitBreakerEntry {
		state: 'open' | 'closed' | 'half-open';
		failure_count: number;
		last_failure_time: string | null;
		last_success_time: string | null;
		note?: string;
		last_failure_reason?: string;
	}

	interface HealthData {
		status: string;
		timestamp: string;
		checks: HealthCheck[];
	}

	interface StatusData {
		kraliki: {
			health?: {
				overall: string;
				endpoints: EndpointHealth[];
				pm2_issues: PM2Issue[];
			};
			pm2: {
				total: number;
				online: number;
				stopped: number;
				errored: number;
				processes: PM2Process[];
			};
			system?: SystemInfo;
		} | null;
		circuitBreakers: Record<string, CircuitBreakerEntry> | null;
	}

	let healthData = $state<HealthData | null>(null);
	let statusData = $state<StatusData | null>(null);
	let loading = $state(true);
	let error = $state<string | null>(null);
	let lastUpdate = $state<string>('--');

	const CLI_NAMES: Record<string, string> = {
		'linear_api': 'LINEAR',
		'claude_cli': 'CLAUDE',
		'codex_cli': 'CODEX',
		'gemini_cli': 'GEMINI',
		'opencode_cli': 'OPENCODE'
	};

	async function fetchHealth() {
		loading = true;
		try {
			const [healthRes, statusRes] = await Promise.all([
				fetch('/api/health'),
				fetch('/api/status')
			]);

			if (healthRes.ok) {
				healthData = await healthRes.json();
			}
			if (statusRes.ok) {
				statusData = await statusRes.json();
			}
			lastUpdate = new Date().toLocaleTimeString();
			error = null;
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to fetch health data';
		} finally {
			loading = false;
		}
	}

	function formatUptime(ms: number): string {
		const seconds = Math.floor(ms / 1000);
		const hours = Math.floor(seconds / 3600);
		const minutes = Math.floor((seconds % 3600) / 60);
		if (hours > 0) return `${hours}h ${minutes}m`;
		return `${minutes}m`;
	}

	function formatMemory(kb: number): string {
		const gb = kb / 1024 / 1024;
		return `${gb.toFixed(1)} GB`;
	}

	function formatProcessMemory(bytes: number): string {
		const mb = bytes / 1024 / 1024;
		if (mb >= 1024) return `${(mb / 1024).toFixed(1)} GB`;
		return `${mb.toFixed(0)} MB`;
	}

	function getOverallStatus(): 'healthy' | 'degraded' | 'unhealthy' {
		if (!statusData?.kraliki) return 'unhealthy';
		const pm2 = statusData.kraliki.pm2;
		const cbOpen = Object.values(statusData.circuitBreakers || {}).filter(cb => cb.state === 'open').length;
		if (pm2.errored > 0 || cbOpen > 2) return 'unhealthy';
		if (pm2.stopped > 0 || cbOpen > 0) return 'degraded';
		return 'healthy';
	}

	onMount(() => {
		fetchHealth();
		const interval = setInterval(fetchHealth, 30000);
		return () => clearInterval(interval);
	});

	const overallStatus = $derived(getOverallStatus());
	const pm2 = $derived(statusData?.kraliki?.pm2 || null);
	const system = $derived(statusData?.kraliki?.system || null);
	const endpoints = $derived(statusData?.kraliki?.health?.endpoints || []);
	const pm2Issues = $derived(statusData?.kraliki?.health?.pm2_issues || []);
	const circuitBreakers = $derived(statusData?.circuitBreakers || {});
	const cbEntries = $derived(Object.entries(circuitBreakers));
	const cbOpen = $derived(cbEntries.filter(([_, cb]) => cb.state === 'open').length);
	const cbClosed = $derived(cbEntries.filter(([_, cb]) => cb.state === 'closed').length);
</script>

<div class="page">
	<div class="page-header">
		<h2 class="glitch">System Health // Diagnostics</h2>
		<div class="header-controls">
			<span class="last-update">LAST_SCAN: {lastUpdate}</span>
			<button class="brutal-btn" onclick={fetchHealth} disabled={loading}>
				{loading ? 'SCANNING...' : 'REFRESH'}
			</button>
		</div>
	</div>

	{#if error}
		<div class="card" style="border-color: var(--system-red);">
			<h2 class="red">CONNECTION_ERROR</h2>
			<p class="error-msg">{error}</p>
		</div>
	{:else}
		<!-- Overall Status Banner -->
		<div class="status-banner" class:healthy={overallStatus === 'healthy'} class:degraded={overallStatus === 'degraded'} class:unhealthy={overallStatus === 'unhealthy'}>
			<div class="status-icon">
				{#if overallStatus === 'healthy'}
					<span class="pulse-dot green big"></span>
				{:else if overallStatus === 'degraded'}
					<span class="pulse-dot yellow big"></span>
				{:else}
					<span class="pulse-dot red big pulse-brutal"></span>
				{/if}
			</div>
			<div class="status-text">
				<span class="status-label">SYSTEM_STATUS</span>
				<span class="status-value">{overallStatus.toUpperCase()}</span>
			</div>
			<div class="status-summary">
				<span>PM2: {pm2?.online || 0}/{pm2?.total || 0}</span>
				<span>CB: {cbClosed}/{cbEntries.length} OK</span>
				{#if pm2Issues.length > 0}
					<span class="issue-count">{pm2Issues.length} ISSUES</span>
				{/if}
			</div>
		</div>

		<div class="grid">
			<!-- System Resources -->
			{#if system}
				<div class="card">
					<h2>SYSTEM_RESOURCES</h2>
					<div class="stat-row">
						<span class="stat-label">Uptime</span>
						<span class="stat-value cyan">{Math.floor((system.uptime_seconds || 0) / 86400)}D {Math.floor(((system.uptime_seconds || 0) % 86400) / 3600)}H</span>
					</div>
					<div class="stat-row">
						<span class="stat-label">Load Average</span>
						<span class="stat-value" class:red={system.load_avg[0] > 4} class:yellow={system.load_avg[0] > 2}>{system.load_avg.map(l => l.toFixed(2)).join(' / ')}</span>
					</div>
					<div class="stat-row">
						<span class="stat-label">Memory Used</span>
						<span class="stat-value" class:red={system.memory.percent_used > 90} class:yellow={system.memory.percent_used > 75}>
							{formatMemory(system.memory.used_kb)} / {formatMemory(system.memory.total_kb)} ({system.memory.percent_used.toFixed(1)}%)
						</span>
					</div>
					<div class="memory-bar">
						<div class="memory-fill" style="width: {system.memory.percent_used}%;" class:high={system.memory.percent_used > 75} class:critical={system.memory.percent_used > 90}></div>
					</div>
				</div>
			{/if}

			<!-- PM2 Summary -->
			{#if pm2}
				<div class="card" class:pulse-scan={pm2.stopped > 0 || pm2.errored > 0}>
					<h2 class:red={pm2.errored > 0} class:yellow={pm2.stopped > 0}>PM2_PROCESSES</h2>
					<div class="pm2-stats">
						<div class="pm2-stat">
							<span class="pm2-count green">{pm2.online}</span>
							<span class="pm2-label">ONLINE</span>
						</div>
						<div class="pm2-stat">
							<span class="pm2-count yellow">{pm2.stopped}</span>
							<span class="pm2-label">STOPPED</span>
						</div>
						<div class="pm2-stat">
							<span class="pm2-count red">{pm2.errored}</span>
							<span class="pm2-label">ERRORED</span>
						</div>
					</div>

					{#if pm2Issues.length > 0}
						<div class="issues-section">
							<h3>ISSUES_DETECTED</h3>
							{#each pm2Issues as issue}
								<div class="issue-item">
									<span class="issue-name">{issue.name}</span>
									<span class="issue-status" class:stopped={issue.status === 'stopped'} class:errored={issue.status === 'errored'}>{issue.status.toUpperCase()}</span>
								</div>
							{/each}
						</div>
					{/if}
				</div>
			{/if}

			<!-- Circuit Breakers -->
			{#if cbEntries.length > 0}
				<div class="card span-2" class:pulse-scan={cbOpen > 0}>
					<h2 class:red={cbOpen > 0}>CIRCUIT_BREAKERS // {cbOpen > 0 ? `${cbOpen} TRIPPED` : 'ALL_OK'}</h2>
					<p class="hint">CLI health status. Open = failing, Closed = healthy, Half-open = recovering.</p>
					<div class="cb-grid">
						{#each cbEntries as [name, cb]}
							<div class="cb-card" class:cb-open={cb.state === 'open'} class:cb-closed={cb.state === 'closed'} class:cb-half={cb.state === 'half-open'}>
								<div class="cb-header">
									<span class="cb-name">{CLI_NAMES[name] || name.toUpperCase()}</span>
									<span class="cb-state">
										<span class="pulse-dot" class:green={cb.state === 'closed'} class:red={cb.state === 'open'} class:yellow={cb.state === 'half-open'}></span>
										{cb.state.toUpperCase()}
									</span>
								</div>
								{#if cb.note}
									<div class="cb-note">{cb.note}</div>
								{/if}
								{#if cb.last_failure_reason && cb.state === 'open'}
									<div class="cb-reason">{cb.last_failure_reason.slice(0, 100)}</div>
								{/if}
								<div class="cb-times">
									{#if cb.last_success_time && cb.state !== 'open'}
										<span>OK: {new Date(cb.last_success_time).toLocaleTimeString()}</span>
									{/if}
									{#if cb.last_failure_time}
										<span>FAIL: {new Date(cb.last_failure_time).toLocaleTimeString()}</span>
									{/if}
								</div>
							</div>
						{/each}
					</div>
				</div>
			{/if}

			<!-- Endpoint Health -->
			{#if endpoints.length > 0}
				<div class="card">
					<h2>ENDPOINT_HEALTH</h2>
					<div class="endpoint-list">
						{#each endpoints as ep}
							<div class="endpoint-item" class:healthy={ep.status === 'healthy'} class:unhealthy={ep.status !== 'healthy'}>
								<div class="ep-info">
									<span class="ep-name">{ep.name}</span>
									<span class="ep-url">{ep.url}</span>
								</div>
								<div class="ep-status">
									<span class="pulse-dot" class:green={ep.status === 'healthy'} class:red={ep.status !== 'healthy'}></span>
									<span>{ep.status_code}</span>
								</div>
							</div>
						{/each}
					</div>
				</div>
			{/if}

			<!-- Service Checks -->
			{#if healthData?.checks}
				<div class="card">
					<h2>SERVICE_CHECKS</h2>
					<div class="check-list">
						{#each healthData.checks as check}
							<div class="check-item" class:healthy={check.status === 'healthy'} class:unhealthy={check.status === 'unhealthy'} class:unknown={check.status === 'unknown'}>
								<span class="check-name">{check.service.toUpperCase()}</span>
								<span class="check-status">
									<span class="pulse-dot" class:green={check.status === 'healthy'} class:red={check.status === 'unhealthy'} class:yellow={check.status === 'unknown'}></span>
									{check.status.toUpperCase()}
								</span>
								{#if check.message}
									<span class="check-msg">{check.message}</span>
								{/if}
							</div>
						{/each}
					</div>
				</div>
			{/if}

			<!-- PM2 Process List -->
			{#if pm2?.processes}
				<div class="card span-2">
					<h2>PM2_PROCESS_LIST</h2>
					<div class="process-table">
						<div class="process-row header">
							<span>NAME</span>
							<span>STATUS</span>
							<span>RESTARTS</span>
							<span>UPTIME</span>
							<span>CPU%</span>
							<span>MEM</span>
						</div>
						{#each pm2.processes as proc}
							<div class="process-row" class:online={proc.status === 'online'} class:stopped={proc.status === 'stopped'} class:errored={proc.status === 'errored'}>
								<span class="proc-name">{proc.name}</span>
								<span class="proc-status">
									<span class="pulse-dot" class:green={proc.status === 'online'} class:red={proc.status !== 'online'}></span>
									{proc.status.toUpperCase()}
								</span>
								<span class:high-restarts={proc.restarts > 5}>{proc.restarts}</span>
								<span>{formatUptime(proc.uptime)}</span>
								<span>{proc.cpu.toFixed(1)}</span>
								<span>{formatProcessMemory(proc.memory)}</span>
							</div>
						{/each}
					</div>
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
		border-bottom: 2px solid var(--border);
		padding-bottom: 16px;
	}

	.header-controls {
		display: flex;
		gap: 16px;
		align-items: center;
	}

	.last-update {
		font-family: 'JetBrains Mono', monospace;
		font-size: 10px;
		color: var(--text-muted);
		text-transform: uppercase;
	}

	.grid {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
		gap: 24px;
	}

	.span-2 {
		grid-column: span 2;
	}

	@media (max-width: 800px) {
		.span-2 {
			grid-column: span 1;
		}
	}

	.hint {
		font-size: 10px;
		color: var(--text-muted);
		text-transform: uppercase;
		margin-bottom: 16px;
		letter-spacing: 0.1em;
	}

	/* Status Banner */
	.status-banner {
		display: flex;
		align-items: center;
		gap: 24px;
		padding: 24px;
		border: 3px solid var(--border);
		background: var(--surface);
		box-shadow: 6px 6px 0 0 var(--border);
	}

	.status-banner.healthy {
		border-color: var(--terminal-green);
		box-shadow: 6px 6px 0 0 var(--terminal-green);
	}

	.status-banner.degraded {
		border-color: var(--warning);
		box-shadow: 6px 6px 0 0 var(--warning);
	}

	.status-banner.unhealthy {
		border-color: var(--system-red);
		box-shadow: 6px 6px 0 0 var(--system-red);
		animation: pulse-border 1s ease-in-out infinite;
	}

	.status-text {
		display: flex;
		flex-direction: column;
		gap: 4px;
	}

	.status-label {
		font-size: 10px;
		color: var(--text-muted);
		text-transform: uppercase;
		letter-spacing: 0.1em;
	}

	.status-value {
		font-family: 'JetBrains Mono', monospace;
		font-size: 24px;
		font-weight: 700;
	}

	.status-summary {
		display: flex;
		gap: 24px;
		margin-left: auto;
		font-family: 'JetBrains Mono', monospace;
		font-size: 12px;
		color: var(--text-muted);
	}

	.issue-count {
		color: var(--system-red);
		font-weight: 700;
	}

	/* Pulse dots */
	.pulse-dot {
		width: 10px;
		height: 10px;
		border-radius: 50%;
		display: inline-block;
	}

	.pulse-dot.big {
		width: 20px;
		height: 20px;
	}

	.pulse-dot.green {
		background: var(--terminal-green);
		box-shadow: 0 0 10px var(--terminal-green);
	}

	.pulse-dot.yellow {
		background: var(--warning);
		box-shadow: 0 0 10px var(--warning);
	}

	.pulse-dot.red {
		background: var(--system-red);
		box-shadow: 0 0 10px var(--system-red);
	}

	.pulse-brutal {
		animation: pulse 1s ease-in-out infinite;
	}

	/* Memory Bar */
	.memory-bar {
		height: 8px;
		background: var(--border);
		margin-top: 12px;
		border: 1px solid var(--border);
	}

	.memory-fill {
		height: 100%;
		background: var(--terminal-green);
		transition: width 0.3s ease;
	}

	.memory-fill.high {
		background: var(--warning);
	}

	.memory-fill.critical {
		background: var(--system-red);
	}

	/* PM2 Stats */
	.pm2-stats {
		display: flex;
		gap: 32px;
		margin-bottom: 16px;
	}

	.pm2-stat {
		display: flex;
		flex-direction: column;
		align-items: center;
	}

	.pm2-count {
		font-family: 'JetBrains Mono', monospace;
		font-size: 32px;
		font-weight: 700;
	}

	.pm2-count.green { color: var(--terminal-green); }
	.pm2-count.yellow { color: var(--warning); }
	.pm2-count.red { color: var(--system-red); }

	.pm2-label {
		font-size: 10px;
		color: var(--text-muted);
		text-transform: uppercase;
	}

	/* Issues */
	.issues-section {
		margin-top: 16px;
		padding-top: 16px;
		border-top: 1px solid var(--border);
	}

	.issues-section h3 {
		font-size: 11px;
		color: var(--system-red);
		margin-bottom: 12px;
	}

	.issue-item {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 8px;
		border: 1px solid var(--border);
		margin-bottom: 8px;
	}

	.issue-name {
		font-family: 'JetBrains Mono', monospace;
		font-size: 11px;
	}

	.issue-status {
		font-size: 10px;
		font-weight: 700;
		padding: 2px 8px;
		border: 1px solid;
	}

	.issue-status.stopped {
		color: var(--warning);
		border-color: var(--warning);
	}

	.issue-status.errored {
		color: var(--system-red);
		border-color: var(--system-red);
	}

	/* Circuit Breakers */
	.cb-grid {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
		gap: 16px;
	}

	.cb-card {
		padding: 16px;
		border: 2px solid var(--border);
		background: var(--surface);
		box-shadow: 4px 4px 0 0 var(--border);
	}

	.cb-card.cb-open {
		border-color: var(--system-red);
		background: rgba(255, 68, 68, 0.05);
	}

	.cb-card.cb-closed {
		border-color: var(--terminal-green);
	}

	.cb-card.cb-half {
		border-color: var(--warning);
	}

	.cb-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 8px;
	}

	.cb-name {
		font-family: 'JetBrains Mono', monospace;
		font-size: 12px;
		font-weight: 700;
	}

	.cb-state {
		display: flex;
		align-items: center;
		gap: 6px;
		font-size: 10px;
	}

	.cb-note {
		font-size: 10px;
		color: var(--cyan-data);
		margin-bottom: 8px;
	}

	.cb-reason {
		font-size: 10px;
		color: var(--system-red);
		margin-bottom: 8px;
		word-break: break-word;
	}

	.cb-times {
		font-size: 9px;
		color: var(--text-muted);
		display: flex;
		gap: 12px;
	}

	/* Endpoint List */
	.endpoint-list {
		display: flex;
		flex-direction: column;
		gap: 8px;
	}

	.endpoint-item {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 12px;
		border: 2px solid var(--border);
	}

	.endpoint-item.healthy {
		border-left: 4px solid var(--terminal-green);
	}

	.endpoint-item.unhealthy {
		border-left: 4px solid var(--system-red);
	}

	.ep-info {
		display: flex;
		flex-direction: column;
		gap: 2px;
	}

	.ep-name {
		font-family: 'JetBrains Mono', monospace;
		font-size: 11px;
		font-weight: 700;
	}

	.ep-url {
		font-size: 9px;
		color: var(--text-muted);
	}

	.ep-status {
		display: flex;
		align-items: center;
		gap: 8px;
		font-family: 'JetBrains Mono', monospace;
		font-size: 12px;
	}

	/* Check List */
	.check-list {
		display: flex;
		flex-direction: column;
		gap: 12px;
	}

	.check-item {
		display: flex;
		align-items: center;
		gap: 16px;
		padding: 12px;
		border: 2px solid var(--border);
	}

	.check-name {
		font-family: 'JetBrains Mono', monospace;
		font-size: 12px;
		font-weight: 700;
		min-width: 80px;
	}

	.check-status {
		display: flex;
		align-items: center;
		gap: 8px;
		font-size: 11px;
	}

	.check-msg {
		font-size: 10px;
		color: var(--text-muted);
		margin-left: auto;
	}

	/* Process Table */
	.process-table {
		font-family: 'JetBrains Mono', monospace;
		font-size: 11px;
		overflow-x: auto;
		width: 100%;
		padding-bottom: 8px;
	}

	.process-row {
		display: grid;
		grid-template-columns: 2fr 1fr 0.8fr 1fr 0.8fr 1fr;
		gap: 16px;
		padding: 10px;
		border-bottom: 1px solid var(--border);
		align-items: center;
		min-width: 600px;
	}

	.process-row.header {
		font-weight: 700;
		color: var(--text-muted);
		text-transform: uppercase;
		font-size: 10px;
		border-bottom: 2px solid var(--border);
	}

	.process-row.online {
		background: rgba(51, 255, 0, 0.03);
	}

	.process-row.stopped {
		background: rgba(255, 200, 0, 0.05);
	}

	.process-row.errored {
		background: rgba(255, 68, 68, 0.05);
	}

	.proc-name {
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
	}

	.proc-status {
		display: flex;
		align-items: center;
		gap: 8px;
	}

	.high-restarts {
		color: var(--warning);
		font-weight: 700;
	}

	/* Animations */
	@keyframes pulse {
		0%, 100% { opacity: 1; }
		50% { opacity: 0.5; }
	}

	@keyframes pulse-border {
		0%, 100% { box-shadow: 6px 6px 0 0 var(--system-red); }
		50% { box-shadow: 6px 6px 15px 0 var(--system-red); }
	}

	/* Color classes */
	.red { color: var(--system-red) !important; }
	.yellow { color: var(--warning) !important; }
	.green { color: var(--terminal-green) !important; }
	.cyan { color: var(--cyan-data) !important; }

	.pulse-scan {
		animation: scan 2s ease-in-out infinite;
	}

	@keyframes scan {
		0%, 100% { box-shadow: 4px 4px 0 0 var(--system-red); }
		50% { box-shadow: 4px 4px 10px 0 var(--system-red); }
	}

	.error-msg {
		color: var(--system-red);
		font-family: 'JetBrains Mono', monospace;
	}

	.stat-row {
		display: flex;
		justify-content: space-between;
		padding: 8px 0;
		border-bottom: 1px solid rgba(240, 240, 240, 0.1);
	}

	.stat-label {
		color: var(--text-muted);
		font-size: 11px;
		text-transform: uppercase;
	}

	.stat-value {
		font-family: 'JetBrains Mono', monospace;
		font-size: 12px;
		font-weight: 600;
	}
</style>
