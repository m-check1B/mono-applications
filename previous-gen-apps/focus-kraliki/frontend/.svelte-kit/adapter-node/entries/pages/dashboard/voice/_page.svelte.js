import { s as sanitize_props, a as spread_props, c as slot, e as attr_class, g as ensure_array_like, f as stringify } from "../../../../chunks/index2.js";
import { o as onDestroy } from "../../../../chunks/index-server.js";
import { a as api } from "../../../../chunks/client.js";
import { l as logger } from "../../../../chunks/logger.js";
import { I as Icon } from "../../../../chunks/Icon.js";
import { a as attr } from "../../../../chunks/attributes.js";
import { e as escape_html } from "../../../../chunks/escaping.js";
function Cloud_upload($$renderer, $$props) {
  const $$sanitized_props = sanitize_props($$props);
  const iconNode = [
    ["path", { "d": "M12 13v8" }],
    [
      "path",
      {
        "d": "M4 14.899A7 7 0 1 1 15.71 8h1.79a4.5 4.5 0 0 1 2.5 8.242"
      }
    ],
    ["path", { "d": "m8 17 4-4 4 4" }]
  ];
  Icon($$renderer, spread_props([
    { name: "cloud-upload" },
    $$sanitized_props,
    {
      /**
       * @component @name CloudUpload
       * @description Lucide SVG icon component, renders SVG Element with children.
       *
       * @preview ![img](data:image/svg+xml;base64,PHN2ZyAgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIgogIHdpZHRoPSIyNCIKICBoZWlnaHQ9IjI0IgogIHZpZXdCb3g9IjAgMCAyNCAyNCIKICBmaWxsPSJub25lIgogIHN0cm9rZT0iIzAwMCIgc3R5bGU9ImJhY2tncm91bmQtY29sb3I6ICNmZmY7IGJvcmRlci1yYWRpdXM6IDJweCIKICBzdHJva2Utd2lkdGg9IjIiCiAgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIgogIHN0cm9rZS1saW5lam9pbj0icm91bmQiCj4KICA8cGF0aCBkPSJNMTIgMTN2OCIgLz4KICA8cGF0aCBkPSJNNCAxNC44OTlBNyA3IDAgMSAxIDE1LjcxIDhoMS43OWE0LjUgNC41IDAgMCAxIDIuNSA4LjI0MiIgLz4KICA8cGF0aCBkPSJtOCAxNyA0LTQgNCA0IiAvPgo8L3N2Zz4K) - https://lucide.dev/icons/cloud-upload
       * @see https://lucide.dev/guide/packages/lucide-svelte - Documentation
       *
       * @param {Object} props - Lucide icons props and any valid SVG attribute
       * @returns {FunctionalComponent} Svelte component
       *
       */
      iconNode,
      children: ($$renderer2) => {
        $$renderer2.push(`<!--[-->`);
        slot($$renderer2, $$props, "default", {});
        $$renderer2.push(`<!--]-->`);
      },
      $$slots: { default: true }
    }
  ]));
}
function Mic($$renderer, $$props) {
  const $$sanitized_props = sanitize_props($$props);
  const iconNode = [
    [
      "path",
      { "d": "M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z" }
    ],
    ["path", { "d": "M19 10v2a7 7 0 0 1-14 0v-2" }],
    ["line", { "x1": "12", "x2": "12", "y1": "19", "y2": "22" }]
  ];
  Icon($$renderer, spread_props([
    { name: "mic" },
    $$sanitized_props,
    {
      /**
       * @component @name Mic
       * @description Lucide SVG icon component, renders SVG Element with children.
       *
       * @preview ![img](data:image/svg+xml;base64,PHN2ZyAgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIgogIHdpZHRoPSIyNCIKICBoZWlnaHQ9IjI0IgogIHZpZXdCb3g9IjAgMCAyNCAyNCIKICBmaWxsPSJub25lIgogIHN0cm9rZT0iIzAwMCIgc3R5bGU9ImJhY2tncm91bmQtY29sb3I6ICNmZmY7IGJvcmRlci1yYWRpdXM6IDJweCIKICBzdHJva2Utd2lkdGg9IjIiCiAgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIgogIHN0cm9rZS1saW5lam9pbj0icm91bmQiCj4KICA8cGF0aCBkPSJNMTIgMmEzIDMgMCAwIDAtMyAzdjdhMyAzIDAgMCAwIDYgMFY1YTMgMyAwIDAgMC0zLTNaIiAvPgogIDxwYXRoIGQ9Ik0xOSAxMHYyYTcgNyAwIDAgMS0xNCAwdi0yIiAvPgogIDxsaW5lIHgxPSIxMiIgeDI9IjEyIiB5MT0iMTkiIHkyPSIyMiIgLz4KPC9zdmc+Cg==) - https://lucide.dev/icons/mic
       * @see https://lucide.dev/guide/packages/lucide-svelte - Documentation
       *
       * @param {Object} props - Lucide icons props and any valid SVG attribute
       * @returns {FunctionalComponent} Svelte component
       *
       */
      iconNode,
      children: ($$renderer2) => {
        $$renderer2.push(`<!--[-->`);
        slot($$renderer2, $$props, "default", {});
        $$renderer2.push(`<!--]-->`);
      },
      $$slots: { default: true }
    }
  ]));
}
function Radio($$renderer, $$props) {
  const $$sanitized_props = sanitize_props($$props);
  const iconNode = [
    ["path", { "d": "M4.9 19.1C1 15.2 1 8.8 4.9 4.9" }],
    ["path", { "d": "M7.8 16.2c-2.3-2.3-2.3-6.1 0-8.5" }],
    ["circle", { "cx": "12", "cy": "12", "r": "2" }],
    ["path", { "d": "M16.2 7.8c2.3 2.3 2.3 6.1 0 8.5" }],
    ["path", { "d": "M19.1 4.9C23 8.8 23 15.1 19.1 19" }]
  ];
  Icon($$renderer, spread_props([
    { name: "radio" },
    $$sanitized_props,
    {
      /**
       * @component @name Radio
       * @description Lucide SVG icon component, renders SVG Element with children.
       *
       * @preview ![img](data:image/svg+xml;base64,PHN2ZyAgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIgogIHdpZHRoPSIyNCIKICBoZWlnaHQ9IjI0IgogIHZpZXdCb3g9IjAgMCAyNCAyNCIKICBmaWxsPSJub25lIgogIHN0cm9rZT0iIzAwMCIgc3R5bGU9ImJhY2tncm91bmQtY29sb3I6ICNmZmY7IGJvcmRlci1yYWRpdXM6IDJweCIKICBzdHJva2Utd2lkdGg9IjIiCiAgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIgogIHN0cm9rZS1saW5lam9pbj0icm91bmQiCj4KICA8cGF0aCBkPSJNNC45IDE5LjFDMSAxNS4yIDEgOC44IDQuOSA0LjkiIC8+CiAgPHBhdGggZD0iTTcuOCAxNi4yYy0yLjMtMi4zLTIuMy02LjEgMC04LjUiIC8+CiAgPGNpcmNsZSBjeD0iMTIiIGN5PSIxMiIgcj0iMiIgLz4KICA8cGF0aCBkPSJNMTYuMiA3LjhjMi4zIDIuMyAyLjMgNi4xIDAgOC41IiAvPgogIDxwYXRoIGQ9Ik0xOS4xIDQuOUMyMyA4LjggMjMgMTUuMSAxOS4xIDE5IiAvPgo8L3N2Zz4K) - https://lucide.dev/icons/radio
       * @see https://lucide.dev/guide/packages/lucide-svelte - Documentation
       *
       * @param {Object} props - Lucide icons props and any valid SVG attribute
       * @returns {FunctionalComponent} Svelte component
       *
       */
      iconNode,
      children: ($$renderer2) => {
        $$renderer2.push(`<!--[-->`);
        slot($$renderer2, $$props, "default", {});
        $$renderer2.push(`<!--]-->`);
      },
      $$slots: { default: true }
    }
  ]));
}
function _page($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    let voiceProvider = "gemini-native";
    let conversationHistory = [];
    let voiceStatus = null;
    let sessionId = null;
    let isInitializing = false;
    let uploadError = null;
    let isRecording = false;
    let isProcessing = false;
    let mediaRecorder = null;
    let recordingStream = null;
    const voiceProviderSelectId = "voice-provider-select";
    onDestroy(() => {
      stopRecording(true);
      cleanupRecording();
    });
    async function initializeVoiceSession() {
      if (isInitializing) return;
      isInitializing = true;
      uploadError = null;
      try {
        const providersResponse = await api.assistant.getProviders();
        voiceStatus = providersResponse;
        sessionId = "ready";
      } catch (error) {
        uploadError = error.message || "Failed to check voice providers.";
        logger.error("Failed to initialize voice session", error);
      } finally {
        isInitializing = false;
      }
    }
    function cleanupRecording() {
      recordingStream?.getTracks().forEach((track) => track.stop());
      recordingStream = null;
      mediaRecorder = null;
    }
    function stopRecording(skipProcessing = false) {
      if (!mediaRecorder) {
        cleanupRecording();
        isRecording = false;
        return;
      }
      if (mediaRecorder.state !== "inactive") {
        mediaRecorder.stop();
      } else {
        cleanupRecording();
      }
      isRecording = false;
    }
    $$renderer2.push(`<div class="space-y-6"><div class="flex items-center justify-between"><div><h1 class="text-3xl font-bold flex items-center gap-2">`);
    Radio($$renderer2, { class: "w-8 h-8 text-primary" });
    $$renderer2.push(`<!----> Voice Interface</h1> <p class="text-muted-foreground mt-1">Upload or record audio to let the assistant respond.</p></div> <button class="px-4 py-2 text-sm bg-accent text-accent-foreground rounded-md hover:bg-accent/80 transition-colors">Clear History</button></div> `);
    {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--> <div class="bg-card border border-border rounded-lg p-6 space-y-4"><div class="flex flex-col gap-4 md:flex-row md:items-end md:justify-between"><div><label class="text-sm font-medium"${attr("for", voiceProviderSelectId)}>Voice Provider</label> `);
    $$renderer2.select(
      {
        id: voiceProviderSelectId,
        value: voiceProvider,
        onchange: initializeVoiceSession,
        class: "mt-1 px-3 py-2 bg-background border border-input rounded-md"
      },
      ($$renderer3) => {
        $$renderer3.option({ value: "gemini-native" }, ($$renderer4) => {
          $$renderer4.push(`Gemini Native`);
        });
        $$renderer3.option({ value: "openai-realtime" }, ($$renderer4) => {
          $$renderer4.push(`OpenAI Realtime`);
        });
      }
    );
    $$renderer2.push(` `);
    if (voiceStatus) {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<p class="text-xs text-muted-foreground mt-1">Available: ${escape_html(Object.keys(voiceStatus.providers || {}).join(", ") || "none")}</p>`);
    } else {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--></div> <div class="flex flex-col sm:flex-row gap-4 items-start w-full md:w-auto"><div class="flex flex-col items-start flex-1"><input type="file" class="hidden" id="voice-file" accept="audio/*"/> <button class="px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"${attr("disabled", isProcessing, true)}>`);
    Cloud_upload($$renderer2, { class: "w-4 h-4" });
    $$renderer2.push(`<!----> Upload Audio</button> <p class="text-xs text-muted-foreground mt-1">Supported formats: webm, wav, mp3</p></div> <div class="flex flex-col items-start flex-1"><button${attr_class(`px-4 py-2 rounded-md flex items-center gap-2 transition-colors disabled:opacity-50 disabled:cursor-not-allowed ${isRecording ? "bg-destructive text-destructive-foreground hover:bg-destructive/80" : "bg-secondary text-secondary-foreground hover:bg-secondary/80"}`)}${attr("disabled", true, true)}>`);
    Mic($$renderer2, { class: "w-4 h-4" });
    $$renderer2.push(`<!----> ${escape_html(isRecording ? "Stop Recording" : "Record Live Audio")}</button> <p class="text-xs text-muted-foreground mt-1">${escape_html("Your browser does not support live recording.")}</p> `);
    {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--></div></div></div> `);
    if (uploadError) {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<p class="text-sm text-destructive">${escape_html(uploadError)}</p>`);
    } else {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--></div> <div class="bg-gradient-to-r from-primary/10 to-purple-500/10 border border-primary/20 rounded-lg p-8 space-y-4"><div class="flex flex-col items-center space-y-4"><div class="w-24 h-24 rounded-full bg-primary flex items-center justify-center">`);
    Mic($$renderer2, { class: "w-12 h-12 text-primary-foreground" });
    $$renderer2.push(`<!----></div> <p class="text-lg font-semibold">Choose a provider and upload audio to receive an AI response.</p></div> `);
    if (isRecording) {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<div class="w-full max-w-2xl p-4 bg-yellow-500/10 border border-yellow-500/30 rounded-lg text-yellow-900 dark:text-yellow-100">Recording... click stop to send audio to the assistant.</div>`);
    } else {
      $$renderer2.push("<!--[!-->");
      {
        $$renderer2.push("<!--[!-->");
      }
      $$renderer2.push(`<!--]-->`);
    }
    $$renderer2.push(`<!--]--> `);
    {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--> `);
    {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--></div> `);
    if (conversationHistory.length > 0) {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<div class="bg-card border border-border rounded-lg p-6"><h2 class="text-xl font-semibold mb-4">Conversation History</h2> <div class="space-y-3 max-h-96 overflow-y-auto"><!--[-->`);
      const each_array = ensure_array_like(conversationHistory);
      for (let $$index = 0, $$length = each_array.length; $$index < $$length; $$index++) {
        let message = each_array[$$index];
        $$renderer2.push(`<div${attr_class(`p-3 rounded-lg ${stringify(message.role === "user" ? "bg-primary/10 ml-8" : "bg-accent/50 mr-8")}`)}><div class="text-xs text-muted-foreground mb-1">${escape_html(message.role === "user" ? "You" : "Assistant")} •
              ${escape_html(new Intl.DateTimeFormat("en-US", { hour: "numeric", minute: "2-digit", hour12: true }).format(message.timestamp))}</div> <p>${escape_html(message.content)}</p></div>`);
      }
      $$renderer2.push(`<!--]--></div></div>`);
    } else {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--></div>`);
  });
}
export {
  _page as default
};
