/**
 * @unified/auth-core
 * Unified authentication for the stack 2025 monorepo system
 * Provides JWT-based SSO across all apps, websites, and demos
 */

// Export types first to avoid circular dependencies
export * from './types';

// Export JWT functionality
export * from './jwt';

// Re-export schemas
export * from './schemas';

// Re-export middleware
export * from './middleware';

// Re-export React hooks
export * from './hooks';

// Version info
export const VERSION = '1.0.0';
export const AUTH_COOKIE_NAME = 'vd_session';
export const AUTH_COOKIE_DOMAIN = process.env.AUTH_COOKIE_DOMAIN || '.verduona.com';
