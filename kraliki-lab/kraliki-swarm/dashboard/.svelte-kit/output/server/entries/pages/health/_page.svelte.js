import { a as attr_class, e as ensure_array_like } from "../../../chunks/index2.js";
import { e as escape_html } from "../../../chunks/escaping.js";
import { b as attr } from "../../../chunks/attributes.js";
function _page($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    let loading = true;
    let lastUpdate = "--";
    const CLI_NAMES = {
      "linear_api": "LINEAR",
      "claude_cli": "CLAUDE",
      "codex_cli": "CODEX",
      "gemini_cli": "GEMINI",
      "opencode_cli": "OPENCODE"
    };
    function getOverallStatus() {
      return "unhealthy";
    }
    const overallStatus = getOverallStatus();
    const endpoints = [];
    const pm2Issues = [];
    const circuitBreakers = {};
    const cbEntries = Object.entries(circuitBreakers);
    const cbOpen = cbEntries.filter(([_, cb]) => cb.state === "open").length;
    const cbClosed = cbEntries.filter(([_, cb]) => cb.state === "closed").length;
    $$renderer2.push(`<div class="page svelte-3hm2cj"><div class="page-header svelte-3hm2cj"><h2 class="glitch svelte-3hm2cj">System Health // Diagnostics</h2> <div class="header-controls svelte-3hm2cj"><span class="last-update svelte-3hm2cj">LAST_SCAN: ${escape_html(lastUpdate)}</span> <button class="brutal-btn svelte-3hm2cj"${attr("disabled", loading, true)}>${escape_html("SCANNING...")}</button></div></div> `);
    {
      $$renderer2.push("<!--[!-->");
      $$renderer2.push(`<div${attr_class("status-banner svelte-3hm2cj", void 0, {
        "healthy": overallStatus === "healthy",
        "degraded": overallStatus === "degraded",
        "unhealthy": overallStatus === "unhealthy"
      })}><div class="status-icon svelte-3hm2cj">`);
      if (overallStatus === "healthy") {
        $$renderer2.push("<!--[-->");
        $$renderer2.push(`<span class="pulse-dot green big svelte-3hm2cj"></span>`);
      } else {
        $$renderer2.push("<!--[!-->");
        if (overallStatus === "degraded") {
          $$renderer2.push("<!--[-->");
          $$renderer2.push(`<span class="pulse-dot yellow big svelte-3hm2cj"></span>`);
        } else {
          $$renderer2.push("<!--[!-->");
          $$renderer2.push(`<span class="pulse-dot red big pulse-brutal svelte-3hm2cj"></span>`);
        }
        $$renderer2.push(`<!--]-->`);
      }
      $$renderer2.push(`<!--]--></div> <div class="status-text svelte-3hm2cj"><span class="status-label svelte-3hm2cj">SYSTEM_STATUS</span> <span class="status-value svelte-3hm2cj">${escape_html(overallStatus.toUpperCase())}</span></div> <div class="status-summary svelte-3hm2cj"><span class="svelte-3hm2cj">PM2: ${escape_html(0)}/${escape_html(0)}</span> <span class="svelte-3hm2cj">CB: ${escape_html(cbClosed)}/${escape_html(cbEntries.length)} OK</span> `);
      if (pm2Issues.length > 0) {
        $$renderer2.push("<!--[-->");
        $$renderer2.push(`<span class="issue-count svelte-3hm2cj">${escape_html(pm2Issues.length)} ISSUES</span>`);
      } else {
        $$renderer2.push("<!--[!-->");
      }
      $$renderer2.push(`<!--]--></div></div> <div class="grid svelte-3hm2cj">`);
      {
        $$renderer2.push("<!--[!-->");
      }
      $$renderer2.push(`<!--]--> `);
      {
        $$renderer2.push("<!--[!-->");
      }
      $$renderer2.push(`<!--]--> `);
      if (cbEntries.length > 0) {
        $$renderer2.push("<!--[-->");
        $$renderer2.push(`<div${attr_class("card span-2 svelte-3hm2cj", void 0, { "pulse-scan": cbOpen > 0 })}><h2${attr_class("svelte-3hm2cj", void 0, { "red": cbOpen > 0 })}>CIRCUIT_BREAKERS // ${escape_html(cbOpen > 0 ? `${cbOpen} TRIPPED` : "ALL_OK")}</h2> <p class="hint svelte-3hm2cj">CLI health status. Open = failing, Closed = healthy, Half-open = recovering.</p> <div class="cb-grid svelte-3hm2cj"><!--[-->`);
        const each_array_1 = ensure_array_like(cbEntries);
        for (let $$index_1 = 0, $$length = each_array_1.length; $$index_1 < $$length; $$index_1++) {
          let [name, cb] = each_array_1[$$index_1];
          $$renderer2.push(`<div${attr_class("cb-card svelte-3hm2cj", void 0, {
            "cb-open": cb.state === "open",
            "cb-closed": cb.state === "closed",
            "cb-half": cb.state === "half-open"
          })}><div class="cb-header svelte-3hm2cj"><span class="cb-name svelte-3hm2cj">${escape_html(CLI_NAMES[name] || name.toUpperCase())}</span> <span class="cb-state svelte-3hm2cj"><span${attr_class("pulse-dot svelte-3hm2cj", void 0, {
            "green": cb.state === "closed",
            "red": cb.state === "open",
            "yellow": cb.state === "half-open"
          })}></span> ${escape_html(cb.state.toUpperCase())}</span></div> `);
          if (cb.note) {
            $$renderer2.push("<!--[-->");
            $$renderer2.push(`<div class="cb-note svelte-3hm2cj">${escape_html(cb.note)}</div>`);
          } else {
            $$renderer2.push("<!--[!-->");
          }
          $$renderer2.push(`<!--]--> `);
          if (cb.last_failure_reason && cb.state === "open") {
            $$renderer2.push("<!--[-->");
            $$renderer2.push(`<div class="cb-reason svelte-3hm2cj">${escape_html(cb.last_failure_reason.slice(0, 100))}</div>`);
          } else {
            $$renderer2.push("<!--[!-->");
          }
          $$renderer2.push(`<!--]--> <div class="cb-times svelte-3hm2cj">`);
          if (cb.last_success_time && cb.state !== "open") {
            $$renderer2.push("<!--[-->");
            $$renderer2.push(`<span class="svelte-3hm2cj">OK: ${escape_html(new Date(cb.last_success_time).toLocaleTimeString())}</span>`);
          } else {
            $$renderer2.push("<!--[!-->");
          }
          $$renderer2.push(`<!--]--> `);
          if (cb.last_failure_time) {
            $$renderer2.push("<!--[-->");
            $$renderer2.push(`<span class="svelte-3hm2cj">FAIL: ${escape_html(new Date(cb.last_failure_time).toLocaleTimeString())}</span>`);
          } else {
            $$renderer2.push("<!--[!-->");
          }
          $$renderer2.push(`<!--]--></div></div>`);
        }
        $$renderer2.push(`<!--]--></div></div>`);
      } else {
        $$renderer2.push("<!--[!-->");
      }
      $$renderer2.push(`<!--]--> `);
      if (endpoints.length > 0) {
        $$renderer2.push("<!--[-->");
        $$renderer2.push(`<div class="card svelte-3hm2cj"><h2 class="svelte-3hm2cj">ENDPOINT_HEALTH</h2> <div class="endpoint-list svelte-3hm2cj"><!--[-->`);
        const each_array_2 = ensure_array_like(endpoints);
        for (let $$index_2 = 0, $$length = each_array_2.length; $$index_2 < $$length; $$index_2++) {
          let ep = each_array_2[$$index_2];
          $$renderer2.push(`<div${attr_class("endpoint-item svelte-3hm2cj", void 0, {
            "healthy": ep.status === "healthy",
            "unhealthy": ep.status !== "healthy"
          })}><div class="ep-info svelte-3hm2cj"><span class="ep-name svelte-3hm2cj">${escape_html(ep.name)}</span> <span class="ep-url svelte-3hm2cj">${escape_html(ep.url)}</span></div> <div class="ep-status svelte-3hm2cj"><span${attr_class("pulse-dot svelte-3hm2cj", void 0, {
            "green": ep.status === "healthy",
            "red": ep.status !== "healthy"
          })}></span> <span class="svelte-3hm2cj">${escape_html(ep.status_code)}</span></div></div>`);
        }
        $$renderer2.push(`<!--]--></div></div>`);
      } else {
        $$renderer2.push("<!--[!-->");
      }
      $$renderer2.push(`<!--]--> `);
      {
        $$renderer2.push("<!--[!-->");
      }
      $$renderer2.push(`<!--]--> `);
      {
        $$renderer2.push("<!--[!-->");
      }
      $$renderer2.push(`<!--]--></div>`);
    }
    $$renderer2.push(`<!--]--></div>`);
  });
}
export {
  _page as default
};
