import { e as ensure_array_like } from "../../../../chunks/index2.js";
import { c as createQuery, d as fetchCampaigns } from "../../../../chunks/calls.js";
import "../../../../chunks/auth2.js";
import "../../../../chunks/queryClient.js";
import { C as Cloud_upload } from "../../../../chunks/cloud-upload.js";
import { F as File_text } from "../../../../chunks/file-text.js";
import { e as escape_html } from "../../../../chunks/escaping.js";
function _page($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    const campaignsQuery = createQuery({
      queryKey: ["campaigns"],
      queryFn: fetchCampaigns,
      staleTime: 6e4
    });
    let campaigns = [];
    let isLoading = false;
    let errorMessage = null;
    campaignsQuery.subscribe((result) => {
      campaigns = result.data ?? [];
      isLoading = result.isPending;
      errorMessage = result.isError ? result.error?.message ?? "Failed to load campaigns." : null;
    });
    $$renderer2.push(`<section class="space-y-6"><header class="flex flex-col gap-3 md:flex-row md:items-center md:justify-between"><div class="space-y-1"><h1 class="text-2xl font-semibold text-text-primary">Campaign Library</h1> <p class="text-sm text-text-muted">Manage AI-driven calling campaigns, preview steps, and sync updates from the FastAPI backend.</p></div> <button class="btn btn-primary">`);
    Cloud_upload($$renderer2, { class: "size-4" });
    $$renderer2.push(`<!----> Import Campaign</button></header> `);
    if (errorMessage) {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<div class="rounded-lg border border-error/40 bg-error/10 px-3 py-2 text-sm text-error">${escape_html(errorMessage)} <button class="ml-2 text-primary underline" type="button">Retry</button></div>`);
    } else {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--> `);
    if (isLoading && !campaigns.length) {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<p class="text-xs text-text-muted">Loading campaigns…</p>`);
    } else {
      $$renderer2.push("<!--[!-->");
      if (campaigns.length === 0) {
        $$renderer2.push("<!--[-->");
        $$renderer2.push(`<p class="text-sm text-text-secondary">No campaigns found.</p>`);
      } else {
        $$renderer2.push("<!--[!-->");
        $$renderer2.push(`<div class="grid gap-4 md:grid-cols-2 xl:grid-cols-3"><!--[-->`);
        const each_array = ensure_array_like(campaigns);
        for (let $$index = 0, $$length = each_array.length; $$index < $$length; $$index++) {
          let campaign = each_array[$$index];
          $$renderer2.push(`<article class="card bg-secondary/80"><div class="card-header"><div class="flex items-center gap-2 text-text-primary">`);
          File_text($$renderer2, { class: "size-4" });
          $$renderer2.push(`<!----> <h2 class="text-lg font-semibold">${escape_html(campaign.name)}</h2></div></div> <ul class="text-sm text-text-secondary"><li>Language: ${escape_html(campaign.language ?? "—")}</li> <li>Steps: ${escape_html(campaign.stepsCount ?? (Array.isArray(campaign.steps) ? campaign.steps.length : "—"))}</li></ul></article>`);
        }
        $$renderer2.push(`<!--]--></div>`);
      }
      $$renderer2.push(`<!--]-->`);
    }
    $$renderer2.push(`<!--]--></section>`);
  });
}
export {
  _page as default
};
