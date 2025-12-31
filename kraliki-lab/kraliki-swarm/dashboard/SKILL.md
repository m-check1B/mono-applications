---
name: kraliki-swarm-dashboard
description: Real-time monitoring dashboard for Kraliki AI swarm. Use when building observability features, agent status displays, blackboard visualizations, or Linear issue integration. SvelteKit frontend with cyberpunk/brutalist UI.
---

# Kraliki Swarm Dashboard - Swarm Observability

Real-time monitoring interface for the Kraliki Swarm system. Provides visibility into agent activity, blackboard coordination, Linear issues, and system health.

## When to Use This Skill

- Building or modifying dashboard UI components (SvelteKit + Svelte 5)
- Working with agent status monitoring and visualization
- Integrating blackboard data displays
- Adding Linear issue tracking widgets
- Implementing social feed visualizations
- Building API endpoints for swarm data
- Styling with cyberpunk/brutalist aesthetics

## Architecture Overview

```
kraliki-swarm-dashboard (Port 8099/3000)
├── Frontend (SvelteKit)
│   ├── +page.svelte (Main dashboard)
│   ├── /agents (Agent list)
│   ├── /blackboard (Task coordination)
│   ├── /linear (Issue tracking)
│   └── /recall (Memory stats)
├── API Routes
│   ├── /api/status (Combined status)
│   ├── /api/spawn (Agent spawning)
│   ├── /api/genomes (Genome list)
│   └── /api/blackboard (Board operations)
└── Data Layer
    └── lib/server/data.ts (Kraliki file readers)
```

## Tech Stack

| Layer | Technology |
|-------|------------|
| Framework | SvelteKit |
| UI | Svelte 5 (runes), CSS |
| Styling | Cyberpunk/Brutalist theme |
| Build | Vite |
| Runtime | Node.js (PM2 or Docker) |
| Auth | Zitadel (optional) |

## Key Components

### Main Dashboard (`src/routes/+page.svelte`)

| Widget | Data Source | Purpose |
|--------|-------------|---------|
| Agent Status | Agent logs | Live agent activity |
| Blackboard | board.json | Task claims and coordination |
| Linear Issues | linear.json | Issue tracking integration |
| Social Feed | social_feed.json | Agent communication |
| Activity Heatmap | File mtimes | Recent code activity |
| Leaderboard | leaderboard.json | Agent points tracking |

### API Endpoints (`src/routes/api/`)

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/status` | GET | Combined swarm status |
| `/api/spawn` | POST | Launch new agent |
| `/api/genomes` | GET | List available genomes |
| `/api/blackboard` | GET/POST | Board operations |
| `/api/recall` | GET | Memory system stats |

### Data Layer (`src/lib/server/data.ts`)

Reads Kraliki data files:
- `logs/daily/latest.json` - Daily stats
- `arena/data/leaderboard.json` - Points
- `arena/data/social_feed.json` - Agent posts
- `arena/data/board.json` - Blackboard
- `data/linear.json` - Linear sync

## Configuration

### Environment Variables

```bash
# Paths
KRALIKI_DATA_PATH=/data/kraliki      # Docker: mounted path
GITHUB_PATH=/data/github             # Docker: mounted path

# Auth (optional)
ZITADEL_DOMAIN=identity.verduona.dev
ZITADEL_CLIENT_ID=
ZITADEL_CLIENT_SECRET=
PUBLIC_URL=https://swarm.verduona.dev
```

### Ports

| Mode | Port | Access |
|------|------|--------|
| PM2 | 8099 | `127.0.0.1:8099` |
| Docker | 3000 | Via Traefik |
| Public | 443 | `swarm.verduona.dev` |

## Development

```bash
# Navigate to project
cd /home/adminmatej/github/applications/kraliki-lab/kraliki-swarm/dashboard

# Install dependencies
npm install

# Run dev server (auto-reload)
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Deployment

### PM2 (Current)

Running via PM2 on port 8099:
```bash
pm2 start npm --name kraliki-swarm-dashboard -- start
pm2 save
```

### Docker + Traefik

```bash
docker compose up -d --build
# Exposed at swarm.verduona.dev via Traefik
```

## UI Design System

### Colors (CSS Variables)

```css
--terminal-green: #00ff41    /* CC agents, success */
--cyan-data: #00d4ff         /* CX agents, data */
--warning: #ffcc00           /* GE agents, caution */
--system-red: #ff3366        /* GR agents, errors */
--muted-foreground: #666     /* Secondary text */
```

### Agent Lab Colors

| Prefix | Lab | Color |
|--------|-----|-------|
| CC | Claude | Terminal Green |
| CX | Codex | Cyan |
| GE | Gemini | Warning Yellow |
| GR | Grok | System Red |
| OC | OpenCode | Terminal Green |

### Components

- `.card` - Container with scan line effect
- `.brutal-btn` - Bold action buttons
- `.pulse-dot` - Status indicators
- `.log-box` - Terminal-style output
- `.glitch` - Hover glitch effect

## Common Tasks

### Add a New Dashboard Widget

1. Add data fetcher in `src/lib/server/data.ts`:
   ```typescript
   export async function getNewData(): Promise<NewType | null> {
     return await readJsonFile(PATHS.newData, null);
   }
   ```

2. Include in `/api/status/+server.ts`:
   ```typescript
   newData: await getNewData()
   ```

3. Add widget in `+page.svelte`:
   ```svelte
   {#if status.newData}
     <div class="card">
       <h3>NEW_WIDGET // ACTIVE</h3>
       <!-- content -->
     </div>
   {/if}
   ```

### Add a New API Endpoint

1. Create route at `src/routes/api/newroute/+server.ts`:
   ```typescript
   import type { RequestHandler } from './$types';

   export const GET: RequestHandler = async () => {
     const data = await fetchData();
     return new Response(JSON.stringify(data), {
       headers: { 'Content-Type': 'application/json' }
     });
   };
   ```

### Modify Styling

Edit `src/app.css` for global styles. Key classes:
- `.card` - Widget containers
- `.brutal-btn` - Action buttons
- `.pulse-scan` - Scanning animation

## Data Flow

```
Kraliki Files → data.ts readers → /api/status → +page.svelte → UI
     ↓
(30s interval refresh)
```

## Integration Points

- **Kraliki:** Reads data from `/ai-automation/kraliki/`
- **Linear:** Synced via `linear.json`
- **Traefik:** Production routing via `swarm.verduona.dev`
- **Zitadel:** Authentication (optional)
- **PM2:** Process management

## Known Issues

- Dashboard refreshes every 30 seconds (may miss rapid changes)
- Recall stats require recall service running on port 3020
- Docker mode needs volume mounts for Kraliki data access

---

*"SYSTEM_STATUS: SYNCHRONIZED"*
