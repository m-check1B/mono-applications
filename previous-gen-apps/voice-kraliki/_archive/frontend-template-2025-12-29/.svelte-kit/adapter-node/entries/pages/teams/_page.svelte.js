import { e as escape_html } from "../../../chunks/escaping.js";
import "clsx";
import "@sveltejs/kit/internal";
import "../../../chunks/exports.js";
import "../../../chunks/utils.js";
import "@sveltejs/kit/internal/server";
import "../../../chunks/state.svelte.js";
function _page($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    $$renderer2.push(`<div class="container mx-auto p-6"><div class="mb-6 flex items-center justify-between"><div><h1 class="text-3xl font-bold">Teams</h1> <p class="text-gray-600 mt-1">Manage team hierarchy and structure</p></div> <div class="flex gap-3"><button class="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50">${escape_html("📋 List View")}</button> <button class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700">+ New Team</button></div></div> `);
    {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--> `);
    {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<div class="text-center py-12"><div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div> <p class="mt-4 text-gray-600">Loading teams...</p></div>`);
    }
    $$renderer2.push(`<!--]--></div>`);
  });
}
export {
  _page as default
};
