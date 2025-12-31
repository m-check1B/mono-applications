import * as universal from '../entries/pages/_layout.ts.js';

export const index = 0;
let component_cache;
export const component = async () => component_cache ??= (await import('../entries/pages/_layout.svelte.js')).default;
export { universal };
export const universal_id = "src/routes/+layout.ts";
export const imports = ["_app/immutable/nodes/0.DKQVVvFT.js","_app/immutable/chunks/CABBFY_M.js","_app/immutable/chunks/DgM1AnfY.js","_app/immutable/chunks/pejWV2dy.js","_app/immutable/chunks/pi1oX53H.js","_app/immutable/chunks/B5hbs7lp.js","_app/immutable/chunks/B9v-mvxn.js","_app/immutable/chunks/CBf0kXIe.js","_app/immutable/chunks/RjzcECkQ.js","_app/immutable/chunks/CQ2dU6u5.js","_app/immutable/chunks/DGcJkfPx.js","_app/immutable/chunks/CUTbOrLX.js","_app/immutable/chunks/BQCnAYr2.js","_app/immutable/chunks/Bl8ZdI5p.js","_app/immutable/chunks/D1iePAOD.js","_app/immutable/chunks/Ctee16U3.js","_app/immutable/chunks/DOSPKQyx.js","_app/immutable/chunks/D9mD-Og7.js","_app/immutable/chunks/BC-kAh8h.js"];
export const stylesheets = ["_app/immutable/assets/0.DyDCCoLw.css"];
export const fonts = [];
