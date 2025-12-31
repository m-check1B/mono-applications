
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
		RouteId(): "/" | "/capture" | "/graph" | "/item" | "/item/[category]" | "/item/[category]/[id]" | "/recent";
		RouteParams(): {
			"/item/[category]": { category: string };
			"/item/[category]/[id]": { category: string; id: string }
		};
		LayoutParams(): {
			"/": { category?: string; id?: string };
			"/capture": Record<string, never>;
			"/graph": Record<string, never>;
			"/item": { category?: string; id?: string };
			"/item/[category]": { category: string; id?: string };
			"/item/[category]/[id]": { category: string; id: string };
			"/recent": Record<string, never>
		};
		Pathname(): "/" | "/capture" | "/capture/" | "/graph" | "/graph/" | "/item" | "/item/" | `/item/${string}` & {} | `/item/${string}/` & {} | `/item/${string}/${string}` & {} | `/item/${string}/${string}/` & {} | "/recent" | "/recent/";
		ResolvedPathname(): `${"" | `/${string}`}${ReturnType<AppTypes['Pathname']>}`;
		Asset(): string & {};
	}
}