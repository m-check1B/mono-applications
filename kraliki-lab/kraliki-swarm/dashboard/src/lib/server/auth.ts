import { createRemoteJWKSet, jwtVerify, type JWTPayload } from 'jose';
import crypto from 'crypto';
import fs from 'fs';
import path from 'path';

let envLoaded = false;

function loadEnvFile(filePath: string): void {
	if (!fs.existsSync(filePath)) {
		return;
	}

	const lines = fs.readFileSync(filePath, 'utf-8').split(/\r?\n/);
	for (const rawLine of lines) {
		const line = rawLine.trim();
		if (!line || line.startsWith('#') || !line.includes('=')) {
			continue;
		}

		const [keyPart, ...valueParts] = line.split('=');
		const key = keyPart.trim();
		if (!key || (process.env[key] ?? '') !== '') {
			continue;
		}

		let value = valueParts.join('=').trim();
		if (
			(value.startsWith('"') && value.endsWith('"')) ||
			(value.startsWith("'") && value.endsWith("'"))
		) {
			value = value.slice(1, -1);
		}
		process.env[key] = value;
	}
}

function loadEnvFiles(): void {
	if (envLoaded) {
		return;
	}
	envLoaded = true;

	const envPaths = [
		path.resolve(process.cwd(), '.env'),
		'/home/adminmatej/github/secrets/kraliki-dashboard.env',
		'/home/adminmatej/github/secrets/kraliki-swarm-dashboard.env'
	];

	for (const envPath of envPaths) {
		loadEnvFile(envPath);
	}
}

loadEnvFiles();

// Zitadel OIDC configuration
const ZITADEL_DOMAIN = process.env.ZITADEL_DOMAIN || 'identity.verduona.dev';
const CLIENT_ID = process.env.ZITADEL_CLIENT_ID || '';
const CLIENT_SECRET = process.env.ZITADEL_CLIENT_SECRET || '';
const SSO_DISABLED = process.env.SSO_DISABLED === 'true';

// Simple local auth fallback (when Zitadel not configured)
// Read from environment variables instead of hardcoding
const LOCAL_AUTH_EMAIL = process.env.LOCAL_AUTH_EMAIL || '';
const LOCAL_AUTH_PASSWORD = process.env.LOCAL_AUTH_PASSWORD || '';
const LOCAL_AUTH_NAME = process.env.LOCAL_AUTH_NAME || 'Local User';
const DEFAULT_AUTH_STORE_PATH =
	'/home/adminmatej/github/secrets/kraliki-swarm-dashboard-users.json';
const LEGACY_AUTH_STORE_PATH =
	'/home/adminmatej/github/secrets/kraliki-dashboard-users.json';
function getLocalAuthStorePath(): string {
	const directPath = (process.env.LOCAL_AUTH_STORE_PATH || '').trim();
	if (directPath) {
		return directPath;
	}

	const env = (process.env.KRALIKI_ENV || '').trim().toUpperCase();
	if (env) {
		const envPath = (process.env[`LOCAL_AUTH_STORE_PATH_${env}`] || '').trim();
		if (envPath) {
			return envPath;
		}
	}

	if (fs.existsSync(DEFAULT_AUTH_STORE_PATH)) {
		return DEFAULT_AUTH_STORE_PATH;
	}
	return LEGACY_AUTH_STORE_PATH;
}

const LOCAL_AUTH_STORE_PATH = getLocalAuthStorePath();

interface LocalUserRecord {
	id: string;
	name: string;
	email: string;
	passwordHash: string;
	salt: string;
	createdAt: string;
}

function normalizeEmail(email: string): string {
	return email.trim().toLowerCase();
}

function readLocalUsers(): LocalUserRecord[] {
	try {
		if (!fs.existsSync(LOCAL_AUTH_STORE_PATH)) {
			return [];
		}
		const raw = fs.readFileSync(LOCAL_AUTH_STORE_PATH, 'utf-8');
		if (!raw.trim()) {
			return [];
		}
		const parsed = JSON.parse(raw);
		return Array.isArray(parsed) ? (parsed as LocalUserRecord[]) : [];
	} catch (error) {
		console.error('Failed to read local auth store:', error);
		return [];
	}
}

function writeLocalUsers(users: LocalUserRecord[]): void {
	const dir = path.dirname(LOCAL_AUTH_STORE_PATH);
	fs.mkdirSync(dir, { recursive: true });
	fs.writeFileSync(LOCAL_AUTH_STORE_PATH, JSON.stringify(users, null, 2));
}

function hashPassword(password: string, salt: string): string {
	return crypto.scryptSync(password, salt, 64).toString('hex');
}

function verifyPassword(password: string, record: LocalUserRecord): boolean {
	const candidate = Buffer.from(hashPassword(password, record.salt), 'hex');
	const stored = Buffer.from(record.passwordHash, 'hex');
	if (candidate.length !== stored.length) {
		return false;
	}
	return crypto.timingSafeEqual(candidate, stored);
}

function findLocalUser(email: string): LocalUserRecord | null {
	const normalized = normalizeEmail(email);
	const users = readLocalUsers();
	return users.find((user) => user.email === normalized) || null;
}

export function createLocalUser(
	name: string,
	email: string,
	password: string
): { user?: User; error?: string } {
	const normalizedEmail = normalizeEmail(email);
	if (!normalizedEmail || !name.trim()) {
		return { error: 'Name and email are required' };
	}
	if (password.length < 8) {
		return { error: 'Password must be at least 8 characters long' };
	}
	if (findLocalUser(normalizedEmail)) {
		return { error: 'Account already exists for this email' };
	}

	const salt = crypto.randomBytes(16).toString('hex');
	const passwordHash = hashPassword(password, salt);
	const userRecord: LocalUserRecord = {
		id: normalizedEmail,
		name: name.trim(),
		email: normalizedEmail,
		passwordHash,
		salt,
		createdAt: new Date().toISOString()
	};

	const users = readLocalUsers();
	users.push(userRecord);
	writeLocalUsers(users);

	return {
		user: {
			id: userRecord.id,
			name: userRecord.name,
			email: userRecord.email,
			isLocal: true
		}
	};
}

export function validateLocalCredentials(email: string, password: string): User | null {
	// Check against environment-configured local credentials
	if (email === LOCAL_AUTH_EMAIL && password === LOCAL_AUTH_PASSWORD && LOCAL_AUTH_EMAIL) {
		return {
			id: email,
			name: LOCAL_AUTH_NAME,
			email: email,
			isLocal: true
		};
	}

	const localUser = findLocalUser(email);
	if (localUser && verifyPassword(password, localUser)) {
		return {
			id: localUser.id,
			name: localUser.name,
			email: localUser.email,
			isLocal: true
		};
	}
	return null;
}

export function isLocalAuthConfigured(): boolean {
	if (LOCAL_AUTH_EMAIL && LOCAL_AUTH_PASSWORD) {
		return true;
	}
	return readLocalUsers().length > 0;
}

// JWKS client for JWT verification (cached automatically by jose)
const JWKS = createRemoteJWKSet(new URL(`https://${ZITADEL_DOMAIN}/oauth/v2/keys`));

export interface VerifiedTokenPayload extends JWTPayload {
	sub: string;
	name?: string;
	preferred_username?: string;
	email?: string;
}

function getRedirectUri(): string {
	return process.env.ORIGIN
		? `${process.env.ORIGIN}/auth/callback`
		: 'http://localhost:8099/auth/callback';
}

export interface User {
	id: string;
	name: string;
	email?: string;
	isLocal: boolean;
	isDemo?: boolean;
}

export function isDemoMode(): boolean {
	return process.env.DEMO_MODE === 'true';
}

export function getDemoUser(): User {
	return {
		id: 'demo-user',
		name: 'Demo Viewer',
		email: 'demo@kraliki.com',
		isLocal: false,
		isDemo: true
	};
}

/**
 * Determines if a request originates from a trusted local source.
 *
 * SECURITY: This bypass is intentional and required for:
 * - Kraliki AI agents running on the same machine
 * - Local development and testing
 * - Internal ZeroTier network communication
 *
 * Allowed sources:
 * - 127.0.0.1/::1 (localhost)
 * - 172.17.* (Docker bridge network)
 * - 10.204.* (ZeroTier private network)
 */
export function isLocalRequest(request: Request): boolean {
	const forwardedFor = request.headers.get('x-forwarded-for');
	const realIp = request.headers.get('x-real-ip');
	const host = request.headers.get('host');

	// Check X-Forwarded-For header first (set by reverse proxies)
	if (forwardedFor) {
		const firstIp = forwardedFor.split(',')[0].trim();
		return firstIp === '127.0.0.1' || firstIp === '::1';
	}

	// Check X-Real-IP header (alternative proxy header)
	if (realIp) {
		return realIp === '127.0.0.1' || realIp === '::1';
	}

	// Check Host header for localhost or trusted internal networks
	if (host) {
		const hostWithoutPort = host.split(':')[0];
		return (
			hostWithoutPort === 'localhost' ||
			hostWithoutPort === '127.0.0.1' ||
			hostWithoutPort.startsWith('172.17.') || // Docker bridge
			hostWithoutPort.startsWith('10.204.') // ZeroTier network
		);
	}

	// Fallback to URL hostname
	const url = new URL(request.url);
	return url.hostname === 'localhost' || url.hostname === '127.0.0.1';
}

export function getLocalUser(): User {
	return {
		id: 'local-agent',
		name: 'Local Agent',
		isLocal: true
	};
}

export function createAuthorizationURL(state: string): URL | null {
	if (!CLIENT_ID) return null;

	const url = new URL(`https://${ZITADEL_DOMAIN}/oauth/v2/authorize`);
	url.searchParams.set('client_id', CLIENT_ID);
	url.searchParams.set('redirect_uri', getRedirectUri());
	url.searchParams.set('response_type', 'code');
	url.searchParams.set('scope', 'openid profile email');
	url.searchParams.set('state', state);

	return url;
}

export async function validateAuthorizationCode(code: string): Promise<{
	accessToken: string;
	refreshToken?: string;
	idToken: string;
} | null> {
	if (!CLIENT_ID || !CLIENT_SECRET) return null;

	try {
		const response = await fetch(`https://${ZITADEL_DOMAIN}/oauth/v2/token`, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/x-www-form-urlencoded',
				'Authorization': 'Basic ' + btoa(`${CLIENT_ID}:${CLIENT_SECRET}`)
			},
			body: new URLSearchParams({
				grant_type: 'authorization_code',
				code,
				redirect_uri: getRedirectUri()
			})
		});

		if (!response.ok) {
			console.error('Token exchange failed:', await response.text());
			return null;
		}

		const tokens = await response.json();
		return {
			accessToken: tokens.access_token,
			refreshToken: tokens.refresh_token,
			idToken: tokens.id_token
		};
	} catch (error) {
		console.error('Failed to validate authorization code:', error);
		return null;
	}
}

export function isAuthConfigured(): boolean {
	if (SSO_DISABLED) {
		return false;
	}
	return !!(CLIENT_ID && CLIENT_SECRET);
}

export function shouldUseSecureCookies(url: URL, request?: Request): boolean {
	const forwardedProto = request?.headers
		.get('x-forwarded-proto')
		?.split(',')[0]
		?.trim()
		.toLowerCase();
	if (forwardedProto) {
		return forwardedProto === 'https';
	}
	return url.protocol === 'https:';
}

export function isSsoDisabled(): boolean {
	return SSO_DISABLED;
}

/**
 * Verify ID token signature using Zitadel's JWKS.
 * This cryptographically validates the token wasn't tampered with.
 */
export async function verifyIdToken(idToken: string): Promise<VerifiedTokenPayload | null> {
	try {
		const { payload } = await jwtVerify(idToken, JWKS, {
			issuer: `https://${ZITADEL_DOMAIN}`,
			// Don't verify audience for ID tokens (varies by flow)
		});

		// Ensure we have required fields
		if (!payload.sub) {
			console.error('ID token missing sub claim');
			return null;
		}

		return payload as VerifiedTokenPayload;
	} catch (error) {
		console.error('ID token verification failed:', error);
		return null;
	}
}
