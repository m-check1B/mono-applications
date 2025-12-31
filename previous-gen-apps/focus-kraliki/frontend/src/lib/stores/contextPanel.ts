import { writable } from 'svelte/store';

export type PanelType =
  | 'tasks'
  | 'projects'
  | 'knowledge'
  | 'calendar'
  | 'analytics'
  | 'settings'
  | 'workflow'
  | 'shadow'
  | 'time'
  | 'pomodoro'
  | 'infra'
  | 'n8n'
  | 'voice'
  | 'captures'
  | null;

export interface PanelState {
  type: PanelType;
  data?: any;
  isOpen: boolean;
  refreshCounter?: number; // ✨ For real-time updates (Gap #6)
  scrollPositions?: Record<string, number>; // ✨ Gap #14: Scroll memory
}

function createContextPanelStore() {
  const { subscribe, set, update } = writable<PanelState>({
    type: null,
    data: undefined,
    isOpen: false,
    scrollPositions: {} // ✨ Gap #14: Initialize scroll memory
  });

  return {
    subscribe,

    open: (type: PanelType, data?: any) => {
      update(state => ({
        type,
        data,
        isOpen: true
      }));
    },

    close: () => {
      update(state => ({
        ...state,
        isOpen: false
      }));
      // Clear after animation
      setTimeout(() => {
        set({
          type: null,
          data: undefined,
          isOpen: false
        });
      }, 300);
    },

    toggle: (type: PanelType, data?: any) => {
      update(state => {
        if (state.isOpen && state.type === type) {
          return { ...state, isOpen: false };
        }
        return {
          type,
          data,
          isOpen: true
        };
      });
    },

    updateData: (data: any) => {
      update(state => ({
        ...state,
        data: { ...state.data, ...data }
      }));
    },

    // ✨ Refresh panel (for real-time updates - Gap #6)
    refresh: (type: PanelType) => {
      update(state => {
        // Only refresh if the panel is currently open and matches the type
        if (state.isOpen && state.type === type) {
          return {
            ...state,
            refreshCounter: (state.refreshCounter || 0) + 1
          };
        }
        return state;
      });
    },

    // ✨ Save scroll position (Gap #14: Scroll memory)
    saveScrollPosition: (type: PanelType, scrollTop: number) => {
      if (!type) return;
      update(state => ({
        ...state,
        scrollPositions: {
          ...state.scrollPositions,
          [type]: scrollTop
        }
      }));
    }
  };
}

export const contextPanelStore = createContextPanelStore();
