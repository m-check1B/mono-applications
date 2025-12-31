import "clsx";
import { s as setContext } from "../../chunks/context.js";
import "../../chunks/auth2.js";
import { q as queryClient } from "../../chunks/queryClient.js";
import { A as APP_CONFIG_KEY } from "../../chunks/app.js";
import { o as onDestroy } from "../../chunks/index-server.js";
import { w as writable } from "../../chunks/index.js";
import "@sveltejs/kit/internal";
import "../../chunks/exports.js";
import "../../chunks/utils.js";
import "@sveltejs/kit/internal/server";
import "../../chunks/state.svelte.js";
import { s as slot, b as bind_props } from "../../chunks/index2.js";
import { QueryClient } from "@tanstack/query-core";
import { s as setQueryClientContext } from "../../chunks/context2.js";
import { f as fallback } from "../../chunks/utils3.js";
function QueryClientProvider($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    let client = fallback($$props["client"], () => new QueryClient(), true);
    setQueryClientContext(client);
    onDestroy(() => {
      client.unmount();
    });
    $$renderer2.push(`<!--[-->`);
    slot($$renderer2, $$props, "default", {});
    $$renderer2.push(`<!--]-->`);
    bind_props($$props, { client });
  });
}
function createErrorStore() {
  const { subscribe, update } = writable([]);
  return {
    subscribe,
    addError: (error) => {
      update((errors) => [
        ...errors,
        {
          ...error,
          id: crypto.randomUUID(),
          timestamp: /* @__PURE__ */ new Date()
        }
      ]);
    },
    clearError: (id) => {
      update((errors) => errors.filter((e) => e.id !== id));
    },
    clearAll: () => {
      update(() => []);
    }
  };
}
createErrorStore();
function ErrorBoundary($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    let { children } = $$props;
    onDestroy(() => {
    });
    {
      $$renderer2.push("<!--[!-->");
      children($$renderer2);
      $$renderer2.push(`<!---->`);
    }
    $$renderer2.push(`<!--]-->`);
  });
}
function _layout($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    const { children, data } = $$props;
    const config = data.config;
    setContext(APP_CONFIG_KEY, config);
    QueryClientProvider($$renderer2, {
      client: queryClient,
      children: ($$renderer3) => {
        $$renderer3.push(`<div class="min-h-screen bg-background bg-grid-pattern text-foreground font-mono"><div class="scanline"></div> `);
        ErrorBoundary($$renderer3, {
          children: ($$renderer4) => {
            children($$renderer4);
            $$renderer4.push(`<!---->`);
          }
        });
        $$renderer3.push(`<!----></div>`);
      },
      $$slots: { default: true }
    });
  });
}
export {
  _layout as default
};
