import { g as sanitize_props, j as spread_props, s as slot, c as attr, e as ensure_array_like } from "../../../../chunks/index2.js";
import { c as createQuery, e as fetchCompanies } from "../../../../chunks/calls.js";
import "../../../../chunks/auth2.js";
import "../../../../chunks/queryClient.js";
import { C as Cloud_upload } from "../../../../chunks/cloud-upload.js";
import { I as Icon } from "../../../../chunks/Icon.js";
import { e as escape_html } from "../../../../chunks/escaping.js";
function Building_2($$renderer, $$props) {
  const $$sanitized_props = sanitize_props($$props);
  const iconNode = [
    ["path", { "d": "M6 22V4a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v18Z" }],
    ["path", { "d": "M6 12H4a2 2 0 0 0-2 2v6a2 2 0 0 0 2 2h2" }],
    ["path", { "d": "M18 9h2a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2h-2" }],
    ["path", { "d": "M10 6h4" }],
    ["path", { "d": "M10 10h4" }],
    ["path", { "d": "M10 14h4" }],
    ["path", { "d": "M10 18h4" }]
  ];
  Icon($$renderer, spread_props([
    { name: "building-2" },
    $$sanitized_props,
    {
      /**
       * @component @name Building2
       * @description Lucide SVG icon component, renders SVG Element with children.
       *
       * @preview ![img](data:image/svg+xml;base64,PHN2ZyAgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIgogIHdpZHRoPSIyNCIKICBoZWlnaHQ9IjI0IgogIHZpZXdCb3g9IjAgMCAyNCAyNCIKICBmaWxsPSJub25lIgogIHN0cm9rZT0iIzAwMCIgc3R5bGU9ImJhY2tncm91bmQtY29sb3I6ICNmZmY7IGJvcmRlci1yYWRpdXM6IDJweCIKICBzdHJva2Utd2lkdGg9IjIiCiAgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIgogIHN0cm9rZS1saW5lam9pbj0icm91bmQiCj4KICA8cGF0aCBkPSJNNiAyMlY0YTIgMiAwIDAgMSAyLTJoOGEyIDIgMCAwIDEgMiAydjE4WiIgLz4KICA8cGF0aCBkPSJNNiAxMkg0YTIgMiAwIDAgMC0yIDJ2NmEyIDIgMCAwIDAgMiAyaDIiIC8+CiAgPHBhdGggZD0iTTE4IDloMmEyIDIgMCAwIDEgMiAydjlhMiAyIDAgMCAxLTIgMmgtMiIgLz4KICA8cGF0aCBkPSJNMTAgNmg0IiAvPgogIDxwYXRoIGQ9Ik0xMCAxMGg0IiAvPgogIDxwYXRoIGQ9Ik0xMCAxNGg0IiAvPgogIDxwYXRoIGQ9Ik0xMCAxOGg0IiAvPgo8L3N2Zz4K) - https://lucide.dev/icons/building-2
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
function _page($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    const companiesQuery = createQuery({
      queryKey: ["companies"],
      queryFn: fetchCompanies,
      staleTime: 3e4
    });
    let companies = [];
    let isLoading = false;
    let errorMessage = null;
    companiesQuery.subscribe((result) => {
      companies = result.data ?? [];
      isLoading = result.isPending;
      errorMessage = result.isError ? result.error?.message ?? "Failed to load companies." : null;
    });
    $$renderer2.push(`<section class="space-y-6"><header class="flex flex-col gap-3 md:flex-row md:items-center md:justify-between"><div class="space-y-1"><h1 class="text-2xl font-semibold text-text-primary">Target Companies</h1> <p class="text-sm text-text-muted">Centralize lead lists, sync CRM exports, and monitor outbound status in one responsive surface.</p></div> <button class="btn btn-primary"${attr("disabled", isLoading, true)}>`);
    Cloud_upload($$renderer2, { class: "size-4" });
    $$renderer2.push(`<!----> Import CSV</button> <input type="file" accept=".csv" class="hidden"/></header> `);
    {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--> `);
    if (errorMessage) {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<div class="rounded-lg border border-error/40 bg-error/10 px-3 py-2 text-sm text-error">${escape_html(errorMessage)} <button class="ml-2 text-primary underline" type="button">Retry</button></div>`);
    } else {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--> `);
    if (isLoading && !companies.length) {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<p class="text-xs text-text-muted">Loading companies…</p>`);
    } else {
      $$renderer2.push("<!--[!-->");
      if (companies.length === 0) {
        $$renderer2.push("<!--[-->");
        $$renderer2.push(`<p class="text-sm text-text-secondary">No companies found.</p>`);
      } else {
        $$renderer2.push("<!--[!-->");
        $$renderer2.push(`<div class="grid gap-3"><!--[-->`);
        const each_array = ensure_array_like(companies);
        for (let $$index = 0, $$length = each_array.length; $$index < $$length; $$index++) {
          let company = each_array[$$index];
          $$renderer2.push(`<article class="card flex items-center justify-between bg-secondary/80"><div class="flex items-center gap-3 text-text-primary">`);
          Building_2($$renderer2, { class: "size-5" });
          $$renderer2.push(`<!----> <div><p class="text-sm font-semibold">${escape_html(company.name)}</p> <p class="text-xs text-text-muted">${escape_html(company.phone)}</p></div></div> <span class="text-xs text-text-muted uppercase tracking-wide">${escape_html(company.status ?? "Pending")}</span></article>`);
        }
        $$renderer2.push(`<!--]--></div>`);
      }
      $$renderer2.push(`<!--]-->`);
    }
    $$renderer2.push(`<!--]--></section>`);
  });
}
export {
  _page as default
};
