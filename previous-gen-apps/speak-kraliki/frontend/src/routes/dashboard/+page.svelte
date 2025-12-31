<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { authStore, accessToken, isAuthenticated } from '$stores/auth';
  import { insights, alerts, actions } from '$api/client';
  import { t } from '$lib/i18n';

  let overview = $state<any>(null);
  let recentAlerts = $state<any[]>([]);
  let recentActions = $state<any[]>([]);
  let loading = $state(true);

  onMount(async () => {
    if (!$isAuthenticated) {
      goto('/login');
      return;
    }

    try {
      const token = $accessToken!;
      [overview, recentAlerts, recentActions] = await Promise.all([
        insights.overview(token),
        alerts.list(token, { is_read: false }),
        actions.list(token),
      ]);
    } catch (e) {
      console.error('Failed to load dashboard', e);
    } finally {
      loading = false;
    }
  });

  function formatPercent(value: number): string {
    return `${Math.round(value * 100)}%`;
  }

  function formatSentiment(value: number): string {
    if (value > 0.2) return $t('sentiment.positive').toUpperCase();
    if (value < -0.2) return $t('sentiment.negative').toUpperCase();
    return $t('sentiment.neutral').toUpperCase();
  }

  function getSentimentColor(value: number): string {
    if (value > 0.2) return 'text-terminal-green';
    if (value < -0.2) return 'text-system-red';
    return 'text-muted-foreground';
  }

  function getStatusLabel(status: string): string {
    const labels: Record<string, string> = {
      new: $t('status.new').toUpperCase(),
      heard: $t('status.heard').toUpperCase(),
      in_progress: $t('status.inProgress').toUpperCase(),
      resolved: $t('status.resolved').toUpperCase(),
    };
    return labels[status] || status;
  }
</script>

<svelte:head>
  <title>{$t('dashboard.title')} - Speak by Kraliki</title>
</svelte:head>

<div class="container mx-auto p-6 bg-grid-pattern min-h-screen">
  <div class="flex flex-col md:flex-row md:items-end justify-between mb-12 border-b-2 border-foreground pb-8 gap-6">
    <div>
      <h1 class="text-5xl font-display tracking-tighter uppercase mb-2">
        Speak <span class="text-terminal-green">INTELLIGENCE</span>
      </h1>
      <p class="text-[11px] font-mono font-bold uppercase tracking-[0.3em] text-muted-foreground flex items-center gap-2">
        <span class="w-2 h-2 bg-terminal-green animate-pulse"></span>
        Status: Live_Stream // Feed: Enterprise_Feedback_Loop
      </p>
    </div>
    <div class="flex items-center gap-4">
      <a href="/dashboard/surveys" class="brutal-btn bg-terminal-green text-void font-display text-lg">
        {($t('dashboard.newCampaign') || 'NEW_CAMPAIGN').toUpperCase()}
      </a>
    </div>
  </div>

  {#if loading}
    <div class="text-center py-24 brutal-card bg-void text-terminal-green border-terminal-green">
      <span class="animate-pulse font-mono font-black tracking-[0.5em] text-xl">>> INITIALIZING_DATA_STREAM...</span>
    </div>
  {:else if overview}
    <!-- Key Metrics -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
      <!-- Sentiment Gauge -->
      <div class="brutal-card p-6 group hover:border-terminal-green hover:-translate-y-1 hover:-translate-x-1 transition-all">
        <div class="text-[10px] font-black uppercase tracking-widest text-muted-foreground mb-3 flex items-center gap-2">
            <div class="w-1 h-3 bg-foreground/20 group-hover:bg-terminal-green"></div>
            {($t('dashboard.sentiment') || 'SENTIMENT').toUpperCase()}
        </div>
        <div class="text-4xl font-display {getSentimentColor(overview.sentiment.current)}">
          {formatSentiment(overview.sentiment.current)}
        </div>
        <div class="text-[11px] font-mono text-muted-foreground mt-3 pt-3 border-t border-foreground/10">
          RAW: {overview.sentiment.current.toFixed(2)}
          {#if overview.sentiment.change !== null}
            <span class="{overview.sentiment.change > 0 ? 'text-terminal-green' : 'text-system-red'} font-bold">
              ({overview.sentiment.change > 0 ? '+' : ''}{overview.sentiment.change.toFixed(2)})
            </span>
          {/if}
        </div>
      </div>

      <!-- Participation -->
      <div class="brutal-card p-6 group hover:border-terminal-green hover:-translate-y-1 hover:-translate-x-1 transition-all">
        <div class="text-[10px] font-black uppercase tracking-widest text-muted-foreground mb-3 flex items-center gap-2">
            <div class="w-1 h-3 bg-foreground/20 group-hover:bg-terminal-green"></div>
            {($t('dashboard.participation') || 'PARTICIPATION').toUpperCase()}
        </div>
        <div class="text-4xl font-display text-terminal-green">
          {formatPercent(overview.participation.current)}
        </div>
        <div class="text-[11px] font-mono text-muted-foreground mt-3 pt-3 border-t border-foreground/10">
          {overview.participation.total_completed} <span class="opacity-50">/</span> {overview.participation.total_invited} SIGNALS
        </div>
      </div>

      <!-- Active Alerts -->
      <div class="brutal-card p-6 group hover:border-system-red hover:-translate-y-1 hover:-translate-x-1 transition-all">
        <div class="text-[10px] font-black uppercase tracking-widest text-muted-foreground mb-3 flex items-center gap-2">
            <div class="w-1 h-3 bg-foreground/20 group-hover:bg-system-red"></div>
            {($t('dashboard.activeAlerts') || 'ALERTS').toUpperCase()}
        </div>
        <div class="text-4xl font-display {overview.active_alerts_count > 0 ? 'text-system-red' : 'text-terminal-green'}">
          {overview.active_alerts_count}
        </div>
        <div class="text-[11px] font-mono text-muted-foreground mt-3 pt-3 border-t border-foreground/10">
          <a href="/dashboard/alerts" class="hover:text-foreground">[ VIEW_INCIDENTS ]</a>
        </div>
      </div>

      <!-- Pending Actions -->
      <div class="brutal-card p-6 group hover:border-cyan-data hover:-translate-y-1 hover:-translate-x-1 transition-all">
        <div class="text-[10px] font-black uppercase tracking-widest text-muted-foreground mb-3 flex items-center gap-2">
            <div class="w-1 h-3 bg-foreground/20 group-hover:bg-cyan-data"></div>
            {($t('dashboard.pendingActions') || 'ACTIONS').toUpperCase()}
        </div>
        <div class="text-4xl font-display text-cyan-data">
          {overview.pending_actions_count}
        </div>
        <div class="text-[11px] font-mono text-muted-foreground mt-3 pt-3 border-t border-foreground/10">
          <a href="/dashboard/actions" class="hover:text-foreground">[ MANAGE_LOOP ]</a>
        </div>
      </div>
    </div>

    <!-- Two Column Layout -->
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-8">
      <!-- Top Topics -->
      <div class="brutal-card lg:col-span-4 p-8 bg-void text-white border-white">
        <div class="flex items-center gap-3 mb-8 border-b-2 border-white/20 pb-4">
            <div class="w-3 h-3 bg-cyan-data"></div>
            <h2 class="text-2xl font-display uppercase tracking-tighter text-cyan-data">{($t('dashboard.topics') || 'SIGNAL_CLUSTERS').toUpperCase()}</h2>
        </div>
        
        {#if overview.top_topics.length > 0}
          <div class="space-y-6">
            {#each overview.top_topics as topic}
              <div class="space-y-1">
                <div class="flex items-center justify-between">
                  <span class="text-[10px] font-black tracking-widest uppercase">{topic.topic}</span>
                  <span class="text-[10px] font-mono text-terminal-green">{topic.count}X</span>
                </div>
                <div class="w-full h-2 bg-white/10 border border-white/20 relative">
                    <div class="absolute inset-y-0 left-0 bg-cyan-data" style="width: {(topic.count / overview.top_topics[0].count) * 100}%"></div>
                </div>
                <div class="text-[9px] font-mono {getSentimentColor(topic.sentiment)}">
                    SENTIMENT: {topic.sentiment.toFixed(2)}
                </div>
              </div>
            {/each}
          </div>
        {:else}
          <p class="text-muted-foreground font-mono text-xs opacity-50">{$t('dashboard.noTopics') || 'NO_SIGNALS_MAPPED'}</p>
        {/if}
      </div>

      <!-- Recent Alerts -->
      <div class="brutal-card lg:col-span-8 p-8 overflow-hidden relative">
        <div class="absolute top-0 right-0 p-4 opacity-5 pointer-events-none">
            <div class="text-9xl font-display uppercase">ALERT</div>
        </div>
        
        <div class="flex items-center justify-between mb-8 border-b-2 border-foreground pb-4 relative z-10">
          <div class="flex items-center gap-3">
              <div class="w-3 h-3 bg-system-red animate-pulse"></div>
              <h2 class="text-2xl font-display uppercase tracking-tighter">{($t('dashboard.alerts') || 'LIVE_ALERT_STREAM').toUpperCase()}</h2>
          </div>
          <a href="/dashboard/alerts" class="text-[10px] font-bold uppercase tracking-widest border-2 border-foreground px-3 py-1 hover:bg-void hover:text-white transition-colors">
            {($t('dashboard.viewAll') || 'FULL_LOGS').toUpperCase()}
          </a>
        </div>

        {#if recentAlerts.length > 0}
          <div class="space-y-4 relative z-10">
            {#each recentAlerts.slice(0, 3) as alert}
            <div class="p-4 border-2 border-foreground bg-void text-white brutal-shadow-sm hover:translate-x-[-2px] hover:translate-y-[-2px] transition-all">
                <div class="flex items-center justify-between mb-2">
                  <span class="text-[10px] font-black uppercase tracking-widest {alert.severity === 'high' ? 'text-system-red' : 'text-cyan-data'}">
                    // TYPE_{alert.type.toUpperCase()}
                  </span>
                  <span class="text-[9px] font-mono text-muted-foreground">
                    TS_{new Date(alert.created_at).getTime()}
                  </span>
                </div>
                <p class="text-sm font-mono leading-relaxed border-l-2 border-terminal-green/30 pl-3 italic">"{alert.description}"</p>
              </div>
            {/each}
          </div>
        {:else}
          <p class="text-muted-foreground font-mono text-xs text-center py-12 border-2 border-dashed border-muted/20">{$t('dashboard.noAlerts') || 'ALL_SYSTEMS_OPTIMAL'}</p>
        {/if}
      </div>
    </div>

    <!-- Actions Feed -->
    <div class="brutal-card p-8 mt-8 bg-muted/5 border-dashed">
      <div class="flex items-center justify-between mb-8 border-b-2 border-foreground pb-4">
        <div class="flex items-center gap-3">
            <div class="w-3 h-3 bg-accent"></div>
            <h2 class="text-2xl font-display uppercase tracking-tighter">{($t('dashboard.actionLoop') || 'EXECUTION_TIMELINE').toUpperCase()}</h2>
        </div>
        <a href="/dashboard/actions" class="brutal-btn py-1 px-4 text-[10px] bg-void text-white">
          {($t('dashboard.manage') || 'SYNC_NOW').toUpperCase()}
        </a>
      </div>

      {#if recentActions.length > 0}
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          {#each recentActions.slice(0, 6) as action}
            <div class="p-6 brutal-card border-muted/40 shadow-none hover:border-foreground hover:shadow-brutal transition-all group">
              <div class="flex items-center justify-between mb-4">
                  <div class="text-[9px] font-black uppercase tracking-widest px-2 py-0.5 border border-foreground group-hover:bg-terminal-green group-hover:text-void transition-colors">
                    {getStatusLabel(action.status)}
                  </div>
                  <div class="w-1.5 h-1.5 bg-accent"></div>
              </div>
              <p class="text-sm font-display mb-3 uppercase tracking-tight">{action.topic}</p>
              {#if action.public_message}
                <div class="p-3 bg-muted/10 text-[10px] font-mono text-muted-foreground italic line-clamp-2">
                    {action.public_message}
                </div>
              {/if}
            </div>
          {/each}
        </div>
      {:else}
        <div class="text-center py-12">
            <p class="text-muted-foreground font-mono text-xs italic opacity-40">
              {$t('dashboard.noActions') || 'LOOP_STABLE: NO_PENDING_EXECUTIONS'}
            </p>
        </div>
      {/if}
    </div>
  {/if}
</div>

<style>
</style>
