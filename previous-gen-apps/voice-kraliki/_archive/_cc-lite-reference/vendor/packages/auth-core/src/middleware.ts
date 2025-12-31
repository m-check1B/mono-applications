/**
 * Authentication middleware factories for different frameworks
 */

import type { FastifyRequest, FastifyReply } from 'fastify';
import type { 
  AuthUser, 
  AppIdentifier, 
  Permission, 
  AccessTokenPayload,
  TokenService 
} from './types';

// Fastify middleware factory
export function createFastifyAuthMiddleware(
  tokenService: TokenService,
  getUserById: (id: string) => Promise<AuthUser | null>
) {
  return async function authMiddleware(
    request: FastifyRequest,
    reply: FastifyReply
  ) {
    try {
      // Extract token from header
      const authHeader = request.headers.authorization;
      if (!authHeader || !authHeader.startsWith('Bearer ')) {
        return reply.code(401).send({ error: 'No token provided' });
      }

      const token = authHeader.substring(7);
      
      // Verify token
      const payload = await tokenService.verify(token);
      if (!payload) {
        return reply.code(401).send({ error: 'Invalid token' });
      }

      // Get user
      const user = await getUserById(payload.sub);
      if (!user) {
        return reply.code(401).send({ error: 'User not found' });
      }

      // Attach to request
      (request as any).user = user;
      (request as any).tokenPayload = payload;
    } catch (error) {
      return reply.code(401).send({ error: 'Authentication failed' });
    }
  };
}

// App access middleware
export function createAppAccessMiddleware(appId: AppIdentifier) {
  return async function appAccessMiddleware(
    request: FastifyRequest,
    reply: FastifyReply
  ) {
    const user = (request as any).user as AuthUser;
    
    if (!user) {
      return reply.code(401).send({ error: 'Not authenticated' });
    }

    const hasAccess = user.apps.some(app => app.appId === appId);
    if (!hasAccess) {
      return reply.code(403).send({ 
        error: 'Access denied to this application' 
      });
    }
  };
}

// Permission middleware
export function createPermissionMiddleware(
  appId: AppIdentifier,
  requiredPermission: Permission
) {
  return async function permissionMiddleware(
    request: FastifyRequest,
    reply: FastifyReply
  ) {
    const user = (request as any).user as AuthUser;
    
    if (!user) {
      return reply.code(401).send({ error: 'Not authenticated' });
    }

    const appAccess = user.apps.find(app => app.appId === appId);
    if (!appAccess) {
      return reply.code(403).send({ 
        error: 'No access to this application' 
      });
    }

    // Check role-based permissions
    if (appAccess.role === 'owner') {
      return; // Owners have all permissions
    }

    if (appAccess.role === 'admin') {
      // Admins have most permissions
      if (requiredPermission !== 'manage_billing') {
        return;
      }
    }

    // Check specific permissions
    if (!appAccess.permissions.includes(requiredPermission)) {
      return reply.code(403).send({ 
        error: `Missing required permission: ${requiredPermission}` 
      });
    }
  };
}

// Express middleware factory (for compatibility)
export function createExpressAuthMiddleware(
  tokenService: TokenService,
  getUserById: (id: string) => Promise<AuthUser | null>
) {
  return async function authMiddleware(req: any, res: any, next: any) {
    try {
      const authHeader = req.headers.authorization;
      if (!authHeader || !authHeader.startsWith('Bearer ')) {
        return res.status(401).json({ error: 'No token provided' });
      }

      const token = authHeader.substring(7);
      const payload = await tokenService.verify(token);
      
      if (!payload) {
        return res.status(401).json({ error: 'Invalid token' });
      }

      const user = await getUserById(payload.sub);
      if (!user) {
        return res.status(401).json({ error: 'User not found' });
      }

      req.user = user;
      req.tokenPayload = payload;
      next();
    } catch (error) {
      return res.status(401).json({ error: 'Authentication failed' });
    }
  };
}

// CORS configuration for auth
export function createAuthCorsConfig(allowedOrigins: string[]) {
  return {
    origin: (origin: string | undefined, callback: any) => {
      if (!origin || allowedOrigins.includes(origin)) {
        callback(null, true);
      } else {
        callback(new Error('Not allowed by CORS'));
      }
    },
    credentials: true,
    methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
    allowedHeaders: ['Content-Type', 'Authorization'],
    exposedHeaders: ['X-Auth-Token', 'X-Refresh-Token']
  };
}

// Rate limiting middleware factory
export function createRateLimitMiddleware(
  maxAttempts: number = 5,
  windowMs: number = 15 * 60 * 1000 // 15 minutes
) {
  const attempts = new Map<string, { count: number; resetAt: number }>();

  return async function rateLimitMiddleware(
    request: FastifyRequest,
    reply: FastifyReply
  ) {
    const identifier = request.ip || 'unknown';
    const now = Date.now();
    
    const record = attempts.get(identifier);
    
    if (!record || record.resetAt < now) {
      attempts.set(identifier, { count: 1, resetAt: now + windowMs });
      return;
    }

    if (record.count >= maxAttempts) {
      const retryAfter = Math.ceil((record.resetAt - now) / 1000);
      return reply
        .code(429)
        .header('Retry-After', retryAfter)
        .send({ 
          error: 'Too many attempts. Please try again later.',
          retryAfter 
        });
    }

    record.count++;
  };
}

// Session validation middleware
export function createSessionMiddleware(
  validateSession: (token: string) => Promise<boolean>
) {
  return async function sessionMiddleware(
    request: FastifyRequest,
    reply: FastifyReply
  ) {
    const cookies = (request as any).cookies;
    const sessionToken = cookies?.sessionToken || 
                        request.headers['x-session-token'];
    
    if (!sessionToken) {
      return reply.code(401).send({ error: 'No session token' });
    }

    const isValid = await validateSession(sessionToken as string);
    if (!isValid) {
      return reply.code(401).send({ error: 'Invalid or expired session' });
    }
  };
}

// Audit logging middleware
export function createAuditMiddleware(
  logAudit: (data: any) => Promise<void>
) {
  return async function auditMiddleware(
    request: FastifyRequest,
    reply: FastifyReply
  ) {
    const user = (request as any).user;
    const startTime = Date.now();

    // Use a response hook alternative
    const replyRaw = reply as any;
    if (replyRaw.addHook) {
      replyRaw.addHook('onSend', async (req: any, rep: any, payload: any) => {
        await logAudit({
          action: request.method + ' ' + request.url,
          userId: user?.id || 'anonymous',
          timestamp: new Date(),
          duration: Date.now() - startTime,
          statusCode: reply.statusCode,
          ip: request.ip,
          userAgent: request.headers['user-agent']
        });
      });
    } else {
      // Fallback: log immediately if hook not available
      setTimeout(async () => {
        await logAudit({
          action: request.method + ' ' + request.url,
          userId: user?.id || 'anonymous',
          timestamp: new Date(),
          duration: Date.now() - startTime,
          statusCode: reply.statusCode,
          ip: request.ip,
          userAgent: request.headers['user-agent']
        });
      }, 0);
    }
  };
}