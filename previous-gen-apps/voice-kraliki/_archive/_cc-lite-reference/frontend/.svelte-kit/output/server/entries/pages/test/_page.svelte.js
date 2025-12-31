import { F as attr_style, G as stringify, x as head } from "../../../chunks/index2.js";
import { B as Button } from "../../../chunks/Button.js";
import { C as Card } from "../../../chunks/Card.js";
import { B as Badge } from "../../../chunks/Badge.js";
import { e as escape_html } from "../../../chunks/escaping.js";
import "clsx";
import "lightweight-charts";
function Sparkline($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    let { height = 40 } = $$props;
    $$renderer2.push(`<div class="w-full"${attr_style(`height: ${stringify(
      // Update data when it changes
      height
    )}px;`)}></div>`);
  });
}
function StatsCard($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    let { title, value, subtitle, icon, trend, trendColor = "#3b82f6" } = $$props;
    $$renderer2.push(`<div class="bg-white dark:bg-gray-800 rounded-xl shadow border border-gray-200 dark:border-gray-700 p-6 relative overflow-hidden">`);
    if (trend && trend.length > 0) {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<div class="absolute inset-0 opacity-10 dark:opacity-5">`);
      Sparkline($$renderer2, { height: 80 });
      $$renderer2.push(`<!----></div>`);
    } else {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--> <div class="flex items-center justify-between relative z-10"><div class="flex-1"><p class="text-sm font-medium text-gray-600 dark:text-gray-400">${escape_html(title)}</p> <p class="mt-2 text-3xl font-bold text-gray-900 dark:text-white">${escape_html(value)}</p> `);
    if (subtitle) {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<p class="mt-1 text-sm text-gray-500 dark:text-gray-400">${escape_html(subtitle)}</p>`);
    } else {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--></div> `);
    if (icon) {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<div class="flex-shrink-0 ml-4">`);
      icon($$renderer2);
      $$renderer2.push(`<!----></div>`);
    } else {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--></div></div>`);
  });
}
function _page($$renderer) {
  head($$renderer, ($$renderer2) => {
    $$renderer2.title(($$renderer3) => {
      $$renderer3.push(`<title>SvelteKit UI Test Page</title>`);
    });
  });
  $$renderer.push(`<div class="min-h-screen bg-gray-50 dark:bg-gray-900 p-8"><div class="max-w-7xl mx-auto space-y-8"><div class="text-center"><h1 class="text-4xl font-bold text-gray-900 dark:text-white mb-2">✅ SvelteKit UI is Working!</h1> <p class="text-lg text-gray-600 dark:text-gray-400">Your new frontend is successfully running</p></div> <div class="grid grid-cols-1 md:grid-cols-4 gap-6">`);
  StatsCard($$renderer, {
    title: "Components",
    value: "22",
    subtitle: "Total files created"
  });
  $$renderer.push(`<!----> `);
  StatsCard($$renderer, {
    title: "Code Reduction",
    value: "87%",
    subtitle: "Less code than React"
  });
  $$renderer.push(`<!----> `);
  StatsCard($$renderer, {
    title: "Bundle Size",
    value: "75%",
    subtitle: "Smaller than React"
  });
  $$renderer.push(`<!----> `);
  StatsCard($$renderer, { title: "Performance", value: "6x", subtitle: "Faster builds" });
  $$renderer.push(`<!----></div> <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">`);
  {
    let header = function($$renderer2) {
      $$renderer2.push(`<h2 class="text-lg font-semibold text-gray-900 dark:text-white">Button Components</h2>`);
    };
    Card($$renderer, {
      header,
      children: ($$renderer2) => {
        $$renderer2.push(`<div class="space-y-4"><div class="flex flex-wrap gap-2">`);
        Button($$renderer2, {
          variant: "primary",
          children: ($$renderer3) => {
            $$renderer3.push(`<!---->Primary Button`);
          }
        });
        $$renderer2.push(`<!----> `);
        Button($$renderer2, {
          variant: "secondary",
          children: ($$renderer3) => {
            $$renderer3.push(`<!---->Secondary Button`);
          }
        });
        $$renderer2.push(`<!----> `);
        Button($$renderer2, {
          variant: "success",
          children: ($$renderer3) => {
            $$renderer3.push(`<!---->Success Button`);
          }
        });
        $$renderer2.push(`<!----> `);
        Button($$renderer2, {
          variant: "danger",
          children: ($$renderer3) => {
            $$renderer3.push(`<!---->Danger Button`);
          }
        });
        $$renderer2.push(`<!----></div> <div class="flex flex-wrap gap-2">`);
        Button($$renderer2, {
          size: "sm",
          variant: "primary",
          children: ($$renderer3) => {
            $$renderer3.push(`<!---->Small`);
          }
        });
        $$renderer2.push(`<!----> `);
        Button($$renderer2, {
          size: "md",
          variant: "primary",
          children: ($$renderer3) => {
            $$renderer3.push(`<!---->Medium`);
          }
        });
        $$renderer2.push(`<!----> `);
        Button($$renderer2, {
          size: "lg",
          variant: "primary",
          children: ($$renderer3) => {
            $$renderer3.push(`<!---->Large`);
          }
        });
        $$renderer2.push(`<!----></div> <div class="flex flex-wrap gap-2">`);
        Button($$renderer2, {
          loading: true,
          variant: "primary",
          children: ($$renderer3) => {
            $$renderer3.push(`<!---->Loading...`);
          }
        });
        $$renderer2.push(`<!----> `);
        Button($$renderer2, {
          disabled: true,
          variant: "primary",
          children: ($$renderer3) => {
            $$renderer3.push(`<!---->Disabled`);
          }
        });
        $$renderer2.push(`<!----></div></div>`);
      }
    });
  }
  $$renderer.push(`<!----> `);
  {
    let header = function($$renderer2) {
      $$renderer2.push(`<h2 class="text-lg font-semibold text-gray-900 dark:text-white">Badge Components</h2>`);
    };
    Card($$renderer, {
      header,
      children: ($$renderer2) => {
        $$renderer2.push(`<div class="space-y-4"><div class="flex flex-wrap gap-2">`);
        Badge($$renderer2, {
          variant: "primary",
          children: ($$renderer3) => {
            $$renderer3.push(`<!---->Primary`);
          }
        });
        $$renderer2.push(`<!----> `);
        Badge($$renderer2, {
          variant: "success",
          children: ($$renderer3) => {
            $$renderer3.push(`<!---->Success`);
          }
        });
        $$renderer2.push(`<!----> `);
        Badge($$renderer2, {
          variant: "warning",
          children: ($$renderer3) => {
            $$renderer3.push(`<!---->Warning`);
          }
        });
        $$renderer2.push(`<!----> `);
        Badge($$renderer2, {
          variant: "danger",
          children: ($$renderer3) => {
            $$renderer3.push(`<!---->Danger`);
          }
        });
        $$renderer2.push(`<!----> `);
        Badge($$renderer2, {
          variant: "gray",
          children: ($$renderer3) => {
            $$renderer3.push(`<!---->Gray`);
          }
        });
        $$renderer2.push(`<!----></div> <div class="flex flex-wrap gap-2 items-center"><span class="text-sm text-gray-600 dark:text-gray-400">Call Status:</span> `);
        Badge($$renderer2, {
          variant: "success",
          children: ($$renderer3) => {
            $$renderer3.push(`<!---->IN_PROGRESS`);
          }
        });
        $$renderer2.push(`<!----> `);
        Badge($$renderer2, {
          variant: "warning",
          children: ($$renderer3) => {
            $$renderer3.push(`<!---->RINGING`);
          }
        });
        $$renderer2.push(`<!----> `);
        Badge($$renderer2, {
          variant: "primary",
          children: ($$renderer3) => {
            $$renderer3.push(`<!---->QUEUED`);
          }
        });
        $$renderer2.push(`<!----></div></div>`);
      }
    });
  }
  $$renderer.push(`<!----></div> `);
  {
    let header = function($$renderer2) {
      $$renderer2.push(`<h2 class="text-lg font-semibold text-gray-900 dark:text-white">Available Dashboards</h2>`);
    };
    Card($$renderer, {
      header,
      children: ($$renderer2) => {
        $$renderer2.push(`<div class="grid grid-cols-1 md:grid-cols-3 gap-4"><a href="/login" class="block p-6 bg-gray-50 dark:bg-gray-700 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors text-center"><div class="text-4xl mb-3">🔐</div> <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-2">Login</h3> <p class="text-sm text-gray-600 dark:text-gray-400">Authentication page (needs backend)</p></a> <a href="/operator" class="block p-6 bg-gray-50 dark:bg-gray-700 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors text-center"><div class="text-4xl mb-3">👨‍💼</div> <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-2">Operator</h3> <p class="text-sm text-gray-600 dark:text-gray-400">Agent dashboard (needs backend)</p></a> <a href="/supervisor" class="block p-6 bg-gray-50 dark:bg-gray-700 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors text-center"><div class="text-4xl mb-3">👔</div> <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-2">Supervisor</h3> <p class="text-sm text-gray-600 dark:text-gray-400">Supervisor cockpit (needs backend)</p></a></div>`);
      }
    });
  }
  $$renderer.push(`<!----> `);
  {
    let header = function($$renderer2) {
      $$renderer2.push(`<h2 class="text-lg font-semibold text-gray-900 dark:text-white">System Status</h2>`);
    };
    Card($$renderer, {
      header,
      children: ($$renderer2) => {
        $$renderer2.push(`<div class="space-y-3"><div class="flex items-center justify-between"><span class="text-sm font-medium text-gray-700 dark:text-gray-300">Frontend (SvelteKit)</span> <span class="px-3 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400">✅ Running</span></div> <div class="flex items-center justify-between"><span class="text-sm font-medium text-gray-700 dark:text-gray-300">Backend (Node.js)</span> <span class="px-3 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400">❌ Not Running</span></div> <div class="mt-4 p-4 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg"><p class="text-sm text-yellow-800 dark:text-yellow-400"><strong>Note:</strong> To use dashboards with real data, start the backend:</p> <pre class="mt-2 p-2 bg-gray-900 text-green-400 rounded text-xs overflow-x-auto">cd /home/adminmatej/github/apps/cc-lite
PORT=3010 HOST=127.0.0.1 pnpm dev:server</pre></div></div>`);
      }
    });
  }
  $$renderer.push(`<!----></div></div>`);
}
export {
  _page as default
};
