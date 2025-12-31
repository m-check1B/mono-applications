<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { accessToken, isAuthenticated } from '$stores/auth';
  import { actions, type Action } from '$api/client';
  import { t } from '$lib/i18n';

  let actionList = $state<Action[]>([]);
  let loading = $state(true);
  let statusFilter = $state<string>('all');
  let showCreateModal = $state(false);

  // New action form
  let newAction = $state({
    topic: '',
    description: '',
    priority: 'medium' as const,
    public_message: '',
    visible_to_employees: true,
  });

  onMount(async () => {
    if (!$isAuthenticated) {
      goto('/login');
      return;
    }

    await loadActions();
  });

  async function loadActions() {
    try {
      loading = true;
      const status = statusFilter === 'all' ? undefined : statusFilter;
      actionList = await actions.list($accessToken!, status);
    } catch (e) {
      console.error('Failed to load actions', e);
    } finally {
      loading = false;
    }
  }

  async function createAction() {
    try {
      await actions.create(newAction, $accessToken!);
      showCreateModal = false;
      newAction = {
        topic: '',
        description: '',
        priority: 'medium',
        public_message: '',
        visible_to_employees: true,
      };
      await loadActions();
    } catch (e) {
      console.error('Failed to create action', e);
    }
  }

  async function updateStatus(id: string, status: 'new' | 'heard' | 'in_progress' | 'resolved') {
    try {
      await actions.update(id, { status }, $accessToken!);
      await loadActions();
    } catch (e) {
      console.error('Failed to update action', e);
    }
  }

  function getStatusLabel(status: string): string {
    const labels: Record<string, string> = {
      new: $t('status.new'),
      heard: $t('status.heard'),
      in_progress: $t('status.inProgress'),
      resolved: $t('status.resolved'),
    };
    return labels[status] || status;
  }

  function getStatusColor(status: string): string {
    const colors: Record<string, string> = {
      new: 'border-cyan-data text-cyan-data',
      heard: 'border-terminal-green text-terminal-green',
      in_progress: 'border-yellow-400 text-yellow-400',
      resolved: 'border-gray-500 text-gray-500',
    };
    return colors[status] || '';
  }

  function getPriorityLabel(priority: string): string {
    const labels: Record<string, string> = {
      low: $t('alerts.severity.low'),
      medium: $t('alerts.severity.medium'),
      high: $t('alerts.severity.high'),
    };
    return labels[priority] || priority;
  }

  $effect(() => {
    loadActions();
  });
</script>

<svelte:head>
  <title>{$t('actions.title')} - Speak by Kraliki</title>
</svelte:head>

<div class="container mx-auto p-6">
  <div class="flex items-center justify-between mb-8">
    <div>
      <a href="/dashboard" class="text-sm text-muted-foreground hover:text-foreground mb-2 inline-block">
        &lt; {$t('nav.dashboard')}
      </a>
      <h1 class="text-3xl">{$t('actions.title').toUpperCase()}</h1>
      <p class="text-muted-foreground text-sm mt-1">Action Loop - {$t('actionLoop.title')}</p>
    </div>
    <button onclick={() => (showCreateModal = true)} class="brutal-btn brutal-btn-primary">
      {$t('actions.create').toUpperCase()}
    </button>
  </div>

  <!-- Status Tabs -->
  <div class="flex gap-2 mb-6 flex-wrap">
    {#each ['all', 'new', 'heard', 'in_progress', 'resolved'] as status}
      <button
        onclick={() => (statusFilter = status)}
        class="brutal-btn text-sm {statusFilter === status ? 'brutal-btn-primary' : ''}"
      >
        {status === 'all' ? $t('common.all').toUpperCase() : getStatusLabel(status).toUpperCase()}
      </button>
    {/each}
  </div>

  {#if loading}
    <div class="text-center py-12">
      <span class="animate-pulse">{$t('common.loading').toUpperCase()}</span>
    </div>
  {:else if actionList.length === 0}
    <div class="brutal-card p-12 text-center">
      <p class="text-muted-foreground mb-4">{$t('actions.noActions')}</p>
      <button onclick={() => (showCreateModal = true)} class="brutal-btn brutal-btn-primary">
        {$t('actions.create').toUpperCase()}
      </button>
    </div>
  {:else}
    <div class="grid gap-4">
      {#each actionList as action}
        <div class="brutal-card p-6">
          <div class="flex items-start justify-between">
            <div class="flex-1">
              <div class="flex items-center gap-3 mb-2">
                <span class="text-xs px-2 py-1 border-2 {getStatusColor(action.status)}">
                  {getStatusLabel(action.status).toUpperCase()}
                </span>
                <span class="text-xs text-muted-foreground">
                  {getPriorityLabel(action.priority)} {$t('actions.priority').toLowerCase()}
                </span>
                {#if action.visible_to_employees}
                  <span class="text-xs text-terminal-green">
                    {$t('actions.visibleToEmployees')}
                  </span>
                {/if}
              </div>
              <h3 class="text-lg font-bold mb-2">{action.topic}</h3>
              {#if action.description}
                <p class="text-muted-foreground text-sm mb-2">{action.description}</p>
              {/if}
              {#if action.public_message}
                <div class="mt-3 p-3 bg-void border-2 border-terminal-green/30">
                  <span class="text-xs text-terminal-green block mb-1">{$t('actions.publicMessage').toUpperCase()}</span>
                  <p class="text-sm">{action.public_message}</p>
                </div>
              {/if}
              <div class="flex gap-4 mt-3 text-xs text-muted-foreground">
                <span>{new Date(action.created_at).toLocaleDateString()}</span>
                {#if action.resolved_at}
                  <span>{$t('status.resolved')}: {new Date(action.resolved_at).toLocaleDateString()}</span>
                {/if}
              </div>
            </div>
          </div>

          <!-- Action Buttons -->
          {#if action.status !== 'resolved'}
            <div class="flex gap-2 mt-4 pt-4 border-t border-foreground/20">
              {#if action.status === 'new'}
                <button onclick={() => updateStatus(action.id, 'heard')} class="brutal-btn text-sm">
                  {$t('actions.markHeard').toUpperCase()}
                </button>
              {/if}
              {#if action.status === 'new' || action.status === 'heard'}
                <button onclick={() => updateStatus(action.id, 'in_progress')} class="brutal-btn text-sm">
                  {$t('actions.markInProgress').toUpperCase()}
                </button>
              {/if}
              <button onclick={() => updateStatus(action.id, 'resolved')} class="brutal-btn brutal-btn-primary text-sm">
                {$t('actions.markResolved').toUpperCase()}
              </button>
            </div>
          {/if}
        </div>
      {/each}
    </div>
  {/if}
</div>

<!-- Create Action Modal -->
{#if showCreateModal}
  <div class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
    <div class="brutal-card max-w-lg w-full max-h-[90vh] overflow-y-auto p-6">
      <div class="flex items-center justify-between mb-6">
        <h2 class="text-xl">{$t('actions.create').toUpperCase()}</h2>
        <button onclick={() => (showCreateModal = false)} class="text-2xl hover:text-terminal-green">
          X
        </button>
      </div>

      <form onsubmit={(e) => { e.preventDefault(); createAction(); }}>
        <div class="space-y-4">
          <div>
            <label for="action-topic" class="block text-sm mb-1">{$t('actions.topic').toUpperCase()}</label>
            <input id="action-topic" type="text" bind:value={newAction.topic} class="brutal-input w-full" required />
          </div>

          <div>
            <label for="action-description" class="block text-sm mb-1">{$t('surveys.description').toUpperCase()}</label>
            <textarea id="action-description" bind:value={newAction.description} class="brutal-input w-full" rows="2"></textarea>
          </div>

          <div>
            <label for="action-priority" class="block text-sm mb-1">{$t('actions.priority').toUpperCase()}</label>
            <select id="action-priority" bind:value={newAction.priority} class="brutal-input w-full">
              <option value="low">{$t('alerts.severity.low')}</option>
              <option value="medium">{$t('alerts.severity.medium')}</option>
              <option value="high">{$t('alerts.severity.high')}</option>
            </select>
          </div>

          <div>
            <label for="action-public-message" class="block text-sm mb-1">{$t('actions.publicMessage').toUpperCase()}</label>
            <textarea
              id="action-public-message"
              bind:value={newAction.public_message}
              class="brutal-input w-full"
              rows="2"
              placeholder="Message visible to employees..."
            ></textarea>
          </div>

          <div class="flex items-center gap-2">
            <input type="checkbox" bind:checked={newAction.visible_to_employees} id="visible" />
            <label for="visible" class="text-sm">{$t('actions.visibleToEmployees')}</label>
          </div>
        </div>

        <div class="flex gap-3 mt-6 pt-6 border-t-2 border-foreground/20">
          <button type="button" onclick={() => (showCreateModal = false)} class="brutal-btn flex-1">
            {$t('common.cancel').toUpperCase()}
          </button>
          <button type="submit" class="brutal-btn brutal-btn-primary flex-1">
            {$t('common.create').toUpperCase()}
          </button>
        </div>
      </form>
    </div>
  </div>
{/if}

<style>
</style>
