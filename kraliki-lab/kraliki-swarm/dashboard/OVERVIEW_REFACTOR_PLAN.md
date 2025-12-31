# Plan: Dashboard Overview Refactoring (VD-622)

## 1. Current State Analysis
The current `Overview` page (`/`) acts as a monolithic dashboard displaying:
1.  **System Health** (Status, Uptime, Commits)
2.  **Focus** (Daily Plan)
3.  **Process Manager** (PM2 Status)
4.  **Linear Issues** (Active & Pending)
5.  **Recall Stats**
6.  **Memory Stats**
7.  **Leaderboard**
8.  **Agent Status Table** (Real-time list)
9.  **Lab Analytics** (Points by Lab)
10. **Genome Stats**
11. **Cost Analytics**
12. **Circuit Breakers**
13. **Orchestrators**
14. **Decision Traces**
15. **Crash Analytics**
16. **Fitness Reports**
17. **Social Pulse**
18. **Heat Map**
19. **Recent Files**
20. **Task Queue**
21. **Blackboard Feed**

**Total Components:** ~21 widgets.
**Issue:** Extreme visual clutter, high cognitive load, and potential performance impact (fetching all data at once).

## 2. Problem Statement
The Overview page tries to answer every question at once ("Is the system healthy?", "What are agents doing?", "How much money are we spending?", "What are the bugs?"). This violates the principle of separation of concerns and makes the "Main Menu" less effective as a launching pad.

## 3. Proposed Solution: The "Control Deck" Strategy

We propose replacing the current monolithic Overview with a **"Control Deck"** and distributing detailed widgets to specialized pages.

### A. New Home Page (The Control Deck)
The new `/` route should be minimal and action-oriented.
**Components to Keep:**
1.  **System Status Banner** (Critical Health: Red/Green)
2.  **Focus / Daily Objective** (What is the human supposed to do?)
3.  **Active Agents Summary** (Just a count or mini-list of *running* agents)
4.  **Quick Actions Grid** (Large buttons to "Spawn Agent", "Open Notebook", "View Issues")
5.  **Blackboard Feed** (The narrative pulse of the swarm)

**Everything else is moved.**

### B. Distribution Strategy

| Widget | Current Location | Proposed New Location | Rationale |
| :--- | :--- | :--- | :--- |
| **PM2 Process List** | Overview | `/health` | Technical operational detail. |
| **Linear Issues** | Overview | `/jobs` or `/linear` | already has a dedicated page (implied). |
| **Recall / Memory** | Overview | `/recall` or `/brain` | Specialized knowledge base stats. |
| **Leaderboard** | Overview | `/leaderboard` | Gamification element, not critical ops. |
| **Agent Status Table** | Overview | `/agents` | Full list belongs on the Agents page. |
| **Lab Analytics** | Overview | `/insights` | Business intelligence / long-term stats. |
| **Genome Stats** | Overview | `/genomes` | Configuration/Genetic data. |
| **Cost Analytics** | Overview | `/costs` | Financials. |
| **Circuit Breakers** | Overview | `/health` | Critical infrastructure health. |
| **Orchestrators** | Overview | `/agents` or `/health` | Orchestration details. |
| **Crash Analytics** | Overview | `/health` | Debugging info. |
| **Fitness Reports** | Overview | `/insights` | Quality metrics. |
| **Social Pulse** | Overview | `/comms` | Communication stream. |
| **Heat Map / Files** | Overview | `/data` or `/insights` | Dev activity metrics. |
| **Task Queue** | Overview | `/jobs` | Work management. |

### C. The Notebook Integration
We have added `/notebook` as a dedicated "Scratchpad".
*   **Future Enhancement:** Add a "Quick Note" widget to the new Control Deck that links to the full Notebook.

## 4. Execution Plan (Next Steps)

1.  **Phase 1 (Done):** Add Notebook page (`/notebook`) and Menu Item.
2.  **Phase 2 (Done):** Verified existing routes (`/health`, `/agents`, `/linear`) contain PM2, circuit breakers, agent status, and Linear issues data.
3.  **Phase 3 (Done - 2025-12-30):** Created simplified "Control Deck" `+page.svelte` with:
    - System Status Banner (health indicator)
    - Focus / Daily Objective
    - Active Agents Summary
    - Quick Actions Grid (8 large buttons)
    - Blackboard Feed
4.  **Phase 4:** Test and verify functionality. (Backup saved as `+page.svelte.backup`)

## What Was Moved
- **PM2 Process List** → Already on `/health`
- **Circuit Breakers** → Already on `/health` and `/agents`
- **Full Agent Status Table** → Already on `/agents`
- **Linear Issues** → Already on `/linear`
- **Recall/Memory Stats** → Already on `/recall` and `/memory`
- **Lab/Genome/Cost Analytics** → Already on dedicated pages

## 5. Decision Required
*   **Approve "Control Deck" concept?** (Y/N)
*   **Approve moving PM2/Breakers to `/health`?** (Y/N)

This plan minimizes risk by ensuring destination pages exist before deleting the Overview widgets.
