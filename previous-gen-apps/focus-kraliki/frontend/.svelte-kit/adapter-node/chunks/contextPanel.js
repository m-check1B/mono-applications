import { w as writable } from "./index.js";
function createContextPanelStore() {
  const { subscribe, set, update } = writable({
    type: null,
    data: void 0,
    isOpen: false,
    scrollPositions: {}
    // ✨ Gap #14: Initialize scroll memory
  });
  return {
    subscribe,
    open: (type, data) => {
      update((state) => ({
        type,
        data,
        isOpen: true
      }));
    },
    close: () => {
      update((state) => ({
        ...state,
        isOpen: false
      }));
      setTimeout(() => {
        set({
          type: null,
          data: void 0,
          isOpen: false
        });
      }, 300);
    },
    toggle: (type, data) => {
      update((state) => {
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
    updateData: (data) => {
      update((state) => ({
        ...state,
        data: { ...state.data, ...data }
      }));
    },
    // ✨ Refresh panel (for real-time updates - Gap #6)
    refresh: (type) => {
      update((state) => {
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
    saveScrollPosition: (type, scrollTop) => {
      if (!type) return;
      update((state) => ({
        ...state,
        scrollPositions: {
          ...state.scrollPositions,
          [type]: scrollTop
        }
      }));
    }
  };
}
const contextPanelStore = createContextPanelStore();
export {
  contextPanelStore as c
};
