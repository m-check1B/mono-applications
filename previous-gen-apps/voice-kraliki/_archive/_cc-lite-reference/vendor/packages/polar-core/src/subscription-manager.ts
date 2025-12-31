import { PolarService } from './polar-service'
import { PolarSubscription, SubscriptionTier, BYOKPricingConfig } from './types'
import { z } from 'zod'

// Subscription management schemas
const createSubscriptionSchema = z.object({
  customerId: z.string(),
  productId: z.string(),
  priceId: z.string().optional(),
  trialDays: z.number().optional(),
  metadata: z.record(z.any()).optional(),
})

const updateSubscriptionSchema = z.object({
  productId: z.string().optional(),
  priceId: z.string().optional(),
  metadata: z.record(z.any()).optional(),
})

/**
 * Subscription Manager for Polar
 * Handles subscription lifecycle, upgrades, downgrades, and usage tracking
 */
export class SubscriptionManager {
  private polar: PolarService

  constructor(polar: PolarService) {
    this.polar = polar
  }

  /**
   * Create a new subscription
   */
  async createSubscription(data: {
    customerId: string
    productId: string
    priceId?: string
    trialDays?: number
    metadata?: Record<string, any>
  }): Promise<PolarSubscription> {
    const validated = createSubscriptionSchema.parse(data)
    
    try {
      // Placeholder for Polar subscription creation
      const subscriptionId = `sub_polar_${Date.now()}`;
      const now = new Date();
      const periodEnd = new Date(now.getTime() + 30 * 24 * 60 * 60 * 1000); // 30 days from now
      
      return {
        id: subscriptionId,
        subscriptionId,
        customerId: validated.customerId,
        tier: SubscriptionTier.STANDARD,
        status: 'active',
        currentPeriodStart: now,
        currentPeriodEnd: periodEnd,
        cancelAtPeriodEnd: false,
        trialStart: validated.trialDays ? now : undefined,
        trialEnd: validated.trialDays ? new Date(now.getTime() + validated.trialDays * 24 * 60 * 60 * 1000) : undefined,
        metadata: validated.metadata,
        createdAt: now,
        updatedAt: now
      }
    } catch (error) {
      throw new Error(`Failed to create subscription: ${error}`)
    }
  }

  /**
   * Update subscription (change plan, add metadata, etc.)
   */
  async updateSubscription(
    subscriptionId: string,
    updates: {
      productId?: string
      priceId?: string
      metadata?: Record<string, any>
    }
  ): Promise<PolarSubscription> {
    const validated = updateSubscriptionSchema.parse(updates)
    
    try {
      // Placeholder for Polar subscription update
      const now = new Date();
      const periodEnd = new Date(now.getTime() + 30 * 24 * 60 * 60 * 1000);
      
      return {
        id: subscriptionId,
        subscriptionId,
        customerId: 'placeholder_customer',
        tier: SubscriptionTier.STANDARD,
        status: 'active',
        currentPeriodStart: now,
        currentPeriodEnd: periodEnd,
        cancelAtPeriodEnd: false,
        metadata: validated.metadata,
        createdAt: now,
        updatedAt: now
      }
    } catch (error) {
      throw new Error(`Failed to update subscription: ${error}`)
    }
  }

  /**
   * Upgrade subscription to higher tier
   */
  async upgradeSubscription(
    subscriptionId: string,
    newProductId: string,
    prorate = true
  ): Promise<PolarSubscription> {
    try {
      return await this.updateSubscription(subscriptionId, {
        productId: newProductId,
        metadata: {
          upgraded_at: new Date().toISOString(),
          prorate: prorate.toString()
        }
      })
    } catch (error) {
      throw new Error(`Failed to upgrade subscription: ${error}`)
    }
  }

  /**
   * Downgrade subscription to lower tier
   */
  async downgradeSubscription(
    subscriptionId: string,
    newProductId: string,
    immediateChange = false
  ): Promise<PolarSubscription> {
    try {
      return await this.updateSubscription(subscriptionId, {
        productId: newProductId,
        metadata: {
          downgraded_at: new Date().toISOString(),
          immediate_change: immediateChange.toString()
        }
      })
    } catch (error) {
      throw new Error(`Failed to downgrade subscription: ${error}`)
    }
  }

  /**
   * Pause subscription (not directly supported by Polar, but we can track it)
   */
  async pauseSubscription(
    subscriptionId: string,
    pauseUntil?: Date
  ): Promise<PolarSubscription> {
    try {
      const subscription = await this.polar.listSubscriptions(subscriptionId);
      
      // In Polar, we can't directly pause, so we'll add metadata and handle in app logic
      return await this.updateSubscription(subscriptionId, {
        metadata: {
          paused_at: new Date().toISOString(),
          paused_until: pauseUntil?.toISOString(),
          status_before_pause: subscription[0]?.status || 'active'
        }
      })
    } catch (error) {
      throw new Error(`Failed to pause subscription: ${error}`)
    }
  }

  /**
   * Resume paused subscription
   */
  async resumeSubscription(subscriptionId: string): Promise<PolarSubscription> {
    try {
      return await this.updateSubscription(subscriptionId, {
        metadata: {
          resumed_at: new Date().toISOString(),
          paused_at: undefined,
          paused_until: undefined,
          status_before_pause: undefined
        }
      })
    } catch (error) {
      throw new Error(`Failed to resume subscription: ${error}`)
    }
  }

  /**
   * Cancel subscription
   */
  async cancelSubscription(
    subscriptionId: string,
    immediately = false,
    reason?: string
  ): Promise<PolarSubscription> {
    try {
      const canceledSubscription = await this.polar.cancelSubscription(
        subscriptionId,
        immediately
      )
      
      if (!canceledSubscription) {
        throw new Error('Subscription not found')
      }

      // Add cancellation metadata
      if (reason) {
        await this.updateSubscription(subscriptionId, {
          metadata: {
            canceled_at: new Date().toISOString(),
            cancellation_reason: reason,
            canceled_immediately: immediately.toString()
          }
        })
      }

      return canceledSubscription
    } catch (error) {
      throw new Error(`Failed to cancel subscription: ${error}`)
    }
  }

  /**
   * Reactivate canceled subscription
   */
  async reactivateSubscription(subscriptionId: string): Promise<PolarSubscription> {
    try {
      const reactivated = await this.polar.resumeSubscription(subscriptionId)
      
      if (!reactivated) {
        throw new Error('Subscription not found')
      }

      // Update metadata
      await this.updateSubscription(subscriptionId, {
        metadata: {
          reactivated_at: new Date().toISOString(),
          canceled_at: undefined,
          cancellation_reason: undefined
        }
      })

      return reactivated
    } catch (error) {
      throw new Error(`Failed to reactivate subscription: ${error}`)
    }
  }

  /**
   * Get subscription details with enhanced information
   */
  async getSubscriptionDetails(subscriptionId: string): Promise<{
    subscription: PolarSubscription
    isActive: boolean
    isInTrial: boolean
    isPaused: boolean
    daysTilRenewal: number
    usage?: any
  }> {
    try {
      const subscriptions = await this.polar.listSubscriptions(subscriptionId);
      const subscription = subscriptions.find(s => s.id === subscriptionId);
      
      if (!subscription) {
        throw new Error('Subscription not found')
      }

      const now = new Date()
      const isActive = ['active', 'trialing'].includes(subscription.status)
      const isInTrial = subscription.status === 'trialing' && 
                        !!subscription.trialEnd && 
                        subscription.trialEnd > now
      const isPaused = subscription.metadata?.paused_at !== undefined
      
      const daysTilRenewal = Math.ceil(
        (subscription.currentPeriodEnd.getTime() - now.getTime()) / 
        (1000 * 60 * 60 * 24)
      )

      return {
        subscription,
        isActive,
        isInTrial,
        isPaused,
        daysTilRenewal
      }
    } catch (error) {
      throw new Error(`Failed to get subscription details: ${error}`)
    }
  }

  /**
   * List all subscriptions for a customer with filtering
   */
  async listCustomerSubscriptions(
    customerId: string,
    filters?: {
      status?: string[]
      tier?: SubscriptionTier[]
      includeInactive?: boolean
    }
  ): Promise<PolarSubscription[]> {
    try {
      const subscriptions = await this.polar.listSubscriptions(customerId)
      
      if (!filters) {
        return subscriptions
      }

      return subscriptions.filter(subscription => {
        // Filter by status
        if (filters.status && !filters.status.includes(subscription.status)) {
          return false
        }

        // Filter by tier
        if (filters.tier && !filters.tier.includes(subscription.tier)) {
          return false
        }

        // Filter inactive subscriptions
        if (!filters.includeInactive && 
            !['active', 'trialing', 'past_due'].includes(subscription.status)) {
          return false
        }

        return true
      })
    } catch (error) {
      throw new Error(`Failed to list customer subscriptions: ${error}`)
    }
  }

  /**
   * Check if customer has access to specific features
   */
  async checkFeatureAccess(
    customerId: string,
    feature: string,
    appId?: string
  ): Promise<{
    hasAccess: boolean
    tier: string | null
    limits?: any
    usage?: any
  }> {
    try {
      const status = await this.polar.getSubscriptionStatus(customerId)
      
      if (!status.active) {
        return {
          hasAccess: false,
          tier: null
        }
      }

      // This would typically integrate with your feature access logic
      // based on subscription tiers and BYOK configurations
      
      return {
        hasAccess: true,
        tier: status.tier,
        limits: {
          // Example limits based on tier
          requests_per_month: status.tier === 'pro' ? 10000 : 1000,
          storage_gb: status.tier === 'pro' ? 100 : 10
        }
      }
    } catch (error) {
      throw new Error(`Failed to check feature access: ${error}`)
    }
  }

  /**
   * Extract subscription tier from metadata
   */
  private extractTierFromMetadata(metadata?: Record<string, any>): SubscriptionTier | null {
    if (!metadata) return null
    
    const tier = metadata.tier || metadata.subscription_tier
    if (!tier) return null
    
    // Normalize tier string to SubscriptionTier enum
    switch (tier.toLowerCase()) {
      case 'mini':
        return SubscriptionTier.MINI
      case 'standard':
        return SubscriptionTier.STANDARD
      case 'pro':
        return SubscriptionTier.PRO
      case 'corporate':
        return SubscriptionTier.CORPORATE
      default:
        return SubscriptionTier.STANDARD
    }
  }

  /**
   * Calculate prorated amount for subscription changes
   */
  calculateProratedAmount(
    currentPrice: number,
    newPrice: number,
    periodStart: Date,
    periodEnd: Date,
    changeDate: Date = new Date()
  ): number {
    const totalDays = Math.ceil(
      (periodEnd.getTime() - periodStart.getTime()) / (1000 * 60 * 60 * 24)
    )
    
    const remainingDays = Math.ceil(
      (periodEnd.getTime() - changeDate.getTime()) / (1000 * 60 * 60 * 24)
    )
    
    const proratedRefund = (currentPrice * remainingDays) / totalDays
    const proratedCharge = (newPrice * remainingDays) / totalDays
    
    return proratedCharge - proratedRefund
  }
}