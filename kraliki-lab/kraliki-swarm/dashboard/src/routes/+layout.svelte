<script lang="ts">
	import '../app.css';
	import type { LayoutData } from './$types';
	import { page } from '$app/stores';
	import { workspaceMode } from '$lib/stores/mode';

	let { data, children }: { data: LayoutData; children: any } = $props();

	let clock = $state(new Date().toLocaleString());

	$effect(() => {
		const interval = setInterval(() => {
			clock = new Date().toLocaleString();
		}, 1000);
		return () => clearInterval(interval);
	});

	const navItems = [
		// TIER 1: Core Operations (daily use)
		{ href: '/', label: 'Overview', icon: '📊' },
		{ href: '/comms', label: 'Comms', icon: '📡' },
		{ href: '/agents', label: 'Agents', icon: '🤖' },
		{ href: '/jobs', label: 'Jobs', icon: '📋' },
		{ href: '/health', label: 'Health', icon: '💚' },
		// TIER 2: Intelligence (strategic work)
		{ href: '/brain', label: 'Brain', icon: '🧠' },
		{ href: '/recall', label: 'Recall', icon: '💾' },
		{ href: '/insights', label: 'Insights', icon: '💡' },
		{ href: '/workflows', label: 'Workflows', icon: '⚡' },
		// TIER 3: Management (configuration)
		{ href: '/genomes', label: 'Genomes', icon: '🧬' },
		{ href: '/leaderboard', label: 'Leaderboard', icon: '🏆' },
		// TIER 4: Advanced (debug/monitor)
		{ href: '/see', label: 'See', icon: '📹' },
		{ href: '/costs', label: 'Costs', icon: '💰' },
		{ href: '/data', label: 'Data', icon: '📁' },
		// TIER 5: Integrated Apps (separate products)
		{ href: '/learn', label: 'Learn', icon: '📚' },
		{ href: '/apps', label: 'Apps', icon: '📦' },
		{ href: '/terminal', label: 'Terminal', icon: '⌨️' },
		{ href: '/notebook', label: 'Notebook', icon: '📝' },
	];

	let isDark = $state(true); // Default to dark for this specific dashboard

	$effect(() => {
		if (isDark) {
			document.documentElement.classList.add('dark');
		} else {
			document.documentElement.classList.remove('dark');
		}
	});

	function toggleTheme() {
		isDark = !isDark;
	}
</script>

<svelte:head>
	<title>Kraliki Swarm</title>
</svelte:head>

<div class="container">
	<header>
		<div>
			<h1 class="glitch">Kraliki // Swarm Control</h1>
			<p class="subtitle">AI Swarm Command Center</p>
		</div>
		<div style="display: flex; gap: 16px; align-items: center;">
			{#if $workspaceMode !== 'normal'}
				<span class="mode-indicator" class:dev={$workspaceMode === 'dev'} class:readonly={$workspaceMode === 'readonly'}>
					{$workspaceMode.toUpperCase()}
				</span>
			{/if}
			<button class="brutal-btn" onclick={toggleTheme} style="padding: 6px 10px; font-size: 16px;">
				{isDark ? '☀️' : '🌙'}
			</button>
			{#if data.user}
				<a href="/settings" class="user-badge" title="Settings">
					<span class="user-avatar">👤</span>
					<span class="user-name">{data.user.isLocal ? 'LOCAL_ROOT' : data.user.name.toUpperCase()}</span>
				</a>
			{/if}
			<span class="updated">{clock}</span>
		</div>
	</header>

	<nav class="nav-tabs">
		{#each navItems as item}
			<a
				href={item.href}
				class="nav-tab"
				class:active={$page.url.pathname === item.href}
			>
				<span class="nav-icon">{item.icon}</span>
				<span class="nav-label">{item.label}</span>
			</a>
		{/each}
	</nav>

	{@render children()}
</div>

<style>
	.nav-tabs {
		display: flex;
		flex-wrap: wrap;
		gap: 8px;
		margin-bottom: 24px;
		border-bottom: 2px solid var(--border);
		padding-bottom: 12px;
	}

	.nav-tab {
		display: flex;
		align-items: center;
		gap: 8px;
		padding: 10px 20px;
		text-decoration: none;
		color: var(--text-main);
		font-size: 11px;
		border: 2px solid var(--border);
		background: var(--surface);
		transition: all 0.05s linear;
		white-space: nowrap;
		text-transform: uppercase;
		font-weight: 700;
		box-shadow: 4px 4px 0 0 var(--border);
	}

	.nav-tab:hover {
		background: var(--terminal-green);
		border-color: var(--terminal-green);
		color: var(--void);
		transform: translate(-2px, -2px);
		box-shadow: 6px 6px 0 0 var(--terminal-green);
	}

	.nav-tab.active {
		background: var(--terminal-green);
		color: var(--void);
		border-color: var(--terminal-green);
		box-shadow: 2px 2px 0 0 var(--void);
		transform: translate(2px, 2px);
	}

	.nav-icon {
		font-size: 16px;
	}

	.nav-label {
		font-family: 'JetBrains Mono', monospace;
	}

	/* Mode Indicator */
	.mode-indicator {
		padding: 6px 12px;
		font-size: 10px;
		font-weight: 700;
		font-family: 'JetBrains Mono', monospace;
		text-transform: uppercase;
		letter-spacing: 0.05em;
	}

	.mode-indicator.dev {
		background: #ffaa00;
		color: var(--void);
	}

	.mode-indicator.readonly {
		background: #888;
		color: var(--void);
	}
</style>
