

export const index = 3;
let component_cache;
export const component = async () => component_cache ??= (await import('../entries/pages/(auth)/_layout.svelte.js')).default;
export const imports = ["_app/immutable/nodes/3.C75c5C66.js","_app/immutable/chunks/DsnmJJEf.js","_app/immutable/chunks/BuVZNLKp.js"];
export const stylesheets = [];
export const fonts = [];
