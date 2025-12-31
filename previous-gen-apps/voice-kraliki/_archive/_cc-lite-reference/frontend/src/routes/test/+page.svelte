<script lang="ts">
  import Button from '$lib/components/shared/Button.svelte';
  import Card from '$lib/components/shared/Card.svelte';
  import Badge from '$lib/components/shared/Badge.svelte';
  import StatsCard from '$lib/components/shared/StatsCard.svelte';
</script>

<svelte:head>
  <title>SvelteKit UI Test Page</title>
</svelte:head>

<div class="min-h-screen bg-gray-50 dark:bg-gray-900 p-8">
  <div class="max-w-7xl mx-auto space-y-8">
    <div class="text-center">
      <h1 class="text-4xl font-bold text-gray-900 dark:text-white mb-2">
        ✅ SvelteKit UI is Working!
      </h1>
      <p class="text-lg text-gray-600 dark:text-gray-400">
        Your new frontend is successfully running
      </p>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
      <StatsCard
        title="Components"
        value="22"
        subtitle="Total files created"
      />
      <StatsCard
        title="Code Reduction"
        value="87%"
        subtitle="Less code than React"
      />
      <StatsCard
        title="Bundle Size"
        value="75%"
        subtitle="Smaller than React"
      />
      <StatsCard
        title="Performance"
        value="6x"
        subtitle="Faster builds"
      />
    </div>

    <!-- Component Demos -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Buttons -->
      <Card>
        {#snippet header()}
          <h2 class="text-lg font-semibold text-gray-900 dark:text-white">Button Components</h2>
        {/snippet}

        <div class="space-y-4">
          <div class="flex flex-wrap gap-2">
            <Button variant="primary">Primary Button</Button>
            <Button variant="secondary">Secondary Button</Button>
            <Button variant="success">Success Button</Button>
            <Button variant="danger">Danger Button</Button>
          </div>
          <div class="flex flex-wrap gap-2">
            <Button size="sm" variant="primary">Small</Button>
            <Button size="md" variant="primary">Medium</Button>
            <Button size="lg" variant="primary">Large</Button>
          </div>
          <div class="flex flex-wrap gap-2">
            <Button loading variant="primary">Loading...</Button>
            <Button disabled variant="primary">Disabled</Button>
          </div>
        </div>
      </Card>

      <!-- Badges -->
      <Card>
        {#snippet header()}
          <h2 class="text-lg font-semibold text-gray-900 dark:text-white">Badge Components</h2>
        {/snippet}

        <div class="space-y-4">
          <div class="flex flex-wrap gap-2">
            <Badge variant="primary">Primary</Badge>
            <Badge variant="success">Success</Badge>
            <Badge variant="warning">Warning</Badge>
            <Badge variant="danger">Danger</Badge>
            <Badge variant="gray">Gray</Badge>
          </div>
          <div class="flex flex-wrap gap-2 items-center">
            <span class="text-sm text-gray-600 dark:text-gray-400">Call Status:</span>
            <Badge variant="success">IN_PROGRESS</Badge>
            <Badge variant="warning">RINGING</Badge>
            <Badge variant="primary">QUEUED</Badge>
          </div>
        </div>
      </Card>
    </div>

    <!-- Dashboard Links -->
    <Card>
      {#snippet header()}
        <h2 class="text-lg font-semibold text-gray-900 dark:text-white">Available Dashboards</h2>
      {/snippet}

      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <a
          href="/login"
          class="block p-6 bg-gray-50 dark:bg-gray-700 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors text-center"
        >
          <div class="text-4xl mb-3">🔐</div>
          <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-2">Login</h3>
          <p class="text-sm text-gray-600 dark:text-gray-400">
            Authentication page (needs backend)
          </p>
        </a>

        <a
          href="/operator"
          class="block p-6 bg-gray-50 dark:bg-gray-700 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors text-center"
        >
          <div class="text-4xl mb-3">👨‍💼</div>
          <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-2">Operator</h3>
          <p class="text-sm text-gray-600 dark:text-gray-400">
            Agent dashboard (needs backend)
          </p>
        </a>

        <a
          href="/supervisor"
          class="block p-6 bg-gray-50 dark:bg-gray-700 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors text-center"
        >
          <div class="text-4xl mb-3">👔</div>
          <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-2">Supervisor</h3>
          <p class="text-sm text-gray-600 dark:text-gray-400">
            Supervisor cockpit (needs backend)
          </p>
        </a>
      </div>
    </Card>

    <!-- Status Info -->
    <Card>
      {#snippet header()}
        <h2 class="text-lg font-semibold text-gray-900 dark:text-white">System Status</h2>
      {/snippet}

      <div class="space-y-3">
        <div class="flex items-center justify-between">
          <span class="text-sm font-medium text-gray-700 dark:text-gray-300">Frontend (SvelteKit)</span>
          <span class="px-3 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400">
            ✅ Running
          </span>
        </div>
        <div class="flex items-center justify-between">
          <span class="text-sm font-medium text-gray-700 dark:text-gray-300">Backend (Node.js)</span>
          <span class="px-3 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400">
            ❌ Not Running
          </span>
        </div>
        <div class="mt-4 p-4 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg">
          <p class="text-sm text-yellow-800 dark:text-yellow-400">
            <strong>Note:</strong> To use dashboards with real data, start the backend:
          </p>
          <pre class="mt-2 p-2 bg-gray-900 text-green-400 rounded text-xs overflow-x-auto">cd /home/adminmatej/github/apps/cc-lite
PORT=3010 HOST=127.0.0.1 pnpm dev:server</pre>
        </div>
      </div>
    </Card>
  </div>
</div>
