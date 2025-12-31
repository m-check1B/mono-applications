import { json } from "@sveltejs/kit";
const VOICE_URL = process.env.VOICE_URL || "http://172.21.0.27:8000";
async function checkVoiceHealth() {
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 2e3);
    const response = await fetch(`${VOICE_URL}/health`, {
      signal: controller.signal
    });
    clearTimeout(timeoutId);
    return response.ok;
  } catch {
    return false;
  }
}
async function getVoiceAnalytics() {
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 3e3);
    const response = await fetch(`${VOICE_URL}/api/analytics/dashboard/overview`, {
      signal: controller.signal
    });
    clearTimeout(timeoutId);
    if (response.ok) {
      const data = await response.json();
      return {
        inbound: data.inbound_calls || data.total_inbound || 0,
        outbound: data.outbound_calls || data.total_outbound || 0
      };
    }
    return { inbound: 0, outbound: 0 };
  } catch {
    return { inbound: 0, outbound: 0 };
  }
}
const GET = async () => {
  const voiceOnline = await checkVoiceHealth();
  const voiceStats = voiceOnline ? await getVoiceAnalytics() : { inbound: 0, outbound: 0 };
  const channels = [
    {
      id: "voice",
      name: "Voice/Calls",
      status: voiceOnline ? "active" : "inactive",
      provider: "Voice by Kraliki",
      inbound: voiceStats.inbound,
      outbound: voiceStats.outbound,
      lastActivity: voiceOnline ? (/* @__PURE__ */ new Date()).toISOString() : void 0
    },
    {
      id: "sms",
      name: "SMS",
      status: "coming",
      provider: "Twilio (planned)",
      inbound: 0,
      outbound: 0
    },
    {
      id: "email",
      name: "Email",
      status: "coming",
      provider: "SMTP (planned)",
      inbound: 0,
      outbound: 0
    },
    {
      id: "chat",
      name: "Chat",
      status: "coming",
      provider: "Voice by Kraliki Chat API",
      inbound: 0,
      outbound: 0
    },
    {
      id: "social",
      name: "Social",
      status: "coming",
      provider: "Meta/LinkedIn (planned)",
      inbound: 0,
      outbound: 0
    }
  ];
  const stats = {
    totalInbound: channels.reduce((sum, c) => sum + c.inbound, 0),
    totalOutbound: channels.reduce((sum, c) => sum + c.outbound, 0),
    activeChannels: channels.filter((c) => c.status === "active").length,
    avgResponseTime: 0,
    voiceStatus: voiceOnline ? "online" : "offline",
    channels
  };
  return json(stats);
};
export {
  GET
};
