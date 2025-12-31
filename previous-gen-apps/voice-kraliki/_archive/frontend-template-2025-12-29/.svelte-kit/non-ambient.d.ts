
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
		RouteId(): "/(protected)" | "/" | "/about" | "/agents" | "/agents/[id]" | "/(protected)/analytics" | "/(protected)/arena" | "/auth" | "/auth/login" | "/auth/register" | "/auth/sso" | "/auth/sso/callback" | "/(protected)/calls" | "/(protected)/calls/agent" | "/(protected)/calls/incoming" | "/(protected)/calls/outbound" | "/(protected)/campaigns" | "/(protected)/chat" | "/(protected)/companies" | "/contact-lists" | "/contact-lists/[id]" | "/cross-tab-demo" | "/(protected)/dashboard" | "/operations" | "/operations/ivr" | "/operations/ivr/builder" | "/operations/recordings" | "/operations/routing" | "/operations/routing/builder" | "/operations/voicemail" | "/privacy" | "/responsive-test" | "/(protected)/scenarios" | "/(protected)/scenarios/builder" | "/(protected)/scenarios/practice" | "/(protected)/settings" | "/shifts" | "/supervisor" | "/supervisor/active-calls" | "/supervisor/dashboard" | "/supervisor/queue" | "/teams" | "/teams/new" | "/teams/[id]";
		RouteParams(): {
			"/agents/[id]": { id: string };
			"/contact-lists/[id]": { id: string };
			"/teams/[id]": { id: string }
		};
		LayoutParams(): {
			"/(protected)": Record<string, never>;
			"/": { id?: string };
			"/about": Record<string, never>;
			"/agents": { id?: string };
			"/agents/[id]": { id: string };
			"/(protected)/analytics": Record<string, never>;
			"/(protected)/arena": Record<string, never>;
			"/auth": Record<string, never>;
			"/auth/login": Record<string, never>;
			"/auth/register": Record<string, never>;
			"/auth/sso": Record<string, never>;
			"/auth/sso/callback": Record<string, never>;
			"/(protected)/calls": Record<string, never>;
			"/(protected)/calls/agent": Record<string, never>;
			"/(protected)/calls/incoming": Record<string, never>;
			"/(protected)/calls/outbound": Record<string, never>;
			"/(protected)/campaigns": Record<string, never>;
			"/(protected)/chat": Record<string, never>;
			"/(protected)/companies": Record<string, never>;
			"/contact-lists": { id?: string };
			"/contact-lists/[id]": { id: string };
			"/cross-tab-demo": Record<string, never>;
			"/(protected)/dashboard": Record<string, never>;
			"/operations": Record<string, never>;
			"/operations/ivr": Record<string, never>;
			"/operations/ivr/builder": Record<string, never>;
			"/operations/recordings": Record<string, never>;
			"/operations/routing": Record<string, never>;
			"/operations/routing/builder": Record<string, never>;
			"/operations/voicemail": Record<string, never>;
			"/privacy": Record<string, never>;
			"/responsive-test": Record<string, never>;
			"/(protected)/scenarios": Record<string, never>;
			"/(protected)/scenarios/builder": Record<string, never>;
			"/(protected)/scenarios/practice": Record<string, never>;
			"/(protected)/settings": Record<string, never>;
			"/shifts": Record<string, never>;
			"/supervisor": Record<string, never>;
			"/supervisor/active-calls": Record<string, never>;
			"/supervisor/dashboard": Record<string, never>;
			"/supervisor/queue": Record<string, never>;
			"/teams": { id?: string };
			"/teams/new": Record<string, never>;
			"/teams/[id]": { id: string }
		};
		Pathname(): "/" | "/about" | "/about/" | "/agents" | "/agents/" | `/agents/${string}` & {} | `/agents/${string}/` & {} | "/analytics" | "/analytics/" | "/arena" | "/arena/" | "/auth" | "/auth/" | "/auth/login" | "/auth/login/" | "/auth/register" | "/auth/register/" | "/auth/sso" | "/auth/sso/" | "/auth/sso/callback" | "/auth/sso/callback/" | "/calls" | "/calls/" | "/calls/agent" | "/calls/agent/" | "/calls/incoming" | "/calls/incoming/" | "/calls/outbound" | "/calls/outbound/" | "/campaigns" | "/campaigns/" | "/chat" | "/chat/" | "/companies" | "/companies/" | "/contact-lists" | "/contact-lists/" | `/contact-lists/${string}` & {} | `/contact-lists/${string}/` & {} | "/cross-tab-demo" | "/cross-tab-demo/" | "/dashboard" | "/dashboard/" | "/operations" | "/operations/" | "/operations/ivr" | "/operations/ivr/" | "/operations/ivr/builder" | "/operations/ivr/builder/" | "/operations/recordings" | "/operations/recordings/" | "/operations/routing" | "/operations/routing/" | "/operations/routing/builder" | "/operations/routing/builder/" | "/operations/voicemail" | "/operations/voicemail/" | "/privacy" | "/privacy/" | "/responsive-test" | "/responsive-test/" | "/scenarios" | "/scenarios/" | "/scenarios/builder" | "/scenarios/builder/" | "/scenarios/practice" | "/scenarios/practice/" | "/settings" | "/settings/" | "/shifts" | "/shifts/" | "/supervisor" | "/supervisor/" | "/supervisor/active-calls" | "/supervisor/active-calls/" | "/supervisor/dashboard" | "/supervisor/dashboard/" | "/supervisor/queue" | "/supervisor/queue/" | "/teams" | "/teams/" | "/teams/new" | "/teams/new/" | `/teams/${string}` & {} | `/teams/${string}/` & {};
		ResolvedPathname(): `${"" | `/${string}`}${ReturnType<AppTypes['Pathname']>}`;
		Asset(): "/favicon.svg" | "/robots.txt" | "/worklets/audio-processor.js" | string & {};
	}
}