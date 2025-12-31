/**
 * @stack-2025/deepgram-agent-core - Agent
 * Main Voice Agent class implementing Deepgram Voice Agent API
 */

import WebSocket from 'ws';
import { v4 as uuidv4 } from 'uuid';
import {
  AgentConfig,
  VoiceAgentOptions,
  ConnectionState,
  ConversationContext,
  VoiceAgentEvent,
  EventHandler,
  FunctionCallHandler,
  AudioChunk,
  VoiceAgentError,
  ConnectionError,
  FunctionDefinition,
  KeepAliveConfig
} from './types.js';
import {
  VoiceAgentEventEmitter,
  EventHandlerRegistry,
  EventProcessor
} from './events.js';
import { ConfigUtils } from './config.js';

/**
 * Main Voice Agent class for Deepgram Voice Agent API
 */
export class DeepgramVoiceAgent {
  private ws: WebSocket | null = null;
  private emitter: VoiceAgentEventEmitter;
  private registry: EventHandlerRegistry;
  private processor: EventProcessor;
  private options: VoiceAgentOptions;
  private context: ConversationContext;
  private state: ConnectionState = ConnectionState.DISCONNECTED;
  private keepAliveInterval: NodeJS.Timeout | null = null;
  private reconnectAttempts = 0;
  private reconnectTimeout: NodeJS.Timeout | null = null;

  constructor(
    private config: AgentConfig,
    options: Partial<VoiceAgentOptions>
  ) {
    this.options = ConfigUtils.validateOptions(options);
    this.emitter = new VoiceAgentEventEmitter();
    this.registry = new EventHandlerRegistry();
    
    // Initialize conversation context
    this.context = this.createContext();
    
    // Initialize event processor
    this.processor = new EventProcessor(
      this.emitter,
      this.registry,
      this.options.conversation_context ? this.context : undefined
    );

    // Set up internal error handling
    this.setupInternalHandlers();
  }

  /**
   * Connect to Deepgram Voice Agent API
   */
  async connect(): Promise<void> {
    if (this.state === ConnectionState.CONNECTED || this.state === ConnectionState.CONNECTING) {
      throw new VoiceAgentError('Already connected or connecting');
    }

    this.setState(ConnectionState.CONNECTING);

    try {
      await this.establishConnection();
      this.setState(ConnectionState.CONNECTED);
      this.resetReconnectAttempts();
      this.startKeepAlive();
      
      this.emitter.emit('connected');
    } catch (error) {
      this.setState(ConnectionState.FAILED);
      const errorMessage = error instanceof Error ? error.message : String(error);
      throw new ConnectionError(`Failed to connect: ${errorMessage}`, error);
    }
  }

  /**
   * Disconnect from Deepgram Voice Agent API
   */
  async disconnect(): Promise<void> {
    this.setState(ConnectionState.DISCONNECTED);
    this.stopKeepAlive();
    this.clearReconnectTimeout();

    if (this.ws) {
      this.ws.close(1000, 'Normal closure');
      this.ws = null;
    }

    this.emitter.emit('disconnected');
  }

  /**
   * Send audio data to the agent
   */
  sendAudio(audioData: Buffer): void {
    if (!this.isConnected()) {
      throw new VoiceAgentError('Not connected to voice agent');
    }

    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(audioData);
    }
  }

  /**
   * Send audio chunk with metadata
   */
  sendAudioChunk(chunk: AudioChunk): void {
    // For Deepgram Voice Agent API, we typically just send the raw audio data
    this.sendAudio(chunk.data);
  }

  /**
   * Send text message directly (if supported by the agent configuration)
   */
  sendText(text: string): void {
    if (!this.isConnected()) {
      throw new VoiceAgentError('Not connected to voice agent');
    }

    const message = {
      type: 'TextInput',
      text: text,
      timestamp: new Date().toISOString()
    };

    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    }
  }

  /**
   * Register event handler
   */
  on<T extends VoiceAgentEvent>(
    eventType: T['type'], 
    handler: EventHandler<T>
  ): this {
    this.emitter.onEvent(eventType, handler);
    this.registry.register(eventType, handler);
    return this;
  }

  /**
   * Register one-time event handler
   */
  once<T extends VoiceAgentEvent>(
    eventType: T['type'], 
    handler: EventHandler<T>
  ): this {
    this.emitter.onceEvent(eventType, handler);
    return this;
  }

  /**
   * Remove event handler
   */
  off<T extends VoiceAgentEvent>(
    eventType: T['type'], 
    handler?: EventHandler<T>
  ): this {
    this.emitter.offEvent(eventType, handler);
    if (handler) {
      this.registry.unregister(eventType, handler);
    }
    return this;
  }

  /**
   * Register function call handler
   */
  onFunction(functionName: string, handler: FunctionCallHandler): this {
    this.registry.registerFunction(functionName, handler);
    return this;
  }

  /**
   * Remove function call handler
   */
  offFunction(functionName: string): this {
    this.registry.unregisterFunction(functionName);
    return this;
  }

  /**
   * Get current connection state
   */
  getState(): ConnectionState {
    return this.state;
  }

  /**
   * Check if connected
   */
  isConnected(): boolean {
    return this.state === ConnectionState.CONNECTED && 
           this.ws !== null && 
           this.ws.readyState === WebSocket.OPEN;
  }

  /**
   * Get conversation context
   */
  getContext(): ConversationContext | null {
    return this.options.conversation_context ? this.context : null;
  }

  /**
   * Clear conversation context
   */
  clearContext(): void {
    if (this.options.conversation_context) {
      this.context = this.createContext();
    }
  }

  /**
   * Update agent configuration
   */
  updateConfig(newConfig: Partial<AgentConfig>): void {
    this.config = { ...this.config, ...newConfig };
    
    // If connected, send configuration update
    if (this.isConnected()) {
      this.sendConfigurationUpdate();
    }
  }

  /**
   * Get current configuration
   */
  getConfig(): AgentConfig {
    return { ...this.config };
  }

  /**
   * Add function definitions to the agent
   */
  addFunctions(functions: FunctionDefinition[]): void {
    if (!this.config.think.functions) {
      this.config.think.functions = [];
    }
    this.config.think.functions.push(...functions);
    
    if (this.isConnected()) {
      this.sendConfigurationUpdate();
    }
  }

  /**
   * Remove function definitions from the agent
   */
  removeFunctions(functionNames: string[]): void {
    if (this.config.think.functions) {
      this.config.think.functions = this.config.think.functions.filter(
        fn => !functionNames.includes(fn.name)
      );
      
      if (this.isConnected()) {
        this.sendConfigurationUpdate();
      }
    }
  }

  /**
   * Get event emitter for custom event handling
   */
  getEmitter(): VoiceAgentEventEmitter {
    return this.emitter;
  }

  /**
   * Switch to Spanish voice configuration
   */
  switchToSpanishVoice(voiceId: string = 'nestor-es'): void {
    const spanishVoices = [
      'nestor-es', 'carina-es', 'alvaro-es', 'diana-es', 
      'aquila-es', 'selena-es', 'estrella-es', 'sirio-es', 
      'celeste-es', 'asteria-es'
    ];

    if (!spanishVoices.includes(voiceId)) {
      throw new VoiceAgentError(`Invalid Spanish voice ID: ${voiceId}`);
    }

    // Update configuration with Spanish voice
    this.updateConfig({
      speak: {
        ...this.config.speak,
        model: this.getVoiceModel(voiceId),
        language: this.getVoiceLanguage(voiceId)
      },
      listen: {
        ...this.config.listen,
        language: 'es'
      }
    });
  }

  /**
   * Switch voice based on use case and language
   */
  switchVoiceByUseCase(
    language: 'en' | 'es' | 'cs' = 'en',
    useCase: 'customer-service' | 'healthcare' | 'sales' | 'corporate' | 'marketing' = 'customer-service',
    gender: 'male' | 'female' = 'female'
  ): void {
    let voiceId: string;

    if (language === 'es') {
      // Spanish voice selection
      switch (useCase) {
        case 'customer-service':
          voiceId = gender === 'male' ? 'nestor-es' : 'selena-es';
          break;
        case 'healthcare':
          voiceId = gender === 'male' ? 'sirio-es' : 'estrella-es';
          break;
        case 'sales':
          voiceId = gender === 'male' ? 'aquila-es' : 'celeste-es';
          break;
        case 'corporate':
          voiceId = gender === 'male' ? 'alvaro-es' : 'carina-es';
          break;
        case 'marketing':
          voiceId = 'diana-es'; // Always female for marketing
          break;
        default:
          voiceId = 'nestor-es';
      }
    } else if (language === 'cs') {
      // Czech voice selection
      voiceId = gender === 'male' ? 'external-czech-pavel' : 'external-czech-kamila';
    } else {
      // English voice selection
      switch (useCase) {
        case 'customer-service':
          voiceId = gender === 'male' ? 'orion-en' : 'asteria-en';
          break;
        case 'healthcare':
          voiceId = gender === 'male' ? 'perseus-en' : 'luna-en';
          break;
        case 'sales':
          voiceId = gender === 'male' ? 'perseus-en' : 'stella-en';
          break;
        case 'corporate':
          voiceId = gender === 'male' ? 'zeus-en' : 'hera-en';
          break;
        case 'marketing':
          voiceId = gender === 'male' ? 'angus-en' : 'stella-en';
          break;
        default:
          voiceId = 'asteria-en';
      }
    }

    this.updateConfig({
      speak: {
        ...this.config.speak,
        model: this.getVoiceModel(voiceId),
        language: this.getVoiceLanguage(voiceId)
      },
      listen: {
        ...this.config.listen,
        language: language
      }
    });
  }

  /**
   * Private Methods
   */

  private async establishConnection(): Promise<void> {
    return new Promise((resolve, reject) => {
      const wsUrl = `${this.options.url}?model=${this.config.speak.model}`;
      
      this.ws = new WebSocket(wsUrl, {
        headers: {
          'Authorization': `Token ${this.options.api_key}`,
          'Content-Type': 'application/json'
        }
      });

      this.ws.onopen = () => {
        this.sendInitialConfiguration();
        resolve();
      };

      this.ws.onmessage = (event) => {
        this.handleMessage(event.data);
      };

      this.ws.onclose = (event) => {
        this.handleClose(event);
      };

      this.ws.onerror = (error) => {
        reject(error);
      };

      // Connection timeout
      const timeout = setTimeout(() => {
        if (this.ws?.readyState === WebSocket.CONNECTING) {
          this.ws.close();
          reject(new ConnectionError('Connection timeout'));
        }
      }, 30000);

      this.ws.onopen = () => {
        clearTimeout(timeout);
        this.sendInitialConfiguration();
        resolve();
      };
    });
  }

  private sendInitialConfiguration(): void {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) return;

    const config = {
      type: 'SettingsConfiguration',
      audio: {
        input: {
          encoding: this.config.listen.encoding,
          sample_rate: this.config.listen.sample_rate,
          channels: this.config.listen.channels
        },
        output: {
          encoding: this.config.speak.encoding,
          sample_rate: this.config.speak.sample_rate,
          channels: this.config.speak.channels,
          container: this.config.speak.container
        }
      },
      agent: {
        listen: {
          model: this.config.listen.model,
          language: this.config.listen.language,
          smart_format: this.config.listen.smart_format
        },
        think: {
          provider: {
            type: this.config.think.provider
          },
          model: this.config.think.model,
          instructions: this.config.think.system_prompt,
          functions: this.config.think.functions
        },
        speak: {
          model: this.config.speak.model
        }
      }
    };

    this.ws.send(JSON.stringify(config));
  }

  private sendConfigurationUpdate(): void {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) return;

    const updateConfig = {
      type: 'ConfigurationUpdate',
      agent: {
        think: {
          provider: {
            type: this.config.think.provider
          },
          model: this.config.think.model,
          instructions: this.config.think.system_prompt,
          functions: this.config.think.functions
        }
      }
    };

    this.ws.send(JSON.stringify(updateConfig));
  }

  private async handleMessage(data: any): Promise<void> {
    try {
      const message = typeof data === 'string' ? data : data.toString();
      await this.processor.processMessage(message);
    } catch (error) {
      console.error('Error handling WebSocket message:', error);
      this.emitter.emit('error', error);
    }
  }

  private handleClose(event: { code: number; reason: string }): void {
    console.log('WebSocket closed:', event.code, event.reason);
    
    if (this.state !== ConnectionState.DISCONNECTED) {
      this.setState(ConnectionState.DISCONNECTED);
      this.stopKeepAlive();
      
      if (this.options.auto_reconnect && 
          this.reconnectAttempts < this.options.max_reconnect_attempts!) {
        this.scheduleReconnect();
      }
    }

    this.emitter.emit('disconnected', { code: event.code, reason: event.reason });
  }

  private scheduleReconnect(): void {
    this.setState(ConnectionState.RECONNECTING);
    this.reconnectAttempts++;

    const delay = Math.min(
      this.options.reconnect_interval! * Math.pow(2, this.reconnectAttempts - 1),
      30000 // Max 30 seconds
    );

    this.reconnectTimeout = setTimeout(async () => {
      try {
        await this.connect();
      } catch (error) {
        console.error('Reconnection failed:', error);
        if (this.reconnectAttempts < this.options.max_reconnect_attempts!) {
          this.scheduleReconnect();
        } else {
          this.setState(ConnectionState.FAILED);
          this.emitter.emit('reconnectFailed');
        }
      }
    }, delay);

    this.emitter.emit('reconnecting', { attempt: this.reconnectAttempts, delay });
  }

  private clearReconnectTimeout(): void {
    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout);
      this.reconnectTimeout = null;
    }
  }

  private resetReconnectAttempts(): void {
    this.reconnectAttempts = 0;
    this.clearReconnectTimeout();
  }

  private startKeepAlive(): void {
    if (!this.options.keep_alive?.enabled) return;

    const config = this.options.keep_alive;
    this.keepAliveInterval = setInterval(() => {
      if (this.isConnected()) {
        const ping = {
          type: 'KeepAlive',
          timestamp: new Date().toISOString()
        };
        this.ws!.send(JSON.stringify(ping));
      }
    }, config.interval);
  }

  private stopKeepAlive(): void {
    if (this.keepAliveInterval) {
      clearInterval(this.keepAliveInterval);
      this.keepAliveInterval = null;
    }
  }

  private setState(newState: ConnectionState): void {
    const oldState = this.state;
    this.state = newState;
    this.emitter.emit('stateChange', { from: oldState, to: newState });
  }

  private createContext(): ConversationContext {
    return {
      conversation_id: uuidv4(),
      messages: [],
      functions_called: [],
      metadata: {
        started_at: Date.now(),
        last_activity: Date.now(),
        total_turns: 0
      }
    };
  }

  private setupInternalHandlers(): void {
    // Handle internal events
    this.emitter.on('error', (error) => {
      console.error('Voice Agent Error:', error);
    });

    this.emitter.on('warning', (warning) => {
      console.warn('Voice Agent Warning:', warning);
    });

    // Update context on conversation start
    this.emitter.on('ConversationStarted', (event) => {
      if (this.context && event.data.conversation_id) {
        this.context.conversation_id = event.data.conversation_id;
      }
    });
  }

  private getVoiceModel(voiceId: string): string {
    const voiceModelMap: Record<string, string> = {
      // Spanish voices
      'nestor-es': 'aura-2-nestor-es',
      'carina-es': 'aura-2-carina-es',
      'alvaro-es': 'aura-2-alvaro-es',
      'diana-es': 'aura-2-diana-es',
      'aquila-es': 'aura-2-aquila-es',
      'selena-es': 'aura-2-selena-es',
      'estrella-es': 'aura-2-estrella-es',
      'sirio-es': 'aura-2-sirio-es',
      'celeste-es': 'aura-2-celeste-es',
      'asteria-es': 'aura-asteria-es',
      
      // English voices
      'asteria-en': 'aura-asteria-en',
      'luna-en': 'aura-luna-en',
      'stella-en': 'aura-stella-en',
      'athena-en': 'aura-athena-en',
      'hera-en': 'aura-hera-en',
      'orion-en': 'aura-orion-en',
      'perseus-en': 'aura-perseus-en',
      'angus-en': 'aura-angus-en',
      'arcas-en': 'aura-arcas-en',
      'zeus-en': 'aura-zeus-en',
      
      // Czech voices
      'external-czech-kamila': 'external-tts-czech-kamila',
      'external-czech-pavel': 'external-tts-czech-pavel',
      'external-czech-jana': 'external-tts-czech-jana',
      'external-czech-tomas': 'external-tts-czech-tomas'
    };

    return voiceModelMap[voiceId] || voiceId;
  }

  private getVoiceLanguage(voiceId: string): string {
    const voiceLanguageMap: Record<string, string> = {
      // Spanish voices
      'nestor-es': 'es-ES',
      'carina-es': 'es-ES',
      'alvaro-es': 'es-ES',
      'diana-es': 'es-ES',
      'aquila-es': 'es-LA',
      'selena-es': 'es-LA',
      'estrella-es': 'es-MX',
      'sirio-es': 'es-MX',
      'celeste-es': 'es-CO',
      'asteria-es': 'es',
      
      // English voices
      'asteria-en': 'en-US',
      'luna-en': 'en-GB',
      'stella-en': 'en-US',
      'athena-en': 'en-GB',
      'hera-en': 'en-US',
      'orion-en': 'en-US',
      'perseus-en': 'en-US',
      'angus-en': 'en-IE',
      'arcas-en': 'en-US',
      'zeus-en': 'en-US',
      
      // Czech voices
      'external-czech-kamila': 'cs',
      'external-czech-pavel': 'cs',
      'external-czech-jana': 'cs',
      'external-czech-tomas': 'cs'
    };

    return voiceLanguageMap[voiceId] || 'en';
  }
}