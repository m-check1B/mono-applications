/**
 * RabbitMQ Adapter
 * Enterprise-grade message queue implementation
 *
 * This is the ONLY queue implementation in Stack 2025.
 * Bull has been completely removed in favor of RabbitMQ for:
 * - Better reliability and persistence
 * - True distributed messaging
 * - Advanced routing capabilities
 * - Dead letter queues
 * - Message TTL and priorities
 */

import * as amqp from 'amqplib';
import { EventEmitter } from 'eventemitter3';
import { v4 as uuidv4 } from 'uuid';
import type {
  QueueMessage,
  QueueOptions,
  ExchangeOptions,
  PublishOptions,
  ConsumerOptions,
  MessageHandler,
  QueueStats,
  QueueName,
  ExchangeName
} from '../types/queue.types';

export interface RabbitMQConfig {
  url: string;
  prefetch?: number;
  heartbeat?: number;
  connectionName?: string;
  retryAttempts?: number;
  retryDelay?: number;
}

export class RabbitMQAdapter extends EventEmitter {
  private connection: any = null;
  private channel: any = null;
  private config: RabbitMQConfig;
  private consumers: Map<string, string> = new Map();
  private reconnectTimer: NodeJS.Timeout | null = null;
  private isClosing = false;

  constructor(config: RabbitMQConfig) {
    super();
    this.config = {
      prefetch: 10,
      heartbeat: 60,
      connectionName: 'cc-lite-queue',
      retryAttempts: 5,
      retryDelay: 5000,
      ...config
    };
  }

  /**
   * Connect to RabbitMQ with automatic reconnection
   */
  async connect(): Promise<void> {
    try {
      this.connection = await amqp.connect(this.config.url, {
        heartbeat: this.config.heartbeat,
        clientProperties: {
          connection_name: this.config.connectionName,
          product: 'Stack 2025 Queue Core',
          version: '2.0.0',
          platform: 'Node.js',
        }
      });

      this.connection.on('error', (err: any) => {
        this.emit('error', err);
        if (!this.isClosing) {
          this.scheduleReconnect();
        }
      });

      this.connection.on('close', () => {
        this.emit('disconnected');
        if (!this.isClosing) {
          this.scheduleReconnect();
        }
      });

      this.channel = await this.connection.createChannel();
      if (this.channel) {
        await this.channel.prefetch(this.config.prefetch!);

        this.channel.on('error', (err: any) => {
          this.emit('channel-error', err);
        });

        this.channel.on('close', () => {
          this.emit('channel-closed');
        });
      }

      // Set up default exchanges and queues for call center
      await this.setupDefaultTopology();

      this.emit('connected');
    } catch (error) {
      this.emit('error', error);
      throw error;
    }
  }

  /**
   * Set up default call center topology
   */
  private async setupDefaultTopology(): Promise<void> {
    if (!this.channel) throw new Error('Channel not initialized');

    // Create exchanges
    const exchanges: Array<[ExchangeName, ExchangeOptions]> = [
      ['calls', { type: 'topic', durable: true }],
      ['events', { type: 'fanout', durable: true }],
      ['notifications', { type: 'direct', durable: true }],
      ['ai', { type: 'topic', durable: true }],
      ['analytics', { type: 'topic', durable: true }],
    ];

    for (const [name, options] of exchanges) {
      await this.createExchange(name, options);
    }

    // Create queues with dead letter support
    const queues: Array<[QueueName, QueueOptions]> = [
      ['inbound', {
        durable: true,
        deadLetterExchange: 'dlx',
        deadLetterRoutingKey: 'inbound.failed',
        messageTtl: 3600000, // 1 hour
      }],
      ['outbound', {
        durable: true,
        deadLetterExchange: 'dlx',
        deadLetterRoutingKey: 'outbound.failed',
      }],
      ['priority', {
        durable: true,
        maxPriority: 10,
        deadLetterExchange: 'dlx',
        deadLetterRoutingKey: 'priority.failed',
      }],
      ['ai-processing', {
        durable: true,
        deadLetterExchange: 'dlx',
        deadLetterRoutingKey: 'ai.failed',
        maxLength: 1000, // Prevent memory issues
      }],
      ['deadLetter', {
        durable: true,
        messageTtl: 86400000, // 24 hours
      }],
    ];

    // Create dead letter exchange
    await this.channel.assertExchange('dlx', 'topic', { durable: true });

    for (const [name, options] of queues) {
      await this.createQueue(name, options);
    }

    // Bind queues to exchanges
    await this.bindQueue('inbound', 'calls', 'call.inbound.*');
    await this.bindQueue('outbound', 'calls', 'call.outbound.*');
    await this.bindQueue('ai-processing', 'ai', 'ai.#');
  }

  /**
   * Schedule reconnection attempt
   */
  private scheduleReconnect(): void {
    if (this.reconnectTimer) return;

    this.reconnectTimer = setTimeout(async () => {
      this.reconnectTimer = null;
      try {
        await this.connect();
      } catch (error) {
        this.scheduleReconnect();
      }
    }, this.config.retryDelay);
  }

  /**
   * Create an exchange
   */
  async createExchange(name: string, options: ExchangeOptions): Promise<void> {
    if (!this.channel) throw new Error('Not connected to RabbitMQ');

    await this.channel.assertExchange(name, options.type, {
      durable: options.durable ?? true,
      autoDelete: options.autoDelete ?? false,
      internal: options.internal ?? false,
      arguments: options.arguments,
    });
  }

  /**
   * Create a queue
   */
  async createQueue(name: string, options: QueueOptions = {}): Promise<void> {
    if (!this.channel) throw new Error('Not connected to RabbitMQ');

    const queueOptions: any = {
      durable: options.durable ?? true,
      autoDelete: options.autoDelete ?? false,
      exclusive: options.exclusive ?? false,
      arguments: {},
    };

    if (options.deadLetterExchange) {
      queueOptions.arguments['x-dead-letter-exchange'] = options.deadLetterExchange;
    }
    if (options.deadLetterRoutingKey) {
      queueOptions.arguments['x-dead-letter-routing-key'] = options.deadLetterRoutingKey;
    }
    if (options.messageTtl) {
      queueOptions.arguments['x-message-ttl'] = options.messageTtl;
    }
    if (options.maxLength) {
      queueOptions.arguments['x-max-length'] = options.maxLength;
    }
    if (options.maxPriority) {
      queueOptions.arguments['x-max-priority'] = options.maxPriority;
    }

    await this.channel.assertQueue(name, queueOptions);
  }

  /**
   * Bind a queue to an exchange
   */
  async bindQueue(queue: string, exchange: string, routingKey: string): Promise<void> {
    if (!this.channel) throw new Error('Not connected to RabbitMQ');
    await this.channel.bindQueue(queue, exchange, routingKey);
  }

  /**
   * Publish a message to an exchange
   */
  async publish<T = any>(
    exchange: string,
    routingKey: string,
    payload: T,
    options: PublishOptions = {}
  ): Promise<void> {
    if (!this.channel) throw new Error('Not connected to RabbitMQ');

    const message: QueueMessage<T> = {
      id: options.messageId || uuidv4(),
      correlationId: options.correlationId,
      payload,
      metadata: {
        timestamp: new Date().toISOString(),
        source: this.config.connectionName!,
        priority: options.priority,
      },
      headers: options.headers,
    };

    const buffer = Buffer.from(JSON.stringify(message));

    const publishOptions: amqp.Options.Publish = {
      persistent: options.persistent ?? true,
      priority: options.priority,
      expiration: options.expiration,
      messageId: message.id,
      timestamp: options.timestamp ?? Date.now(),
      correlationId: options.correlationId,
      replyTo: options.replyTo,
      headers: options.headers,
    };

    const published = this.channel.publish(exchange, routingKey, buffer, publishOptions);

    if (!published) {
      // Handle backpressure
      await new Promise<void>((resolve) => {
        this.channel!.once('drain', resolve);
      });
    }

    this.emit('message-published', { exchange, routingKey, messageId: message.id });
  }

  /**
   * Send a message directly to a queue
   */
  async sendToQueue<T = any>(
    queue: string,
    payload: T,
    options: PublishOptions = {}
  ): Promise<void> {
    if (!this.channel) throw new Error('Not connected to RabbitMQ');

    const message: QueueMessage<T> = {
      id: options.messageId || uuidv4(),
      correlationId: options.correlationId,
      payload,
      metadata: {
        timestamp: new Date().toISOString(),
        source: this.config.connectionName!,
        priority: options.priority,
      },
      headers: options.headers,
    };

    const buffer = Buffer.from(JSON.stringify(message));

    const sent = this.channel.sendToQueue(queue, buffer, {
      persistent: options.persistent ?? true,
      priority: options.priority,
      expiration: options.expiration,
      messageId: message.id,
      timestamp: options.timestamp ?? Date.now(),
      correlationId: options.correlationId,
      replyTo: options.replyTo,
      headers: options.headers,
    });

    if (!sent) {
      // Handle backpressure
      await new Promise<void>((resolve) => {
        this.channel!.once('drain', resolve);
      });
    }

    this.emit('message-sent', { queue, messageId: message.id });
  }

  /**
   * Consume messages from a queue
   */
  async consume<T = any>(
    queue: string,
    handler: MessageHandler<T>,
    options: ConsumerOptions = {}
  ): Promise<string> {
    if (!this.channel) throw new Error('Not connected to RabbitMQ');

    if (options.prefetchCount) {
      await this.channel.prefetch(options.prefetchCount);
    }

    const { consumerTag } = await this.channel.consume(
      queue,
      async (msg: any) => {
        if (!msg) return;

        try {
          const message: QueueMessage<T> = JSON.parse(msg.content.toString());

          const ack = () => {
            if (this.channel) {
              this.channel.ack(msg);
              this.emit('message-acked', { queue, messageId: message.id });
            }
          };

          const nack = (requeue = true) => {
            if (this.channel) {
              this.channel.nack(msg, false, requeue);
              this.emit('message-nacked', { queue, messageId: message.id, requeue });
            }
          };

          const reject = (requeue = false) => {
            if (this.channel) {
              this.channel.reject(msg, requeue);
              this.emit('message-rejected', { queue, messageId: message.id, requeue });
            }
          };

          await handler(message, ack, nack, reject);
        } catch (error) {
          this.emit('handler-error', { queue, error });
          // Reject message and send to dead letter queue
          if (this.channel) {
            this.channel.reject(msg, false);
          }
        }
      },
      {
        noAck: options.noAck ?? false,
        exclusive: options.exclusive ?? false,
        priority: options.priority,
        arguments: options.arguments,
      }
    );

    this.consumers.set(consumerTag, queue);
    this.emit('consumer-started', { queue, consumerTag });

    return consumerTag;
  }

  /**
   * Cancel a consumer
   */
  async cancel(consumerTag: string): Promise<void> {
    if (!this.channel) throw new Error('Not connected to RabbitMQ');

    await this.channel.cancel(consumerTag);
    const queue = this.consumers.get(consumerTag);
    this.consumers.delete(consumerTag);

    this.emit('consumer-cancelled', { queue, consumerTag });
  }

  /**
   * Get queue statistics
   */
  async getQueueStats(queue: string): Promise<QueueStats> {
    if (!this.channel) throw new Error('Not connected to RabbitMQ');

    const info = await this.channel.checkQueue(queue);

    return {
      name: info.queue,
      messageCount: info.messageCount,
      consumerCount: info.consumerCount,
      memory: 0, // RabbitMQ doesn't provide memory per queue via AMQP
    };
  }

  /**
   * Purge all messages from a queue
   */
  async purgeQueue(queue: string): Promise<number> {
    if (!this.channel) throw new Error('Not connected to RabbitMQ');

    const { messageCount } = await this.channel.purgeQueue(queue);
    this.emit('queue-purged', { queue, messageCount });

    return messageCount;
  }

  /**
   * Close the connection gracefully
   */
  async close(): Promise<void> {
    this.isClosing = true;

    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }

    // Cancel all consumers
    for (const [consumerTag] of this.consumers) {
      await this.cancel(consumerTag);
    }

    if (this.channel) {
      await this.channel.close();
      this.channel = null;
    }

    if (this.connection) {
      try {
        await this.connection.close();
      } catch (error) {
        // Connection may already be closed
        console.warn('Error closing connection:', error);
      }
      this.connection = null;
    }

    this.emit('closed');
  }

  /**
   * Check if connected
   */
  isConnected(): boolean {
    return this.connection !== null && this.channel !== null;
  }
}