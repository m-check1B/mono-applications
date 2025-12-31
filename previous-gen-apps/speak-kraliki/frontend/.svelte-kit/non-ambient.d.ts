
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
		RouteId(): "/" | "/auth" | "/auth/sso" | "/auth/sso/callback" | "/dashboard" | "/dashboard/actions" | "/dashboard/alerts" | "/dashboard/employees" | "/dashboard/settings" | "/dashboard/surveys" | "/login" | "/register" | "/v" | "/v/[token]" | "/v/[token]/transcript";
		RouteParams(): {
			"/v/[token]": { token: string };
			"/v/[token]/transcript": { token: string }
		};
		LayoutParams(): {
			"/": { token?: string };
			"/auth": Record<string, never>;
			"/auth/sso": Record<string, never>;
			"/auth/sso/callback": Record<string, never>;
			"/dashboard": Record<string, never>;
			"/dashboard/actions": Record<string, never>;
			"/dashboard/alerts": Record<string, never>;
			"/dashboard/employees": Record<string, never>;
			"/dashboard/settings": Record<string, never>;
			"/dashboard/surveys": Record<string, never>;
			"/login": Record<string, never>;
			"/register": Record<string, never>;
			"/v": { token?: string };
			"/v/[token]": { token: string };
			"/v/[token]/transcript": { token: string }
		};
		Pathname(): "/" | "/auth" | "/auth/" | "/auth/sso" | "/auth/sso/" | "/auth/sso/callback" | "/auth/sso/callback/" | "/dashboard" | "/dashboard/" | "/dashboard/actions" | "/dashboard/actions/" | "/dashboard/alerts" | "/dashboard/alerts/" | "/dashboard/employees" | "/dashboard/employees/" | "/dashboard/settings" | "/dashboard/settings/" | "/dashboard/surveys" | "/dashboard/surveys/" | "/login" | "/login/" | "/register" | "/register/" | "/v" | "/v/" | `/v/${string}` & {} | `/v/${string}/` & {} | `/v/${string}/transcript` & {} | `/v/${string}/transcript/` & {};
		ResolvedPathname(): `${"" | `/${string}`}${ReturnType<AppTypes['Pathname']>}`;
		Asset(): string & {};
	}
}