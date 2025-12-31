

export const index = 0;
let component_cache;
export const component = async () => component_cache ??= (await import('../entries/pages/_layout.svelte.js')).default;
export const imports = ["_app/immutable/nodes/0.C0fleZE4.js","_app/immutable/chunks/B3cyiPE4.js","_app/immutable/chunks/cNlArlAb.js","_app/immutable/chunks/DeC8RXLS.js"];
export const stylesheets = ["_app/immutable/assets/0.BB_P2DnK.css"];
export const fonts = [];
