import { json } from "@sveltejs/kit";
const VOICE_URL = process.env.VOICE_URL || "http://172.27.0.5:8000";
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
const GET = async ({ url, cookies }) => {
  const path = url.searchParams.get("path") || "/health";
  const targetUrl = `${VOICE_URL}${path}`;
  const headers = getKralikiHeaders(cookies);
  try {
    const response = await fetch(targetUrl, {
      headers,
      signal: AbortSignal.timeout(1e4)
    });
    if (!response.ok) {
      return json({ error: "Voice by Kraliki API error", status: response.status }, { status: response.status });
    }
    const data = await response.json();
    return json(data);
  } catch {
    return json({ error: "Voice by Kraliki service unavailable" }, { status: 503 });
  }
};
const POST = async ({ url, request, cookies }) => {
  const path = url.searchParams.get("path") || "/";
  const targetUrl = `${VOICE_URL}${path}`;
  const headers = getKralikiHeaders(cookies);
  try {
    const body = await request.json();
    const response = await fetch(targetUrl, {
      method: "POST",
      headers,
      body: JSON.stringify(body),
      signal: AbortSignal.timeout(1e4)
    });
    if (!response.ok) {
      return json({ error: "Voice by Kraliki API error", status: response.status }, { status: response.status });
    }
    const data = await response.json();
    return json(data);
  } catch {
    return json({ error: "Voice by Kraliki service unavailable" }, { status: 503 });
  }
};
const PUT = async ({ url, request, cookies }) => {
  const path = url.searchParams.get("path") || "/";
  const targetUrl = `${VOICE_URL}${path}`;
  const headers = getKralikiHeaders(cookies);
  try {
    const body = await request.json();
    const response = await fetch(targetUrl, {
      method: "PUT",
      headers,
      body: JSON.stringify(body),
      signal: AbortSignal.timeout(1e4)
    });
    if (!response.ok) {
      return json({ error: "Voice by Kraliki API error", status: response.status }, { status: response.status });
    }
    const data = await response.json();
    return json(data);
  } catch {
    return json({ error: "Voice by Kraliki service unavailable" }, { status: 503 });
  }
};
const DELETE = async ({ url, cookies }) => {
  const path = url.searchParams.get("path") || "/";
  const targetUrl = `${VOICE_URL}${path}`;
  const headers = getKralikiHeaders(cookies);
  try {
    const response = await fetch(targetUrl, {
      method: "DELETE",
      headers,
      signal: AbortSignal.timeout(1e4)
    });
    if (!response.ok) {
      return json({ error: "Voice by Kraliki API error", status: response.status }, { status: response.status });
    }
    const text = await response.text();
    if (!text) {
      return json({ success: true });
    }
    try {
      const data = JSON.parse(text);
      return json(data);
    } catch {
      return json({ success: true });
    }
  } catch {
    return json({ error: "Voice by Kraliki service unavailable" }, { status: 503 });
  }
};
export {
  DELETE,
  GET,
  POST,
  PUT
};
