import { json } from "@sveltejs/kit";
const VOICE_URL = process.env.VOICE_URL || "http://172.21.0.27:8000";
async function fetchVoiceAgents() {
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 5e3);
    const response = await fetch(`${VOICE_URL}/team-management/agents`, {
      signal: controller.signal
    });
    clearTimeout(timeoutId);
    if (response.ok) {
      const data = await response.json();
      if (Array.isArray(data)) {
        return data.map((a) => ({
          id: String(a.id || a.agent_id),
          name: String(a.name || a.display_name || "AI Agent"),
          type: "voice",
          status: mapAgentStatus(a.status),
          currentSession: a.current_session,
          callsToday: Number(a.calls_today || 0),
          avgCallDuration: Number(a.avg_call_duration || 0),
          successRate: Number(a.success_rate || 0)
        }));
      }
    }
    return [];
  } catch {
    return [];
  }
}
function mapAgentStatus(status) {
  switch (status?.toLowerCase()) {
    case "available":
    case "ready":
    case "idle":
      return "available";
    case "busy":
    case "on_call":
    case "incall":
      return "busy";
    default:
      return "offline";
  }
}
const GET = async () => {
  const agents = await fetchVoiceAgents();
  const displayAgents = agents.length > 0 ? agents : [
    {
      id: "ai-voice-1",
      name: "Voice AI Agent",
      type: "voice",
      status: "available",
      callsToday: 0,
      avgCallDuration: 0,
      successRate: 0
    },
    {
      id: "ai-chat-1",
      name: "Chat AI Agent",
      type: "chat",
      status: "offline",
      callsToday: 0,
      avgCallDuration: 0,
      successRate: 0
    },
    {
      id: "ai-email-1",
      name: "Email AI Agent",
      type: "email",
      status: "offline",
      callsToday: 0,
      avgCallDuration: 0,
      successRate: 0
    }
  ];
  return json({
    agents: displayAgents,
    total: displayAgents.length,
    available: displayAgents.filter((a) => a.status === "available").length,
    busy: displayAgents.filter((a) => a.status === "busy").length,
    offline: displayAgents.filter((a) => a.status === "offline").length
  });
};
export {
  GET
};
