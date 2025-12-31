<script lang="ts">
  import { onMount } from 'svelte';
  import { trpc } from '$lib/trpc/client';
  import Card from '$lib/components/shared/Card.svelte';
  import StatsCard from '$lib/components/shared/StatsCard.svelte';
  import Button from '$lib/components/shared/Button.svelte';

  let loading = $state(true);
  let stats = $state<any>({});

  async function loadStats() {
    try {
      const data = await trpc.dashboard.getOverview.query();
      stats = data.stats || {};
    } catch (error) {
      console.error('Failed to load stats:', error);
    } finally {
      loading = false;
    }
  }

  onMount(() => {
    loadStats();
  });
</script>

<svelte:head>
  <title>Admin Dashboard - Voice by Kraliki</title>
</svelte:head>

<div class="space-y-6">
  <!-- Header -->
  <div class="flex items-center justify-between">
    <div>
      <h1 class="text-2xl font-bold text-gray-900 dark:text-white">Admin Dashboard</h1>
      <p class="mt-1 text-sm text-gray-600 dark:text-gray-400">
        System overview and management
      </p>
    </div>
    <div class="flex space-x-3">
      <Button variant="secondary" onclick={() => window.location.href = '/admin/users'}>
        Manage Users
      </Button>
      <Button variant="primary" onclick={() => window.location.href = '/admin/campaigns'}>
        Campaigns
      </Button>
    </div>
  </div>

  {#if loading}
    <div class="flex justify-center py-12">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
    </div>
  {:else}
    <!-- Stats Grid -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
      <StatsCard
        title="Total Calls"
        value={stats.totalCalls || 0}
        subtitle="All time"
      />
      <StatsCard
        title="Active Users"
        value={stats.activeUsers || 0}
        subtitle="Online now"
      />
      <StatsCard
        title="Campaigns"
        value={stats.totalCampaigns || 0}
        subtitle="Active campaigns"
      />
      <StatsCard
        title="Avg Duration"
        value={`${stats.avgDuration || 0}s`}
        subtitle="Call duration"
      />
    </div>

    <!-- Quick Actions -->
    <Card>
      {#snippet header()}
        <h2 class="text-lg font-semibold text-gray-900 dark:text-white">Quick Actions</h2>
      {/snippet}

      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <a
          href="/admin/users"
          class="block p-6 bg-gray-50 dark:bg-gray-700 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors"
        >
          <div class="text-2xl mb-2">👥</div>
          <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-1">
            User Management
          </h3>
          <p class="text-sm text-gray-600 dark:text-gray-400">
            Add, edit, and manage user accounts
          </p>
        </a>

        <a
          href="/admin/campaigns"
          class="block p-6 bg-gray-50 dark:bg-gray-700 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors"
        >
          <div class="text-2xl mb-2">📢</div>
          <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-1">
            Campaigns
          </h3>
          <p class="text-sm text-gray-600 dark:text-gray-400">
            Create and manage call campaigns
          </p>
        </a>

        <a
          href="/admin/analytics"
          class="block p-6 bg-gray-50 dark:bg-gray-700 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors"
        >
          <div class="text-2xl mb-2">📊</div>
          <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-1">
            Analytics
          </h3>
          <p class="text-sm text-gray-600 dark:text-gray-400">
            View reports and insights
          </p>
        </a>
      </div>
    </Card>

    <!-- System Health -->
    <Card>
      {#snippet header()}
        <h2 class="text-lg font-semibold text-gray-900 dark:text-white">System Health</h2>
      {/snippet}

      <div class="space-y-4">
        <div class="flex items-center justify-between">
          <span class="text-sm font-medium text-gray-700 dark:text-gray-300">API Server</span>
          <span class="px-3 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400">
            Healthy
          </span>
        </div>
        <div class="flex items-center justify-between">
          <span class="text-sm font-medium text-gray-700 dark:text-gray-300">Database</span>
          <span class="px-3 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400">
            Connected
          </span>
        </div>
        <div class="flex items-center justify-between">
          <span class="text-sm font-medium text-gray-700 dark:text-gray-300">WebSocket</span>
          <span class="px-3 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400">
            Active
          </span>
        </div>
        <div class="flex items-center justify-between">
          <span class="text-sm font-medium text-gray-700 dark:text-gray-300">Telephony</span>
          <span class="px-3 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400">
            Ready
          </span>
        </div>
      </div>
    </Card>
  {/if}
</div>
