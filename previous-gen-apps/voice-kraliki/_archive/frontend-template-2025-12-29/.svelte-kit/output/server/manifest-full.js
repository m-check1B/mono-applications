export const manifest = (() => {
function __memo(fn) {
	let value;
	return () => value ??= (value = fn());
}

return {
	appDir: "_app",
	appPath: "_app",
	assets: new Set(["favicon.svg","robots.txt","worklets/audio-processor.js"]),
	mimeTypes: {".svg":"image/svg+xml",".txt":"text/plain",".js":"text/javascript"},
	_: {
		client: {start:"_app/immutable/entry/start.l7x-Vnk7.js",app:"_app/immutable/entry/app.68uBeUI-.js",imports:["_app/immutable/entry/start.l7x-Vnk7.js","_app/immutable/chunks/CTjsJUPt.js","_app/immutable/chunks/aQ_ifger.js","_app/immutable/chunks/B4dMqloI.js","_app/immutable/chunks/CYgJF_JY.js","_app/immutable/chunks/DLb8tBY9.js","_app/immutable/chunks/8UtF8RsF.js","_app/immutable/chunks/0VtO9hYy.js","_app/immutable/entry/app.68uBeUI-.js","_app/immutable/chunks/PPVm8Dsz.js","_app/immutable/chunks/aQ_ifger.js","_app/immutable/chunks/DBuqHHqM.js","_app/immutable/chunks/C918u5xm.js","_app/immutable/chunks/pFl1CK35.js","_app/immutable/chunks/0VtO9hYy.js","_app/immutable/chunks/BTxJJ6eU.js","_app/immutable/chunks/BMKFQ0yK.js","_app/immutable/chunks/CEkw2kT7.js","_app/immutable/chunks/Bo6fAwy7.js","_app/immutable/chunks/DzqNI6-e.js","_app/immutable/chunks/BPSUqZ7R.js","_app/immutable/chunks/B4dMqloI.js"],stylesheets:[],fonts:[],uses_env_dynamic_public:true},
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
			__memo(() => import('./nodes/30.js')),
			__memo(() => import('./nodes/31.js')),
			__memo(() => import('./nodes/32.js')),
			__memo(() => import('./nodes/33.js')),
			__memo(() => import('./nodes/34.js')),
			__memo(() => import('./nodes/35.js')),
			__memo(() => import('./nodes/36.js')),
			__memo(() => import('./nodes/37.js')),
			__memo(() => import('./nodes/38.js'))
		],
		remotes: {
			
		},
		routes: [
			{
				id: "/",
				pattern: /^\/$/,
				params: [],
				page: { layouts: [0,], errors: [1,], leaf: 3 },
				endpoint: null
			},
			{
				id: "/about",
				pattern: /^\/about\/?$/,
				params: [],
				page: { layouts: [0,], errors: [1,], leaf: 17 },
				endpoint: null
			},
			{
				id: "/agents",
				pattern: /^\/agents\/?$/,
				params: [],
				page: { layouts: [0,], errors: [1,], leaf: 18 },
				endpoint: null
			},
			{
				id: "/agents/[id]",
				pattern: /^\/agents\/([^/]+?)\/?$/,
				params: [{"name":"id","optional":false,"rest":false,"chained":false}],
				page: { layouts: [0,], errors: [1,], leaf: 19 },
				endpoint: null
			},
			{
				id: "/(protected)/analytics",
				pattern: /^\/analytics\/?$/,
				params: [],
				page: { layouts: [0,2,], errors: [1,,], leaf: 4 },
				endpoint: null
			},
			{
				id: "/(protected)/arena",
				pattern: /^\/arena\/?$/,
				params: [],
				page: { layouts: [0,2,], errors: [1,,], leaf: 5 },
				endpoint: null
			},
			{
				id: "/auth/login",
				pattern: /^\/auth\/login\/?$/,
				params: [],
				page: { layouts: [0,], errors: [1,], leaf: 20 },
				endpoint: null
			},
			{
				id: "/auth/register",
				pattern: /^\/auth\/register\/?$/,
				params: [],
				page: { layouts: [0,], errors: [1,], leaf: 21 },
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
				id: "/auth/sso/callback",
				pattern: /^\/auth\/sso\/callback\/?$/,
				params: [],
				page: null,
				endpoint: __memo(() => import('./entries/endpoints/auth/sso/callback/_server.ts.js'))
			},
			{
				id: "/(protected)/calls/agent",
				pattern: /^\/calls\/agent\/?$/,
				params: [],
				page: { layouts: [0,2,], errors: [1,,], leaf: 6 },
				endpoint: null
			},
			{
				id: "/(protected)/calls/incoming",
				pattern: /^\/calls\/incoming\/?$/,
				params: [],
				page: { layouts: [0,2,], errors: [1,,], leaf: 7 },
				endpoint: null
			},
			{
				id: "/(protected)/calls/outbound",
				pattern: /^\/calls\/outbound\/?$/,
				params: [],
				page: { layouts: [0,2,], errors: [1,,], leaf: 8 },
				endpoint: null
			},
			{
				id: "/(protected)/campaigns",
				pattern: /^\/campaigns\/?$/,
				params: [],
				page: { layouts: [0,2,], errors: [1,,], leaf: 9 },
				endpoint: null
			},
			{
				id: "/(protected)/chat",
				pattern: /^\/chat\/?$/,
				params: [],
				page: { layouts: [0,2,], errors: [1,,], leaf: 10 },
				endpoint: null
			},
			{
				id: "/(protected)/companies",
				pattern: /^\/companies\/?$/,
				params: [],
				page: { layouts: [0,2,], errors: [1,,], leaf: 11 },
				endpoint: null
			},
			{
				id: "/contact-lists/[id]",
				pattern: /^\/contact-lists\/([^/]+?)\/?$/,
				params: [{"name":"id","optional":false,"rest":false,"chained":false}],
				page: { layouts: [0,], errors: [1,], leaf: 22 },
				endpoint: null
			},
			{
				id: "/cross-tab-demo",
				pattern: /^\/cross-tab-demo\/?$/,
				params: [],
				page: { layouts: [0,], errors: [1,], leaf: 23 },
				endpoint: null
			},
			{
				id: "/(protected)/dashboard",
				pattern: /^\/dashboard\/?$/,
				params: [],
				page: { layouts: [0,2,], errors: [1,,], leaf: 12 },
				endpoint: null
			},
			{
				id: "/operations/ivr",
				pattern: /^\/operations\/ivr\/?$/,
				params: [],
				page: { layouts: [0,], errors: [1,], leaf: 24 },
				endpoint: null
			},
			{
				id: "/operations/ivr/builder",
				pattern: /^\/operations\/ivr\/builder\/?$/,
				params: [],
				page: { layouts: [0,], errors: [1,], leaf: 25 },
				endpoint: null
			},
			{
				id: "/operations/recordings",
				pattern: /^\/operations\/recordings\/?$/,
				params: [],
				page: { layouts: [0,], errors: [1,], leaf: 26 },
				endpoint: null
			},
			{
				id: "/operations/routing",
				pattern: /^\/operations\/routing\/?$/,
				params: [],
				page: { layouts: [0,], errors: [1,], leaf: 27 },
				endpoint: null
			},
			{
				id: "/operations/routing/builder",
				pattern: /^\/operations\/routing\/builder\/?$/,
				params: [],
				page: { layouts: [0,], errors: [1,], leaf: 28 },
				endpoint: null
			},
			{
				id: "/operations/voicemail",
				pattern: /^\/operations\/voicemail\/?$/,
				params: [],
				page: { layouts: [0,], errors: [1,], leaf: 29 },
				endpoint: null
			},
			{
				id: "/privacy",
				pattern: /^\/privacy\/?$/,
				params: [],
				page: { layouts: [0,], errors: [1,], leaf: 30 },
				endpoint: null
			},
			{
				id: "/responsive-test",
				pattern: /^\/responsive-test\/?$/,
				params: [],
				page: { layouts: [0,], errors: [1,], leaf: 31 },
				endpoint: null
			},
			{
				id: "/(protected)/scenarios",
				pattern: /^\/scenarios\/?$/,
				params: [],
				page: { layouts: [0,2,], errors: [1,,], leaf: 13 },
				endpoint: null
			},
			{
				id: "/(protected)/scenarios/builder",
				pattern: /^\/scenarios\/builder\/?$/,
				params: [],
				page: { layouts: [0,2,], errors: [1,,], leaf: 14 },
				endpoint: null
			},
			{
				id: "/(protected)/scenarios/practice",
				pattern: /^\/scenarios\/practice\/?$/,
				params: [],
				page: { layouts: [0,2,], errors: [1,,], leaf: 15 },
				endpoint: null
			},
			{
				id: "/(protected)/settings",
				pattern: /^\/settings\/?$/,
				params: [],
				page: { layouts: [0,2,], errors: [1,,], leaf: 16 },
				endpoint: null
			},
			{
				id: "/shifts",
				pattern: /^\/shifts\/?$/,
				params: [],
				page: { layouts: [0,], errors: [1,], leaf: 32 },
				endpoint: null
			},
			{
				id: "/supervisor/active-calls",
				pattern: /^\/supervisor\/active-calls\/?$/,
				params: [],
				page: { layouts: [0,], errors: [1,], leaf: 33 },
				endpoint: null
			},
			{
				id: "/supervisor/dashboard",
				pattern: /^\/supervisor\/dashboard\/?$/,
				params: [],
				page: { layouts: [0,], errors: [1,], leaf: 34 },
				endpoint: null
			},
			{
				id: "/supervisor/queue",
				pattern: /^\/supervisor\/queue\/?$/,
				params: [],
				page: { layouts: [0,], errors: [1,], leaf: 35 },
				endpoint: null
			},
			{
				id: "/teams",
				pattern: /^\/teams\/?$/,
				params: [],
				page: { layouts: [0,], errors: [1,], leaf: 36 },
				endpoint: null
			},
			{
				id: "/teams/new",
				pattern: /^\/teams\/new\/?$/,
				params: [],
				page: { layouts: [0,], errors: [1,], leaf: 38 },
				endpoint: null
			},
			{
				id: "/teams/[id]",
				pattern: /^\/teams\/([^/]+?)\/?$/,
				params: [{"name":"id","optional":false,"rest":false,"chained":false}],
				page: { layouts: [0,], errors: [1,], leaf: 37 },
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
