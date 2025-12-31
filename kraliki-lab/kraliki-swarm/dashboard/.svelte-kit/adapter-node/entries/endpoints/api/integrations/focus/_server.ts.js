import { json } from "@sveltejs/kit";
const FOCUS_URL = process.env.FOCUS_URL || "http://172.28.0.4:3017";
const GET = async ({ url }) => {
  const appDomain = url.hostname.endsWith("verduona.dev") ? "verduona.dev" : "kraliki.com";
  const publicUrl = `https://focus.${appDomain}`;
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 2e3);
    const response = await fetch(`${FOCUS_URL}/health`, {
      signal: controller.signal
    });
    clearTimeout(timeoutId);
    if (response.ok) {
      return json({
        status: "online",
        url: FOCUS_URL,
        publicUrl
      });
    } else {
      return json({
        status: "offline",
        url: FOCUS_URL,
        publicUrl
      });
    }
  } catch {
    return json({
      status: "offline",
      url: FOCUS_URL,
      publicUrl
    });
  }
};
export {
  GET
};
