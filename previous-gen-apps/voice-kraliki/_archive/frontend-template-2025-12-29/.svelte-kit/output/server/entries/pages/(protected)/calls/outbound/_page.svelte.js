import { g as sanitize_props, j as spread_props, s as slot, a as store_get, e as ensure_array_like, c as attr, u as unsubscribe_stores } from "../../../../../chunks/index2.js";
import { o as onDestroy } from "../../../../../chunks/index-server.js";
import { u as useAppConfig } from "../../../../../chunks/useAppConfig.js";
import { c as createQuery, f as fetchAvailableVoices, a as fetchAvailableModels, b as fetchVoiceConfig } from "../../../../../chunks/calls.js";
import "../../../../../chunks/env.js";
import "../../../../../chunks/auth2.js";
import { c as createProviderSession, P as ProviderSwitcher } from "../../../../../chunks/providerSession.js";
import { c as createAudioManager, P as Phone_off } from "../../../../../chunks/audioManager.js";
import { R as Refresh_ccw, A as AIInsightsPanel } from "../../../../../chunks/AIInsightsPanel.js";
import { F as File_text } from "../../../../../chunks/file-text.js";
import { P as Plus } from "../../../../../chunks/plus.js";
import { I as Icon } from "../../../../../chunks/Icon.js";
import { T as Trash_2 } from "../../../../../chunks/trash-2.js";
import { A as Activity } from "../../../../../chunks/activity.js";
import { e as escape_html } from "../../../../../chunks/escaping.js";
function Loader_circle($$renderer, $$props) {
  const $$sanitized_props = sanitize_props($$props);
  const iconNode = [["path", { "d": "M21 12a9 9 0 1 1-6.219-8.56" }]];
  Icon($$renderer, spread_props([
    { name: "loader-circle" },
    $$sanitized_props,
    {
      /**
       * @component @name LoaderCircle
       * @description Lucide SVG icon component, renders SVG Element with children.
       *
       * @preview ![img](data:image/svg+xml;base64,PHN2ZyAgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIgogIHdpZHRoPSIyNCIKICBoZWlnaHQ9IjI0IgogIHZpZXdCb3g9IjAgMCAyNCAyNCIKICBmaWxsPSJub25lIgogIHN0cm9rZT0iIzAwMCIgc3R5bGU9ImJhY2tncm91bmQtY29sb3I6ICNmZmY7IGJvcmRlci1yYWRpdXM6IDJweCIKICBzdHJva2Utd2lkdGg9IjIiCiAgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIgogIHN0cm9rZS1saW5lam9pbj0icm91bmQiCj4KICA8cGF0aCBkPSJNMjEgMTJhOSA5IDAgMSAxLTYuMjE5LTguNTYiIC8+Cjwvc3ZnPgo=) - https://lucide.dev/icons/loader-circle
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
function Phone_outgoing($$renderer, $$props) {
  const $$sanitized_props = sanitize_props($$props);
  const iconNode = [
    ["polyline", { "points": "22 8 22 2 16 2" }],
    ["line", { "x1": "16", "x2": "22", "y1": "8", "y2": "2" }],
    [
      "path",
      {
        "d": "M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"
      }
    ]
  ];
  Icon($$renderer, spread_props([
    { name: "phone-outgoing" },
    $$sanitized_props,
    {
      /**
       * @component @name PhoneOutgoing
       * @description Lucide SVG icon component, renders SVG Element with children.
       *
       * @preview ![img](data:image/svg+xml;base64,PHN2ZyAgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIgogIHdpZHRoPSIyNCIKICBoZWlnaHQ9IjI0IgogIHZpZXdCb3g9IjAgMCAyNCAyNCIKICBmaWxsPSJub25lIgogIHN0cm9rZT0iIzAwMCIgc3R5bGU9ImJhY2tncm91bmQtY29sb3I6ICNmZmY7IGJvcmRlci1yYWRpdXM6IDJweCIKICBzdHJva2Utd2lkdGg9IjIiCiAgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIgogIHN0cm9rZS1saW5lam9pbj0icm91bmQiCj4KICA8cG9seWxpbmUgcG9pbnRzPSIyMiA4IDIyIDIgMTYgMiIgLz4KICA8bGluZSB4MT0iMTYiIHgyPSIyMiIgeTE9IjgiIHkyPSIyIiAvPgogIDxwYXRoIGQ9Ik0yMiAxNi45MnYzYTIgMiAwIDAgMS0yLjE4IDIgMTkuNzkgMTkuNzkgMCAwIDEtOC42My0zLjA3IDE5LjUgMTkuNSAwIDAgMS02LTYgMTkuNzkgMTkuNzkgMCAwIDEtMy4wNy04LjY3QTIgMiAwIDAgMSA0LjExIDJoM2EyIDIgMCAwIDEgMiAxLjcyIDEyLjg0IDEyLjg0IDAgMCAwIC43IDIuODEgMiAyIDAgMCAxLS40NSAyLjExTDguMDkgOS45MWExNiAxNiAwIDAgMCA2IDZsMS4yNy0xLjI3YTIgMiAwIDAgMSAyLjExLS40NSAxMi44NCAxMi44NCAwIDAgMCAyLjgxLjdBMiAyIDAgMCAxIDIyIDE2LjkyeiIgLz4KPC9zdmc+Cg==) - https://lucide.dev/icons/phone-outgoing
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
    var $$store_subs;
    const config = useAppConfig();
    const AVAILABLE_LANGUAGES = [
      { code: "en", label: "English" },
      { code: "es", label: "Spanish" },
      { code: "cz", label: "Czech" }
    ];
    const AVAILABLE_COUNTRIES = [
      {
        code: "US",
        name: "United States",
        flag: "🇺🇸",
        phoneNumber: config.countryFromNumbers.US ?? config.defaultFromNumber
      },
      {
        code: "CZ",
        name: "Czech Republic",
        flag: "🇨🇿",
        phoneNumber: config.countryFromNumbers.CZ ?? config.defaultFromNumber
      },
      {
        code: "ES",
        name: "Spain",
        flag: "🇪🇸",
        phoneNumber: config.countryFromNumbers.ES ?? config.defaultFromNumber
      }
    ];
    const SAMPLE_CAMPAIGNS = [
      {
        id: 1,
        title: "Insurance Renewal",
        description: "Multi-step follow-up call with sentiment tracking."
      },
      {
        id: 2,
        title: "Solar Outreach",
        description: "Energy-efficiency appointment setting."
      },
      {
        id: 3,
        title: "Customer Re-engagement",
        description: "Generic follow-up script for dormant accounts."
      }
    ];
    let audioMode = "twilio";
    let enableDeEssing = false;
    let selectedCountry = "CZ";
    let fromPhoneNumber = config.defaultFromNumber;
    let selectedModel = "";
    let selectedVoice = "";
    let selectedLanguage = "en";
    let aiInstructions = "";
    let isLoadingScript = false;
    let isProcessing = false;
    let lastError = null;
    let callStatus = "idle";
    let companies = [{ name: "", phone: "" }];
    let transcriptMessages = [];
    let currentIntent = null;
    let currentSentiment = null;
    let suggestions = [];
    let availableProviders = [
      {
        id: "gemini",
        name: "Google Gemini Live",
        status: "available",
        capabilities: { realtime: true, multimodal: true, functionCalling: true }
      },
      {
        id: "openai",
        name: "OpenAI Realtime",
        status: "available",
        capabilities: { realtime: true, multimodal: false, functionCalling: true }
      },
      {
        id: "deepgram_nova3",
        name: "Deepgram Nova 3",
        status: "available",
        capabilities: { realtime: true, multimodal: false, functionCalling: true }
      }
    ];
    let currentProvider = "gemini";
    const providerSession = createProviderSession({ provider: currentProvider });
    let sessionState = providerSession.getState();
    const unsubscribeSession = providerSession.subscribe((value) => {
      sessionState = value;
    });
    const audioManager = createAudioManager();
    let audioState = audioManager.getState();
    const unsubscribeAudio = audioManager.subscribe((value) => {
      audioState = value;
    });
    audioManager.sendCapturedFrame((buffer) => {
      try {
        const base64 = btoa(String.fromCharCode(...new Uint8Array(buffer.buffer)));
        providerSession.send(JSON.stringify({ type: "audio-data", audioData: base64 }));
      } catch (error) {
        console.error("Failed to send captured audio frame", error);
      }
    });
    const voicesQuery = createQuery({
      queryKey: ["available-voices"],
      queryFn: fetchAvailableVoices
    });
    const modelsQuery = createQuery({
      queryKey: ["available-models"],
      queryFn: fetchAvailableModels
    });
    const voiceConfigQuery = createQuery({ queryKey: ["voice-config"], queryFn: fetchVoiceConfig });
    const voicesData = store_get($$store_subs ??= {}, "$voicesQuery", voicesQuery).data;
    const modelsData = store_get($$store_subs ??= {}, "$modelsQuery", modelsQuery).data;
    const voiceConfigData = store_get($$store_subs ??= {}, "$voiceConfigQuery", voiceConfigQuery).data;
    const availableVoiceDetails = voicesData?.voices ?? {};
    const availableVoices = Object.keys(availableVoiceDetails);
    const voiceDescriptions = voiceConfigData?.voiceDescriptions ?? {};
    const availableModels = modelsData?.availableModels ?? {};
    voicesData?.currentDefault;
    modelsData?.defaultModel;
    const isConfigurationLoading = store_get($$store_subs ??= {}, "$voicesQuery", voicesQuery).isPending || store_get($$store_subs ??= {}, "$modelsQuery", modelsQuery).isPending || store_get($$store_subs ??= {}, "$voiceConfigQuery", voiceConfigQuery).isPending;
    onDestroy(() => {
      providerSession.disconnect();
      unsubscribeSession();
      void audioManager.cleanup();
      unsubscribeAudio();
    });
    function resolveVoiceLabel(voice) {
      const description = voiceDescriptions[voice];
      if (description) return description;
      const detail = availableVoiceDetails[voice];
      if (detail) {
        const meta = [detail.gender, detail.characteristics].filter(Boolean).join(" · ");
        return meta ? `${voice} — ${meta}` : voice;
      }
      return voice;
    }
    function statusLabel(status) {
      switch (status) {
        case "in-progress":
          return "In progress";
        case "polling-results":
          return "Processing results";
        case "completed":
          return "Completed";
        case "failed":
          return "Failed";
        default:
          return "Pending";
      }
    }
    function callStatusDescription(status) {
      switch (status) {
        case "configuring":
          return "Sending session configuration to backend...";
        case "initiating-call":
          return "Dialing target company via telephony provider...";
        case "in-progress":
          return "Live call in progress.";
        case "polling-results":
          return "Awaiting call summary and analytics...";
        case "completed":
          return "Call completed successfully. Review summary below.";
        case "failed":
          return "Call failed or was stopped. Check logs and retry.";
        default:
          return "Ready to launch the next outbound call.";
      }
    }
    async function handleProviderSwitch(providerId) {
      console.log("Switching to provider:", providerId);
      const newProvider = providerId;
      if (newProvider === currentProvider) return;
      try {
        await providerSession.switchProvider(newProvider);
        currentProvider = newProvider;
        availableProviders = availableProviders.map((p) => ({ ...p, status: p.id === providerId ? "active" : "available" }));
        transcriptMessages = [
          ...transcriptMessages,
          {
            role: "assistant",
            content: `🔄 Switched to ${availableProviders.find((p) => p.id === providerId)?.name}`,
            timestamp: /* @__PURE__ */ new Date()
          }
        ];
      } catch (error) {
        console.error("Failed to switch provider:", error);
        lastError = "Failed to switch provider. Please try again.";
      }
    }
    function handleSuggestionAction(suggestionId, action) {
      suggestions = suggestions.map((s) => s.id === suggestionId ? { ...s, status: action === "accept" ? "accepted" : "rejected" } : s);
      if (action === "accept") {
        const suggestion = suggestions.find((s) => s.id === suggestionId);
        if (suggestion) {
          providerSession.send(JSON.stringify({
            type: "suggestion-action",
            suggestionId,
            action: "accept",
            suggestion
          }));
        }
      }
    }
    $$renderer2.push(`<section class="space-y-6"><header class="space-y-1"><h1 class="text-2xl font-semibold text-text-primary">Outbound Call Orchestration</h1> <p class="text-sm text-text-muted">Configure AI voice, language, and campaign script, then launch targeted outbound sessions with Stack 2026 ergonomics.</p></header> `);
    if (lastError) {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<div class="rounded-xl border border-error/40 bg-error/10 px-4 py-3 text-sm text-error">${escape_html(lastError)}</div>`);
    } else {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--> <div class="grid gap-4 xl:grid-cols-[2fr_3fr]"><div class="space-y-4">`);
    ProviderSwitcher($$renderer2, {
      providers: availableProviders,
      currentProvider,
      isLive: sessionState.status === "connected",
      onSwitch: handleProviderSwitch
    });
    $$renderer2.push(`<!----> <article class="card"><div class="card-header"><h2 class="text-lg font-semibold text-text-primary">Call Configuration</h2> <span class="text-xs text-text-muted">Telephony source • AI runtime • Output language</span></div> <div class="space-y-4">`);
    if (store_get($$store_subs ??= {}, "$voicesQuery", voicesQuery).isError || store_get($$store_subs ??= {}, "$modelsQuery", modelsQuery).isError) {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<p class="rounded-lg border border-error/40 bg-error/10 px-3 py-2 text-sm text-error">Failed to load voice/model configuration. <button class="text-primary underline" type="button">Retry</button></p>`);
    } else {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--> `);
    if (isConfigurationLoading) {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<p class="text-xs text-text-muted">Loading configuration…</p>`);
    } else {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--> <label class="field" for="country-select"><span class="field-label">Country &amp; Twilio Number</span> `);
    $$renderer2.select(
      {
        id: "country-select",
        class: "select-field",
        value: selectedCountry
      },
      ($$renderer3) => {
        $$renderer3.push(`<!--[-->`);
        const each_array = ensure_array_like(AVAILABLE_COUNTRIES);
        for (let $$index = 0, $$length = each_array.length; $$index < $$length; $$index++) {
          let country = each_array[$$index];
          $$renderer3.option({ value: country.code }, ($$renderer4) => {
            $$renderer4.push(`${escape_html(country.flag)} ${escape_html(country.name)} (${escape_html(country.phoneNumber)})`);
          });
        }
        $$renderer3.push(`<!--]-->`);
      }
    );
    $$renderer2.push(`</label> <label class="field" for="from-number"><span class="field-label">From Phone Number</span> <input id="from-number" class="input-field"${attr("value", fromPhoneNumber)} readonly/></label> <label class="field" for="model-select"><span class="field-label">AI Model</span> `);
    $$renderer2.select(
      {
        id: "model-select",
        class: "select-field",
        value: selectedModel
      },
      ($$renderer3) => {
        $$renderer3.push(`<!--[-->`);
        const each_array_1 = ensure_array_like(Object.entries(availableModels));
        for (let $$index_1 = 0, $$length = each_array_1.length; $$index_1 < $$length; $$index_1++) {
          let [modelId, modelInfo] = each_array_1[$$index_1];
          $$renderer3.option({ value: modelId }, ($$renderer4) => {
            $$renderer4.push(`${escape_html(typeof modelInfo === "object" && modelInfo && "name" in modelInfo ? modelInfo.name : modelId)}`);
          });
        }
        $$renderer3.push(`<!--]-->`);
      }
    );
    $$renderer2.push(`</label> <label class="field" for="voice-select"><span class="field-label">AI Voice</span> `);
    $$renderer2.select(
      {
        id: "voice-select",
        class: "select-field",
        value: selectedVoice
      },
      ($$renderer3) => {
        $$renderer3.push(`<!--[-->`);
        const each_array_2 = ensure_array_like(availableVoices);
        for (let $$index_2 = 0, $$length = each_array_2.length; $$index_2 < $$length; $$index_2++) {
          let voice = each_array_2[$$index_2];
          $$renderer3.option({ value: voice }, ($$renderer4) => {
            $$renderer4.push(`${escape_html(resolveVoiceLabel(voice))}`);
          });
        }
        $$renderer3.push(`<!--]-->`);
      }
    );
    $$renderer2.push(`</label> <div class="grid gap-4 md:grid-cols-2"><label class="field" for="language-select"><span class="field-label">Language</span> `);
    $$renderer2.select(
      {
        id: "language-select",
        class: "select-field",
        value: selectedLanguage
      },
      ($$renderer3) => {
        $$renderer3.push(`<!--[-->`);
        const each_array_3 = ensure_array_like(AVAILABLE_LANGUAGES);
        for (let $$index_3 = 0, $$length = each_array_3.length; $$index_3 < $$length; $$index_3++) {
          let language = each_array_3[$$index_3];
          $$renderer3.option({ value: language.code }, ($$renderer4) => {
            $$renderer4.push(`${escape_html(language.label)}`);
          });
        }
        $$renderer3.push(`<!--]-->`);
      }
    );
    $$renderer2.push(`</label> <label class="field" for="audio-mode"><span class="field-label">Audio Mode</span> `);
    $$renderer2.select({ id: "audio-mode", class: "select-field", value: audioMode }, ($$renderer3) => {
      $$renderer3.option({ value: "twilio" }, ($$renderer4) => {
        $$renderer4.push(`Twilio PSTN`);
      });
      $$renderer3.option({ value: "local" }, ($$renderer4) => {
        $$renderer4.push(`Local WebRTC (beta)`);
      });
    });
    $$renderer2.push(`</label></div> <div class="flex items-center justify-between rounded-xl border border-divider bg-secondary px-4 py-3"><div><p class="text-sm font-medium text-text-primary">AI De-essing</p> <p class="text-xs text-text-muted">Reduce harsh sibilance for sharp telephony audio.</p></div> <label class="relative inline-flex cursor-pointer items-center"><input type="checkbox" class="peer sr-only"${attr("checked", enableDeEssing, true)}/> <span class="peer h-6 w-11 rounded-full bg-divider transition peer-checked:bg-primary-soft"></span> <span class="absolute left-1 top-1 h-4 w-4 rounded-full bg-text-muted transition peer-checked:translate-x-5 peer-checked:bg-primary"></span></label></div></div></article> <article class="card"><div class="card-header"><h2 class="text-lg font-semibold text-text-primary">Campaign Script &amp; Instructions</h2> <button class="btn btn-ghost">`);
    Refresh_ccw($$renderer2, { class: "size-4" });
    $$renderer2.push(`<!----> Reset Summary</button></div> <div class="space-y-4"><div class="grid gap-2 md:grid-cols-3"><!--[-->`);
    const each_array_4 = ensure_array_like(SAMPLE_CAMPAIGNS);
    for (let $$index_4 = 0, $$length = each_array_4.length; $$index_4 < $$length; $$index_4++) {
      let campaign = each_array_4[$$index_4];
      $$renderer2.push(`<button class="btn btn-secondary"${attr("disabled", isLoadingScript, true)}>`);
      File_text($$renderer2, { class: "size-4" });
      $$renderer2.push(`<!----> ${escape_html(campaign.title)}</button>`);
    }
    $$renderer2.push(`<!--]--></div> <textarea class="textarea-field" rows="8" placeholder="Paste or generate AI instructions here...">`);
    const $$body = escape_html(aiInstructions);
    if ($$body) {
      $$renderer2.push(`${$$body}`);
    }
    $$renderer2.push(`</textarea></div></article></div> <div class="space-y-4"><article class="card"><div class="card-header"><h2 class="text-lg font-semibold text-text-primary">Target Companies</h2> <button class="btn btn-ghost">`);
    Plus($$renderer2, { class: "size-4" });
    $$renderer2.push(`<!----> Add company</button></div> <div class="space-y-3"><!--[-->`);
    const each_array_5 = ensure_array_like(companies);
    for (let index = 0, $$length = each_array_5.length; index < $$length; index++) {
      let company = each_array_5[index];
      $$renderer2.push(`<div class="rounded-2xl border border-divider bg-secondary/80 p-4"><div class="flex items-start justify-between gap-3"><div class="grid flex-1 gap-3 md:grid-cols-2"><label class="field"${attr("for", `company-${index}`)}><span class="field-label">Company</span> <input${attr("id", `company-${index}`)} class="input-field"${attr("value", company.name)}/></label> <label class="field"${attr("for", `phone-${index}`)}><span class="field-label">Phone</span> <input${attr("id", `phone-${index}`)} class="input-field"${attr("value", company.phone)}/></label></div> <div class="flex items-center gap-2"><button class="btn btn-primary"${attr("disabled", isProcessing, true)}>`);
      if (company.status === "in-progress") {
        $$renderer2.push("<!--[-->");
        Loader_circle($$renderer2, { class: "size-4 animate-spin" });
      } else {
        $$renderer2.push("<!--[!-->");
        Phone_outgoing($$renderer2, { class: "size-4" });
      }
      $$renderer2.push(`<!--]--> Launch Call</button> <button class="btn btn-ghost"${attr("disabled", !company.callSid || isProcessing, true)}>`);
      Phone_off($$renderer2, { class: "size-4" });
      $$renderer2.push(`<!----> Stop</button> <button class="btn btn-ghost">`);
      Trash_2($$renderer2, { class: "size-4" });
      $$renderer2.push(`<!----></button></div></div> <p class="mt-3 text-xs text-text-muted">Status: ${escape_html(statusLabel(company.status))}</p></div>`);
    }
    $$renderer2.push(`<!--]--></div></article> `);
    AIInsightsPanel($$renderer2, {
      messages: transcriptMessages,
      isLive: sessionState.status === "connected",
      intent: currentIntent,
      sentiment: currentSentiment,
      suggestions,
      onSuggestionAction: handleSuggestionAction
    });
    $$renderer2.push(`<!----> <article class="card"><div class="card-header"><h2 class="text-lg font-semibold text-text-primary">Local Audio Tester</h2> <div class="text-xs text-text-muted">Status: ${escape_html(audioState.status)}</div></div> <div class="space-y-3 text-sm text-text-secondary">`);
    if (audioState.error) {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<p class="rounded-lg border border-error/40 bg-error/10 px-3 py-2 text-error">${escape_html(audioState.error)}</p>`);
    } else {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--> `);
    if (audioState.message) {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<p class="text-xs text-text-muted">${escape_html(audioState.message)}</p>`);
    } else {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--> <div class="flex gap-2"><button type="button" class="btn btn-primary"${attr("disabled", audioState.status === "requesting-mic" || audioState.status === "recording", true)}>${escape_html(audioState.status === "requesting-mic" ? "Requesting…" : "Start microphone")}</button> <button type="button" class="btn btn-ghost"${attr("disabled", audioState.status === "idle" || audioState.status === "ready", true)}>Stop</button></div> `);
    if (audioState.lastPlaybackAt) {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<p class="text-xs text-text-muted">Last playback: ${escape_html(new Date(audioState.lastPlaybackAt).toLocaleTimeString())}</p>`);
    } else {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--></div></article> <article class="card"><div class="card-header"><div class="flex items-center gap-2 text-text-primary">`);
    Activity($$renderer2, { class: "size-4" });
    $$renderer2.push(`<!----> <h2 class="text-lg font-semibold">Session Monitor</h2></div></div> <div class="space-y-3"><p class="text-sm text-text-muted">${escape_html(callStatusDescription(callStatus))}</p> `);
    {
      $$renderer2.push("<!--[!-->");
      $$renderer2.push(`<p class="text-xs text-text-muted">No call summaries available yet. Launch a call to populate analytics.</p>`);
    }
    $$renderer2.push(`<!--]--></div></article> <article class="card"><div class="card-header"><h2 class="text-lg font-semibold text-text-primary">Realtime Session</h2> <div class="text-xs text-text-muted">Provider: ${escape_html(sessionState.provider)} • Status: ${escape_html(sessionState.status)}</div></div> <div class="space-y-3 text-sm text-text-secondary">`);
    if (sessionState.error) {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<p class="rounded-lg border border-error/40 bg-error/10 px-3 py-2 text-error">${escape_html(sessionState.error)}</p>`);
    } else {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--> <div class="flex gap-2"><button type="button" class="btn btn-secondary"${attr("disabled", sessionState.status === "connecting" || sessionState.status === "connected", true)}>${escape_html(sessionState.status === "connecting" ? "Connecting…" : "Connect session")}</button> <button type="button" class="btn btn-ghost"${attr("disabled", sessionState.status === "idle" || sessionState.status === "disconnected", true)}>Disconnect</button></div> <p class="text-xs text-text-muted">Last event: ${escape_html(sessionState.lastEventAt ? new Date(sessionState.lastEventAt).toLocaleTimeString() : "—")}</p></div></article></div></div></section>`);
    if ($$store_subs) unsubscribe_stores($$store_subs);
  });
}
export {
  _page as default
};
