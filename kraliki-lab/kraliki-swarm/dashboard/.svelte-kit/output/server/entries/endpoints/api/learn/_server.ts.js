import { json } from "@sveltejs/kit";
const LEARN_URL = process.env.LEARN_URL || "http://127.0.0.1:8030";
const GET = async ({ url }) => {
  const path = url.searchParams.get("path") || "/";
  const targetUrl = `${LEARN_URL}${path}`;
  try {
    const response = await fetch(targetUrl, {
      signal: AbortSignal.timeout(1e4)
    });
    if (!response.ok) {
      return json({ error: "Learn by Kraliki API error", status: response.status }, { status: response.status });
    }
    const data = await response.json();
    return json(data);
  } catch {
    return json({ error: "Learn by Kraliki service unavailable" }, { status: 503 });
  }
};
const POST = async ({ url, request }) => {
  const path = url.searchParams.get("path") || "/";
  const targetUrl = `${LEARN_URL}${path}`;
  try {
    const body = await request.json();
    const response = await fetch(targetUrl, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
      signal: AbortSignal.timeout(1e4)
    });
    if (!response.ok) {
      return json({ error: "Learn by Kraliki API error", status: response.status }, { status: response.status });
    }
    const data = await response.json();
    return json(data);
  } catch {
    return json({ error: "Learn by Kraliki service unavailable" }, { status: 503 });
  }
};
const PUT = async ({ url, request }) => {
  const path = url.searchParams.get("path") || "/";
  const targetUrl = `${LEARN_URL}${path}`;
  try {
    const body = await request.json();
    const response = await fetch(targetUrl, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
      signal: AbortSignal.timeout(1e4)
    });
    if (!response.ok) {
      return json({ error: "Learn by Kraliki API error", status: response.status }, { status: response.status });
    }
    const data = await response.json();
    return json(data);
  } catch {
    return json({ error: "Learn by Kraliki service unavailable" }, { status: 503 });
  }
};
export {
  GET,
  POST,
  PUT
};
