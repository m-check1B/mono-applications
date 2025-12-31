import { w as writable, g as get } from "./index.js";
import "./env.js";
import { QueryClient } from "@tanstack/query-core";
const DEFAULT_THEME = "dark";
function readInitialTheme() {
  return DEFAULT_THEME;
}
function createThemeStore() {
  const initialTheme = readInitialTheme();
  const store = writable(initialTheme);
  return {
    subscribe: store.subscribe,
    init: () => {
      get(store);
    },
    set(theme) {
      store.set(theme);
    },
    toggle() {
      store.update((prev) => {
        const next = prev === "dark" ? "light" : "dark";
        return next;
      });
    }
  };
}
createThemeStore();
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: true,
      refetchOnReconnect: true,
      retry: 1,
      staleTime: 3e4
    },
    mutations: {
      retry: 0
    }
  }
});
export {
  queryClient as q
};
