<script lang="ts">
	import {
		LayoutDashboard,
		PhoneOutgoing,
		PhoneIncoming,
		Building2,
		Workflow,
		Settings,
		UserCircle,
		LogOut,
		Mic,
		Mail,
		Phone,
		GitBranch,
		BarChart3
	} from 'lucide-svelte';
	import { page } from '$app/stores';
	import { onDestroy } from 'svelte';
	import ThemeToggle from './ThemeToggle.svelte';
	import LanguageSwitcher from './LanguageSwitcher.svelte';
	import { authStore, type AuthState } from '$lib/stores/auth';

	type IconComponent = typeof LayoutDashboard;

	interface NavItem {
		label: string;
		href: string;
		icon: IconComponent;
	}

	const navItems: NavItem[] = [
		{ label: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
		{ label: 'Outbound', href: '/calls/outbound', icon: PhoneOutgoing },
		{ label: 'Incoming', href: '/calls/incoming', icon: PhoneIncoming },
		{ label: 'Companies', href: '/companies', icon: Building2 },
		{ label: 'Campaigns', href: '/campaigns', icon: Workflow },
		{ label: 'IVR', href: '/operations/ivr', icon: Phone },
		{ label: 'Routing', href: '/operations/routing', icon: GitBranch },
		{ label: 'Recordings', href: '/operations/recordings', icon: Mic },
		{ label: 'Voicemail', href: '/operations/voicemail', icon: Mail },
		{ label: 'Analytics', href: '/analytics/dashboard', icon: BarChart3 },
		{ label: 'Settings', href: '/settings', icon: Settings }
	];

	let currentPath = $state<string>('/');
	let auth = $state<AuthState>(authStore.getSnapshot());

	const unsubscribePage = page.subscribe(($page) => {
		currentPath = $page.url.pathname;
	});

	const unsubscribeAuth = authStore.subscribe((value) => {
		auth = value;
	});

	onDestroy(() => {
		unsubscribePage();
		unsubscribeAuth();
	});

	function isActive(path: string) {
		return currentPath.startsWith(path);
	}

	function handleSignOut() {
		authStore.logout();
	}
</script>

<header class="header">
	<div class="brand">
		<div class="brand-mark">
			<span class="brand-initials">AO</span>
		</div>
		<div class="brand-copy">
			<span class="brand-title">Operator Console</span>
			<span class="brand-subtitle">Stack 2026 · Machine Cold UI</span>
		</div>
	</div>

	<nav class="nav">
		{#each navItems as item}
			{@const Icon = item.icon}
			<a href={item.href} class={`nav-item ${isActive(item.href) ? 'is-active' : ''}`}>
				<Icon class="size-4 shrink-0" />
				<span>{item.label}</span>
			</a>
		{/each}
	</nav>

	<div class="actions">
		<LanguageSwitcher />
		<ThemeToggle />
		<div class="user-chip">
			<UserCircle class="size-5" />
			<div class="flex flex-col leading-none">
				<span class="user-name">{auth.user?.name ?? 'Operator'}</span>
				<span class="user-role">
					{#if auth.status === 'authenticated'}
						{auth.user?.role ?? 'Agent'}
					{:else}
						Signed out
					{/if}
				</span>
			</div>
		</div>
		<button type="button" onclick={handleSignOut} class="btn btn-ghost btn-sm signout">
			<LogOut class="size-4" />
			<span>Sign out</span>
		</button>
	</div>
</header>

<style>
	.header {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 1rem;
		padding: 0.85rem 1rem;
		background: hsl(var(--card));
		color: hsl(var(--foreground));
		border: 2px solid hsl(var(--border));
		box-shadow: var(--shadow-brutal);
	}

	.brand {
		display: flex;
		align-items: center;
		gap: 0.75rem;
	}

	.brand-mark {
		width: 40px;
		height: 40px;
		display: flex;
		align-items: center;
		justify-content: center;
		background: hsl(var(--primary) / 0.15);
		color: hsl(var(--primary));
		border: 2px solid hsl(var(--border));
		box-shadow: var(--shadow-brutal-subtle);
	}

	.brand-initials {
		font-weight: 800;
		font-size: 1rem;
		letter-spacing: 0.05em;
	}

	.brand-copy {
		display: flex;
		flex-direction: column;
		gap: 0.1rem;
	}

	.brand-title {
		font-size: 0.95rem;
		font-weight: 800;
		letter-spacing: 0.03em;
		text-transform: uppercase;
	}

	.brand-subtitle {
		font-size: 0.75rem;
		color: hsl(var(--muted-foreground));
	}

	.nav {
		display: none;
		align-items: center;
		gap: 0.5rem;
	}

	.nav-item {
		display: inline-flex;
		align-items: center;
		gap: 0.5rem;
		padding: 0.6rem 0.9rem;
		border: 2px solid hsl(var(--border));
		background: hsl(var(--card));
		color: hsl(var(--foreground));
		box-shadow: var(--shadow-brutal-subtle);
		font-weight: 800;
		text-transform: uppercase;
		letter-spacing: 0.05em;
		transition: transform 60ms linear, box-shadow 60ms linear, background-color 60ms linear, color 60ms linear;
	}

	.nav-item:hover {
		background: var(--color-terminal-green);
		color: #000;
		transform: translate(2px, 2px);
		box-shadow: 2px 2px 0px 0px hsl(var(--foreground));
	}

	.nav-item.is-active {
		background: var(--color-terminal-green);
		color: #000;
	}

	.actions {
		display: flex;
		align-items: center;
		gap: 0.5rem;
	}

	.user-chip {
		display: none;
		align-items: center;
		gap: 0.5rem;
		padding: 0.5rem 0.75rem;
		border: 2px solid hsl(var(--border));
		background: hsl(var(--secondary));
		box-shadow: var(--shadow-brutal-subtle);
	}

	.user-name {
		font-size: 0.85rem;
		font-weight: 800;
		color: hsl(var(--foreground));
	}

	.user-role {
		font-size: 0.7rem;
		color: hsl(var(--muted-foreground));
	}

	.signout {
		display: none;
	}

	@media (min-width: 768px) {
		.nav {
			display: flex;
		}

		.user-chip,
		.signout {
			display: inline-flex;
		}
	}
</style>
