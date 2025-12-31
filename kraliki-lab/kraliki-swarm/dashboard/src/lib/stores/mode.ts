/**
 * Workspace Mode Store
 * Controls data editing permissions across the Kraliki Swarm dashboard.
 *
 * Modes:
 * - dev: Full CRUD access, can start agents
 * - normal: Limited editing, view-only for critical data
 * - readonly: View only, can export/save results
 *
 * Priority: URL param > localStorage > default 'normal'
 */
import { writable, derived, get } from 'svelte/store';
import { browser } from '$app/environment';

export type WorkspaceMode = 'dev' | 'normal' | 'readonly';

const STORAGE_KEY = 'kraliki-mode';
const VALID_MODES: WorkspaceMode[] = ['dev', 'normal', 'readonly'];

function isValidMode(mode: string | null): mode is WorkspaceMode {
  return mode !== null && VALID_MODES.includes(mode as WorkspaceMode);
}

function getInitialMode(): WorkspaceMode {
  if (!browser) return 'normal';

  // Priority 1: URL param
  const urlParams = new URLSearchParams(window.location.search);
  const urlMode = urlParams.get('mode');
  if (isValidMode(urlMode)) {
    return urlMode;
  }

  // Priority 2: localStorage
  const stored = localStorage.getItem(STORAGE_KEY);
  if (isValidMode(stored)) {
    return stored;
  }

  // Priority 3: Default
  return 'normal';
}

function createModeStore() {
  const { subscribe, set, update } = writable<WorkspaceMode>(getInitialMode());

  return {
    subscribe,
    set: (mode: WorkspaceMode) => {
      if (browser) {
        localStorage.setItem(STORAGE_KEY, mode);
      }
      set(mode);
    },
    update,
    // Utility to check URL override
    hasUrlOverride: (): boolean => {
      if (!browser) return false;
      const urlParams = new URLSearchParams(window.location.search);
      return isValidMode(urlParams.get('mode'));
    }
  };
}

export const workspaceMode = createModeStore();

// Derived permission helpers
export const canEdit = derived(workspaceMode, $mode => $mode === 'dev');
export const canExecute = derived(workspaceMode, $mode => $mode === 'dev');
export const canLimitedEdit = derived(workspaceMode, $mode => $mode === 'dev' || $mode === 'normal');
export const isReadOnly = derived(workspaceMode, $mode => $mode === 'readonly');
export const isDevMode = derived(workspaceMode, $mode => $mode === 'dev');

// Mode display info
export const modeInfo = derived(workspaceMode, $mode => {
  switch ($mode) {
    case 'dev':
      return {
        label: 'DEV',
        description: 'Full editing enabled',
        color: 'warning'
      };
    case 'readonly':
      return {
        label: 'READ-ONLY',
        description: 'Viewing only',
        color: 'muted'
      };
    default:
      return {
        label: 'NORMAL',
        description: 'Standard access',
        color: 'default'
      };
  }
});
