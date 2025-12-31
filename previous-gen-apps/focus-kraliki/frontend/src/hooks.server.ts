import type { Handle } from '@sveltejs/kit';

export const handle: Handle = async ({ event, resolve }) => {
		// Proxy API requests to backend in production
		if (event.url.pathname.startsWith('/api')) {
			const backendUrl = process.env.BACKEND_URL || process.env.PUBLIC_API_URL;
			if (!backendUrl) {
				return new Response('Missing BACKEND_URL or PUBLIC_API_URL', { status: 500 });
			}
                // Remove /api prefix since backend routes don't have it
                const backendPath = event.url.pathname.replace(/^\/api/, '');
                const targetUrl = `${backendUrl}${backendPath}${event.url.search}`;

                const headers = new Headers(event.request.headers);
                headers.delete('host');
                headers.delete('connection');

                const response = await fetch(targetUrl, {
                        method: event.request.method,
                        headers: headers,
                        body: event.request.method !== 'GET' && event.request.method !== 'HEAD'
                                ? await event.request.arrayBuffer()
                                : undefined,
                });

                const responseHeaders = new Headers(response.headers);
                responseHeaders.delete('content-encoding');
                responseHeaders.delete('transfer-encoding');

                return new Response(response.body, {
                        status: response.status,
                        statusText: response.statusText,
                        headers: responseHeaders,
                });
        }

        // Add Content Security Policy headers
        const response = await resolve(event);

        // CSP for Markdown renderer and app security
        const csp = [
                "default-src 'self'",
                "script-src 'self' 'unsafe-inline' 'unsafe-eval'", // needed for SvelteKit dev
                "style-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com", // for highlight.js
                "img-src 'self' data: https: http:",
                "font-src 'self' https:",
                "connect-src 'self' https://analytics.verduona.com",
                "frame-ancestors 'none'",
                "object-src 'none'",
                "base-uri 'self'",
        ].join('; ');

        response.headers.set('Content-Security-Policy', csp);
        response.headers.set('X-Content-Type-Options', 'nosniff');
        response.headers.set('X-Frame-Options', 'DENY');

        return response;
};
