import { h as head, a as attr_class, s as store_get, u as unsubscribe_stores, b as stringify } from "../../../../chunks/index2.js";
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
    head("1lh6zvb", $$renderer2, ($$renderer3) => {
      $$renderer3.title(($$renderer4) => {
        $$renderer4.push(`<title>${escape_html(store_get($$store_subs ??= {}, "$t", t)("alerts.title"))} - Speak by Kraliki</title>`);
      });
    });
    $$renderer2.push(`<div class="container mx-auto p-6"><div class="flex items-center justify-between mb-8"><div><a href="/dashboard" class="text-sm text-muted-foreground hover:text-foreground mb-2 inline-block">&lt; ${escape_html(store_get($$store_subs ??= {}, "$t", t)("nav.dashboard"))}</a> <h1 class="text-3xl">${escape_html(store_get($$store_subs ??= {}, "$t", t)("alerts.title").toUpperCase())}</h1></div> <div class="flex gap-2"><button${attr_class(`brutal-btn text-sm ${stringify("brutal-btn-primary")}`)}>${escape_html(store_get($$store_subs ??= {}, "$t", t)("common.all").toUpperCase())}</button> <button${attr_class(`brutal-btn text-sm ${stringify("")}`)}>${escape_html(store_get($$store_subs ??= {}, "$t", t)("alerts.unread").toUpperCase())}</button></div></div> `);
    {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<div class="text-center py-12"><span class="animate-pulse">${escape_html(store_get($$store_subs ??= {}, "$t", t)("common.loading").toUpperCase())}</span></div>`);
    }
    $$renderer2.push(`<!--]--></div>`);
    if ($$store_subs) unsubscribe_stores($$store_subs);
  });
}
export {
  _page as default
};
