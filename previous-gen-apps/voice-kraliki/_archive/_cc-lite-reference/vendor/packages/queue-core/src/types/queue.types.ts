/**
 * Queue Core Types
 * Defines the contract for queue implementations
 */

import { z } from 'zod';

export type QueueName = 'inbound' | 'outbound' | 'priority' | 'deadLetter' | 'analytics' | 'ai-processing';
export type ExchangeName = 'calls' | 'events' | 'notifications' | 'ai' | 'analytics';

export interface QueueMessage<T = any> {
  id: string;
  correlationId?: string;
  payload: T;
  metadata: {
    timestamp: string;
    source: string;
    priority?: number;
    retryCount?: number;
    maxRetries?: number;
  };
  headers?: Record<string, any>;
}

export interface QueueOptions {
  durable?: boolean;
  autoDelete?: boolean;
  exclusive?: boolean;
  deadLetterExchange?: string;
  deadLetterRoutingKey?: string;
  messageTtl?: number;
  maxLength?: number;
  maxPriority?: number;
  arguments?: Record<string, any>;
}

export interface ExchangeOptions {
  type: 'direct' | 'topic' | 'fanout' | 'headers';
  durable?: boolean;
  autoDelete?: boolean;
  internal?: boolean;
  arguments?: Record<string, any>;
}

export interface PublishOptions {
  persistent?: boolean;
  priority?: number;
  expiration?: string;
  messageId?: string;
  timestamp?: number;
  correlationId?: string;
  replyTo?: string;
  headers?: Record<string, any>;
}

export interface ConsumerOptions {
  noAck?: boolean;
  exclusive?: boolean;
  priority?: number;
  arguments?: Record<string, any>;
  prefetchCount?: number;
}

export type MessageHandler<T = any> = (
  message: QueueMessage<T>,
  ack: () => void,
  nack: (requeue?: boolean) => void,
  reject: (requeue?: boolean) => void
) => Promise<void> | void;

export interface QueueStats {
  name: string;
  messageCount: number;
  consumerCount: number;
  idleSince?: Date;
  memory: number;
}

// Zod schemas for validation
export const QueueMessageSchema = z.object({
  id: z.string(),
  correlationId: z.string().optional(),
  payload: z.any(),
  metadata: z.object({
    timestamp: z.string(),
    source: z.string(),
    priority: z.number().optional(),
    retryCount: z.number().optional(),
    maxRetries: z.number().optional(),
  }),
  headers: z.record(z.any()).optional(),
});

// Call center specific message types
export interface CallEvent {
  type: 'call.started' | 'call.ended' | 'call.transferred' | 'call.recorded';
  callId: string;
  agentId?: string;
  customerId: string;
  timestamp: Date;
  data: Record<string, any>;
}

export interface TranscriptionEvent {
  type: 'transcription.partial' | 'transcription.final';
  callId: string;
  sessionId: string;
  speaker: 'agent' | 'customer' | 'ai';
  text: string;
  confidence: number;
  timestamp: Date;
  language?: string;
}

export interface AIProcessingRequest {
  type: 'sentiment' | 'intent' | 'summary' | 'agent-assist';
  callId: string;
  input: string | Record<string, any>;
  context?: Record<string, any>;
  priority: 'low' | 'medium' | 'high' | 'critical';
}