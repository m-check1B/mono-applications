import { json } from "@sveltejs/kit";
const VOICE_URL = process.env.VOICE_URL || "http://172.21.0.27:8000";
async function fetchVoiceCampaigns() {
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 5e3);
    const response = await fetch(`${VOICE_URL}/simple-campaigns/`, {
      signal: controller.signal
    });
    clearTimeout(timeoutId);
    if (response.ok) {
      const data = await response.json();
      return data.map((c) => ({
        id: String(c.id),
        name: c.name || "Unnamed Campaign",
        type: c.type || "outbound",
        status: c.status || "draft",
        channel: "voice",
        progress: c.progress || 0,
        totalContacts: c.total_contacts || 0,
        completedContacts: c.completed_contacts || 0,
        createdAt: c.created_at || (/* @__PURE__ */ new Date()).toISOString(),
        updatedAt: c.updated_at || (/* @__PURE__ */ new Date()).toISOString()
      }));
    }
    return [];
  } catch {
    return [];
  }
}
const GET = async () => {
  const campaigns = await fetchVoiceCampaigns();
  return json({
    campaigns,
    total: campaigns.length,
    active: campaigns.filter((c) => c.status === "active").length,
    paused: campaigns.filter((c) => c.status === "paused").length,
    completed: campaigns.filter((c) => c.status === "completed").length
  });
};
const POST = async ({ request }) => {
  const body = await request.json();
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 5e3);
    const response = await fetch(`${VOICE_URL}/simple-campaigns/start`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        campaign_id: body.campaignId
      }),
      signal: controller.signal
    });
    clearTimeout(timeoutId);
    if (response.ok) {
      const data = await response.json();
      return json({ success: true, data });
    }
    return json({ success: false, error: "Failed to start campaign" }, { status: 400 });
  } catch (error) {
    return json({ success: false, error: String(error) }, { status: 500 });
  }
};
export {
  GET,
  POST
};
