import { e as ensure_array_like, a as attr_class, b as stringify } from "../../../chunks/index2.js";
import { e as escape_html } from "../../../chunks/escaping.js";
import { b as attr } from "../../../chunks/attributes.js";
function _page($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    const isDevHost = typeof window !== "undefined" && window.location.hostname.endsWith("verduona.dev");
    const appDomain = isDevHost ? "verduona.dev" : "kraliki.com";
    const kralikiUrl = isDevHost ? "https://kraliki.verduona.dev" : "https://kraliki.com";
    const apps = [
      // THE PLATFORM
      {
        id: "kraliki",
        name: "Kraliki",
        tagline: "AI Swarm Automation Platform",
        description: "Self-organizing AI agent swarm that runs your business 24/7. 41 specialized agents across 4 CLI engines coordinate via blackboard, execute tasks autonomously, and continuously improve. This dashboard is the control center.",
        icon: "🐰",
        status: "live",
        tier: "enterprise",
        category: "ai_tools",
        url: kralikiUrl,
        features: [
          "41 Agent Swarm",
          "Autonomous Task Execution",
          "Multi-CLI Coordination",
          "Self-Organizing System",
          "Real-Time Monitoring"
        ],
        price: "Platform Foundation"
      },
      // CUSTOMER-FACING APPS (by customer journey)
      {
        id: "focus",
        name: "Focus by Kraliki",
        tagline: "AI-First Project Management",
        description: "Pomodoro timer, task management, AI-powered calendar, and execution insights. Turn strategy into action with focus sessions and Linear sync.",
        icon: "🎯",
        status: "beta",
        tier: "free",
        category: "productivity",
        url: `https://focus.${appDomain}`,
        features: [
          "Pomodoro Timer",
          "Task Management",
          "AI Calendar",
          "Linear Integration",
          "Voice Commands"
        ],
        price: "Free / Pro €9.99/mo"
      },
      {
        id: "voice",
        name: "Voice by Kraliki",
        tagline: "AI Call Center Platform",
        description: "AI-powered voice and chat support platform. Handle customer calls, chat sessions, and gain real-time insights. Scale your support without scaling headcount.",
        icon: "📞",
        status: "beta",
        tier: "pro",
        category: "communication",
        url: `https://voice.${appDomain}`,
        features: [
          "Voice Calls",
          "AI Transcription",
          "Chat Sessions",
          "Call Analytics",
          "Team Management"
        ],
        price: "From €29/mo"
      },
      {
        id: "speak",
        name: "Speak by Kraliki",
        tagline: "Employee Feedback & Surveys",
        description: "Collect voice and text feedback from employees and customers. AI-powered sentiment analysis extracts insights automatically. Know what your team really thinks.",
        icon: "🗣️",
        status: "beta",
        tier: "starter",
        category: "business",
        url: `https://speak.${appDomain}`,
        features: [
          "Voice Surveys",
          "Text Feedback",
          "Sentiment Analysis",
          "Real-time Dashboard",
          "Export Reports"
        ],
        price: "From €19/mo"
      },
      {
        id: "lab",
        name: "Lab by Kraliki",
        tagline: "Private AI Workstation",
        description: "VM fleet management platform. Deploy private AI workstations with Claude, GPT-4, Gemini orchestration for teams. Your own AI infrastructure.",
        icon: "⚡",
        status: "beta",
        tier: "enterprise",
        category: "ai_tools",
        url: `https://lab.${appDomain}`,
        features: [
          "VM Fleet Management",
          "Multi-Model Access",
          "Usage Monitoring",
          "Team Workspaces",
          "One-Click Deploy"
        ],
        price: "From €49/mo per seat"
      },
      {
        id: "learn",
        name: "Learn by Kraliki",
        tagline: "AI Academy & Client Onboarding",
        description: "Business-focused learning platform. Client onboarding courses, AI Academy L1-L4 certification, and product tutorials. Your team learns AI while they work.",
        icon: "📚",
        status: "beta",
        tier: "starter",
        category: "education",
        url: `https://learn.${appDomain}`,
        features: [
          "AI Academy L1-L4",
          "Client Onboarding",
          "Progress Tracking",
          "Certifications",
          "Team Training"
        ],
        price: "L1 Free / L2-L4 from €197"
      },
      {
        id: "sense",
        name: "Sense by Kraliki",
        tagline: "AI Readiness Assessment",
        description: "Comprehensive AI audit for your organization. Get AI readiness scores, automation opportunities, ROI calculations, and implementation roadmaps. Know where you stand.",
        icon: "🔍",
        status: "beta",
        tier: "enterprise",
        category: "business",
        url: `https://sense.${appDomain}`,
        features: [
          "AI Readiness Score",
          "Automation Opportunities",
          "ROI Calculator",
          "Implementation Roadmap",
          "Expert Consultation"
        ],
        price: "From €499 (one-time)"
      }
    ];
    let integrations = [];
    let selectedCategory = "all";
    let selectedTier = "all";
    const categories = [
      { id: "all", label: "All Apps", icon: "📱" },
      { id: "productivity", label: "Productivity", icon: "🎯" },
      { id: "communication", label: "Communication", icon: "💬" },
      { id: "ai_tools", label: "AI Tools", icon: "🤖" },
      { id: "education", label: "Education", icon: "📚" },
      { id: "business", label: "Business", icon: "💼" }
    ];
    const tiers = [
      { id: "all", label: "All Tiers" },
      { id: "free", label: "Free" },
      { id: "starter", label: "Starter" },
      { id: "pro", label: "Pro" },
      { id: "enterprise", label: "Enterprise" }
    ];
    function getAppStatus(appId) {
      const mapping = {
        "focus": "Focus by Kraliki",
        "voice": "Voice by Kraliki",
        "speak": "Speak by Kraliki",
        "learn": "Learn by Kraliki",
        "lab": "Lab by Kraliki",
        "sense": "Sense by Kraliki"
      };
      const integration = integrations.find((i) => i.name === mapping[appId]);
      return integration?.status || "unknown";
    }
    const filteredApps = apps.filter((app) => {
      return true;
    });
    function getStatusBadgeClass(status) {
      switch (status) {
        case "live":
          return "status-live";
        case "beta":
          return "status-beta";
        case "coming_soon":
          return "status-soon";
        case "internal":
          return "status-internal";
        default:
          return "";
      }
    }
    function getTierBadgeClass(tier) {
      switch (tier) {
        case "free":
          return "tier-free";
        case "starter":
          return "tier-starter";
        case "pro":
          return "tier-pro";
        case "enterprise":
          return "tier-enterprise";
        default:
          return "";
      }
    }
    $$renderer2.push(`<div class="page svelte-12ewbr5"><div class="page-header svelte-12ewbr5"><div><h2 class="glitch">Apps // Verduona Portfolio</h2> <p class="subtitle svelte-12ewbr5">AI-powered tools for modern businesses</p></div> <div class="header-stats svelte-12ewbr5"><span class="stat-pill svelte-12ewbr5">${escape_html(apps.filter((a) => a.status === "beta" || a.status === "live").length)} LIVE</span> <span class="stat-pill svelte-12ewbr5">${escape_html(apps.filter((a) => a.status === "coming_soon").length)} COMING SOON</span></div></div> <div class="filter-section svelte-12ewbr5"><div class="filter-group svelte-12ewbr5"><span class="filter-label svelte-12ewbr5">CATEGORY:</span> <!--[-->`);
    const each_array = ensure_array_like(categories);
    for (let $$index = 0, $$length = each_array.length; $$index < $$length; $$index++) {
      let cat = each_array[$$index];
      $$renderer2.push(`<button${attr_class("filter-btn svelte-12ewbr5", void 0, { "active": selectedCategory === cat.id })}><span>${escape_html(cat.icon)}</span> ${escape_html(cat.label)}</button>`);
    }
    $$renderer2.push(`<!--]--></div> <div class="filter-group svelte-12ewbr5"><span class="filter-label svelte-12ewbr5">TIER:</span> <!--[-->`);
    const each_array_1 = ensure_array_like(tiers);
    for (let $$index_1 = 0, $$length = each_array_1.length; $$index_1 < $$length; $$index_1++) {
      let tier = each_array_1[$$index_1];
      $$renderer2.push(`<button${attr_class("filter-btn small svelte-12ewbr5", void 0, { "active": selectedTier === tier.id })}>${escape_html(tier.label)}</button>`);
    }
    $$renderer2.push(`<!--]--></div></div> <div class="apps-grid svelte-12ewbr5"><!--[-->`);
    const each_array_2 = ensure_array_like(filteredApps);
    for (let $$index_3 = 0, $$length = each_array_2.length; $$index_3 < $$length; $$index_3++) {
      let app = each_array_2[$$index_3];
      $$renderer2.push(`<div${attr_class("app-card svelte-12ewbr5", void 0, { "internal": app.status === "internal" })}><div class="app-header svelte-12ewbr5"><span class="app-icon svelte-12ewbr5">${escape_html(app.icon)}</span> <div class="app-badges svelte-12ewbr5"><span${attr_class(`status-badge ${stringify(getStatusBadgeClass(app.status))}`, "svelte-12ewbr5")}>${escape_html(app.status.replace("_", " ").toUpperCase())}</span> <span${attr_class(`tier-badge ${stringify(getTierBadgeClass(app.tier))}`, "svelte-12ewbr5")}>${escape_html(app.tier.toUpperCase())}</span></div></div> <h3 class="app-name svelte-12ewbr5">${escape_html(app.name)}</h3> <p class="app-tagline svelte-12ewbr5">${escape_html(app.tagline)}</p> <p class="app-description svelte-12ewbr5">${escape_html(app.description)}</p> <div class="app-features svelte-12ewbr5"><!--[-->`);
      const each_array_3 = ensure_array_like(app.features.slice(0, 3));
      for (let $$index_2 = 0, $$length2 = each_array_3.length; $$index_2 < $$length2; $$index_2++) {
        let feature = each_array_3[$$index_2];
        $$renderer2.push(`<span class="feature-tag svelte-12ewbr5">${escape_html(feature)}</span>`);
      }
      $$renderer2.push(`<!--]--> `);
      if (app.features.length > 3) {
        $$renderer2.push("<!--[-->");
        $$renderer2.push(`<span class="feature-more svelte-12ewbr5">+${escape_html(app.features.length - 3)} more</span>`);
      } else {
        $$renderer2.push("<!--[!-->");
      }
      $$renderer2.push(`<!--]--></div> <div class="app-footer svelte-12ewbr5"><span class="app-price svelte-12ewbr5">${escape_html(app.price || "Contact Us")}</span> <div class="app-actions svelte-12ewbr5">`);
      if (app.status === "beta" || app.status === "live") {
        $$renderer2.push("<!--[-->");
        if (app.url) {
          $$renderer2.push("<!--[-->");
          $$renderer2.push(`<a${attr("href", app.url)} target="_blank" class="brutal-btn small svelte-12ewbr5">OPEN APP</a>`);
        } else {
          $$renderer2.push("<!--[!-->");
        }
        $$renderer2.push(`<!--]-->`);
      } else {
        $$renderer2.push("<!--[!-->");
        if (app.status === "coming_soon") {
          $$renderer2.push("<!--[-->");
          $$renderer2.push(`<button class="brutal-btn small disabled svelte-12ewbr5" disabled>NOTIFY ME</button>`);
        } else {
          $$renderer2.push("<!--[!-->");
          $$renderer2.push(`<span class="internal-label svelte-12ewbr5">INTERNAL</span>`);
        }
        $$renderer2.push(`<!--]-->`);
      }
      $$renderer2.push(`<!--]--></div></div> `);
      if (app.status === "beta" || app.status === "live") {
        $$renderer2.push("<!--[-->");
        const status = getAppStatus(app.id);
        if (status === "online") {
          $$renderer2.push("<!--[-->");
          $$renderer2.push(`<div class="app-status-bar online svelte-12ewbr5">● SERVICE ONLINE</div>`);
        } else {
          $$renderer2.push("<!--[!-->");
          if (status === "offline") {
            $$renderer2.push("<!--[-->");
            $$renderer2.push(`<div class="app-status-bar offline svelte-12ewbr5">○ SERVICE OFFLINE</div>`);
          } else {
            $$renderer2.push("<!--[!-->");
          }
          $$renderer2.push(`<!--]-->`);
        }
        $$renderer2.push(`<!--]-->`);
      } else {
        $$renderer2.push("<!--[!-->");
      }
      $$renderer2.push(`<!--]--></div>`);
    }
    $$renderer2.push(`<!--]--></div> <div class="upgrade-section svelte-12ewbr5"><div class="upgrade-content svelte-12ewbr5"><h3 class="svelte-12ewbr5">Unlock the Full Kraliki Suite</h3> <p class="svelte-12ewbr5">Get access to all apps with a Pro or Enterprise subscription. One login, all tools.</p> <div class="upgrade-tiers svelte-12ewbr5"><div class="tier-card svelte-12ewbr5"><h4 class="svelte-12ewbr5">Starter</h4> <p class="tier-price svelte-12ewbr5">€29/mo</p> <ul class="svelte-12ewbr5"><li class="svelte-12ewbr5">3 Apps</li> <li class="svelte-12ewbr5">Basic Support</li> <li class="svelte-12ewbr5">5 Team Members</li></ul></div> <div class="tier-card featured svelte-12ewbr5"><span class="featured-badge svelte-12ewbr5">POPULAR</span> <h4 class="svelte-12ewbr5">Pro</h4> <p class="tier-price svelte-12ewbr5">€99/mo</p> <ul class="svelte-12ewbr5"><li class="svelte-12ewbr5">All Apps</li> <li class="svelte-12ewbr5">Priority Support</li> <li class="svelte-12ewbr5">Unlimited Team</li> <li class="svelte-12ewbr5">API Access</li></ul></div> <div class="tier-card svelte-12ewbr5"><h4 class="svelte-12ewbr5">Enterprise</h4> <p class="tier-price svelte-12ewbr5">Custom</p> <ul class="svelte-12ewbr5"><li class="svelte-12ewbr5">All Apps + Kraliki</li> <li class="svelte-12ewbr5">Dedicated Support</li> <li class="svelte-12ewbr5">Custom Integrations</li> <li class="svelte-12ewbr5">On-Premise Option</li></ul></div></div></div></div></div>`);
  });
}
export {
  _page as default
};
