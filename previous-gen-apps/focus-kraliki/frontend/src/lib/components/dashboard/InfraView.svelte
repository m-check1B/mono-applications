<script lang="ts">
    import { onMount } from 'svelte';
    import { api } from '$lib/api/client';
    import { Activity, Terminal, RefreshCw, AlertTriangle, CheckCircle2, Server, Clock, Database } from 'lucide-svelte';

    let status: any = null;
    let logs: string = '';
    let selectedService: 'backend' | 'frontend' = 'backend';
    let isLoadingStatus = false;
    let isLoadingLogs = false;
    let error: string | null = null;

    onMount(() => {
        loadStatus();
        loadLogs();
    });

    async function loadStatus() {
        isLoadingStatus = true;
        try {
            const res = await api.get<any>('/infra/status');
            status = res.data;
        } catch (e: any) {
            error = e.message;
        } finally {
            isLoadingStatus = false;
        }
    }

    async function loadLogs() {
        isLoadingLogs = true;
        try {
            const res = await api.get<any>(`/infra/logs/${selectedService}`);
            logs = res.data.content;
        } catch (e: any) {
             logs = `Failed to load logs: ${e.message}`;
        } finally {
            isLoadingLogs = false;
        }
    }

    function handleServiceChange(service: 'backend' | 'frontend') {
        selectedService = service;
        loadLogs();
    }
</script>

<div class="h-full flex flex-col relative overflow-hidden">
    <!-- Header -->
	<div class="flex-shrink-0 p-6 border-b-2 border-black dark:border-white flex items-center justify-between bg-background z-10">
		<div class="flex items-center gap-3">
			<div class="p-2 border-2 border-black dark:border-white bg-secondary text-secondary-foreground">
				<Server class="w-6 h-6" />
			</div>
			<div>
				<h2 class="text-2xl font-black uppercase tracking-tighter">Infrastructure</h2>
				<p class="text-sm font-bold text-muted-foreground">System Status & Logs</p>
			</div>
		</div>
		<button
			class="brutal-btn bg-white text-black flex items-center gap-2"
			onclick={() => { loadStatus(); loadLogs(); }}
		>
			<RefreshCw class="w-4 h-4 {isLoadingStatus ? 'animate-spin' : ''}" />
			Refresh
		</button>
	</div>

    <div class="flex-1 overflow-y-auto p-6 space-y-6">
        <!-- Status Cards -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <!-- System Health -->
             <div class="brutal-card p-4">
                <div class="flex items-center justify-between mb-2">
                    <span class="text-xs font-black uppercase text-muted-foreground">System Health</span>
                    <Activity class="w-4 h-4" />
                </div>
                <div class="flex items-center gap-2">
                    {#if status?.system === 'healthy'}
                        <CheckCircle2 class="w-6 h-6 text-green-500" />
                        <span class="text-xl font-black uppercase">Healthy</span>
                    {:else}
                        <AlertTriangle class="w-6 h-6 text-red-500" />
                        <span class="text-xl font-black uppercase">{status?.system || 'Unknown'}</span>
                    {/if}
                </div>
             </div>

             <!-- Uptime -->
             <div class="brutal-card p-4">
                <div class="flex items-center justify-between mb-2">
                    <span class="text-xs font-black uppercase text-muted-foreground">Uptime</span>
                    <Clock class="w-4 h-4" />
                </div>
                <div class="text-xl font-black font-mono">
                    {status ? Math.floor(status.uptime_seconds / 60) : 0} min
                </div>
             </div>

             <!-- Database -->
             <div class="brutal-card p-4">
                <div class="flex items-center justify-between mb-2">
                    <span class="text-xs font-black uppercase text-muted-foreground">Database</span>
                    <Database class="w-4 h-4" />
                </div>
                 <div class="text-lg font-bold uppercase">
                    {status?.services?.database || 'Checking...'}
                </div>
             </div>
        </div>

        <!-- Logs Viewer -->
        <div class="brutal-card flex flex-col h-[500px]">
            <div class="p-4 border-b-2 border-black dark:border-white bg-secondary flex items-center justify-between">
                <div class="flex items-center gap-2 font-bold uppercase">
                    <Terminal class="w-4 h-4" />
                    System Logs
                </div>
                <div class="flex border-2 border-black dark:border-white">
                    <button
                        class="px-3 py-1 text-xs font-bold uppercase {selectedService === 'backend' ? 'bg-black text-white dark:bg-white dark:text-black' : 'bg-white text-black hover:bg-gray-200 dark:bg-black dark:text-white dark:hover:bg-gray-800'}"
                        onclick={() => handleServiceChange('backend')}
                    >
                        Backend
                    </button>
                    <button
                        class="px-3 py-1 text-xs font-bold uppercase border-l-2 border-black dark:border-white {selectedService === 'frontend' ? 'bg-black text-white dark:bg-white dark:text-black' : 'bg-white text-black hover:bg-gray-200 dark:bg-black dark:text-white dark:hover:bg-gray-800'}"
                        onclick={() => handleServiceChange('frontend')}
                    >
                        Frontend
                    </button>
                </div>
            </div>
            <div class="flex-1 overflow-auto p-4 bg-black text-green-400 font-mono text-xs">
                <pre class="whitespace-pre-wrap">{logs || 'Loading logs...'}</pre>
            </div>
        </div>
    </div>
</div>
