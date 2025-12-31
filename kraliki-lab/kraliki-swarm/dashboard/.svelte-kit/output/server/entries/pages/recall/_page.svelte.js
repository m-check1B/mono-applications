import "clsx";
function _page($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    let entries = [];
    let searchQuery = "";
    searchQuery.trim() === "" ? entries : entries.filter((entry) => {
      const query = searchQuery.toLowerCase();
      return entry.agent.toLowerCase().includes(query) || entry.key.toLowerCase().includes(query) || entry.text && entry.text.toLowerCase().includes(query);
    });
    $$renderer2.push(`<div class="page svelte-1h3yci6"><div class="page-header svelte-1h3yci6"><h2 class="glitch">Recall // Agent Knowledge Base</h2> `);
    {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--></div> `);
    {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<div class="loading">RETRIEVING_NEURAL_PATTERNS...</div>`);
    }
    $$renderer2.push(`<!--]--></div>`);
  });
}
export {
  _page as default
};
