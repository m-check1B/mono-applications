import { json } from "@sveltejs/kit";
const WINDMILL_API_URL = "http://127.0.0.1:8101";
const GET = async () => {
  try {
    const response = await fetch(`${WINDMILL_API_URL}/health`, {
      signal: AbortSignal.timeout(5e3)
    });
    if (response.ok) {
      const data = await response.json();
      return json(data);
    } else {
      return json({
        status: "unhealthy",
        error: `HTTP ${response.status}`
      }, { status: 503 });
    }
  } catch (error) {
    return json({
      status: "unhealthy",
      error: "Windmill API unreachable"
    }, { status: 503 });
  }
};
export {
  GET
};
