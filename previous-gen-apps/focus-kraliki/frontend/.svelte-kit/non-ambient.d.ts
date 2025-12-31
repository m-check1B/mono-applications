
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
		RouteId(): "/" | "/auth" | "/auth/google" | "/auth/google/callback" | "/auth/sso" | "/auth/sso/callback" | "/dashboard" | "/dashboard/agent" | "/dashboard/analytics" | "/dashboard/calendar" | "/dashboard/chat" | "/dashboard/insights" | "/dashboard/knowledge" | "/dashboard/projects" | "/dashboard/settings" | "/dashboard/shadow" | "/dashboard/subscription" | "/dashboard/tasks" | "/dashboard/team" | "/dashboard/time" | "/dashboard/voice" | "/dashboard/work" | "/login" | "/onboarding" | "/register";
		RouteParams(): {
			
		};
		LayoutParams(): {
			"/": Record<string, never>;
			"/auth": Record<string, never>;
			"/auth/google": Record<string, never>;
			"/auth/google/callback": Record<string, never>;
			"/auth/sso": Record<string, never>;
			"/auth/sso/callback": Record<string, never>;
			"/dashboard": Record<string, never>;
			"/dashboard/agent": Record<string, never>;
			"/dashboard/analytics": Record<string, never>;
			"/dashboard/calendar": Record<string, never>;
			"/dashboard/chat": Record<string, never>;
			"/dashboard/insights": Record<string, never>;
			"/dashboard/knowledge": Record<string, never>;
			"/dashboard/projects": Record<string, never>;
			"/dashboard/settings": Record<string, never>;
			"/dashboard/shadow": Record<string, never>;
			"/dashboard/subscription": Record<string, never>;
			"/dashboard/tasks": Record<string, never>;
			"/dashboard/team": Record<string, never>;
			"/dashboard/time": Record<string, never>;
			"/dashboard/voice": Record<string, never>;
			"/dashboard/work": Record<string, never>;
			"/login": Record<string, never>;
			"/onboarding": Record<string, never>;
			"/register": Record<string, never>
		};
		Pathname(): "/" | "/auth" | "/auth/" | "/auth/google" | "/auth/google/" | "/auth/google/callback" | "/auth/google/callback/" | "/auth/sso" | "/auth/sso/" | "/auth/sso/callback" | "/auth/sso/callback/" | "/dashboard" | "/dashboard/" | "/dashboard/agent" | "/dashboard/agent/" | "/dashboard/analytics" | "/dashboard/analytics/" | "/dashboard/calendar" | "/dashboard/calendar/" | "/dashboard/chat" | "/dashboard/chat/" | "/dashboard/insights" | "/dashboard/insights/" | "/dashboard/knowledge" | "/dashboard/knowledge/" | "/dashboard/projects" | "/dashboard/projects/" | "/dashboard/settings" | "/dashboard/settings/" | "/dashboard/shadow" | "/dashboard/shadow/" | "/dashboard/subscription" | "/dashboard/subscription/" | "/dashboard/tasks" | "/dashboard/tasks/" | "/dashboard/team" | "/dashboard/team/" | "/dashboard/time" | "/dashboard/time/" | "/dashboard/voice" | "/dashboard/voice/" | "/dashboard/work" | "/dashboard/work/" | "/login" | "/login/" | "/onboarding" | "/onboarding/" | "/register" | "/register/";
		ResolvedPathname(): `${"" | `/${string}`}${ReturnType<AppTypes['Pathname']>}`;
		Asset(): "/icon-144.svg" | "/icon-384.svg" | "/icon-512.svg" | "/icon-128.svg" | "/icon-96.svg" | "/manifest.json" | "/icon-192.svg" | "/icon-72.svg" | "/favicon.svg" | "/service-worker.js" | "/icon-152.svg" | string & {};
	}
}