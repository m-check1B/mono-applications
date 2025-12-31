import { a as attr_class, e as ensure_array_like, b as stringify } from "../../../chunks/index2.js";
import { e as escape_html } from "../../../chunks/escaping.js";
import { b as attr } from "../../../chunks/attributes.js";
function _page($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    let voiceStatus = "checking";
    const isDevHost = typeof window !== "undefined" && window.location.hostname.endsWith("verduona.dev");
    let voiceUrl = isDevHost ? "https://voice.verduona.dev" : "https://voice.kraliki.com";
    let channels = [];
    let campaigns = [];
    let agents = [];
    let queueItems = [];
    let activeTab = "overview";
    const totalInbound = channels.reduce((sum, c) => sum + c.inbound, 0);
    const totalOutbound = channels.reduce((sum, c) => sum + c.outbound, 0);
    const activeChannels = channels.filter((c) => c.status === "active").length;
    campaigns.filter((c) => c.status === "active").length;
    agents.filter((a) => a.status === "available").length;
    queueItems.filter((q) => q.status === "waiting").length;
    $$renderer2.push(`<div class="page svelte-t803t0"><div class="page-header svelte-t803t0"><h2 class="glitch svelte-t803t0">Reach // Unified Communication</h2> <div class="header-badges svelte-t803t0"><span class="status-badge svelte-t803t0">${escape_html(activeChannels)}/${escape_html(channels.length)} CHANNELS</span> <span${attr_class(`voice-badge ${stringify(voiceStatus)}`, "svelte-t803t0")}>`);
    {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`VOICE: CHECKING...`);
    }
    $$renderer2.push(`<!--]--></span></div></div> <div${attr_class("integration-banner svelte-t803t0", void 0, { "online": voiceStatus === "online" })}><div class="banner-content svelte-t803t0"><span class="banner-icon svelte-t803t0">📞</span> <div class="banner-text svelte-t803t0"><strong class="svelte-t803t0">Voice Engine: Voice by Kraliki</strong> <span class="svelte-t803t0">AI-powered call center for inbound/outbound voice communication</span></div> <div class="banner-actions svelte-t803t0"><a${attr("href", voiceUrl)} target="_blank" class="brutal-btn small svelte-t803t0">OPEN VOICE</a> `);
    {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--></div></div></div> <div class="reach-tabs svelte-t803t0"><button${attr_class("reach-tab svelte-t803t0", void 0, { "active": activeTab === "overview" })}>OVERVIEW</button> <button${attr_class("reach-tab svelte-t803t0", void 0, { "active": activeTab === "inbound" })}>INBOUND</button> <button${attr_class("reach-tab svelte-t803t0", void 0, { "active": activeTab === "outbound" })}>OUTBOUND</button> <button${attr_class("reach-tab svelte-t803t0", void 0, { "active": activeTab === "agents" })}>AI_AGENTS</button></div> `);
    {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<div class="stats-row svelte-t803t0"><div class="stat-card svelte-t803t0"><span class="stat-value svelte-t803t0">${escape_html(totalInbound)}</span> <span class="stat-label svelte-t803t0">INBOUND_TODAY</span></div> <div class="stat-card svelte-t803t0"><span class="stat-value svelte-t803t0">${escape_html(totalOutbound)}</span> <span class="stat-label svelte-t803t0">OUTBOUND_TODAY</span></div> <div class="stat-card svelte-t803t0"><span class="stat-value svelte-t803t0">${escape_html(activeChannels)}</span> <span class="stat-label svelte-t803t0">ACTIVE_CHANNELS</span></div> <div class="stat-card svelte-t803t0"><span class="stat-value svelte-t803t0">--</span> <span class="stat-label svelte-t803t0">RESPONSE_RATE</span></div></div> <div class="section svelte-t803t0"><h3 class="svelte-t803t0">CHANNELS</h3> <div class="channels-grid svelte-t803t0"><!--[-->`);
      const each_array = ensure_array_like(channels);
      for (let $$index = 0, $$length = each_array.length; $$index < $$length; $$index++) {
        let channel = each_array[$$index];
        $$renderer2.push(`<div${attr_class("channel-card svelte-t803t0", void 0, {
          "coming": channel.status === "coming",
          "active": channel.status === "active"
        })}><div class="channel-header svelte-t803t0"><span class="channel-icon svelte-t803t0">${escape_html(channel.icon)}</span> <span class="channel-name svelte-t803t0">${escape_html(channel.name)}</span> <span${attr_class("channel-status svelte-t803t0", void 0, {
          "active": channel.status === "active",
          "coming": channel.status === "coming"
        })}>${escape_html(channel.status.toUpperCase())}</span></div> <div class="channel-provider svelte-t803t0">via ${escape_html(channel.provider)}</div> <div class="channel-stats svelte-t803t0"><div class="channel-stat svelte-t803t0"><span class="stat-num svelte-t803t0">${escape_html(channel.inbound)}</span> <span class="stat-lbl svelte-t803t0">IN</span></div> <div class="channel-stat svelte-t803t0"><span class="stat-num svelte-t803t0">${escape_html(channel.outbound)}</span> <span class="stat-lbl svelte-t803t0">OUT</span></div></div></div>`);
      }
      $$renderer2.push(`<!--]--></div></div> <div class="section svelte-t803t0"><h3 class="svelte-t803t0">ARCHITECTURE</h3> <div class="arch-diagram svelte-t803t0"><div class="arch-box kraliki svelte-t803t0"><div class="arch-title svelte-t803t0">KRALIKI</div> <div class="arch-content svelte-t803t0"><div class="arch-item svelte-t803t0">Reach UI (this page)</div> <div class="arch-item svelte-t803t0">Orchestration</div> <div class="arch-item svelte-t803t0">Multi-call flows</div></div></div> <div class="arch-arrow svelte-t803t0">→ uses →</div> <div class="arch-box voice svelte-t803t0"><div class="arch-title svelte-t803t0">VOICE BY KRALIKI</div> <div class="arch-content svelte-t803t0"><div class="arch-item svelte-t803t0">Voice Engine</div> <div class="arch-item svelte-t803t0">Call Handling</div> <div class="arch-item svelte-t803t0">Voice AI Agents</div></div></div></div></div> <div class="section svelte-t803t0"><h3 class="svelte-t803t0">INTEGRATION STATUS</h3> <div class="checklist svelte-t803t0"><div${attr_class(`check-item ${stringify("pending")}`, "svelte-t803t0")}>Voice by Kraliki Voice Integration</div> <div class="check-item pending svelte-t803t0">SMS Gateway</div> <div class="check-item pending svelte-t803t0">Email Integration</div> <div class="check-item pending svelte-t803t0">Chat Widget</div> <div class="check-item pending svelte-t803t0">Social APIs</div> <div class="check-item pending svelte-t803t0">Multi-call Orchestration</div></div></div>`);
    }
    $$renderer2.push(`<!--]--></div>`);
  });
}
export {
  _page as default
};
