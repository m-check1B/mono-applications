import "clsx";
import { o as onDestroy } from "../../../../chunks/index-server.js";
import "@sveltejs/kit/internal";
import "../../../../chunks/exports.js";
import "../../../../chunks/utils.js";
import "@sveltejs/kit/internal/server";
import "../../../../chunks/state.svelte.js";
function _page($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    onDestroy(() => {
    });
    $$renderer2.push(`<div class="container mx-auto p-6"><div class="mb-6 flex items-center justify-between"><div><h1 class="text-3xl font-bold">Supervisor Dashboard</h1> <p class="text-gray-600 mt-1">Real-time monitoring and control center</p></div> <div class="flex gap-3"><button class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">Call Queue</button> <button class="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700">Active Calls</button></div></div> `);
    {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--> `);
    {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<div class="text-center py-12"><div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div> <p class="mt-4 text-gray-600">Loading dashboard...</p></div>`);
    }
    $$renderer2.push(`<!--]--></div>`);
  });
}
export {
  _page as default
};
