import * as server from '../entries/pages/_page.server.ts.js';

export const index = 3;
let component_cache;
export const component = async () => component_cache ??= (await import('../entries/pages/_page.svelte.js')).default;
export { server };
export const server_id = "src/routes/+page.server.ts";
export const imports = ["_app/immutable/nodes/3.BvVFK9jn.js","_app/immutable/chunks/pejWV2dy.js","_app/immutable/chunks/DgM1AnfY.js","_app/immutable/chunks/CQ2dU6u5.js","_app/immutable/chunks/CUTbOrLX.js","_app/immutable/chunks/D9mD-Og7.js","_app/immutable/chunks/CABBFY_M.js","_app/immutable/chunks/D1iePAOD.js","_app/immutable/chunks/CBf0kXIe.js"];
export const stylesheets = [];
export const fonts = [];
