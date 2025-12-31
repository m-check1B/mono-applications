import * as server from '../entries/pages/agent-board/_page.server.ts.js';

export const index = 3;
let component_cache;
export const component = async () => component_cache ??= (await import('../entries/pages/agent-board/_page.svelte.js')).default;
export { server };
export const server_id = "src/routes/agent-board/+page.server.ts";
export const imports = ["_app/immutable/nodes/3.DRJgvg5D.js","_app/immutable/chunks/CZY_NlAX.js","_app/immutable/chunks/CHIrzwsT.js","_app/immutable/chunks/D1Luo-Nw.js"];
export const stylesheets = [];
export const fonts = [];
