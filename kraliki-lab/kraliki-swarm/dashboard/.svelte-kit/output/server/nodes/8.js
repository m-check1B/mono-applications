import * as server from '../entries/pages/blackboard/_page.server.ts.js';

export const index = 8;
let component_cache;
export const component = async () => component_cache ??= (await import('../entries/pages/blackboard/_page.svelte.js')).default;
export { server };
export const server_id = "src/routes/blackboard/+page.server.ts";
export const imports = ["_app/immutable/nodes/8.CKezq8AC.js","_app/immutable/chunks/CZY_NlAX.js","_app/immutable/chunks/CHIrzwsT.js","_app/immutable/chunks/D1Luo-Nw.js"];
export const stylesheets = [];
export const fonts = [];
