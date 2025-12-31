# Agent Capability Analysis: "Human Ops" Tasks
**Date:** December 20, 2025
**Context:** Assessment of autonomous AI agents against tasks requiring real-world account creation, identity verification, and secure infrastructure management.

## Executive Summary

As of late 2025, while AI agents have mastered code generation and localized execution environments (Devin, OpenCode), they still hit a "hard wall" with **Human Operations (Human Ops)**. 

The primary blockers are not intelligence, but **identity and authentication**:
1.  **2FA & Phone Verification:** Agents lack persistent phone numbers/SIM cards required for Telegram, Stripe, and Google Cloud.
2.  **KYC & Legal:** Financial services (Stripe) require government ID uploads and live identity verification which agents cannot legally fake.
3.  **Anti-Bot Measures:** Cloudflare and CAPTCHAs effectively block automated browsers (Claude Computer Use, Selenium-based agents).
4.  **Credential Security:** Passing root passwords or API keys to cloud-hosted agents (OpenAI, Anthropic) remains a massive security policy violation for most organizations.

---

## Task-by-Task Feasibility Matrix

| Task | Feasibility | Primary Blocker | Best Suited Agent |
| :--- | :---: | :--- | :--- |
| **1. Create Telegram Bot** | 🔴 **Impossible** | Requires mobile phone number & SMS 2FA. | Human Required |
| **2. Create Cal.com Account** | 🟡 **Difficult** | Email verification loop + potential CAPTCHA. | Claude Computer Use |
| **3. SSH & Check Server** | 🟢 **Solved** | None, provided keys are handled safely. | Devin / Custom Scripts |
| **4. Configure EspoCRM** | 🟡 **Possible** | Complex UI navigation, state management. | Claude Computer Use |
| **5. Create Formspree Account** | 🟡 **Difficult** | Email confirmation loop. | Claude Computer Use |
| **6. Configure Cloudflare DNS** | 🔴 **Risky** | Login protections (Turnstile) are designed to block this. | Human Required |
| **7. Create Stripe Account** | 🔴 **Impossible** | **KYC (Know Your Customer)**, ID upload, Bank Auth. | Human Required |
| **8. Post to LinkedIn** | 🟡 **Possible** | API is safer; Web UI risks account ban (anti-bot). | Custom API Script |
| **9. SSH with Password** | 🟢 **Solved** | Trivial for CLI agents, but security risk to share pwd. | Devin / CLI Agent |
| **10. Enable GCP Vertex AI** | 🔴 **Difficult** | Requires billing setup (CC) + potential phone verify. | Human Required |

---

## Detailed Agent Analysis

### 1. Claude Computer Use (Anthropic)
**Mechanism:** Screenshot-to-coordinate mapping, controlling virtual mouse/keyboard.
*   **Pros:** Can theoretically click through *any* UI (EspoCRM, Cal.com).
*   **Cons:** Extremely slow compared to API calls. Fragile. If a "I'm not a robot" CAPTCHA appears, it often fails or gets flagged by behavioral analysis (mouse movement doesn't look human enough).
*   **Verdict:** Good for configuring internal tools (EspoCRM) where CAPTCHAs are disabled, but fails on public sign-ups (Cloudflare/Stripe).

### 2. Devin (Cognition) & OpenCode Interpreters
**Mechanism:** Containerized dev environment with shell/browser access.
*   **Pros:** Excellent at Task #3 (SSH checks) and #9 (SSH commands). Can script interactions.
*   **Cons:** Not designed for "human" browsing. If the task requires a GUI browser (not headless), it struggles. It cannot own a phone number for Task #1.
*   **Verdict:** The king of engineering tasks, but useless for administrative account creation.

### 3. OpenAI Operator / ChatGPT Agent
**Mechanism:** Tool-calling LLM with browsing capabilities.
*   **Pros:** High reasoning capability. Good for generating the *content* for LinkedIn (#8).
*   **Cons:** "Walled garden" limitations often prevent it from logging into external accounts or solving CAPTCHAs due to safety guardrails. It will refuse to perform actions that look like "hacking" or "financial impersonation" (Stripe).
*   **Verdict:** Best as a copilot, not an autonomous operator for these tasks.

### 4. Manus / Generalist Agents
**Mechanism:** "Operating System" level agents.
*   **Pros:** designed to bridge apps.
*   **Cons:** Still bound by the physical world constraints. Unless the user provisions a "virtual mobile phone" API service (like Twilio) and hooks it into the agent's tools *beforehand*, the agent cannot pass 2FA.

### 5. Perplexity
**Mechanism:** Search & Answer engine.
*   **Pros:** Great at finding *how* to do these tasks.
*   **Cons:** **Read-only**. Cannot perform actions.
*   **Verdict:** Research tool only.

---

## The "Human-in-the-Loop" Gap

To automate these 10 tasks, you don't need a better AI model; you need **Infrastructure for Agents**:

1.  **Identity Proxy:** A service providing temporary email inboxes + SMS numbers that the agent can read.
2.  **KYC/Auth Vault:** A secure way for the agent to retrieve the user's Passport ID/Credit Card without the LLM seeing the raw data (currently unsolved).
3.  **Human Handoff:** The agent should do the filling out, then pause and ping the human for: "Please solve this CAPTCHA" or "Please verify the SMS code sent to your phone."

**Conclusion:** For December 2025, a hybrid approach is required. Use **Devin** for the SSH/Server tasks and a human for the Account Creation/KYC tasks.
