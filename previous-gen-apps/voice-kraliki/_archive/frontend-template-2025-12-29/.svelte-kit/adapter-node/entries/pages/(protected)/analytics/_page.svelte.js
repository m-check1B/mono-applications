import { c as attr, d as attr_class, h as head } from "../../../../chunks/index2.js";
import { o as onDestroy } from "../../../../chunks/index-server.js";
function EnhancedDashboard($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    let isLoading = true;
    onDestroy(() => {
    });
    $$renderer2.push(`<div class="enhanced-dashboard svelte-1992uwp"><div class="dashboard-header svelte-1992uwp"><div class="title-section svelte-1992uwp"><h2 class="dashboard-title svelte-1992uwp">Analytics Dashboard</h2> `);
    {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--></div> <button class="refresh-btn svelte-1992uwp"${attr("disabled", isLoading, true)}><span${attr_class("refresh-icon svelte-1992uwp", void 0, { "spinning": isLoading })}>🔄</span> Refresh</button></div> `);
    {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--> `);
    {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<div class="loading-state svelte-1992uwp"><span class="spinner svelte-1992uwp">⟳</span> <p>Loading analytics...</p></div>`);
    }
    $$renderer2.push(`<!--]--></div>`);
  });
}
function _page($$renderer) {
  let activeTab = "overview";
  head("10q6bi9", $$renderer, ($$renderer2) => {
    $$renderer2.title(($$renderer3) => {
      $$renderer3.push(`<title>Analytics Dashboard | Voice by Kraliki</title>`);
    });
    $$renderer2.push(`<meta name="description" content="Real-time analytics and performance metrics"/>`);
  });
  $$renderer.push(`<div class="analytics-page svelte-10q6bi9"><div class="page-header svelte-10q6bi9"><div class="header-content svelte-10q6bi9"><h1 class="page-title svelte-10q6bi9">Analytics &amp; Insights</h1> <p class="page-description svelte-10q6bi9">Real-time monitoring of call metrics, provider performance, and agent activity</p></div></div> <div class="tab-navigation svelte-10q6bi9"><button${attr_class("tab-btn svelte-10q6bi9", void 0, { "active": activeTab === "overview" })}><span class="tab-icon svelte-10q6bi9">📊</span> <span class="tab-label svelte-10q6bi9">Overview</span></button> <button${attr_class("tab-btn svelte-10q6bi9", void 0, { "active": activeTab === "metrics" })}><span class="tab-icon svelte-10q6bi9">📈</span> <span class="tab-label svelte-10q6bi9">Metrics &amp; Charts</span></button> <button${attr_class("tab-btn svelte-10q6bi9", void 0, { "active": activeTab === "health" })}><span class="tab-icon svelte-10q6bi9">🏥</span> <span class="tab-label svelte-10q6bi9">Provider Health</span></button></div> <div class="tab-content svelte-10q6bi9">`);
  {
    $$renderer.push("<!--[-->");
    $$renderer.push(`<div class="tab-panel svelte-10q6bi9" data-tab="overview">`);
    EnhancedDashboard($$renderer);
    $$renderer.push(`<!----></div>`);
  }
  $$renderer.push(`<!--]--></div> <div class="info-section svelte-10q6bi9"><div class="info-card svelte-10q6bi9"><div class="info-icon svelte-10q6bi9">💡</div> <div class="info-content"><h4 class="info-title svelte-10q6bi9">Getting Started</h4> <p class="info-text svelte-10q6bi9">Analytics data is collected from all active calls. Visit the <a href="/calls/agent" class="svelte-10q6bi9">Agent Operations</a> page to start demo calls and see live metrics.</p></div></div> <div class="info-card svelte-10q6bi9"><div class="info-icon svelte-10q6bi9">⚙️</div> <div class="info-content"><h4 class="info-title svelte-10q6bi9">Auto-Refresh</h4> <p class="info-text svelte-10q6bi9">All dashboards auto-refresh to show the latest data. Overview refreshes every 30 seconds, metrics every 60 seconds, and health every 15 seconds.</p></div></div> <div class="info-card svelte-10q6bi9"><div class="info-icon svelte-10q6bi9">📋</div> <div class="info-content"><h4 class="info-title svelte-10q6bi9">Data Retention</h4> <p class="info-text svelte-10q6bi9">Time-series data is retained for 24 hours. Historical summaries can be retrieved via the API with custom date ranges.</p></div></div></div></div>`);
}
export {
  _page as default
};
