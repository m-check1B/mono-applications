import "clsx";
import { d as disableTransitions, t as themeColors, a as darkClassNames, l as lightClassNames, m as modeStorageKey, b as themeStorageKey } from "../../chunks/notifications.js";
import { b as bind_props, h as head } from "../../chunks/index2.js";
import { U as fallback } from "../../chunks/utils2.js";
import { a as attr } from "../../chunks/attributes.js";
import { h as html } from "../../chunks/html.js";
import "../../chunks/auth2.js";
import { w as writable } from "../../chunks/index.js";
import "../../chunks/tasks.js";
import "@sveltejs/kit/internal";
import "../../chunks/exports.js";
import "../../chunks/utils.js";
import "@sveltejs/kit/internal/server";
import "../../chunks/state.svelte.js";
function defineConfig(config) {
  return config;
}
function setInitialMode({ defaultMode = "system", themeColors: themeColors2, darkClassNames: darkClassNames2 = ["dark"], lightClassNames: lightClassNames2 = [], defaultTheme = "", modeStorageKey: modeStorageKey2 = "mode-watcher-mode", themeStorageKey: themeStorageKey2 = "mode-watcher-theme" }) {
  const rootEl = document.documentElement;
  const mode = localStorage.getItem(modeStorageKey2) || defaultMode;
  const theme = localStorage.getItem(themeStorageKey2) || defaultTheme;
  const light = mode === "light" || mode === "system" && window.matchMedia("(prefers-color-scheme: light)").matches;
  if (light) {
    if (darkClassNames2.length)
      rootEl.classList.remove(...darkClassNames2);
    if (lightClassNames2.length)
      rootEl.classList.add(...lightClassNames2);
  } else {
    if (lightClassNames2.length)
      rootEl.classList.remove(...lightClassNames2);
    if (darkClassNames2.length)
      rootEl.classList.add(...darkClassNames2);
  }
  rootEl.style.colorScheme = light ? "light" : "dark";
  if (themeColors2) {
    const themeMetaEl = document.querySelector('meta[name="theme-color"]');
    if (themeMetaEl) {
      themeMetaEl.setAttribute("content", mode === "light" ? themeColors2.light : themeColors2.dark);
    }
  }
  if (theme) {
    rootEl.setAttribute("data-theme", theme);
    localStorage.setItem(themeStorageKey2, theme);
  }
  localStorage.setItem(modeStorageKey2, mode);
}
function Mode_watcher_lite($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    let themeColors2 = fallback($$props["themeColors"], () => void 0, true);
    if (themeColors2) {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<meta name="theme-color"${attr("content", themeColors2.dark)}/>`);
    } else {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]-->`);
    bind_props($$props, { themeColors: themeColors2 });
  });
}
function Mode_watcher_full($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    let trueNonce = fallback($$props["trueNonce"], "");
    let initConfig = $$props["initConfig"];
    let themeColors2 = fallback($$props["themeColors"], () => void 0, true);
    head("kme15g", $$renderer2, ($$renderer3) => {
      if (themeColors2) {
        $$renderer3.push("<!--[-->");
        $$renderer3.push(`<meta name="theme-color"${attr("content", themeColors2.dark)}/>`);
      } else {
        $$renderer3.push("<!--[!-->");
      }
      $$renderer3.push(`<!--]--> ${html(`<script${trueNonce ? ` nonce=${trueNonce}` : ""}>(` + setInitialMode.toString() + `)(` + JSON.stringify(initConfig) + `);<\/script>`)}`);
    });
    bind_props($$props, { trueNonce, initConfig, themeColors: themeColors2 });
  });
}
function Mode_watcher($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    let trueNonce;
    let track = fallback($$props["track"], true);
    let defaultMode = fallback($$props["defaultMode"], "system");
    let themeColors$1 = fallback($$props["themeColors"], () => void 0, true);
    let disableTransitions$1 = fallback($$props["disableTransitions"], true);
    let darkClassNames$1 = fallback($$props["darkClassNames"], () => ["dark"], true);
    let lightClassNames$1 = fallback($$props["lightClassNames"], () => [], true);
    let defaultTheme = fallback($$props["defaultTheme"], "");
    let nonce = fallback($$props["nonce"], "");
    let themeStorageKey$1 = fallback($$props["themeStorageKey"], "mode-watcher-theme");
    let modeStorageKey$1 = fallback($$props["modeStorageKey"], "mode-watcher-mode");
    let disableHeadScriptInjection = fallback($$props["disableHeadScriptInjection"], false);
    const initConfig = defineConfig({
      defaultMode,
      themeColors: themeColors$1,
      darkClassNames: darkClassNames$1,
      lightClassNames: lightClassNames$1,
      defaultTheme,
      modeStorageKey: modeStorageKey$1,
      themeStorageKey: themeStorageKey$1
    });
    disableTransitions.set(disableTransitions$1);
    themeColors.set(themeColors$1);
    darkClassNames.set(darkClassNames$1);
    lightClassNames.set(lightClassNames$1);
    modeStorageKey.set(modeStorageKey$1);
    themeStorageKey.set(themeStorageKey$1);
    trueNonce = typeof window === "undefined" ? nonce : "";
    if (disableHeadScriptInjection) {
      $$renderer2.push("<!--[-->");
      Mode_watcher_lite($$renderer2, { themeColors: themeColors$1 });
    } else {
      $$renderer2.push("<!--[!-->");
      Mode_watcher_full($$renderer2, { trueNonce, initConfig, themeColors: themeColors$1 });
    }
    $$renderer2.push(`<!--]-->`);
    bind_props($$props, {
      track,
      defaultMode,
      themeColors: themeColors$1,
      disableTransitions: disableTransitions$1,
      darkClassNames: darkClassNames$1,
      lightClassNames: lightClassNames$1,
      defaultTheme,
      nonce,
      themeStorageKey: themeStorageKey$1,
      modeStorageKey: modeStorageKey$1,
      disableHeadScriptInjection
    });
  });
}
const initialState = {
  isConnected: false,
  isConnecting: false,
  error: null,
  lastMessage: null
};
function createWebSocketStore() {
  const { subscribe, set, update } = writable(initialState);
  function connect() {
    return;
  }
  function disconnect() {
    update((s) => ({ ...s, isConnected: false, isConnecting: false }));
  }
  function sendMessage(type, data) {
    return false;
  }
  return {
    subscribe,
    connect,
    disconnect,
    sendMessage,
    ping: () => sendMessage()
  };
}
createWebSocketStore();
function PWAInstallPrompt($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]-->`);
  });
}
function _layout($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    let { children } = $$props;
    Mode_watcher($$renderer2, {});
    $$renderer2.push(`<!----> <div class="min-h-screen flex flex-col bg-background bg-grid-pattern text-foreground font-mono"><div class="scanline"></div> `);
    {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--> <div class="flex-1">`);
    children($$renderer2);
    $$renderer2.push(`<!----></div> <footer class="border-t border-border py-4 px-6 text-center text-sm text-muted-foreground"><div class="flex items-center justify-center gap-4"><span>© 2026 Verduona s.r.o.</span> <a href="/privacy" class="hover:text-foreground transition-colors">Privacy</a></div></footer> `);
    PWAInstallPrompt($$renderer2);
    $$renderer2.push(`<!----></div>`);
  });
}
export {
  _layout as default
};
