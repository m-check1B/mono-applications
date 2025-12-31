import { json } from "@sveltejs/kit";
const VOICE_URL = "http://127.0.0.1:8000";
const GET = async () => {
  try {
    const response = await fetch(`${VOICE_URL}/api/v1/providers`, {
      signal: AbortSignal.timeout(1e4)
    });
    if (!response.ok) {
      return json({ error: "Voice by Kraliki providers API error", status: response.status }, { status: response.status });
    }
    const data = await response.json();
    return json(data);
  } catch {
    return json({ error: "Voice by Kraliki providers service unavailable" }, { status: 503 });
  }
};
export {
  GET
};
