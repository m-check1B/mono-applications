import { json } from "@sveltejs/kit";
const GET = async () => {
  return json({ status: "ok", timestamp: (/* @__PURE__ */ new Date()).toISOString() });
};
export {
  GET
};
