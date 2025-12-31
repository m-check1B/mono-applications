<script lang="ts">
  import { onMount } from 'svelte';

  interface Trace {
    trace_id: string;
    timestamp: string;
    agent_id: string;
    decision_type: string;
    decision: string;
    reasoning: string;
    alternatives: string[];
    confidence: number;
    outcome: string | null;
    duration_ms: number | null;
    linear_issue: string | null;
    genome: string | null;
    cli: string | null;
    context: Record<string, any>;
    metadata: Record<string, any>;
  }

  interface Stats {
    total_traces: number;
    by_type: Record<string, number>;
    by_agent: Record<string, number>;
    by_outcome: Record<string, number>;
    by_genome: Record<string, number>;
    oldest_trace: string | null;
    newest_trace: string | null;
  }

  let traces = $state<Trace[]>([]);
  let stats = $state<Stats | null>(null);
  let loading = $state(true);
  let error = $state<string | null>(null);
  let selectedTrace = $state<Trace | null>(null);

  // Filters
  let filterType = $state('');
  let filterAgent = $state('');
  let limit = $state(50);

  async function loadTraces() {
    loading = true;
    error = null;
    try {
      const params = new URLSearchParams();
      if (filterType) params.set('type', filterType);
      if (filterAgent) params.set('agent_id', filterAgent);
      params.set('limit', limit.toString());

      const response = await fetch(`/api/traces?${params}`);
      const data = await response.json();
      traces = data.traces || [];
      stats = data.stats || null;
    } catch (e) {
      error = e instanceof Error ? e.message : 'Failed to load traces';
    } finally {
      loading = false;
    }
  }

  function formatTimestamp(ts: string): string {
    const date = new Date(ts);
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    });
  }

  function getTypeColor(type: string): string {
    const colors: Record<string, string> = {
      spawn: '#33ff00',
      task_selection: '#00d4ff',
      implementation_strategy: '#ff9500',
      tool_choice: '#9d4edd',
      error_handling: '#ff4444',
      completion: '#33ff00',
      claim: '#00d4ff',
      skip: '#6b7280',
      delegate: '#ff9500',
      abort: '#ff4444'
    };
    return colors[type] || '#6b7280';
  }

  function getOutcomeColor(outcome: string | null): string {
    if (!outcome) return '#6b7280';
    const colors: Record<string, string> = {
      success: '#33ff00',
      complete: '#33ff00',
      partial: '#ff9500',
      failure: '#ff4444',
      error: '#ff4444',
      pending: '#6b7280'
    };
    return colors[outcome.toLowerCase()] || '#6b7280';
  }

  onMount(() => {
    loadTraces();
  });
</script>

<div class="page">
  <div class="page-header">
    <h2 class="glitch">Decision Traces // Agent Observability</h2>
    <div class="controls">
      <select bind:value={filterType} onchange={loadTraces} class="filter-select">
        <option value="">ALL TYPES</option>
        <option value="spawn">SPAWN</option>
        <option value="task_selection">TASK_SELECTION</option>
        <option value="implementation_strategy">IMPL_STRATEGY</option>
        <option value="tool_choice">TOOL_CHOICE</option>
        <option value="completion">COMPLETION</option>
        <option value="error_handling">ERROR_HANDLING</option>
        <option value="claim">CLAIM</option>
        <option value="skip">SKIP</option>
        <option value="delegate">DELEGATE</option>
        <option value="abort">ABORT</option>
      </select>
      <select bind:value={limit} onchange={loadTraces} class="filter-select">
        <option value={25}>25 TRACES</option>
        <option value={50}>50 TRACES</option>
        <option value={100}>100 TRACES</option>
        <option value={200}>200 TRACES</option>
      </select>
      <button class="brutal-btn" onclick={loadTraces}>
        REFRESH
      </button>
    </div>
  </div>

  {#if stats}
    <div class="stats-grid">
      <div class="stat-card">
        <span class="stat-value">{stats.total_traces}</span>
        <span class="stat-label">TOTAL TRACES</span>
      </div>
      <div class="stat-card">
        <span class="stat-value">{Object.keys(stats.by_type).length}</span>
        <span class="stat-label">DECISION TYPES</span>
      </div>
      <div class="stat-card">
        <span class="stat-value">{Object.keys(stats.by_agent).length}</span>
        <span class="stat-label">UNIQUE AGENTS</span>
      </div>
      <div class="stat-card">
        <span class="stat-value">{Object.keys(stats.by_genome).length}</span>
        <span class="stat-label">GENOMES</span>
      </div>
    </div>

    <div class="type-breakdown">
      <h3>BY DECISION TYPE</h3>
      <div class="type-bars">
        {#each Object.entries(stats.by_type) as [type, count]}
          <div class="type-bar">
            <span class="type-name" style="color: {getTypeColor(type)}">{type.toUpperCase()}</span>
            <div class="bar-container">
              <div
                class="bar-fill"
                style="width: {(count / stats.total_traces) * 100}%; background: {getTypeColor(type)}"
              ></div>
            </div>
            <span class="type-count">{count}</span>
          </div>
        {/each}
      </div>
    </div>
  {/if}

  <div class="content-grid">
    <div class="traces-list card">
      <h3>RECENT DECISIONS</h3>
      {#if loading}
        <div class="loading-state">
          <span class="loading-text">LOADING_TRACES...</span>
        </div>
      {:else if error}
        <div class="error-state">
          <span class="error-text">ERROR: {error}</span>
        </div>
      {:else if traces.length === 0}
        <div class="empty-state">
          <span class="empty-text">NO_TRACES_FOUND</span>
        </div>
      {:else}
        <div class="trace-items">
          {#each traces.slice().reverse() as trace}
            <button
              class="trace-item"
              class:selected={selectedTrace?.trace_id === trace.trace_id}
              onclick={() => selectedTrace = trace}
            >
              <div class="trace-header">
                <span class="trace-type" style="color: {getTypeColor(trace.decision_type)}">
                  {trace.decision_type.toUpperCase()}
                </span>
                <span class="trace-time">{formatTimestamp(trace.timestamp)}</span>
              </div>
              <div class="trace-agent">{trace.agent_id}</div>
              <div class="trace-decision">{trace.decision.slice(0, 80)}...</div>
              {#if trace.outcome}
                <div class="trace-outcome" style="color: {getOutcomeColor(trace.outcome)}">
                  {trace.outcome.toUpperCase()}
                </div>
              {/if}
            </button>
          {/each}
        </div>
      {/if}
    </div>

    <div class="trace-detail card">
      <h3>TRACE DETAIL</h3>
      {#if selectedTrace}
        <div class="detail-content">
          <div class="detail-row">
            <span class="detail-label">TRACE_ID</span>
            <span class="detail-value mono">{selectedTrace.trace_id}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">TIMESTAMP</span>
            <span class="detail-value">{formatTimestamp(selectedTrace.timestamp)}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">AGENT</span>
            <span class="detail-value mono">{selectedTrace.agent_id}</span>
          </div>
          {#if selectedTrace.genome}
            <div class="detail-row">
              <span class="detail-label">GENOME</span>
              <span class="detail-value">{selectedTrace.genome}</span>
            </div>
          {/if}
          {#if selectedTrace.cli}
            <div class="detail-row">
              <span class="detail-label">CLI</span>
              <span class="detail-value">{selectedTrace.cli}</span>
            </div>
          {/if}
          {#if selectedTrace.linear_issue}
            <div class="detail-row">
              <span class="detail-label">LINEAR</span>
              <a href="https://linear.app/verduona/issue/{selectedTrace.linear_issue}" target="_blank" class="detail-link">
                {selectedTrace.linear_issue}
              </a>
            </div>
          {/if}
          <div class="detail-section">
            <span class="detail-label">DECISION</span>
            <div class="detail-text">{selectedTrace.decision}</div>
          </div>
          <div class="detail-section">
            <span class="detail-label">REASONING</span>
            <div class="detail-text">{selectedTrace.reasoning}</div>
          </div>
          {#if selectedTrace.alternatives.length > 0}
            <div class="detail-section">
              <span class="detail-label">ALTERNATIVES</span>
              <ul class="alternatives-list">
                {#each selectedTrace.alternatives as alt}
                  <li>{alt}</li>
                {/each}
              </ul>
            </div>
          {/if}
          {#if selectedTrace.confidence > 0}
            <div class="detail-row">
              <span class="detail-label">CONFIDENCE</span>
              <div class="confidence-bar">
                <div class="confidence-fill" style="width: {selectedTrace.confidence * 100}%"></div>
                <span class="confidence-text">{(selectedTrace.confidence * 100).toFixed(0)}%</span>
              </div>
            </div>
          {/if}
          {#if selectedTrace.outcome}
            <div class="detail-row">
              <span class="detail-label">OUTCOME</span>
              <span class="detail-value outcome" style="color: {getOutcomeColor(selectedTrace.outcome)}">
                {selectedTrace.outcome.toUpperCase()}
              </span>
            </div>
          {/if}
          {#if selectedTrace.duration_ms}
            <div class="detail-row">
              <span class="detail-label">DURATION</span>
              <span class="detail-value">{selectedTrace.duration_ms}ms</span>
            </div>
          {/if}
          {#if Object.keys(selectedTrace.context).length > 0}
            <div class="detail-section">
              <span class="detail-label">CONTEXT</span>
              <pre class="context-json">{JSON.stringify(selectedTrace.context, null, 2)}</pre>
            </div>
          {/if}
        </div>
      {:else}
        <div class="empty-detail">
          <span class="empty-text">SELECT A TRACE TO VIEW DETAILS</span>
        </div>
      {/if}
    </div>
  </div>
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
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 16px;
  }

  .stat-card {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 8px;
    padding: 20px;
    background: var(--surface);
    border: 2px solid var(--border);
    box-shadow: 4px 4px 0 0 var(--border);
  }

  .stat-value {
    font-family: 'JetBrains Mono', monospace;
    font-size: 32px;
    font-weight: 700;
    color: var(--terminal-green);
  }

  .stat-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    text-transform: uppercase;
    color: var(--text-muted);
    letter-spacing: 0.1em;
  }

  .type-breakdown {
    padding: 16px;
    background: var(--surface);
    border: 2px solid var(--border);
    box-shadow: 4px 4px 0 0 var(--border);
  }

  .type-breakdown h3 {
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    text-transform: uppercase;
    color: var(--text-muted);
    margin-bottom: 16px;
    letter-spacing: 0.1em;
  }

  .type-bars {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .type-bar {
    display: grid;
    grid-template-columns: 160px 1fr 60px;
    align-items: center;
    gap: 12px;
  }

  .type-name {
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    font-weight: 600;
  }

  .bar-container {
    height: 8px;
    background: var(--border);
    border-radius: 2px;
    overflow: hidden;
  }

  .bar-fill {
    height: 100%;
    transition: width 0.3s ease;
  }

  .type-count {
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    color: var(--text-main);
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

  .traces-list,
  .trace-detail {
    min-height: 500px;
    max-height: 700px;
    overflow: hidden;
    display: flex;
    flex-direction: column;
  }

  .traces-list h3,
  .trace-detail h3 {
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    text-transform: uppercase;
    color: var(--text-muted);
    margin-bottom: 16px;
    letter-spacing: 0.1em;
    flex-shrink: 0;
  }

  .trace-items {
    flex: 1;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .trace-item {
    display: flex;
    flex-direction: column;
    gap: 4px;
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

  .trace-item:hover {
    border-color: var(--terminal-green);
  }

  .trace-item.selected {
    border-color: var(--terminal-green);
    background: rgba(51, 255, 0, 0.1);
  }

  .trace-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .trace-type {
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    font-weight: 700;
  }

  .trace-time {
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    color: var(--text-muted);
  }

  .trace-agent {
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    color: var(--cyan-data);
  }

  .trace-decision {
    font-size: 12px;
    color: var(--text-main);
    line-height: 1.4;
  }

  .trace-outcome {
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    font-weight: 700;
    margin-top: 4px;
  }

  .detail-content {
    flex: 1;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    gap: 16px;
  }

  .detail-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 16px;
  }

  .detail-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    text-transform: uppercase;
    color: var(--text-muted);
    letter-spacing: 0.1em;
    flex-shrink: 0;
  }

  .detail-value {
    font-size: 13px;
    color: var(--text-main);
    text-align: right;
  }

  .detail-value.mono {
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
  }

  .detail-value.outcome {
    font-weight: 700;
  }

  .detail-link {
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    color: var(--cyan-data);
    text-decoration: none;
  }

  .detail-link:hover {
    text-decoration: underline;
  }

  .detail-section {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .detail-text {
    font-size: 13px;
    color: var(--text-main);
    line-height: 1.5;
    background: rgba(0, 0, 0, 0.3);
    padding: 12px;
    border: 1px solid var(--border);
  }

  .alternatives-list {
    margin: 0;
    padding-left: 20px;
    font-size: 13px;
    color: var(--text-main);
  }

  .alternatives-list li {
    margin-bottom: 4px;
  }

  .confidence-bar {
    display: flex;
    align-items: center;
    gap: 8px;
    flex: 1;
    max-width: 200px;
  }

  .confidence-fill {
    height: 8px;
    background: var(--terminal-green);
    border-radius: 2px;
  }

  .confidence-text {
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    color: var(--terminal-green);
  }

  .context-json {
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    color: var(--text-main);
    background: rgba(0, 0, 0, 0.3);
    padding: 12px;
    border: 1px solid var(--border);
    overflow-x: auto;
    white-space: pre-wrap;
    word-break: break-word;
  }

  .loading-state,
  .error-state,
  .empty-state,
  .empty-detail {
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
