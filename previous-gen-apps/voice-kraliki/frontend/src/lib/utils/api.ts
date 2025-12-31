import { BACKEND_URL } from '$lib/config/env';
import { authStore } from '$lib/stores/auth';

const JSON_CONTENT_TYPES = ['application/json', 'application/ld+json'];

function resolveUrl(path: string) {
	if (path.startsWith('http://') || path.startsWith('https://')) {
		return path;
	}

	const normalizedPath = path.startsWith('/') ? path : `/${path}`;
	return `${BACKEND_URL}${normalizedPath}`;
}

function toHeaders(input?: HeadersInit): Headers {
	if (!input) return new Headers();
	if (input instanceof Headers) return new Headers(input);
	return new Headers(input);
}

export interface ApiFetchOptions extends RequestInit {
	retryOnAuthError?: boolean;
	autoJson?: boolean;
	maxRetries?: number;
	retryDelay?: number;
}

export interface ApiError extends Error {
	status: number;
	payload?: unknown;
}

// Exponential backoff with jitter
function getRetryDelay(attempt: number, baseDelay: number = 1000): number {
	const exponentialDelay = Math.min(baseDelay * Math.pow(2, attempt), 30000);
	const jitter = Math.random() * 0.3 * exponentialDelay;
	return exponentialDelay + jitter;
}

// Check if error is retryable
function isRetryableError(status: number): boolean {
	// Retry on network errors (5xx) and rate limiting (429)
	return status === 429 || (status >= 500 && status < 600);
}

async function tryRefreshTokens() {
	try {
		return await authStore.refreshTokens();
	} catch (error) {
		console.error('Failed to refresh tokens', error);
		return false;
	}
}

export async function apiFetch(input: string, init: ApiFetchOptions = {}) {
	const {
		retryOnAuthError = true,
		autoJson = true,
		maxRetries = 3,
		retryDelay = 1000,
		headers,
		...rest
	} = init;

	const url = resolveUrl(input);
	const headerBag = toHeaders(headers);
	const { tokens } = authStore.getSnapshot();

	if (rest.body && !headerBag.has('Content-Type')) {
		headerBag.set('Content-Type', 'application/json');
	}

	if (tokens?.accessToken) {
		headerBag.set('Authorization', `Bearer ${tokens.accessToken}`);
	}

	let lastError: ApiError | null = null;

	for (let attempt = 0; attempt <= maxRetries; attempt++) {
		try {
			const response = await fetch(url, {
				...rest,
				headers: headerBag
			});

			if (response.status === 401 && retryOnAuthError) {
				const refreshed = await tryRefreshTokens();
				if (refreshed) {
					return apiFetch(input, { ...init, retryOnAuthError: false });
				}
			}

			if (!response.ok) {
				let payload: unknown;
				if (autoJson) {
					try {
						payload = await response.clone().json();
					} catch {
						payload = await response.text();
					}
				}

				const error: ApiError = Object.assign(new Error(response.statusText), {
					status: response.status,
					payload
				});

				// If error is retryable and we have attempts left, retry
				if (isRetryableError(response.status) && attempt < maxRetries) {
					lastError = error;
					const delay = getRetryDelay(attempt, retryDelay);
					console.warn(`Request failed with status ${response.status}, retrying in ${delay}ms...`);
					await new Promise(resolve => setTimeout(resolve, delay));
					continue;
				}

				throw error;
			}

			if (!autoJson) {
				return response;
			}

			const contentType = response.headers.get('Content-Type') ?? '';
			const shouldParseJson = JSON_CONTENT_TYPES.some((type) => contentType.includes(type));
			return shouldParseJson ? response.json() : response.text();

		} catch (error) {
			// Network error or other fetch failure
			if (attempt < maxRetries) {
				lastError = error as ApiError;
				const delay = getRetryDelay(attempt, retryDelay);
				console.warn(`Network error, retrying in ${delay}ms...`, error);
				await new Promise(resolve => setTimeout(resolve, delay));
				continue;
			}
			throw error;
		}
	}

	// If we get here, all retries failed
	throw lastError || new Error('Request failed after all retries');
}

export async function apiGet<T>(path: string, options?: Omit<ApiFetchOptions, 'method'>): Promise<T> {
	return apiFetch(path, { ...options, method: 'GET' });
}

export async function apiPost<T, B = unknown>(
	path: string,
	body: B,
	options: ApiFetchOptions = {}
): Promise<T> {
	const { body: overrideBody, ...rest } = options;
	return apiFetch(path, {
		...rest,
		method: 'POST',
		body: overrideBody ?? JSON.stringify(body)
	});
}

export async function apiPatch<T, B = unknown>(
	path: string,
	body: B,
	options: ApiFetchOptions = {}
): Promise<T> {
	const { body: overrideBody, ...rest } = options;
	return apiFetch(path, {
		...rest,
		method: 'PATCH',
		body: overrideBody ?? JSON.stringify(body)
	});
}

export async function apiDelete<T>(path: string, options?: Omit<ApiFetchOptions, 'method'>): Promise<T> {
	return apiFetch(path, { ...options, method: 'DELETE' });
}
