import { s as sanitize_props, a as spread_props, c as slot } from "./index2.js";
import { I as Icon } from "./Icon.js";
import { w as writable } from "./index.js";
import { a as api } from "./client.js";
import { i as isOnline, d as offlineKnowledge, q as queueOperation, c as clearOfflineStore, O as OFFLINE_STORES, e as offlineKnowledgeTypes } from "./offlineStorage.js";
function Calendar($$renderer, $$props) {
  const $$sanitized_props = sanitize_props($$props);
  const iconNode = [
    ["path", { "d": "M8 2v4" }],
    ["path", { "d": "M16 2v4" }],
    [
      "rect",
      { "width": "18", "height": "18", "x": "3", "y": "4", "rx": "2" }
    ],
    ["path", { "d": "M3 10h18" }]
  ];
  Icon($$renderer, spread_props([
    { name: "calendar" },
    $$sanitized_props,
    {
      /**
       * @component @name Calendar
       * @description Lucide SVG icon component, renders SVG Element with children.
       *
       * @preview ![img](data:image/svg+xml;base64,PHN2ZyAgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIgogIHdpZHRoPSIyNCIKICBoZWlnaHQ9IjI0IgogIHZpZXdCb3g9IjAgMCAyNCAyNCIKICBmaWxsPSJub25lIgogIHN0cm9rZT0iIzAwMCIgc3R5bGU9ImJhY2tncm91bmQtY29sb3I6ICNmZmY7IGJvcmRlci1yYWRpdXM6IDJweCIKICBzdHJva2Utd2lkdGg9IjIiCiAgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIgogIHN0cm9rZS1saW5lam9pbj0icm91bmQiCj4KICA8cGF0aCBkPSJNOCAydjQiIC8+CiAgPHBhdGggZD0iTTE2IDJ2NCIgLz4KICA8cmVjdCB3aWR0aD0iMTgiIGhlaWdodD0iMTgiIHg9IjMiIHk9IjQiIHJ4PSIyIiAvPgogIDxwYXRoIGQ9Ik0zIDEwaDE4IiAvPgo8L3N2Zz4K) - https://lucide.dev/icons/calendar
       * @see https://lucide.dev/guide/packages/lucide-svelte - Documentation
       *
       * @param {Object} props - Lucide icons props and any valid SVG attribute
       * @returns {FunctionalComponent} Svelte component
       *
       */
      iconNode,
      children: ($$renderer2) => {
        $$renderer2.push(`<!--[-->`);
        slot($$renderer2, $$props, "default", {});
        $$renderer2.push(`<!--]-->`);
      },
      $$slots: { default: true }
    }
  ]));
}
function Plus($$renderer, $$props) {
  const $$sanitized_props = sanitize_props($$props);
  const iconNode = [["path", { "d": "M5 12h14" }], ["path", { "d": "M12 5v14" }]];
  Icon($$renderer, spread_props([
    { name: "plus" },
    $$sanitized_props,
    {
      /**
       * @component @name Plus
       * @description Lucide SVG icon component, renders SVG Element with children.
       *
       * @preview ![img](data:image/svg+xml;base64,PHN2ZyAgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIgogIHdpZHRoPSIyNCIKICBoZWlnaHQ9IjI0IgogIHZpZXdCb3g9IjAgMCAyNCAyNCIKICBmaWxsPSJub25lIgogIHN0cm9rZT0iIzAwMCIgc3R5bGU9ImJhY2tncm91bmQtY29sb3I6ICNmZmY7IGJvcmRlci1yYWRpdXM6IDJweCIKICBzdHJva2Utd2lkdGg9IjIiCiAgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIgogIHN0cm9rZS1saW5lam9pbj0icm91bmQiCj4KICA8cGF0aCBkPSJNNSAxMmgxNCIgLz4KICA8cGF0aCBkPSJNMTIgNXYxNCIgLz4KPC9zdmc+Cg==) - https://lucide.dev/icons/plus
       * @see https://lucide.dev/guide/packages/lucide-svelte - Documentation
       *
       * @param {Object} props - Lucide icons props and any valid SVG attribute
       * @returns {FunctionalComponent} Svelte component
       *
       */
      iconNode,
      children: ($$renderer2) => {
        $$renderer2.push(`<!--[-->`);
        slot($$renderer2, $$props, "default", {});
        $$renderer2.push(`<!--]-->`);
      },
      $$slots: { default: true }
    }
  ]));
}
function Trash_2($$renderer, $$props) {
  const $$sanitized_props = sanitize_props($$props);
  const iconNode = [
    ["path", { "d": "M3 6h18" }],
    ["path", { "d": "M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6" }],
    ["path", { "d": "M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2" }],
    ["line", { "x1": "10", "x2": "10", "y1": "11", "y2": "17" }],
    ["line", { "x1": "14", "x2": "14", "y1": "11", "y2": "17" }]
  ];
  Icon($$renderer, spread_props([
    { name: "trash-2" },
    $$sanitized_props,
    {
      /**
       * @component @name Trash2
       * @description Lucide SVG icon component, renders SVG Element with children.
       *
       * @preview ![img](data:image/svg+xml;base64,PHN2ZyAgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIgogIHdpZHRoPSIyNCIKICBoZWlnaHQ9IjI0IgogIHZpZXdCb3g9IjAgMCAyNCAyNCIKICBmaWxsPSJub25lIgogIHN0cm9rZT0iIzAwMCIgc3R5bGU9ImJhY2tncm91bmQtY29sb3I6ICNmZmY7IGJvcmRlci1yYWRpdXM6IDJweCIKICBzdHJva2Utd2lkdGg9IjIiCiAgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIgogIHN0cm9rZS1saW5lam9pbj0icm91bmQiCj4KICA8cGF0aCBkPSJNMyA2aDE4IiAvPgogIDxwYXRoIGQ9Ik0xOSA2djE0YzAgMS0xIDItMiAySDdjLTEgMC0yLTEtMi0yVjYiIC8+CiAgPHBhdGggZD0iTTggNlY0YzAtMSAxLTIgMi0yaDRjMSAwIDIgMSAyIDJ2MiIgLz4KICA8bGluZSB4MT0iMTAiIHgyPSIxMCIgeTE9IjExIiB5Mj0iMTciIC8+CiAgPGxpbmUgeDE9IjE0IiB4Mj0iMTQiIHkxPSIxMSIgeTI9IjE3IiAvPgo8L3N2Zz4K) - https://lucide.dev/icons/trash-2
       * @see https://lucide.dev/guide/packages/lucide-svelte - Documentation
       *
       * @param {Object} props - Lucide icons props and any valid SVG attribute
       * @returns {FunctionalComponent} Svelte component
       *
       */
      iconNode,
      children: ($$renderer2) => {
        $$renderer2.push(`<!--[-->`);
        slot($$renderer2, $$props, "default", {});
        $$renderer2.push(`<!--]-->`);
      },
      $$slots: { default: true }
    }
  ]));
}
function X($$renderer, $$props) {
  const $$sanitized_props = sanitize_props($$props);
  const iconNode = [
    ["path", { "d": "M18 6 6 18" }],
    ["path", { "d": "m6 6 12 12" }]
  ];
  Icon($$renderer, spread_props([
    { name: "x" },
    $$sanitized_props,
    {
      /**
       * @component @name X
       * @description Lucide SVG icon component, renders SVG Element with children.
       *
       * @preview ![img](data:image/svg+xml;base64,PHN2ZyAgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIgogIHdpZHRoPSIyNCIKICBoZWlnaHQ9IjI0IgogIHZpZXdCb3g9IjAgMCAyNCAyNCIKICBmaWxsPSJub25lIgogIHN0cm9rZT0iIzAwMCIgc3R5bGU9ImJhY2tncm91bmQtY29sb3I6ICNmZmY7IGJvcmRlci1yYWRpdXM6IDJweCIKICBzdHJva2Utd2lkdGg9IjIiCiAgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIgogIHN0cm9rZS1saW5lam9pbj0icm91bmQiCj4KICA8cGF0aCBkPSJNMTggNiA2IDE4IiAvPgogIDxwYXRoIGQ9Im02IDYgMTIgMTIiIC8+Cjwvc3ZnPgo=) - https://lucide.dev/icons/x
       * @see https://lucide.dev/guide/packages/lucide-svelte - Documentation
       *
       * @param {Object} props - Lucide icons props and any valid SVG attribute
       * @returns {FunctionalComponent} Svelte component
       *
       */
      iconNode,
      children: ($$renderer2) => {
        $$renderer2.push(`<!--[-->`);
        slot($$renderer2, $$props, "default", {});
        $$renderer2.push(`<!--]-->`);
      },
      $$slots: { default: true }
    }
  ]));
}
const initialState = {
  items: [],
  itemTypes: [],
  isLoading: false,
  error: null,
  selectedTypeId: null
};
function createKnowledgeStore() {
  const { subscribe, set, update } = writable(initialState);
  return {
    subscribe,
    // Item Types
    async loadItemTypes() {
      update((state) => ({ ...state, isLoading: true, error: null }));
      try {
        if (!isOnline()) {
          const itemTypes2 = await offlineKnowledgeTypes.getAll();
          update((state) => ({
            ...state,
            itemTypes: itemTypes2,
            isLoading: false
          }));
          return { success: true, itemTypes: itemTypes2 };
        }
        const response = await api.knowledge.listItemTypes();
        const itemTypes = response.itemTypes || [];
        await clearOfflineStore(OFFLINE_STORES.KNOWLEDGE_TYPES);
        for (const itemType of itemTypes) {
          await offlineKnowledgeTypes.save(itemType);
        }
        update((state) => ({
          ...state,
          itemTypes,
          isLoading: false
        }));
        return { success: true, itemTypes };
      } catch (error) {
        const errorMessage = error.detail || "Failed to load item types";
        update((state) => ({
          ...state,
          isLoading: false,
          error: errorMessage
        }));
        return { success: false, error: errorMessage };
      }
    },
    async createItemType(data) {
      try {
        if (!isOnline()) {
          return { success: false, error: "Offline mode: cannot create item types." };
        }
        const newType = await api.knowledge.createItemType(data);
        await offlineKnowledgeTypes.save(newType);
        update((state) => ({
          ...state,
          itemTypes: [...state.itemTypes, newType]
        }));
        return { success: true, itemType: newType };
      } catch (error) {
        const errorMessage = error.detail || "Failed to create item type";
        return { success: false, error: errorMessage };
      }
    },
    async updateItemType(typeId, updates) {
      try {
        if (!isOnline()) {
          return { success: false, error: "Offline mode: cannot update item types." };
        }
        const updatedType = await api.knowledge.updateItemType(typeId, updates);
        await offlineKnowledgeTypes.save(updatedType);
        update((state) => ({
          ...state,
          itemTypes: state.itemTypes.map((t) => t.id === typeId ? updatedType : t)
        }));
        return { success: true, itemType: updatedType };
      } catch (error) {
        const errorMessage = error.detail || "Failed to update item type";
        return { success: false, error: errorMessage };
      }
    },
    async deleteItemType(typeId) {
      try {
        if (!isOnline()) {
          return { success: false, error: "Offline mode: cannot delete item types." };
        }
        await api.knowledge.deleteItemType(typeId);
        await offlineKnowledgeTypes.delete(typeId);
        update((state) => ({
          ...state,
          itemTypes: state.itemTypes.filter((t) => t.id !== typeId)
        }));
        return { success: true };
      } catch (error) {
        const errorMessage = error.detail || "Failed to delete item type";
        return { success: false, error: errorMessage };
      }
    },
    // Knowledge Items
    async loadKnowledgeItems(filters) {
      update((state) => ({ ...state, isLoading: true, error: null }));
      try {
        if (!isOnline()) {
          const offlineItems = await offlineKnowledge.getAll();
          const items2 = offlineItems.filter((item) => {
            if (filters?.typeId && item.typeId !== filters.typeId) return false;
            if (filters?.completed !== void 0 && item.completed !== filters.completed) return false;
            return true;
          });
          update((state) => ({
            ...state,
            items: items2,
            isLoading: false
          }));
          return { success: true, items: items2 };
        }
        const response = await api.knowledge.listKnowledgeItems(filters);
        const items = response.items || [];
        await clearOfflineStore(OFFLINE_STORES.KNOWLEDGE);
        for (const item of items) {
          await offlineKnowledge.save(item);
        }
        update((state) => ({
          ...state,
          items,
          isLoading: false
        }));
        return { success: true, items };
      } catch (error) {
        const errorMessage = error.detail || "Failed to load knowledge items";
        update((state) => ({
          ...state,
          isLoading: false,
          error: errorMessage
        }));
        return { success: false, error: errorMessage };
      }
    },
    async createKnowledgeItem(data) {
      try {
        if (!isOnline()) {
          const now = (/* @__PURE__ */ new Date()).toISOString();
          const offlineItem = {
            id: crypto.randomUUID?.() || `offline-${Date.now()}`,
            userId: "offline",
            typeId: data.typeId,
            title: data.title,
            content: data.content,
            item_metadata: data.item_metadata,
            completed: data.completed ?? false,
            createdAt: now,
            updatedAt: now
          };
          await offlineKnowledge.save(offlineItem);
          await queueOperation({
            type: "create",
            entity: "knowledge",
            data,
            endpoint: "/knowledge/items"
          });
          update((state) => ({
            ...state,
            items: [offlineItem, ...state.items]
          }));
          return { success: true, item: offlineItem };
        }
        const newItem = await api.knowledge.createKnowledgeItem(data);
        await offlineKnowledge.save(newItem);
        update((state) => ({
          ...state,
          items: [newItem, ...state.items]
        }));
        return { success: true, item: newItem };
      } catch (error) {
        const errorMessage = error.detail || "Failed to create knowledge item";
        return { success: false, error: errorMessage };
      }
    },
    async updateKnowledgeItem(itemId, updates) {
      try {
        if (!isOnline()) {
          const now = (/* @__PURE__ */ new Date()).toISOString();
          let updatedItem2 = null;
          update((state) => {
            const items = state.items.map((item) => {
              if (item.id !== itemId) return item;
              const updated = {
                ...item,
                ...updates,
                updatedAt: now
              };
              updatedItem2 = updated;
              return updated;
            });
            return {
              ...state,
              items
            };
          });
          if (updatedItem2) {
            await offlineKnowledge.save(updatedItem2);
          }
          await queueOperation({
            type: "update",
            entity: "knowledge",
            data: updates,
            endpoint: `/knowledge/items/${itemId}`
          });
          return { success: true, item: updatedItem2 };
        }
        const updatedItem = await api.knowledge.updateKnowledgeItem(itemId, updates);
        await offlineKnowledge.save(updatedItem);
        update((state) => ({
          ...state,
          items: state.items.map((i) => i.id === itemId ? updatedItem : i)
        }));
        return { success: true, item: updatedItem };
      } catch (error) {
        const errorMessage = error.detail || "Failed to update knowledge item";
        return { success: false, error: errorMessage };
      }
    },
    async toggleKnowledgeItem(itemId) {
      try {
        if (!isOnline()) {
          let updatedItem2 = null;
          update((state) => {
            const items = state.items.map((item) => {
              if (item.id !== itemId) return item;
              updatedItem2 = {
                ...item,
                completed: !item.completed,
                updatedAt: (/* @__PURE__ */ new Date()).toISOString()
              };
              return updatedItem2;
            });
            return {
              ...state,
              items
            };
          });
          if (updatedItem2) {
            await offlineKnowledge.save(updatedItem2);
          }
          await queueOperation({
            type: "create",
            entity: "knowledge",
            data: {},
            endpoint: `/knowledge/items/${itemId}/toggle`
          });
          return { success: true, item: updatedItem2 };
        }
        const updatedItem = await api.knowledge.toggleKnowledgeItem(itemId);
        await offlineKnowledge.save(updatedItem);
        update((state) => ({
          ...state,
          items: state.items.map((i) => i.id === itemId ? updatedItem : i)
        }));
        return { success: true, item: updatedItem };
      } catch (error) {
        const errorMessage = error.detail || "Failed to toggle knowledge item";
        return { success: false, error: errorMessage };
      }
    },
    async deleteKnowledgeItem(itemId) {
      try {
        if (!isOnline()) {
          await offlineKnowledge.delete(itemId);
          await queueOperation({
            type: "delete",
            entity: "knowledge",
            data: {},
            endpoint: `/knowledge/items/${itemId}`
          });
          update((state) => ({
            ...state,
            items: state.items.filter((i) => i.id !== itemId)
          }));
          return { success: true };
        }
        await api.knowledge.deleteKnowledgeItem(itemId);
        update((state) => ({
          ...state,
          items: state.items.filter((i) => i.id !== itemId)
        }));
        return { success: true };
      } catch (error) {
        const errorMessage = error.detail || "Failed to delete knowledge item";
        return { success: false, error: errorMessage };
      }
    },
    async searchKnowledgeItems(query, typeId) {
      update((state) => ({ ...state, isLoading: true }));
      try {
        if (!isOnline()) {
          const offlineItems = await offlineKnowledge.getAll();
          const q = query.toLowerCase();
          const items2 = offlineItems.filter((item) => {
            if (typeId && item.typeId !== typeId) return false;
            return item.title.toLowerCase().includes(q) || (item.content || "").toLowerCase().includes(q);
          });
          update((state) => ({
            ...state,
            items: items2,
            isLoading: false
          }));
          return { success: true, items: items2 };
        }
        const response = await api.knowledge.searchKnowledgeItems(query, typeId);
        const items = response.items || [];
        update((state) => ({
          ...state,
          items,
          isLoading: false
        }));
        return { success: true, items };
      } catch (error) {
        const errorMessage = error.detail || "Search failed";
        update((state) => ({
          ...state,
          isLoading: false,
          error: errorMessage
        }));
        return { success: false, error: errorMessage };
      }
    },
    setSelectedTypeId(typeId) {
      update((state) => ({ ...state, selectedTypeId: typeId }));
    },
    clearError() {
      update((state) => ({ ...state, error: null }));
    }
  };
}
const knowledgeStore = createKnowledgeStore();
export {
  Calendar as C,
  Plus as P,
  Trash_2 as T,
  X,
  knowledgeStore as k
};
