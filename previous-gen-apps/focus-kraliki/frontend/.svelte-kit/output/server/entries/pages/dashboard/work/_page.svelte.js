import { s as sanitize_props, a as spread_props, c as slot, d as store_get, g as ensure_array_like, u as unsubscribe_stores, e as attr_class } from "../../../../chunks/index2.js";
import { X, T as Trash_2, P as Plus, k as knowledgeStore, C as Calendar } from "../../../../chunks/knowledge.js";
import { t as tasksStore } from "../../../../chunks/tasks.js";
import { e as escape_html } from "../../../../chunks/escaping.js";
import { a as attr } from "../../../../chunks/attributes.js";
import { I as Icon } from "../../../../chunks/Icon.js";
import { S as Settings } from "../../../../chunks/settings.js";
import { S as Sparkles } from "../../../../chunks/sparkles.js";
function Book_open($$renderer, $$props) {
  const $$sanitized_props = sanitize_props($$props);
  const iconNode = [
    ["path", { "d": "M12 7v14" }],
    [
      "path",
      {
        "d": "M3 18a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1h5a4 4 0 0 1 4 4 4 4 0 0 1 4-4h5a1 1 0 0 1 1 1v13a1 1 0 0 1-1 1h-6a3 3 0 0 0-3 3 3 3 0 0 0-3-3z"
      }
    ]
  ];
  Icon($$renderer, spread_props([
    { name: "book-open" },
    $$sanitized_props,
    {
      /**
       * @component @name BookOpen
       * @description Lucide SVG icon component, renders SVG Element with children.
       *
       * @preview ![img](data:image/svg+xml;base64,PHN2ZyAgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIgogIHdpZHRoPSIyNCIKICBoZWlnaHQ9IjI0IgogIHZpZXdCb3g9IjAgMCAyNCAyNCIKICBmaWxsPSJub25lIgogIHN0cm9rZT0iIzAwMCIgc3R5bGU9ImJhY2tncm91bmQtY29sb3I6ICNmZmY7IGJvcmRlci1yYWRpdXM6IDJweCIKICBzdHJva2Utd2lkdGg9IjIiCiAgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIgogIHN0cm9rZS1saW5lam9pbj0icm91bmQiCj4KICA8cGF0aCBkPSJNMTIgN3YxNCIgLz4KICA8cGF0aCBkPSJNMyAxOGExIDEgMCAwIDEtMS0xVjRhMSAxIDAgMCAxIDEtMWg1YTQgNCAwIDAgMSA0IDQgNCA0IDAgMCAxIDQtNGg1YTEgMSAwIDAgMSAxIDF2MTNhMSAxIDAgMCAxLTEgMWgtNmEzIDMgMCAwIDAtMyAzIDMgMyAwIDAgMC0zLTN6IiAvPgo8L3N2Zz4K) - https://lucide.dev/icons/book-open
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
function Clipboard($$renderer, $$props) {
  const $$sanitized_props = sanitize_props($$props);
  const iconNode = [
    [
      "rect",
      {
        "width": "8",
        "height": "4",
        "x": "8",
        "y": "2",
        "rx": "1",
        "ry": "1"
      }
    ],
    [
      "path",
      {
        "d": "M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"
      }
    ]
  ];
  Icon($$renderer, spread_props([
    { name: "clipboard" },
    $$sanitized_props,
    {
      /**
       * @component @name Clipboard
       * @description Lucide SVG icon component, renders SVG Element with children.
       *
       * @preview ![img](data:image/svg+xml;base64,PHN2ZyAgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIgogIHdpZHRoPSIyNCIKICBoZWlnaHQ9IjI0IgogIHZpZXdCb3g9IjAgMCAyNCAyNCIKICBmaWxsPSJub25lIgogIHN0cm9rZT0iIzAwMCIgc3R5bGU9ImJhY2tncm91bmQtY29sb3I6ICNmZmY7IGJvcmRlci1yYWRpdXM6IDJweCIKICBzdHJva2Utd2lkdGg9IjIiCiAgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIgogIHN0cm9rZS1saW5lam9pbj0icm91bmQiCj4KICA8cmVjdCB3aWR0aD0iOCIgaGVpZ2h0PSI0IiB4PSI4IiB5PSIyIiByeD0iMSIgcnk9IjEiIC8+CiAgPHBhdGggZD0iTTE2IDRoMmEyIDIgMCAwIDEgMiAydjE0YTIgMiAwIDAgMS0yIDJINmEyIDIgMCAwIDEtMi0yVjZhMiAyIDAgMCAxIDItMmgyIiAvPgo8L3N2Zz4K) - https://lucide.dev/icons/clipboard
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
function Square_check_big($$renderer, $$props) {
  const $$sanitized_props = sanitize_props($$props);
  const iconNode = [
    [
      "path",
      {
        "d": "M21 10.5V19a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h12.5"
      }
    ],
    ["path", { "d": "m9 11 3 3L22 4" }]
  ];
  Icon($$renderer, spread_props([
    { name: "square-check-big" },
    $$sanitized_props,
    {
      /**
       * @component @name SquareCheckBig
       * @description Lucide SVG icon component, renders SVG Element with children.
       *
       * @preview ![img](data:image/svg+xml;base64,PHN2ZyAgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIgogIHdpZHRoPSIyNCIKICBoZWlnaHQ9IjI0IgogIHZpZXdCb3g9IjAgMCAyNCAyNCIKICBmaWxsPSJub25lIgogIHN0cm9rZT0iIzAwMCIgc3R5bGU9ImJhY2tncm91bmQtY29sb3I6ICNmZmY7IGJvcmRlci1yYWRpdXM6IDJweCIKICBzdHJva2Utd2lkdGg9IjIiCiAgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIgogIHN0cm9rZS1saW5lam9pbj0icm91bmQiCj4KICA8cGF0aCBkPSJNMjEgMTAuNVYxOWEyIDIgMCAwIDEtMiAySDVhMiAyIDAgMCAxLTItMlY1YTIgMiAwIDAgMSAyLTJoMTIuNSIgLz4KICA8cGF0aCBkPSJtOSAxMSAzIDNMMjIgNCIgLz4KPC9zdmc+Cg==) - https://lucide.dev/icons/square-check-big
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
function ManageTypesDialog($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    var $$store_subs;
    let { open = false } = $$props;
    let itemTypes = store_get($$store_subs ??= {}, "$knowledgeStore", knowledgeStore).itemTypes;
    const defaultTypes = ["Ideas", "Notes", "Tasks", "Plans"];
    if (open) {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<div class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"><div class="bg-card border border-border rounded-lg max-w-2xl w-full p-6"><div class="flex items-center justify-between mb-6"><h2 class="text-2xl font-bold">Manage Knowledge Types</h2> <button class="p-2 hover:bg-accent rounded-md transition-colors">`);
      X($$renderer2, { class: "w-5 h-5" });
      $$renderer2.push(`<!----></button></div> <div class="space-y-4"><div class="space-y-2"><!--[-->`);
      const each_array = ensure_array_like(itemTypes);
      for (let $$index = 0, $$length = each_array.length; $$index < $$length; $$index++) {
        let type = each_array[$$index];
        $$renderer2.push(`<div class="bg-background border border-border rounded-lg p-4 flex items-center justify-between"><div class="flex items-center gap-3"><span class="px-3 py-1 rounded-full bg-accent text-accent-foreground border border-border">${escape_html(type.name)}</span></div> `);
        if (!defaultTypes.includes(type.name)) {
          $$renderer2.push("<!--[-->");
          $$renderer2.push(`<button class="p-2 text-muted-foreground hover:text-destructive hover:bg-destructive/10 rounded-md transition-colors">`);
          Trash_2($$renderer2, { class: "w-4 h-4" });
          $$renderer2.push(`<!----></button>`);
        } else {
          $$renderer2.push("<!--[!-->");
        }
        $$renderer2.push(`<!--]--></div>`);
      }
      $$renderer2.push(`<!--]--></div> `);
      {
        $$renderer2.push("<!--[-->");
        $$renderer2.push(`<button class="w-full flex items-center justify-center gap-2 px-4 py-3 border-2 border-dashed border-border rounded-lg hover:border-primary hover:bg-accent/50 transition-colors">`);
        Plus($$renderer2, { class: "w-4 h-4" });
        $$renderer2.push(`<!----> Add Custom Type</button>`);
      }
      $$renderer2.push(`<!--]--></div></div></div>`);
    } else {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]-->`);
    if ($$store_subs) unsubscribe_stores($$store_subs);
  });
}
function KnowledgeItemDialog($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    var $$store_subs;
    let {
      open = false,
      item = null
    } = $$props;
    let itemTypes = store_get($$store_subs ??= {}, "$knowledgeStore", knowledgeStore).itemTypes;
    let formData = { typeId: "", title: "", content: "" };
    let isPending = false;
    if (open) {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<div class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"><div class="bg-card border border-border rounded-lg max-w-2xl w-full p-6"><div class="flex items-center justify-between mb-6"><h2 class="text-2xl font-bold">${escape_html(item ? "Edit Item" : "Create Item")}</h2> <button class="p-2 hover:bg-accent rounded-md transition-colors">`);
      X($$renderer2, { class: "w-5 h-5" });
      $$renderer2.push(`<!----></button></div> <form class="space-y-4"><div class="space-y-2"><label for="typeId" class="text-sm font-medium">Type</label> `);
      $$renderer2.select(
        {
          id: "typeId",
          value: formData.typeId,
          required: true,
          class: "w-full px-3 py-2 bg-background border border-input rounded-md focus:outline-none focus:ring-2 focus:ring-ring"
        },
        ($$renderer3) => {
          $$renderer3.push(`<!--[-->`);
          const each_array = ensure_array_like(itemTypes);
          for (let $$index = 0, $$length = each_array.length; $$index < $$length; $$index++) {
            let type = each_array[$$index];
            $$renderer3.option({ value: type.id }, ($$renderer4) => {
              $$renderer4.push(`${escape_html(type.name)}`);
            });
          }
          $$renderer3.push(`<!--]-->`);
        }
      );
      $$renderer2.push(`</div> <div class="space-y-2"><label for="title" class="text-sm font-medium">Title</label> <input id="title" type="text"${attr("value", formData.title)} placeholder="Enter title" required class="w-full px-3 py-2 bg-background border border-input rounded-md focus:outline-none focus:ring-2 focus:ring-ring"/></div> <div class="space-y-2"><label for="content" class="text-sm font-medium">Content</label> <textarea id="content" placeholder="Enter content" required rows="6" class="w-full px-3 py-2 bg-background border border-input rounded-md focus:outline-none focus:ring-2 focus:ring-ring resize-none">`);
      const $$body = escape_html(formData.content);
      if ($$body) {
        $$renderer2.push(`${$$body}`);
      }
      $$renderer2.push(`</textarea></div> <div class="flex gap-2 justify-end pt-4"><button type="button"${attr("disabled", isPending, true)} class="px-4 py-2 bg-accent text-accent-foreground rounded-md hover:bg-accent/80 disabled:opacity-50 transition-colors">Cancel</button> <button type="submit"${attr("disabled", !formData.title.trim() || !formData.content.trim(), true)} class="px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed transition-colors">${escape_html(item ? "Update" : "Create")}</button></div></form></div></div>`);
    } else {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]-->`);
    if ($$store_subs) unsubscribe_stores($$store_subs);
  });
}
function _page($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    var $$store_subs;
    let showManageTypesDialog = false;
    let showItemDialog = false;
    let editingItem = null;
    let selectedTypeId = null;
    let storeState = store_get($$store_subs ??= {}, "$knowledgeStore", knowledgeStore);
    let itemTypes = storeState.itemTypes;
    let items = storeState.items;
    let displayedTypes = itemTypes;
    let groupedStacks = displayedTypes.map((type) => ({
      type,
      items: items.filter((item) => item.typeId === type.id).slice(0, 10)
    }));
    store_get($$store_subs ??= {}, "$tasksStore", tasksStore).tasks;
    store_get($$store_subs ??= {}, "$tasksStore", tasksStore).isLoading;
    $$renderer2.push(`<div class="space-y-6"><header class="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between"><div><h1 class="text-3xl font-bold flex items-center gap-2">`);
    Square_check_big($$renderer2, { class: "w-8 h-8 text-primary" });
    $$renderer2.push(`<!----> Work Canvas</h1> <p class="text-muted-foreground">Manage tasks, knowledge, and calendar—all routed back through the assistant.</p></div></header> <div class="flex gap-2 border-b border-border pb-2"><button${attr_class(`flex items-center gap-2 px-4 py-2 text-sm rounded-t-lg transition-colors ${"bg-primary text-primary-foreground"}`)}>`);
    Book_open($$renderer2, { class: "w-4 h-4" });
    $$renderer2.push(`<!----> Knowledge</button> <button${attr_class(`flex items-center gap-2 px-4 py-2 text-sm rounded-t-lg transition-colors ${"text-muted-foreground hover:bg-accent/40"}`)}>`);
    Square_check_big($$renderer2, { class: "w-4 h-4" });
    $$renderer2.push(`<!----> Tasks</button> <button${attr_class(`flex items-center gap-2 px-4 py-2 text-sm rounded-t-lg transition-colors ${"text-muted-foreground hover:bg-accent/40"}`)}>`);
    Calendar($$renderer2, { class: "w-4 h-4" });
    $$renderer2.push(`<!----> Calendar</button></div> `);
    {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<div class="flex flex-col gap-4"><div class="flex justify-end gap-2"><button class="flex items-center gap-2 px-3 py-2 text-sm rounded-full border border-border hover:bg-accent/40 transition-colors">`);
      Settings($$renderer2, { class: "w-4 h-4" });
      $$renderer2.push(`<!----> Manage types</button> <button class="flex items-center gap-2 px-3 py-2 text-sm rounded-full bg-primary text-primary-foreground hover:bg-primary/90 transition-colors">`);
      Plus($$renderer2, { class: "w-4 h-4" });
      $$renderer2.push(`<!----> Add item</button></div> <div class="flex gap-2 overflow-x-auto pb-2"><button${attr_class(`px-3 py-1.5 rounded-full text-sm border ${"bg-primary text-primary-foreground border-transparent"}`)}>All</button> <!--[-->`);
      const each_array = ensure_array_like(itemTypes);
      for (let $$index = 0, $$length = each_array.length; $$index < $$length; $$index++) {
        let type = each_array[$$index];
        $$renderer2.push(`<button${attr_class(`px-3 py-1.5 rounded-full text-sm border ${selectedTypeId === type.id ? "bg-primary text-primary-foreground border-transparent" : "border-border text-muted-foreground hover:bg-accent/40"}`)}>${escape_html(type.name)}</button>`);
      }
      $$renderer2.push(`<!--]--></div> `);
      {
        $$renderer2.push("<!--[!-->");
      }
      $$renderer2.push(`<!--]--> `);
      if (groupedStacks.length === 0) {
        $$renderer2.push("<!--[-->");
        $$renderer2.push(`<div class="border border-dashed border-border rounded-2xl p-8 text-center text-muted-foreground"><p class="font-medium">No knowledge types found.</p> <p class="text-sm">Create a type to start capturing ideas, notes, or plans.</p></div>`);
      } else {
        $$renderer2.push("<!--[!-->");
        $$renderer2.push(`<div class="space-y-4"><!--[-->`);
        const each_array_1 = ensure_array_like(groupedStacks);
        for (let $$index_2 = 0, $$length = each_array_1.length; $$index_2 < $$length; $$index_2++) {
          let stack = each_array_1[$$index_2];
          $$renderer2.push(`<section class="bg-card/80 border border-border rounded-2xl p-5 shadow-sm backdrop-blur"><div class="flex items-center justify-between mb-4"><div><p class="text-xs uppercase tracking-wide text-muted-foreground">${escape_html(stack.type.name)}</p> <p class="text-lg font-semibold">${escape_html(stack.items.length)} item${escape_html(stack.items.length === 1 ? "" : "s")}</p></div> <button class="text-xs px-3 py-1.5 rounded-full border border-border hover:bg-accent/40 transition-colors">`);
          Plus($$renderer2, { class: "w-3 h-3" });
          $$renderer2.push(`<!----> New ${escape_html(stack.type.name)}</button></div> `);
          if (stack.items.length === 0) {
            $$renderer2.push("<!--[-->");
            $$renderer2.push(`<p class="text-sm text-muted-foreground">No entries yet. Start by creating a ${escape_html(stack.type.name.toLowerCase())}.</p>`);
          } else {
            $$renderer2.push("<!--[!-->");
            $$renderer2.push(`<ul class="space-y-3"><!--[-->`);
            const each_array_2 = ensure_array_like(stack.items);
            for (let $$index_1 = 0, $$length2 = each_array_2.length; $$index_1 < $$length2; $$index_1++) {
              let item = each_array_2[$$index_1];
              $$renderer2.push(`<li class="p-3 rounded-xl border border-border hover:border-primary/40 transition-all"><div class="flex items-start justify-between gap-3"><div class="space-y-1"><p class="font-medium text-sm">${escape_html(item.title)}</p> <p class="text-xs text-muted-foreground line-clamp-2">${escape_html(item.content)}</p></div> <div class="flex gap-1"><div class="flex gap-1"><button class="p-1.5 rounded-full text-xs border border-border hover:bg-accent/40" title="Send to assistant">`);
              Sparkles($$renderer2, { class: "w-3.5 h-3.5" });
              $$renderer2.push(`<!----></button> <button class="p-1.5 rounded-full text-xs border border-border hover:bg-accent/40" title="Copy context">`);
              Clipboard($$renderer2, { class: "w-3.5 h-3.5" });
              $$renderer2.push(`<!----></button> <button class="p-1.5 rounded-full text-xs border border-border hover:bg-accent/40" title="Edit item">✎</button></div></div></div></li>`);
            }
            $$renderer2.push(`<!--]--></ul>`);
          }
          $$renderer2.push(`<!--]--></section>`);
        }
        $$renderer2.push(`<!--]--></div>`);
      }
      $$renderer2.push(`<!--]--></div>`);
    }
    $$renderer2.push(`<!--]--> `);
    {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--> `);
    {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--></div> `);
    ManageTypesDialog($$renderer2, {
      open: showManageTypesDialog
    });
    $$renderer2.push(`<!----> `);
    KnowledgeItemDialog($$renderer2, {
      open: showItemDialog,
      item: editingItem
    });
    $$renderer2.push(`<!---->`);
    if ($$store_subs) unsubscribe_stores($$store_subs);
  });
}
export {
  _page as default
};
