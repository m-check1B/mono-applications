import { h as head, s as store_get, e as ensure_array_like, u as unsubscribe_stores } from "../../../chunks/index2.js";
import { e as escape_html } from "../../../chunks/escaping.js";
import "clsx";
import { b as ssr_context } from "../../../chunks/context.js";
import { w as writable } from "../../../chunks/index.js";
import { b as attr } from "../../../chunks/attributes.js";
function onDestroy(fn) {
  /** @type {SSRContext} */
  ssr_context.r.on_destroy(fn);
}
function Terminal_1($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    let { id } = $$props;
    onDestroy(() => {
    });
    $$renderer2.push(`<div class="terminal-wrapper svelte-maclc7"><div class="terminal-header svelte-maclc7"><div class="terminal-title svelte-maclc7"><span class="terminal-id svelte-maclc7">Terminal ${escape_html(id)}</span> <div class="status svelte-maclc7">`);
    {
      $$renderer2.push("<!--[!-->");
      $$renderer2.push(`<span class="status-dot offline svelte-maclc7"></span> <span>Disconnected</span>`);
    }
    $$renderer2.push(`<!--]--></div></div> <div class="actions svelte-maclc7"><button class="brutal-btn small">Reconnect</button> <button class="brutal-btn small danger svelte-maclc7">Kill</button></div></div> `);
    {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--> <div class="terminal-container svelte-maclc7"></div></div>`);
  });
}
function getInitialTerminals() {
  return [1];
}
function createTerminalStore() {
  const initial = getInitialTerminals();
  const { subscribe, set, update } = writable(initial);
  return {
    subscribe,
    add: (id) => update((n) => {
      const next = [...n, id];
      return next;
    }),
    remove: (id) => update((n) => {
      const next = n.filter((t) => t !== id);
      return next;
    }),
    set: (val) => {
      set(val);
    }
  };
}
const activeTerminals = createTerminalStore();
function _page($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    var $$store_subs;
    const MAX_TERMINALS = 4;
    head("1dhdpeh", $$renderer2, ($$renderer3) => {
      $$renderer3.title(($$renderer4) => {
        $$renderer4.push(`<title>Terminal - Kraliki Swarm</title>`);
      });
      $$renderer3.push(`<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/xterm@5.3.0/css/xterm.css"/>`);
    });
    $$renderer2.push(`<div class="terminal-page svelte-1dhdpeh"><div class="page-header svelte-1dhdpeh"><h2 class="svelte-1dhdpeh">Terminal</h2> <div class="controls svelte-1dhdpeh"><button class="brutal-btn"${attr("disabled", store_get($$store_subs ??= {}, "$activeTerminals", activeTerminals).length >= MAX_TERMINALS, true)}>+ Add Terminal (${escape_html(store_get($$store_subs ??= {}, "$activeTerminals", activeTerminals).length)}/4)</button></div></div> <div class="terminals-grid svelte-1dhdpeh"><!--[-->`);
    const each_array = ensure_array_like(store_get($$store_subs ??= {}, "$activeTerminals", activeTerminals));
    for (let $$index = 0, $$length = each_array.length; $$index < $$length; $$index++) {
      let id = each_array[$$index];
      $$renderer2.push(`<div class="terminal-slot svelte-1dhdpeh">`);
      Terminal_1($$renderer2, { id });
      $$renderer2.push(`<!----></div>`);
    }
    $$renderer2.push(`<!--]--></div> <div class="terminal-info svelte-1dhdpeh"><p class="svelte-1dhdpeh"><strong class="svelte-1dhdpeh">Status:</strong> Terminals are persistent. Navigating away will NOT close your sessions.</p> <p class="svelte-1dhdpeh"><strong class="svelte-1dhdpeh">Persistence:</strong> Use the "KILL" button to permanently end a session and its background process.</p> <p class="svelte-1dhdpeh"><strong class="svelte-1dhdpeh">Shortcuts:</strong> Ctrl+C (interrupt), Ctrl+D (exit), Ctrl+L (clear)</p> <p class="svelte-1dhdpeh"><strong class="svelte-1dhdpeh">Max terminals:</strong> 4</p></div></div>`);
    if ($$store_subs) unsubscribe_stores($$store_subs);
  });
}
export {
  _page as default
};
