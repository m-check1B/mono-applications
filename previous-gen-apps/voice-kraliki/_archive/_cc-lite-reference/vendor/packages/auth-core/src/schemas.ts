/**
 * Zod validation schemas for authentication
 */

import { z } from 'zod';
import type { AppIdentifier, UserRole, Permission } from './types';

// Password validation
export const passwordSchema = z
  .string()
  .min(8, 'Password must be at least 8 characters')
  .regex(/[A-Z]/, 'Password must contain at least one uppercase letter')
  .regex(/[0-9]/, 'Password must contain at least one number')
  .regex(/[!@#$%^&*]/, 'Password must contain at least one special character');

// Email validation
export const emailSchema = z
  .string()
  .email('Invalid email address')
  .toLowerCase();

// Login request schema
export const loginRequestSchema = z.object({
  email: emailSchema,
  password: z.string().min(1, 'Password is required'),
  appId: z.enum(['cc-light', 'productivity-hub', 'midnight-burner', 'admin-panel', 'demo'] as const),
  rememberMe: z.boolean().optional().default(false)
});

// Register request schema
export const registerRequestSchema = z.object({
  email: emailSchema,
  password: passwordSchema,
  name: z.string().min(2, 'Name must be at least 2 characters').optional(),
  appId: z.enum(['cc-light', 'productivity-hub', 'midnight-burner', 'admin-panel', 'demo'] as const)
});

// Refresh token schema
export const refreshTokenSchema = z.object({
  refreshToken: z.string().min(1, 'Refresh token is required'),
  appId: z.enum(['cc-light', 'productivity-hub', 'midnight-burner', 'admin-panel', 'demo'] as const)
});

// Password reset request
export const passwordResetRequestSchema = z.object({
  email: emailSchema
});

// Password reset confirmation
export const passwordResetConfirmSchema = z.object({
  token: z.string().min(1, 'Reset token is required'),
  newPassword: passwordSchema
});

// Email verification
export const emailVerificationSchema = z.object({
  token: z.string().min(1, 'Verification token is required')
});

// Update user profile
export const updateProfileSchema = z.object({
  name: z.string().min(2).optional(),
  avatar: z.string().url().optional()
});

// Grant app access
export const grantAppAccessSchema = z.object({
  userId: z.string().cuid(),
  appId: z.enum(['cc-light', 'productivity-hub', 'midnight-burner', 'admin-panel', 'demo'] as const),
  role: z.enum(['user', 'admin', 'owner', 'guest'] as const),
  permissions: z.array(z.enum([
    'read',
    'write',
    'delete',
    'manage_users',
    'manage_billing',
    'manage_settings',
    'view_analytics',
    'export_data'
  ] as const)).optional().default([])
});

// Revoke app access
export const revokeAppAccessSchema = z.object({
  userId: z.string().cuid(),
  appId: z.enum(['cc-light', 'productivity-hub', 'midnight-burner', 'admin-panel', 'demo'] as const)
});

// Session validation
export const sessionSchema = z.object({
  id: z.string().cuid(),
  userId: z.string().cuid(),
  appId: z.enum(['cc-light', 'productivity-hub', 'midnight-burner', 'admin-panel', 'demo'] as const),
  token: z.string(),
  refreshToken: z.string().optional(),
  expiresAt: z.date(),
  createdAt: z.date(),
  lastActivity: z.date(),
  ip: z.string().ip().optional(),
  userAgent: z.string().optional()
});

// OAuth callback
export const oauthCallbackSchema = z.object({
  provider: z.enum(['google', 'github', 'microsoft'] as const),
  code: z.string(),
  state: z.string(),
  appId: z.enum(['cc-light', 'productivity-hub', 'midnight-burner', 'admin-panel', 'demo'] as const)
});

// Two-factor authentication
export const twoFactorSetupSchema = z.object({
  secret: z.string()
});

export const twoFactorVerifySchema = z.object({
  code: z.string().length(6, 'Code must be 6 digits')
});

// API key management
export const apiKeyCreateSchema = z.object({
  name: z.string().min(1, 'API key name is required'),
  expiresAt: z.date().optional(),
  permissions: z.array(z.string()).optional()
});

export const apiKeyRevokeSchema = z.object({
  keyId: z.string().cuid()
});

// Audit log query
export const auditLogQuerySchema = z.object({
  userId: z.string().cuid().optional(),
  appId: z.enum(['cc-light', 'productivity-hub', 'midnight-burner', 'admin-panel', 'demo'] as const).optional(),
  action: z.string().optional(),
  startDate: z.date().optional(),
  endDate: z.date().optional(),
  limit: z.number().min(1).max(100).default(50),
  offset: z.number().min(0).default(0)
});

// Schema-inferred types (these are the same as in types.ts but created from schemas)
export type LoginRequestSchema = z.infer<typeof loginRequestSchema>;
export type RegisterRequestSchema = z.infer<typeof registerRequestSchema>;
export type RefreshTokenRequestSchema = z.infer<typeof refreshTokenSchema>;
export type PasswordResetRequestSchema = z.infer<typeof passwordResetRequestSchema>;
export type PasswordResetConfirmSchema = z.infer<typeof passwordResetConfirmSchema>;
export type EmailVerificationSchema = z.infer<typeof emailVerificationSchema>;
export type UpdateProfileSchema = z.infer<typeof updateProfileSchema>;
export type GrantAppAccessSchema = z.infer<typeof grantAppAccessSchema>;
export type RevokeAppAccessSchema = z.infer<typeof revokeAppAccessSchema>;
export type SessionDataSchema = z.infer<typeof sessionSchema>;
export type OAuthCallbackSchema = z.infer<typeof oauthCallbackSchema>;
export type TwoFactorSetupSchema = z.infer<typeof twoFactorSetupSchema>;
export type TwoFactorVerifySchema = z.infer<typeof twoFactorVerifySchema>;
export type ApiKeyCreateSchema = z.infer<typeof apiKeyCreateSchema>;
export type ApiKeyRevokeSchema = z.infer<typeof apiKeyRevokeSchema>;
export type AuditLogQuerySchema = z.infer<typeof auditLogQuerySchema>;