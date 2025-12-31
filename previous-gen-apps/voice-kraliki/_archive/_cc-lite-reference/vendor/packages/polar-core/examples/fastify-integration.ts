/**
 * Example: Polar integration with Fastify (replacing Stripe)
 * 
 * This example shows how to integrate @stack-2025/polar-core
 * with a Fastify application, similar to existing CC Light payment routes
 */

import { FastifyInstance, FastifyRequest, FastifyReply } from 'fastify';
import { 
  PolarService, 
  WebhookHandler, 
  PolarWebhookEventType,
  CheckoutSessionOptions 
} from '@stack-2025/polar-core';
import { z } from 'zod';

// Initialize Polar services
const polar = new PolarService(
  process.env.POLAR_ACCESS_TOKEN!,
  process.env.POLAR_WEBHOOK_SECRET
);

const webhooks = new WebhookHandler(polar);

// Register webhook handlers
webhooks.registerDefaultHandlers();
webhooks.registerBYOKHandlers();
webhooks.registerAppHandlers('cc-light');

// Request schemas
const CreateCheckoutSchema = z.object({
  productId: z.string(),
  quantity: z.number().optional().default(1),
  customerId: z.string().optional(),
  metadata: z.record(z.string()).optional(),
  trialDays: z.number().optional()
});

const CreatePortalSchema = z.object({
  customerId: z.string()
});

export default async function polarPaymentRoutes(fastify: FastifyInstance) {
  
  // Create checkout session - Direct replacement for Stripe
  fastify.post('/api/payments/checkout', async (request: FastifyRequest, reply: FastifyReply) => {
    try {
      const body = CreateCheckoutSchema.parse(request.body);
      const user = (request as any).user; // From auth middleware
      
      // Get or create Polar customer (replacing Stripe customer logic)
      let customerId = body.customerId || user?.polarCustomerId;
      
      if (!customerId && user) {
        const customer = await polar.createCustomer({
          email: user.email,
          name: user.name,
          metadata: {
            userId: user.id,
            app: 'cc-light',
            source: 'checkout'
          }
        });
        customerId = customer.id;
        
        // Save customer ID to database
        await fastify.databaseService.updateUser(user.id, {
          polarCustomerId: customerId // Updated field name
        });
      }
      
      // Create checkout session (similar API to Stripe)
      const session = await polar.createCheckoutSession({
        customerId,
        productId: body.productId, // Note: productId instead of priceId
        successUrl: process.env.POLAR_SUCCESS_URL || `${process.env.FRONTEND_URL}/dashboard?subscribed=true`,
        cancelUrl: process.env.POLAR_CANCEL_URL || `${process.env.FRONTEND_URL}/pricing`,
        metadata: {
          ...body.metadata,
          app: 'cc-light',
          userId: user?.id,
          created_via: 'api'
        },
        trialDays: body.trialDays || 14 // 14-day trial for new subscriptions
      });
      
      console.log('📦 Polar checkout session created', {
        sessionId: session.id,
        customerId,
        productId: body.productId,
        url: session.url
      });
      
      return { url: session.url };
      
    } catch (error) {
      console.error('❌ Failed to create Polar checkout session', error as Error);
      reply.code(500).send({ error: 'Failed to create checkout session' });
    }
  });
  
  // Create customer portal session - Direct replacement for Stripe
  fastify.post('/api/payments/portal', async (request: FastifyRequest, reply: FastifyReply) => {
    try {
      const user = (request as any).user;
      const body = CreatePortalSchema.parse(request.body);
      
      const customerId = body.customerId || user?.polarCustomerId;
      
      if (!customerId) {
        return reply.code(400).send({ error: 'No Polar customer found' });
      }
      
      const session = await polar.createPortalSession({
        customerId,
        returnUrl: process.env.POLAR_PORTAL_RETURN_URL || `${process.env.FRONTEND_URL}/settings`
      });
      
      console.log('🏛️ Polar portal session created', {
        customerId,
        sessionId: session.id,
        url: session.url
      });
      
      return { url: session.url };
      
    } catch (error) {
      console.error('❌ Failed to create Polar portal session', error as Error);
      reply.code(500).send({ error: 'Failed to create portal session' });
    }
  });
  
  // Get subscription status - Compatible with existing frontend
  fastify.get('/api/payments/subscription', async (request: FastifyRequest, reply: FastifyReply) => {
    try {
      const user = (request as any).user;
      
      if (!user?.polarCustomerId) {
        return { 
          active: false, 
          tier: 'free',
          message: 'No subscription found' 
        };
      }
      
      const status = await polar.getSubscriptionStatus(user.polarCustomerId);
      
      return {
        active: status.active,
        tier: status.tier || 'free',
        currentPeriodEnd: status.currentPeriodEnd,
        trialEnd: status.trialEnd,
        cancelAtPeriodEnd: status.cancelAtPeriodEnd
      };
      
    } catch (error) {
      console.error('❌ Failed to get Polar subscription status', error as Error);
      reply.code(500).send({ error: 'Failed to get subscription status' });
    }
  });

  // List customer subscriptions - New endpoint for enhanced functionality
  fastify.get('/api/payments/subscriptions', async (request: FastifyRequest, reply: FastifyReply) => {
    try {
      const user = (request as any).user;
      
      if (!user?.polarCustomerId) {
        return { subscriptions: [] };
      }
      
      const subscriptions = await polar.listSubscriptions(user.polarCustomerId);
      
      return {
        subscriptions: subscriptions.map(sub => ({
          id: sub.id,
          tier: sub.tier,
          status: sub.status,
          currentPeriodStart: sub.currentPeriodStart,
          currentPeriodEnd: sub.currentPeriodEnd,
          trialEnd: sub.trialEnd,
          cancelAtPeriodEnd: sub.cancelAtPeriodEnd
        }))
      };
      
    } catch (error) {
      console.error('❌ Failed to list Polar subscriptions', error as Error);
      reply.code(500).send({ error: 'Failed to list subscriptions' });
    }
  });
  
  // Polar webhook handler - Replaces Stripe webhook
  fastify.post('/api/payments/webhook', 
    {
      config: {
        rawBody: true // Need raw body for Polar signature verification
      }
    },
    async (request: FastifyRequest, reply: FastifyReply) => {
      try {
        const signature = request.headers['polar-signature'] as string;
        const rawBody = (request as any).rawBody;
        
        if (!signature || !rawBody) {
          return reply.code(400).send({ error: 'Missing signature or body' });
        }
        
        const result = await webhooks.processWebhook(
          rawBody,
          signature,
          process.env.POLAR_WEBHOOK_SECRET!
        );
        
        if (!result.success) {
          console.error('❌ Polar webhook processing failed:', result.error);
          return reply.code(400).send({ error: result.error });
        }
        
        const event = result.event!;
        
        console.log('📥 Polar webhook processed successfully', {
          type: event.type,
          id: event.id
        });
        
        // Handle specific events for CC Light
        switch (event.type) {
          case PolarWebhookEventType.CHECKOUT_SUCCEEDED: {
            const checkout = event.data.object;
            
            // Update user subscription in database
            if (checkout.metadata?.userId) {
              await fastify.databaseService.updateUser(checkout.metadata.userId, {
                subscriptionId: checkout.subscription_id,
                subscriptionStatus: 'active',
                subscribedAt: new Date(),
                subscriptionTier: checkout.metadata?.tier || 'standard'
              });
              
              console.log('✅ User subscription activated via Polar', {
                userId: checkout.metadata.userId,
                subscriptionId: checkout.subscription_id
              });
            }
            break;
          }
          
          case PolarWebhookEventType.SUBSCRIPTION_UPDATED: {
            const subscription = event.data.object;
            
            // Update subscription status
            if (subscription.metadata?.userId) {
              await fastify.databaseService.updateUser(subscription.metadata.userId, {
                subscriptionStatus: subscription.status,
                subscriptionEndDate: subscription.cancel_at_period_end 
                  ? new Date(subscription.current_period_end)
                  : null,
                subscriptionTier: subscription.metadata?.tier
              });
              
              console.log('🔄 User subscription updated via Polar', {
                userId: subscription.metadata.userId,
                status: subscription.status
              });
            }
            break;
          }
          
          case PolarWebhookEventType.SUBSCRIPTION_CANCELED: {
            const subscription = event.data.object;
            
            // Handle subscription cancellation
            if (subscription.metadata?.userId) {
              await fastify.databaseService.updateUser(subscription.metadata.userId, {
                subscriptionStatus: 'canceled',
                subscriptionEndDate: new Date(),
                subscriptionTier: 'free'
              });
              
              console.log('❌ User subscription canceled via Polar', {
                userId: subscription.metadata.userId
              });
            }
            break;
          }
        }
        
        return { received: true };
        
      } catch (error) {
        console.error('❌ Polar webhook processing failed', error as Error);
        reply.code(400).send({ error: 'Webhook processing failed' });
      }
    }
  );

  // Get available products - New endpoint for product catalog
  fastify.get('/api/payments/products', async (request: FastifyRequest, reply: FastifyReply) => {
    try {
      // In a real app, you'd fetch from Polar API or cache
      // For now, return the predefined CC Light products
      const products = [
        {
          id: 'prod_cc_light_starter',
          name: 'CC Light Starter',
          description: 'Perfect for small teams',
          features: [
            '5 agents',
            '100 calls/month', 
            'Basic reporting',
            'Email support'
          ],
          pricing: {
            monthly: { amount: 2900, currency: 'usd' },
            yearly: { amount: 29000, currency: 'usd', discount: '17%' }
          },
          metadata: {
            tier: 'starter',
            app: 'cc-light'
          }
        },
        {
          id: 'prod_cc_light_pro',
          name: 'CC Light Professional',
          description: 'For growing call centers',
          features: [
            '25 agents',
            'Unlimited calls',
            'Advanced analytics',
            'AI-powered insights',
            'Priority support'
          ],
          pricing: {
            monthly: { amount: 9900, currency: 'usd' },
            yearly: { amount: 99000, currency: 'usd', discount: '17%' }
          },
          metadata: {
            tier: 'professional',
            app: 'cc-light'
          }
        }
      ];
      
      return { products };
    } catch (error) {
      console.error('❌ Failed to get products', error as Error);
      reply.code(500).send({ error: 'Failed to get products' });
    }
  });
}

// CC Light Product Configuration for Polar
export const CC_LIGHT_POLAR_PRODUCTS = {
  starter: {
    id: 'prod_cc_light_starter',
    name: 'CC Light Starter',
    description: 'Perfect for small teams',
    features: [
      '5 agents',
      '100 calls/month',
      'Basic reporting',
      'Email support'
    ],
    pricing: {
      monthly: 'prod_cc_light_starter', // Polar uses product IDs
      yearly: 'prod_cc_light_starter_yearly'
    },
    metadata: {
      tier: 'starter',
      app: 'cc-light'
    }
  },
  professional: {
    id: 'prod_cc_light_pro',
    name: 'CC Light Professional',
    description: 'For growing call centers',
    features: [
      '25 agents',
      'Unlimited calls',
      'Advanced analytics',
      'AI-powered insights',
      'Priority support'
    ],
    pricing: {
      monthly: 'prod_cc_light_pro',
      yearly: 'prod_cc_light_pro_yearly'
    },
    metadata: {
      tier: 'professional',
      app: 'cc-light'
    }
  },
  enterprise: {
    id: 'prod_cc_light_enterprise',
    name: 'CC Light Enterprise',
    description: 'For large organizations',
    features: [
      'Unlimited agents',
      'Unlimited calls',
      'Custom integrations',
      'Dedicated support',
      'SLA guarantee'
    ],
    pricing: {
      monthly: 'prod_cc_light_enterprise',
      yearly: 'prod_cc_light_enterprise_yearly'
    },
    metadata: {
      tier: 'enterprise',
      app: 'cc-light'
    }
  }
};

// BYOK Products Configuration
export const BYOK_POLAR_PRODUCTS = {
  mini: {
    id: 'prod_byok_mini',
    name: 'BYOK Mini',
    description: 'Bring Your Own Keys - Mini Plan',
    appAccess: 2,
    pricing: {
      monthly: 'prod_byok_mini',
      yearly: 'prod_byok_mini_yearly'
    },
    metadata: {
      tier: 'mini',
      byok: 'true'
    }
  },
  standard: {
    id: 'prod_byok_standard',
    name: 'BYOK Standard', 
    description: 'Bring Your Own Keys - Standard Plan',
    appAccess: 5,
    pricing: {
      monthly: 'prod_byok_standard',
      yearly: 'prod_byok_standard_yearly'
    },
    metadata: {
      tier: 'standard',
      byok: 'true'
    }
  },
  pro: {
    id: 'prod_byok_pro',
    name: 'BYOK Pro',
    description: 'Bring Your Own Keys - Pro Plan', 
    appAccess: 10,
    pricing: {
      monthly: 'prod_byok_pro',
      yearly: 'prod_byok_pro_yearly'
    },
    metadata: {
      tier: 'pro',
      byok: 'true'
    }
  }
};