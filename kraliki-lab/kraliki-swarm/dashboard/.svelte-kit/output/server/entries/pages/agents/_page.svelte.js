import { a as attr_class, b as stringify } from "../../../chunks/index2.js";
import { b as attr } from "../../../chunks/attributes.js";
import { e as escape_html } from "../../../chunks/escaping.js";
function _page($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    let genomes = [];
    let circuitBreakers = {};
    let resetting = false;
    let softResetting = false;
    let powering = false;
    let pausing = false;
    genomes.reduce(
      (acc, g) => {
        if (!acc[g.cli]) acc[g.cli] = [];
        acc[g.cli].push(g);
        return acc;
      },
      {}
    );
    const cbEntries = Object.entries(circuitBreakers);
    cbEntries.filter(([_, cb]) => cb.state === "open").length;
    $$renderer2.push(`<div class="page svelte-h3sa6j"><div class="page-header svelte-h3sa6j"><h2 class="glitch svelte-h3sa6j">Agent Management // Swarm Control</h2> <div class="header-controls svelte-h3sa6j">`);
    {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--> `);
    {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--> <button class="brutal-btn yellow-btn svelte-h3sa6j"${attr("disabled", softResetting, true)}>${escape_html(`SOFT_RESET${""}`)}</button> <button class="brutal-btn red-btn svelte-h3sa6j"${attr("disabled", resetting, true)} title="Nuclear option - restarts everything">${escape_html("HARD_RESET")}</button> <button${attr_class(`brutal-btn ${stringify("orange-btn")}`, "svelte-h3sa6j")}${attr("disabled", pausing, true)}${attr("title", "Pause all swarm activities and kill running agents")}>`);
    {
      $$renderer2.push("<!--[!-->");
      $$renderer2.push(`${escape_html("SLEEP")}`);
    }
    $$renderer2.push(`<!--]--></button> <button class="brutal-btn orange-btn svelte-h3sa6j"${attr("disabled", powering, true)} title="Restart core swarm services">RESTART</button> <button class="brutal-btn svelte-h3sa6j"${attr("disabled", powering, true)}${attr("title", "Power on core swarm services")}>${escape_html("POWER")}</button></div></div> `);
    {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<div class="loading svelte-h3sa6j">INQUIRY_INTO_SWARM_STATE...</div>`);
    }
    $$renderer2.push(`<!--]--></div>`);
  });
}
export {
  _page as default
};
