import { json } from "@sveltejs/kit";
const VOICE_URL = "http://127.0.0.1:8000";
const GET = async () => {
  try {
    const response = await fetch(`${VOICE_URL}/health`, {
      signal: AbortSignal.timeout(5e3)
    });
    if (!response.ok) {
      return json({
        status: "unhealthy",
        service: "voice-kraliki",
        error: `HTTP ${response.status}`
      }, { status: 503 });
    }
    const data = await response.json();
    return json({
      ...data,
      proxy: "kraliki-swarm-dashboard"
    });
  } catch {
    return json({
      status: "unhealthy",
      service: "voice-kraliki",
      error: "Service unreachable"
    }, { status: 503 });
  }
};
export {
  GET
};
