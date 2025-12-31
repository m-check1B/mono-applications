import { e as ensure_array_like, d as attr_style, b as stringify } from "../../../chunks/index2.js";
import { e as escape_html } from "../../../chunks/escaping.js";
import { b as attr } from "../../../chunks/attributes.js";
function _page($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    let { data } = $$props;
    let captures = [];
    let sendingCapture = false;
    function getStatusColor(status) {
      switch (status) {
        case "online":
          return "#33ff00";
        case "idle":
          return "#6b7280";
        case "error":
          return "#ff4444";
        default:
          return "#6b7280";
      }
    }
    function countByStatus(status) {
      return data.agents.filter((a) => a.status === status).length;
    }
    $$renderer2.push(`<div class="page svelte-183qobo"><div class="page-header svelte-183qobo"><h2 class="glitch svelte-183qobo">Kraliki See // Multimodal Input</h2> <p class="subtitle svelte-183qobo">Visual + Voice AI Interface</p></div> <div class="content svelte-183qobo"><div class="card camera-card svelte-183qobo"><h3 class="svelte-183qobo">📹 VISUAL_INPUT // RECEPTION</h3> <div class="camera-container svelte-183qobo">`);
    {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<div class="camera-placeholder svelte-183qobo"><span class="placeholder-icon svelte-183qobo">📹</span> <p class="placeholder-text svelte-183qobo">Camera inactive</p> <button class="brutal-btn svelte-183qobo">START CAMERA</button></div>`);
    }
    $$renderer2.push(`<!--]--> `);
    {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--></div> `);
    if (captures.length > 0) {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<div class="captures-section svelte-183qobo"><h4 class="svelte-183qobo">RECENT CAPTURES (${escape_html(captures.length)})</h4> <div class="captures-grid svelte-183qobo"><!--[-->`);
      const each_array = ensure_array_like(captures);
      for (let index = 0, $$length = each_array.length; index < $$length; index++) {
        let capture = each_array[index];
        $$renderer2.push(`<div class="capture-item svelte-183qobo"><img${attr("src", capture)}${attr("alt", `Capture ${stringify(index + 1)}`)} class="svelte-183qobo"/> <div class="capture-actions svelte-183qobo"><button class="action-btn send svelte-183qobo"${attr("disabled", sendingCapture, true)}>📤</button> <button class="action-btn delete svelte-183qobo">🗑️</button></div></div>`);
      }
      $$renderer2.push(`<!--]--></div></div>`);
    } else {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--></div> <div class="status-summary svelte-183qobo"><div class="status-card online svelte-183qobo"><span class="status-dot svelte-183qobo" style="background: #33ff00;"></span> <span class="status-count svelte-183qobo">${escape_html(countByStatus("online"))}</span> <span class="status-label svelte-183qobo">ONLINE</span></div> <div class="status-card idle svelte-183qobo"><span class="status-dot svelte-183qobo" style="background: #6b7280;"></span> <span class="status-count svelte-183qobo">${escape_html(countByStatus("idle"))}</span> <span class="status-label svelte-183qobo">IDLE</span></div> <div class="status-card error svelte-183qobo"><span class="status-dot svelte-183qobo" style="background: #ff4444;"></span> <span class="status-count svelte-183qobo">${escape_html(countByStatus("error"))}</span> <span class="status-label svelte-183qobo">ERROR</span></div></div> <div class="card voice-card svelte-183qobo"><h3 class="svelte-183qobo">🎤 VOICE_INPUT // AI_CONVERSATION</h3> `);
    {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<div class="stt-error svelte-183qobo">⚠️ Speech recognition not supported in this browser. Try Chrome or Edge.</div>`);
    }
    $$renderer2.push(`<!--]--></div> <div class="card agent-card svelte-183qobo"><h3 class="svelte-183qobo">ACTIVE_PROCESSES</h3> <div class="agent-grid svelte-183qobo"><!--[-->`);
    const each_array_2 = ensure_array_like(data.agents);
    for (let $$index_2 = 0, $$length = each_array_2.length; $$index_2 < $$length; $$index_2++) {
      let agent = each_array_2[$$index_2];
      $$renderer2.push(`<div class="agent-badge svelte-183qobo"${attr_style(`border-color: ${stringify(getStatusColor(agent.status))}`)}><span class="agent-dot svelte-183qobo"${attr_style(`background: ${stringify(getStatusColor(agent.status))};`)}></span> <span class="agent-name svelte-183qobo">${escape_html(agent.name)}</span> `);
      if (agent.task) {
        $$renderer2.push("<!--[-->");
        $$renderer2.push(`<span class="agent-task svelte-183qobo">${escape_html(agent.task)}</span>`);
      } else {
        $$renderer2.push("<!--[!-->");
      }
      $$renderer2.push(`<!--]--></div>`);
    }
    $$renderer2.push(`<!--]--></div></div></div></div>`);
  });
}
export {
  _page as default
};
