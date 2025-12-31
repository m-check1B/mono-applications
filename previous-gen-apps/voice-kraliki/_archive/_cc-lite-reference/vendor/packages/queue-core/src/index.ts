/**
 * @stack-2025/queue-core
 * RabbitMQ-based enterprise queue system
 *
 * This package provides the ONLY queue implementation for Stack 2025.
 * Bull has been completely removed in favor of RabbitMQ.
 *
 * Migration from Bull to RabbitMQ:
 * 1. Replace Bull queue instances with RabbitMQAdapter
 * 2. Update job processing to use consume() instead of process()
 * 3. Use publish() or sendToQueue() instead of add()
 * 4. Implement proper ack/nack/reject handling
 * 5. Set up exchanges and bindings for routing
 */

export { RabbitMQAdapter } from './adapters/rabbitmq.adapter';
export type { RabbitMQConfig } from './adapters/rabbitmq.adapter';

// Export all types
export type {
  QueueName,
  ExchangeName,
  QueueMessage,
  QueueOptions,
  ExchangeOptions,
  PublishOptions,
  ConsumerOptions,
  MessageHandler,
  QueueStats,
  CallEvent,
  TranscriptionEvent,
  AIProcessingRequest,
} from './types/queue.types';

// Re-export schemas
export { QueueMessageSchema } from './types/queue.types';

/**
 * Quick Start Guide:
 *
 * ```typescript
 * import { RabbitMQAdapter } from '@stack-2025/queue-core';
 *
 * // Initialize
 * const queue = new RabbitMQAdapter({
 *   url: 'amqp://localhost:5672',
 *   connectionName: 'cc-lite',
 *   prefetch: 10
 * });
 *
 * // Connect
 * await queue.connect();
 *
 * // Publish to exchange
 * await queue.publish('calls', 'call.inbound.new', {
 *   callId: '123',
 *   customerId: '456',
 *   timestamp: new Date()
 * });
 *
 * // Consume from queue
 * await queue.consume('inbound', async (message, ack, nack, reject) => {
 *   try {
 *     // Process message
 *     await processCall(message.payload);
 *     ack(); // Acknowledge success
 *   } catch (error) {
 *     if (error.retryable) {
 *       nack(true); // Requeue for retry
 *     } else {
 *       reject(false); // Send to dead letter queue
 *     }
 *   }
 * });
 * ```
 *
 * Why RabbitMQ over Bull:
 * - True distributed messaging across multiple services
 * - Advanced routing with exchanges and bindings
 * - Built-in dead letter queues
 * - Message persistence and durability
 * - Better monitoring and management tools
 * - Industry standard AMQP protocol
 * - Supports complex messaging patterns (pub/sub, RPC, routing)
 */

// Version and metadata
export const VERSION = '2.0.0';
export const QUEUE_ENGINE = 'RabbitMQ';
export const SUPPORTED_PATTERNS = ['work-queue', 'publish-subscribe', 'routing', 'topics', 'rpc'];

// Default configuration
export const DEFAULT_CONFIG = {
  RABBITMQ_URL: process.env.RABBITMQ_URL || 'amqp://localhost:5672',
  PREFETCH_COUNT: 10,
  HEARTBEAT_INTERVAL: 60,
  RECONNECT_DELAY: 5000,
  MAX_RETRY_ATTEMPTS: 5,
};