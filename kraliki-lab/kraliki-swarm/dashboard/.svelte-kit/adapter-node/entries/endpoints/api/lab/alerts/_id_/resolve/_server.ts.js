import { json } from "@sveltejs/kit";
const PUT = async ({ params }) => {
  const alertId = params.id;
  if (!alertId) {
    return json({ error: "Alert ID is required" }, { status: 400 });
  }
  console.log(`Resolving alert: ${alertId}`);
  return json({ success: true, message: `Alert ${alertId} resolved` });
};
export {
  PUT
};
