<script lang="ts">
	import type { Snippet } from "svelte";
	import ThemeToggle from "$lib/components/ThemeToggle.svelte";
	import { contextPanelStore } from "$lib/stores/contextPanel";
	import {
		LayoutGridIcon as LayoutGrid,
		SettingsIcon as Settings,
		BarChart3Icon as BarChart3,
		CalendarIcon as Calendar,
		FolderKanbanIcon as FolderKanban,
		SparklesIcon as Sparkles,
	} from "lucide-svelte";

	interface Props {
		user?: {
			full_name?: string;
			email?: string;
			isPremium?: boolean;
			academyStatus?: string;
			academyInterest?: string;
		} | null;
		onLogout?: (() => void | Promise<void>) | null;
		onlogout?: () => void;
		children: Snippet;
	}

	let { user = null, onLogout = null, onlogout, children }: Props = $props();

	function handleLogout() {
		if (onLogout) {
			onLogout();
		} else if (onlogout) {
			onlogout();
		}
	}

	const quickActions = [
		{
			icon: FolderKanban,
			label: "Projects",
			action: () => contextPanelStore.open("projects"),
		},
		{
			icon: Calendar,
			label: "Calendar",
			action: () => contextPanelStore.open("calendar"),
		},
		{
			icon: BarChart3,
			label: "Analytics",
			action: () => contextPanelStore.open("analytics"),
		},
		{
			icon: Settings,
			label: "Settings",
			action: () => contextPanelStore.open("settings"),
		},
	];
</script>

<!--
  AI-First Shell - Simplified
  - Desktop: Centered container with app look
  - Mobile: Full screen
  - Navigation: Top quick actions + contextual panels
  - No bottom tabs - AI chat always central
-->
<div
	class="min-h-screen bg-neutral-100 dark:bg-neutral-900 flex items-center justify-center p-0 md:p-4 lg:p-8"
>
	<div
		class="w-full h-screen md:h-[calc(100vh-4rem)] lg:h-[calc(100vh-8rem)] max-w-[1920px] bg-background text-foreground relative flex flex-col md:border-2 md:border-black md:dark:border-white md:shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] md:dark:shadow-[8px_8px_0px_0px_rgba(255,255,255,1)] overflow-hidden"
	>
		<!-- Header -->
		<header
			class="flex-shrink-0 flex items-center justify-between p-4 border-b-2 border-black dark:border-white bg-card z-10"
		>
			<div class="flex items-center gap-3">
				<div
					class="w-8 h-8 border-2 border-black dark:border-white bg-primary text-primary-foreground flex items-center justify-center font-black text-sm"
				>
					{user?.full_name?.charAt(0).toUpperCase() || "F"}
				</div>
				<div class="font-black text-xl uppercase tracking-tighter">
					Focus <span class="text-muted-foreground text-sm font-normal normal-case">by Kraliki</span>
				</div>
				{#if !user?.isPremium}
					<a
						href="/dashboard/settings?tab=billing"
						class="hidden md:flex items-center gap-1.5 px-3 py-1 {user?.academyStatus ===
						'WAITLIST'
							? 'bg-secondary text-muted-foreground'
							: 'bg-terminal-green text-black'} text-[10px] font-black uppercase tracking-widest border-2 border-black {user?.academyStatus ===
						'WAITLIST'
							? ''
							: 'animate-pulse hover:animate-none'} transition-all shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] active:shadow-none active:translate-x-[1px] active:translate-y-[1px]"
					>
						<Sparkles class="w-3 h-3" />
						{user?.academyStatus === "WAITLIST"
							? "Waitlisted"
							: "Join Academy (Jan 1)"}
					</a>
				{/if}
			</div>
			<div class="flex items-center gap-1">
				<!-- Quick Actions -->
				{#each quickActions as { icon: IconComponent, label, action }}
					<button
						type="button"
						class="p-2 hover:bg-accent border-2 border-transparent hover:border-black dark:hover:border-white"
						onclick={action}
						title={label}
					>
						<IconComponent class="w-5 h-5" />
					</button>
				{/each}

				<div class="w-px h-6 bg-border mx-1"></div>

				<ThemeToggle />
				<button
					type="button"
					class="p-2 hover:bg-accent border-2 border-transparent hover:border-black dark:hover:border-white"
					onclick={handleLogout}
					title="Log out"
				>
					<svg
						xmlns="http://www.w3.org/2000/svg"
						width="20"
						height="20"
						viewBox="0 0 24 24"
						fill="none"
						stroke="currentColor"
						stroke-width="2"
						stroke-linecap="round"
						stroke-linejoin="round"
						class="lucide lucide-log-out"
						><path
							d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"
						/><polyline points="16 17 21 12 16 7" /><line
							x1="21"
							x2="9"
							y1="12"
							y2="12"
						/></svg
					>
				</button>
			</div>
		</header>

		<!-- Main Content Area (AI Chat - Always Visible) -->
		<main class="flex-1 overflow-hidden bg-background relative">
			{@render children()}
		</main>
	</div>
</div>
