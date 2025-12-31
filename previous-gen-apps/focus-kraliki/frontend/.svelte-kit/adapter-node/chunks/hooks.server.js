const handle = async ({ event, resolve }) => {
  if (event.url.pathname.startsWith("/api")) {
    const backendUrl = process.env.BACKEND_URL || process.env.PUBLIC_API_URL;
    if (!backendUrl) {
      return new Response("Missing BACKEND_URL or PUBLIC_API_URL", { status: 500 });
    }
    const backendPath = event.url.pathname.replace(/^\/api/, "");
    const targetUrl = `${backendUrl}${backendPath}${event.url.search}`;
    const headers = new Headers(event.request.headers);
    headers.delete("host");
    headers.delete("connection");
    const response2 = await fetch(targetUrl, {
      method: event.request.method,
      headers,
      body: event.request.method !== "GET" && event.request.method !== "HEAD" ? await event.request.arrayBuffer() : void 0
    });
    const responseHeaders = new Headers(response2.headers);
    responseHeaders.delete("content-encoding");
    responseHeaders.delete("transfer-encoding");
    return new Response(response2.body, {
      status: response2.status,
      statusText: response2.statusText,
      headers: responseHeaders
    });
  }
  const response = await resolve(event);
  const csp = [
    "default-src 'self'",
    "script-src 'self' 'unsafe-inline' 'unsafe-eval'",
    // needed for SvelteKit dev
    "style-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com",
    // for highlight.js
    "img-src 'self' data: https: http:",
    "font-src 'self' https:",
    "connect-src 'self' https://analytics.verduona.com",
    "frame-ancestors 'none'"
  ].join("; ");
  response.headers.set("Content-Security-Policy", csp);
  response.headers.set("X-Content-Type-Options", "nosniff");
  response.headers.set("X-Frame-Options", "DENY");
  return response;
};
export {
  handle
};
