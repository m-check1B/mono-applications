import { s as sanitize_props, a as spread_props, c as slot, d as store_get, g as ensure_array_like, e as attr_class, f as stringify, u as unsubscribe_stores } from "../../../../chunks/index2.js";
import { a as attr } from "../../../../chunks/attributes.js";
import { w as workspacesStore } from "../../../../chunks/workspaces.js";
import { S as Sparkles } from "../../../../chunks/sparkles.js";
import { I as Icon } from "../../../../chunks/Icon.js";
import { S as Shield } from "../../../../chunks/shield.js";
import { e as escape_html } from "../../../../chunks/escaping.js";
function User_plus($$renderer, $$props) {
  const $$sanitized_props = sanitize_props($$props);
  const iconNode = [
    ["path", { "d": "M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" }],
    ["circle", { "cx": "9", "cy": "7", "r": "4" }],
    ["line", { "x1": "19", "x2": "19", "y1": "8", "y2": "14" }],
    ["line", { "x1": "22", "x2": "16", "y1": "11", "y2": "11" }]
  ];
  Icon($$renderer, spread_props([
    { name: "user-plus" },
    $$sanitized_props,
    {
      /**
       * @component @name UserPlus
       * @description Lucide SVG icon component, renders SVG Element with children.
       *
       * @preview ![img](data:image/svg+xml;base64,PHN2ZyAgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIgogIHdpZHRoPSIyNCIKICBoZWlnaHQ9IjI0IgogIHZpZXdCb3g9IjAgMCAyNCAyNCIKICBmaWxsPSJub25lIgogIHN0cm9rZT0iIzAwMCIgc3R5bGU9ImJhY2tncm91bmQtY29sb3I6ICNmZmY7IGJvcmRlci1yYWRpdXM6IDJweCIKICBzdHJva2Utd2lkdGg9IjIiCiAgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIgogIHN0cm9rZS1saW5lam9pbj0icm91bmQiCj4KICA8cGF0aCBkPSJNMTYgMjF2LTJhNCA0IDAgMCAwLTQtNEg2YTQgNCAwIDAgMC00IDR2MiIgLz4KICA8Y2lyY2xlIGN4PSI5IiBjeT0iNyIgcj0iNCIgLz4KICA8bGluZSB4MT0iMTkiIHgyPSIxOSIgeTE9IjgiIHkyPSIxNCIgLz4KICA8bGluZSB4MT0iMjIiIHgyPSIxNiIgeTE9IjExIiB5Mj0iMTEiIC8+Cjwvc3ZnPgo=) - https://lucide.dev/icons/user-plus
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
function Users($$renderer, $$props) {
  const $$sanitized_props = sanitize_props($$props);
  const iconNode = [
    ["path", { "d": "M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" }],
    ["circle", { "cx": "9", "cy": "7", "r": "4" }],
    ["path", { "d": "M22 21v-2a4 4 0 0 0-3-3.87" }],
    ["path", { "d": "M16 3.13a4 4 0 0 1 0 7.75" }]
  ];
  Icon($$renderer, spread_props([
    { name: "users" },
    $$sanitized_props,
    {
      /**
       * @component @name Users
       * @description Lucide SVG icon component, renders SVG Element with children.
       *
       * @preview ![img](data:image/svg+xml;base64,PHN2ZyAgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIgogIHdpZHRoPSIyNCIKICBoZWlnaHQ9IjI0IgogIHZpZXdCb3g9IjAgMCAyNCAyNCIKICBmaWxsPSJub25lIgogIHN0cm9rZT0iIzAwMCIgc3R5bGU9ImJhY2tncm91bmQtY29sb3I6ICNmZmY7IGJvcmRlci1yYWRpdXM6IDJweCIKICBzdHJva2Utd2lkdGg9IjIiCiAgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIgogIHN0cm9rZS1saW5lam9pbj0icm91bmQiCj4KICA8cGF0aCBkPSJNMTYgMjF2LTJhNCA0IDAgMCAwLTQtNEg2YTQgNCAwIDAgMC00IDR2MiIgLz4KICA8Y2lyY2xlIGN4PSI5IiBjeT0iNyIgcj0iNCIgLz4KICA8cGF0aCBkPSJNMjIgMjF2LTJhNCA0IDAgMCAwLTMtMy44NyIgLz4KICA8cGF0aCBkPSJNMTYgMy4xM2E0IDQgMCAwIDEgMCA3Ljc1IiAvPgo8L3N2Zz4K) - https://lucide.dev/icons/users
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
    var $$store_subs;
    let inviteEmail = "";
    let inviteRole = "MEMBER";
    let newWorkspaceName = "";
    let newWorkspaceDescription = "";
    let selectedWorkspaceId = null;
    let workspaceState = store_get($$store_subs ??= {}, "$workspacesStore", workspacesStore);
    let workspaceOptions = workspaceState.workspaces;
    workspaceState.members;
    $$renderer2.push(`<div class="space-y-6"><div><h1 class="text-3xl font-bold">Team Workspaces</h1> <p class="text-muted-foreground mt-1">Manage shared workspaces, roles, and invites</p></div> <div class="flex flex-wrap gap-2 text-xs sm:text-sm"><button class="inline-flex items-center gap-2 px-3 py-1.5 rounded-full border border-dashed border-primary/40 text-primary hover:bg-primary/10 transition">`);
    Sparkles($$renderer2, { class: "w-3.5 h-3.5" });
    $$renderer2.push(`<!----> Ask for staffing plan</button> <button class="inline-flex items-center gap-2 px-3 py-1.5 rounded-full border border-dashed border-primary/40 text-primary hover:bg-primary/10 transition">`);
    Sparkles($$renderer2, { class: "w-3.5 h-3.5" });
    $$renderer2.push(`<!----> Craft invite note</button> <button class="inline-flex items-center gap-2 px-3 py-1.5 rounded-full border border-dashed border-primary/40 text-primary hover:bg-primary/10 transition">`);
    Sparkles($$renderer2, { class: "w-3.5 h-3.5" });
    $$renderer2.push(`<!----> Review access &amp; roles</button></div> `);
    {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--> <div class="grid grid-cols-1 lg:grid-cols-3 gap-4"><div class="bg-card border border-border rounded-lg p-6 space-y-4"><div class="flex items-center gap-2">`);
    Users($$renderer2, { class: "w-5 h-5 text-primary" });
    $$renderer2.push(`<!----> <h2 class="text-lg font-semibold">Your Workspaces</h2></div> <div class="space-y-3"><!--[-->`);
    const each_array = ensure_array_like(workspaceOptions);
    for (let $$index = 0, $$length = each_array.length; $$index < $$length; $$index++) {
      let workspace = each_array[$$index];
      $$renderer2.push(`<button${attr_class(`w-full text-left px-3 py-2 rounded-md border ${stringify(selectedWorkspaceId === workspace.id ? "border-primary bg-primary/10" : "border-border hover:bg-accent/40")}`)}><p class="font-medium">${escape_html(workspace.name)}</p> <p class="text-xs text-muted-foreground">${escape_html(workspace.memberCount || 0)} member${escape_html(workspace.memberCount === 1 ? "" : "s")}</p></button>`);
    }
    $$renderer2.push(`<!--]--></div> <div class="border-t border-border pt-4 space-y-2"><h3 class="text-sm font-semibold">Create Workspace</h3> <input type="text" placeholder="Name"${attr("value", newWorkspaceName)} class="w-full px-3 py-2 bg-background border border-input rounded-md focus:outline-none focus:ring-2 focus:ring-ring"/> <input type="text" placeholder="Description"${attr("value", newWorkspaceDescription)} class="w-full px-3 py-2 bg-background border border-input rounded-md focus:outline-none focus:ring-2 focus:ring-ring"/> <button class="w-full px-3 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors">Create</button></div></div> <div class="bg-card border border-border rounded-lg p-6 space-y-4 lg:col-span-2"><div class="flex items-center gap-2">`);
    User_plus($$renderer2, { class: "w-5 h-5 text-primary" });
    $$renderer2.push(`<!----> <h2 class="text-lg font-semibold">Invite Team Members</h2></div> <p class="text-sm text-muted-foreground">Invite teammates to collaborate in your active workspace.</p> <div class="grid grid-cols-1 md:grid-cols-3 gap-3"><input type="email" placeholder="team@company.com"${attr("value", inviteEmail)} class="md:col-span-2 px-3 py-2 bg-background border border-input rounded-md focus:outline-none focus:ring-2 focus:ring-ring"/> `);
    $$renderer2.select(
      {
        value: inviteRole,
        class: "px-3 py-2 bg-background border border-input rounded-md focus:outline-none focus:ring-2 focus:ring-ring"
      },
      ($$renderer3) => {
        $$renderer3.option({ value: "MEMBER" }, ($$renderer4) => {
          $$renderer4.push(`Member`);
        });
        $$renderer3.option({ value: "ADMIN" }, ($$renderer4) => {
          $$renderer4.push(`Admin`);
        });
      }
    );
    $$renderer2.push(`</div> <div class="flex items-center gap-3"><button class="px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors"${attr("disabled", !inviteEmail, true)}>Send Invite</button> `);
    {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--></div></div></div> <div class="bg-card border border-border rounded-lg p-6 space-y-4"><div class="flex items-center gap-2">`);
    Shield($$renderer2, { class: "w-5 h-5 text-primary" });
    $$renderer2.push(`<!----> <h2 class="text-lg font-semibold">Workspace Members</h2></div> `);
    {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<p class="text-muted-foreground">Select or create a workspace to manage members.</p>`);
    }
    $$renderer2.push(`<!--]--></div></div>`);
    if ($$store_subs) unsubscribe_stores($$store_subs);
  });
}
export {
  _page as default
};
