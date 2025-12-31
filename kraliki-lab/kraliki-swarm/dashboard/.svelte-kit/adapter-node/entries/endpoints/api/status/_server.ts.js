import { json } from "@sveltejs/kit";
import { b as getFullStatus } from "../../../../chunks/data.js";
const GET = async () => {
  const status = await getFullStatus();
  return json(status);
};
export {
  GET
};
