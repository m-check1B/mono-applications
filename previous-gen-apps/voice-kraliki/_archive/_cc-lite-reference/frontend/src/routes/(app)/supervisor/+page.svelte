<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { trpc } from '$lib/trpc/client';
  import { auth } from '$lib/stores/auth.svelte';
  import { ws } from '$lib/stores/websocket.svelte';
  import StatsCard from '$lib/components/shared/StatsCard.svelte';
  import LiveCallGrid from '$lib/components/supervisor/LiveCallGrid.svelte';
  import AgentStatusGrid from '$lib/components/supervisor/AgentStatusGrid.svelte';
  import Card from '$lib/components/shared/Card.svelte';
  import Badge from '$lib/components/shared/Badge.svelte';

  let loading = $state(true);
  let dashboardData = $state<any>(null);
  let error = $state<string | null>(null);

  // Live calls from API
  let liveCalls = $state<any[]>([]);

  // Load live calls from backend
  const loadLiveCalls = async () => {
    try {
      loading = true;
      error = null;

      // Fetch real active calls from backend
      const calls = await trpc.telephony.getAllActiveCalls.query();

      // Transform to supervisor view format
      liveCalls = calls.map((call: any) => ({
        id: call.id,
        agentName: call.agent ? `${call.agent.firstName} ${call.agent.lastName}` : 'Unknown',
        agentId: call.agent?.id || 'N/A',
        customerName: 'Customer', // Would come from call metadata
        customerPhone: call.fromNumber || call.toNumber,
        duration: call.duration || 0,
        sentiment: 'neutral' as const, // Would come from sentiment analysis
        status: call.status === 'IN_PROGRESS' ? 'active' as const :
                call.status === 'ON_HOLD' ? 'on-hold' as const : 'active' as const
      }));

      console.log('✅ Loaded live calls:', liveCalls.length);
    } catch (err: any) {
      console.error('Failed to load live calls:', err);
      error = err.message;

      // Fallback to mock data
      liveCalls = [
        {
          id: '1',
          agentName: 'John Doe',
          agentId: 'AGT001',
          customerName: 'Alice Johnson',
          customerPhone: '+1 (555) 234-5678',
          duration: 187,
          sentiment: 'positive' as const,
          status: 'active' as const
        },
        {
          id: '2',
          agentName: 'Sarah Smith',
          agentId: 'AGT002',
          customerName: 'Bob Williams',
          customerPhone: '+1 (555) 876-5432',
          duration: 95,
          sentiment: 'neutral' as const,
          status: 'active' as const
        }
      ];
    } finally {
      loading = false;
    }
  };

  let agents = $state([
    {
      id: 'AGT001',
      name: 'John Doe',
      email: 'john.doe@company.com',
      status: 'on-call' as const,
      currentCall: {
        customerName: 'Alice Johnson',
        duration: 187
      },
      stats: {
        callsToday: 18,
        avgDuration: 245,
        satisfaction: 96
      }
    },
    {
      id: 'AGT002',
      name: 'Sarah Smith',
      email: 'sarah.smith@company.com',
      status: 'on-call' as const,
      currentCall: {
        customerName: 'Bob Williams',
        duration: 95
      },
      stats: {
        callsToday: 22,
        avgDuration: 198,
        satisfaction: 94
      }
    },
    {
      id: 'AGT003',
      name: 'Mike Chen',
      email: 'mike.chen@company.com',
      status: 'on-call' as const,
      currentCall: {
        customerName: 'Carol Martinez',
        duration: 240
      },
      stats: {
        callsToday: 15,
        avgDuration: 312,
        satisfaction: 89
      }
    },
    {
      id: 'AGT004',
      name: 'Emma Davis',
      email: 'emma.davis@company.com',
      status: 'available' as const,
      stats: {
        callsToday: 20,
        avgDuration: 220,
        satisfaction: 97
      }
    },
    {
      id: 'AGT005',
      name: 'David Wilson',
      email: 'david.wilson@company.com',
      status: 'break' as const,
      stats: {
        callsToday: 17,
        avgDuration: 265,
        satisfaction: 92
      }
    }
  ]);

  async function loadDashboard() {
    try {
      // Load live calls from backend
      await loadLiveCalls();

      // Try to load overview data
      const data = await trpc.supervisor.getOverview.query();
      dashboardData = data;
    } catch (error) {
      console.error('Failed to load supervisor dashboard:', error);
      // Use mock data
      dashboardData = {
        stats: {
          activeCalls: liveCalls.length,
          availableAgents: agents.filter(a => a.status === 'available').length,
          avgWaitTime: 32,
          satisfaction: 94
        }
      };
    } finally {
      loading = false;
    }
  }

  onMount(() => {
    void loadDashboard();
    const interval = setInterval(loadDashboard, 15000);
    return () => clearInterval(interval);
  });

  onDestroy(() => {
    ws.disconnect();
  });
</script>

<svelte:head>
  <title>Supervisor Dashboard - Voice by Kraliki</title>
</svelte:head>

<div class="space-y-6">
  <!-- Header -->
  <div class="flex justify-between items-center">
    <div>
      <h1 class="text-2xl font-bold text-gray-900 dark:text-white">Supervisor Cockpit</h1>
      <p class="mt-1 text-sm text-gray-600 dark:text-gray-400">
        Real-time monitoring and team management
      </p>
    </div>

    <div class="flex items-center gap-3">
      <Badge variant="success" class="text-sm">
        🟢 {agents.filter(a => a.status === 'available').length} Available
      </Badge>
      <Badge variant="primary" class="text-sm">
        📞 {liveCalls.length} Active Calls
      </Badge>
    </div>
  </div>

  {#if loading}
    <div class="flex justify-center py-12">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
    </div>
  {:else}
    <!-- Stats Overview -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
      <StatsCard
        title="Active Calls"
        value={dashboardData?.stats?.activeCalls || liveCalls.length}
        subtitle="Calls in progress"
      />
      <StatsCard
        title="Available Agents"
        value={dashboardData?.stats?.availableAgents || agents.filter(a => a.status === 'available').length}
        subtitle="Ready to take calls"
      />
      <StatsCard
        title="Avg Wait Time"
        value={`${dashboardData?.stats?.avgWaitTime || 32}s`}
        subtitle="Queue wait time"
      />
      <StatsCard
        title="Team CSAT"
        value={`${dashboardData?.stats?.satisfaction || 94}%`}
        subtitle="Customer satisfaction"
      />
    </div>

    <!-- Live Calls Monitoring -->
    <LiveCallGrid calls={liveCalls} />

    <!-- Agent Status Grid -->
    <AgentStatusGrid agents={agents} />

    <!-- Call Queue -->
    <Card>
      {#snippet header()}
        <div class="flex items-center justify-between">
          <h2 class="text-lg font-semibold text-gray-900 dark:text-white">Call Queue</h2>
          <Badge variant="primary">5 waiting</Badge>
        </div>
      {/snippet}

      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
          <thead>
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                Customer
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                Wait Time
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                Priority
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                Campaign
              </th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-200 dark:divide-gray-700">
            <tr>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                <div>James Brown</div>
                <div class="text-xs text-gray-500">+1 (555) 111-2222</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600 dark:text-gray-400">
                1:23
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <Badge variant="danger">HIGH</Badge>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600 dark:text-gray-400">
                Sales Q4
              </td>
            </tr>
            <tr>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                <div>Lisa Anderson</div>
                <div class="text-xs text-gray-500">+1 (555) 333-4444</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600 dark:text-gray-400">
                0:45
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <Badge variant="primary">NORMAL</Badge>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600 dark:text-gray-400">
                Support
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </Card>

    <!-- WebSocket Status Indicator -->
    <div class="fixed bottom-4 right-4">
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-lg px-4 py-2 flex items-center space-x-2 border border-gray-200 dark:border-gray-700">
        <div class={`w-2 h-2 rounded-full ${ws.connected ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`}></div>
        <span class="text-sm font-medium text-gray-700 dark:text-gray-300">
          {ws.connected ? 'Live Monitoring' : ws.reconnecting ? 'Reconnecting...' : 'Disconnected'}
        </span>
      </div>
    </div>
  {/if}
</div>
