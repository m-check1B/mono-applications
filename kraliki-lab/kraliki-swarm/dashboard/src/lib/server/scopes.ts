import { readFile } from 'fs/promises';
import { join } from 'path';

// Default path to scopes config - can be overridden via KRALIKI_WORKSPACE env var
const WORKSPACE_DIR = process.env.KRALIKI_WORKSPACE || '/home/adminmatej/github/applications/kraliki-lab/kraliki-swarm/workspace';
const SCOPES_FILE = join(WORKSPACE_DIR, 'scopes.json');

export interface ScopeConfig {
	path: string;
	description?: string;
	subpaths?: Record<string, string>;
}

export interface ScopesConfig {
	version: string;
	name: string;
	description?: string;
	scopes: Record<string, ScopeConfig>;
	storage: {
		type: 'local' | 's3' | 'azure';
		base: string;
	};
	created?: string;
	lastModified?: string;
}

let cachedScopes: ScopesConfig | null = null;
let cacheTime: number = 0;
const CACHE_TTL = 60000; // 1 minute cache

/**
 * Load scopes configuration from workspace
 * Caches for 1 minute to avoid repeated disk reads
 */
export async function loadScopes(): Promise<ScopesConfig> {
	const now = Date.now();

	if (cachedScopes && (now - cacheTime) < CACHE_TTL) {
		return cachedScopes;
	}

	try {
		const content = await readFile(SCOPES_FILE, 'utf-8');
		cachedScopes = JSON.parse(content);
		cacheTime = now;
		return cachedScopes!;
	} catch (e) {
		console.error('Failed to load scopes config:', e);
		// Return default config if file doesn't exist
		return getDefaultScopes();
	}
}

/**
 * Get the full path for a scope
 */
export async function getScopePath(scopeName: string): Promise<string | null> {
	const scopes = await loadScopes();
	const scope = scopes.scopes[scopeName];
	return scope?.path || null;
}

/**
 * Get the full path for a subpath within a scope
 */
export async function getSubpath(scopeName: string, subpathName: string): Promise<string | null> {
	const scopes = await loadScopes();
	const scope = scopes.scopes[scopeName];

	if (!scope) return null;

	const subpath = scope.subpaths?.[subpathName];
	if (!subpath) return null;

	return join(scope.path, subpath);
}

/**
 * Get all available scope names
 */
export async function getScopeNames(): Promise<string[]> {
	const scopes = await loadScopes();
	return Object.keys(scopes.scopes);
}

/**
 * Check if a scope exists
 */
export async function hasScope(scopeName: string): Promise<boolean> {
	const scopes = await loadScopes();
	return scopeName in scopes.scopes;
}

/**
 * Get scope configuration details
 */
export async function getScope(scopeName: string): Promise<ScopeConfig | null> {
	const scopes = await loadScopes();
	return scopes.scopes[scopeName] || null;
}

/**
 * Clear the scopes cache (useful after config updates)
 */
export function clearScopesCache(): void {
	cachedScopes = null;
	cacheTime = 0;
}

/**
 * Default scopes for when config file is missing
 */
function getDefaultScopes(): ScopesConfig {
	return {
		version: '1.0',
		name: 'Default',
		description: 'Default scope configuration',
		scopes: {
			kraliki: {
				path: '/home/adminmatej/github/applications/kraliki-lab/kraliki-swarm',
				description: 'Kraliki system'
			}
		},
		storage: {
			type: 'local',
			base: '/home/adminmatej/github'
		}
	};
}
