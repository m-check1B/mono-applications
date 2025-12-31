<script lang="ts">
	import { useAppConfig } from '$lib/hooks/useAppConfig';
	import { PhoneCall, PhoneIncoming, Activity, Clock, Users, Target, CheckCircle, AlertCircle } from 'lucide-svelte';
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';
	import { createQuery } from '@tanstack/svelte-query';
	import { fetchCompanies, fetchCampaigns, fetchTelephonyStats } from '$lib/services/calls';
	import { apiGet } from '$lib/utils/api';

	const config = useAppConfig();

	// Fetch real metrics
	const companiesQuery = createQuery({
		queryKey: ['companies-count'],
		queryFn: fetchCompanies,
		staleTime: 30_000
	});

	const campaignsQuery = createQuery({
		queryKey: ['campaigns-count'],
		queryFn: fetchCampaigns,
		staleTime: 30_000
	});

	const healthQuery = createQuery({
		queryKey: ['health'],
		queryFn: () => apiGet<{ status: string; version: string; environment: string }>('/health'),
		staleTime: 10_000
	});

	const telephonyStatsQuery = createQuery({
		queryKey: ['telephony-stats'],
		queryFn: fetchTelephonyStats,
		staleTime: 15_000
	});

	let totalCompanies = $state(0);
	let totalCampaigns = $state(0);
	let systemStatus = $state('checking...');
	let callsToday = $state(0);
	let completedCalls = $state(0);
	let activeCalls = $state(0);
	let successRate = $state(0);

	$effect(() => {
		totalCompanies = $companiesQuery.data?.length || 0;
		totalCampaigns = $campaignsQuery.data?.length || 0;
		systemStatus = $healthQuery.data?.status || 'checking...';

		// Use real telephony stats
		if ($telephonyStatsQuery.data) {
			callsToday = $telephonyStatsQuery.data.total_calls;
			completedCalls = $telephonyStatsQuery.data.completed_calls;
			activeCalls = $telephonyStatsQuery.data.active_calls;
			// Calculate success rate (completed / total * 100)
			if (callsToday > 0) {
				successRate = Math.round((completedCalls / callsToday) * 100);
			} else {
				successRate = 0;
			}
		}
	});

	const overviewTiles = [
		{
			label: 'Total Companies',
			value: totalCompanies,
			icon: Users,
			color: 'text-cyan-data'
		},
		{
			label: 'Active Campaigns',
			value: totalCampaigns,
			icon: Target,
			color: 'text-terminal-green'
		},
		{
			label: 'Calls Today',
			value: callsToday,
			icon: PhoneCall,
			color: 'text-accent'
		},
		{
			label: 'Success Rate',
			value: `${successRate}%`,
			icon: CheckCircle,
			color: 'text-terminal-green'
		}
	];

	const systemInfo = [
		{
			label: 'System Status',
			value: systemStatus,
			icon: systemStatus === 'healthy' ? CheckCircle : AlertCircle,
			color: systemStatus === 'healthy' ? 'text-terminal-green' : 'text-system-red'
		},
		{
			label: 'Backend',
			value: config.backendUrl,
			icon: Activity,
			color: 'text-muted-foreground'
		},
		{
			label: 'WebSocket',
			value: config.wsUrl,
			icon: PhoneIncoming,
			color: 'text-muted-foreground'
		},
		{
			label: 'Last Updated',
			value: new Date().toLocaleTimeString(),
			icon: Clock,
			color: 'text-muted-foreground'
		}
	];
</script>

<section class="space-y-12">
	<header class="flex flex-col gap-6 md:flex-row md:items-end md:justify-between border-b-2 border-foreground pb-8">
		<div class="space-y-2">
			<h1 class="text-5xl font-display text-foreground tracking-tighter uppercase">
				Operator Console <span class="text-terminal-green">Overview</span>
			</h1>
			<p class="text-[11px] font-bold uppercase tracking-[0.3em] text-muted-foreground">
				SYSTEM_STATUS: {systemStatus} // ENVIROMENT: PRODUCTION // VERSION: 1.0.4-LITE
			</p>
		</div>
		<div class="flex items-center gap-4">
			<button class="brutal-btn bg-terminal-green text-void" onclick={() => goto('/calls/outbound')}>
				Start Outbound Session
			</button>
			<button class="brutal-btn bg-void text-terminal-green border-terminal-green" onclick={() => goto('/calls/incoming')}>
				Manage Incoming
			</button>
		</div>
	</header>

	<!-- Main Metrics -->
	<div class="grid gap-6 md:grid-cols-2 xl:grid-cols-4">
		{#each overviewTiles as tile}
			{@const Icon = tile.icon}
			<article class="brutal-card p-6 hover:translate-x-[-2px] hover:translate-y-[-2px] transition-all group hover:border-terminal-green hover:shadow-[8px_8px_0px_0px_rgba(51,255,0,1)]">
				<div class="flex items-start justify-between">
					<div class="space-y-3">
						<p class="text-[10px] font-bold uppercase tracking-widest text-muted-foreground flex items-center gap-2">
							<span class="w-2 h-2 bg-foreground/20 group-hover:bg-terminal-green"></span>
							{tile.label}
						</p>
						<p class="text-4xl font-display text-foreground">{tile.value}</p>
					</div>
					<div class="flex size-12 items-center justify-center border-2 border-foreground group-hover:border-terminal-green group-hover:text-terminal-green {tile.color}">
						<Icon class="size-6" />
					</div>
				</div>
			</article>
		{/each}
	</div>

	<!-- System Information -->
	<div class="grid gap-6 md:grid-cols-2 xl:grid-cols-4">
		{#each systemInfo as info}
			{@const Icon = info.icon}
			<article class="brutal-card p-4 border-muted/30 shadow-[4px_4px_0px_0px_rgba(0,0,0,0.1)] hover:shadow-brutal hover:border-foreground transition-all">
				<div class="flex items-center justify-between">
					<div class="space-y-1">
						<p class="text-[9px] font-bold uppercase tracking-wider text-muted-foreground">{info.label}</p>
						<p class="text-[11px] font-mono font-bold text-foreground break-all">{info.value}</p>
					</div>
					<div class="flex size-8 items-center justify-center border border-muted/30 {info.color}">
						<Icon class="size-4" />
					</div>
				</div>
			</article>
		{/each}
	</div>

	<div class="grid grid-cols-1 lg:grid-cols-12 gap-8">
		<article class="brutal-card lg:col-span-8 p-8 relative overflow-hidden">
			<div class="absolute top-0 right-0 p-4 opacity-5">
				<Activity class="size-32" />
			</div>
			
			<div class="relative z-10">
				<div class="flex items-center gap-3 mb-6">
					<div class="w-4 h-4 bg-terminal-green"></div>
					<h2 class="text-3xl font-display uppercase">Next Operations</h2>
				</div>
				
				<div class="grid grid-cols-1 md:grid-cols-2 gap-8">
					<div class="space-y-4">
						<p class="text-sm font-mono text-muted-foreground leading-relaxed italic border-l-2 border-terminal-green pl-4">
							"Continue migration by wiring data sources and testing real-time flows. System integrity is priority #1."
						</p>
						<ul class="space-y-4 text-[11px] font-bold uppercase tracking-widest text-foreground">
							<li class="flex items-center gap-3">
								<span class="text-terminal-green font-mono">[01]</span>
								<span>Configure outbound models</span>
							</li>
							<li class="flex items-center gap-3">
								<span class="text-terminal-green font-mono">[02]</span>
								<span>Validate WebSocket events</span>
							</li>
							<li class="flex items-center gap-3">
								<span class="text-terminal-green font-mono">[03]</span>
								<span>Integrate provider health</span>
							</li>
						</ul>
					</div>
					
					<div class="bg-muted/5 border-2 border-muted/20 p-6 font-mono text-[10px] text-muted-foreground space-y-2">
						<p class="text-terminal-green font-bold">>> SYSTEM_LOG_EXTRACT</p>
						<p>[23:13:22] GE-designer-23:13.22.12.AA: Applying Style 2026...</p>
						<p>[23:13:24] Dashboard UI refactored to Brutalism.</p>
						<p>[23:13:25] All shadows offset 4px solid.</p>
						<p>[23:13:26] Scanning for non-compliant elements...</p>
						<div class="flex gap-1 mt-4">
							<div class="w-1 h-3 bg-terminal-green animate-pulse"></div>
							<div class="w-1 h-3 bg-terminal-green animate-pulse delay-75"></div>
							<div class="w-1 h-3 bg-terminal-green animate-pulse delay-150"></div>
						</div>
					</div>
				</div>
			</div>
		</article>

		<aside class="lg:col-span-4 space-y-6">
			<div class="brutal-card p-6 bg-void text-terminal-green border-terminal-green shadow-[6px_6px_0px_0px_rgba(51,255,0,0.3)]">
				<h3 class="font-display text-xl mb-4 uppercase tracking-tighter">Terminal Feed</h3>
				<div class="font-mono text-[10px] space-y-3">
					<div class="flex justify-between border-b border-terminal-green/20 pb-1">
						<span>OUTBOUND_ENGINE</span>
						<span class="text-cyan-data">ACTIVE</span>
					</div>
					<div class="flex justify-between border-b border-terminal-green/20 pb-1">
						<span>TRANSCRIPTION_V2</span>
						<span class="text-terminal-green">READY</span>
					</div>
					<div class="flex justify-between border-b border-terminal-green/20 pb-1">
						<span>IVR_ROUTING</span>
						<span class="text-system-red">ERROR_404</span>
					</div>
				</div>
				<button class="mt-6 w-full py-2 border border-terminal-green text-[9px] font-bold uppercase hover:bg-terminal-green hover:text-void transition-colors">
					Access Low-Level Logs
				</button>
			</div>
		</aside>
	</div>
</section>
