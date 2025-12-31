<script lang="ts">
  import { onMount } from 'svelte';

  interface GenomeEntry {
    name: string;
    cli: string;
    spawns_today: number;
    points_earned: number;
    decisions: number;
    last_active: string | null;
    description?: string;
    enabled: boolean;
  }

  interface TemplatePack {
    template: string;
    description?: string;
    active_roles: string[];
    muted_roles: string[];
    active_genome_count: number;
    muted_genome_count: number;
    missing_roles: string[];
  }

  interface GenomeFile {
    name: string;
    cli: string;
    path: string;
    size_kb: number;
  }

  interface GenomeData {
    genomes: GenomeEntry[];
    files: GenomeFile[];
    by_cli: Record<string, { genomes: number; spawns: number; points: number }>;
    total_genomes: number;
    active_today: number;
    template_packs?: TemplatePack[];
  }

  let data = $state<GenomeData | null>(null);
  let loading = $state(true);
  let error = $state<string | null>(null);
  let selectedCli = $state('all');
  let sortBy = $state<'name' | 'spawns' | 'points'>('spawns');
  let selectedGenome = $state<GenomeEntry | null>(null);
  let genomeContent = $state<string | null>(null);
  let loadingContent = $state(false);

  async function loadGenomes() {
    loading = true;
    error = null;
    try {
      const response = await fetch('/api/genomes');
      if (!response.ok) throw new Error('Failed to load genomes');
      data = await response.json();
    } catch (e) {
      error = e instanceof Error ? e.message : 'Failed to load genomes';
    } finally {
      loading = false;
    }
  }

  let toggleLoading = $state<string | null>(null);

  async function loadGenomeContent(genome: GenomeEntry) {
    selectedGenome = genome;
    loadingContent = true;
    genomeContent = null;
    try {
      const response = await fetch(`/api/genomes/${genome.name}`);
      if (!response.ok) throw new Error('Failed to load genome');
      const result = await response.json();
      genomeContent = result.content;
    } catch (e) {
      genomeContent = `Error loading genome: ${e instanceof Error ? e.message : 'Unknown error'}`;
    } finally {
      loadingContent = false;
    }
  }

  async function toggleGenome(genome: GenomeEntry, event: Event) {
    event.stopPropagation();
    toggleLoading = genome.name;
    try {
      const response = await fetch('/api/genomes', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: genome.name, enabled: !genome.enabled })
      });
      if (!response.ok) throw new Error('Failed to toggle genome');
      // Reload genomes to get updated state
      await loadGenomes();
    } catch (e) {
      console.error('Toggle failed:', e);
    } finally {
      toggleLoading = null;
    }
  }

  function getCliColor(cli: string): string {
    const colors: Record<string, string> = {
      claude: '#33ff00',
      opencode: '#00d4ff',
      codex: '#9d4edd',
      gemini: '#ff9500',
      grok: '#ff4444'
    };
    return colors[cli] || '#6b7280';
  }

  function getFilteredGenomes(): GenomeEntry[] {
    if (!data) return [];
    let genomes = [...data.genomes];

    if (selectedCli !== 'all') {
      genomes = genomes.filter(g => g.cli === selectedCli);
    }

    // Sort
    genomes.sort((a, b) => {
      if (sortBy === 'name') return a.name.localeCompare(b.name);
      if (sortBy === 'spawns') return b.spawns_today - a.spawns_today;
      if (sortBy === 'points') return b.points_earned - a.points_earned;
      return 0;
    });

    return genomes;
  }

  function formatRole(name: string, cli: string): string {
    return name.replace(cli + '_', '').replace(/_/g, ' ').toUpperCase();
  }

  function formatRoleList(roles: string[], limit = 6): string {
    if (!roles || roles.length === 0) return 'NONE';
    const formatted = roles.map((role) => role.replace(/_/g, ' ').toUpperCase());
    if (formatted.length <= limit) return formatted.join(', ');
    return `${formatted.slice(0, limit).join(', ')} +${formatted.length - limit} more`;
  }

  function formatLastActive(timestamp: string | null): string {
    if (!timestamp) return 'Never';
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);

    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    return `${diffDays}d ago`;
  }

  onMount(() => {
    loadGenomes();
  });

  let filteredGenomes = $derived(getFilteredGenomes());
  let cliOptions = $derived(data ? ['all', ...Object.keys(data.by_cli)] : ['all']);
</script>

<div class="page">
  <div class="page-header">
    <h2 class="glitch">Genome Registry // Template Packs</h2>
    <div class="controls">
      <select bind:value={selectedCli} class="filter-select">
        <option value="all">ALL CLIs</option>
        {#if data}
          {#each Object.keys(data.by_cli) as cli}
            <option value={cli}>{cli.toUpperCase()}</option>
          {/each}
        {/if}
      </select>
      <select bind:value={sortBy} class="filter-select">
        <option value="spawns">BY SPAWNS</option>
        <option value="points">BY POINTS</option>
        <option value="name">BY NAME</option>
      </select>
      <button class="brutal-btn" onclick={loadGenomes}>
        REFRESH
      </button>
    </div>
  </div>

  {#if loading && !data}
    <div class="loading-state">
      <span class="loading-text">LOADING_GENOME_REGISTRY...</span>
    </div>
  {:else if error}
    <div class="error-state">
      <span class="error-text">ERROR: {error}</span>
    </div>
  {:else if data}
    <!-- Stats Overview -->
    <div class="stats-grid">
      <div class="stat-card">
        <span class="stat-value">{data.total_genomes}</span>
        <span class="stat-label">TOTAL GENOMES</span>
      </div>
      <div class="stat-card">
        <span class="stat-value green">{data.active_today}</span>
        <span class="stat-label">ACTIVE TODAY</span>
      </div>
      {#each Object.entries(data.by_cli).sort((a, b) => b[1].spawns - a[1].spawns) as [cli, stats]}
        <div class="stat-card" style="border-color: {getCliColor(cli)}">
          <span class="stat-value" style="color: {getCliColor(cli)}">{stats.spawns}</span>
          <span class="stat-label">{cli.toUpperCase()} SPAWNS</span>
        </div>
      {/each}
    </div>

    <!-- CLI Summary Bars -->
    <div class="cli-summary card">
      <h3>CLI DISTRIBUTION</h3>
      <div class="cli-bars">
        {#each Object.entries(data.by_cli).sort((a, b) => b[1].genomes - a[1].genomes) as [cli, stats]}
          {@const maxGenomes = Math.max(...Object.values(data.by_cli).map(s => s.genomes))}
          <div class="cli-bar">
            <span class="cli-name" style="color: {getCliColor(cli)}">{cli.toUpperCase()}</span>
            <div class="bar-container">
              <div
                class="bar-fill"
                style="width: {(stats.genomes / maxGenomes) * 100}%; background: {getCliColor(cli)}"
              ></div>
            </div>
            <span class="cli-stats">{stats.genomes} genomes / {stats.spawns} spawns / {stats.points} pts</span>
          </div>
        {/each}
      </div>
    </div>

    {#if data.template_packs && data.template_packs.length > 0}
      <div class="template-packs card">
        <h3>TEMPLATE GENOME PACKS</h3>
        <p class="hint">
          Templates activate role packs; genomes outside the pack are muted for that template. Global toggles still apply.
        </p>
        <div class="template-pack-grid">
          {#each data.template_packs as pack}
            <div class="template-pack">
              <div class="template-pack-header">
                <span class="template-name">{pack.template.toUpperCase()}</span>
                <span class="template-count">{pack.active_genome_count} active / {pack.muted_genome_count} muted</span>
              </div>
              {#if pack.description}
                <div class="template-desc">{pack.description}</div>
              {/if}
              <div class="role-row">
                <span class="role-label">ACTIVE ROLES</span>
                <span class="role-list">{formatRoleList(pack.active_roles)}</span>
              </div>
              <div class="role-row muted">
                <span class="role-label">MUTED ROLES</span>
                <span class="role-list">{formatRoleList(pack.muted_roles)}</span>
              </div>
              {#if pack.missing_roles.length > 0}
                <div class="role-row missing">
                  <span class="role-label">MISSING ROLES</span>
                  <span class="role-list">{formatRoleList(pack.missing_roles, 8)}</span>
                </div>
              {/if}
            </div>
          {/each}
        </div>
      </div>
    {/if}

    <div class="content-grid">
      <!-- Genome List -->
      <div class="genome-list card">
        <h3>GENOMES ({filteredGenomes.length})</h3>
        <div class="genome-items">
          {#each filteredGenomes as genome}
            <div
              class="genome-item"
              class:selected={selectedGenome?.name === genome.name}
              class:active={genome.spawns_today > 0 || genome.points_earned > 0}
              class:disabled={!genome.enabled}
              onclick={() => loadGenomeContent(genome)}
              role="button"
              tabindex="0"
              onkeydown={(e) => e.key === 'Enter' && loadGenomeContent(genome)}
            >
              <div class="genome-header">
                <span class="genome-cli" style="color: {getCliColor(genome.cli)}">{genome.cli.toUpperCase()}</span>
                <span class="genome-role">{formatRole(genome.name, genome.cli)}</span>
                <button
                  class="toggle-btn"
                  class:enabled={genome.enabled}
                  class:loading={toggleLoading === genome.name}
                  onclick={(e) => toggleGenome(genome, e)}
                  title={genome.enabled ? 'Click to mute genome globally' : 'Click to activate genome globally'}
                >
                  {#if toggleLoading === genome.name}
                    ...
                  {:else}
                    {genome.enabled ? 'ACTIVE' : 'MUTED'}
                  {/if}
                </button>
              </div>
              <div class="genome-metrics">
                <span class="metric" class:highlight={genome.spawns_today > 0}>
                  <span class="metric-value">{genome.spawns_today}</span>
                  <span class="metric-label">SPAWNS</span>
                </span>
                <span class="metric" class:highlight={genome.points_earned > 0}>
                  <span class="metric-value">{genome.points_earned}</span>
                  <span class="metric-label">POINTS</span>
                </span>
                <span class="metric">
                  <span class="metric-value">{genome.decisions}</span>
                  <span class="metric-label">DECISIONS</span>
                </span>
              </div>
              <div class="genome-footer">
                <span class="last-active">LAST: {formatLastActive(genome.last_active)}</span>
              </div>
            </div>
          {/each}
        </div>
      </div>

      <!-- Genome Detail -->
      <div class="genome-detail card">
        <h3>GENOME DEFINITION</h3>
        {#if selectedGenome}
          <div class="detail-header">
            <div class="detail-title">
              <span class="detail-cli" style="color: {getCliColor(selectedGenome.cli)}">
                {selectedGenome.cli.toUpperCase()}
              </span>
              <span class="detail-role">{formatRole(selectedGenome.name, selectedGenome.cli)}</span>
            </div>
            <div class="detail-stats">
              <span class="detail-stat green">{selectedGenome.spawns_today} spawns today</span>
              <span class="detail-stat yellow">{selectedGenome.points_earned} points</span>
            </div>
          </div>
          <div class="detail-content">
            {#if loadingContent}
              <div class="loading-content">
                <span class="loading-text">LOADING_DEFINITION...</span>
              </div>
            {:else if genomeContent}
              <pre class="genome-markdown">{genomeContent}</pre>
            {/if}
          </div>
        {:else}
          <div class="empty-detail">
            <span class="empty-text">SELECT A GENOME TO VIEW DEFINITION</span>
          </div>
        {/if}
      </div>
    </div>
  {/if}
</div>

<style>
  .page {
    display: flex;
    flex-direction: column;
    gap: 24px;
  }

  .page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 2px solid var(--border);
    padding-bottom: 16px;
    flex-wrap: wrap;
    gap: 16px;
  }

  .controls {
    display: flex;
    gap: 12px;
    align-items: center;
    flex-wrap: wrap;
  }

  .filter-select {
    padding: 10px 16px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    text-transform: uppercase;
    font-weight: 700;
    background: var(--surface);
    border: 2px solid var(--border);
    color: var(--text-main);
    cursor: pointer;
    box-shadow: 4px 4px 0 0 var(--border);
  }

  .filter-select:hover {
    border-color: var(--terminal-green);
    box-shadow: 4px 4px 0 0 var(--terminal-green);
  }

  .filter-select:focus {
    outline: none;
    border-color: var(--terminal-green);
  }

  .stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
    gap: 12px;
  }

  .stat-card {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 8px;
    padding: 16px;
    background: var(--surface);
    border: 2px solid var(--border);
    box-shadow: 4px 4px 0 0 var(--border);
  }

  .stat-value {
    font-family: 'JetBrains Mono', monospace;
    font-size: 28px;
    font-weight: 700;
    color: var(--text-main);
  }

  .stat-value.green {
    color: var(--terminal-green);
  }

  .stat-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 9px;
    text-transform: uppercase;
    color: var(--text-muted);
    letter-spacing: 0.1em;
    text-align: center;
  }

  .cli-summary {
    padding: 16px;
  }

  .hint {
    color: var(--text-muted);
    font-size: 10px;
    text-transform: uppercase;
    margin: 0 0 16px;
    letter-spacing: 0.1em;
  }

  .cli-summary h3 {
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    text-transform: uppercase;
    color: var(--text-muted);
    margin-bottom: 16px;
    letter-spacing: 0.1em;
  }

  .cli-bars {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  .cli-bar {
    display: grid;
    grid-template-columns: 100px 1fr 250px;
    align-items: center;
    gap: 16px;
  }

  @media (max-width: 768px) {
    .cli-bar {
      grid-template-columns: 80px 1fr;
    }
    .cli-stats {
      display: none;
    }
  }

  .cli-name {
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    font-weight: 700;
  }

  .bar-container {
    height: 12px;
    background: var(--border);
    border-radius: 2px;
    overflow: hidden;
  }

  .bar-fill {
    height: 100%;
    transition: width 0.3s ease;
  }

  .cli-stats {
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    color: var(--text-muted);
    text-align: right;
  }

  .content-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 24px;
  }

  @media (max-width: 1024px) {
    .content-grid {
      grid-template-columns: 1fr;
    }
  }

  .genome-list,
  .genome-detail {
    min-height: 500px;
    max-height: 700px;
    overflow: hidden;
    display: flex;
    flex-direction: column;
  }

  .genome-list h3,
  .genome-detail h3 {
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    text-transform: uppercase;
    color: var(--text-muted);
    margin-bottom: 16px;
    letter-spacing: 0.1em;
    flex-shrink: 0;
  }

  .genome-items {
    flex: 1;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .genome-item {
    display: flex;
    flex-direction: column;
    gap: 8px;
    padding: 12px;
    background: rgba(0, 0, 0, 0.3);
    border: 1px solid var(--border);
    cursor: pointer;
    transition: all 0.2s ease;
    text-align: left;
    width: 100%;
    font-family: inherit;
    color: inherit;
  }

  .genome-item:hover {
    border-color: var(--terminal-green);
  }

  .genome-item.selected {
    border-color: var(--terminal-green);
    background: rgba(51, 255, 0, 0.1);
  }

  .genome-item.active {
    border-left: 3px solid var(--terminal-green);
  }

  .template-packs {
    padding: 16px;
  }

  .template-pack-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
    gap: 16px;
  }

  .template-pack {
    border: 1px solid var(--border);
    padding: 12px;
    background: rgba(0, 0, 0, 0.25);
  }

  .template-pack-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
    gap: 8px;
  }

  .template-name {
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.1em;
  }

  .template-count {
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    color: var(--text-muted);
    text-transform: uppercase;
  }

  .template-desc {
    font-size: 11px;
    color: var(--text-muted);
    margin-bottom: 10px;
  }

  .role-row {
    display: grid;
    grid-template-columns: 90px 1fr;
    gap: 8px;
    align-items: start;
    margin-bottom: 6px;
  }

  .role-row.muted .role-label {
    color: var(--text-muted);
  }

  .role-row.missing .role-label {
    color: var(--warning);
  }

  .role-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 9px;
    text-transform: uppercase;
    letter-spacing: 0.1em;
  }

  .role-list {
    font-size: 11px;
    color: var(--text-main);
  }

  .genome-header {
    display: flex;
    align-items: center;
    gap: 12px;
  }

  .genome-cli {
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    font-weight: 700;
    padding: 2px 6px;
    background: rgba(255, 255, 255, 0.1);
    border-radius: 2px;
  }

  .genome-role {
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    font-weight: 600;
    color: var(--text-main);
    flex: 1;
  }

  .toggle-btn {
    font-family: 'JetBrains Mono', monospace;
    font-size: 9px;
    font-weight: 700;
    padding: 4px 8px;
    border: 1px solid var(--system-red);
    background: transparent;
    color: var(--system-red);
    cursor: pointer;
    transition: all 0.2s ease;
    min-width: 36px;
  }

  .toggle-btn.enabled {
    border-color: var(--terminal-green);
    color: var(--terminal-green);
  }

  .toggle-btn:hover {
    background: rgba(255, 68, 68, 0.2);
  }

  .toggle-btn.enabled:hover {
    background: rgba(51, 255, 0, 0.2);
  }

  .toggle-btn.loading {
    opacity: 0.5;
    cursor: wait;
  }

  .genome-item.disabled {
    opacity: 0.5;
  }

  .genome-item.disabled .genome-role {
    text-decoration: line-through;
    color: var(--text-muted);
  }

  .genome-metrics {
    display: flex;
    gap: 16px;
  }

  .metric {
    display: flex;
    flex-direction: column;
    gap: 2px;
  }

  .metric.highlight .metric-value {
    color: var(--terminal-green);
  }

  .metric-value {
    font-family: 'JetBrains Mono', monospace;
    font-size: 14px;
    font-weight: 700;
    color: var(--text-muted);
  }

  .metric-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 8px;
    text-transform: uppercase;
    color: var(--text-muted);
    letter-spacing: 0.1em;
  }

  .genome-footer {
    display: flex;
    justify-content: flex-end;
  }

  .last-active {
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    color: var(--text-muted);
  }

  .detail-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    padding-bottom: 16px;
    border-bottom: 1px solid var(--border);
    margin-bottom: 16px;
    flex-wrap: wrap;
    gap: 12px;
  }

  .detail-title {
    display: flex;
    align-items: center;
    gap: 12px;
  }

  .detail-cli {
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    font-weight: 700;
    padding: 4px 8px;
    background: rgba(255, 255, 255, 0.1);
    border-radius: 2px;
  }

  .detail-role {
    font-family: 'JetBrains Mono', monospace;
    font-size: 16px;
    font-weight: 700;
    color: var(--text-main);
  }

  .detail-stats {
    display: flex;
    gap: 16px;
  }

  .detail-stat {
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
  }

  .detail-stat.green {
    color: var(--terminal-green);
  }

  .detail-stat.yellow {
    color: var(--warning);
  }

  .detail-content {
    flex: 1;
    overflow-y: auto;
  }

  .genome-markdown {
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    line-height: 1.6;
    color: var(--text-main);
    background: rgba(0, 0, 0, 0.3);
    padding: 16px;
    border: 1px solid var(--border);
    white-space: pre-wrap;
    word-break: break-word;
    overflow-x: auto;
  }

  .loading-state,
  .error-state,
  .empty-detail,
  .loading-content {
    flex: 1;
    display: flex;
    justify-content: center;
    align-items: center;
  }

  .loading-text {
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    color: var(--terminal-green);
    animation: blink 1s ease-in-out infinite;
  }

  .error-text {
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    color: var(--system-red);
  }

  .empty-text {
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    color: var(--text-muted);
  }

  @keyframes blink {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
  }
</style>
