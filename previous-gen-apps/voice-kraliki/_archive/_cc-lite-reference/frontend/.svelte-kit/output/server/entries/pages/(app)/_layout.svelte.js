import { e as escape_html } from "../../../chunks/escaping.js";
import "clsx";
import { a as auth } from "../../../chunks/auth.svelte.js";
import "@sveltejs/kit/internal";
import "../../../chunks/exports.js";
import "../../../chunks/utils.js";
import "@sveltejs/kit/internal/server";
import "../../../chunks/state.svelte.js";
function _layout($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    let { children } = $$props;
    if (auth.loading) {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<div class="min-h-screen flex items-center justify-center"><div class="text-center"><div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div> <p class="mt-4 text-gray-600 dark:text-gray-400">Loading...</p></div></div>`);
    } else {
      $$renderer2.push("<!--[!-->");
      if (auth.isAuthenticated) {
        $$renderer2.push("<!--[-->");
        $$renderer2.push(`<div class="min-h-screen bg-gray-50 dark:bg-gray-900"><header class="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700"><div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8"><div class="flex justify-between items-center h-16"><div class="flex items-center"><h1 class="text-xl font-bold text-gray-900 dark:text-white">Voice by Kraliki</h1> <nav class="ml-10 flex space-x-4">`);
        if (auth.isAgent) {
          $$renderer2.push("<!--[-->");
          $$renderer2.push(`<a href="/operator" class="text-gray-700 dark:text-gray-300 hover:text-primary-600 dark:hover:text-primary-400 px-3 py-2 rounded-md text-sm font-medium">Dashboard</a>`);
        } else {
          $$renderer2.push("<!--[!-->");
          if (auth.isSupervisor) {
            $$renderer2.push("<!--[-->");
            $$renderer2.push(`<a href="/supervisor" class="text-gray-700 dark:text-gray-300 hover:text-primary-600 dark:hover:text-primary-400 px-3 py-2 rounded-md text-sm font-medium">Dashboard</a>`);
          } else {
            $$renderer2.push("<!--[!-->");
            if (auth.isAdmin) {
              $$renderer2.push("<!--[-->");
              $$renderer2.push(`<a href="/admin" class="text-gray-700 dark:text-gray-300 hover:text-primary-600 dark:hover:text-primary-400 px-3 py-2 rounded-md text-sm font-medium">Dashboard</a> <a href="/admin/campaigns" class="text-gray-700 dark:text-gray-300 hover:text-primary-600 dark:hover:text-primary-400 px-3 py-2 rounded-md text-sm font-medium">Campaigns</a> <a href="/admin/users" class="text-gray-700 dark:text-gray-300 hover:text-primary-600 dark:hover:text-primary-400 px-3 py-2 rounded-md text-sm font-medium">Users</a>`);
            } else {
              $$renderer2.push("<!--[!-->");
            }
            $$renderer2.push(`<!--]-->`);
          }
          $$renderer2.push(`<!--]-->`);
        }
        $$renderer2.push(`<!--]--></nav></div> <div class="flex items-center space-x-4"><span class="text-sm text-gray-700 dark:text-gray-300">${escape_html(auth.user?.firstName)} ${escape_html(auth.user?.lastName)} <span class="text-xs text-gray-500 dark:text-gray-400">(${escape_html(auth.user?.role)})</span></span> <button class="text-gray-700 dark:text-gray-300 hover:text-primary-600 dark:hover:text-primary-400 text-sm font-medium">Logout</button></div></div></div></header> <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">`);
        children?.($$renderer2);
        $$renderer2.push(`<!----></main></div>`);
      } else {
        $$renderer2.push("<!--[!-->");
      }
      $$renderer2.push(`<!--]-->`);
    }
    $$renderer2.push(`<!--]-->`);
  });
}
export {
  _layout as default
};
