
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
		RouteId(): "/" | "/ai-readiness" | "/courses" | "/courses/[slug]" | "/{courses" | "/{courses/\"[slug]\"}";
		RouteParams(): {
			"/courses/[slug]": { slug: string };
			"/{courses/\"[slug]\"}": { slug: string }
		};
		LayoutParams(): {
			"/": { slug?: string };
			"/ai-readiness": Record<string, never>;
			"/courses": { slug?: string };
			"/courses/[slug]": { slug: string };
			"/{courses": { slug?: string };
			"/{courses/\"[slug]\"}": { slug: string }
		};
		Pathname(): "/" | "/ai-readiness" | "/ai-readiness/" | "/courses" | "/courses/" | `/courses/${string}` & {} | `/courses/${string}/` & {} | "/{courses" | "/{courses/" | `/{courses/"[slug]"}` & {} | `/{courses/"[slug]"}/` & {};
		ResolvedPathname(): `${"" | `/${string}`}${ReturnType<AppTypes['Pathname']>}`;
		Asset(): "/favicon.png" | string & {};
	}
}