import { PolarService } from './polar-service'
import { PolarWebhookEvent } from './types'
import { z } from 'zod'

// Webhook event types that Polar supports
export enum PolarWebhookEventType {
  // Subscription events
  SUBSCRIPTION_CREATED = 'subscription.created',
  SUBSCRIPTION_UPDATED = 'subscription.updated',
  SUBSCRIPTION_CANCELED = 'subscription.canceled',
  SUBSCRIPTION_ACTIVE = 'subscription.active',
  SUBSCRIPTION_PAST_DUE = 'subscription.past_due',
  
  // Order/Payment events
  ORDER_CREATED = 'order.created',
  ORDER_UPDATED = 'order.updated',
  ORDER_FULFILLED = 'order.fulfilled',
  ORDER_CANCELED = 'order.canceled',
  
  // Customer events
  CUSTOMER_CREATED = 'customer.created',
  CUSTOMER_UPDATED = 'customer.updated',
  
  // Checkout events
  CHECKOUT_CREATED = 'checkout.created',
  CHECKOUT_UPDATED = 'checkout.updated',
  CHECKOUT_SUCCEEDED = 'checkout.succeeded',
  CHECKOUT_FAILED = 'checkout.failed',
  
  // Product events
  PRODUCT_CREATED = 'product.created',
  PRODUCT_UPDATED = 'product.updated',
  
  // Benefit events
  BENEFIT_CREATED = 'benefit.created',
  BENEFIT_GRANTED = 'benefit.granted',
  BENEFIT_REVOKED = 'benefit.revoked'
}

// Webhook handler function type
export type WebhookHandlerFn = (event: PolarWebhookEvent) => Promise<void> | void

// Webhook processing options
export interface WebhookProcessingOptions {
  verifySignature?: boolean
  logEvents?: boolean
  retryFailedEvents?: boolean
  maxRetries?: number
}

/**
 * Webhook Handler for Polar
 * Processes incoming webhooks and routes them to appropriate handlers
 */
export class WebhookHandler {
  private polar: PolarService
  private handlers: Map<string, WebhookHandlerFn[]> = new Map()
  private options: WebhookProcessingOptions

  constructor(polar: PolarService, options: WebhookProcessingOptions = {}) {
    this.polar = polar
    this.options = {
      verifySignature: true,
      logEvents: true,
      retryFailedEvents: true,
      maxRetries: 3,
      ...options
    }
  }

  /**
   * Register a webhook event handler
   */
  on(eventType: PolarWebhookEventType | string, handler: WebhookHandlerFn): void {
    if (!this.handlers.has(eventType)) {
      this.handlers.set(eventType, [])
    }
    this.handlers.get(eventType)!.push(handler)
  }

  /**
   * Remove a webhook event handler
   */
  off(eventType: PolarWebhookEventType | string, handler?: WebhookHandlerFn): void {
    if (!handler) {
      this.handlers.delete(eventType)
      return
    }

    const handlers = this.handlers.get(eventType)
    if (handlers) {
      const index = handlers.indexOf(handler)
      if (index > -1) {
        handlers.splice(index, 1)
      }
    }
  }

  /**
   * Process incoming webhook
   */
  async processWebhook(
    payload: string | Buffer,
    signature: string,
    secret?: string
  ): Promise<{
    success: boolean
    event?: PolarWebhookEvent
    error?: string
  }> {
    try {
      // Verify and construct webhook event
      const event = await this.polar.constructWebhookEvent(payload, signature, secret)
      
      if (this.options.logEvents) {
        console.log('📥 Polar webhook received:', {
          type: event.type,
          id: event.id,
          timestamp: event.created_at
        })
      }

      // Process the event
      await this.handleEvent(event)

      return {
        success: true,
        event
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error'
      
      if (this.options.logEvents) {
        console.error('❌ Polar webhook processing failed:', errorMessage)
      }

      return {
        success: false,
        error: errorMessage
      }
    }
  }

  /**
   * Handle individual webhook event
   */
  private async handleEvent(event: PolarWebhookEvent): Promise<void> {
    const handlers = this.handlers.get(event.type) || []
    
    if (handlers.length === 0) {
      if (this.options.logEvents) {
        console.log(`⚠️ No handlers registered for event type: ${event.type}`)
      }
      return
    }

    // Execute all handlers for this event type
    const promises = handlers.map(handler => this.executeHandler(handler, event))
    
    try {
      await Promise.allSettled(promises)
    } catch (error) {
      console.error(`Failed to process webhook handlers for ${event.type}:`, error)
    }
  }

  /**
   * Execute a single handler with error handling and retries
   */
  private async executeHandler(handler: WebhookHandlerFn, event: PolarWebhookEvent): Promise<void> {
    const maxRetries = this.options.retryFailedEvents ? (this.options.maxRetries || 3) : 0
    let attempt = 0
    
    while (attempt <= maxRetries) {
      try {
        await handler(event)
        return // Success, exit retry loop
      } catch (error) {
        attempt++
        const errorMessage = error instanceof Error ? error.message : 'Unknown error'
        
        if (attempt > maxRetries) {
          console.error(`❌ Handler failed after ${maxRetries} retries for event ${event.type}:`, errorMessage)
          throw error
        }
        
        if (this.options.logEvents) {
          console.log(`🔄 Retrying handler for event ${event.type} (attempt ${attempt}/${maxRetries})`)
        }
        
        // Wait before retrying (exponential backoff)
        await new Promise(resolve => setTimeout(resolve, Math.pow(2, attempt) * 1000))
      }
    }
  }

  /**
   * Register common Stack 2025 webhook handlers
   */
  registerDefaultHandlers(): void {
    // Subscription lifecycle handlers
    this.on(PolarWebhookEventType.SUBSCRIPTION_CREATED, async (event) => {
      console.log('🎉 New subscription created:', event.data.object.id)
      // Update database with new subscription
      // Send welcome email
      // Grant access to features
    })

    this.on(PolarWebhookEventType.SUBSCRIPTION_CANCELED, async (event) => {
      console.log('❌ Subscription canceled:', event.data.object.id)
      // Update database subscription status
      // Revoke access to premium features
      // Send cancellation confirmation
    })

    this.on(PolarWebhookEventType.SUBSCRIPTION_UPDATED, async (event) => {
      console.log('🔄 Subscription updated:', event.data.object.id)
      // Handle plan changes, billing updates, etc.
      // Update feature access based on new plan
    })

    // Checkout handlers
    this.on(PolarWebhookEventType.CHECKOUT_SUCCEEDED, async (event) => {
      console.log('✅ Checkout succeeded:', event.data.object.id)
      // Activate subscription
      // Send receipt email
      // Grant immediate access
    })

    this.on(PolarWebhookEventType.CHECKOUT_FAILED, async (event) => {
      console.log('❌ Checkout failed:', event.data.object.id)
      // Log failure reason
      // Send notification to customer
      // Clean up incomplete records
    })

    // Order/Payment handlers
    this.on(PolarWebhookEventType.ORDER_FULFILLED, async (event) => {
      console.log('📦 Order fulfilled:', event.data.object.id)
      // Update order status in database
      // Send fulfillment notification
      // Update analytics
    })

    // Customer handlers
    this.on(PolarWebhookEventType.CUSTOMER_CREATED, async (event) => {
      console.log('👤 New customer created:', event.data.object.id)
      // Sync customer data with local database
      // Set up customer preferences
      // Send welcome sequence
    })
  }

  /**
   * Create handlers for BYOK (Bring Your Own Keys) events
   */
  registerBYOKHandlers(): void {
    this.on(PolarWebhookEventType.SUBSCRIPTION_CREATED, async (event) => {
      const subscription = event.data.object
      
      if (subscription.metadata?.byok === 'true') {
        console.log('🔑 BYOK subscription created:', subscription.id)
        // Send API key setup instructions
        // Create user onboarding flow
        // Set up BYOK-specific features
      }
    })

    this.on(PolarWebhookEventType.SUBSCRIPTION_UPDATED, async (event) => {
      const subscription = event.data.object
      
      if (subscription.metadata?.byok === 'true') {
        console.log('🔑 BYOK subscription updated:', subscription.id)
        // Update feature limits
        // Adjust API key permissions
        // Recalculate usage quotas
      }
    })
  }

  /**
   * Create app-specific handlers
   */
  registerAppHandlers(appId: string): void {
    const appPrefix = `[${appId.toUpperCase()}]`
    
    this.on(PolarWebhookEventType.SUBSCRIPTION_CREATED, async (event) => {
      const subscription = event.data.object
      
      if (subscription.metadata?.app === appId) {
        console.log(`${appPrefix} App subscription created:`, subscription.id)
        // Enable app-specific features
        // Set up app configuration
        // Initialize app data
      }
    })

    this.on(PolarWebhookEventType.SUBSCRIPTION_CANCELED, async (event) => {
      const subscription = event.data.object
      
      if (subscription.metadata?.app === appId) {
        console.log(`${appPrefix} App subscription canceled:`, subscription.id)
        // Disable app features
        // Archive app data
        // Clean up resources
      }
    })
  }

  /**
   * Get webhook statistics
   */
  getStats(): {
    registeredEventTypes: string[]
    totalHandlers: number
    handlerCounts: Record<string, number>
  } {
    const handlerCounts: Record<string, number> = {}
    let totalHandlers = 0
    
    for (const [eventType, handlers] of this.handlers.entries()) {
      handlerCounts[eventType] = handlers.length
      totalHandlers += handlers.length
    }
    
    return {
      registeredEventTypes: Array.from(this.handlers.keys()),
      totalHandlers,
      handlerCounts
    }
  }

  /**
   * Clear all handlers (useful for testing)
   */
  clearAllHandlers(): void {
    this.handlers.clear()
  }

  /**
   * Validate webhook event structure
   */
  private validateWebhookEvent(event: any): PolarWebhookEvent {
    const schema = z.object({
      id: z.string(),
      type: z.string(),
      data: z.object({
        object: z.any()
      }),
      created_at: z.string()
    })

    return schema.parse(event)
  }

  /**
   * Test webhook handler (for development)
   */
  async testWebhook(eventType: PolarWebhookEventType, testData: any): Promise<void> {
    const testEvent: PolarWebhookEvent = {
      id: `test_${Date.now()}`,
      type: eventType,
      data: {
        object: testData
      },
      created_at: new Date().toISOString()
    }

    console.log('🧪 Testing webhook event:', eventType)
    await this.handleEvent(testEvent)
  }
}