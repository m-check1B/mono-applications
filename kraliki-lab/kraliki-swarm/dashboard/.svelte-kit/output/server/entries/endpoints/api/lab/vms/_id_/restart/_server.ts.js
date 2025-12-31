import { json } from "@sveltejs/kit";
const POST = async ({ params }) => {
  const vmId = params.id;
  if (!vmId) {
    return json({ error: "VM ID is required" }, { status: 400 });
  }
  console.log(`Restarting VM: ${vmId}`);
  return json({ success: true, message: `Restart command sent for VM ${vmId}` });
};
export {
  POST
};
