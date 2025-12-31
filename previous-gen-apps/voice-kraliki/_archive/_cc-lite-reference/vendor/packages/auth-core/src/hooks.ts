/**
 * Server-safe hooks exports
 * This file exports React hooks only when in client environment
 */

// Re-export types that are safe for server use
export type { 
  AuthUser, 
  AppIdentifier, 
  LoginRequest, 
  RegisterRequest,
  AuthResponse,
  AccessTokenPayload,
  Permission,
  UserRole,
  AppAccess
} from './types';

// Server-safe client hooks exports
// These will be undefined on server, defined on client

// Define variables to hold client hooks
let clientHooks: any = {};
let isClient = false;

// Check if we're in client environment safely
try {
  isClient = typeof globalThis !== 'undefined' && 
             typeof globalThis.window !== 'undefined';
} catch (e) {
  isClient = false;
}

if (isClient) {
  try {
    // Dynamically import client hooks only in browser
    clientHooks = require('./hooks.client');
  } catch (error) {
    // Silent fail - hooks will be undefined
  }
}

// Export client hooks (will be undefined on server)
export const AuthProvider = clientHooks.AuthProvider;
export const useAuth = clientHooks.useAuth;
export const useRequireAuth = clientHooks.useRequireAuth;
export const useRequireAppAccess = clientHooks.useRequireAppAccess;
export const usePermission = clientHooks.usePermission;
export const useAuthToken = clientHooks.useAuthToken;

// Export types - these are always available
export type AuthContextType = any; // Define basic type to avoid import errors
export type AuthProviderProps = any;

// Utility function to check if client hooks are available
export const isClientHooksAvailable = () => isClient && !!clientHooks.AuthProvider;