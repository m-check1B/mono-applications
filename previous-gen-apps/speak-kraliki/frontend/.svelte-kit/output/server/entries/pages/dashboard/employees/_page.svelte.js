import { h as head, s as store_get, e as ensure_array_like, u as unsubscribe_stores } from "../../../../chunks/index2.js";
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
    let departments = [];
    let departmentFilter = "";
    head("poswkx", $$renderer2, ($$renderer3) => {
      $$renderer3.title(($$renderer4) => {
        $$renderer4.push(`<title>${escape_html(store_get($$store_subs ??= {}, "$t", t)("employees.title"))} - Speak by Kraliki</title>`);
      });
    });
    $$renderer2.push(`<div class="container mx-auto p-6"><div class="flex items-center justify-between mb-8"><div><a href="/dashboard" class="text-sm text-muted-foreground hover:text-foreground mb-2 inline-block">&lt; ${escape_html(store_get($$store_subs ??= {}, "$t", t)("nav.dashboard"))}</a> <h1 class="text-3xl">${escape_html(store_get($$store_subs ??= {}, "$t", t)("employees.title").toUpperCase())}</h1></div> <div class="flex gap-2"><button class="brutal-btn">${escape_html(store_get($$store_subs ??= {}, "$t", t)("employees.import").toUpperCase())}</button> <button class="brutal-btn brutal-btn-primary">${escape_html(store_get($$store_subs ??= {}, "$t", t)("employees.add").toUpperCase())}</button></div></div> `);
    if (departments.length > 0) {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<div class="mb-6">`);
      $$renderer2.select({ value: departmentFilter, class: "brutal-input" }, ($$renderer3) => {
        $$renderer3.option({ value: "" }, ($$renderer4) => {
          $$renderer4.push(`${escape_html(store_get($$store_subs ??= {}, "$t", t)("common.all"))} ${escape_html(store_get($$store_subs ??= {}, "$t", t)("employees.department"))}`);
        });
        $$renderer3.push(`<!--[-->`);
        const each_array = ensure_array_like(departments);
        for (let $$index = 0, $$length = each_array.length; $$index < $$length; $$index++) {
          let dept = each_array[$$index];
          $$renderer3.option({ value: dept.id }, ($$renderer4) => {
            $$renderer4.push(`${escape_html(dept.name)}`);
          });
        }
        $$renderer3.push(`<!--]-->`);
      });
      $$renderer2.push(`</div>`);
    } else {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--> `);
    {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<div class="text-center py-12"><span class="animate-pulse">${escape_html(store_get($$store_subs ??= {}, "$t", t)("common.loading").toUpperCase())}</span></div>`);
    }
    $$renderer2.push(`<!--]--></div> `);
    {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--> `);
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
