import { h as head, s as store_get, a as attr_class, e as ensure_array_like, u as unsubscribe_stores } from "../../chunks/index2.js";
import { g as getContext } from "../../chunks/context.js";
import "clsx";
import "@sveltejs/kit/internal";
import "../../chunks/exports.js";
import "../../chunks/utils.js";
import "@sveltejs/kit/internal/server";
import "../../chunks/state.svelte.js";
import { w as workspaceMode } from "../../chunks/mode.js";
import { e as escape_html } from "../../chunks/escaping.js";
import { b as attr } from "../../chunks/attributes.js";
const getStores = () => {
  const stores$1 = getContext("__svelte__");
  return {
    /** @type {typeof page} */
    page: {
      subscribe: stores$1.page.subscribe
    },
    /** @type {typeof navigating} */
    navigating: {
      subscribe: stores$1.navigating.subscribe
    },
    /** @type {typeof updated} */
    updated: stores$1.updated
  };
};
const page = {
  subscribe(fn) {
    const store = getStores().page;
    return store.subscribe(fn);
  }
};
function _layout($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    var $$store_subs;
    let { data, children } = $$props;
    let clock = (/* @__PURE__ */ new Date()).toLocaleString();
    const navItems = [
      // TIER 1: Core Operations (daily use)
      { href: "/", label: "Overview", icon: "📊" },
      { href: "/comms", label: "Comms", icon: "📡" },
      { href: "/agents", label: "Agents", icon: "🤖" },
      { href: "/jobs", label: "Jobs", icon: "📋" },
      { href: "/health", label: "Health", icon: "💚" },
      // TIER 2: Intelligence (strategic work)
      { href: "/brain", label: "Brain", icon: "🧠" },
      { href: "/recall", label: "Recall", icon: "💾" },
      { href: "/insights", label: "Insights", icon: "💡" },
      { href: "/workflows", label: "Workflows", icon: "⚡" },
      // TIER 3: Management (configuration)
      { href: "/genomes", label: "Genomes", icon: "🧬" },
      { href: "/leaderboard", label: "Leaderboard", icon: "🏆" },
      // TIER 4: Advanced (debug/monitor)
      { href: "/see", label: "See", icon: "📹" },
      { href: "/costs", label: "Costs", icon: "💰" },
      { href: "/data", label: "Data", icon: "📁" },
      // TIER 5: Integrated Apps (separate products)
      { href: "/learn", label: "Learn", icon: "📚" },
      { href: "/apps", label: "Apps", icon: "📦" },
      { href: "/terminal", label: "Terminal", icon: "⌨️" },
      { href: "/notebook", label: "Notebook", icon: "📝" }
    ];
    head("12qhfyh", $$renderer2, ($$renderer3) => {
      $$renderer3.title(($$renderer4) => {
        $$renderer4.push(`<title>Kraliki Swarm</title>`);
      });
    });
    $$renderer2.push(`<div class="container"><header><div><h1 class="glitch">Kraliki // Swarm Control</h1> <p class="subtitle">AI Swarm Command Center</p></div> <div style="display: flex; gap: 16px; align-items: center;">`);
    if (store_get($$store_subs ??= {}, "$workspaceMode", workspaceMode) !== "normal") {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<span${attr_class("mode-indicator svelte-12qhfyh", void 0, {
        "dev": store_get($$store_subs ??= {}, "$workspaceMode", workspaceMode) === "dev",
        "readonly": store_get($$store_subs ??= {}, "$workspaceMode", workspaceMode) === "readonly"
      })}>${escape_html(store_get($$store_subs ??= {}, "$workspaceMode", workspaceMode).toUpperCase())}</span>`);
    } else {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--> <button class="brutal-btn" style="padding: 6px 10px; font-size: 16px;">${escape_html("☀️")}</button> `);
    if (data.user) {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<a href="/settings" class="user-badge" title="Settings"><span class="user-avatar">👤</span> <span class="user-name">${escape_html(data.user.isLocal ? "LOCAL_ROOT" : data.user.name.toUpperCase())}</span></a>`);
    } else {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--> <span class="updated">${escape_html(clock)}</span></div></header> <nav class="nav-tabs svelte-12qhfyh"><!--[-->`);
    const each_array = ensure_array_like(navItems);
    for (let $$index = 0, $$length = each_array.length; $$index < $$length; $$index++) {
      let item = each_array[$$index];
      $$renderer2.push(`<a${attr("href", item.href)}${attr_class("nav-tab svelte-12qhfyh", void 0, {
        "active": store_get($$store_subs ??= {}, "$page", page).url.pathname === item.href
      })}><span class="nav-icon svelte-12qhfyh">${escape_html(item.icon)}</span> <span class="nav-label svelte-12qhfyh">${escape_html(item.label)}</span></a>`);
    }
    $$renderer2.push(`<!--]--></nav> `);
    children($$renderer2);
    $$renderer2.push(`<!----></div>`);
    if ($$store_subs) unsubscribe_stores($$store_subs);
  });
}
export {
  _layout as default
};
