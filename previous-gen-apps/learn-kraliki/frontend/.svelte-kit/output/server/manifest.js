export const manifest = (() => {
function __memo(fn) {
	let value;
	return () => value ??= (value = fn());
}

return {
	appDir: "_app",
	appPath: "_app",
	assets: new Set(["favicon.png"]),
	mimeTypes: {".png":"image/png"},
	_: {
		client: {start:"_app/immutable/entry/start.DPr82eOG.js",app:"_app/immutable/entry/app.XAkfZYRZ.js",imports:["_app/immutable/entry/start.DPr82eOG.js","_app/immutable/chunks/CpevPvZf.js","_app/immutable/chunks/cNlArlAb.js","_app/immutable/chunks/YXzn0DR7.js","_app/immutable/chunks/BfxBEUs2.js","_app/immutable/entry/app.XAkfZYRZ.js","_app/immutable/chunks/cNlArlAb.js","_app/immutable/chunks/C245tV3e.js","_app/immutable/chunks/B3cyiPE4.js","_app/immutable/chunks/BfxBEUs2.js","_app/immutable/chunks/BIALqde0.js","_app/immutable/chunks/DeC8RXLS.js","_app/immutable/chunks/3iMayhyq.js","_app/immutable/chunks/C9fS2if3.js","_app/immutable/chunks/YXzn0DR7.js"],stylesheets:[],fonts:[],uses_env_dynamic_public:false},
		nodes: [
			__memo(() => import('./nodes/0.js')),
			__memo(() => import('./nodes/1.js')),
			__memo(() => import('./nodes/2.js')),
			__memo(() => import('./nodes/3.js')),
			__memo(() => import('./nodes/4.js'))
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
				id: "/ai-readiness",
				pattern: /^\/ai-readiness\/?$/,
				params: [],
				page: { layouts: [0,], errors: [1,], leaf: 3 },
				endpoint: null
			},
			{
				id: "/courses/[slug]",
				pattern: /^\/courses\/([^/]+?)\/?$/,
				params: [{"name":"slug","optional":false,"rest":false,"chained":false}],
				page: { layouts: [0,], errors: [1,], leaf: 4 },
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
