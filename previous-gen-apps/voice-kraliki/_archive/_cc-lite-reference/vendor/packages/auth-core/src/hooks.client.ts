/**
 * React hooks for authentication
 * These hooks can be used in any React application within the unified stack
 */

import React, { useState, useEffect, useCallback, createContext, useContext } from 'react';
import type { 
  AuthUser, 
  AppIdentifier, 
  LoginRequest, 
  RegisterRequest,
  AuthResponse 
} from './types';

// Auth context type
interface AuthContextType {
  user: AuthUser | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (credentials: LoginRequest) => Promise<AuthResponse>;
  register: (data: RegisterRequest) => Promise<AuthResponse>;
  logout: () => Promise<void>;
  refreshToken: () => Promise<void>;
  hasAppAccess: (appId: AppIdentifier) => boolean;
  hasPermission: (appId: AppIdentifier, permission: string) => boolean;
}

// Create context
const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Auth provider props
interface AuthProviderProps {
  children: React.ReactNode;
  appId: AppIdentifier;
  authUrl: string;
  onAuthError?: (error: Error) => void;
}

// Auth provider component
export function AuthProvider({ 
  children, 
  appId, 
  authUrl,
  onAuthError 
}: AuthProviderProps) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Check if authenticated
  const isAuthenticated = !!user;

  // Login function
  const login = useCallback(async (credentials: LoginRequest): Promise<AuthResponse> => {
    try {
      const response = await fetch(`${authUrl}/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({ ...credentials, appId }),
      });

      const data = await response.json() as AuthResponse;

      if (!response.ok) {
        throw new Error((data as any).error || 'Login failed');
      }

      if (data.user) {
        setUser(data.user);
        
        // Store tokens if provided
        if (data.accessToken) {
          localStorage.setItem('accessToken', data.accessToken);
        }
        if (data.refreshToken) {
          localStorage.setItem('refreshToken', data.refreshToken);
        }
      }

      return data;
    } catch (error) {
      onAuthError?.(error as Error);
      throw error;
    }
  }, [authUrl, appId, onAuthError]);

  // Register function
  const register = useCallback(async (data: RegisterRequest): Promise<AuthResponse> => {
    try {
      const response = await fetch(`${authUrl}/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({ ...data, appId }),
      });

      const result = await response.json() as AuthResponse;

      if (!response.ok) {
        throw new Error((result as any).error || 'Registration failed');
      }

      if (result.user) {
        setUser(result.user);
        
        // Store tokens if provided
        if (result.accessToken) {
          localStorage.setItem('accessToken', result.accessToken);
        }
        if (result.refreshToken) {
          localStorage.setItem('refreshToken', result.refreshToken);
        }
      }

      return result;
    } catch (error) {
      onAuthError?.(error as Error);
      throw error;
    }
  }, [authUrl, appId, onAuthError]);

  // Logout function
  const logout = useCallback(async () => {
    try {
      await fetch(`${authUrl}/auth/logout`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('accessToken')}`,
        },
        credentials: 'include',
      });
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      setUser(null);
      localStorage.removeItem('accessToken');
      localStorage.removeItem('refreshToken');
    }
  }, [authUrl]);

  // Refresh token function
  const refreshToken = useCallback(async () => {
    const storedRefreshToken = localStorage.getItem('refreshToken');
    
    if (!storedRefreshToken) {
      throw new Error('No refresh token available');
    }

    try {
      const response = await fetch(`${authUrl}/auth/refresh`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({
          refreshToken: storedRefreshToken,
          appId,
        }),
      });

      const data = await response.json() as AuthResponse;

      if (!response.ok) {
        throw new Error((data as any).error || 'Token refresh failed');
      }

      if (data.accessToken) {
        localStorage.setItem('accessToken', data.accessToken);
      }
      if (data.refreshToken) {
        localStorage.setItem('refreshToken', data.refreshToken);
      }
      if (data.user) {
        setUser(data.user);
      }
    } catch (error) {
      onAuthError?.(error as Error);
      setUser(null);
      localStorage.removeItem('accessToken');
      localStorage.removeItem('refreshToken');
      throw error;
    }
  }, [authUrl, appId, onAuthError]);

  // Check app access
  const hasAppAccess = useCallback((checkAppId: AppIdentifier) => {
    if (!user) return false;
    return user.apps.some(app => app.appId === checkAppId);
  }, [user]);

  // Check permission
  const hasPermission = useCallback((checkAppId: AppIdentifier, permission: string) => {
    if (!user) return false;
    
    const appAccess = user.apps.find(app => app.appId === checkAppId);
    if (!appAccess) return false;
    
    // Owners have all permissions
    if (appAccess.role === 'owner') return true;
    
    // Admins have most permissions
    if (appAccess.role === 'admin' && permission !== 'manage_billing') return true;
    
    // Check specific permissions
    return appAccess.permissions.includes(permission as any);
  }, [user]);

  // Initialize auth on mount
  useEffect(() => {
    const initAuth = async () => {
      const accessToken = localStorage.getItem('accessToken');
      
      if (!accessToken) {
        setIsLoading(false);
        return;
      }

      try {
        const response = await fetch(`${authUrl}/auth/me`, {
          headers: {
            'Authorization': `Bearer ${accessToken}`,
          },
          credentials: 'include',
        });

        if (response.ok) {
          const data = await response.json() as { user: AuthUser };
          setUser(data.user);
        } else {
          // Try to refresh token
          await refreshToken();
        }
      } catch (error) {
        console.error('Auth initialization error:', error);
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
      } finally {
        setIsLoading(false);
      }
    };

    initAuth();
  }, [authUrl, refreshToken]);

  // Auto refresh token before expiry
  useEffect(() => {
    if (!user) return;

    // Refresh token 5 minutes before expiry
    const refreshInterval = setInterval(() => {
      refreshToken().catch(console.error);
    }, 10 * 60 * 1000); // 10 minutes

    return () => clearInterval(refreshInterval);
  }, [user, refreshToken]);

  const value: AuthContextType = {
    user,
    isLoading,
    isAuthenticated,
    login,
    register,
    logout,
    refreshToken,
    hasAppAccess,
    hasPermission,
  };

  return React.createElement(AuthContext.Provider, { value }, children);
}

// useAuth hook
export function useAuth() {
  const context = useContext(AuthContext);
  
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  
  return context;
}

// useRequireAuth hook - redirects if not authenticated
export function useRequireAuth(redirectTo = '/login') {
  const { isAuthenticated, isLoading } = useAuth();

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      window.location.href = redirectTo;
    }
  }, [isAuthenticated, isLoading, redirectTo]);

  return { isAuthenticated, isLoading };
}

// useRequireAppAccess hook - ensures user has access to specific app
export function useRequireAppAccess(appId: AppIdentifier, redirectTo = '/access-denied') {
  const { hasAppAccess, isLoading } = useAuth();
  const hasAccess = hasAppAccess(appId);

  useEffect(() => {
    if (!isLoading && !hasAccess) {
      window.location.href = redirectTo;
    }
  }, [hasAccess, isLoading, redirectTo]);

  return { hasAccess, isLoading };
}

// usePermission hook - check specific permission
export function usePermission(appId: AppIdentifier, permission: string) {
  const { hasPermission } = useAuth();
  return hasPermission(appId, permission);
}

// useAuthToken hook - get current access token
export function useAuthToken() {
  const [token, setToken] = useState<string | null>(null);

  useEffect(() => {
    setToken(localStorage.getItem('accessToken'));

    // Listen for storage changes
    const handleStorageChange = () => {
      setToken(localStorage.getItem('accessToken'));
    };

    window.addEventListener('storage', handleStorageChange);
    return () => window.removeEventListener('storage', handleStorageChange);
  }, []);

  return token;
}

// Export types for external use
export type { AuthContextType, AuthProviderProps };