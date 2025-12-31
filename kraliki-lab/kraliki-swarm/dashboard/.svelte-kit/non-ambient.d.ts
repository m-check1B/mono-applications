
// this file is generated — do not edit it


declare module "svelte/elements" {
	export interface HTMLAttributes<T> {
		'data-sveltekit-keepfocus'?: true | '' | 'off' | undefined | null;
		'data-sveltekit-noscroll'?: true | '' | 'off' | undefined | null;
		'data-sveltekit-preload-code'?:
			| true
			| ''
			| 'eager'
			| 'viewport'
			| 'hover'
			| 'tap'
			| 'off'
			| undefined
			| null;
		'data-sveltekit-preload-data'?: true | '' | 'hover' | 'tap' | 'off' | undefined | null;
		'data-sveltekit-reload'?: true | '' | 'off' | undefined | null;
		'data-sveltekit-replacestate'?: true | '' | 'off' | undefined | null;
	}
}

export {};


declare module "$app/types" {
	export interface AppTypes {
		RouteId(): "/" | "/agent-board" | "/agents" | "/api" | "/api/agents" | "/api/brain" | "/api/brain/strategy" | "/api/circuit-breakers" | "/api/cli-policy" | "/api/comms" | "/api/costs" | "/api/crm" | "/api/dashboard-redeploy" | "/api/genomes" | "/api/genomes/[name]" | "/api/health" | "/api/human-blockers" | "/api/insights" | "/api/insights/boards" | "/api/insights/posts" | "/api/insights/posts/[boardId]" | "/api/insights/[...path]" | "/api/integrations" | "/api/integrations/focus" | "/api/integrations/voice" | "/api/jobs" | "/api/lab" | "/api/lab/alerts" | "/api/lab/alerts/[id]" | "/api/lab/alerts/[id]/resolve" | "/api/lab/customers" | "/api/lab/metrics" | "/api/lab/metrics/fleet" | "/api/lab/vms" | "/api/lab/vms/[id]" | "/api/lab/vms/[id]/rebuild" | "/api/lab/vms/[id]/restart" | "/api/leaderboard" | "/api/learn" | "/api/memory" | "/api/memory/consolidate" | "/api/pause-swarm" | "/api/pipeline-policy" | "/api/power-swarm" | "/api/reach" | "/api/reach/agents" | "/api/reach/campaigns" | "/api/reach/queue" | "/api/reset-soft" | "/api/reset" | "/api/scopes" | "/api/spawn" | "/api/status" | "/api/traces" | "/api/voice" | "/api/voice/analytics" | "/api/voice/campaigns" | "/api/voice/health" | "/api/voice/providers" | "/api/voice/sessions" | "/api/voice/teams" | "/api/vop" | "/api/vop/conversations" | "/api/vop/surveys" | "/api/windmill" | "/api/windmill/health" | "/apple-touch-icon-precomposed.png" | "/apple-touch-icon.png" | "/apps" | "/auth" | "/auth/callback" | "/auth/login" | "/auth/register" | "/auth/sso" | "/blackboard" | "/brain" | "/comms" | "/costs" | "/crm" | "/data" | "/favicon.ico" | "/genomes" | "/health" | "/insights" | "/jobs" | "/lab" | "/leaderboard" | "/learn" | "/linear" | "/memory" | "/notebook" | "/reach" | "/recall" | "/see" | "/see/traces" | "/settings" | "/terminal" | "/workflows";
		RouteParams(): {
			"/api/genomes/[name]": { name: string };
			"/api/insights/posts/[boardId]": { boardId: string };
			"/api/insights/[...path]": { path: string };
			"/api/lab/alerts/[id]": { id: string };
			"/api/lab/alerts/[id]/resolve": { id: string };
			"/api/lab/vms/[id]": { id: string };
			"/api/lab/vms/[id]/rebuild": { id: string };
			"/api/lab/vms/[id]/restart": { id: string }
		};
		LayoutParams(): {
			"/": { name?: string; boardId?: string; path?: string; id?: string };
			"/agent-board": Record<string, never>;
			"/agents": Record<string, never>;
			"/api": { name?: string; boardId?: string; path?: string; id?: string };
			"/api/agents": Record<string, never>;
			"/api/brain": Record<string, never>;
			"/api/brain/strategy": Record<string, never>;
			"/api/circuit-breakers": Record<string, never>;
			"/api/cli-policy": Record<string, never>;
			"/api/comms": Record<string, never>;
			"/api/costs": Record<string, never>;
			"/api/crm": Record<string, never>;
			"/api/dashboard-redeploy": Record<string, never>;
			"/api/genomes": { name?: string };
			"/api/genomes/[name]": { name: string };
			"/api/health": Record<string, never>;
			"/api/human-blockers": Record<string, never>;
			"/api/insights": { boardId?: string; path?: string };
			"/api/insights/boards": Record<string, never>;
			"/api/insights/posts": { boardId?: string };
			"/api/insights/posts/[boardId]": { boardId: string };
			"/api/insights/[...path]": { path: string };
			"/api/integrations": Record<string, never>;
			"/api/integrations/focus": Record<string, never>;
			"/api/integrations/voice": Record<string, never>;
			"/api/jobs": Record<string, never>;
			"/api/lab": { id?: string };
			"/api/lab/alerts": { id?: string };
			"/api/lab/alerts/[id]": { id: string };
			"/api/lab/alerts/[id]/resolve": { id: string };
			"/api/lab/customers": Record<string, never>;
			"/api/lab/metrics": Record<string, never>;
			"/api/lab/metrics/fleet": Record<string, never>;
			"/api/lab/vms": { id?: string };
			"/api/lab/vms/[id]": { id: string };
			"/api/lab/vms/[id]/rebuild": { id: string };
			"/api/lab/vms/[id]/restart": { id: string };
			"/api/leaderboard": Record<string, never>;
			"/api/learn": Record<string, never>;
			"/api/memory": Record<string, never>;
			"/api/memory/consolidate": Record<string, never>;
			"/api/pause-swarm": Record<string, never>;
			"/api/pipeline-policy": Record<string, never>;
			"/api/power-swarm": Record<string, never>;
			"/api/reach": Record<string, never>;
			"/api/reach/agents": Record<string, never>;
			"/api/reach/campaigns": Record<string, never>;
			"/api/reach/queue": Record<string, never>;
			"/api/reset-soft": Record<string, never>;
			"/api/reset": Record<string, never>;
			"/api/scopes": Record<string, never>;
			"/api/spawn": Record<string, never>;
			"/api/status": Record<string, never>;
			"/api/traces": Record<string, never>;
			"/api/voice": Record<string, never>;
			"/api/voice/analytics": Record<string, never>;
			"/api/voice/campaigns": Record<string, never>;
			"/api/voice/health": Record<string, never>;
			"/api/voice/providers": Record<string, never>;
			"/api/voice/sessions": Record<string, never>;
			"/api/voice/teams": Record<string, never>;
			"/api/vop": Record<string, never>;
			"/api/vop/conversations": Record<string, never>;
			"/api/vop/surveys": Record<string, never>;
			"/api/windmill": Record<string, never>;
			"/api/windmill/health": Record<string, never>;
			"/apple-touch-icon-precomposed.png": Record<string, never>;
			"/apple-touch-icon.png": Record<string, never>;
			"/apps": Record<string, never>;
			"/auth": Record<string, never>;
			"/auth/callback": Record<string, never>;
			"/auth/login": Record<string, never>;
			"/auth/register": Record<string, never>;
			"/auth/sso": Record<string, never>;
			"/blackboard": Record<string, never>;
			"/brain": Record<string, never>;
			"/comms": Record<string, never>;
			"/costs": Record<string, never>;
			"/crm": Record<string, never>;
			"/data": Record<string, never>;
			"/favicon.ico": Record<string, never>;
			"/genomes": Record<string, never>;
			"/health": Record<string, never>;
			"/insights": Record<string, never>;
			"/jobs": Record<string, never>;
			"/lab": Record<string, never>;
			"/leaderboard": Record<string, never>;
			"/learn": Record<string, never>;
			"/linear": Record<string, never>;
			"/memory": Record<string, never>;
			"/notebook": Record<string, never>;
			"/reach": Record<string, never>;
			"/recall": Record<string, never>;
			"/see": Record<string, never>;
			"/see/traces": Record<string, never>;
			"/settings": Record<string, never>;
			"/terminal": Record<string, never>;
			"/workflows": Record<string, never>
		};
		Pathname(): "/" | "/agent-board" | "/agent-board/" | "/agents" | "/agents/" | "/api" | "/api/" | "/api/agents" | "/api/agents/" | "/api/brain" | "/api/brain/" | "/api/brain/strategy" | "/api/brain/strategy/" | "/api/circuit-breakers" | "/api/circuit-breakers/" | "/api/cli-policy" | "/api/cli-policy/" | "/api/comms" | "/api/comms/" | "/api/costs" | "/api/costs/" | "/api/crm" | "/api/crm/" | "/api/dashboard-redeploy" | "/api/dashboard-redeploy/" | "/api/genomes" | "/api/genomes/" | `/api/genomes/${string}` & {} | `/api/genomes/${string}/` & {} | "/api/health" | "/api/health/" | "/api/human-blockers" | "/api/human-blockers/" | "/api/insights" | "/api/insights/" | "/api/insights/boards" | "/api/insights/boards/" | "/api/insights/posts" | "/api/insights/posts/" | `/api/insights/posts/${string}` & {} | `/api/insights/posts/${string}/` & {} | `/api/insights/${string}` & {} | `/api/insights/${string}/` & {} | "/api/integrations" | "/api/integrations/" | "/api/integrations/focus" | "/api/integrations/focus/" | "/api/integrations/voice" | "/api/integrations/voice/" | "/api/jobs" | "/api/jobs/" | "/api/lab" | "/api/lab/" | "/api/lab/alerts" | "/api/lab/alerts/" | `/api/lab/alerts/${string}` & {} | `/api/lab/alerts/${string}/` & {} | `/api/lab/alerts/${string}/resolve` & {} | `/api/lab/alerts/${string}/resolve/` & {} | "/api/lab/customers" | "/api/lab/customers/" | "/api/lab/metrics" | "/api/lab/metrics/" | "/api/lab/metrics/fleet" | "/api/lab/metrics/fleet/" | "/api/lab/vms" | "/api/lab/vms/" | `/api/lab/vms/${string}` & {} | `/api/lab/vms/${string}/` & {} | `/api/lab/vms/${string}/rebuild` & {} | `/api/lab/vms/${string}/rebuild/` & {} | `/api/lab/vms/${string}/restart` & {} | `/api/lab/vms/${string}/restart/` & {} | "/api/leaderboard" | "/api/leaderboard/" | "/api/learn" | "/api/learn/" | "/api/memory" | "/api/memory/" | "/api/memory/consolidate" | "/api/memory/consolidate/" | "/api/pause-swarm" | "/api/pause-swarm/" | "/api/pipeline-policy" | "/api/pipeline-policy/" | "/api/power-swarm" | "/api/power-swarm/" | "/api/reach" | "/api/reach/" | "/api/reach/agents" | "/api/reach/agents/" | "/api/reach/campaigns" | "/api/reach/campaigns/" | "/api/reach/queue" | "/api/reach/queue/" | "/api/reset-soft" | "/api/reset-soft/" | "/api/reset" | "/api/reset/" | "/api/scopes" | "/api/scopes/" | "/api/spawn" | "/api/spawn/" | "/api/status" | "/api/status/" | "/api/traces" | "/api/traces/" | "/api/voice" | "/api/voice/" | "/api/voice/analytics" | "/api/voice/analytics/" | "/api/voice/campaigns" | "/api/voice/campaigns/" | "/api/voice/health" | "/api/voice/health/" | "/api/voice/providers" | "/api/voice/providers/" | "/api/voice/sessions" | "/api/voice/sessions/" | "/api/voice/teams" | "/api/voice/teams/" | "/api/vop" | "/api/vop/" | "/api/vop/conversations" | "/api/vop/conversations/" | "/api/vop/surveys" | "/api/vop/surveys/" | "/api/windmill" | "/api/windmill/" | "/api/windmill/health" | "/api/windmill/health/" | "/apple-touch-icon-precomposed.png" | "/apple-touch-icon-precomposed.png/" | "/apple-touch-icon.png" | "/apple-touch-icon.png/" | "/apps" | "/apps/" | "/auth" | "/auth/" | "/auth/callback" | "/auth/callback/" | "/auth/login" | "/auth/login/" | "/auth/register" | "/auth/register/" | "/auth/sso" | "/auth/sso/" | "/blackboard" | "/blackboard/" | "/brain" | "/brain/" | "/comms" | "/comms/" | "/costs" | "/costs/" | "/crm" | "/crm/" | "/data" | "/data/" | "/favicon.ico" | "/favicon.ico/" | "/genomes" | "/genomes/" | "/health" | "/health/" | "/insights" | "/insights/" | "/jobs" | "/jobs/" | "/lab" | "/lab/" | "/leaderboard" | "/leaderboard/" | "/learn" | "/learn/" | "/linear" | "/linear/" | "/memory" | "/memory/" | "/notebook" | "/notebook/" | "/reach" | "/reach/" | "/recall" | "/recall/" | "/see" | "/see/" | "/see/traces" | "/see/traces/" | "/settings" | "/settings/" | "/terminal" | "/terminal/" | "/workflows" | "/workflows/";
		ResolvedPathname(): `${"" | `/${string}`}${ReturnType<AppTypes['Pathname']>}`;
		Asset(): "/favicon.svg" | "/robots.txt" | string & {};
	}
}