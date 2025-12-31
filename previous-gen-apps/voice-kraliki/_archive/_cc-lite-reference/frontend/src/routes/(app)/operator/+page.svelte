<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { fly, fade } from 'svelte/transition';
  import { quintOut } from 'svelte/easing';
  import { trpc } from '$lib/trpc/client';
  import { auth } from '$lib/stores/auth.svelte';
  import { ws } from '$lib/stores/websocket.svelte';
  import { calls } from '$lib/stores/calls.svelte';
  import StatsCard from '$lib/components/shared/StatsCard.svelte';
  import Button from '$lib/components/shared/Button.svelte';
  import Badge from '$lib/components/shared/Badge.svelte';
  import ActiveCallPanel from '$lib/components/operator/ActiveCallPanel.svelte';
  import CallQueue from '$lib/components/operator/CallQueue.svelte';
  import AgentAssist from '$lib/components/operator/AgentAssist.svelte';
  import TranscriptionViewer from '$lib/components/operator/TranscriptionViewer.svelte';

  let loading = $state(true);
  let dashboardData = $state<any>(null);
  let agentStatus = $state<'AVAILABLE' | 'BUSY' | 'BREAK' | 'WRAP_UP' | 'OFFLINE'>('OFFLINE');
  let activeCall = $state<any>(null);
  let aiSuggestions = $state<any[]>([]);
  let knowledgeArticles = $state<any[]>([]);
  let transcriptEntries = $state<any[]>([]);

  // Generate sparkline data (mock trend data for stats)
  const generateSparklineData = (baseValue: number, points: number = 20) => {
    return Array.from({ length: points }, (_, i) => ({
      time: Date.now() / 1000 - (points - i) * 3600,
      value: baseValue + Math.random() * 10 - 5
    }));
  };

  let callsTrend = $state(generateSparklineData(20));
  let durationTrend = $state(generateSparklineData(180));
  let queueTrend = $state(generateSparklineData(2));
  let satisfactionTrend = $state(generateSparklineData(92));

  let queuedCalls = $state([
    {
      id: '1',
      customerName: 'John Smith',
      customerPhone: '+1 (555) 123-4567',
      waitTime: 45,
      priority: 'high' as const,
      campaignName: 'Sales Campaign Q4'
    },
    {
      id: '2',
      customerName: 'Sarah Johnson',
      customerPhone: '+1 (555) 987-6543',
      waitTime: 23,
      priority: 'normal' as const
    }
  ]);

  // Load AI suggestions when active call changes
  $effect(() => {
    if (activeCall) {
      loadAISuggestions(activeCall.id);
      const interval = setInterval(() => loadTranscripts(activeCall.id), 3000);
      return () => clearInterval(interval);
    }
  });

  // Auto-start demo call when available
  $effect(() => {
    if (!activeCall && agentStatus === 'AVAILABLE') {
      const timeout = setTimeout(() => {
        activeCall = {
          id: 'demo-call-1',
          customerName: 'Alice Johnson',
          customerPhone: '+1 (555) 234-5678',
          duration: 0,
          status: 'active' as const,
          sentiment: 'neutral' as const
        };
        transcriptEntries = [{
          id: '1',
          speaker: 'customer' as const,
          text: 'Hi, I\'m having trouble with my billing account',
          timestamp: new Date(),
          sentiment: 'neutral' as const
        }];
      }, 2000);
      return () => clearTimeout(timeout);
    }
  });

  async function loadAISuggestions(callId: string) {
    try {
      const lastMessages = transcriptEntries.map(t => `${t.speaker}: ${t.text}`);
      const result = await trpc.agentAssist.suggestions.mutate({
        callId,
        context: `Call with ${activeCall?.customerName}`,
        lastMessages
      });
      aiSuggestions = result.suggestions.map((s: any) => ({
        id: s.id,
        type: s.type,
        title: s.type.charAt(0).toUpperCase() + s.type.slice(1),
        content: s.text,
        confidence: s.confidence
      }));
      knowledgeArticles = result.articles.map((a: any) => ({
        id: a.id,
        title: a.title,
        summary: a.summary,
        relevance: a.relevanceScore || 0.5
      }));
    } catch (error) {
      console.error('AI error:', error);
    }
  }

  async function loadTranscripts(callId: string) {
    console.log('🎤 Fetching transcripts');
  }

  async function loadDashboard() {
    try {
      const data = await trpc.dashboard.getOverview.query();
      dashboardData = data;
    } catch {
      dashboardData = { stats: { totalCalls: 24, avgDuration: 185, satisfaction: 94 } };
    } finally {
      loading = false;
    }
  }

  async function updateAgentStatus(newStatus: typeof agentStatus) {
    try {
      await trpc.agent.updateStatus.mutate({ status: newStatus });
    } catch {}
    agentStatus = newStatus;
  }

  function getStatusVariant(status: string) {
    switch (status) {
      case 'AVAILABLE': return 'success';
      case 'BUSY': return 'warning';
      case 'BREAK': return 'primary';
      case 'WRAP_UP': return 'secondary';
      default: return 'gray';
    }
  }

  // Handle wrap-up transition after call ends
  $effect(() => {
    if (!activeCall && agentStatus === 'WRAP_UP') {
      // Auto-transition from WRAP_UP to AVAILABLE after 15 seconds
      const timeout = setTimeout(() => {
        if (agentStatus === 'WRAP_UP') {
          agentStatus = 'AVAILABLE';
        }
      }, 15000);
      return () => clearTimeout(timeout);
    }
  });

  onMount(() => {
    void (async () => {
      await loadDashboard();
      ws.connect();
    })();

    const interval = setInterval(loadDashboard, 30000);

    const handleCallEnded = (e: CustomEvent) => {
      if (e.detail?.requiresWrapUp && agentStatus === 'BUSY') {
        agentStatus = 'WRAP_UP';
      }
    };

    window.addEventListener('call-ended', handleCallEnded as EventListener);

    return () => {
      clearInterval(interval);
      window.removeEventListener('call-ended', handleCallEnded as EventListener);
    };
  });

  onDestroy(() => ws.disconnect());
</script>

<svelte:head>
  <title>Operator Dashboard - Voice by Kraliki</title>
</svelte:head>

<!-- Ambient Background Gradients -->
<div class="fixed inset-0 -z-10 overflow-hidden pointer-events-none">
  <div class="absolute -top-40 left-1/2 h-[480px] w-[720px] -translate-x-1/2 rounded-full bg-gradient-radial from-primary-500/25 via-primary-600/10 to-transparent blur-3xl"></div>
  <div class="absolute bottom-[-200px] right-[-120px] h-[520px] w-[520px] rounded-full bg-gradient-radial from-purple-500/25 via-purple-600/10 to-transparent blur-3xl"></div>
</div>

<div class="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900">
  <!-- Glassmorphic Header -->
  <header class="sticky top-0 z-50 border-b border-white/10 bg-black/40 backdrop-blur-xl">
    <div class="mx-auto max-w-7xl px-4 h-16 flex items-center justify-between">
      <div class="flex items-center gap-3">
        <div class="p-2 bg-primary-500/20 rounded-lg">
          <svg class="w-6 h-6 text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"></path>
          </svg>
        </div>
        <div>
          <h1 class="text-lg font-bold text-white">Operator Console</h1>
          <p class="text-xs text-gray-400">Welcome, {auth.user?.firstName || 'Agent'}</p>
        </div>
      </div>

      <div class="flex items-center gap-4">
        <!-- Connection Status -->
        <div class={`flex items-center gap-2 px-3 py-1.5 rounded-full text-sm backdrop-blur-sm ${
          ws.connected
            ? 'bg-green-500/20 text-green-400 border border-green-500/30'
            : 'bg-red-500/20 text-red-400 border border-red-500/30'
        }`}>
          <div class={`w-2 h-2 rounded-full ${ws.connected ? 'bg-green-400 animate-pulse' : 'bg-red-400'}`}></div>
          {ws.connected ? 'Connected' : 'Disconnected'}
        </div>

        <!-- Agent Status -->
        <Badge variant={getStatusVariant(agentStatus)} class="px-4 py-1.5">
          {agentStatus}
        </Badge>

        <!-- Status Controls -->
        <div class="flex gap-2">
          <Button
            size="sm"
            variant={agentStatus === 'AVAILABLE' ? 'success' : 'secondary'}
            onclick={() => updateAgentStatus('AVAILABLE')}
          >
            Available
          </Button>
          <Button
            size="sm"
            variant={agentStatus === 'BREAK' ? 'primary' : 'secondary'}
            onclick={() => updateAgentStatus('BREAK')}
          >
            Break
          </Button>
        </div>
      </div>
    </div>
  </header>

  {#if loading}
    <div class="flex justify-center items-center py-24">
      <div class="relative">
        <div class="w-16 h-16 border-4 border-primary-500/30 border-t-primary-500 rounded-full animate-spin"></div>
        <div class="absolute inset-0 w-16 h-16 border-4 border-transparent border-t-purple-500 rounded-full animate-spin" style="animation-delay: -0.3s;"></div>
      </div>
    </div>
  {:else}
    <main class="mx-auto max-w-7xl px-4 py-8">
      <!-- Stats Grid with Animation -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        {#each [
          {
            title: 'Calls Today',
            value: dashboardData?.stats?.totalCalls || 24,
            subtitle: 'Total handled',
            trend: callsTrend,
            trendColor: '#10b981'
          },
          {
            title: 'Avg Duration',
            value: `${Math.floor((dashboardData?.stats?.avgDuration || 185) / 60)}:${((dashboardData?.stats?.avgDuration || 185) % 60).toString().padStart(2, '0')}`,
            subtitle: 'Minutes',
            trend: durationTrend,
            trendColor: '#3b82f6'
          },
          {
            title: 'Queue',
            value: queuedCalls.length,
            subtitle: 'Waiting',
            trend: queueTrend,
            trendColor: '#f59e0b'
          },
          {
            title: 'Satisfaction',
            value: `${dashboardData?.stats?.satisfaction || 94}%`,
            subtitle: 'CSAT Score',
            trend: satisfactionTrend,
            trendColor: '#8b5cf6'
          }
        ] as stat, i}
          <div
            in:fly={{ y: 20, duration: 400, delay: i * 100, easing: quintOut }}
            out:fade
          >
            <StatsCard {...stat} />
          </div>
        {/each}
      </div>

      <!-- Main Content with Glassmorphism -->
      <div class="grid grid-cols-1 xl:grid-cols-3 gap-6">
        <!-- Left: Active Call & Queue -->
        <div class="xl:col-span-2 space-y-6">
          <div
            in:fly={{ x: -20, duration: 500, easing: quintOut }}
            class="backdrop-blur-sm bg-white/5 border border-white/10 rounded-2xl p-1 shadow-2xl"
          >
            <ActiveCallPanel bind:call={activeCall} />
          </div>

          <div
            in:fly={{ x: -20, duration: 500, delay: 100, easing: quintOut }}
            class="backdrop-blur-sm bg-white/5 border border-white/10 rounded-2xl p-1 shadow-2xl"
          >
            <CallQueue calls={queuedCalls} />
          </div>
        </div>

        <!-- Right: AI Assist & Transcription -->
        <div class="space-y-6">
          <div
            in:fly={{ x: 20, duration: 500, easing: quintOut }}
            class="backdrop-blur-sm bg-white/5 border border-white/10 rounded-2xl p-1 shadow-2xl"
          >
            <AgentAssist suggestions={aiSuggestions} articles={knowledgeArticles} />
          </div>

          <div
            in:fly={{ x: 20, duration: 500, delay: 100, easing: quintOut }}
            class="backdrop-blur-sm bg-white/5 border border-white/10 rounded-2xl p-1 shadow-2xl"
          >
            <TranscriptionViewer entries={transcriptEntries} />
          </div>
        </div>
      </div>
    </main>
  {/if}
</div>

<style>
  .bg-gradient-radial {
    background: radial-gradient(circle, var(--tw-gradient-stops));
  }
</style>
