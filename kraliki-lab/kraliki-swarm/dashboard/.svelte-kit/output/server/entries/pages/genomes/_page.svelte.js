import "clsx";
function _page($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    let selectedCli = "all";
    let sortBy = "spawns";
    $$renderer2.push(`<div class="page svelte-95wonh"><div class="page-header svelte-95wonh"><h2 class="glitch svelte-95wonh">Genome Registry // Template Packs</h2> <div class="controls svelte-95wonh">`);
    $$renderer2.select(
      { value: selectedCli, class: "filter-select" },
      ($$renderer3) => {
        $$renderer3.option(
          { value: "all", class: "" },
          ($$renderer4) => {
            $$renderer4.push(`ALL CLIs`);
          },
          "svelte-95wonh"
        );
        {
          $$renderer3.push("<!--[!-->");
        }
        $$renderer3.push(`<!--]-->`);
      },
      "svelte-95wonh"
    );
    $$renderer2.push(` `);
    $$renderer2.select(
      { value: sortBy, class: "filter-select" },
      ($$renderer3) => {
        $$renderer3.option(
          { value: "spawns", class: "" },
          ($$renderer4) => {
            $$renderer4.push(`BY SPAWNS`);
          },
          "svelte-95wonh"
        );
        $$renderer3.option(
          { value: "points", class: "" },
          ($$renderer4) => {
            $$renderer4.push(`BY POINTS`);
          },
          "svelte-95wonh"
        );
        $$renderer3.option(
          { value: "name", class: "" },
          ($$renderer4) => {
            $$renderer4.push(`BY NAME`);
          },
          "svelte-95wonh"
        );
      },
      "svelte-95wonh"
    );
    $$renderer2.push(` <button class="brutal-btn svelte-95wonh">REFRESH</button></div></div> `);
    {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<div class="loading-state svelte-95wonh"><span class="loading-text svelte-95wonh">LOADING_GENOME_REGISTRY...</span></div>`);
    }
    $$renderer2.push(`<!--]--></div>`);
  });
}
export {
  _page as default
};
