<script lang="ts">
	import {
		LayoutDashboard,
		PhoneOutgoing,
		PhoneIncoming,
		Building2,
		Workflow,
		MessageCircle,
		Settings
	} from 'lucide-svelte';
import { page } from '$app/stores';
import { onDestroy } from 'svelte';

	type IconComponent = typeof LayoutDashboard;

	interface NavItem {
		label: string;
		href: string;
		icon: IconComponent;
	}

	const navItems: NavItem[] = [
		{ label: 'Home', href: '/dashboard', icon: LayoutDashboard },
		{ label: 'Outbound', href: '/calls/outbound', icon: PhoneOutgoing },
		{ label: 'Incoming', href: '/calls/incoming', icon: PhoneIncoming },
		{ label: 'Chat', href: '/chat', icon: MessageCircle },
		{ label: 'Companies', href: '/companies', icon: Building2 },
		{ label: 'Settings', href: '/settings', icon: Settings }
	];

let currentPath = $state<string>('/');

const unsubscribe = page.subscribe(($page) => {
	currentPath = $page.url.pathname;
});

onDestroy(() => {
	unsubscribe();
});

function isActive(path: string) {
	return currentPath.startsWith(path);
}
</script>

<nav class="bottom-nav">
	{#each navItems as item}
		{@const Icon = item.icon}
		<a href={item.href} class={`nav-item ${isActive(item.href) ? 'is-active' : ''}`}>
			<Icon class="size-5" />
			<span>{item.label}</span>
		</a>
	{/each}
</nav>

<style>
	.bottom-nav {
		display: grid;
		grid-template-columns: repeat(3, minmax(0, 1fr));
		gap: 0.5rem;
		padding: 0.75rem;
		border-top: 2px solid hsl(var(--border));
		background: hsl(var(--card));
		box-shadow: var(--shadow-brutal);
	}

	.nav-item {
		display: inline-flex;
		min-height: var(--touch-target);
		flex-direction: column;
		align-items: center;
		justify-content: center;
		gap: 0.25rem;
		padding: 0.4rem 0.5rem;
		border: 2px solid hsl(var(--border));
		background: hsl(var(--card));
		color: hsl(var(--muted-foreground));
		font-weight: 800;
		text-transform: uppercase;
		letter-spacing: 0.05em;
		box-shadow: var(--shadow-brutal-subtle);
		transition: transform 60ms linear, box-shadow 60ms linear, background-color 60ms linear, color 60ms linear;
		text-align: center;
		font-size: 0.8rem;
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

	@media (min-width: 640px) {
		.bottom-nav {
			grid-template-columns: repeat(6, minmax(0, 1fr));
		}
	}
</style>
