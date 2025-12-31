/**
 * @stack-2025/byok-middleware
 * Express and tRPC middleware for BYOK integration
 */

import { Request, Response, NextFunction } from 'express';
import { TRPCError } from '@trpc/server';
import { createBYOKManager, BYOKProvider } from '@stack-2025/byok-core';
import { SubscriptionManager, SubscriptionTier } from '@stack-2025/subscription-tiers';

// Initialize managers
const byokManager = createBYOKManager({
  encryptionKey: process.env.BYOK_ENCRYPTION_KEY || '',
  redisUrl: process.env.REDIS_URL,
  cacheEnabled: true,
  auditingEnabled: true,
  fallbackEnabled: true
});

const subscriptionManager = new SubscriptionManager(
  process.env.STRIPE_SECRET_KEY || ''
);

// Extended request interface
export interface BYOKRequest extends Request {
  userId?: string;
  subscription?: {
    tier: SubscriptionTier;
    features: string[];
    limits: Record<string, number>;
  };
  byok?: {
    getKey: (provider: BYOKProvider) => Promise<string>;
    trackUsage: (provider: BYOKProvider, operation: string, metadata?: any) => Promise<void>;
  };
}

/**
 * Express middleware for BYOK
 */
export function byokMiddleware() {
  return async (req: BYOKRequest, res: Response, next: NextFunction) => {
    try {
      // Extract user ID from auth (assumes auth middleware has run)
      const userId = req.userId || (req as any).auth?.userId;
      
      if (!userId) {
        return next();
      }

      // Get subscription details
      const subscription = await subscriptionManager.getSubscription(userId);
      
      if (subscription) {
        req.subscription = {
          tier: subscription.tier as SubscriptionTier,
          features: subscription.features as string[],
          limits: subscription.limits as Record<string, number>
        };
      }

      // Add BYOK helper functions
      req.byok = {
        getKey: async (provider: BYOKProvider) => {
          return await byokManager.getProviderKey(userId, provider);
        },
        trackUsage: async (provider: BYOKProvider, operation: string, metadata?: any) => {
          await byokManager.trackUsage({
            keyId: '',
            userId,
            provider,
            operation,
            success: true,
            metadata
          });
        }
      };

      next();
    } catch (error) {
      console.error('BYOK middleware error:', error);
      next();
    }
  };
}

/**
 * Express middleware to check subscription tier
 */
export function requireTier(minTier: SubscriptionTier) {
  return async (req: BYOKRequest, res: Response, next: NextFunction) => {
    const tierOrder = {
      [SubscriptionTier.MINI]: 1,
      [SubscriptionTier.STANDARD]: 2,
      [SubscriptionTier.PRO]: 3,
      [SubscriptionTier.CORPORATE]: 4
    };

    if (!req.subscription) {
      return res.status(403).json({
        error: 'No active subscription',
        code: 'NO_SUBSCRIPTION'
      });
    }

    const userTierLevel = tierOrder[req.subscription.tier];
    const requiredTierLevel = tierOrder[minTier];

    if (userTierLevel < requiredTierLevel) {
      return res.status(403).json({
        error: `This feature requires ${minTier} tier or higher`,
        code: 'INSUFFICIENT_TIER',
        currentTier: req.subscription.tier,
        requiredTier: minTier
      });
    }

    next();
  };
}

/**
 * Express middleware to check app access
 */
export function requireApp(appName: string) {
  return async (req: BYOKRequest, res: Response, next: NextFunction) => {
    const userId = req.userId || (req as any).auth?.userId;
    
    if (!userId) {
      return res.status(401).json({
        error: 'Authentication required',
        code: 'UNAUTHORIZED'
      });
    }

    const hasAccess = await subscriptionManager.hasAppAccess(userId, appName);
    
    if (!hasAccess) {
      return res.status(403).json({
        error: `No access to ${appName}`,
        code: 'APP_ACCESS_DENIED',
        app: appName
      });
    }

    next();
  };
}

/**
 * Express middleware to check usage limits
 */
export function checkUsageLimit(feature: string) {
  return async (req: BYOKRequest, res: Response, next: NextFunction) => {
    const userId = req.userId || (req as any).auth?.userId;
    
    if (!userId) {
      return next();
    }

    const { allowed, usage, limit } = await subscriptionManager.checkUsage(
      userId,
      feature as any
    );

    if (!allowed) {
      return res.status(429).json({
        error: 'Usage limit exceeded',
        code: 'USAGE_LIMIT_EXCEEDED',
        feature,
        usage,
        limit
      });
    }

    // Track usage after successful request
    res.on('finish', async () => {
      if (res.statusCode < 400) {
        await subscriptionManager.trackUsage(userId, feature, 1);
      }
    });

    next();
  };
}

/**
 * tRPC middleware for BYOK
 */
export function createBYOKContext(userId: string) {
  return {
    byok: {
      getKey: async (provider: BYOKProvider) => {
        return await byokManager.getProviderKey(userId, provider);
      },
      trackUsage: async (provider: BYOKProvider, operation: string, metadata?: any) => {
        await byokManager.trackUsage({
          keyId: '',
          userId,
          provider,
          operation,
          success: true,
          metadata
        });
      },
      validateKey: async (provider: BYOKProvider) => {
        const keys = await byokManager.listKeys(userId);
        const providerKey = keys.find(k => k.provider === provider);
        if (providerKey) {
          const validations = await byokManager.validateUserKeys(userId);
          return validations.get(providerKey.id);
        }
        return null;
      }
    },
    subscription: {
      getTier: async () => {
        const sub = await subscriptionManager.getSubscription(userId);
        return sub?.tier as SubscriptionTier;
      },
      hasAccess: async (appName: string) => {
        return await subscriptionManager.hasAppAccess(userId, appName);
      },
      checkLimit: async (feature: string) => {
        return await subscriptionManager.checkUsage(userId, feature as any);
      },
      trackUsage: async (feature: string, amount: number = 1) => {
        return await subscriptionManager.trackUsage(userId, feature, amount);
      }
    }
  };
}

/**
 * tRPC procedure middleware for tier checking
 */
export function requireTierTRPC(minTier: SubscriptionTier) {
  return async (opts: any) => {
    const { ctx, next } = opts;
    
    if (!ctx.userId) {
      throw new TRPCError({
        code: 'UNAUTHORIZED',
        message: 'Authentication required'
      });
    }

    const subscription = await subscriptionManager.getSubscription(ctx.userId);
    
    if (!subscription) {
      throw new TRPCError({
        code: 'FORBIDDEN',
        message: 'No active subscription'
      });
    }

    const tierOrder = {
      [SubscriptionTier.MINI]: 1,
      [SubscriptionTier.STANDARD]: 2,
      [SubscriptionTier.PRO]: 3,
      [SubscriptionTier.CORPORATE]: 4
    };

    const userTierLevel = tierOrder[subscription.tier as SubscriptionTier];
    const requiredTierLevel = tierOrder[minTier];

    if (userTierLevel < requiredTierLevel) {
      throw new TRPCError({
        code: 'FORBIDDEN',
        message: `This feature requires ${minTier} tier or higher`
      });
    }

    return next({
      ...opts,
      ctx: {
        ...ctx,
        subscription
      }
    });
  };
}

/**
 * Helper to get API client with BYOK
 */
export async function getAIClient(
  userId: string,
  provider: BYOKProvider
) {
  const apiKey = await byokManager.getProviderKey(userId, provider);
  
  switch (provider) {
    case BYOKProvider.OPENAI:
      const { OpenAI } = await import('openai');
      return new OpenAI({ apiKey });
      
    case BYOKProvider.ANTHROPIC:
      const Anthropic = (await import('@anthropic-ai/sdk')).default;
      return new Anthropic({ apiKey });
      
    case BYOKProvider.DEEPGRAM:
      const { createClient } = await import('@deepgram/sdk');
      return createClient(apiKey);
      
    case BYOKProvider.TWILIO:
      const { Twilio } = await import('twilio');
      const [accountSid, authToken] = apiKey.split(':');
      return new Twilio(accountSid, authToken);
      
    default:
      throw new Error(`Unsupported provider: ${provider}`);
  }
}

// Export managers for direct use
export { byokManager, subscriptionManager };

// Re-export types
export * from '@stack-2025/byok-core';
export * from '@stack-2025/subscription-tiers';