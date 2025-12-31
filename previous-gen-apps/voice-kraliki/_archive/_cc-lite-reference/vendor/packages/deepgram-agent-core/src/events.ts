/**
 * @stack-2025/deepgram-agent-core - Events
 * Event management and handlers for Deepgram Voice Agent API
 */

import { EventEmitter } from 'eventemitter3';
import { 
  VoiceAgentEvent, 
  EventHandler, 
  FunctionCallHandler,
  FunctionCallEvent,
  ConversationContext
} from './types.js';

/**
 * Enhanced EventEmitter for Voice Agent with typed events
 */
export class VoiceAgentEventEmitter extends EventEmitter {
  /**
   * Register handler for specific event type
   */
  onEvent<T extends VoiceAgentEvent>(
    eventType: T['type'], 
    handler: EventHandler<T>
  ): this {
    return this.on(eventType, handler);
  }

  /**
   * Register one-time handler for specific event type
   */
  onceEvent<T extends VoiceAgentEvent>(
    eventType: T['type'], 
    handler: EventHandler<T>
  ): this {
    return this.once(eventType, handler);
  }

  /**
   * Remove handler for specific event type
   */
  offEvent<T extends VoiceAgentEvent>(
    eventType: T['type'], 
    handler?: EventHandler<T>
  ): this {
    return this.off(eventType, handler);
  }

  /**
   * Emit typed event
   */
  emitEvent<T extends VoiceAgentEvent>(event: T): boolean {
    return this.emit(event.type, event);
  }
}

/**
 * Event handler registry for managing multiple handlers
 */
export class EventHandlerRegistry {
  private handlers = new Map<string, Set<EventHandler>>();
  private functionHandlers = new Map<string, FunctionCallHandler>();

  /**
   * Register event handler
   */
  register<T extends VoiceAgentEvent>(
    eventType: T['type'], 
    handler: EventHandler<T>
  ): void {
    if (!this.handlers.has(eventType)) {
      this.handlers.set(eventType, new Set());
    }
    this.handlers.get(eventType)!.add(handler as EventHandler);
  }

  /**
   * Register function call handler
   */
  registerFunction(functionName: string, handler: FunctionCallHandler): void {
    this.functionHandlers.set(functionName, handler);
  }

  /**
   * Unregister event handler
   */
  unregister<T extends VoiceAgentEvent>(
    eventType: T['type'], 
    handler: EventHandler<T>
  ): void {
    const handlerSet = this.handlers.get(eventType);
    if (handlerSet) {
      handlerSet.delete(handler as EventHandler);
      if (handlerSet.size === 0) {
        this.handlers.delete(eventType);
      }
    }
  }

  /**
   * Unregister function call handler
   */
  unregisterFunction(functionName: string): void {
    this.functionHandlers.delete(functionName);
  }

  /**
   * Get handlers for event type
   */
  getHandlers(eventType: string): Set<EventHandler> {
    return this.handlers.get(eventType) || new Set();
  }

  /**
   * Get function handler
   */
  getFunctionHandler(functionName: string): FunctionCallHandler | undefined {
    return this.functionHandlers.get(functionName);
  }

  /**
   * Clear all handlers
   */
  clear(): void {
    this.handlers.clear();
    this.functionHandlers.clear();
  }

  /**
   * Get all registered event types
   */
  getEventTypes(): string[] {
    return Array.from(this.handlers.keys());
  }

  /**
   * Get all registered function names
   */
  getFunctionNames(): string[] {
    return Array.from(this.functionHandlers.keys());
  }
}

/**
 * Event processor for handling incoming WebSocket events
 */
export class EventProcessor {
  constructor(
    private emitter: VoiceAgentEventEmitter,
    private registry: EventHandlerRegistry,
    private context?: ConversationContext
  ) {}

  /**
   * Process raw WebSocket message and emit appropriate events
   */
  async processMessage(message: string): Promise<void> {
    try {
      const data = JSON.parse(message);
      const event = this.createEvent(data);
      
      if (event) {
        // Update conversation context if available
        if (this.context) {
          this.updateContext(event);
        }

        // Emit event through EventEmitter
        this.emitter.emitEvent(event);

        // Execute registered handlers
        await this.executeHandlers(event);

        // Handle function calls specially
        if (event.type === 'FunctionCall') {
          await this.handleFunctionCall(event as FunctionCallEvent);
        }
      }
    } catch (error) {
      console.error('Error processing WebSocket message:', error);
      this.emitter.emit('error', error);
    }
  }

  /**
   * Create typed event from raw WebSocket data
   */
  private createEvent(data: any): VoiceAgentEvent | null {
    const timestamp = Date.now();

    switch (data.type) {
      case 'UserStartedSpeaking':
        return { type: 'UserStartedSpeaking', timestamp };

      case 'UserStoppedSpeaking':
        return { type: 'UserStoppedSpeaking', timestamp };

      case 'SpeechStarted':
        return { 
          type: 'SpeechStarted', 
          timestamp,
          data: { timestamp: data.timestamp || new Date().toISOString() }
        };

      case 'UtteranceEnd':
        return {
          type: 'UtteranceEnd',
          timestamp,
          data: {
            channel: data.channel || 0,
            alternatives: data.alternatives || []
          }
        };

      case 'AgentThinking':
        return { type: 'AgentThinking', timestamp };

      case 'AgentSpeaking':
        return { type: 'AgentSpeaking', timestamp };

      case 'ConversationStarted':
        return {
          type: 'ConversationStarted',
          timestamp,
          data: { conversation_id: data.conversation_id }
        };

      case 'FunctionCall':
        return {
          type: 'FunctionCall',
          timestamp,
          data: {
            function_name: data.function_name,
            parameters: data.parameters || {},
            call_id: data.call_id
          }
        };

      case 'Error':
        return {
          type: 'Error',
          timestamp,
          data: {
            error: data.error,
            description: data.description
          }
        };

      case 'Warning':
        return {
          type: 'Warning',
          timestamp,
          data: {
            warning: data.warning,
            description: data.description
          }
        };

      case 'Metadata':
        return {
          type: 'Metadata',
          timestamp,
          data: {
            request_id: data.request_id,
            sha256: data.sha256,
            created: data.created,
            model_info: data.model_info
          }
        };

      default:
        console.warn('Unknown event type:', data.type);
        return null;
    }
  }

  /**
   * Execute all registered handlers for an event
   */
  private async executeHandlers(event: VoiceAgentEvent): Promise<void> {
    const handlers = this.registry.getHandlers(event.type);
    
    const promises = Array.from(handlers).map(async (handler) => {
      try {
        await handler(event);
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : String(error);
        console.error(`Error in event handler for ${event.type}:`, errorMessage);
      }
    });

    await Promise.all(promises);
  }

  /**
   * Handle function calls with registered handlers
   */
  private async handleFunctionCall(event: FunctionCallEvent): Promise<void> {
    const { function_name, parameters, call_id } = event.data;
    const handler = this.registry.getFunctionHandler(function_name);

    if (handler) {
      try {
        const result = await handler(event.data);
        
        // Emit function result event (custom event)
        this.emitter.emit('FunctionResult', {
          call_id,
          function_name,
          result,
          timestamp: Date.now()
        });
      } catch (error) {
        console.error(`Error executing function ${function_name}:`, error);
        
        // Emit function error event (custom event)
        const errorMessage = error instanceof Error ? error.message : String(error);
        this.emitter.emit('FunctionError', {
          call_id,
          function_name,
          error: errorMessage,
          timestamp: Date.now()
        });
      }
    } else {
      console.warn(`No handler registered for function: ${function_name}`);
    }
  }

  /**
   * Update conversation context with event data
   */
  private updateContext(event: VoiceAgentEvent): void {
    if (!this.context) return;

    this.context.metadata.last_activity = event.timestamp;

    switch (event.type) {
      case 'ConversationStarted':
        this.context.conversation_id = event.data.conversation_id;
        this.context.metadata.started_at = event.timestamp;
        break;

      case 'UtteranceEnd':
        if (event.data.alternatives.length > 0) {
          const transcript = event.data.alternatives[0].transcript;
          this.context.messages.push({
            role: 'user',
            content: transcript,
            timestamp: event.timestamp
          });
          this.context.metadata.total_turns++;
        }
        break;

      case 'AgentSpeaking':
        // Note: Agent response content would need to be captured from TTS events
        // This is a placeholder for when that data becomes available
        break;

      case 'FunctionCall':
        this.context.functions_called.push({
          function_name: event.data.function_name,
          parameters: event.data.parameters,
          timestamp: event.timestamp
        });
        break;
    }
  }
}

/**
 * Pre-built event handlers for common use cases
 */
export class StandardEventHandlers {
  /**
   * Create a logging handler that logs all events
   */
  static createLogger(prefix = '[VoiceAgent]'): EventHandler {
    return (event) => {
      console.log(`${prefix} ${event.type}:`, event.data || 'no data');
    };
  }

  /**
   * Create a transcript collector that accumulates user speech
   */
  static createTranscriptCollector(): {
    handler: EventHandler;
    getTranscripts: () => string[];
    clear: () => void;
  } {
    const transcripts: string[] = [];

    return {
      handler: (event) => {
        if (event.type === 'UtteranceEnd' && event.data.alternatives.length > 0) {
          const transcript = event.data.alternatives[0].transcript;
          if (transcript.trim()) {
            transcripts.push(transcript);
          }
        }
      },
      getTranscripts: () => [...transcripts],
      clear: () => transcripts.length = 0
    };
  }

  /**
   * Create a conversation state tracker
   */
  static createStateTracker(): {
    handler: EventHandler;
    getState: () => {
      isUserSpeaking: boolean;
      isAgentThinking: boolean;
      isAgentSpeaking: boolean;
      conversationActive: boolean;
    };
  } {
    let isUserSpeaking = false;
    let isAgentThinking = false;
    let isAgentSpeaking = false;
    let conversationActive = false;

    return {
      handler: (event) => {
        switch (event.type) {
          case 'UserStartedSpeaking':
            isUserSpeaking = true;
            break;
          case 'UserStoppedSpeaking':
            isUserSpeaking = false;
            break;
          case 'AgentThinking':
            isAgentThinking = true;
            isAgentSpeaking = false;
            break;
          case 'AgentSpeaking':
            isAgentThinking = false;
            isAgentSpeaking = true;
            break;
          case 'ConversationStarted':
            conversationActive = true;
            break;
        }
      },
      getState: () => ({
        isUserSpeaking,
        isAgentThinking,
        isAgentSpeaking,
        conversationActive
      })
    };
  }

  /**
   * Create an error handler that logs errors and warnings
   */
  static createErrorHandler(onError?: (error: string, description?: string) => void): EventHandler {
    return (event) => {
      if (event.type === 'Error') {
        console.error('Voice Agent Error:', event.data.error, event.data.description);
        onError?.(event.data.error, event.data.description);
      } else if (event.type === 'Warning') {
        console.warn('Voice Agent Warning:', event.data.warning, event.data.description);
      }
    };
  }
}