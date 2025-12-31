<script lang="ts">
	import '../app.css';
	import { theme, toggleTheme } from '$lib/stores/theme';
	import { page } from '$app/stores';

	const navItems = [
		{ href: '/', label: 'Search', icon: '🔍' },
		{ href: '/capture', label: 'Capture', icon: '📥' },
		{ href: '/graph', label: 'Graph', icon: '🕸️' },
		{ href: '/recent', label: 'Recent', icon: '🕒' }
	];
</script>

<div class="min-h-screen flex flex-col">
	<div class="scanline"></div>

	<!-- Header -->
	<header class="border-b-2 border-border bg-card">
		<div class="container mx-auto px-4">
			<div class="flex flex-col md:flex-row items-center justify-between py-4 gap-4">
				<a href="/" class="flex items-center space-x-3 group">
					<span class="text-3xl brutal-card p-1 bg-void group-hover:bg-terminal-green transition-colors">🎯</span>
					<div class="flex flex-col">
						<span class="text-2xl font-display tracking-tighter">RECALL-KRALIKI</span>
						<span class="text-[10px] font-mono font-bold tracking-[0.2em] opacity-50 uppercase -mt-1">Memory_Engine // v0.1.0</span>
					</div>
				</a>

				<nav class="flex items-center space-x-2">
					{#each navItems as item}
						<a 
							href={item.href} 
							class="px-3 py-1.5 text-xs font-mono font-bold uppercase tracking-wider transition-all border-2 {$page.url.pathname === item.href ? 'bg-terminal-green text-void border-terminal-green' : 'border-transparent hover:border-border hover:bg-secondary'}"
						>
							<span class="mr-1 opacity-50">{item.icon}</span> {item.label}
						</a>
					{/each}

					<!-- Dark Mode Toggle -->
					<button
						on:click={toggleTheme}
						class="ml-2 brutal-btn !p-1.5 !px-2.5 text-sm"
						aria-label="Toggle dark mode"
					>
						{#if $theme === 'dark'}
							☀️
						{:else}
							🌙
						{/if}
					</button>
				</nav>
			</div>
		</div>
	</header>

	<!-- Main Content -->
	<main class="flex-1 container mx-auto px-4 py-8 relative">
		<div class="absolute top-0 left-0 w-full h-1 bg-terminal-green opacity-20"></div>
		<slot />
	</main>

	<!-- Footer -->
	<footer class="border-t-2 border-border bg-void text-concrete py-6 mt-8">
		<div class="container mx-auto px-4 flex flex-col md:flex-row items-center justify-between gap-4">
			<div class="text-[10px] font-mono font-bold tracking-widest opacity-50 uppercase">
				&copy; 2026 VERDUONA S.R.O. // OCELOT_PLATFORM
			</div>
			<div class="flex space-x-6 text-[10px] font-mono font-bold uppercase tracking-widest">
				<a href="https://github.com/adminmatej/github" class="hover:text-terminal-green transition-colors">[ GITHUB ]</a>
				<a href="/privacy" class="hover:text-terminal-green transition-colors">[ PRIVACY ]</a>
				<span class="text-cyan-data">STATUS: NOMINAL</span>
			</div>
		</div>
	</footer>
</div>

<style>
	:global(.container) {
		max-width: 1000px;
	}
</style>