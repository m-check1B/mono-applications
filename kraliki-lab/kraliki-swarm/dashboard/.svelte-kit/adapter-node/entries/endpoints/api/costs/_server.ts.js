import { json } from "@sveltejs/kit";
import { a as getCostAnalytics } from "../../../../chunks/data.js";
const GET = async () => {
  const costs = await getCostAnalytics();
  return json(costs);
};
export {
  GET
};
