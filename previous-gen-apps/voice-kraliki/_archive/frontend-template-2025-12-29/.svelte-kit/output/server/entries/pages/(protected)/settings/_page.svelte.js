import { c as attr } from "../../../../chunks/index2.js";
import { u as useAppConfig } from "../../../../chunks/useAppConfig.js";
import { S as Save } from "../../../../chunks/save.js";
function _page($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    const config = useAppConfig();
    let backendUrl = config.backendUrl;
    let wsUrl = config.wsUrl;
    $$renderer2.push(`<section class="space-y-6"><header class="space-y-1"><h1 class="text-2xl font-semibold text-text-primary">Console Settings</h1> <p class="text-sm text-text-muted">Update runtime endpoints and experiment flags for the operator console.</p></header> <article class="card"><div class="card-header"><h2 class="text-lg font-semibold text-text-primary">Environment Overrides</h2></div> <div class="space-y-4"><label class="field" for="backend-url"><span class="field-label">Backend URL</span> <input id="backend-url" class="input-field"${attr("value", backendUrl)}/></label> <label class="field" for="ws-url"><span class="field-label">WebSocket URL</span> <input id="ws-url" class="input-field"${attr("value", wsUrl)}/></label> <button class="btn btn-primary">`);
    Save($$renderer2, { class: "size-4" });
    $$renderer2.push(`<!----> Save Changes</button></div></article></section>`);
  });
}
export {
  _page as default
};
