# Workspace Modes Feature Spec

**Date:** 2025-12-28
**Status:** Implemented

## Summary

Add workspace modes to Kraliki dashboard to control data editing permissions. Different modes for different use cases:

| Mode | CRUD Data | Start Agents | View Data | Save/Export |
|------|-----------|--------------|-----------|-------------|
| **DEV** | Full access | Yes | Yes | Yes |
| **NORMAL** | Limited | No | Yes | Yes |
| **READ-ONLY** | None | No | Yes | Results only |

## Use Cases

- **DEV mode**: For developers actively working on the system
- **NORMAL mode**: For operators monitoring the swarm
- **READ-ONLY mode**: For stakeholders viewing dashboards, agents querying state

## Implementation

### 1. Mode Store (`dashboard/src/lib/stores/mode.ts`)

```typescript
import { writable, derived } from 'svelte/store';
import { browser } from '$app/environment';
import { page } from '$app/stores';

export type WorkspaceMode = 'dev' | 'normal' | 'readonly';

function getInitialMode(): WorkspaceMode {
  if (!browser) return 'normal';

  // Priority 1: URL param
  const urlParams = new URLSearchParams(window.location.search);
  const urlMode = urlParams.get('mode');
  if (urlMode && ['dev', 'normal', 'readonly'].includes(urlMode)) {
    return urlMode as WorkspaceMode;
  }

  // Priority 2: localStorage
  const stored = localStorage.getItem('kraliki-mode');
  if (stored && ['dev', 'normal', 'readonly'].includes(stored)) {
    return stored as WorkspaceMode;
  }

  // Priority 3: Default
  return 'normal';
}

export const workspaceMode = writable<WorkspaceMode>(getInitialMode());

// Persist to localStorage when changed
if (browser) {
  workspaceMode.subscribe(mode => {
    localStorage.setItem('kraliki-mode', mode);
  });
}

// Derived permission helpers
export const canEdit = derived(workspaceMode, $mode => $mode === 'dev');
export const canExecute = derived(workspaceMode, $mode => $mode === 'dev');
export const isReadOnly = derived(workspaceMode, $mode => $mode === 'readonly');
```

### 2. Settings Page Addition

Add to `dashboard/src/routes/settings/+page.svelte`:

```svelte
<!-- Workspace Mode -->
<div class="card">
  <h3>WORKSPACE_MODE</h3>
  <div class="setting-row">
    <div class="setting-info">
      <span class="setting-name">Access Mode</span>
      <span class="setting-desc">Controls editing capabilities</span>
    </div>
    <select bind:value={$workspaceMode}>
      <option value="dev">DEV (Full Access)</option>
      <option value="normal">NORMAL (View + Limited Edit)</option>
      <option value="readonly">READ-ONLY (View Only)</option>
    </select>
  </div>
  <div class="mode-info">
    {#if $workspaceMode === 'dev'}
      <span class="mode-badge dev">DEV MODE: Full editing enabled</span>
    {:else if $workspaceMode === 'readonly'}
      <span class="mode-badge readonly">READ-ONLY: Viewing only</span>
    {:else}
      <span class="mode-badge normal">NORMAL: Standard access</span>
    {/if}
  </div>
</div>
```

### 3. Header Mode Indicator

Add to layout header:

```svelte
<script>
  import { workspaceMode } from '$lib/stores/mode';
</script>

{#if $workspaceMode !== 'normal'}
  <span class="mode-indicator" class:dev={$workspaceMode === 'dev'} class:readonly={$workspaceMode === 'readonly'}>
    {$workspaceMode.toUpperCase()}
  </span>
{/if}
```

### 4. Brain Page Controls

Update `dashboard/src/routes/brain/+page.svelte`:

```svelte
<script>
  import { canEdit, isReadOnly } from '$lib/stores/mode';
</script>

<!-- Disable SEND_TO_FOCUS in readonly -->
<button
  class="brutal-btn send-btn"
  onclick={() => sendToFocus(strategy)}
  disabled={sendingToFocus === strategy.id || $isReadOnly}
  title={$isReadOnly ? 'Read-only mode' : ''}
>
  {sendingToFocus === strategy.id ? 'SENDING...' : 'SEND_TO_FOCUS'}
</button>
```

## Files to Modify

1. `dashboard/src/lib/stores/mode.ts` (new file)
2. `dashboard/src/routes/settings/+page.svelte`
3. `dashboard/src/routes/brain/+page.svelte`
4. `dashboard/src/routes/+layout.svelte`
5. `dashboard/src/routes/data/+page.svelte`

## CSS for Mode Badges

```css
.mode-indicator {
  padding: 4px 8px;
  font-size: 9px;
  font-weight: 700;
  text-transform: uppercase;
}

.mode-indicator.dev {
  background: var(--warning, #ffaa00);
  color: var(--void);
}

.mode-indicator.readonly {
  background: #888;
  color: var(--void);
}

.mode-badge {
  padding: 8px 12px;
  font-size: 11px;
  display: block;
  margin-top: 12px;
}

.mode-badge.dev {
  background: rgba(255, 170, 0, 0.2);
  border-left: 3px solid var(--warning);
}

.mode-badge.readonly {
  background: rgba(136, 136, 136, 0.2);
  border-left: 3px solid #888;
}
```

## URL Sharing

Share read-only view: `https://kraliki.verduona.dev/brain?mode=readonly`

## Acceptance Criteria

- [x] Mode selector in settings page
- [x] Mode persists in localStorage
- [x] ?mode=readonly URL param overrides stored mode
- [x] DEV mode shows all edit buttons
- [x] READ-ONLY mode hides/disables edit buttons
- [x] Mode badge visible in header when not "normal"
- [x] SEND_TO_FOCUS disabled in readonly mode
- [x] Data page CRUD buttons hidden in readonly mode
