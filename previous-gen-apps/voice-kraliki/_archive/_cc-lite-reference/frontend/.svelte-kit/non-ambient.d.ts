
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
		RouteId(): "/(auth)" | "/(app)" | "/" | "/(app)/admin" | "/(app)/admin/campaigns" | "/(app)/admin/users" | "/(auth)/login" | "/(app)/operator" | "/(app)/supervisor" | "/test";
		RouteParams(): {
			
		};
		LayoutParams(): {
			"/(auth)": Record<string, never>;
			"/(app)": Record<string, never>;
			"/": Record<string, never>;
			"/(app)/admin": Record<string, never>;
			"/(app)/admin/campaigns": Record<string, never>;
			"/(app)/admin/users": Record<string, never>;
			"/(auth)/login": Record<string, never>;
			"/(app)/operator": Record<string, never>;
			"/(app)/supervisor": Record<string, never>;
			"/test": Record<string, never>
		};
		Pathname(): "/" | "/admin" | "/admin/" | "/admin/campaigns" | "/admin/campaigns/" | "/admin/users" | "/admin/users/" | "/login" | "/login/" | "/operator" | "/operator/" | "/supervisor" | "/supervisor/" | "/test" | "/test/";
		ResolvedPathname(): `${"" | `/${string}`}${ReturnType<AppTypes['Pathname']>}`;
		Asset(): "/robots.txt" | string & {};
	}
}