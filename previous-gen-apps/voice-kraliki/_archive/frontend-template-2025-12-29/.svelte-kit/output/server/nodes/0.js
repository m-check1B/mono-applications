import * as universal from '../entries/pages/_layout.ts.js';

export const index = 0;
let component_cache;
export const component = async () => component_cache ??= (await import('../entries/pages/_layout.svelte.js')).default;
export { universal };
export const universal_id = "src/routes/+layout.ts";
export const imports = ["_app/immutable/nodes/0.Ch_cRiJP.js","_app/immutable/chunks/J6IVVljB.js","_app/immutable/chunks/B4dMqloI.js","_app/immutable/chunks/aQ_ifger.js","_app/immutable/chunks/pFl1CK35.js","_app/immutable/chunks/0VtO9hYy.js","_app/immutable/chunks/D2QsL1jb.js","_app/immutable/chunks/BMKFQ0yK.js","_app/immutable/chunks/Bu_bTSTr.js","_app/immutable/chunks/9yISC1dT.js","_app/immutable/chunks/XctAiTdr.js","_app/immutable/chunks/C918u5xm.js","_app/immutable/chunks/BTxJJ6eU.js","_app/immutable/chunks/ahVOO_2e.js","_app/immutable/chunks/CTjsJUPt.js","_app/immutable/chunks/CYgJF_JY.js","_app/immutable/chunks/DLb8tBY9.js","_app/immutable/chunks/8UtF8RsF.js","_app/immutable/chunks/CnJ-dsFT.js","_app/immutable/chunks/DaxPoLM8.js","_app/immutable/chunks/ft9JqUN4.js","_app/immutable/chunks/DzqNI6-e.js","_app/immutable/chunks/BPSUqZ7R.js","_app/immutable/chunks/DOOofxWo.js"];
export const stylesheets = ["_app/immutable/assets/0.DOebGi_g.css"];
export const fonts = [];
