import { PolarService } from './polar-service'
import { PolarPayment, PolarOrder, PaymentStatus, CheckoutSessionOptions } from './types'
import { z } from 'zod'

// Payment processing schemas
const processPaymentSchema = z.object({
  customerId: z.string(),
  amount: z.number().positive(),
  currency: z.string().default('usd'),
  productId: z.string(),
  description: z.string().optional(),
  metadata: z.record(z.any()).optional(),
})

const createOrderSchema = z.object({
  customerId: z.string(),
  productId: z.string(),
  amount: z.number().positive(),
  currency: z.string().default('usd'),
  description: z.string().optional(),
  metadata: z.record(z.any()).optional(),
})

/**
 * Payment Processor for Polar
 * Handles one-time payments, orders, and payment processing
 */
export class PaymentProcessor {
  private polar: PolarService

  constructor(polar: PolarService) {
    this.polar = polar
  }

  /**
   * Create a checkout session for one-time payment
   */
  async createPaymentCheckout(options: {
    customerId?: string
    email?: string
    productId: string
    amount?: number // For custom amounts
    currency?: string
    successUrl: string
    cancelUrl?: string
    description?: string
    metadata?: Record<string, any>
  }): Promise<{ url: string; id: string }> {
    try {
      const checkoutOptions: CheckoutSessionOptions = {
        customerId: options.customerId,
        email: options.email,
        productId: options.productId,
        successUrl: options.successUrl,
        cancelUrl: options.cancelUrl,
        metadata: {
          ...options.metadata,
          payment_type: 'one_time',
          description: options.description,
          custom_amount: options.amount?.toString(),
          currency: options.currency || 'usd'
        }
      }

      return await this.polar.createCheckoutSession(checkoutOptions)
    } catch (error) {
      throw new Error(`Failed to create payment checkout: ${error}`)
    }
  }

  /**
   * Create an order (Polar's equivalent of payment intent)
   */
  async createOrder(data: {
    customerId: string
    productId: string
    amount: number
    currency?: string
    description?: string
    metadata?: Record<string, any>
  }): Promise<PolarOrder> {
    const validated = createOrderSchema.parse(data)
    
    try {
      // Placeholder for Polar order creation
      const orderId = `ord_polar_${Date.now()}`;
      
      return {
        id: orderId,
        orderId,
        customerId: validated.customerId,
        subscriptionId: undefined,
        amount: validated.amount,
        currency: validated.currency || 'usd',
        status: 'pending',
        billing_reason: 'manual',
        metadata: {
          ...validated.metadata,
          description: validated.description,
          created_by: 'payment_processor'
        },
        createdAt: new Date()
      }
    } catch (error) {
      throw new Error(`Failed to create order: ${error}`)
    }
  }

  /**
   * Process a payment (create order + initiate payment)
   */
  async processPayment(data: {
    customerId: string
    amount: number
    currency?: string
    productId: string
    description?: string
    metadata?: Record<string, any>
    successUrl: string
    cancelUrl?: string
  }): Promise<{
    orderId: string
    checkoutUrl: string
    status: PaymentStatus
  }> {
    const validated = processPaymentSchema.parse(data)
    
    try {
      // Step 1: Create the order
      const order = await this.createOrder({
        customerId: validated.customerId,
        productId: validated.productId,
        amount: validated.amount,
        currency: validated.currency,
        description: validated.description,
        metadata: validated.metadata
      })

      // Step 2: Create checkout session for payment
      const checkout = await this.createPaymentCheckout({
        customerId: validated.customerId,
        productId: validated.productId,
        successUrl: data.successUrl,
        cancelUrl: data.cancelUrl,
        description: validated.description,
        metadata: {
          ...validated.metadata,
          order_id: order.id
        }
      })

      return {
        orderId: order.id,
        checkoutUrl: checkout.url,
        status: PaymentStatus.PENDING
      }
    } catch (error) {
      throw new Error(`Failed to process payment: ${error}`)
    }
  }

  /**
   * Get payment status
   */
  async getPaymentStatus(orderId: string): Promise<{
    status: PaymentStatus
    amount: number
    currency: string
    paidAt?: Date
    failureReason?: string
  }> {
    try {
      // Placeholder for Polar order status check
      return {
        status: PaymentStatus.PENDING,
        amount: 0,
        currency: 'usd',
        paidAt: undefined,
        failureReason: undefined
      }
    } catch (error) {
      throw new Error(`Failed to get payment status: ${error}`)
    }
  }

  /**
   * List payments for a customer
   */
  async listCustomerPayments(
    customerId: string,
    options?: {
      status?: PaymentStatus[]
      limit?: number
      startDate?: Date
      endDate?: Date
    }
  ): Promise<PolarOrder[]> {
    try {
      // Placeholder for Polar orders list
      let orders: PolarOrder[] = []

      // Apply filters
      if (options?.status) {
        orders = orders.filter((order: PolarOrder) => 
          options.status?.includes(this.mapStatusToPaymentStatus(order.status))
        )
      }

      if (options?.startDate) {
        orders = orders.filter((order: PolarOrder) => order.createdAt >= options.startDate!)
      }

      if (options?.endDate) {
        orders = orders.filter((order: PolarOrder) => order.createdAt <= options.endDate!)
      }

      return orders
    } catch (error) {
      throw new Error(`Failed to list customer payments: ${error}`)
    }
  }

  /**
   * Process a refund (Note: Polar handles refunds through their system)
   */
  async processRefund(orderId: string, options?: {
    amount?: number
    reason?: string
    metadata?: Record<string, any>
  }): Promise<{
    refundId: string
    status: string
    amount: number
  }> {
    try {
      // Polar doesn't have a direct refund API endpoint
      // Refunds are typically processed through their dashboard
      // This is a placeholder implementation
      
      const refundId = `ref_polar_${Date.now()}`
      
      // Log the refund request for processing
      console.log('Refund requested for order:', {
        orderId,
        refundId,
        amount: options?.amount,
        reason: options?.reason,
        metadata: options?.metadata
      })

      // In a real implementation, you might:
      // 1. Create a database record for the refund request
      // 2. Send an email to administrators
      // 3. Integrate with Polar's webhook system for manual processing
      
      return {
        refundId,
        status: 'requested',
        amount: options?.amount || 0
      }
    } catch (error) {
      throw new Error(`Failed to process refund: ${error}`)
    }
  }

  /**
   * Calculate payment fees and taxes
   */
  calculatePaymentFees(amount: number, currency: string = 'usd'): {
    subtotal: number
    processingFee: number
    tax: number
    total: number
  } {
    // Polar's fee structure (approximate - check current rates)
    const processingFeeRate = 0.029 // 2.9% + $0.30
    const fixedFee = 30 // $0.30 in cents
    
    const subtotal = amount
    const processingFee = Math.round(amount * processingFeeRate + fixedFee)
    const tax = 0 // Tax calculation would depend on business location and rules
    const total = subtotal + processingFee + tax

    return {
      subtotal,
      processingFee,
      tax,
      total
    }
  }

  /**
   * Validate payment data
   */
  validatePaymentData(data: {
    amount: number
    currency: string
    customerId: string
    productId: string
  }): {
    isValid: boolean
    errors: string[]
  } {
    const errors: string[] = []

    // Amount validation
    if (data.amount <= 0) {
      errors.push('Amount must be greater than 0')
    }

    if (data.amount < 50) { // Minimum $0.50
      errors.push('Amount must be at least $0.50')
    }

    if (data.amount > 999999999) { // Maximum ~$10M
      errors.push('Amount exceeds maximum limit')
    }

    // Currency validation
    const supportedCurrencies = ['usd', 'eur', 'gbp', 'cad', 'aud']
    if (!supportedCurrencies.includes(data.currency.toLowerCase())) {
      errors.push(`Currency ${data.currency} is not supported`)
    }

    // Customer ID validation
    if (!data.customerId || data.customerId.trim().length === 0) {
      errors.push('Customer ID is required')
    }

    // Product ID validation
    if (!data.productId || data.productId.trim().length === 0) {
      errors.push('Product ID is required')
    }

    return {
      isValid: errors.length === 0,
      errors
    }
  }

  /**
   * Get payment analytics for a customer
   */
  async getPaymentAnalytics(customerId: string, period: {
    startDate: Date
    endDate: Date
  }): Promise<{
    totalAmount: number
    totalPayments: number
    successfulPayments: number
    failedPayments: number
    averageAmount: number
    currency: string
  }> {
    try {
      const payments = await this.listCustomerPayments(customerId, {
        startDate: period.startDate,
        endDate: period.endDate
      })

      const totalPayments = payments.length
      const successfulPayments = payments.filter(p => p.status === 'succeeded').length
      const failedPayments = payments.filter(p => p.status === 'failed').length
      
      const totalAmount = payments
        .filter(p => p.status === 'succeeded')
        .reduce((sum, payment) => sum + payment.amount, 0)
      
      const averageAmount = successfulPayments > 0 ? totalAmount / successfulPayments : 0
      
      // Get the most common currency
      const currencies = payments.map(p => p.currency)
      const currency = currencies.length > 0 ? currencies[0] : 'usd'

      return {
        totalAmount,
        totalPayments,
        successfulPayments,
        failedPayments,
        averageAmount,
        currency
      }
    } catch (error) {
      throw new Error(`Failed to get payment analytics: ${error}`)
    }
  }

  /**
   * Map Polar order status to PaymentStatus enum
   */
  private mapStatusToPaymentStatus(status: string): PaymentStatus {
    switch (status) {
      case 'pending':
        return PaymentStatus.PENDING
      case 'processing':
        return PaymentStatus.PROCESSING
      case 'succeeded':
      case 'paid':
        return PaymentStatus.SUCCEEDED
      case 'failed':
        return PaymentStatus.FAILED
      case 'refunded':
        return PaymentStatus.REFUNDED
      case 'canceled':
        return PaymentStatus.CANCELED
      default:
        return PaymentStatus.PENDING
    }
  }
}