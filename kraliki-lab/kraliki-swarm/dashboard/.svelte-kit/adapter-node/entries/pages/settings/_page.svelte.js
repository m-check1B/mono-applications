import { s as store_get, u as unsubscribe_stores } from "../../../chunks/index2.js";
import { w as workspaceMode } from "../../../chunks/mode.js";
import { b as attr } from "../../../chunks/attributes.js";
function _page($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    var $$store_subs;
    let settings = {
      theme: "dark",
      refreshInterval: 30,
      notifications: true,
      soundAlerts: false
    };
    $$renderer2.push(`<div class="page svelte-1i19ct2"><div class="page-header svelte-1i19ct2"><h2 class="glitch">Settings // Configuration</h2> `);
    {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--></div> <div class="settings-grid svelte-1i19ct2"><div class="card svelte-1i19ct2"><h3 class="svelte-1i19ct2">WORKSPACE_MODE</h3> <div class="setting-row svelte-1i19ct2"><div class="setting-info svelte-1i19ct2"><span class="setting-name svelte-1i19ct2">Access Mode</span> <span class="setting-desc svelte-1i19ct2">Controls editing capabilities</span></div> `);
    $$renderer2.select(
      {
        value: store_get($$store_subs ??= {}, "$workspaceMode", workspaceMode),
        class: ""
      },
      ($$renderer3) => {
        $$renderer3.option({ value: "dev" }, ($$renderer4) => {
          $$renderer4.push(`DEV (Full Access)`);
        });
        $$renderer3.option({ value: "normal" }, ($$renderer4) => {
          $$renderer4.push(`NORMAL (Standard)`);
        });
        $$renderer3.option({ value: "readonly" }, ($$renderer4) => {
          $$renderer4.push(`READ-ONLY (View Only)`);
        });
      },
      "svelte-1i19ct2"
    );
    $$renderer2.push(`</div> <div class="mode-info svelte-1i19ct2">`);
    if (store_get($$store_subs ??= {}, "$workspaceMode", workspaceMode) === "dev") {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<span class="mode-badge dev svelte-1i19ct2">DEV MODE: Full CRUD + agent control</span>`);
    } else {
      $$renderer2.push("<!--[!-->");
      if (store_get($$store_subs ??= {}, "$workspaceMode", workspaceMode) === "readonly") {
        $$renderer2.push("<!--[-->");
        $$renderer2.push(`<span class="mode-badge readonly svelte-1i19ct2">READ-ONLY: View data, export results</span>`);
      } else {
        $$renderer2.push("<!--[!-->");
        $$renderer2.push(`<span class="mode-badge normal svelte-1i19ct2">NORMAL: Standard access</span>`);
      }
      $$renderer2.push(`<!--]-->`);
    }
    $$renderer2.push(`<!--]--></div></div> <div class="card svelte-1i19ct2"><h3 class="svelte-1i19ct2">APPEARANCE</h3> <div class="setting-row svelte-1i19ct2"><div class="setting-info svelte-1i19ct2"><span class="setting-name svelte-1i19ct2">Theme</span> <span class="setting-desc svelte-1i19ct2">Dashboard color scheme</span></div> `);
    $$renderer2.select(
      { value: settings.theme, class: "" },
      ($$renderer3) => {
        $$renderer3.option({ value: "dark" }, ($$renderer4) => {
          $$renderer4.push(`Dark`);
        });
        $$renderer3.option({ value: "light" }, ($$renderer4) => {
          $$renderer4.push(`Light`);
        });
      },
      "svelte-1i19ct2"
    );
    $$renderer2.push(`</div></div> <div class="card svelte-1i19ct2"><h3 class="svelte-1i19ct2">DATA_REFRESH</h3> <div class="setting-row svelte-1i19ct2"><div class="setting-info svelte-1i19ct2"><span class="setting-name svelte-1i19ct2">Auto Refresh Interval</span> <span class="setting-desc svelte-1i19ct2">How often to refresh data (seconds)</span></div> `);
    $$renderer2.select(
      { value: settings.refreshInterval, class: "" },
      ($$renderer3) => {
        $$renderer3.option({ value: 15 }, ($$renderer4) => {
          $$renderer4.push(`15s`);
        });
        $$renderer3.option({ value: 30 }, ($$renderer4) => {
          $$renderer4.push(`30s`);
        });
        $$renderer3.option({ value: 60 }, ($$renderer4) => {
          $$renderer4.push(`60s`);
        });
        $$renderer3.option({ value: 120 }, ($$renderer4) => {
          $$renderer4.push(`2m`);
        });
      },
      "svelte-1i19ct2"
    );
    $$renderer2.push(`</div></div> <div class="card svelte-1i19ct2"><h3 class="svelte-1i19ct2">NOTIFICATIONS</h3> <div class="setting-row svelte-1i19ct2"><div class="setting-info svelte-1i19ct2"><span class="setting-name svelte-1i19ct2">Browser Notifications</span> <span class="setting-desc svelte-1i19ct2">Get notified of important events</span></div> <label class="toggle svelte-1i19ct2"><input type="checkbox"${attr("checked", settings.notifications, true)} class="svelte-1i19ct2"/> <span class="toggle-slider svelte-1i19ct2"></span></label></div> <div class="setting-row svelte-1i19ct2"><div class="setting-info svelte-1i19ct2"><span class="setting-name svelte-1i19ct2">Sound Alerts</span> <span class="setting-desc svelte-1i19ct2">Play sounds for critical alerts</span></div> <label class="toggle svelte-1i19ct2"><input type="checkbox"${attr("checked", settings.soundAlerts, true)} class="svelte-1i19ct2"/> <span class="toggle-slider svelte-1i19ct2"></span></label></div></div> <div class="card svelte-1i19ct2"><h3 class="svelte-1i19ct2">ACCOUNT</h3> <div class="account-info svelte-1i19ct2"><div class="avatar svelte-1i19ct2">👤</div> <div class="account-details svelte-1i19ct2"><span class="account-name svelte-1i19ct2">LOCAL_ROOT</span> <span class="account-role svelte-1i19ct2">Administrator</span></div></div> <div class="account-actions svelte-1i19ct2"><a href="/auth/login" class="brutal-btn small svelte-1i19ct2">SWITCH_USER</a></div></div> <div class="card span-2 svelte-1i19ct2"><h3 class="svelte-1i19ct2">SYSTEM_INFO</h3> <div class="info-grid svelte-1i19ct2"><div class="info-item svelte-1i19ct2"><span class="info-label svelte-1i19ct2">VERSION</span> <span class="info-value svelte-1i19ct2">0.1.0-alpha</span></div> <div class="info-item svelte-1i19ct2"><span class="info-label svelte-1i19ct2">DASHBOARD_PORT</span> <span class="info-value svelte-1i19ct2">8099</span></div> <div class="info-item svelte-1i19ct2"><span class="info-label svelte-1i19ct2">ARENA_PORT</span> <span class="info-value svelte-1i19ct2">3021</span></div> <div class="info-item svelte-1i19ct2"><span class="info-label svelte-1i19ct2">MEMORY_PORT</span> <span class="info-value svelte-1i19ct2">3020</span></div></div></div> <div class="card danger svelte-1i19ct2"><h3 class="svelte-1i19ct2">DANGER_ZONE</h3> <div class="setting-row svelte-1i19ct2"><div class="setting-info svelte-1i19ct2"><span class="setting-name svelte-1i19ct2">Reset Dashboard</span> <span class="setting-desc svelte-1i19ct2">Clear all local settings and cache</span></div> <button class="brutal-btn danger small svelte-1i19ct2">RESET</button></div></div></div> <div class="save-bar svelte-1i19ct2"><button class="brutal-btn primary svelte-1i19ct2">SAVE_SETTINGS</button></div></div>`);
    if ($$store_subs) unsubscribe_stores($$store_subs);
  });
}
export {
  _page as default
};
