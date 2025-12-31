import { json } from "@sveltejs/kit";
const VOICE_URL = process.env.VOICE_URL || "http://172.21.0.27:8000";
async function fetchVoiceQueue() {
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 5e3);
    const response = await fetch(`${VOICE_URL}/api/queue/available-agents`, {
      signal: controller.signal
    });
    clearTimeout(timeoutId);
    if (response.ok) {
      return [];
    }
    return [];
  } catch {
    return [];
  }
}
async function fetchVoicemails() {
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 5e3);
    const response = await fetch(`${VOICE_URL}/voicemails`, {
      signal: controller.signal
    });
    clearTimeout(timeoutId);
    if (response.ok) {
      const data = await response.json();
      if (Array.isArray(data)) {
        return data.map((vm) => ({
          id: String(vm.id),
          channel: "voice",
          type: "inbound",
          status: vm.heard ? "completed" : "waiting",
          caller: String(vm.caller || vm.from_number || "Unknown"),
          waitTime: 0,
          startedAt: String(vm.created_at || (/* @__PURE__ */ new Date()).toISOString())
        }));
      }
    }
    return [];
  } catch {
    return [];
  }
}
const GET = async ({ url }) => {
  const type = url.searchParams.get("type") || "all";
  const queueItems = await fetchVoiceQueue();
  const voicemails = await fetchVoicemails();
  let items = [...queueItems, ...voicemails];
  if (type === "inbound") {
    items = items.filter((i) => i.type === "inbound");
  } else if (type === "outbound") {
    items = items.filter((i) => i.type === "outbound");
  }
  return json({
    items,
    total: items.length,
    waiting: items.filter((i) => i.status === "waiting").length,
    inProgress: items.filter((i) => i.status === "in_progress").length,
    avgWaitTime: items.length > 0 ? Math.round(items.reduce((sum, i) => sum + i.waitTime, 0) / items.length) : 0
  });
};
export {
  GET
};
