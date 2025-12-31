<script lang="ts">
	import { onMount } from 'svelte';
	import { workspaceMode, modeInfo, type WorkspaceMode } from '$lib/stores/mode';

	interface Settings {
		theme: 'dark' | 'light';
		refreshInterval: number;
		notifications: boolean;
		soundAlerts: boolean;
	}

	let settings = $state<Settings>({
		theme: 'dark',
		refreshInterval: 30,
		notifications: true,
		soundAlerts: false
	});

	let saved = $state(false);

	function saveSettings() {
		localStorage.setItem('kraliki-settings', JSON.stringify(settings));
		saved = true;
		setTimeout(() => saved = false, 2000);
	}

	onMount(() => {
		const stored = localStorage.getItem('kraliki-settings');
		if (stored) {
			settings = JSON.parse(stored);
		}
	});
</script>

<div class="page">
	<div class="page-header">
		<h2 class="glitch">Settings // Configuration</h2>
		{#if saved}
			<span class="saved-badge">SAVED</span>
		{/if}
	</div>

	<div class="settings-grid">
		<!-- Workspace Mode -->
		<div class="card">
			<h3>WORKSPACE_MODE</h3>
			<div class="setting-row">
				<div class="setting-info">
					<span class="setting-name">Access Mode</span>
					<span class="setting-desc">Controls editing capabilities</span>
				</div>
				<select bind:value={$workspaceMode}>
					<option value="dev">DEV (Full Access)</option>
					<option value="normal">NORMAL (Standard)</option>
					<option value="readonly">READ-ONLY (View Only)</option>
				</select>
			</div>
			<div class="mode-info">
				{#if $workspaceMode === 'dev'}
					<span class="mode-badge dev">DEV MODE: Full CRUD + agent control</span>
				{:else if $workspaceMode === 'readonly'}
					<span class="mode-badge readonly">READ-ONLY: View data, export results</span>
				{:else}
					<span class="mode-badge normal">NORMAL: Standard access</span>
				{/if}
			</div>
		</div>

		<!-- Appearance -->
		<div class="card">
			<h3>APPEARANCE</h3>
			<div class="setting-row">
				<div class="setting-info">
					<span class="setting-name">Theme</span>
					<span class="setting-desc">Dashboard color scheme</span>
				</div>
				<select bind:value={settings.theme}>
					<option value="dark">Dark</option>
					<option value="light">Light</option>
				</select>
			</div>
		</div>

		<!-- Refresh -->
		<div class="card">
			<h3>DATA_REFRESH</h3>
			<div class="setting-row">
				<div class="setting-info">
					<span class="setting-name">Auto Refresh Interval</span>
					<span class="setting-desc">How often to refresh data (seconds)</span>
				</div>
				<select bind:value={settings.refreshInterval}>
					<option value={15}>15s</option>
					<option value={30}>30s</option>
					<option value={60}>60s</option>
					<option value={120}>2m</option>
				</select>
			</div>
		</div>

		<!-- Notifications -->
		<div class="card">
			<h3>NOTIFICATIONS</h3>
			<div class="setting-row">
				<div class="setting-info">
					<span class="setting-name">Browser Notifications</span>
					<span class="setting-desc">Get notified of important events</span>
				</div>
				<label class="toggle">
					<input type="checkbox" bind:checked={settings.notifications} />
					<span class="toggle-slider"></span>
				</label>
			</div>
			<div class="setting-row">
				<div class="setting-info">
					<span class="setting-name">Sound Alerts</span>
					<span class="setting-desc">Play sounds for critical alerts</span>
				</div>
				<label class="toggle">
					<input type="checkbox" bind:checked={settings.soundAlerts} />
					<span class="toggle-slider"></span>
				</label>
			</div>
		</div>

		<!-- Account -->
		<div class="card">
			<h3>ACCOUNT</h3>
			<div class="account-info">
				<div class="avatar">👤</div>
				<div class="account-details">
					<span class="account-name">LOCAL_ROOT</span>
					<span class="account-role">Administrator</span>
				</div>
			</div>
			<div class="account-actions">
				<a href="/auth/login" class="brutal-btn small">SWITCH_USER</a>
			</div>
		</div>

		<!-- System Info -->
		<div class="card span-2">
			<h3>SYSTEM_INFO</h3>
			<div class="info-grid">
				<div class="info-item">
					<span class="info-label">VERSION</span>
					<span class="info-value">0.1.0-alpha</span>
				</div>
				<div class="info-item">
					<span class="info-label">DASHBOARD_PORT</span>
					<span class="info-value">8099</span>
				</div>
				<div class="info-item">
					<span class="info-label">ARENA_PORT</span>
					<span class="info-value">3021</span>
				</div>
				<div class="info-item">
					<span class="info-label">MEMORY_PORT</span>
					<span class="info-value">3020</span>
				</div>
			</div>
		</div>

		<!-- Danger Zone -->
		<div class="card danger">
			<h3>DANGER_ZONE</h3>
			<div class="setting-row">
				<div class="setting-info">
					<span class="setting-name">Reset Dashboard</span>
					<span class="setting-desc">Clear all local settings and cache</span>
				</div>
				<button class="brutal-btn danger small" onclick={() => {
					localStorage.clear();
					location.reload();
				}}>RESET</button>
			</div>
		</div>
	</div>

	<div class="save-bar">
		<button class="brutal-btn primary" onclick={saveSettings}>SAVE_SETTINGS</button>
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
		align-items: center;
		border-bottom: 2px solid var(--border);
		padding-bottom: 16px;
	}

	.saved-badge {
		padding: 8px 16px;
		background: var(--terminal-green);
		color: var(--void);
		font-family: 'JetBrains Mono', monospace;
		font-size: 11px;
		font-weight: 700;
	}

	.settings-grid {
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

	.card.danger {
		border-color: #ff5555;
	}

	.card.span-2 {
		grid-column: span 2;
	}

	.card h3 {
		font-size: 11px;
		font-weight: 700;
		margin: 0 0 16px 0;
		text-transform: uppercase;
		letter-spacing: 0.05em;
		color: var(--text-muted);
	}

	.setting-row {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 12px 0;
		border-bottom: 1px solid var(--border);
	}

	.setting-row:last-child {
		border-bottom: none;
	}

	.setting-info {
		display: flex;
		flex-direction: column;
		gap: 4px;
	}

	.setting-name {
		font-size: 13px;
		font-weight: 600;
		color: var(--text-main);
	}

	.setting-desc {
		font-size: 11px;
		color: var(--text-muted);
	}

	select {
		padding: 8px 12px;
		background: var(--surface);
		border: 2px solid var(--border);
		color: var(--text-main);
		font-family: 'JetBrains Mono', monospace;
		font-size: 12px;
		cursor: pointer;
	}

	select:focus {
		outline: none;
		border-color: var(--terminal-green);
	}

	/* Toggle */
	.toggle {
		position: relative;
		display: inline-block;
		width: 48px;
		height: 24px;
	}

	.toggle input {
		opacity: 0;
		width: 0;
		height: 0;
	}

	.toggle-slider {
		position: absolute;
		cursor: pointer;
		top: 0;
		left: 0;
		right: 0;
		bottom: 0;
		background: var(--border);
		transition: 0.2s;
	}

	.toggle-slider:before {
		position: absolute;
		content: "";
		height: 18px;
		width: 18px;
		left: 3px;
		bottom: 3px;
		background: var(--text-muted);
		transition: 0.2s;
	}

	.toggle input:checked + .toggle-slider {
		background: var(--terminal-green);
	}

	.toggle input:checked + .toggle-slider:before {
		transform: translateX(24px);
		background: var(--surface);
	}

	/* Account */
	.account-info {
		display: flex;
		align-items: center;
		gap: 16px;
		margin-bottom: 16px;
	}

	.avatar {
		width: 48px;
		height: 48px;
		background: var(--border);
		display: flex;
		align-items: center;
		justify-content: center;
		font-size: 24px;
	}

	.account-details {
		display: flex;
		flex-direction: column;
		gap: 4px;
	}

	.account-name {
		font-size: 14px;
		font-weight: 700;
		color: var(--terminal-green);
	}

	.account-role {
		font-size: 11px;
		color: var(--text-muted);
	}

	.account-actions {
		display: flex;
		gap: 8px;
	}

	/* Info Grid */
	.info-grid {
		display: grid;
		grid-template-columns: repeat(4, 1fr);
		gap: 16px;
	}

	.info-item {
		display: flex;
		flex-direction: column;
		gap: 4px;
	}

	.info-label {
		font-size: 10px;
		color: var(--text-muted);
	}

	.info-value {
		font-family: 'JetBrains Mono', monospace;
		font-size: 13px;
		color: var(--terminal-green);
	}

	/* Save Bar */
	.save-bar {
		display: flex;
		justify-content: flex-end;
		padding-top: 16px;
		border-top: 2px solid var(--border);
	}

	/* Buttons */
	.brutal-btn {
		background: var(--surface);
		border: 2px solid var(--terminal-green);
		color: var(--terminal-green);
		padding: 12px 24px;
		font-family: 'JetBrains Mono', monospace;
		font-size: 11px;
		font-weight: 700;
		text-transform: uppercase;
		cursor: pointer;
		text-decoration: none;
		transition: all 0.1s ease;
	}

	.brutal-btn:hover {
		background: var(--terminal-green);
		color: var(--void);
	}

	.brutal-btn.primary {
		background: var(--terminal-green);
		color: var(--void);
	}

	.brutal-btn.danger {
		border-color: #ff5555;
		color: #ff5555;
	}

	.brutal-btn.danger:hover {
		background: #ff5555;
		color: var(--void);
	}

	.brutal-btn.small {
		padding: 6px 12px;
		font-size: 10px;
	}

	/* Mode Badges */
	.mode-info {
		margin-top: 12px;
	}

	.mode-badge {
		padding: 8px 12px;
		font-size: 11px;
		font-family: 'JetBrains Mono', monospace;
		display: block;
	}

	.mode-badge.dev {
		background: rgba(255, 170, 0, 0.2);
		border-left: 3px solid #ffaa00;
		color: #ffaa00;
	}

	.mode-badge.readonly {
		background: rgba(136, 136, 136, 0.2);
		border-left: 3px solid #888;
		color: #888;
	}

	.mode-badge.normal {
		background: rgba(0, 255, 136, 0.1);
		border-left: 3px solid var(--terminal-green);
		color: var(--terminal-green);
	}

	@media (max-width: 768px) {
		.settings-grid {
			grid-template-columns: 1fr;
		}

		.card.span-2 {
			grid-column: span 1;
		}

		.info-grid {
			grid-template-columns: repeat(2, 1fr);
		}
	}
</style>
