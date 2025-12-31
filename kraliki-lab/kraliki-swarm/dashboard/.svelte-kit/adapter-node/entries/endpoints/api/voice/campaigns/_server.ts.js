import { json } from "@sveltejs/kit";
const VOICE_URL = "http://127.0.0.1:8000";
function getUserFromCookie(cookies) {
  const sessionToken = cookies.get("session");
  if (!sessionToken) return null;
  try {
    const userData = JSON.parse(atob(sessionToken));
    return {
      id: userData.sub || "unknown",
      email: userData.email || `${userData.sub}@kraliki.local`,
      name: userData.name || "Kraliki User"
    };
  } catch {
    return null;
  }
}
function getKralikiHeaders(cookies) {
  const user = getUserFromCookie(cookies);
  if (user) {
    return {
      "X-Kraliki-Session": "kraliki-internal",
      "X-Kraliki-User-Id": user.id,
      "X-Kraliki-User-Email": user.email,
      "X-Kraliki-User-Name": user.name,
      "X-Kraliki-Tier": "free",
      "Content-Type": "application/json"
    };
  }
  return {
    "X-Kraliki-Session": "kraliki-internal",
    "X-Kraliki-User-Id": "local-agent",
    "X-Kraliki-User-Email": "agent@kraliki.local",
    "X-Kraliki-User-Name": "Local Agent",
    "X-Kraliki-Tier": "free",
    "Content-Type": "application/json"
  };
}
const GET = async ({ cookies }) => {
  const headers = getKralikiHeaders(cookies);
  try {
    const response = await fetch(`${VOICE_URL}/api/v1/campaigns`, {
      headers,
      signal: AbortSignal.timeout(1e4)
    });
    if (!response.ok) {
      return json({ error: "Voice by Kraliki campaigns API error", status: response.status }, { status: response.status });
    }
    const data = await response.json();
    return json(data);
  } catch {
    return json({ error: "Voice by Kraliki campaigns service unavailable" }, { status: 503 });
  }
};
const POST = async ({ request, cookies }) => {
  const headers = getKralikiHeaders(cookies);
  try {
    const body = await request.json();
    const response = await fetch(`${VOICE_URL}/api/v1/campaigns`, {
      method: "POST",
      headers,
      body: JSON.stringify(body),
      signal: AbortSignal.timeout(1e4)
    });
    if (!response.ok) {
      return json({ error: "Voice by Kraliki campaigns API error", status: response.status }, { status: response.status });
    }
    const data = await response.json();
    return json(data);
  } catch {
    return json({ error: "Voice by Kraliki campaigns service unavailable" }, { status: 503 });
  }
};
export {
  GET,
  POST
};
