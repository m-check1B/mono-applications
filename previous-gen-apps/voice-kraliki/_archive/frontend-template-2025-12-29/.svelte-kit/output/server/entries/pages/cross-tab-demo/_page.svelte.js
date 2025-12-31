import { d as attr_class, c as attr, l as clsx, f as stringify, a as store_get, e as ensure_array_like, u as unsubscribe_stores } from "../../../chunks/index2.js";
import { c as crossTabSync, b as authStore } from "../../../chunks/auth2.js";
import { e as escape_html } from "../../../chunks/escaping.js";
function _page($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    var $$store_subs;
    let messages = [];
    let testMessage = "";
    $$renderer2.push(`<div class="cross-tab-demo svelte-7wxcfb"><h1 class="svelte-7wxcfb">Cross-Tab Synchronization Demo</h1> <div class="status svelte-7wxcfb"><div class="status-item svelte-7wxcfb"><strong class="svelte-7wxcfb">BroadcastChannel:</strong> <span${attr_class(clsx(crossTabSync.isAvailable() ? "supported" : "not-supported"), "svelte-7wxcfb")}>${escape_html(crossTabSync.isAvailable() ? "✓ Supported" : "✗ Not Supported")}</span></div> <div class="status-item svelte-7wxcfb"><strong class="svelte-7wxcfb">Auth Status:</strong> <span${attr_class(`auth-status status-${stringify(store_get($$store_subs ??= {}, "$authStore", authStore).status)}`, "svelte-7wxcfb")}>${escape_html(store_get($$store_subs ??= {}, "$authStore", authStore).status)}</span></div> <div class="status-item svelte-7wxcfb"><strong class="svelte-7wxcfb">User:</strong> <span>${escape_html(store_get($$store_subs ??= {}, "$authStore", authStore).user?.email || "Not logged in")}</span></div></div> <div class="instructions svelte-7wxcfb"><h2 class="svelte-7wxcfb">Instructions:</h2> <ol class="svelte-7wxcfb"><li class="svelte-7wxcfb">Open this page in multiple browser tabs (Ctrl+Click or Cmd+Click on the tab)</li> <li class="svelte-7wxcfb">Login or logout in one tab using the auth pages</li> <li class="svelte-7wxcfb">Observe automatic synchronization in other tabs</li> <li class="svelte-7wxcfb">You can also send test messages between tabs using the form below</li></ol></div> <div class="test-section svelte-7wxcfb"><h2 class="svelte-7wxcfb">Test Messages</h2> <div class="input-group svelte-7wxcfb"><input${attr("value", testMessage)} placeholder="Enter test message" class="svelte-7wxcfb"/> <button${attr("disabled", !testMessage.trim(), true)} class="svelte-7wxcfb">Send to Other Tabs</button></div></div> <div class="messages svelte-7wxcfb"><div class="messages-header svelte-7wxcfb"><h3 class="svelte-7wxcfb">Messages from Other Tabs:</h3> <button class="clear-btn svelte-7wxcfb"${attr("disabled", messages.length === 0, true)}>Clear</button></div> <div class="messages-list svelte-7wxcfb">`);
    if (messages.length === 0) {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<p class="no-messages svelte-7wxcfb">No messages yet. Try logging in/out in another tab or send a test message.</p>`);
    } else {
      $$renderer2.push("<!--[!-->");
      $$renderer2.push(`<!--[-->`);
      const each_array = ensure_array_like(messages);
      for (let $$index = 0, $$length = each_array.length; $$index < $$length; $$index++) {
        let message = each_array[$$index];
        $$renderer2.push(`<div class="message svelte-7wxcfb">${escape_html(message)}</div>`);
      }
      $$renderer2.push(`<!--]-->`);
    }
    $$renderer2.push(`<!--]--></div></div> <div class="info-box svelte-7wxcfb"><h3 class="svelte-7wxcfb">How It Works</h3> <p class="svelte-7wxcfb">This feature uses the <code class="svelte-7wxcfb">BroadcastChannel API</code> to synchronize authentication state
			and sessions across multiple browser tabs. When you login, logout, or update your session in
			one tab, all other tabs are automatically notified and updated.</p> <p class="svelte-7wxcfb"><strong>Benefits:</strong></p> <ul class="svelte-7wxcfb"><li class="svelte-7wxcfb">Consistent authentication state across all tabs</li> <li class="svelte-7wxcfb">Automatic logout in all tabs when you logout in one</li> <li class="svelte-7wxcfb">Real-time session updates</li> <li class="svelte-7wxcfb">No server polling required</li></ul></div></div>`);
    if ($$store_subs) unsubscribe_stores($$store_subs);
  });
}
export {
  _page as default
};
