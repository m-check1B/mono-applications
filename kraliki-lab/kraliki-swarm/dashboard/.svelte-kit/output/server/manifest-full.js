export const manifest = (() => {
function __memo(fn) {
	let value;
	return () => value ??= (value = fn());
}

return {
	appDir: "_app",
	appPath: "_app",
	assets: new Set(["favicon.svg","robots.txt"]),
	mimeTypes: {".svg":"image/svg+xml",".txt":"text/plain"},
	_: {
		client: {start:"_app/immutable/entry/start.CmqTgex5.js",app:"_app/immutable/entry/app.CC2x-q1g.js",imports:["_app/immutable/entry/start.CmqTgex5.js","_app/immutable/chunks/BH447Nci.js","_app/immutable/chunks/CHIrzwsT.js","_app/immutable/chunks/DZKKosdP.js","_app/immutable/chunks/BHyL2apj.js","_app/immutable/entry/app.CC2x-q1g.js","_app/immutable/chunks/PPVm8Dsz.js","_app/immutable/chunks/CHIrzwsT.js","_app/immutable/chunks/DsvTbyZG.js","_app/immutable/chunks/CaHQap0G.js","_app/immutable/chunks/CZY_NlAX.js","_app/immutable/chunks/BHyL2apj.js","_app/immutable/chunks/DNv7RG3c.js","_app/immutable/chunks/DWj8Yt1E.js","_app/immutable/chunks/C46B7vkt.js","_app/immutable/chunks/CKCuCExv.js","_app/immutable/chunks/DZKKosdP.js"],stylesheets:[],fonts:[],uses_env_dynamic_public:false},
		nodes: [
			__memo(() => import('./nodes/0.js')),
			__memo(() => import('./nodes/1.js')),
			__memo(() => import('./nodes/2.js')),
			__memo(() => import('./nodes/3.js')),
			__memo(() => import('./nodes/4.js')),
			__memo(() => import('./nodes/5.js')),
			__memo(() => import('./nodes/6.js')),
			__memo(() => import('./nodes/7.js')),
			__memo(() => import('./nodes/8.js')),
			__memo(() => import('./nodes/9.js')),
			__memo(() => import('./nodes/10.js')),
			__memo(() => import('./nodes/11.js')),
			__memo(() => import('./nodes/12.js')),
			__memo(() => import('./nodes/13.js')),
			__memo(() => import('./nodes/14.js')),
			__memo(() => import('./nodes/15.js')),
			__memo(() => import('./nodes/16.js')),
			__memo(() => import('./nodes/17.js')),
			__memo(() => import('./nodes/18.js')),
			__memo(() => import('./nodes/19.js')),
			__memo(() => import('./nodes/20.js')),
			__memo(() => import('./nodes/21.js')),
			__memo(() => import('./nodes/22.js')),
			__memo(() => import('./nodes/23.js')),
			__memo(() => import('./nodes/24.js')),
			__memo(() => import('./nodes/25.js')),
			__memo(() => import('./nodes/26.js')),
			__memo(() => import('./nodes/27.js')),
			__memo(() => import('./nodes/28.js')),
			__memo(() => import('./nodes/29.js')),
			__memo(() => import('./nodes/30.js'))
		],
		remotes: {
			
		},
		routes: [
			{
				id: "/",
				pattern: /^\/$/,
				params: [],
				page: { layouts: [0,], errors: [1,], leaf: 2 },
				endpoint: null
			},
			{
				id: "/agent-board",
				pattern: /^\/agent-board\/?$/,
				params: [],
				page: { layouts: [0,], errors: [1,], leaf: 3 },
				endpoint: null
			},
			{
				id: "/agents",
				pattern: /^\/agents\/?$/,
				params: [],
				page: { layouts: [0,], errors: [1,], leaf: 4 },
				endpoint: null
			},
			{
				id: "/api/agents",
				pattern: /^\/api\/agents\/?$/,
				params: [],
				page: null,
				endpoint: __memo(() => import('./entries/endpoints/api/agents/_server.ts.js'))
			},
			{
				id: "/api/brain",
				pattern: /^\/api\/brain\/?$/,
				params: [],
				page: null,
				endpoint: __memo(() => import('./entries/endpoints/api/brain/_server.ts.js'))
			},
			{
				id: "/api/brain/strategy",
				pattern: /^\/api\/brain\/strategy\/?$/,
				params: [],
				page: null,
				endpoint: __memo(() => import('./entries/endpoints/api/brain/strategy/_server.ts.js'))
			},
			{
				id: "/api/circuit-breakers",
				pattern: /^\/api\/circuit-breakers\/?$/,
				params: [],
				page: null,
				endpoint: __memo(() => import('./entries/endpoints/api/circuit-breakers/_server.ts.js'))
			},
			{
				id: "/api/cli-policy",
				pattern: /^\/api\/cli-policy\/?$/,
				params: [],
				page: null,
				endpoint: __memo(() => import('./entries/endpoints/api/cli-policy/_server.ts.js'))
			},
			{
				id: "/api/comms",
				pattern: /^\/api\/comms\/?$/,
				params: [],
				page: null,
				endpoint: __memo(() => import('./entries/endpoints/api/comms/_server.ts.js'))
			},
			{
				id: "/api/costs",
				pattern: /^\/api\/costs\/?$/,
				params: [],
				page: null,
				endpoint: __memo(() => import('./entries/endpoints/api/costs/_server.ts.js'))
			},
			{
				id: "/api/crm",
				pattern: /^\/api\/crm\/?$/,
				params: [],
				page: null,
				endpoint: __memo(() => import('./entries/endpoints/api/crm/_server.ts.js'))
			},
			{
				id: "/api/dashboard-redeploy",
				pattern: /^\/api\/dashboard-redeploy\/?$/,
				params: [],
				page: null,
				endpoint: __memo(() => import('./entries/endpoints/api/dashboard-redeploy/_server.ts.js'))
			},
			{
				id: "/api/genomes",
				pattern: /^\/api\/genomes\/?$/,
				params: [],
				page: null,
				endpoint: __memo(() => import('./entries/endpoints/api/genomes/_server.ts.js'))
			},
			{
				id: "/api/genomes/[name]",
				pattern: /^\/api\/genomes\/([^/]+?)\/?$/,
				params: [{"name":"name","optional":false,"rest":false,"chained":false}],
				page: null,
				endpoint: __memo(() => import('./entries/endpoints/api/genomes/_name_/_server.ts.js'))
			},
			{
				id: "/api/health",
				pattern: /^\/api\/health\/?$/,
				params: [],
				page: null,
				endpoint: __memo(() => import('./entries/endpoints/api/health/_server.ts.js'))
			},
			{
				id: "/api/human-blockers",
				pattern: /^\/api\/human-blockers\/?$/,
				params: [],
				page: null,
				endpoint: __memo(() => import('./entries/endpoints/api/human-blockers/_server.ts.js'))
			},
			{
				id: "/api/insights",
				pattern: /^\/api\/insights\/?$/,
				params: [],
				page: null,
				endpoint: __memo(() => import('./entries/endpoints/api/insights/_server.ts.js'))
			},
			{
				id: "/api/insights/boards",
				pattern: /^\/api\/insights\/boards\/?$/,
				params: [],
				page: null,
				endpoint: __memo(() => import('./entries/endpoints/api/insights/boards/_server.ts.js'))
			},
			{
				id: "/api/insights/posts",
				pattern: /^\/api\/insights\/posts\/?$/,
				params: [],
				page: null,
				endpoint: __memo(() => import('./entries/endpoints/api/insights/posts/_server.ts.js'))
			},
			{
				id: "/api/insights/posts/[boardId]",
				pattern: /^\/api\/insights\/posts\/([^/]+?)\/?$/,
				params: [{"name":"boardId","optional":false,"rest":false,"chained":false}],
				page: null,
				endpoint: __memo(() => import('./entries/endpoints/api/insights/posts/_boardId_/_server.ts.js'))
			},
			{
				id: "/api/insights/[...path]",
				pattern: /^\/api\/insights(?:\/([^]*))?\/?$/,
				params: [{"name":"path","optional":false,"rest":true,"chained":true}],
				page: null,
				endpoint: __memo(() => import('./entries/endpoints/api/insights/_...path_/_server.ts.js'))
			},
			{
				id: "/api/integrations",
				pattern: /^\/api\/integrations\/?$/,
				params: [],
				page: null,
				endpoint: __memo(() => import('./entries/endpoints/api/integrations/_server.ts.js'))
			},
			{
				id: "/api/integrations/focus",
				pattern: /^\/api\/integrations\/focus\/?$/,
				params: [],
				page: null,
				endpoint: __memo(() => import('./entries/endpoints/api/integrations/focus/_server.ts.js'))
			},
			{
				id: "/api/integrations/voice",
				pattern: /^\/api\/integrations\/voice\/?$/,
				params: [],
				page: null,
				endpoint: __memo(() => import('./entries/endpoints/api/integrations/voice/_server.ts.js'))
			},
			{
				id: "/api/jobs",
				pattern: /^\/api\/jobs\/?$/,
				params: [],
				page: null,
				endpoint: __memo(() => import('./entries/endpoints/api/jobs/_server.ts.js'))
			},
			{
				id: "/api/lab/alerts",
				pattern: /^\/api\/lab\/alerts\/?$/,
				params: [],
				page: null,
				endpoint: __memo(() => import('./entries/endpoints/api/lab/alerts/_server.ts.js'))
			},
			{
				id: "/api/lab/alerts/[id]/resolve",
				pattern: /^\/api\/lab\/alerts\/([^/]+?)\/resolve\/?$/,
				params: [{"name":"id","optional":false,"rest":false,"chained":false}],
				page: null,
				endpoint: __memo(() => import('./entries/endpoints/api/lab/alerts/_id_/resolve/_server.ts.js'))
			},
			{
				id: "/api/lab/customers",
				pattern: /^\/api\/lab\/customers\/?$/,
				params: [],
				page: null,
				endpoint: __memo(() => import('./entries/endpoints/api/lab/customers/_server.ts.js'))
			},
			{
				id: "/api/lab/metrics/fleet",
				pattern: /^\/api\/lab\/metrics\/fleet\/?$/,
				params: [],
				page: null,
				endpoint: __memo(() => import('./entries/endpoints/api/lab/metrics/fleet/_server.ts.js'))
			},
			{
				id: "/api/lab/vms",
				pattern: /^\/api\/lab\/vms\/?$/,
				params: [],
				page: null,
				endpoint: __memo(() => import('./entries/endpoints/api/lab/vms/_server.ts.js'))
			},
			{
				id: "/api/lab/vms/[id]/rebuild",
				pattern: /^\/api\/lab\/vms\/([^/]+?)\/rebuild\/?$/,
				params: [{"name":"id","optional":false,"rest":false,"chained":false}],
				page: null,
				endpoint: __memo(() => import('./entries/endpoints/api/lab/vms/_id_/rebuild/_server.ts.js'))
			},
			{
				id: "/api/lab/vms/[id]/restart",
				pattern: /^\/api\/lab\/vms\/([^/]+?)\/restart\/?$/,
				params: [{"name":"id","optional":false,"rest":false,"chained":false}],
				page: null,
				endpoint: __memo(() => import('./entries/endpoints/api/lab/vms/_id_/restart/_server.ts.js'))
			},
			{
				id: "/api/leaderboard",
				pattern: /^\/api\/leaderboard\/?$/,
				params: [],
				page: null,
				endpoint: __memo(() => import('./entries/endpoints/api/leaderboard/_server.ts.js'))
			},
			{
				id: "/api/learn",
				pattern: /^\/api\/learn\/?$/,
				params: [],
				page: null,
				endpoint: __memo(() => import('./entries/endpoints/api/learn/_server.ts.js'))
			},
			{
				id: "/api/memory",
				pattern: /^\/api\/memory\/?$/,
				params: [],
				page: null,
				endpoint: __memo(() => import('./entries/endpoints/api/memory/_server.ts.js'))
			},
			{
				id: "/api/memory/consolidate",
				pattern: /^\/api\/memory\/consolidate\/?$/,
				params: [],
				page: null,
				endpoint: __memo(() => import('./entries/endpoints/api/memory/consolidate/_server.ts.js'))
			},
			{
				id: "/api/pause-swarm",
				pattern: /^\/api\/pause-swarm\/?$/,
				params: [],
				page: null,
				endpoint: __memo(() => import('./entries/endpoints/api/pause-swarm/_server.ts.js'))
			},
			{
				id: "/api/pipeline-policy",
				pattern: /^\/api\/pipeline-policy\/?$/,
				params: [],
				page: null,
				endpoint: __memo(() => import('./entries/endpoints/api/pipeline-policy/_server.ts.js'))
			},
			{
				id: "/api/power-swarm",
				pattern: /^\/api\/power-swarm\/?$/,
				params: [],
				page: null,
				endpoint: __memo(() => import('./entries/endpoints/api/power-swarm/_server.ts.js'))
			},
			{
				id: "/api/reach",
				pattern: /^\/api\/reach\/?$/,
				params: [],
				page: null,
				endpoint: __memo(() => import('./entries/endpoints/api/reach/_server.ts.js'))
			},
			{
				id: "/api/reach/agents",
				pattern: /^\/api\/reach\/agents\/?$/,
				params: [],
				page: null,
				endpoint: __memo(() => import('./entries/endpoints/api/reach/agents/_server.ts.js'))
			},
			{
				id: "/api/reach/campaigns",
				pattern: /^\/api\/reach\/campaigns\/?$/,
				params: [],
				page: null,
				endpoint: __memo(() => import('./entries/endpoints/api/reach/campaigns/_server.ts.js'))
			},
			{
				id: "/api/reach/queue",
				pattern: /^\/api\/reach\/queue\/?$/,
				params: [],
				page: null,
				endpoint: __memo(() => import('./entries/endpoints/api/reach/queue/_server.ts.js'))
			},
			{
				id: "/api/reset-soft",
				pattern: /^\/api\/reset-soft\/?$/,
				params: [],
				page: null,
				endpoint: __memo(() => import('./entries/endpoints/api/reset-soft/_server.ts.js'))
			},
			{
				id: "/api/reset",
				pattern: /^\/api\/reset\/?$/,
				params: [],
				page: null,
				endpoint: __memo(() => import('./entries/endpoints/api/reset/_server.ts.js'))
			},
			{
				id: "/api/scopes",
				pattern: /^\/api\/scopes\/?$/,
				params: [],
				page: null,
				endpoint: __memo(() => import('./entries/endpoints/api/scopes/_server.ts.js'))
			},
			{
				id: "/api/spawn",
				pattern: /^\/api\/spawn\/?$/,
				params: [],
				page: null,
				endpoint: __memo(() => import('./entries/endpoints/api/spawn/_server.ts.js'))
			},
			{
				id: "/api/status",
				pattern: /^\/api\/status\/?$/,
				params: [],
				page: null,
				endpoint: __memo(() => import('./entries/endpoints/api/status/_server.ts.js'))
			},
			{
				id: "/api/traces",
				pattern: /^\/api\/traces\/?$/,
				params: [],
				page: null,
				endpoint: __memo(() => import('./entries/endpoints/api/traces/_server.ts.js'))
			},
			{
				id: "/api/voice",
				pattern: /^\/api\/voice\/?$/,
				params: [],
				page: null,
				endpoint: __memo(() => import('./entries/endpoints/api/voice/_server.ts.js'))
			},
			{
				id: "/api/voice/analytics",
				pattern: /^\/api\/voice\/analytics\/?$/,
				params: [],
				page: null,
				endpoint: __memo(() => import('./entries/endpoints/api/voice/analytics/_server.ts.js'))
			},
			{
				id: "/api/voice/campaigns",
				pattern: /^\/api\/voice\/campaigns\/?$/,
				params: [],
				page: null,
				endpoint: __memo(() => import('./entries/endpoints/api/voice/campaigns/_server.ts.js'))
			},
			{
				id: "/api/voice/health",
				pattern: /^\/api\/voice\/health\/?$/,
				params: [],
				page: null,
				endpoint: __memo(() => import('./entries/endpoints/api/voice/health/_server.ts.js'))
			},
			{
				id: "/api/voice/providers",
				pattern: /^\/api\/voice\/providers\/?$/,
				params: [],
				page: null,
				endpoint: __memo(() => import('./entries/endpoints/api/voice/providers/_server.ts.js'))
			},
			{
				id: "/api/voice/sessions",
				pattern: /^\/api\/voice\/sessions\/?$/,
				params: [],
				page: null,
				endpoint: __memo(() => import('./entries/endpoints/api/voice/sessions/_server.ts.js'))
			},
			{
				id: "/api/voice/teams",
				pattern: /^\/api\/voice\/teams\/?$/,
				params: [],
				page: null,
				endpoint: __memo(() => import('./entries/endpoints/api/voice/teams/_server.ts.js'))
			},
			{
				id: "/api/vop",
				pattern: /^\/api\/vop\/?$/,
				params: [],
				page: null,
				endpoint: __memo(() => import('./entries/endpoints/api/vop/_server.ts.js'))
			},
			{
				id: "/api/vop/conversations",
				pattern: /^\/api\/vop\/conversations\/?$/,
				params: [],
				page: null,
				endpoint: __memo(() => import('./entries/endpoints/api/vop/conversations/_server.ts.js'))
			},
			{
				id: "/api/vop/surveys",
				pattern: /^\/api\/vop\/surveys\/?$/,
				params: [],
				page: null,
				endpoint: __memo(() => import('./entries/endpoints/api/vop/surveys/_server.ts.js'))
			},
			{
				id: "/api/windmill/health",
				pattern: /^\/api\/windmill\/health\/?$/,
				params: [],
				page: null,
				endpoint: __memo(() => import('./entries/endpoints/api/windmill/health/_server.ts.js'))
			},
			{
				id: "/apple-touch-icon-precomposed.png",
				pattern: /^\/apple-touch-icon-precomposed\.png\/?$/,
				params: [],
				page: null,
				endpoint: __memo(() => import('./entries/endpoints/apple-touch-icon-precomposed.png/_server.ts.js'))
			},
			{
				id: "/apple-touch-icon.png",
				pattern: /^\/apple-touch-icon\.png\/?$/,
				params: [],
				page: null,
				endpoint: __memo(() => import('./entries/endpoints/apple-touch-icon.png/_server.ts.js'))
			},
			{
				id: "/apps",
				pattern: /^\/apps\/?$/,
				params: [],
				page: { layouts: [0,], errors: [1,], leaf: 5 },
				endpoint: null
			},
			{
				id: "/auth/callback",
				pattern: /^\/auth\/callback\/?$/,
				params: [],
				page: null,
				endpoint: __memo(() => import('./entries/endpoints/auth/callback/_server.ts.js'))
			},
			{
				id: "/auth/login",
				pattern: /^\/auth\/login\/?$/,
				params: [],
				page: { layouts: [0,], errors: [1,], leaf: 6 },
				endpoint: null
			},
			{
				id: "/auth/register",
				pattern: /^\/auth\/register\/?$/,
				params: [],
				page: { layouts: [0,], errors: [1,], leaf: 7 },
				endpoint: null
			},
			{
				id: "/auth/sso",
				pattern: /^\/auth\/sso\/?$/,
				params: [],
				page: null,
				endpoint: __memo(() => import('./entries/endpoints/auth/sso/_server.ts.js'))
			},
			{
				id: "/blackboard",
				pattern: /^\/blackboard\/?$/,
				params: [],
				page: { layouts: [0,], errors: [1,], leaf: 8 },
				endpoint: null
			},
			{
				id: "/brain",
				pattern: /^\/brain\/?$/,
				params: [],
				page: { layouts: [0,], errors: [1,], leaf: 9 },
				endpoint: null
			},
			{
				id: "/comms",
				pattern: /^\/comms\/?$/,
				params: [],
				page: { layouts: [0,], errors: [1,], leaf: 10 },
				endpoint: null
			},
			{
				id: "/costs",
				pattern: /^\/costs\/?$/,
				params: [],
				page: { layouts: [0,], errors: [1,], leaf: 11 },
				endpoint: null
			},
			{
				id: "/crm",
				pattern: /^\/crm\/?$/,
				params: [],
				page: { layouts: [0,], errors: [1,], leaf: 12 },
				endpoint: null
			},
			{
				id: "/data",
				pattern: /^\/data\/?$/,
				params: [],
				page: { layouts: [0,], errors: [1,], leaf: 13 },
				endpoint: null
			},
			{
				id: "/favicon.ico",
				pattern: /^\/favicon\.ico\/?$/,
				params: [],
				page: null,
				endpoint: __memo(() => import('./entries/endpoints/favicon.ico/_server.ts.js'))
			},
			{
				id: "/genomes",
				pattern: /^\/genomes\/?$/,
				params: [],
				page: { layouts: [0,], errors: [1,], leaf: 14 },
				endpoint: null
			},
			{
				id: "/health",
				pattern: /^\/health\/?$/,
				params: [],
				page: { layouts: [0,], errors: [1,], leaf: 15 },
				endpoint: __memo(() => import('./entries/endpoints/health/_server.ts.js'))
			},
			{
				id: "/insights",
				pattern: /^\/insights\/?$/,
				params: [],
				page: { layouts: [0,], errors: [1,], leaf: 16 },
				endpoint: null
			},
			{
				id: "/jobs",
				pattern: /^\/jobs\/?$/,
				params: [],
				page: { layouts: [0,], errors: [1,], leaf: 17 },
				endpoint: null
			},
			{
				id: "/lab",
				pattern: /^\/lab\/?$/,
				params: [],
				page: { layouts: [0,], errors: [1,], leaf: 18 },
				endpoint: null
			},
			{
				id: "/leaderboard",
				pattern: /^\/leaderboard\/?$/,
				params: [],
				page: { layouts: [0,], errors: [1,], leaf: 19 },
				endpoint: null
			},
			{
				id: "/learn",
				pattern: /^\/learn\/?$/,
				params: [],
				page: { layouts: [0,], errors: [1,], leaf: 20 },
				endpoint: null
			},
			{
				id: "/linear",
				pattern: /^\/linear\/?$/,
				params: [],
				page: { layouts: [0,], errors: [1,], leaf: 21 },
				endpoint: null
			},
			{
				id: "/memory",
				pattern: /^\/memory\/?$/,
				params: [],
				page: { layouts: [0,], errors: [1,], leaf: 22 },
				endpoint: null
			},
			{
				id: "/notebook",
				pattern: /^\/notebook\/?$/,
				params: [],
				page: { layouts: [0,], errors: [1,], leaf: 23 },
				endpoint: null
			},
			{
				id: "/reach",
				pattern: /^\/reach\/?$/,
				params: [],
				page: { layouts: [0,], errors: [1,], leaf: 24 },
				endpoint: null
			},
			{
				id: "/recall",
				pattern: /^\/recall\/?$/,
				params: [],
				page: { layouts: [0,], errors: [1,], leaf: 25 },
				endpoint: null
			},
			{
				id: "/see",
				pattern: /^\/see\/?$/,
				params: [],
				page: { layouts: [0,], errors: [1,], leaf: 26 },
				endpoint: null
			},
			{
				id: "/see/traces",
				pattern: /^\/see\/traces\/?$/,
				params: [],
				page: { layouts: [0,], errors: [1,], leaf: 27 },
				endpoint: null
			},
			{
				id: "/settings",
				pattern: /^\/settings\/?$/,
				params: [],
				page: { layouts: [0,], errors: [1,], leaf: 28 },
				endpoint: null
			},
			{
				id: "/terminal",
				pattern: /^\/terminal\/?$/,
				params: [],
				page: { layouts: [0,], errors: [1,], leaf: 29 },
				endpoint: null
			},
			{
				id: "/workflows",
				pattern: /^\/workflows\/?$/,
				params: [],
				page: { layouts: [0,], errors: [1,], leaf: 30 },
				endpoint: null
			}
		],
		prerendered_routes: new Set([]),
		matchers: async () => {
			
			return {  };
		},
		server_assets: {}
	}
}
})();
