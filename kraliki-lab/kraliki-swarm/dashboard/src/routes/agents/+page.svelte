<script lang="ts">
	import { onMount } from "svelte";

	interface AgentStatusEntry {
		id: string;
		genome: string | null;
		cli: string | null;
		status: 'running' | 'completed' | 'failed';
		pid: number | null;
		startTime: string;
		duration: string;
		points: number | null;
	}

	interface GenomeConfig {
		name: string;
		cli: string;
		enabled: boolean;
	}

	interface CliPolicyEntry {
		name: string;
		enabled: boolean;
		reason: string;
		priority: number;
		disabled_until?: string;
	}

	interface PipelinePolicyEntry {
		name: string;
		enabled: boolean;
		reason: string;
		intended?: boolean;
		signals?: string[];
	}

	interface CircuitBreakerEntry {
		state: 'open' | 'closed' | 'half-open';
		last_success_time: string | null;
		last_failure_time: string | null;
		last_failure_reason?: string;
		note?: string;
	}

	let agentStatus = $state<AgentStatusEntry[]>([]);
	let genomes = $state<GenomeConfig[]>([]);
	let cliPolicy = $state<CliPolicyEntry[]>([]);
	let pipelinePolicy = $state<PipelinePolicyEntry[]>([]);
	let circuitBreakers = $state<Record<string, CircuitBreakerEntry>>({});
	let loading = $state(true);
	let saving = $state(false);
	let message = $state<string | null>(null);
	let resetting = $state(false);
	let softResetting = $state(false);
	let redeploying = $state(false);
	let powering = $state(false);
	let swarmPowered = $state<boolean | null>(null);
	let staleCount = $state(0);
	let paused = $state(false);
	let pausing = $state(false);
	let pausedAt = $state<string | null>(null);

	const CLI_DISPLAY_NAMES: Record<string, string> = {
		'linear_api': 'LINEAR',
		'claude_cli': 'CLAUDE',
		'codex_cli': 'CODEX',
		'gemini_cli': 'GEMINI',
		'opencode_cli': 'OPENCODE'
	};

	const CORE_SWARM_PROCESSES = [
		'kraliki-watchdog-claude',
		'kraliki-watchdog-opencode',
		'kraliki-watchdog-gemini',
		'kraliki-watchdog-codex',
		'kraliki-health',
		'kraliki-stats',
		'kraliki-n8n-api',
		'kraliki-comm',
		'kraliki-comm-zt',
		'kraliki-comm-ws',
		'kraliki-msg-poller',
		'kraliki-linear-sync',
		'kraliki-agent-board',
		'kraliki-recall',
		'kraliki-events-bridge',
		'kraliki-mcp'
	];

	function formatCBTime(isoTime: string | null): string {
		if (!isoTime) return '--';
		const date = new Date(isoTime);
		return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: false });
	}

	async function fetchData() {
		try {
			const [statusRes, genomesRes, policyRes, pipelineRes] = await Promise.all([
				fetch('/api/status'),
				fetch('/api/genomes'),
				fetch('/api/cli-policy'),
				fetch('/api/pipeline-policy')
			]);
			const statusData = await statusRes.json();
			agentStatus = statusData.agentStatus || [];
			circuitBreakers = statusData.circuitBreakers || {};
			const processes = statusData?.kraliki?.pm2?.processes || [];
			swarmPowered = processes.some((proc: { name: string; status: string }) =>
				CORE_SWARM_PROCESSES.includes(proc.name) && proc.status === 'online'
			);

			if (genomesRes.ok) {
				const genomesData = await genomesRes.json();
				genomes = genomesData.genomes || [];
			}

			if (policyRes.ok) {
				const policyData = await policyRes.json();
				cliPolicy = policyData.clis || [];
			}

			if (pipelineRes.ok) {
				const pipelineData = await pipelineRes.json();
				pipelinePolicy = pipelineData.pipelines || [];
			}

			// Check for stale agents
			checkStaleAgents();
		} catch (e) {
			console.error('Failed to fetch:', e);
		} finally {
			loading = false;
		}
	}

	async function checkStaleAgents() {
		try {
			const res = await fetch("/api/reset-soft");
			if (res.ok) {
				const data = await res.json();
				staleCount = data.stale_count || 0;
			}
		} catch {
			staleCount = 0;
		}
	}

	async function fetchPauseState() {
		try {
			const res = await fetch("/api/pause-swarm");
			if (res.ok) {
				const data = await res.json();
				paused = data.paused;
				pausedAt = data.paused_at || null;
			}
		} catch {
			paused = false;
		}
	}

	async function togglePause() {
		if (pausing) return;
		pausing = true;
		message = null;
		try {
			const action = paused ? 'resume' : 'pause';
			const res = await fetch("/api/pause-swarm", {
				method: "POST",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify({ action, kill_running: !paused })
			});
			const data = await res.json();
			if (data.success) {
				paused = data.paused;
				pausedAt = data.paused_at || null;
				message = data.message || (paused ? "SWARM_PAUSED" : "SWARM_RESUMED");
				setTimeout(() => message = null, 4000);
				await fetchData();
			} else {
				message = data.message || "TOGGLE_FAILED";
			}
		} catch (e) {
			message = e instanceof Error ? e.message : "PAUSE_ERROR";
		} finally {
			pausing = false;
		}
	}

	async function softResetSwarm() {
		if (softResetting) return;
		softResetting = true;
		message = null;
		try {
			const res = await fetch("/api/reset-soft", { method: "POST" });
			const data = await res.json();
			if (data.success) {
				message = data.killed > 0 ? `KILLED ${data.killed} STALE` : "NO_STALE_AGENTS";
				setTimeout(() => message = null, 3000);
				await fetchData();
			} else {
				message = data.message || "SOFT_RESET_FAILED";
			}
		} catch (e) {
			message = e instanceof Error ? e.message : "SOFT_RESET_ERROR";
		} finally {
			softResetting = false;
		}
	}

	async function resetSwarm() {
		if (resetting) return;
		resetting = true;
		message = null;
		try {
			const res = await fetch("/api/reset", { method: "POST" });
			const data = await res.json();
			if (data.success) {
				message = "SWARM_RESET_COMPLETE";
				setTimeout(() => message = null, 3000);
				await fetchData();
			} else {
				message = data.message || "RESET_FAILED";
			}
		} catch (e) {
			message = e instanceof Error ? e.message : "RESET_ERROR";
		} finally {
			resetting = false;
		}
	}

	async function redeployDashboard() {
		if (redeploying) return;
		redeploying = true;
		message = null;
		try {
			const res = await fetch("/api/dashboard-redeploy", { method: "POST" });
			const data = await res.json();
			if (data.success) {
				message = "DASHBOARD_REDEPLOY_QUEUED";
			} else {
				message = data.message || "REDEPLOY_FAILED";
			}
		} catch (e) {
			message = e instanceof Error ? e.message : "REDEPLOY_ERROR";
		} finally {
			redeploying = false;
			setTimeout(() => message = null, 3000);
		}
	}

	async function powerSwarm(action: 'off' | 'on' | 'restart') {
		if (powering) return;
		if (action !== 'on') {
			const confirmed = confirm(`Confirm swarm power ${action.toUpperCase()}?`);
			if (!confirmed) return;
		}
		powering = true;
		message = null;
		try {
			const res = await fetch('/api/power-swarm', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ action })
			});
			const data = await res.json();
			if (data.success) {
				message = data.message || `SWARM_${action.toUpperCase()}`;
				setTimeout(() => message = null, 3000);
				await fetchData();
			} else {
				message = data.message || 'POWER_ACTION_FAILED';
			}
		} catch (e) {
			message = e instanceof Error ? e.message : 'POWER_ACTION_ERROR';
		} finally {
			powering = false;
		}
	}

	async function togglePower() {
		const action = swarmPowered ? 'off' : 'on';
		await powerSwarm(action);
	}

	async function toggleCliPolicy(cliName: string, newEnabled: boolean, reason: string) {
		console.log(`[CLI Toggle] Toggling ${cliName} to ${newEnabled}`);
		saving = true;
		message = null;
		try {
			const res = await fetch('/api/cli-policy', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ cli: cliName, enabled: newEnabled, reason })
			});
			if (res.ok) {
				const updated = await res.json();
				cliPolicy = updated.clis;
				message = `${cliName.toUpperCase()} ${newEnabled ? 'ENABLED' : 'DISABLED'}`;
			} else {
				message = `Failed to update ${cliName}`;
			}
		} catch (e) {
			message = 'Failed to update CLI policy';
		} finally {
			saving = false;
			setTimeout(() => message = null, 3000);
		}
	}

	async function toggleGenome(name: string, enabled: boolean) {
		saving = true;
		message = null;
		try {
			const res = await fetch('/api/genomes', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ name, enabled })
			});
			if (res.ok) {
				const updated = await res.json();
				genomes = updated;
				message = `${name} ${enabled ? 'enabled' : 'disabled'}`;
			}
		} catch (e) {
			message = 'Failed to update genome';
		} finally {
			saving = false;
			setTimeout(() => message = null, 3000);
		}
	}

	async function togglePipelinePolicy(pipelineName: string, newEnabled: boolean, reason: string) {
		saving = true;
		message = null;
		try {
			const res = await fetch('/api/pipeline-policy', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ pipeline: pipelineName, enabled: newEnabled, reason })
			});
			if (res.ok) {
				const updated = await res.json();
				pipelinePolicy = updated.pipelines || [];
				message = `${pipelineName.toUpperCase()} ${newEnabled ? 'ENABLED' : 'DISABLED'}`;
			} else {
				message = `Failed to update ${pipelineName}`;
			}
		} catch (e) {
			message = 'Failed to update pipeline policy';
		} finally {
			saving = false;
			setTimeout(() => message = null, 3000);
		}
	}

	async function spawnAgent(genomeName: string) {
		saving = true;
		message = null;
		try {
			const res = await fetch('/api/spawn', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ genome: genomeName })
			});
			if (res.ok) {
				message = `Spawned ${genomeName}`;
				await fetchData();
			} else {
				message = 'Failed to spawn agent';
			}
		} catch (e) {
			message = 'Failed to spawn agent';
		} finally {
			saving = false;
			setTimeout(() => message = null, 3000);
		}
	}

	onMount(() => {
		fetchData();
		fetchPauseState();
		const interval = setInterval(() => {
			fetchData();
			fetchPauseState();
		}, 30000);
		return () => clearInterval(interval);
	});

	const cliGroups = $derived(
		genomes.reduce((acc, g) => {
			if (!acc[g.cli]) acc[g.cli] = [];
			acc[g.cli].push(g);
			return acc;
		}, {} as Record<string, GenomeConfig[]>)
	);

	const cbEntries = $derived(Object.entries(circuitBreakers));
	const cbOpen = $derived(cbEntries.filter(([_, cb]) => cb.state === 'open').length);
</script>

<div class="page">
	<div class="page-header">
		<h2 class="glitch">Agent Management // Swarm Control</h2>
		<div class="header-controls">
			{#if message}
				<span class="reset-message" class:success={message.includes("NO_STALE") || message.includes("COMPLETE") || message.includes("KILLED") || message.includes("RESUMED")}>{message.toUpperCase()}</span>
			{/if}
			{#if paused}
				<span class="pause-indicator">PAUSED</span>
			{/if}
			<button class="brutal-btn yellow-btn" onclick={softResetSwarm} disabled={softResetting}>
				{softResetting ? 'CLEANING...' : `SOFT_RESET${staleCount > 0 ? ` (${staleCount})` : ''}`}
			</button>
			<button class="brutal-btn red-btn" onclick={resetSwarm} disabled={resetting} title="Nuclear option - restarts everything">
				{resetting ? 'RESETTING...' : 'HARD_RESET'}
			</button>
			<button
				class="brutal-btn {paused ? 'green-btn' : 'orange-btn'}"
				onclick={togglePause}
				disabled={pausing}
				title={paused ? 'Resume all swarm activities' : 'Pause all swarm activities and kill running agents'}
			>
				{#if pausing}
					{paused ? 'WAKING...' : 'SLEEPING...'}
				{:else}
					{paused ? 'WAKE' : 'SLEEP'}
				{/if}
			</button>
			<button class="brutal-btn orange-btn" onclick={() => powerSwarm('restart')} disabled={powering} title="Restart core swarm services">
				RESTART
			</button>
			<button
				class="brutal-btn"
				onclick={togglePower}
				disabled={powering}
				title={swarmPowered ? 'Power off core swarm services' : 'Power on core swarm services'}
			>
				{swarmPowered === null ? 'POWER' : (swarmPowered ? 'POWER_OFF' : 'POWER_ON')}
			</button>
		</div>
	</div>

	{#if loading}
		<div class="loading">INQUIRY_INTO_SWARM_STATE...</div>
	{:else}
		<div class="card dev-tools">
			<h2>DEV_TOOLS</h2>
			<div class="dev-tools-actions">
				<button class="brutal-btn" onclick={fetchData} disabled={loading}>
					{loading ? 'SYNCING...' : 'REFRESH'}
				</button>
				<button class="brutal-btn" onclick={redeployDashboard} disabled={redeploying} title="Build + restart dashboard">
					{redeploying ? 'REDEPLOYING...' : 'REDEPLOY_UI'}
				</button>
			</div>
		</div>
		<!-- CLI Policy Control -->
		<div class="card">
			<h2>CLI_POLICY_CONTROL // SPAWN_AUTHORIZATION</h2>
			<p class="hint">Toggle CLI availability for agent spawning. Policy persists across watchdog cycles.</p>

			<div class="cli-policy-grid">
				{#each cliPolicy as cli}
					<div class="cli-policy-item" class:disabled={!cli.enabled}>
						<div class="cli-info">
							<span class="cli-name">{cli.name.toUpperCase()}</span>
							<span class="cli-reason">{cli.reason}</span>
						</div>
						<div class="cli-controls">
							<span class="cli-status" class:enabled={cli.enabled} class:disabled={!cli.enabled}>
								{cli.enabled ? 'ONLINE' : 'OFFLINE'}
							</span>
							<button
								class="brutal-btn {cli.enabled ? 'disable-btn' : 'enable-btn'}"
								disabled={saving}
								data-cli={cli.name}
								onclick={(e) => {
									const target = e.currentTarget as HTMLButtonElement;
									const cliName = target.dataset.cli || cli.name;
									const currentEnabled = cli.enabled;
									toggleCliPolicy(cliName, !currentEnabled, currentEnabled ? 'Disabled via dashboard' : 'Enabled via dashboard');
								}}
							>
								{cli.enabled ? 'DISABLE' : 'ENABLE'}
							</button>
						</div>
					</div>
				{/each}
			</div>
		</div>

		<!-- Pipeline Policy Control -->
		<div class="card">
			<h2>PIPELINE_POLICY_CONTROL // WORK_MODE</h2>
			<p class="hint">Disable pipelines to focus. Example: disable BIZ to stop brainstorming while coding.</p>

			<div class="cli-policy-grid">
				{#each pipelinePolicy as pipeline}
					<div class="cli-policy-item" class:disabled={!pipeline.enabled}>
						<div class="cli-info">
							<span class="cli-name">{pipeline.name.replace('_', ' ').toUpperCase()}</span>
							<span class="cli-reason">{pipeline.reason}</span>
							{#if pipeline.intended}
								<span class="pipeline-intended">
									INTENDED{pipeline.signals && pipeline.signals.length ? ` (${pipeline.signals.join(' + ')})` : ''}
								</span>
							{/if}
						</div>
						<div class="cli-controls">
							<span class="cli-status" class:enabled={pipeline.enabled} class:disabled={!pipeline.enabled}>
								{pipeline.enabled ? 'ONLINE' : 'OFFLINE'}
							</span>
							<button
								class="brutal-btn {pipeline.enabled ? 'disable-btn' : 'enable-btn'}"
								disabled={saving}
								data-pipeline={pipeline.name}
								onclick={(e) => {
									const target = e.currentTarget as HTMLButtonElement;
									const pipelineName = target.dataset.pipeline || pipeline.name;
									const currentEnabled = pipeline.enabled;
									togglePipelinePolicy(
										pipelineName,
										!currentEnabled,
										currentEnabled ? 'Disabled via dashboard' : 'Enabled via dashboard'
									);
								}}
							>
								{pipeline.enabled ? 'DISABLE' : 'ENABLE'}
							</button>
						</div>
					</div>
				{/each}
			</div>
		</div>

		<!-- Circuit Breakers (CLI Health) -->
		{#if cbEntries.length > 0}
			<div class="card" class:pulse-scan={cbOpen > 0} style={cbOpen > 0 ? 'border-color: var(--system-red);' : ''}>
				<h2 class:red={cbOpen > 0}>CLI_HEALTH // {cbOpen > 0 ? `${cbOpen} TRIPPED` : 'ALL_OK'}</h2>
				<p class="hint">Circuit breaker status for each CLI. Tripped = CLI is failing, spawns may fail.</p>
				<div class="cb-grid">
					{#each cbEntries as [name, cb]}
						<div
							class="cb-card"
							class:cb-open={cb.state === 'open'}
							class:cb-closed={cb.state === 'closed'}
							class:cb-half={cb.state === 'half-open'}
						>
							<div class="cb-name">{CLI_DISPLAY_NAMES[name] || name.toUpperCase()}</div>
							<div class="cb-state">
								<span
									class="pulse-dot"
									class:green={cb.state === 'closed'}
									class:red={cb.state === 'open'}
									class:yellow={cb.state === 'half-open'}
								></span>
								{cb.state.toUpperCase()}
							</div>
							<div class="cb-times">
								{#if cb.last_success_time && cb.state !== 'open'}
									<span class="cb-time-label">OK:</span> {formatCBTime(cb.last_success_time)}
								{/if}
								{#if cb.last_failure_time}
									<span class="cb-time-label" style="margin-left: 8px;">FAIL:</span> {formatCBTime(cb.last_failure_time)}
								{/if}
							</div>
							{#if cb.note}
								<div class="cb-note">{cb.note}</div>
							{/if}
							{#if cb.last_failure_reason && cb.state === 'open'}
								<div class="cb-reason">{cb.last_failure_reason.slice(0, 60)}</div>
							{/if}
						</div>
					{/each}
				</div>
			</div>
		{/if}

		<!-- Agent Launcher -->
		<div class="card">
			<h2>AGENT_LAUNCHER // GENOME_WATCHDOG</h2>
			<p class="hint">Template packs activate roles; these toggles are a global override for watchdog auto-spawning.</p>

			<div class="cli-groups-container">
				{#each Object.entries(cliGroups) as [cli, cliGenomes]}
					<div class="cli-group">
						<div class="cli-header">
							<span class="lab-badge" data-lab={cli.toUpperCase().slice(0,2)}>{cli.toUpperCase()}_UNIT</span>
						</div>
						<div class="genome-list">
							{#each cliGenomes as genome}
								<div class="genome-item" class:disabled={!genome.enabled}>
									<label class="genome-toggle">
										<input
											type="checkbox"
											checked={genome.enabled}
											disabled={saving}
											onchange={(event) => {
												const target = event.currentTarget as HTMLInputElement;
												toggleGenome(genome.name, target.checked);
											}}
										/>
										<span class="genome-name">{genome.name.replace(`${cli}_`, '').replace(`${cli}-`, '').toUpperCase()}</span>
									</label>
									<button
										class="brutal-btn spawn-btn"
										disabled={saving || !genome.enabled}
										onclick={() => spawnAgent(genome.name)}
									>
										SPAWN
									</button>
								</div>
							{/each}
						</div>
					</div>
				{/each}
			</div>
		</div>

		<!-- Agent Status Table -->
		<div class="card">
			<h2>ACTIVE_AGENT_FEED // SECTOR_01</h2>
			{#if agentStatus.length === 0}
				<p class="hint">No active agents detected in current sector.</p>
			{:else}
				<div class="agent-table">
					<div class="agent-row agent-header">
						<span>Agent ID</span>
						<span>Genome</span>
						<span>CLI</span>
						<span>Status</span>
						<span>PID</span>
						<span>Start</span>
						<span>Duration</span>
						<span>Points</span>
					</div>
					{#each agentStatus as agent}
						<div
							class="agent-row"
							class:running={agent.status === 'running'}
							class:completed={agent.status === 'completed'}
							class:failed={agent.status === 'failed'}
						>
							<span class="agent-cell agent-id">{agent.id}</span>
							<span class="agent-cell">{agent.genome || '--'}</span>
							<span class="agent-cell">{agent.cli || '--'}</span>
							<span
								class="agent-cell agent-status"
								class:running={agent.status === 'running'}
								class:completed={agent.status === 'completed'}
								class:failed={agent.status === 'failed'}
							>
								{agent.status}
							</span>
							<span class="agent-cell">{agent.pid ?? '--'}</span>
							<span class="agent-cell">{agent.startTime}</span>
							<span class="agent-cell">{agent.duration}</span>
							<span class="agent-cell agent-points">{agent.points ?? '--'}</span>
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
		flex-wrap: wrap;
		gap: 16px;
	}

	.hint {
		color: var(--text-muted);
		font-size: 10px;
		text-transform: uppercase;
		margin-bottom: 20px;
		letter-spacing: 0.1em;
		display: flex;
		align-items: center;
		gap: 8px;
	}

	.hint::before {
		content: '>>';
		color: var(--terminal-green);
		font-weight: 700;
	}

	.cli-groups-container {
		display: flex;
		flex-direction: column;
		gap: 20px;
	}

	.cli-group {
		padding: 16px;
		background: rgba(240, 240, 240, 0.02);
		border: 2px solid var(--border);
		box-shadow: 4px 4px 0 0 var(--border);
	}

	.cli-header {
		margin-bottom: 16px;
		border-bottom: 1px solid rgba(240, 240, 240, 0.1);
		padding-bottom: 8px;
	}

	.genome-list {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
		gap: 16px;
	}

	.genome-item {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 12px;
		padding: 12px;
		background: var(--surface);
		border: 2px solid var(--border);
		transition: all 0.1s ease;
		box-shadow: 4px 4px 0 0 var(--border);
	}

	.genome-item:hover {
		border-color: var(--terminal-green);
		background: rgba(51, 255, 0, 0.05);
		transform: translate(-2px, -2px);
		box-shadow: 6px 6px 0 0 var(--terminal-green);
	}

	.genome-item.disabled {
		opacity: 0.4;
		border-style: solid;
		background: #000;
		filter: grayscale(1);
	}

	.genome-toggle {
		display: flex;
		align-items: center;
		gap: 12px;
		cursor: pointer;
		flex: 1;
		user-select: none;
	}

	.genome-toggle input[type="checkbox"] {
		appearance: none;
		width: 20px;
		height: 20px;
		border: 2px solid var(--border);
		background: var(--surface);
		cursor: pointer;
		position: relative;
		transition: all 0.05s linear;
		border-radius: 0;
	}

	.genome-toggle input[type="checkbox"]:checked {
		background: var(--terminal-green);
		border-color: var(--terminal-green);
		box-shadow: 2px 2px 0 0 var(--void);
	}

	.genome-toggle input[type="checkbox"]:checked::after {
		content: '';
		position: absolute;
		top: 3px;
		left: 3px;
		right: 3px;
		bottom: 3px;
		background: var(--surface);
	}

	.genome-name {
		font-family: 'JetBrains Mono', monospace;
		font-size: 11px;
		text-transform: uppercase;
		font-weight: 700;
		color: var(--text-main);
	}

	.spawn-btn {
		padding: 4px 12px;
		font-size: 10px;
		box-shadow: 2px 2px 0 0 var(--border);
	}

	.spawn-btn:hover {
		box-shadow: 4px 4px 0 0 var(--void);
	}

	.cli-policy-grid {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
		gap: 16px;
	}

	.cli-policy-item {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 16px;
		padding: 16px;
		background: var(--surface);
		border: 2px solid var(--border);
		box-shadow: 4px 4px 0 0 var(--border);
		transition: all 0.1s ease;
		flex-wrap: wrap;
	}

	.cli-policy-item:hover {
		transform: translate(-2px, -2px);
		box-shadow: 6px 6px 0 0 var(--border);
	}

	.cli-policy-item.disabled {
		opacity: 0.5;
		border-color: #ff4444;
	}

	.cli-info {
		display: flex;
		flex-direction: column;
		gap: 4px;
		flex: 1;
	}

	.cli-name {
		font-family: 'JetBrains Mono', monospace;
		font-size: 14px;
		font-weight: 700;
		text-transform: uppercase;
		color: var(--text-main);
	}

	.cli-reason {
		font-size: 10px;
		color: var(--text-muted);
		text-transform: uppercase;
		letter-spacing: 0.05em;
	}

	.pipeline-intended {
		font-size: 10px;
		color: var(--terminal-green);
		text-transform: uppercase;
		letter-spacing: 0.08em;
	}

	.cli-controls {
		display: flex;
		align-items: center;
		gap: 12px;
	}

	.cli-status {
		font-family: 'JetBrains Mono', monospace;
		font-size: 10px;
		font-weight: 700;
		text-transform: uppercase;
		padding: 4px 8px;
		border: 1px solid var(--border);
		letter-spacing: 0.1em;
	}

	.cli-status.enabled {
		color: var(--terminal-green);
		border-color: var(--terminal-green);
		background: rgba(51, 255, 0, 0.1);
	}

	.cli-status.disabled {
		color: #ff4444;
		border-color: #ff4444;
		background: rgba(255, 68, 68, 0.1);
	}

	.enable-btn {
		background: var(--terminal-green);
		color: var(--void);
		box-shadow: 2px 2px 0 0 var(--border);
	}

	.enable-btn:hover {
		box-shadow: 4px 4px 0 0 var(--void);
	}

	.disable-btn {
		background: #ff4444;
		color: var(--void);
		box-shadow: 2px 2px 0 0 var(--border);
	}

	.disable-btn:hover {
		box-shadow: 4px 4px 0 0 var(--void);
	}

	/* Header controls */
	.header-controls {
		display: flex;
		gap: 12px;
		align-items: center;
		flex-wrap: wrap;
		margin-left: auto;
		justify-content: flex-end;
	}

	.dev-tools-actions {
		display: flex;
		gap: 12px;
		flex-wrap: wrap;
	}

	.reset-message {
		font-family: 'JetBrains Mono', monospace;
		font-size: 10px;
		padding: 6px 12px;
		border: 2px solid var(--system-red);
		color: var(--system-red);
		text-transform: uppercase;
		letter-spacing: 0.1em;
		animation: pulse 0.5s ease-in-out;
	}

	.reset-message.success {
		border-color: var(--terminal-green);
		color: var(--terminal-green);
	}

	.yellow-btn {
		background: var(--warning);
		color: var(--void);
	}

	.yellow-btn:hover {
		background: #ffcc00;
	}

	.red-btn {
		background: var(--system-red);
		color: var(--void);
	}

	.red-btn:hover {
		background: #ff6666;
	}

	.orange-btn {
		background: #ff8c00;
		color: var(--void);
	}

	.orange-btn:hover {
		background: #ffa500;
	}

	.green-btn {
		background: var(--terminal-green);
		color: var(--void);
	}

	.green-btn:hover {
		background: #66ff00;
	}

	.pause-indicator {
		font-family: 'JetBrains Mono', monospace;
		font-size: 11px;
		font-weight: 700;
		padding: 6px 12px;
		background: #ff8c00;
		color: var(--void);
		text-transform: uppercase;
		letter-spacing: 0.1em;
		animation: pulse 1s ease-in-out infinite;
		border: 2px solid var(--void);
	}

	/* Circuit Breaker styles */
	.cb-grid {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
		gap: 16px;
	}

	.cb-card {
		padding: 16px;
		background: var(--surface);
		border: 2px solid var(--border);
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

	.cb-name {
		font-family: 'JetBrains Mono', monospace;
		font-size: 14px;
		font-weight: 700;
		margin-bottom: 8px;
	}

	.cb-state {
		display: flex;
		align-items: center;
		gap: 8px;
		font-size: 12px;
		font-weight: 600;
		margin-bottom: 8px;
	}

	.cb-times {
		font-size: 10px;
		color: var(--text-muted);
	}

	.cb-time-label {
		color: var(--text-main);
		font-weight: 600;
	}

	.cb-note {
		font-size: 10px;
		color: var(--cyan-data);
		margin-top: 8px;
		font-style: italic;
	}

	.cb-reason {
		font-size: 10px;
		color: var(--system-red);
		margin-top: 4px;
		word-break: break-word;
	}

	.pulse-dot {
		width: 8px;
		height: 8px;
		border-radius: 50%;
		display: inline-block;
	}

	.pulse-dot.green {
		background: var(--terminal-green);
		box-shadow: 0 0 8px var(--terminal-green);
	}

	.pulse-dot.red {
		background: var(--system-red);
		box-shadow: 0 0 8px var(--system-red);
		animation: pulse 1s ease-in-out infinite;
	}

	.pulse-dot.yellow {
		background: var(--warning);
		box-shadow: 0 0 8px var(--warning);
	}

	.pulse-scan {
		animation: scan 2s ease-in-out infinite;
	}

	.red {
		color: var(--system-red) !important;
	}

	@keyframes pulse {
		0%, 100% { opacity: 1; }
		50% { opacity: 0.5; }
	}

	@keyframes scan {
		0%, 100% { box-shadow: 4px 4px 0 0 var(--system-red); }
		50% { box-shadow: 4px 4px 10px 0 var(--system-red); }
	}
</style>
