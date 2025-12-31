import { x as head } from "../../../../chunks/index2.js";
import "../../../../chunks/client.js";
import "lightweight-charts";
import { B as Button } from "../../../../chunks/Button.js";
function _page($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    head($$renderer2, ($$renderer3) => {
      $$renderer3.title(($$renderer4) => {
        $$renderer4.push(`<title>Admin Dashboard - Voice by Kraliki</title>`);
      });
    });
    $$renderer2.push(`<div class="space-y-6"><div class="flex items-center justify-between"><div><h1 class="text-2xl font-bold text-gray-900 dark:text-white">Admin Dashboard</h1> <p class="mt-1 text-sm text-gray-600 dark:text-gray-400">System overview and management</p></div> <div class="flex space-x-3">`);
    Button($$renderer2, {
      variant: "secondary",
      onclick: () => window.location.href = "/admin/users",
      children: ($$renderer3) => {
        $$renderer3.push(`<!---->Manage Users`);
      }
    });
    $$renderer2.push(`<!----> `);
    Button($$renderer2, {
      variant: "primary",
      onclick: () => window.location.href = "/admin/campaigns",
      children: ($$renderer3) => {
        $$renderer3.push(`<!---->Campaigns`);
      }
    });
    $$renderer2.push(`<!----></div></div> `);
    {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<div class="flex justify-center py-12"><div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div></div>`);
    }
    $$renderer2.push(`<!--]--></div>`);
  });
}
export {
  _page as default
};
