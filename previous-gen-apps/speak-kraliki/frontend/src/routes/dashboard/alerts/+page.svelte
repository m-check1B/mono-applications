<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { accessToken, isAuthenticated } from '$stores/auth';
  import { alerts, type Alert } from '$api/client';
  import { t } from '$lib/i18n';

  let alertList = $state<Alert[]>([]);
  let loading = $state(true);
  let filter = $state<'all' | 'unread'>('all');

  onMount(async () => {
    if (!$isAuthenticated) {
      goto('/login');
      return;
    }

    await loadAlerts();
  });

  async function loadAlerts() {
    try {
      loading = true;
      const filters = filter === 'unread' ? { is_read: false } : undefined;
      alertList = await alerts.list($accessToken!, filters);
    } catch (e) {
      console.error('Failed to load alerts', e);
    } finally {
      loading = false;
    }
  }

  async function markAsRead(id: string) {
    try {
      await alerts.update(id, { is_read: true }, $accessToken!);
      await loadAlerts();
    } catch (e) {
      console.error('Failed to mark alert as read', e);
    }
  }

  async function createActionFromAlert(id: string) {
    try {
      await alerts.createAction(id, $accessToken!);
      goto('/dashboard/actions');
    } catch (e) {
      console.error('Failed to create action from alert', e);
    }
  }

  function getSeverityLabel(severity: string): string {
    const labels: Record<string, string> = {
      low: $t('alerts.severity.low'),
      medium: $t('alerts.severity.medium'),
      high: $t('alerts.severity.high'),
    };
    return labels[severity] || severity;
  }

  function getSeverityColor(severity: string): string {
    const colors: Record<string, string> = {
      low: 'border-muted-foreground text-muted-foreground',
      medium: 'border-yellow-400 text-yellow-400',
      high: 'border-system-red text-system-red',
    };
    return colors[severity] || '';
  }

  $effect(() => {
    loadAlerts();
  });
</script>

<svelte:head>
  <title>{$t('alerts.title')} - Speak by Kraliki</title>
</svelte:head>

<div class="container mx-auto p-6">
  <div class="flex items-center justify-between mb-8">
    <div>
      <a href="/dashboard" class="text-sm text-muted-foreground hover:text-foreground mb-2 inline-block">
        &lt; {$t('nav.dashboard')}
      </a>
      <h1 class="text-3xl">{$t('alerts.title').toUpperCase()}</h1>
    </div>
    <div class="flex gap-2">
      <button
        onclick={() => (filter = 'all')}
        class="brutal-btn text-sm {filter === 'all' ? 'brutal-btn-primary' : ''}"
      >
        {$t('common.all').toUpperCase()}
      </button>
      <button
        onclick={() => (filter = 'unread')}
        class="brutal-btn text-sm {filter === 'unread' ? 'brutal-btn-primary' : ''}"
      >
        {$t('alerts.unread').toUpperCase()}
      </button>
    </div>
  </div>

  {#if loading}
    <div class="text-center py-12">
      <span class="animate-pulse">{$t('common.loading').toUpperCase()}</span>
    </div>
  {:else if alertList.length === 0}
    <div class="brutal-card p-12 text-center">
      <p class="text-muted-foreground">{$t('alerts.noAlerts')}</p>
    </div>
  {:else}
    <div class="space-y-4">
      {#each alertList as alert}
        <div class="brutal-card p-6 {alert.is_read ? 'opacity-60' : ''}">
          <div class="flex items-start justify-between">
            <div class="flex-1">
              <div class="flex items-center gap-3 mb-2">
                <span class="text-xs px-2 py-1 border-2 {getSeverityColor(alert.severity)}">
                  {getSeverityLabel(alert.severity).toUpperCase()}
                </span>
                <span class="text-sm text-muted-foreground">
                  {alert.type.replace(/_/g, ' ').toUpperCase()}
                </span>
                {#if alert.department_name}
                  <span class="text-sm text-cyan-data">
                    {alert.department_name}
                  </span>
                {/if}
                <span class="text-xs text-muted-foreground ml-auto">
                  {new Date(alert.created_at).toLocaleDateString()}
                </span>
              </div>
              <p class="text-foreground">{alert.description}</p>
            </div>
          </div>

          <div class="flex gap-2 mt-4 pt-4 border-t border-foreground/20">
            {#if !alert.is_read}
              <button onclick={() => markAsRead(alert.id)} class="brutal-btn text-sm">
                {$t('alerts.markRead').toUpperCase()}
              </button>
            {/if}
            {#if !alert.is_resolved}
              <button onclick={() => createActionFromAlert(alert.id)} class="brutal-btn brutal-btn-primary text-sm">
                {$t('alerts.createAction').toUpperCase()}
              </button>
            {/if}
          </div>
        </div>
      {/each}
    </div>
  {/if}
</div>

<style>
</style>
