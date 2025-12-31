/**
 * @stack-2025/subscription-tiers
 * Unified subscription tier management for Stack 2025
 * 
 * Feature-based pricing with BYOK (Bring Your Own Keys)
 * Mini ($19), Standard ($49), Pro ($149), Corporate ($399)
 */

import { z } from 'zod';
import Stripe from 'stripe';
import { PrismaClient } from '@prisma/client';

// Subscription Tiers
export enum SubscriptionTier {
  MINI = 'mini',
  STANDARD = 'standard',
  PRO = 'pro',
  CORPORATE = 'corporate'
}

// Application Access by Tier
export const TierApplications = {
  [SubscriptionTier.MINI]: ['productivity-hub', 'invoice-gym'],
  [SubscriptionTier.STANDARD]: ['productivity-hub', 'invoice-gym', 'cc-light'],
  [SubscriptionTier.PRO]: ['productivity-hub', 'invoice-gym', 'cc-light', 'cc-gym', 'script-factory'],
  [SubscriptionTier.CORPORATE]: ['all']
} as const;

// Feature Limits by Tier
export const TierLimits = {
  [SubscriptionTier.MINI]: {
    aiRequests: 1000,
    callMinutes: 100,
    invoices: 25,
    scripts: 10,
    teamMembers: 1,
    storage: 1, // GB
    apiCalls: 5000
  },
  [SubscriptionTier.STANDARD]: {
    aiRequests: 5000,
    callMinutes: 500,
    invoices: 100,
    scripts: 50,
    teamMembers: 5,
    storage: 10,
    apiCalls: 25000
  },
  [SubscriptionTier.PRO]: {
    aiRequests: 25000,
    callMinutes: 2000,
    invoices: 500,
    scripts: 200,
    teamMembers: 25,
    storage: 100,
    apiCalls: 100000
  },
  [SubscriptionTier.CORPORATE]: {
    aiRequests: -1, // Unlimited
    callMinutes: -1,
    invoices: -1,
    scripts: -1,
    teamMembers: -1,
    storage: -1,
    apiCalls: -1
  }
} as const;

// Pricing Configuration
export const TierPricing = {
  [SubscriptionTier.MINI]: {
    monthly: 1900, // $19.00 in cents
    yearly: 19000, // $190.00 (2 months free)
    stripePriceIds: {
      monthly: process.env.STRIPE_PRICE_MINI_MONTHLY,
      yearly: process.env.STRIPE_PRICE_MINI_YEARLY
    }
  },
  [SubscriptionTier.STANDARD]: {
    monthly: 4900,
    yearly: 49000,
    stripePriceIds: {
      monthly: process.env.STRIPE_PRICE_STANDARD_MONTHLY,
      yearly: process.env.STRIPE_PRICE_STANDARD_YEARLY
    }
  },
  [SubscriptionTier.PRO]: {
    monthly: 14900,
    yearly: 149000,
    stripePriceIds: {
      monthly: process.env.STRIPE_PRICE_PRO_MONTHLY,
      yearly: process.env.STRIPE_PRICE_PRO_YEARLY
    }
  },
  [SubscriptionTier.CORPORATE]: {
    monthly: 39900,
    yearly: 399000,
    stripePriceIds: {
      monthly: process.env.STRIPE_PRICE_CORPORATE_MONTHLY,
      yearly: process.env.STRIPE_PRICE_CORPORATE_YEARLY
    }
  }
} as const;

// Subscription Manager Class
export class SubscriptionManager {
  private stripe: Stripe;
  private prisma: PrismaClient;

  constructor(stripeKey: string) {
    this.stripe = new Stripe(stripeKey, {
      apiVersion: '2023-10-16'
    });
    this.prisma = new PrismaClient();
  }

  /**
   * Create a new subscription
   */
  async createSubscription(
    userId: string,
    tier: SubscriptionTier,
    billingCycle: 'monthly' | 'yearly',
    paymentMethodId?: string
  ) {
    try {
      // Get or create Stripe customer
      let subscription = await this.prisma.userSubscription.findUnique({
        where: { userId }
      });

      let customerId = subscription?.stripeCustomerId;

      if (!customerId) {
        const customer = await this.stripe.customers.create({
          metadata: { userId }
        });
        customerId = customer.id;
      }

      // Attach payment method if provided
      if (paymentMethodId) {
        await this.stripe.paymentMethods.attach(paymentMethodId, {
          customer: customerId
        });
        await this.stripe.customers.update(customerId, {
          invoice_settings: {
            default_payment_method: paymentMethodId
          }
        });
      }

      // Create Stripe subscription
      const priceId = TierPricing[tier].stripePriceIds[billingCycle];
      if (!priceId) {
        throw new Error(`Price ID not configured for ${tier} ${billingCycle}`);
      }

      const stripeSubscription = await this.stripe.subscriptions.create({
        customer: customerId,
        items: [{ price: priceId }],
        trial_period_days: tier === SubscriptionTier.MINI ? 7 : 14,
        metadata: { userId, tier }
      });

      // Save to database
      const dbSubscription = await this.prisma.userSubscription.upsert({
        where: { userId },
        create: {
          userId,
          tier,
          stripeCustomerId: customerId,
          stripePriceId: priceId,
          status: stripeSubscription.status,
          startDate: new Date(stripeSubscription.current_period_start * 1000),
          endDate: new Date(stripeSubscription.current_period_end * 1000),
          trialEndsAt: stripeSubscription.trial_end 
            ? new Date(stripeSubscription.trial_end * 1000)
            : null,
          features: TierApplications[tier],
          limits: TierLimits[tier]
        },
        update: {
          tier,
          stripePriceId: priceId,
          status: stripeSubscription.status,
          features: TierApplications[tier],
          limits: TierLimits[tier]
        }
      });

      return {
        subscription: dbSubscription,
        stripeSubscription
      };
    } catch (error) {
      console.error('Failed to create subscription:', error);
      throw error;
    }
  }

  /**
   * Upgrade or downgrade subscription
   */
  async changeSubscription(
    userId: string,
    newTier: SubscriptionTier,
    billingCycle: 'monthly' | 'yearly'
  ) {
    const subscription = await this.prisma.userSubscription.findUnique({
      where: { userId }
    });

    if (!subscription || !subscription.stripeCustomerId) {
      throw new Error('No active subscription found');
    }

    // Get current Stripe subscription
    const subscriptions = await this.stripe.subscriptions.list({
      customer: subscription.stripeCustomerId,
      status: 'active',
      limit: 1
    });

    if (subscriptions.data.length === 0) {
      throw new Error('No active Stripe subscription found');
    }

    const stripeSubscription = subscriptions.data[0];
    const newPriceId = TierPricing[newTier].stripePriceIds[billingCycle];

    if (!newPriceId) {
      throw new Error(`Price ID not configured for ${newTier} ${billingCycle}`);
    }

    // Update Stripe subscription
    const updated = await this.stripe.subscriptions.update(
      stripeSubscription.id,
      {
        items: [{
          id: stripeSubscription.items.data[0].id,
          price: newPriceId
        }],
        proration_behavior: 'create_prorations'
      }
    );

    // Update database
    const dbSubscription = await this.prisma.userSubscription.update({
      where: { userId },
      data: {
        tier: newTier,
        stripePriceId: newPriceId,
        features: TierApplications[newTier],
        limits: TierLimits[newTier],
        updatedAt: new Date()
      }
    });

    return {
      subscription: dbSubscription,
      stripeSubscription: updated
    };
  }

  /**
   * Cancel subscription
   */
  async cancelSubscription(
    userId: string,
    immediate: boolean = false
  ) {
    const subscription = await this.prisma.userSubscription.findUnique({
      where: { userId }
    });

    if (!subscription || !subscription.stripeCustomerId) {
      throw new Error('No active subscription found');
    }

    // Get Stripe subscription
    const subscriptions = await this.stripe.subscriptions.list({
      customer: subscription.stripeCustomerId,
      status: 'active',
      limit: 1
    });

    if (subscriptions.data.length === 0) {
      throw new Error('No active Stripe subscription found');
    }

    // Cancel in Stripe
    const canceled = immediate
      ? await this.stripe.subscriptions.cancel(subscriptions.data[0].id)
      : await this.stripe.subscriptions.update(subscriptions.data[0].id, {
          cancel_at_period_end: true
        });

    // Update database
    const dbSubscription = await this.prisma.userSubscription.update({
      where: { userId },
      data: {
        status: immediate ? 'canceled' : 'canceling',
        endDate: immediate ? new Date() : subscription.endDate
      }
    });

    return {
      subscription: dbSubscription,
      stripeSubscription: canceled
    };
  }

  /**
   * Check if user has access to an application
   */
  async hasAppAccess(
    userId: string,
    appName: string
  ): Promise<boolean> {
    const subscription = await this.prisma.userSubscription.findUnique({
      where: { userId }
    });

    if (!subscription || subscription.status !== 'active') {
      return false;
    }

    const apps = TierApplications[subscription.tier as SubscriptionTier];
    return apps.includes('all') || apps.includes(appName);
  }

  /**
   * Check usage against limits
   */
  async checkUsage(
    userId: string,
    feature: keyof typeof TierLimits.mini
  ): Promise<{ allowed: boolean; usage: number; limit: number }> {
    const subscription = await this.prisma.userSubscription.findUnique({
      where: { userId }
    });

    if (!subscription) {
      return { allowed: false, usage: 0, limit: 0 };
    }

    const limits = subscription.limits as any;
    const limit = limits[feature] || 0;

    // Unlimited (-1) always allowed
    if (limit === -1) {
      return { allowed: true, usage: 0, limit: -1 };
    }

    // Get current usage
    const usage = await this.prisma.subscriptionUsage.aggregate({
      where: {
        userId,
        feature: feature as string,
        periodStart: {
          gte: new Date(new Date().setDate(1)) // Start of month
        }
      },
      _sum: { usage: true }
    });

    const currentUsage = usage._sum.usage || 0;

    return {
      allowed: currentUsage < limit,
      usage: currentUsage,
      limit
    };
  }

  /**
   * Track feature usage
   */
  async trackUsage(
    userId: string,
    feature: string,
    amount: number = 1
  ) {
    const subscription = await this.prisma.userSubscription.findUnique({
      where: { userId }
    });

    if (!subscription) {
      throw new Error('No subscription found');
    }

    const now = new Date();
    const periodStart = new Date(now.getFullYear(), now.getMonth(), 1);
    const periodEnd = new Date(now.getFullYear(), now.getMonth() + 1, 0);

    await this.prisma.subscriptionUsage.create({
      data: {
        userId,
        tier: subscription.tier,
        feature,
        usage: amount,
        limit: (subscription.limits as any)[feature] || 0,
        period: 'monthly',
        periodStart,
        periodEnd
      }
    });
  }

  /**
   * Get subscription details
   */
  async getSubscription(userId: string) {
    const subscription = await this.prisma.userSubscription.findUnique({
      where: { userId }
    });

    if (!subscription) {
      return null;
    }

    // Get current usage
    const usage = await this.prisma.subscriptionUsage.groupBy({
      by: ['feature'],
      where: {
        userId,
        periodStart: {
          gte: new Date(new Date().setDate(1))
        }
      },
      _sum: { usage: true }
    });

    const usageMap = usage.reduce((acc, curr) => {
      acc[curr.feature] = curr._sum.usage || 0;
      return acc;
    }, {} as Record<string, number>);

    return {
      ...subscription,
      currentUsage: usageMap
    };
  }

  /**
   * Handle Stripe webhook
   */
  async handleWebhook(event: Stripe.Event) {
    switch (event.type) {
      case 'customer.subscription.created':
      case 'customer.subscription.updated':
        const subscription = event.data.object as Stripe.Subscription;
        const userId = subscription.metadata.userId;
        
        if (userId) {
          await this.prisma.userSubscription.update({
            where: { userId },
            data: {
              status: subscription.status,
              startDate: new Date(subscription.current_period_start * 1000),
              endDate: new Date(subscription.current_period_end * 1000)
            }
          });
        }
        break;

      case 'customer.subscription.deleted':
        const deleted = event.data.object as Stripe.Subscription;
        const deletedUserId = deleted.metadata.userId;
        
        if (deletedUserId) {
          await this.prisma.userSubscription.update({
            where: { userId: deletedUserId },
            data: {
              status: 'canceled',
              endDate: new Date()
            }
          });
        }
        break;

      case 'invoice.payment_succeeded':
        const invoice = event.data.object as Stripe.Invoice;
        console.log('Payment succeeded for invoice:', invoice.id);
        break;

      case 'invoice.payment_failed':
        const failedInvoice = event.data.object as Stripe.Invoice;
        console.error('Payment failed for invoice:', failedInvoice.id);
        // TODO: Send notification to user
        break;
    }
  }

  /**
   * Cleanup resources
   */
  async cleanup() {
    await this.prisma.$disconnect();
  }
}

// Export helper functions
export function getTierFeatures(tier: SubscriptionTier) {
  return {
    applications: TierApplications[tier],
    limits: TierLimits[tier],
    pricing: TierPricing[tier]
  };
}

export function canAccessApp(tier: SubscriptionTier, appName: string): boolean {
  const apps = TierApplications[tier];
  return apps.includes('all') || apps.includes(appName);
}

export function isUnlimited(tier: SubscriptionTier, feature: keyof typeof TierLimits.mini): boolean {
  return TierLimits[tier][feature] === -1;
}