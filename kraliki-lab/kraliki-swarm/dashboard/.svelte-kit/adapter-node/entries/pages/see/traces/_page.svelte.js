import { e as ensure_array_like, d as attr_style, b as stringify, a as attr_class } from "../../../../chunks/index2.js";
import { e as escape_html } from "../../../../chunks/escaping.js";
function _page($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    let traces = [];
    let stats = null;
    let loading = true;
    let error = null;
    let selectedTrace = null;
    let filterType = "";
    let filterAgent = "";
    let limit = 50;
    async function loadTraces() {
      loading = true;
      error = null;
      try {
        const params = new URLSearchParams();
        if (filterType) ;
        if (filterAgent) ;
        params.set("limit", limit.toString());
        const response = await fetch(`/api/traces?${params}`);
        const data = await response.json();
        traces = data.traces || [];
        stats = data.stats || null;
      } catch (e) {
        error = e instanceof Error ? e.message : "Failed to load traces";
      } finally {
        loading = false;
      }
    }
    function formatTimestamp(ts) {
      const date = new Date(ts);
      return date.toLocaleString("en-US", {
        month: "short",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit"
      });
    }
    function getTypeColor(type) {
      const colors = {
        spawn: "#33ff00",
        task_selection: "#00d4ff",
        implementation_strategy: "#ff9500",
        tool_choice: "#9d4edd",
        error_handling: "#ff4444",
        completion: "#33ff00",
        claim: "#00d4ff",
        skip: "#6b7280",
        delegate: "#ff9500",
        abort: "#ff4444"
      };
      return colors[type] || "#6b7280";
    }
    function getOutcomeColor(outcome) {
      if (!outcome) return "#6b7280";
      const colors = {
        success: "#33ff00",
        complete: "#33ff00",
        partial: "#ff9500",
        failure: "#ff4444",
        error: "#ff4444",
        pending: "#6b7280"
      };
      return colors[outcome.toLowerCase()] || "#6b7280";
    }
    $$renderer2.push(`<div class="page svelte-n4cblv"><div class="page-header svelte-n4cblv"><h2 class="glitch svelte-n4cblv">Decision Traces // Agent Observability</h2> <div class="controls svelte-n4cblv">`);
    $$renderer2.select(
      {
        value: filterType,
        onchange: loadTraces,
        class: "filter-select"
      },
      ($$renderer3) => {
        $$renderer3.option(
          { value: "", class: "" },
          ($$renderer4) => {
            $$renderer4.push(`ALL TYPES`);
          },
          "svelte-n4cblv"
        );
        $$renderer3.option(
          { value: "spawn", class: "" },
          ($$renderer4) => {
            $$renderer4.push(`SPAWN`);
          },
          "svelte-n4cblv"
        );
        $$renderer3.option(
          { value: "task_selection", class: "" },
          ($$renderer4) => {
            $$renderer4.push(`TASK_SELECTION`);
          },
          "svelte-n4cblv"
        );
        $$renderer3.option(
          { value: "implementation_strategy", class: "" },
          ($$renderer4) => {
            $$renderer4.push(`IMPL_STRATEGY`);
          },
          "svelte-n4cblv"
        );
        $$renderer3.option(
          { value: "tool_choice", class: "" },
          ($$renderer4) => {
            $$renderer4.push(`TOOL_CHOICE`);
          },
          "svelte-n4cblv"
        );
        $$renderer3.option(
          { value: "completion", class: "" },
          ($$renderer4) => {
            $$renderer4.push(`COMPLETION`);
          },
          "svelte-n4cblv"
        );
        $$renderer3.option(
          { value: "error_handling", class: "" },
          ($$renderer4) => {
            $$renderer4.push(`ERROR_HANDLING`);
          },
          "svelte-n4cblv"
        );
        $$renderer3.option(
          { value: "claim", class: "" },
          ($$renderer4) => {
            $$renderer4.push(`CLAIM`);
          },
          "svelte-n4cblv"
        );
        $$renderer3.option(
          { value: "skip", class: "" },
          ($$renderer4) => {
            $$renderer4.push(`SKIP`);
          },
          "svelte-n4cblv"
        );
        $$renderer3.option(
          { value: "delegate", class: "" },
          ($$renderer4) => {
            $$renderer4.push(`DELEGATE`);
          },
          "svelte-n4cblv"
        );
        $$renderer3.option(
          { value: "abort", class: "" },
          ($$renderer4) => {
            $$renderer4.push(`ABORT`);
          },
          "svelte-n4cblv"
        );
      },
      "svelte-n4cblv"
    );
    $$renderer2.push(` `);
    $$renderer2.select(
      { value: limit, onchange: loadTraces, class: "filter-select" },
      ($$renderer3) => {
        $$renderer3.option(
          { value: 25, class: "" },
          ($$renderer4) => {
            $$renderer4.push(`25 TRACES`);
          },
          "svelte-n4cblv"
        );
        $$renderer3.option(
          { value: 50, class: "" },
          ($$renderer4) => {
            $$renderer4.push(`50 TRACES`);
          },
          "svelte-n4cblv"
        );
        $$renderer3.option(
          { value: 100, class: "" },
          ($$renderer4) => {
            $$renderer4.push(`100 TRACES`);
          },
          "svelte-n4cblv"
        );
        $$renderer3.option(
          { value: 200, class: "" },
          ($$renderer4) => {
            $$renderer4.push(`200 TRACES`);
          },
          "svelte-n4cblv"
        );
      },
      "svelte-n4cblv"
    );
    $$renderer2.push(` <button class="brutal-btn svelte-n4cblv">REFRESH</button></div></div> `);
    if (stats) {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<div class="stats-grid svelte-n4cblv"><div class="stat-card svelte-n4cblv"><span class="stat-value svelte-n4cblv">${escape_html(stats.total_traces)}</span> <span class="stat-label svelte-n4cblv">TOTAL TRACES</span></div> <div class="stat-card svelte-n4cblv"><span class="stat-value svelte-n4cblv">${escape_html(Object.keys(stats.by_type).length)}</span> <span class="stat-label svelte-n4cblv">DECISION TYPES</span></div> <div class="stat-card svelte-n4cblv"><span class="stat-value svelte-n4cblv">${escape_html(Object.keys(stats.by_agent).length)}</span> <span class="stat-label svelte-n4cblv">UNIQUE AGENTS</span></div> <div class="stat-card svelte-n4cblv"><span class="stat-value svelte-n4cblv">${escape_html(Object.keys(stats.by_genome).length)}</span> <span class="stat-label svelte-n4cblv">GENOMES</span></div></div> <div class="type-breakdown svelte-n4cblv"><h3 class="svelte-n4cblv">BY DECISION TYPE</h3> <div class="type-bars svelte-n4cblv"><!--[-->`);
      const each_array = ensure_array_like(Object.entries(stats.by_type));
      for (let $$index = 0, $$length = each_array.length; $$index < $$length; $$index++) {
        let [type, count] = each_array[$$index];
        $$renderer2.push(`<div class="type-bar svelte-n4cblv"><span class="type-name svelte-n4cblv"${attr_style(`color: ${stringify(getTypeColor(type))}`)}>${escape_html(type.toUpperCase())}</span> <div class="bar-container svelte-n4cblv"><div class="bar-fill svelte-n4cblv"${attr_style(`width: ${stringify(count / stats.total_traces * 100)}%; background: ${stringify(getTypeColor(type))}`)}></div></div> <span class="type-count svelte-n4cblv">${escape_html(count)}</span></div>`);
      }
      $$renderer2.push(`<!--]--></div></div>`);
    } else {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--> <div class="content-grid svelte-n4cblv"><div class="traces-list card svelte-n4cblv"><h3 class="svelte-n4cblv">RECENT DECISIONS</h3> `);
    if (loading) {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<div class="loading-state svelte-n4cblv"><span class="loading-text svelte-n4cblv">LOADING_TRACES...</span></div>`);
    } else {
      $$renderer2.push("<!--[!-->");
      if (error) {
        $$renderer2.push("<!--[-->");
        $$renderer2.push(`<div class="error-state svelte-n4cblv"><span class="error-text svelte-n4cblv">ERROR: ${escape_html(error)}</span></div>`);
      } else {
        $$renderer2.push("<!--[!-->");
        if (traces.length === 0) {
          $$renderer2.push("<!--[-->");
          $$renderer2.push(`<div class="empty-state svelte-n4cblv"><span class="empty-text svelte-n4cblv">NO_TRACES_FOUND</span></div>`);
        } else {
          $$renderer2.push("<!--[!-->");
          $$renderer2.push(`<div class="trace-items svelte-n4cblv"><!--[-->`);
          const each_array_1 = ensure_array_like(traces.slice().reverse());
          for (let $$index_1 = 0, $$length = each_array_1.length; $$index_1 < $$length; $$index_1++) {
            let trace = each_array_1[$$index_1];
            $$renderer2.push(`<button${attr_class("trace-item svelte-n4cblv", void 0, { "selected": selectedTrace?.trace_id === trace.trace_id })}><div class="trace-header svelte-n4cblv"><span class="trace-type svelte-n4cblv"${attr_style(`color: ${stringify(getTypeColor(trace.decision_type))}`)}>${escape_html(trace.decision_type.toUpperCase())}</span> <span class="trace-time svelte-n4cblv">${escape_html(formatTimestamp(trace.timestamp))}</span></div> <div class="trace-agent svelte-n4cblv">${escape_html(trace.agent_id)}</div> <div class="trace-decision svelte-n4cblv">${escape_html(trace.decision.slice(0, 80))}...</div> `);
            if (trace.outcome) {
              $$renderer2.push("<!--[-->");
              $$renderer2.push(`<div class="trace-outcome svelte-n4cblv"${attr_style(`color: ${stringify(getOutcomeColor(trace.outcome))}`)}>${escape_html(trace.outcome.toUpperCase())}</div>`);
            } else {
              $$renderer2.push("<!--[!-->");
            }
            $$renderer2.push(`<!--]--></button>`);
          }
          $$renderer2.push(`<!--]--></div>`);
        }
        $$renderer2.push(`<!--]-->`);
      }
      $$renderer2.push(`<!--]-->`);
    }
    $$renderer2.push(`<!--]--></div> <div class="trace-detail card svelte-n4cblv"><h3 class="svelte-n4cblv">TRACE DETAIL</h3> `);
    {
      $$renderer2.push("<!--[!-->");
      $$renderer2.push(`<div class="empty-detail svelte-n4cblv"><span class="empty-text svelte-n4cblv">SELECT A TRACE TO VIEW DETAILS</span></div>`);
    }
    $$renderer2.push(`<!--]--></div></div></div>`);
  });
}
export {
  _page as default
};
