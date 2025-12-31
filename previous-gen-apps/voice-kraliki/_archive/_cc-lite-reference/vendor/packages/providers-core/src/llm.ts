/**
 * Unified LLM Provider Interface
 * Supports multiple providers without vendor lock-in
 */

// Supported LLM Providers
export type LLMProvider = 
  | 'anthropic'
  | 'openai'
  | 'google'
  | 'azure-openai'
  | 'aws-bedrock'
  | 'local-ollama';

// Model identifiers with provider prefix
export type ModelId = 
  | 'anthropic/claude-3-opus'
  | 'anthropic/claude-3-sonnet'
  | 'anthropic/claude-3-haiku'
  | 'openai/gpt-4-turbo'
  | 'openai/gpt-4o'
  | 'openai/gpt-3.5-turbo'
  | 'google/gemini-1.5-pro'
  | 'google/gemini-1.5-flash'
  | string; // Allow custom models

// Common message format
export interface Message {
  role: 'system' | 'user' | 'assistant';
  content: string;
  name?: string;
}

// Common completion options
export interface CompletionOptions {
  model?: ModelId;
  temperature?: number;
  maxTokens?: number;
  stream?: boolean;
  stopSequences?: string[];
  tools?: Tool[];
}

// Tool/function calling support
export interface Tool {
  name: string;
  description: string;
  parameters: Record<string, any>; // JSON Schema
}

// Response format
export interface CompletionResponse {
  content: string;
  usage?: {
    promptTokens: number;
    completionTokens: number;
    totalTokens: number;
  };
  model: string;
  finishReason?: 'stop' | 'length' | 'tool_call';
  toolCalls?: ToolCall[];
}

export interface ToolCall {
  name: string;
  arguments: Record<string, any>;
}

// Main LLM client interface
export interface LLMClient {
  provider: LLMProvider;
  
  // Text completion
  complete(messages: Message[], options?: CompletionOptions): Promise<CompletionResponse>;
  
  // Streaming completion
  completeStream(messages: Message[], options?: CompletionOptions): AsyncIterable<string>;
  
  // Embeddings
  embed(texts: string[], model?: string): Promise<number[][]>;
  
  // List available models
  listModels(): Promise<ModelId[]>;
}

// Base implementation
export abstract class BaseLLMClient implements LLMClient {
  abstract provider: LLMProvider;
  
  constructor(protected config: {
    apiKey?: string;
    baseUrl?: string;
    defaultModel?: ModelId;
    timeout?: number;
  }) {}
  
  abstract complete(messages: Message[], options?: CompletionOptions): Promise<CompletionResponse>;
  
  abstract completeStream(messages: Message[], options?: CompletionOptions): AsyncIterable<string>;
  
  abstract embed(texts: string[], model?: string): Promise<number[][]>;
  
  abstract listModels(): Promise<ModelId[]>;
}

// Factory for creating clients
export class LLMProviderFactory {
  private static providers = new Map<LLMProvider, typeof BaseLLMClient>();
  
  static register(provider: LLMProvider, clientClass: typeof BaseLLMClient) {
    this.providers.set(provider, clientClass);
  }
  
  static create(provider: LLMProvider, config: any): LLMClient {
    const ClientClass = this.providers.get(provider);
    if (!ClientClass) {
      throw new Error(`Provider ${provider} not registered`);
    }
    return new (ClientClass as any)(config);
  }
}