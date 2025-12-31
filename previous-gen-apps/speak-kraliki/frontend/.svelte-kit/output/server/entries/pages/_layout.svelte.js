import { s as store_get, a as attr_class, b as stringify, u as unsubscribe_stores } from "../../chunks/index2.js";
import { p as page } from "../../chunks/stores.js";
import "@sveltejs/kit/internal";
import "../../chunks/exports.js";
import "../../chunks/utils.js";
import { V as escape_html } from "../../chunks/context.js";
import "clsx";
import "@sveltejs/kit/internal/server";
import "../../chunks/state.svelte.js";
import { c as currentUser, i as isAuthenticated } from "../../chunks/auth.js";
import { w as writable } from "../../chunks/index.js";
import { l as locale, t } from "../../chunks/index3.js";
function createThemeStore() {
  const initialTheme = "dark";
  const { subscribe, set, update } = writable(initialTheme);
  return {
    subscribe,
    toggle: () => update((theme) => {
      const next = theme === "light" ? "dark" : "light";
      return next;
    }),
    set: (theme) => {
      set(theme);
    }
  };
}
const themeStore = createThemeStore();
function OnboardingModal($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]-->`);
  });
}
function _layout($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    var $$store_subs;
    let { children } = $$props;
    const isVoiceInterface = store_get($$store_subs ??= {}, "$page", page).url.pathname.startsWith("/v/");
    const isAuthPage = store_get($$store_subs ??= {}, "$page", page).url.pathname === "/login" || store_get($$store_subs ??= {}, "$page", page).url.pathname === "/register" || store_get($$store_subs ??= {}, "$page", page).url.pathname === "/";
    const isDashboard = store_get($$store_subs ??= {}, "$page", page).url.pathname.startsWith("/dashboard");
    $$renderer2.push(`<div class="min-h-screen bg-background bg-grid-pattern"><div class="scanline"></div> `);
    if (!isVoiceInterface && !isAuthPage) {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<nav class="border-b-2 border-foreground bg-card"><div class="container mx-auto px-4 py-3 flex items-center justify-between"><a href="/dashboard" class="flex items-center gap-2"><span class="text-terminal-green text-2xl">///</span> <span class="font-display text-lg">SPEAK BY KRALIKI</span> `);
      if (store_get($$store_subs ??= {}, "$currentUser", currentUser)?.company_name) {
        $$renderer2.push("<!--[-->");
        $$renderer2.push(`<span class="text-muted text-sm ml-2">| ${escape_html(store_get($$store_subs ??= {}, "$currentUser", currentUser).company_name)}</span>`);
      } else {
        $$renderer2.push("<!--[!-->");
      }
      $$renderer2.push(`<!--]--></a> <div class="flex items-center gap-4"><button class="brutal-btn text-xs py-1 px-2" title="Toggle theme">${escape_html(store_get($$store_subs ??= {}, "$themeStore", themeStore) === "dark" ? "☀️" : "🌙")}</button> `);
      if (store_get($$store_subs ??= {}, "$isAuthenticated", isAuthenticated)) {
        $$renderer2.push("<!--[-->");
        $$renderer2.push(`<span class="text-sm text-muted hidden md:inline">${escape_html(store_get($$store_subs ??= {}, "$currentUser", currentUser)?.first_name)} ${escape_html(store_get($$store_subs ??= {}, "$currentUser", currentUser)?.last_name)}</span> <button class="brutal-btn text-xs py-1 px-2" title="Switch language">${escape_html(store_get($$store_subs ??= {}, "$locale", locale).toUpperCase())}</button> <button class="brutal-btn brutal-btn-secondary text-sm">${escape_html(store_get($$store_subs ??= {}, "$t", t)("nav.logout").toUpperCase())}</button>`);
      } else {
        $$renderer2.push("<!--[!-->");
        $$renderer2.push(`<a href="/login" class="brutal-btn text-sm">${escape_html(store_get($$store_subs ??= {}, "$t", t)("auth.login").toUpperCase())}</a>`);
      }
      $$renderer2.push(`<!--]--></div></div> `);
      if (isDashboard) {
        $$renderer2.push("<!--[-->");
        $$renderer2.push(`<div class="border-t border-foreground/30 bg-void"><div class="container mx-auto px-4 py-2 flex gap-4 overflow-x-auto"><a href="/dashboard"${attr_class(`text-sm whitespace-nowrap ${stringify(store_get($$store_subs ??= {}, "$page", page).url.pathname === "/dashboard" ? "text-terminal-green" : "text-muted-foreground hover:text-foreground")}`)}>${escape_html(store_get($$store_subs ??= {}, "$t", t)("nav.dashboard").toUpperCase())}</a> <a href="/dashboard/surveys"${attr_class(`text-sm whitespace-nowrap ${stringify(store_get($$store_subs ??= {}, "$page", page).url.pathname.startsWith("/dashboard/surveys") ? "text-terminal-green" : "text-muted-foreground hover:text-foreground")}`)}>${escape_html(store_get($$store_subs ??= {}, "$t", t)("nav.surveys").toUpperCase())}</a> <a href="/dashboard/alerts"${attr_class(`text-sm whitespace-nowrap ${stringify(store_get($$store_subs ??= {}, "$page", page).url.pathname.startsWith("/dashboard/alerts") ? "text-terminal-green" : "text-muted-foreground hover:text-foreground")}`)}>${escape_html(store_get($$store_subs ??= {}, "$t", t)("nav.alerts").toUpperCase())}</a> <a href="/dashboard/actions"${attr_class(`text-sm whitespace-nowrap ${stringify(store_get($$store_subs ??= {}, "$page", page).url.pathname.startsWith("/dashboard/actions") ? "text-terminal-green" : "text-muted-foreground hover:text-foreground")}`)}>${escape_html(store_get($$store_subs ??= {}, "$t", t)("nav.actions").toUpperCase())}</a> <a href="/dashboard/employees"${attr_class(`text-sm whitespace-nowrap ${stringify(store_get($$store_subs ??= {}, "$page", page).url.pathname.startsWith("/dashboard/employees") ? "text-terminal-green" : "text-muted-foreground hover:text-foreground")}`)}>${escape_html(store_get($$store_subs ??= {}, "$t", t)("nav.employees").toUpperCase())}</a> <a href="/dashboard/settings"${attr_class(`text-sm whitespace-nowrap ${stringify(store_get($$store_subs ??= {}, "$page", page).url.pathname.startsWith("/dashboard/settings") ? "text-terminal-green" : "text-muted-foreground hover:text-foreground")}`)}>${escape_html(store_get($$store_subs ??= {}, "$t", t)("nav.settings").toUpperCase())}</a></div></div>`);
      } else {
        $$renderer2.push("<!--[!-->");
      }
      $$renderer2.push(`<!--]--></nav>`);
    } else {
      $$renderer2.push("<!--[!-->");
      if (!isVoiceInterface) {
        $$renderer2.push("<!--[-->");
        $$renderer2.push(`<nav class="border-b-2 border-foreground bg-card"><div class="container mx-auto px-4 py-3 flex items-center justify-between"><a href="/" class="flex items-center gap-2"><span class="text-terminal-green text-2xl">///</span> <span class="font-display text-lg">SPEAK BY KRALIKI</span></a> <button class="brutal-btn text-xs py-1 px-2" title="Switch language">${escape_html(store_get($$store_subs ??= {}, "$locale", locale).toUpperCase())}</button></div></nav>`);
      } else {
        $$renderer2.push("<!--[!-->");
      }
      $$renderer2.push(`<!--]-->`);
    }
    $$renderer2.push(`<!--]--> <main>`);
    children($$renderer2);
    $$renderer2.push(`<!----></main> `);
    if (!isVoiceInterface) {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<footer class="border-t border-foreground/20 py-4 px-6 text-center text-sm text-muted-foreground"><div class="flex flex-col sm:flex-row items-center justify-center gap-2 sm:gap-4"><span>© 2026 Verduona s.r.o.</span> <a href="/privacy" class="hover:text-foreground transition-colors">Privacy</a></div></footer>`);
    } else {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--> `);
    if (isDashboard && store_get($$store_subs ??= {}, "$isAuthenticated", isAuthenticated)) {
      $$renderer2.push("<!--[-->");
      OnboardingModal($$renderer2);
    } else {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--></div>`);
    if ($$store_subs) unsubscribe_stores($$store_subs);
  });
}
export {
  _layout as default
};
