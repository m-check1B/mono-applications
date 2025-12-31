import { a as attr_class, e as ensure_array_like, d as attr_style, b as stringify } from "../../../chunks/index2.js";
import { b as attr } from "../../../chunks/attributes.js";
import { e as escape_html } from "../../../chunks/escaping.js";
function _page($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    let issues = [];
    let blockers = [];
    let loading = true;
    let activeTab = "blockers";
    let markingDone = null;
    const blockerColors = {
      CRITICAL: "#ff5555",
      HIGH: "#ffaa00",
      MEDIUM: "#33ff00",
      LOW: "#888"
    };
    const linearUrl = "https://linear.app/verduona/team/VD/active";
    const criticalCount = blockers.filter((b) => b.priority === "CRITICAL").length;
    $$renderer2.push(`<div class="page svelte-4b134t"><div class="page-header svelte-4b134t"><h2 class="glitch svelte-4b134t">Jobs // Work Queue</h2> <div style="display: flex; gap: 12px;" class="svelte-4b134t"><button class="brutal-btn svelte-4b134t"${attr("disabled", loading, true)}>${escape_html("LOADING...")}</button> <a${attr("href", linearUrl)} target="_blank" class="brutal-btn svelte-4b134t">OPEN_LINEAR</a></div></div> <div class="tabs svelte-4b134t"><button${attr_class("tab-btn svelte-4b134t", void 0, { "active": activeTab === "blockers" })}>HUMAN_BLOCKERS `);
    if (criticalCount > 0) {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<span class="critical-badge svelte-4b134t">${escape_html(criticalCount)} CRITICAL</span>`);
    } else {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--></button> <button${attr_class("tab-btn svelte-4b134t", void 0, { "active": activeTab === "linear" })}>LINEAR_ISSUES (${escape_html(issues.length)})</button></div> `);
    {
      $$renderer2.push("<!--[-->");
      if (blockers.length === 0) {
        $$renderer2.push("<!--[-->");
        $$renderer2.push(`<div class="loading svelte-4b134t">LOADING_HUMAN_BLOCKERS...</div>`);
      } else {
        $$renderer2.push("<!--[!-->");
        if (blockers.length === 0) {
          $$renderer2.push("<!--[-->");
          $$renderer2.push(`<div class="empty success svelte-4b134t">NO_BLOCKERS - All clear for human work queue!</div>`);
        } else {
          $$renderer2.push("<!--[!-->");
          $$renderer2.push(`<div class="blockers-list svelte-4b134t"><!--[-->`);
          const each_array = ensure_array_like(blockers);
          for (let $$index = 0, $$length = each_array.length; $$index < $$length; $$index++) {
            let blocker = each_array[$$index];
            $$renderer2.push(`<div${attr_class("blocker-card svelte-4b134t", void 0, {
              "critical": blocker.priority === "CRITICAL",
              "high": blocker.priority === "HIGH"
            })}><div class="blocker-header svelte-4b134t"><span class="blocker-id svelte-4b134t">${escape_html(blocker.id)}</span> <span class="blocker-priority svelte-4b134t"${attr_style(`color: ${stringify(blockerColors[blocker.priority])}`)}>${escape_html(blocker.priority)}</span></div> <div class="blocker-task svelte-4b134t">${escape_html(blocker.task)}</div> <div class="blocker-meta svelte-4b134t">`);
            if (blocker.time) {
              $$renderer2.push("<!--[-->");
              $$renderer2.push(`<span class="blocker-time svelte-4b134t">EST: ${escape_html(blocker.time)}</span>`);
            } else {
              $$renderer2.push("<!--[!-->");
            }
            $$renderer2.push(`<!--]--> `);
            if (blocker.notes) {
              $$renderer2.push("<!--[-->");
              $$renderer2.push(`<span class="blocker-notes svelte-4b134t">${escape_html(blocker.notes)}</span>`);
            } else {
              $$renderer2.push("<!--[!-->");
            }
            $$renderer2.push(`<!--]--></div> <div class="blocker-actions svelte-4b134t"><button class="brutal-btn done-btn svelte-4b134t"${attr("disabled", markingDone === blocker.id, true)}>${escape_html(markingDone === blocker.id ? "MARKING..." : "MARK_DONE")}</button></div></div>`);
          }
          $$renderer2.push(`<!--]--></div>`);
        }
        $$renderer2.push(`<!--]-->`);
      }
      $$renderer2.push(`<!--]-->`);
    }
    $$renderer2.push(`<!--]--> `);
    {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--></div>`);
  });
}
export {
  _page as default
};
