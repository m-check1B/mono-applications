// Type definitions for @unified/auth-core

export type AppIdentifier = 'productivity-hub' | 'invoice-gym' | 'cc-light' | 'midnight-burner' | 'admin-panel' | 'demo' | string;

export type UserRole = 'admin' | 'user' | 'guest' | 'owner';

export type Permission = 
  | 'read'
  | 'write'
  | 'delete'
  | 'manage_users'
  | 'manage_billing'
  | 'manage_settings'
  | 'view_analytics'
  | 'export_data'
  | string;

export interface AppAccess {
  appId: AppIdentifier;
  role: UserRole;
  permissions: Permission[];
  grantedAt: string;
  grantedBy?: string;
}

export interface AuthUser {
  id: string;
  email: string;
  name?: string;
  role?: UserRole;
  organizationId?: string;
  permissions?: Permission[];
  apps: AppAccess[];
  avatar?: string;
  emailVerified?: boolean;
  twoFactorEnabled?: boolean;
  createdAt?: string;
  updatedAt?: string;
  lastLoginAt?: string;
}

export interface AuthResponse {
  user: AuthUser;
  token?: string;
  accessToken?: string;
  refreshToken?: string;
  expiresIn?: number;
}

export interface AccessTokenPayload {
  sub: string;
  email: string;
  roles?: string[];
  permissions?: string[];
  iat?: number;
  exp?: number;
  appId?: AppIdentifier;
}

export interface SessionPayload {
  sub: string;
  email: string;
  roles: string[];
  iat?: number;
  exp?: number;
  metadata?: Record<string, any>;
}

export interface TokenService {
  sign(payload: AccessTokenPayload): Promise<string>;
  verify(token: string): Promise<AccessTokenPayload>;
  verifyAccessToken(token: string): AccessTokenPayload | null;
  refresh(refreshToken: string): Promise<AuthResponse>;
}

// Schema request/response types
export interface LoginRequest {
  email: string;
  password: string;
  appId: AppIdentifier;
  rememberMe?: boolean;
}

export interface RegisterRequest {
  email: string;
  password: string;
  name?: string;
  appId: AppIdentifier;
}

export interface RefreshTokenRequest {
  refreshToken: string;
  appId: AppIdentifier;
}

export interface PasswordResetRequest {
  email: string;
}

export interface PasswordResetConfirm {
  token: string;
  newPassword: string;
}

export interface EmailVerification {
  token: string;
}

export interface UpdateProfile {
  name?: string;
  avatar?: string;
}

export interface GrantAppAccess {
  userId: string;
  appId: AppIdentifier;
  role: UserRole;
  permissions?: Permission[];
}

export interface RevokeAppAccess {
  userId: string;
  appId: AppIdentifier;
}

export interface SessionData {
  id: string;
  userId: string;
  appId: AppIdentifier;
  token: string;
  refreshToken?: string;
  expiresAt: Date;
  createdAt: Date;
  lastActivity: Date;
  ip?: string;
  userAgent?: string;
}

export interface OAuthCallback {
  provider: 'google' | 'github' | 'microsoft';
  code: string;
  state: string;
  appId: AppIdentifier;
}

export interface TwoFactorSetup {
  secret: string;
}

export interface TwoFactorVerify {
  code: string;
}

export interface ApiKeyCreate {
  name: string;
  expiresAt?: Date;
  permissions?: string[];
}

export interface ApiKeyRevoke {
  keyId: string;
}

export interface AuditLogQuery {
  userId?: string;
  appId?: AppIdentifier;
  action?: string;
  startDate?: Date;
  endDate?: Date;
  limit?: number;
  offset?: number;
}
