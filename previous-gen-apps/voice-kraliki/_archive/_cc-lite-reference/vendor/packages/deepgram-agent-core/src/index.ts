/**
 * @stack-2025/deepgram-agent-core
 * Complete Deepgram Voice Agent API integration for Stack 2025
 * 
 * Features:
 * - Real-time voice-to-voice conversations
 * - Built-in LLM orchestration (OpenAI, Anthropic, Deepgram)
 * - Advanced conversation management
 * - Function calling support
 * - Auto-reconnection and keep-alive
 * - TypeScript-first with comprehensive types
 */

// Main Voice Agent class
export { DeepgramVoiceAgent } from './agent';

// Configuration builders and presets
export {
  VoiceAgentConfigBuilder,
  LLMProviders,
  VoiceModels,
  PresetConfigs,
  ConfigUtils,
  createVoiceAgentConfig,
  DEFAULT_KEEP_ALIVE
} from './config';

// Event management
export {
  VoiceAgentEventEmitter,
  EventHandlerRegistry,
  EventProcessor,
  StandardEventHandlers
} from './events';

// Provider configurations
export {
  ProviderFactory,
  FunctionDefinitions,
  IndustryProviders,
  ProviderChecker
} from './providers';

// Voice configuration
export {
  DEEPGRAM_VOICES,
  VOICE_PRESETS,
  VOICE_MAPPING,
  findVoiceByCharacteristics,
  getVoiceConfig,
  getVoicesForLanguage,
  defaultVoiceConfig,
  type VoiceCharacteristics,
  type VoiceSelectionConfig
} from './voices';

// Model configuration
export {
  AVAILABLE_MODELS,
  MODEL_PRESETS,
  selectModelByRequirements,
  calculateModelCost,
  defaultModelConfig,
  type ModelDefinition,
  type ModelConfig,
  type ModelUsage
} from './models';

// Audio format configuration
export {
  AUDIO_FORMATS,
  AUDIO_CONFIGS,
  AudioConverter,
  AudioFormatDetector,
  type AudioFormat
} from './audio-formats';

// Types and interfaces
export type {
  // Core configuration types
  AgentConfig,
  VoiceConfig,
  LLMConfig,
  VoiceAgentOptions,
  KeepAliveConfig,
  
  // Provider-specific types
  LLMProvider,
  ProviderLLMConfig,
  OpenAIConfig,
  AnthropicConfig,
  DeepgramLLMConfig,
  
  // Event types
  VoiceAgentEvent,
  UserStartedSpeakingEvent,
  UserStoppedSpeakingEvent,
  SpeechStartedEvent,
  UtteranceEndEvent,
  AgentThinkingEvent,
  AgentSpeakingEvent,
  ConversationStartedEvent,
  FunctionCallEvent,
  ErrorEvent,
  WarningEvent,
  MetadataEvent,
  
  // Handler types
  EventHandler,
  FunctionCallHandler,
  
  // State and context types
  ConversationContext,
  AudioChunk,
  FunctionDefinition,
  
  // Error types
  VoiceAgentError,
  ConnectionError,
  ConfigurationError
} from './types';

// Re-export schemas for runtime validation
export {
  VoiceConfigSchema,
  LLMConfigSchema,
  AgentConfigSchema
} from './types';

// Connection states enum
export { ConnectionState } from './types';

/**
 * Quick Start Example:
 * 
 * ```typescript
 * import { 
 *   DeepgramVoiceAgent, 
 *   PresetConfigs, 
 *   StandardEventHandlers 
 * } from '@stack-2025/deepgram-agent-core';
 * 
 * // Create agent with preset configuration
 * const agent = new DeepgramVoiceAgent(
 *   PresetConfigs.customerService().build(),
 *   { api_key: process.env.DEEPGRAM_API_KEY! }
 * );
 * 
 * // Set up event handlers
 * agent.on('UtteranceEnd', (event) => {
 *   console.log('User said:', event.data.alternatives[0]?.transcript);
 * });
 * 
 * agent.on('AgentSpeaking', () => {
 *   console.log('Agent is responding...');
 * });
 * 
 * // Register function handlers
 * agent.onFunction('get_current_time', async () => {
 *   return { time: new Date().toISOString() };
 * });
 * 
 * // Connect and start conversation
 * await agent.connect();
 * 
 * // Send audio data (from microphone, WebRTC, etc.)
 * agent.sendAudio(audioBuffer);
 * ```
 */

/**
 * Custom Configuration Example:
 * 
 * ```typescript
 * import { 
 *   DeepgramVoiceAgent,
 *   createVoiceAgentConfig,
 *   LLMProviders,
 *   VoiceModels,
 *   FunctionDefinitions
 * } from '@stack-2025/deepgram-agent-core';
 * 
 * // Build custom configuration
 * const config = createVoiceAgentConfig()
 *   .listen({
 *     model: 'nova-2-conversational',
 *     language: 'en',
 *     smart_format: true
 *   })
 *   .think(LLMProviders.anthropic({
 *     model: 'claude-3-5-sonnet-20241022',
 *     temperature: 0.7,
 *     system_prompt: 'You are a helpful assistant.',
 *     functions: [
 *       FunctionDefinitions.getCurrentTime(),
 *       FunctionDefinitions.getWeather()
 *     ]
 *   }))
 *   .speak(VoiceModels.english.asteria)
 *   .build();
 * 
 * const agent = new DeepgramVoiceAgent(config, {
 *   api_key: process.env.DEEPGRAM_API_KEY!,
 *   auto_reconnect: true,
 *   conversation_context: true
 * });
 * ```
 */

/**
 * Function Calling Example:
 * 
 * ```typescript
 * import { 
 *   DeepgramVoiceAgent,
 *   FunctionDefinitions
 * } from '@stack-2025/deepgram-agent-core';
 * 
 * // Add custom function
 * agent.addFunctions([
 *   FunctionDefinitions.custom(
 *     'order_pizza',
 *     'Order a pizza with specified toppings',
 *     {
 *       type: 'object',
 *       properties: {
 *         size: { type: 'string', enum: ['small', 'medium', 'large'] },
 *         toppings: { type: 'string' }
 *       },
 *       required: ['size']
 *     }
 *   )
 * ]);
 * 
 * // Handle function calls
 * agent.onFunction('order_pizza', async ({ size, toppings }) => {
 *   // Process pizza order
 *   return { 
 *     order_id: '12345',
 *     estimated_time: '30 minutes',
 *     total: '$15.99'
 *   };
 * });
 * ```
 */