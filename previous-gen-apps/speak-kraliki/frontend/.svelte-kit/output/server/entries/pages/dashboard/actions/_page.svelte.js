import { h as head, s as store_get, e as ensure_array_like, a as attr_class, u as unsubscribe_stores, b as stringify } from "../../../../chunks/index2.js";
import "@sveltejs/kit/internal";
import "../../../../chunks/exports.js";
import "../../../../chunks/utils.js";
import { V as escape_html } from "../../../../chunks/context.js";
import "clsx";
import "@sveltejs/kit/internal/server";
import "../../../../chunks/state.svelte.js";
import "../../../../chunks/auth.js";
import { t } from "../../../../chunks/index3.js";
function _page($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    var $$store_subs;
    let statusFilter = "all";
    function getStatusLabel(status) {
      const labels = {
        new: store_get($$store_subs ??= {}, "$t", t)("status.new"),
        heard: store_get($$store_subs ??= {}, "$t", t)("status.heard"),
        in_progress: store_get($$store_subs ??= {}, "$t", t)("status.inProgress"),
        resolved: store_get($$store_subs ??= {}, "$t", t)("status.resolved")
      };
      return labels[status] || status;
    }
    head("m5zg27", $$renderer2, ($$renderer3) => {
      $$renderer3.title(($$renderer4) => {
        $$renderer4.push(`<title>${escape_html(store_get($$store_subs ??= {}, "$t", t)("actions.title"))} - Speak by Kraliki</title>`);
      });
    });
    $$renderer2.push(`<div class="container mx-auto p-6"><div class="flex items-center justify-between mb-8"><div><a href="/dashboard" class="text-sm text-muted-foreground hover:text-foreground mb-2 inline-block">&lt; ${escape_html(store_get($$store_subs ??= {}, "$t", t)("nav.dashboard"))}</a> <h1 class="text-3xl">${escape_html(store_get($$store_subs ??= {}, "$t", t)("actions.title").toUpperCase())}</h1> <p class="text-muted-foreground text-sm mt-1">Action Loop - ${escape_html(store_get($$store_subs ??= {}, "$t", t)("actionLoop.title"))}</p></div> <button class="brutal-btn brutal-btn-primary">${escape_html(store_get($$store_subs ??= {}, "$t", t)("actions.create").toUpperCase())}</button></div> <div class="flex gap-2 mb-6 flex-wrap"><!--[-->`);
    const each_array = ensure_array_like(["all", "new", "heard", "in_progress", "resolved"]);
    for (let $$index = 0, $$length = each_array.length; $$index < $$length; $$index++) {
      let status = each_array[$$index];
      $$renderer2.push(`<button${attr_class(`brutal-btn text-sm ${stringify(statusFilter === status ? "brutal-btn-primary" : "")}`)}>${escape_html(status === "all" ? store_get($$store_subs ??= {}, "$t", t)("common.all").toUpperCase() : getStatusLabel(status).toUpperCase())}</button>`);
    }
    $$renderer2.push(`<!--]--></div> `);
    {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<div class="text-center py-12"><span class="animate-pulse">${escape_html(store_get($$store_subs ??= {}, "$t", t)("common.loading").toUpperCase())}</span></div>`);
    }
    $$renderer2.push(`<!--]--></div> `);
    {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]-->`);
    if ($$store_subs) unsubscribe_stores($$store_subs);
  });
}
export {
  _page as default
};
