import { g as sanitize_props, j as spread_props, s as slot, d as attr_class, c as attr, b as bind_props, k as attr_style, f as stringify, e as ensure_array_like } from "../../../../../chunks/index2.js";
import { o as onDestroy } from "../../../../../chunks/index-server.js";
import { e as escape_html } from "../../../../../chunks/escaping.js";
import "clsx";
import { M as Message_circle, U as User, B as Bot } from "../../../../../chunks/user.js";
import { P as ProviderSwitcher, c as createProviderSession } from "../../../../../chunks/providerSession.js";
import { I as Icon } from "../../../../../chunks/Icon.js";
import { A as Activity } from "../../../../../chunks/activity.js";
import { R as Refresh_cw } from "../../../../../chunks/refresh-cw.js";
import { W as Wifi_off } from "../../../../../chunks/wifi-off.js";
import { C as Circle_check_big } from "../../../../../chunks/circle-check-big.js";
import { w as writable, g as get } from "../../../../../chunks/index.js";
import { c as createAudioManager, P as Phone_off } from "../../../../../chunks/audioManager.js";
import { P as Phone_call } from "../../../../../chunks/phone-call.js";
import { M as Mic } from "../../../../../chunks/mic.js";
function Circle_x($$renderer, $$props) {
  const $$sanitized_props = sanitize_props($$props);
  const iconNode = [
    ["circle", { "cx": "12", "cy": "12", "r": "10" }],
    ["path", { "d": "m15 9-6 6" }],
    ["path", { "d": "m9 9 6 6" }]
  ];
  Icon($$renderer, spread_props([
    { name: "circle-x" },
    $$sanitized_props,
    {
      /**
       * @component @name CircleX
       * @description Lucide SVG icon component, renders SVG Element with children.
       *
       * @preview ![img](data:image/svg+xml;base64,PHN2ZyAgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIgogIHdpZHRoPSIyNCIKICBoZWlnaHQ9IjI0IgogIHZpZXdCb3g9IjAgMCAyNCAyNCIKICBmaWxsPSJub25lIgogIHN0cm9rZT0iIzAwMCIgc3R5bGU9ImJhY2tncm91bmQtY29sb3I6ICNmZmY7IGJvcmRlci1yYWRpdXM6IDJweCIKICBzdHJva2Utd2lkdGg9IjIiCiAgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIgogIHN0cm9rZS1saW5lam9pbj0icm91bmQiCj4KICA8Y2lyY2xlIGN4PSIxMiIgY3k9IjEyIiByPSIxMCIgLz4KICA8cGF0aCBkPSJtMTUgOS02IDYiIC8+CiAgPHBhdGggZD0ibTkgOSA2IDYiIC8+Cjwvc3ZnPgo=) - https://lucide.dev/icons/circle-x
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
function Mic_off($$renderer, $$props) {
  const $$sanitized_props = sanitize_props($$props);
  const iconNode = [
    ["line", { "x1": "2", "x2": "22", "y1": "2", "y2": "22" }],
    ["path", { "d": "M18.89 13.23A7.12 7.12 0 0 0 19 12v-2" }],
    ["path", { "d": "M5 10v2a7 7 0 0 0 12 5" }],
    ["path", { "d": "M15 9.34V5a3 3 0 0 0-5.68-1.33" }],
    ["path", { "d": "M9 9v3a3 3 0 0 0 5.12 2.12" }],
    ["line", { "x1": "12", "x2": "12", "y1": "19", "y2": "22" }]
  ];
  Icon($$renderer, spread_props([
    { name: "mic-off" },
    $$sanitized_props,
    {
      /**
       * @component @name MicOff
       * @description Lucide SVG icon component, renders SVG Element with children.
       *
       * @preview ![img](data:image/svg+xml;base64,PHN2ZyAgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIgogIHdpZHRoPSIyNCIKICBoZWlnaHQ9IjI0IgogIHZpZXdCb3g9IjAgMCAyNCAyNCIKICBmaWxsPSJub25lIgogIHN0cm9rZT0iIzAwMCIgc3R5bGU9ImJhY2tncm91bmQtY29sb3I6ICNmZmY7IGJvcmRlci1yYWRpdXM6IDJweCIKICBzdHJva2Utd2lkdGg9IjIiCiAgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIgogIHN0cm9rZS1saW5lam9pbj0icm91bmQiCj4KICA8bGluZSB4MT0iMiIgeDI9IjIyIiB5MT0iMiIgeTI9IjIyIiAvPgogIDxwYXRoIGQ9Ik0xOC44OSAxMy4yM0E3LjEyIDcuMTIgMCAwIDAgMTkgMTJ2LTIiIC8+CiAgPHBhdGggZD0iTTUgMTB2MmE3IDcgMCAwIDAgMTIgNSIgLz4KICA8cGF0aCBkPSJNMTUgOS4zNFY1YTMgMyAwIDAgMC01LjY4LTEuMzMiIC8+CiAgPHBhdGggZD0iTTkgOXYzYTMgMyAwIDAgMCA1LjEyIDIuMTIiIC8+CiAgPGxpbmUgeDE9IjEyIiB4Mj0iMTIiIHkxPSIxOSIgeTI9IjIyIiAvPgo8L3N2Zz4K) - https://lucide.dev/icons/mic-off
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
function Triangle_alert($$renderer, $$props) {
  const $$sanitized_props = sanitize_props($$props);
  const iconNode = [
    [
      "path",
      {
        "d": "m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3"
      }
    ],
    ["path", { "d": "M12 9v4" }],
    ["path", { "d": "M12 17h.01" }]
  ];
  Icon($$renderer, spread_props([
    { name: "triangle-alert" },
    $$sanitized_props,
    {
      /**
       * @component @name TriangleAlert
       * @description Lucide SVG icon component, renders SVG Element with children.
       *
       * @preview ![img](data:image/svg+xml;base64,PHN2ZyAgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIgogIHdpZHRoPSIyNCIKICBoZWlnaHQ9IjI0IgogIHZpZXdCb3g9IjAgMCAyNCAyNCIKICBmaWxsPSJub25lIgogIHN0cm9rZT0iIzAwMCIgc3R5bGU9ImJhY2tncm91bmQtY29sb3I6ICNmZmY7IGJvcmRlci1yYWRpdXM6IDJweCIKICBzdHJva2Utd2lkdGg9IjIiCiAgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIgogIHN0cm9rZS1saW5lam9pbj0icm91bmQiCj4KICA8cGF0aCBkPSJtMjEuNzMgMTgtOC0xNGEyIDIgMCAwIDAtMy40OCAwbC04IDE0QTIgMiAwIDAgMCA0IDIxaDE2YTIgMiAwIDAgMCAxLjczLTMiIC8+CiAgPHBhdGggZD0iTTEyIDl2NCIgLz4KICA8cGF0aCBkPSJNMTIgMTdoLjAxIiAvPgo8L3N2Zz4K) - https://lucide.dev/icons/triangle-alert
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
function CallControlPanel($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    let { session = null, onEndCall, onMute, onHold, onTransfer } = $$props;
    let isMuted = false;
    let isOnHold = false;
    let callDuration = 0;
    let connectionStatus = "disconnected";
    const formatDuration = (seconds) => {
      const mins = Math.floor(seconds / 60);
      const secs = seconds % 60;
      return `${mins.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")}`;
    };
    onDestroy(() => {
    });
    $$renderer2.push(`<div class="call-control-panel svelte-1blqu8h" role="region" aria-label="Call controls"><div class="status-bar svelte-1blqu8h"><div${attr_class("status-indicator svelte-1blqu8h", void 0, {
      "connected": connectionStatus === "connected",
      "connecting": connectionStatus === "connecting",
      "disconnected": connectionStatus === "disconnected"
    })} role="status" aria-live="polite">`);
    {
      $$renderer2.push("<!--[!-->");
      {
        $$renderer2.push("<!--[!-->");
        $$renderer2.push(`<span class="status-dot svelte-1blqu8h" aria-hidden="true"></span> <span class="status-text svelte-1blqu8h">No Active Call</span>`);
      }
      $$renderer2.push(`<!--]-->`);
    }
    $$renderer2.push(`<!--]--></div> <div class="call-timer svelte-1blqu8h" role="timer" aria-label="Call duration"><span class="timer-icon svelte-1blqu8h" aria-hidden="true">⏱</span> <span class="timer-text svelte-1blqu8h">${escape_html(formatDuration(callDuration))}</span></div></div> <div class="controls svelte-1blqu8h" role="group" aria-label="Call control buttons"><button${attr_class("control-btn mute svelte-1blqu8h", void 0, { "active": isMuted })}${attr("disabled", connectionStatus !== "connected", true)}${attr("aria-label", "Mute microphone")}${attr("aria-pressed", isMuted)} tabindex="0"><span class="icon svelte-1blqu8h" aria-hidden="true">${escape_html("🎤")}</span> <span class="label svelte-1blqu8h">${escape_html("Mute")}</span> <span class="sr-only svelte-1blqu8h">${escape_html("Microphone is active")}</span></button> <button${attr_class("control-btn hold svelte-1blqu8h", void 0, { "active": isOnHold })}${attr("disabled", connectionStatus !== "connected", true)}${attr("aria-label", "Place call on hold")}${attr("aria-pressed", isOnHold)} tabindex="0"><span class="icon svelte-1blqu8h" aria-hidden="true">${escape_html("⏸")}</span> <span class="label svelte-1blqu8h">${escape_html("Hold")}</span> <span class="sr-only svelte-1blqu8h">${escape_html("Call is active")}</span></button> <button class="control-btn transfer svelte-1blqu8h"${attr("disabled", connectionStatus !== "connected", true)} aria-label="Transfer call to another agent" tabindex="0"><span class="icon svelte-1blqu8h" aria-hidden="true">↗</span> <span class="label svelte-1blqu8h">Transfer</span></button> <button class="control-btn end-call svelte-1blqu8h"${attr("disabled", connectionStatus === "disconnected", true)} aria-label="End call" tabindex="0"><span class="icon svelte-1blqu8h" aria-hidden="true">📞</span> <span class="label svelte-1blqu8h">End Call</span></button></div></div>`);
    bind_props($$props, { session });
  });
}
function SentimentIndicator($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    let { sentiment = null, trend = null } = $$props;
    const emotionIcons = {
      happy: "😊",
      satisfied: "🙂",
      neutral: "😐",
      frustrated: "😤",
      angry: "😠",
      confused: "😕",
      anxious: "😰"
    };
    const sentimentColors = {
      very_positive: "#10b981",
      positive: "#84cc16",
      neutral: "#a3a3a3",
      negative: "#f59e0b",
      very_negative: "#ef4444"
    };
    const getSentimentColor = (sentiment2) => {
      return sentimentColors[sentiment2] || "#a3a3a3";
    };
    const getPolarityPosition = (polarity) => {
      return (polarity + 1) / 2 * 100;
    };
    const formatSentiment = (sentiment2) => {
      return sentiment2.split("_").map((word) => word.charAt(0).toUpperCase() + word.slice(1)).join(" ");
    };
    $$renderer2.push(`<div class="sentiment-indicator svelte-6xlqpg" role="region" aria-label="Customer sentiment analysis">`);
    if (sentiment) {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<div class="header svelte-6xlqpg"><h3 class="title svelte-6xlqpg">Customer Sentiment</h3> `);
      if (trend && trend.alert_level !== "none") {
        $$renderer2.push("<!--[-->");
        $$renderer2.push(`<span${attr_class("alert-badge svelte-6xlqpg", void 0, {
          "high": trend.alert_level === "high",
          "medium": trend.alert_level === "medium",
          "low": trend.alert_level === "low"
        })} role="alert" aria-live="assertive"><span aria-hidden="true" class="svelte-6xlqpg">⚠</span> ${escape_html(trend.alert_level.toUpperCase())} <span class="sr-only svelte-6xlqpg">Alert: ${escape_html(trend.alert_level)} sentiment level detected</span></span>`);
      } else {
        $$renderer2.push("<!--[!-->");
      }
      $$renderer2.push(`<!--]--></div> <div class="current-sentiment svelte-6xlqpg" role="status" aria-live="polite" aria-atomic="true"${attr("aria-label", `Current sentiment: ${stringify(formatSentiment(sentiment.sentiment))}`)}><div class="sentiment-label svelte-6xlqpg"><span class="sentiment-text svelte-6xlqpg"${attr_style(`color: ${stringify(getSentimentColor(sentiment.sentiment))}`)}>${escape_html(formatSentiment(sentiment.sentiment))}</span> <span class="confidence svelte-6xlqpg">(${escape_html(Math.round(sentiment.confidence * 100))}% confident)</span> <span class="sr-only svelte-6xlqpg">Customer sentiment is ${escape_html(formatSentiment(sentiment.sentiment))} with ${escape_html(Math.round(sentiment.confidence * 100))} percent confidence</span></div> <div class="emotions svelte-6xlqpg" role="list" aria-label="Detected emotions"><!--[-->`);
      const each_array = ensure_array_like(sentiment.emotions);
      for (let $$index = 0, $$length = each_array.length; $$index < $$length; $$index++) {
        let emotion = each_array[$$index];
        $$renderer2.push(`<span class="emotion-badge svelte-6xlqpg" role="listitem"${attr("aria-label", `${stringify(emotion)} emotion`)}${attr("title", emotion)}><span aria-hidden="true" class="svelte-6xlqpg">${escape_html(emotionIcons[emotion] || "😐")}</span></span>`);
      }
      $$renderer2.push(`<!--]--></div></div> <div class="polarity-bar svelte-6xlqpg" role="group" aria-label="Sentiment polarity indicator"><div class="polarity-labels svelte-6xlqpg" aria-hidden="true"><span class="label-negative svelte-6xlqpg">Negative</span> <span class="label-neutral svelte-6xlqpg">Neutral</span> <span class="label-positive svelte-6xlqpg">Positive</span></div> <div class="polarity-track svelte-6xlqpg" role="img"${attr("aria-label", `Polarity score: ${stringify(sentiment.polarity_score.toFixed(2))} out of range -1 to 1`)}><div class="polarity-fill svelte-6xlqpg"${attr_style(`width: ${stringify(getPolarityPosition(sentiment.polarity_score))}%; background: ${stringify(getSentimentColor(sentiment.sentiment))}`)} aria-hidden="true"></div> <div class="polarity-indicator svelte-6xlqpg"${attr_style(`left: ${stringify(getPolarityPosition(sentiment.polarity_score))}%; background: ${stringify(getSentimentColor(sentiment.sentiment))}`)} aria-hidden="true"></div></div> <div class="polarity-value svelte-6xlqpg" role="status">Score: ${escape_html(sentiment.polarity_score.toFixed(2))} <span class="sr-only svelte-6xlqpg">Polarity score is ${escape_html(sentiment.polarity_score.toFixed(2))}, ranging from -1 (very negative) to 1 (very positive)</span></div></div> <div class="intensity-meter svelte-6xlqpg" role="group" aria-label="Sentiment intensity meter"><span class="intensity-label svelte-6xlqpg" id="intensity-label">Intensity:</span> <div class="intensity-bar svelte-6xlqpg" role="progressbar" aria-labelledby="intensity-label"${attr("aria-valuenow", Math.round(sentiment.intensity * 100))} aria-valuemin="0" aria-valuemax="100"${attr("aria-valuetext", `${stringify(Math.round(sentiment.intensity * 100))} percent`)}><div class="intensity-fill svelte-6xlqpg"${attr_style(`width: ${stringify(sentiment.intensity * 100)}%; background: ${stringify(getSentimentColor(sentiment.sentiment))}`)} aria-hidden="true"></div></div> <span class="intensity-value svelte-6xlqpg">${escape_html(Math.round(sentiment.intensity * 100))}%</span></div> `);
      if (trend) {
        $$renderer2.push("<!--[-->");
        $$renderer2.push(`<div class="trend-info svelte-6xlqpg" role="group" aria-label="Sentiment trend information"><div class="trend-item svelte-6xlqpg"><span class="trend-label svelte-6xlqpg">Trend:</span> <span${attr_class("trend-value svelte-6xlqpg", void 0, {
          "improving": trend.is_improving,
          "declining": !trend.is_improving
        })} role="status" aria-live="polite"><span aria-hidden="true" class="svelte-6xlqpg">${escape_html(trend.is_improving ? "📈" : "📉")}</span> ${escape_html(trend.is_improving ? "Improving" : "Declining")} <span class="sr-only svelte-6xlqpg">Sentiment trend is ${escape_html(trend.is_improving ? "improving" : "declining")}</span></span></div> <div class="trend-item svelte-6xlqpg"><span class="trend-label svelte-6xlqpg">Avg Polarity:</span> <span class="trend-value svelte-6xlqpg" role="status">${escape_html(trend.average_polarity.toFixed(2))}</span></div> <div class="trend-item svelte-6xlqpg"><span class="trend-label svelte-6xlqpg">Changes:</span> <span class="trend-value svelte-6xlqpg" role="status">${escape_html(trend.sentiment_changes)}</span></div></div>`);
      } else {
        $$renderer2.push("<!--[!-->");
      }
      $$renderer2.push(`<!--]--> <div class="footer svelte-6xlqpg" role="contentinfo"><span class="speaker-badge svelte-6xlqpg"><span aria-hidden="true" class="svelte-6xlqpg">${escape_html(sentiment.speaker === "customer" ? "👤" : "👨‍💼")}</span> ${escape_html(sentiment.speaker === "customer" ? "Customer" : "Agent")}</span> <time class="timestamp svelte-6xlqpg"${attr("datetime", new Date(sentiment.timestamp).toISOString())}>${escape_html(new Date(sentiment.timestamp).toLocaleTimeString())}</time></div>`);
    } else {
      $$renderer2.push("<!--[!-->");
      $$renderer2.push(`<div class="no-data svelte-6xlqpg" role="status" aria-live="polite"><span class="icon svelte-6xlqpg" aria-hidden="true">😐</span> <p class="svelte-6xlqpg">No sentiment data yet</p> <p class="hint svelte-6xlqpg">Sentiment will appear once the conversation starts</p></div>`);
    }
    $$renderer2.push(`<!--]--></div>`);
    bind_props($$props, { sentiment, trend });
  });
}
function AIAssistancePanel($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    let { suggestions = [], onUseSuggestion, onDismissSuggestion } = $$props;
    const typeIcons = {
      suggested_response: "💬",
      knowledge_article: "📚",
      compliance_warning: "⚠️",
      performance_tip: "💡",
      escalation_guide: "🚀"
    };
    const priorityColors = {
      urgent: { bg: "#fef2f2", border: "#ef4444", text: "#991b1b" },
      high: { bg: "#fff7ed", border: "#f97316", text: "#9a3412" },
      medium: { bg: "#fef3c7", border: "#f59e0b", text: "#92400e" },
      low: { bg: "#f0fdf4", border: "#10b981", text: "#065f46" }
    };
    const formatType = (type) => {
      return type.split("_").map((word) => word.charAt(0).toUpperCase() + word.slice(1)).join(" ");
    };
    const sortedSuggestions = () => {
      const priorityOrder = ["urgent", "high", "medium", "low"];
      return [...suggestions].sort((a, b) => {
        const priorityDiff = priorityOrder.indexOf(a.priority) - priorityOrder.indexOf(b.priority);
        if (priorityDiff !== 0) return priorityDiff;
        return b.confidence - a.confidence;
      });
    };
    $$renderer2.push(`<div class="ai-assistance-panel svelte-1w4jx6a"><div class="header svelte-1w4jx6a"><h3 class="title svelte-1w4jx6a"><span class="icon svelte-1w4jx6a">🤖</span> AI Assistance</h3> `);
    if (suggestions.length > 0) {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<span class="badge svelte-1w4jx6a">${escape_html(suggestions.length)} ${escape_html(suggestions.length === 1 ? "suggestion" : "suggestions")}</span>`);
    } else {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--></div> <div class="suggestions-list svelte-1w4jx6a">`);
    if (sortedSuggestions().length > 0) {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<!--[-->`);
      const each_array = ensure_array_like(sortedSuggestions());
      for (let $$index = 0, $$length = each_array.length; $$index < $$length; $$index++) {
        let suggestion = each_array[$$index];
        const colors = priorityColors[suggestion.priority];
        $$renderer2.push(`<div class="suggestion-card svelte-1w4jx6a"${attr_style(`background: ${stringify(colors.bg)}; border-color: ${stringify(colors.border)}`)}><div class="card-header svelte-1w4jx6a"><div class="type-badge svelte-1w4jx6a"${attr_style(`color: ${stringify(colors.text)}`)}><span class="type-icon svelte-1w4jx6a">${escape_html(typeIcons[suggestion.type] || "📌")}</span> <span class="type-text">${escape_html(formatType(suggestion.type))}</span></div> <div class="priority-badge svelte-1w4jx6a"${attr_style(`color: ${stringify(colors.text)}`)}>${escape_html(suggestion.priority.toUpperCase())}</div></div> <h4 class="suggestion-title svelte-1w4jx6a"${attr_style(`color: ${stringify(colors.text)}`)}>${escape_html(suggestion.title)}</h4> <p class="suggestion-content svelte-1w4jx6a">${escape_html(suggestion.content)}</p> <div class="card-footer svelte-1w4jx6a"><div class="confidence svelte-1w4jx6a"><span class="confidence-label svelte-1w4jx6a">Confidence:</span> <div class="confidence-bar svelte-1w4jx6a"><div class="confidence-fill svelte-1w4jx6a"${attr_style(`width: ${stringify(suggestion.confidence * 100)}%; background: ${stringify(colors.border)}`)}></div></div> <span class="confidence-value svelte-1w4jx6a">${escape_html(Math.round(suggestion.confidence * 100))}%</span></div></div> <div class="card-actions svelte-1w4jx6a">`);
        if (suggestion.type === "suggested_response") {
          $$renderer2.push("<!--[-->");
          $$renderer2.push(`<button class="action-btn primary svelte-1w4jx6a"${attr_style(`background: ${stringify(colors.border)}`)}><span class="btn-icon svelte-1w4jx6a">✓</span> Use Response</button>`);
        } else {
          $$renderer2.push("<!--[!-->");
          if (suggestion.type === "knowledge_article") {
            $$renderer2.push("<!--[-->");
            $$renderer2.push(`<button class="action-btn secondary svelte-1w4jx6a"${attr_style(`color: ${stringify(colors.border)}; border-color: ${stringify(colors.border)}`)}><span class="btn-icon svelte-1w4jx6a">👁</span> View Article</button>`);
          } else {
            $$renderer2.push("<!--[!-->");
            $$renderer2.push(`<button class="action-btn secondary svelte-1w4jx6a"${attr_style(`color: ${stringify(colors.border)}; border-color: ${stringify(colors.border)}`)}><span class="btn-icon svelte-1w4jx6a">ℹ</span> More Info</button>`);
          }
          $$renderer2.push(`<!--]-->`);
        }
        $$renderer2.push(`<!--]--> <button class="action-btn dismiss svelte-1w4jx6a"><span class="btn-icon svelte-1w4jx6a">✕</span> Dismiss</button></div></div>`);
      }
      $$renderer2.push(`<!--]-->`);
    } else {
      $$renderer2.push("<!--[!-->");
      $$renderer2.push(`<div class="no-suggestions svelte-1w4jx6a"><span class="no-suggestions-icon svelte-1w4jx6a">🤖</span> <p class="no-suggestions-text svelte-1w4jx6a">No suggestions yet</p> <p class="no-suggestions-hint svelte-1w4jx6a">AI assistance will appear as the conversation progresses</p></div>`);
    }
    $$renderer2.push(`<!--]--></div></div>`);
    bind_props($$props, { suggestions });
  });
}
function TranscriptionPanel($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    let { messages = [], segments = [], isLive = false } = $$props;
    const displayMessages = segments.length > 0 ? segments : messages;
    function formatTime(date) {
      return date.toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit", second: "2-digit" });
    }
    function getRoleLabel(role) {
      return role === "user" ? "Customer" : "AI Agent";
    }
    function getRoleIcon(role) {
      return role === "user" ? User : Bot;
    }
    function getRoleColor(role) {
      return role === "user" ? "text-cyan-data" : "text-terminal-green";
    }
    function getBgColor(role) {
      return role === "user" ? "bg-cyan-data/5" : "bg-terminal-green/5";
    }
    $$renderer2.push(`<article class="brutal-card h-full flex flex-col" role="region" aria-label="Live transcription"><div class="flex items-center justify-between mb-6 border-b-2 border-foreground pb-4"><div class="flex items-center gap-3">`);
    Message_circle($$renderer2, { class: "size-5 text-foreground", "aria-hidden": "true" });
    $$renderer2.push(`<!----> <h2 class="text-xl font-display uppercase tracking-tight">Transcription</h2> `);
    if (isLive) {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<span class="inline-flex items-center gap-1.5 border-2 border-terminal-green bg-void px-2 py-0.5 text-[10px] font-bold uppercase text-terminal-green" role="status" aria-live="polite"><span class="size-1.5 animate-pulse bg-terminal-green" aria-hidden="true"></span> Live_Feed <span class="sr-only">Transcription is live</span></span>`);
    } else {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--></div> <span class="text-[10px] font-mono font-bold uppercase tracking-widest text-muted-foreground" role="status" aria-live="polite" aria-atomic="true">[${escape_html(displayMessages.length)}] Segments</span></div> <div class="flex-1 space-y-4 overflow-y-auto pr-2 custom-scrollbar svelte-1k71it6" role="log" aria-live="polite" aria-relevant="additions" aria-label="Conversation transcript">`);
    if (displayMessages.length === 0) {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<div class="flex flex-col items-center justify-center py-24 text-center border-2 border-dashed border-muted/20" role="status"><div class="relative mb-6">`);
      Message_circle($$renderer2, { class: "size-16 text-muted/10", "aria-hidden": "true" });
      $$renderer2.push(`<!----> <div class="absolute inset-0 flex items-center justify-center"><span class="text-terminal-green animate-pulse font-mono text-xs">AWAITING_SIGNAL...</span></div></div> <p class="text-[11px] font-bold uppercase tracking-[0.2em] text-muted-foreground max-w-xs">No active stream detected. Start a call to initiate real-time logging.</p></div>`);
    } else {
      $$renderer2.push("<!--[!-->");
      $$renderer2.push(`<!--[-->`);
      const each_array = ensure_array_like(displayMessages);
      for (let $$index = 0, $$length = each_array.length; $$index < $$length; $$index++) {
        let message = each_array[$$index];
        $$renderer2.push(`<div${attr_class(`border-2 border-foreground p-4 relative group hover:shadow-[4px_4px_0px_0px_rgba(51,255,0,0.5)] transition-all ${stringify(getBgColor(message.role))}`, "svelte-1k71it6")} role="article"${attr("aria-label", `${stringify(getRoleLabel(message.role))} message`)}><div class="flex items-start gap-4"><div${attr_class(`border-2 border-foreground p-2 bg-void ${getRoleColor(message.role)}`, "svelte-1k71it6")} aria-hidden="true"><!---->`);
        getRoleIcon(message.role)?.($$renderer2, { class: "size-4" });
        $$renderer2.push(`<!----></div> <div class="flex-1 space-y-2"><div class="flex items-center justify-between border-b border-foreground/10 pb-1"><span${attr_class(`text-[10px] font-black uppercase tracking-widest ${getRoleColor(message.role)}`, "svelte-1k71it6")}>// ${escape_html(getRoleLabel(message.role))}</span> <time class="text-[9px] font-mono font-bold text-muted-foreground"${attr("datetime", message.timestamp.toISOString())}>${escape_html(formatTime(message.timestamp))}</time></div> <p class="text-sm font-mono leading-relaxed text-foreground">${escape_html(message.content)}</p></div></div> `);
        if (message.role === "assistant") {
          $$renderer2.push("<!--[-->");
          $$renderer2.push(`<div class="absolute top-0 right-0 p-1"><div class="w-1 h-1 bg-terminal-green animate-pulse"></div></div>`);
        } else {
          $$renderer2.push("<!--[!-->");
        }
        $$renderer2.push(`<!--]--></div>`);
      }
      $$renderer2.push(`<!--]-->`);
    }
    $$renderer2.push(`<!--]--></div></article>`);
  });
}
const STATE_VERSION = "1.0.0";
const MAX_CALL_HISTORY = 10;
const STATE_THROTTLE_MS = 1e3;
function createSessionStateManager() {
  const initialState = {
    call: null,
    provider: "gemini",
    audio: {
      isMuted: false,
      isRecording: false,
      inputLevel: 0,
      outputLevel: 0
    },
    ui: {
      activePanel: "transcription",
      sidebarOpen: true,
      theme: "light"
    },
    errors: [],
    lastActivity: Date.now(),
    version: STATE_VERSION
  };
  const state = writable(initialState);
  let saveTimeout = null;
  let callHistory = [];
  function throttleSave() {
    if (saveTimeout) {
      clearTimeout(saveTimeout);
    }
    saveTimeout = setTimeout(() => {
      saveTimeout = null;
    }, STATE_THROTTLE_MS);
  }
  function saveState() {
    return;
  }
  function restoreState() {
    return false;
  }
  function clearState() {
    return;
  }
  function validateState(state2) {
    if (!state2 || typeof state2 !== "object") return false;
    if (!state2.version || !state2.provider || !state2.audio || !state2.ui) return false;
    if (!["gemini", "openai", "deepgram_nova3"].includes(state2.provider)) return false;
    return true;
  }
  function updateCallState(callUpdate) {
    state.update((current) => {
      const newCall = current.call ? { ...current.call, ...callUpdate } : callUpdate;
      if (current.call && callUpdate.status === "ended") {
        const endedCall = { ...current.call, ...callUpdate };
        callHistory = [endedCall, ...callHistory.slice(0, MAX_CALL_HISTORY - 1)];
      }
      return {
        ...current,
        call: newCall
      };
    });
    throttleSave();
  }
  function updateProvider(provider) {
    state.update((current) => ({
      ...current,
      provider
    }));
    throttleSave();
  }
  function updateAudioState(audioUpdate) {
    state.update((current) => ({
      ...current,
      audio: { ...current.audio, ...audioUpdate }
    }));
    throttleSave();
  }
  function updateUIState(uiUpdate) {
    state.update((current) => ({
      ...current,
      ui: { ...current.ui, ...uiUpdate }
    }));
    throttleSave();
  }
  function addError(error) {
    const errorWithTimestamp = {
      ...error,
      timestamp: Date.now()
    };
    state.update((current) => ({
      ...current,
      errors: [...current.errors.slice(-9), errorWithTimestamp]
      // Keep last 10 errors
    }));
    throttleSave();
  }
  function clearErrors() {
    state.update((current) => ({
      ...current,
      errors: []
    }));
    throttleSave();
  }
  async function recoverFromError(errorCode) {
    const currentState = get(state);
    const error = currentState.errors.find((e) => e.code === errorCode);
    if (!error || !error.recoverable || !error.recoveryAction) {
      return false;
    }
    try {
      console.log(`🔄 Attempting to recover from error: ${errorCode}`);
      await error.recoveryAction();
      state.update((current) => ({
        ...current,
        errors: current.errors.filter((e) => e.code !== errorCode)
      }));
      throttleSave();
      return true;
    } catch (recoveryError) {
      console.error(`❌ Failed to recover from error ${errorCode}:`, recoveryError);
      return false;
    }
  }
  function getCallHistory() {
    return [...callHistory];
  }
  function exportState() {
    const currentState = get(state);
    const exportData = {
      ...currentState,
      callHistory,
      exportedAt: Date.now()
    };
    return JSON.stringify(exportData, null, 2);
  }
  function importState(stateJson) {
    try {
      const importedData = JSON.parse(stateJson);
      if (!validateState(importedData)) {
        throw new Error("Invalid state structure");
      }
      if (importedData.callHistory) {
        callHistory = importedData.callHistory.slice(0, MAX_CALL_HISTORY);
      }
      const importedState = {
        ...importedData,
        call: null,
        audio: {
          ...importedData.audio,
          isRecording: false,
          inputLevel: 0,
          outputLevel: 0
        }
      };
      state.set(importedState);
      throttleSave();
      console.log("📥 State imported successfully");
      return true;
    } catch (error) {
      console.error("❌ Failed to import state:", error);
      return false;
    }
  }
  state.subscribe(() => {
    throttleSave();
  });
  setInterval(() => {
    const currentState = get(state);
    const recentErrors = currentState.errors.filter(
      (error) => Date.now() - error.timestamp < 3e5
      // 5 minutes
    );
    if (recentErrors.length !== currentState.errors.length) {
      state.update((current) => ({
        ...current,
        errors: recentErrors
      }));
    }
  }, 6e4);
  return {
    subscribe: state.subscribe,
    saveState,
    restoreState,
    clearState,
    updateCallState,
    updateProvider,
    updateAudioState,
    updateUIState,
    addError,
    clearErrors,
    recoverFromError,
    getCallHistory,
    exportState,
    importState
  };
}
function EnhancedConnectionStatus($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    let {
      stats = void 0,
      isLive = false,
      currentProvider = "unknown",
      onRetry,
      onSwitchProvider,
      onSettings,
      showDetails = false
    } = $$props;
    let isExpanded = false;
    const connectionQuality = () => {
      if (!stats) return "unknown";
      const { latency, packetLoss, bitrate } = stats;
      if (latency < 100 && packetLoss < 1 && bitrate > 50) return "excellent";
      if (latency < 200 && packetLoss < 3 && bitrate > 30) return "good";
      if (latency < 500 && packetLoss < 10 && bitrate > 10) return "fair";
      return "poor";
    };
    const connectionStatus = () => {
      if (!stats) return "unknown";
      return stats.connectionState;
    };
    const statusColor = () => {
      switch (connectionQuality()) {
        case "excellent":
          return "text-green-500";
        case "good":
          return "text-blue-500";
        case "fair":
          return "text-yellow-500";
        case "poor":
          return "text-red-500";
        default:
          return "text-gray-500";
      }
    };
    const statusIcon = () => {
      switch (connectionStatus()) {
        case "connected":
          return Circle_check_big;
        case "connecting":
          return Refresh_cw;
        case "disconnected":
          return Wifi_off;
        case "failed":
          return Circle_x;
        case "reconnecting":
          return Refresh_cw;
        default:
          return Activity;
      }
    };
    const statusText = () => {
      switch (connectionStatus()) {
        case "connected":
          return "Connected";
        case "connecting":
          return "Connecting...";
        case "disconnected":
          return "Disconnected";
        case "failed":
          return "Connection Failed";
        case "reconnecting":
          return "Reconnecting...";
        default:
          return "Unknown";
      }
    };
    const qualityText = () => {
      switch (connectionQuality()) {
        case "excellent":
          return "Excellent";
        case "good":
          return "Good";
        case "fair":
          return "Fair";
        case "poor":
          return "Poor";
        default:
          return "Unknown";
      }
    };
    const hasWarnings = () => {
      if (!stats) return false;
      return stats.latency > 300 || stats.packetLoss > 5 || stats.audioLevel < 0.1;
    };
    onDestroy(() => {
    });
    $$renderer2.push(`<div class="connection-status svelte-12jkq20"><div${attr_class("compact-view svelte-12jkq20", void 0, { "expanded": isExpanded })}><div class="status-indicator svelte-12jkq20"><!---->`);
    statusIcon()?.($$renderer2, {
      class: `icon ${stringify(statusColor())} ${stringify(connectionStatus() === "connecting" || connectionStatus() === "reconnecting" ? "spinning" : "")}`
    });
    $$renderer2.push(`<!----> <span class="status-text svelte-12jkq20">${escape_html(statusText())}</span></div> <div class="quality-indicator svelte-12jkq20"><div${attr_class("quality-bar svelte-12jkq20", void 0, {
      "excellent": connectionQuality() === "excellent",
      "good": connectionQuality() === "good",
      "fair": connectionQuality() === "fair",
      "poor": connectionQuality() === "poor"
    })}><div class="quality-fill svelte-12jkq20"></div></div> <span class="quality-text svelte-12jkq20">${escape_html(qualityText())}</span></div> `);
    if (hasWarnings()) {
      $$renderer2.push("<!--[-->");
      Triangle_alert($$renderer2, { class: "warning-icon" });
    } else {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--> `);
    if (showDetails) {
      $$renderer2.push("<!--[-->");
      Activity($$renderer2, {
        class: `expand-icon ${stringify("")}`
      });
    } else {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--></div> `);
    {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--></div>`);
    bind_props($$props, { stats });
  });
}
function createWebRTCManager(config = {}) {
  ({ ...config });
  const stats = writable({
    connectionState: "idle",
    latency: 0,
    packetLoss: 0,
    audioLevel: 0,
    bitrate: 0,
    lastUpdate: Date.now()
  });
  const audioManager = createAudioManager();
  let screenStream = null;
  let currentSignalingUrl = "";
  function updateStats(updates) {
    stats.update((prev) => ({
      ...prev,
      ...updates,
      lastUpdate: Date.now()
    }));
  }
  function updateConnectionState(state) {
    updateStats({ connectionState: state });
    console.log("🔗 WebRTC connection state:", state);
  }
  async function connect(signalingUrl) {
    {
      throw new Error("WebRTC not available outside browser");
    }
  }
  async function disconnect() {
    updateConnectionState("disconnected");
  }
  async function switchProvider(newProvider) {
    const wasConnected = get(stats).connectionState === "connected";
    const oldUrl = currentSignalingUrl;
    try {
      const baseUrl = oldUrl.split("/").slice(0, -1).join("/");
      const newUrl = `${baseUrl}/${newProvider}`;
      if (wasConnected) {
        await disconnect();
      }
      await connect(newUrl);
    } catch (error) {
      console.error("❌ Failed to switch provider:", error);
      if (wasConnected) {
        try {
          await connect(oldUrl);
        } catch (reconnectError) {
          console.error("❌ Failed to reconnect to previous provider:", reconnectError);
        }
      }
      throw error;
    }
  }
  function muteAudio(muted) {
  }
  function sendAudioChunk(chunk) {
    console.log("🎵 Audio chunk received (WebRTC handles streaming automatically)");
  }
  async function startScreenShare() {
    {
      throw new Error("Screen sharing not available outside browser");
    }
  }
  function stopScreenShare() {
    console.log("🖥️ Screen sharing stopped");
  }
  function getScreenShareStream() {
    return screenStream;
  }
  function isScreenSharing() {
    return screenStream !== null;
  }
  async function cleanup() {
    stopScreenShare();
    await disconnect();
    await audioManager.cleanup();
  }
  return {
    subscribe: stats.subscribe,
    connect,
    disconnect,
    switchProvider,
    getConnectionState() {
      return get(stats).connectionState;
    },
    async getStats() {
      return null;
    },
    muteAudio,
    sendAudioChunk,
    startScreenShare,
    stopScreenShare,
    getScreenShareStream,
    isScreenSharing,
    cleanup
  };
}
function ScreenShare($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    createWebRTCManager();
    onDestroy(() => {
    });
    $$renderer2.push(`<div class="screen-share-container svelte-1e8mw4j" role="region" aria-label="Screen sharing controls"><div class="header svelte-1e8mw4j"><h3 class="title svelte-1e8mw4j">Screen Share</h3> `);
    {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--></div> `);
    {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--> `);
    {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<div class="start-view svelte-1e8mw4j"><p class="description svelte-1e8mw4j">Share your screen to collaborate with others in real-time.</p> <button class="share-button svelte-1e8mw4j" aria-label="Start screen sharing"><span class="button-icon svelte-1e8mw4j" aria-hidden="true">🖥️</span> Start Screen Share</button> <p class="note svelte-1e8mw4j"><strong class="svelte-1e8mw4j">Note:</strong> Requires HTTPS and a modern browser (Chrome, Firefox, Edge, Safari).</p></div>`);
    }
    $$renderer2.push(`<!--]--></div>`);
  });
}
function AgentWorkspace($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    let {
      session = null,
      onEndCall,
      onMute,
      onHold,
      onTransfer,
      onRetryConnection: onRetryConnectionCb
    } = $$props;
    if (!onRetryConnectionCb) {
      onRetryConnectionCb = async () => {
      };
    }
    const sessionStateManager = createSessionStateManager();
    let transcriptionSegments = [];
    let currentSentiment = null;
    let sentimentTrend = null;
    let assistanceSuggestions = [];
    let callStatus = "idle";
    const transcriptMessages = () => {
      return transcriptionSegments.map((segment) => ({
        role: segment.speaker === "customer" ? "user" : "assistant",
        content: segment.text,
        timestamp: new Date(segment.timestamp)
      }));
    };
    function shutdownAIServices() {
      console.log("🛑 Shutting down AI services");
      transcriptionSegments = [];
      currentSentiment = null;
      sentimentTrend = null;
      assistanceSuggestions = [];
      sessionStateManager.updateCallState({ status: "ended", metadata: { aiServices: "stopped" } });
      callStatus = "ended";
    }
    function handleUseSuggestion(suggestion) {
      console.log("✓ Using suggestion:", suggestion.title);
      assistanceSuggestions = assistanceSuggestions.filter((s) => s.id !== suggestion.id);
    }
    function handleDismissSuggestion(suggestionId) {
      console.log("✕ Dismissing suggestion:", suggestionId);
      assistanceSuggestions = assistanceSuggestions.filter((s) => s.id !== suggestionId);
    }
    async function onRetryConnection() {
      try {
        sessionStateManager.clearErrors();
        sessionStateManager.updateCallState({ status: "connecting" });
        sessionStateManager.saveState();
        callStatus = "connecting";
        await onRetryConnectionCb?.();
      } catch (error) {
        sessionStateManager.addError({
          code: "retry_failed",
          message: error instanceof Error ? error.message : "Failed to retry connection",
          recoverable: true
        });
        callStatus = "error";
      }
    }
    onDestroy(() => {
      shutdownAIServices();
    });
    let $$settled = true;
    let $$inner_renderer;
    function $$render_inner($$renderer3) {
      $$renderer3.push(`<div class="agent-workspace svelte-e2j4"><div class="top-bar svelte-e2j4"><div class="call-controls-container svelte-e2j4">`);
      CallControlPanel($$renderer3, {
        onEndCall,
        onMute,
        onHold,
        onTransfer,
        get session() {
          return session;
        },
        set session($$value) {
          session = $$value;
          $$settled = false;
        }
      });
      $$renderer3.push(`<!----></div> <div class="provider-selector-container svelte-e2j4">`);
      ProviderSwitcher($$renderer3, {});
      $$renderer3.push(`<!----></div> <div class="connection-status-container svelte-e2j4">`);
      EnhancedConnectionStatus($$renderer3, {
        isLive: callStatus === "active",
        currentProvider: session?.provider ?? "unknown",
        onRetry: onRetryConnection
      });
      $$renderer3.push(`<!----></div></div> <div class="main-content svelte-e2j4"><div class="left-panel svelte-e2j4"><div class="customer-info svelte-e2j4"><h3 class="section-title svelte-e2j4">Customer Information</h3> `);
      if (session) {
        $$renderer3.push("<!--[-->");
        $$renderer3.push(`<div class="info-grid svelte-e2j4"><div class="info-item svelte-e2j4"><span class="info-label svelte-e2j4">Session ID:</span> <span class="info-value svelte-e2j4">${escape_html(session.sessionId)}</span></div> <div class="info-item svelte-e2j4"><span class="info-label svelte-e2j4">Status:</span> <span${attr_class("info-value status svelte-e2j4", void 0, { "active": callStatus === "active" })}>${escape_html(callStatus)}</span></div> <div class="info-item svelte-e2j4"><span class="info-label svelte-e2j4">Provider:</span> <span class="info-value svelte-e2j4">${escape_html(session.provider)}</span></div></div>`);
      } else {
        $$renderer3.push("<!--[!-->");
        $$renderer3.push(`<p class="no-session svelte-e2j4">No active session</p>`);
      }
      $$renderer3.push(`<!--]--></div> <div class="transcription-container svelte-e2j4"><h3 class="section-title svelte-e2j4">Live Transcription</h3> `);
      TranscriptionPanel($$renderer3, { segments: transcriptMessages() });
      $$renderer3.push(`<!----></div></div> <div class="right-panel svelte-e2j4"><div class="sentiment-container svelte-e2j4">`);
      SentimentIndicator($$renderer3, { sentiment: currentSentiment, trend: sentimentTrend });
      $$renderer3.push(`<!----></div> <div class="screen-share-wrapper svelte-e2j4">`);
      ScreenShare($$renderer3);
      $$renderer3.push(`<!----></div> <div class="assistance-container svelte-e2j4">`);
      AIAssistancePanel($$renderer3, {
        suggestions: assistanceSuggestions,
        onUseSuggestion: handleUseSuggestion,
        onDismissSuggestion: handleDismissSuggestion
      });
      $$renderer3.push(`<!----></div></div></div></div>`);
    }
    do {
      $$settled = true;
      $$inner_renderer = $$renderer2.copy();
      $$render_inner($$inner_renderer);
    } while (!$$settled);
    $$renderer2.subsume($$inner_renderer);
    bind_props($$props, { session });
  });
}
function _page($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    const providerSession = createProviderSession({ provider: "gemini" });
    let session = providerSession.getState();
    const unsubscribeSession = providerSession.subscribe((value) => {
      session = value;
    });
    const audioManager = createAudioManager();
    let audioState = audioManager.getState();
    const unsubscribeAudio = audioManager.subscribe((value) => {
      audioState = value;
    });
    let isCallActive = false;
    let isMuted = false;
    audioManager.sendCapturedFrame((buffer) => {
      if (session.status === "connected") {
        try {
          const base64 = btoa(String.fromCharCode(...new Uint8Array(buffer.buffer)));
          providerSession.send(JSON.stringify({ type: "audio-data", audioData: base64 }));
        } catch (error) {
          console.error("Failed to send captured audio frame", error);
        }
      }
    });
    function endCall() {
      providerSession.disconnect();
      audioManager.stop();
      isCallActive = false;
    }
    function handleMute(muted) {
      isMuted = muted;
      console.log(muted ? "Muted" : "Unmuted");
    }
    function handleHold(held) {
      console.log(held ? "On hold" : "Resumed");
    }
    function handleTransfer() {
      console.log("Transfer requested");
    }
    async function retryConnection() {
      providerSession.connect();
    }
    onDestroy(() => {
      providerSession.disconnect();
      void audioManager.cleanup();
      unsubscribeSession();
      unsubscribeAudio();
    });
    let $$settled = true;
    let $$inner_renderer;
    function $$render_inner($$renderer3) {
      $$renderer3.push(`<section class="agent-operations-page svelte-47l5b6"><header class="page-header svelte-47l5b6"><div class="svelte-47l5b6"><h1 class="page-title svelte-47l5b6">AI Agent Workspace</h1> <p class="page-description svelte-47l5b6">Production-ready agent interface with real-time AI assistance, sentiment analysis, and live transcription.</p></div> <div class="header-actions svelte-47l5b6">`);
      if (!isCallActive) {
        $$renderer3.push("<!--[-->");
        $$renderer3.push(`<button class="btn btn-primary btn-lg svelte-47l5b6">`);
        Phone_call($$renderer3, { class: "size-5" });
        $$renderer3.push(`<!----> Start Demo Call</button>`);
      } else {
        $$renderer3.push("<!--[!-->");
        $$renderer3.push(`<button class="btn btn-danger btn-lg svelte-47l5b6">`);
        Phone_off($$renderer3, { class: "size-5" });
        $$renderer3.push(`<!----> End Call</button>`);
      }
      $$renderer3.push(`<!--]--></div></header> `);
      {
        $$renderer3.push("<!--[!-->");
      }
      $$renderer3.push(`<!--]--> <div class="status-bar svelte-47l5b6"><div class="status-item svelte-47l5b6">`);
      Activity($$renderer3, { class: "size-4" });
      $$renderer3.push(`<!----> <span class="svelte-47l5b6">Session: <strong class="svelte-47l5b6">${escape_html(session.status)}</strong></span></div> <div class="status-item svelte-47l5b6">`);
      if (isMuted) {
        $$renderer3.push("<!--[-->");
        Mic_off($$renderer3, { class: "size-4 text-red-500" });
      } else {
        $$renderer3.push("<!--[!-->");
        Mic($$renderer3, { class: "size-4 text-green-500" });
      }
      $$renderer3.push(`<!--]--> <span class="svelte-47l5b6">Audio: <strong class="svelte-47l5b6">${escape_html(audioState.status)}</strong></span></div> <div class="status-item svelte-47l5b6"><span${attr_class("status-dot svelte-47l5b6", void 0, { "active": isCallActive })}></span> <span class="svelte-47l5b6">Call: <strong class="svelte-47l5b6">${escape_html(isCallActive ? "Active" : "Inactive")}</strong></span></div></div> <div class="workspace-container svelte-47l5b6">`);
      AgentWorkspace($$renderer3, {
        onEndCall: endCall,
        onMute: handleMute,
        onHold: handleHold,
        onTransfer: handleTransfer,
        onRetryConnection: retryConnection,
        get session() {
          return session;
        },
        set session($$value) {
          session = $$value;
          $$settled = false;
        }
      });
      $$renderer3.push(`<!----></div> `);
      if (!isCallActive) {
        $$renderer3.push("<!--[-->");
        $$renderer3.push(`<article class="instructions-card svelte-47l5b6"><h3 class="instructions-title svelte-47l5b6">Getting Started</h3> <div class="instructions-list svelte-47l5b6"><div class="instruction-item svelte-47l5b6"><span class="instruction-number svelte-47l5b6">1</span> <div class="svelte-47l5b6"><p class="instruction-text svelte-47l5b6">Click "Start Demo Call" to begin a test session</p> <p class="instruction-hint svelte-47l5b6">This will connect to the AI provider and start your microphone</p></div></div> <div class="instruction-item svelte-47l5b6"><span class="instruction-number svelte-47l5b6">2</span> <div class="svelte-47l5b6"><p class="instruction-text svelte-47l5b6">Speak naturally to interact with the AI</p> <p class="instruction-hint svelte-47l5b6">Real-time transcription and sentiment analysis will appear automatically</p></div></div> <div class="instruction-item svelte-47l5b6"><span class="instruction-number svelte-47l5b6">3</span> <div class="svelte-47l5b6"><p class="instruction-text svelte-47l5b6">Watch for AI assistance suggestions</p> <p class="instruction-hint svelte-47l5b6">Suggested responses, compliance warnings, and coaching tips will appear as you speak</p></div></div></div></article>`);
      } else {
        $$renderer3.push("<!--[!-->");
      }
      $$renderer3.push(`<!--]--></section>`);
    }
    do {
      $$settled = true;
      $$inner_renderer = $$renderer2.copy();
      $$render_inner($$inner_renderer);
    } while (!$$settled);
    $$renderer2.subsume($$inner_renderer);
  });
}
export {
  _page as default
};
