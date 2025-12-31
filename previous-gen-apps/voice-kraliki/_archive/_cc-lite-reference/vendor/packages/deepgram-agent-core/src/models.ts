/**
 * Deepgram Voice Agent - Model Configuration
 * Model settings for Deepgram's Voice Agent API
 */

export interface ModelDefinition {
  id: string;
  name: string;
  provider: 'deepgram' | 'openai' | 'anthropic' | 'google' | 'groq' | 'meta';
  description: string;
  capabilities: string[];
  contextWindow: number;
  maxTokens: number;
  supportsFunctionCalling: boolean;
  responseTime: 'fast' | 'normal' | 'slow';
  quality: 'standard' | 'enhanced' | 'premium';
  cost: 'low' | 'medium' | 'high';
}

/**
 * Available LLM models for the thinking layer
 */
export const AVAILABLE_MODELS: Record<string, ModelDefinition> = {
  // OpenAI Models
  'gpt-4-turbo': {
    id: 'gpt-4-turbo',
    name: 'GPT-4 Turbo',
    provider: 'openai',
    description: 'Most capable model with vision, function calling, and JSON mode',
    capabilities: ['chat', 'function-calling', 'vision', 'json-mode'],
    contextWindow: 128000,
    maxTokens: 4096,
    supportsFunctionCalling: true,
    responseTime: 'normal',
    quality: 'premium',
    cost: 'high'
  },
  'gpt-4o': {
    id: 'gpt-4o',
    name: 'GPT-4o',
    provider: 'openai',
    description: 'Multimodal flagship model with vision and audio capabilities',
    capabilities: ['chat', 'function-calling', 'vision', 'audio'],
    contextWindow: 128000,
    maxTokens: 16384,
    supportsFunctionCalling: true,
    responseTime: 'fast',
    quality: 'premium',
    cost: 'high'
  },
  'gpt-4o-mini': {
    id: 'gpt-4o-mini',
    name: 'GPT-4o Mini',
    provider: 'openai',
    description: 'Affordable small model for fast, lightweight tasks',
    capabilities: ['chat', 'function-calling', 'vision'],
    contextWindow: 128000,
    maxTokens: 16384,
    supportsFunctionCalling: true,
    responseTime: 'fast',
    quality: 'standard',
    cost: 'low'
  },
  'gpt-3.5-turbo': {
    id: 'gpt-3.5-turbo',
    name: 'GPT-3.5 Turbo',
    provider: 'openai',
    description: 'Fast, efficient model for simple tasks',
    capabilities: ['chat', 'function-calling'],
    contextWindow: 16385,
    maxTokens: 4096,
    supportsFunctionCalling: true,
    responseTime: 'fast',
    quality: 'standard',
    cost: 'low'
  },

  // Anthropic Models
  'claude-3-opus': {
    id: 'claude-3-opus-20240229',
    name: 'Claude 3 Opus',
    provider: 'anthropic',
    description: 'Most powerful Claude model for complex tasks',
    capabilities: ['chat', 'vision', 'analysis'],
    contextWindow: 200000,
    maxTokens: 4096,
    supportsFunctionCalling: false,
    responseTime: 'normal',
    quality: 'premium',
    cost: 'high'
  },
  'claude-3-sonnet': {
    id: 'claude-3-sonnet-20240229',
    name: 'Claude 3 Sonnet',
    provider: 'anthropic',
    description: 'Balanced Claude model for most tasks',
    capabilities: ['chat', 'vision', 'analysis'],
    contextWindow: 200000,
    maxTokens: 4096,
    supportsFunctionCalling: false,
    responseTime: 'fast',
    quality: 'enhanced',
    cost: 'medium'
  },
  'claude-3-haiku': {
    id: 'claude-3-haiku-20240307',
    name: 'Claude 3 Haiku',
    provider: 'anthropic',
    description: 'Fast, lightweight Claude model',
    capabilities: ['chat', 'vision'],
    contextWindow: 200000,
    maxTokens: 4096,
    supportsFunctionCalling: false,
    responseTime: 'fast',
    quality: 'standard',
    cost: 'low'
  },

  // Google Models
  'gemini-1.5-pro': {
    id: 'gemini-1.5-pro',
    name: 'Gemini 1.5 Pro',
    provider: 'google',
    description: 'Advanced reasoning with 2M token context window',
    capabilities: ['chat', 'vision', 'code', 'function-calling'],
    contextWindow: 2097152,
    maxTokens: 8192,
    supportsFunctionCalling: true,
    responseTime: 'normal',
    quality: 'premium',
    cost: 'medium'
  },
  'gemini-1.5-flash': {
    id: 'gemini-1.5-flash',
    name: 'Gemini 1.5 Flash',
    provider: 'google',
    description: 'Fast multimodal model optimized for efficiency',
    capabilities: ['chat', 'vision', 'code', 'function-calling'],
    contextWindow: 1048576,
    maxTokens: 8192,
    supportsFunctionCalling: true,
    responseTime: 'fast',
    quality: 'enhanced',
    cost: 'low'
  },

  // Groq Models (Ultra-fast inference)
  'llama-3.1-70b': {
    id: 'llama-3.1-70b-versatile',
    name: 'Llama 3.1 70B',
    provider: 'groq',
    description: 'Large open model with ultra-fast inference',
    capabilities: ['chat', 'code'],
    contextWindow: 131072,
    maxTokens: 8192,
    supportsFunctionCalling: false,
    responseTime: 'fast',
    quality: 'enhanced',
    cost: 'low'
  },
  'mixtral-8x7b': {
    id: 'mixtral-8x7b-32768',
    name: 'Mixtral 8x7B',
    provider: 'groq',
    description: 'MoE model with fast inference',
    capabilities: ['chat', 'code'],
    contextWindow: 32768,
    maxTokens: 32768,
    supportsFunctionCalling: false,
    responseTime: 'fast',
    quality: 'standard',
    cost: 'low'
  },

  // Deepgram Nova Models (For comparison/fallback)
  'nova-2': {
    id: 'nova-2',
    name: 'Deepgram Nova-2',
    provider: 'deepgram',
    description: 'Deepgram\'s latest speech understanding model',
    capabilities: ['transcription', 'understanding'],
    contextWindow: 10000,
    maxTokens: 2048,
    supportsFunctionCalling: false,
    responseTime: 'fast',
    quality: 'enhanced',
    cost: 'low'
  }
};

/**
 * Model presets for different use cases
 */
export const MODEL_PRESETS = {
  customerService: {
    model: 'gpt-4o-mini',
    temperature: 0.7,
    maxTokens: 500,
    systemPrompt: 'You are a helpful customer service agent. Be friendly, professional, and solution-oriented.'
  },
  technicalSupport: {
    model: 'gpt-4-turbo',
    temperature: 0.3,
    maxTokens: 1000,
    systemPrompt: 'You are a technical support specialist. Provide accurate, detailed solutions to technical problems.'
  },
  sales: {
    model: 'gpt-4o',
    temperature: 0.8,
    maxTokens: 750,
    systemPrompt: 'You are a knowledgeable sales representative. Be persuasive but honest, focusing on customer needs.'
  },
  healthcare: {
    model: 'claude-3-opus',
    temperature: 0.2,
    maxTokens: 1000,
    systemPrompt: 'You are a healthcare information assistant. Provide accurate information but always recommend consulting healthcare professionals.'
  },
  finance: {
    model: 'gpt-4-turbo',
    temperature: 0.1,
    maxTokens: 1000,
    systemPrompt: 'You are a financial advisor assistant. Provide accurate financial information and always include appropriate disclaimers.'
  },
  education: {
    model: 'gemini-1.5-pro',
    temperature: 0.5,
    maxTokens: 1500,
    systemPrompt: 'You are an educational tutor. Explain concepts clearly and encourage learning through questions.'
  },
  quickResponse: {
    model: 'groq/llama-3.1-70b',
    temperature: 0.7,
    maxTokens: 200,
    systemPrompt: 'Provide quick, concise responses. Get to the point immediately.'
  }
};

/**
 * Model selection based on requirements
 */
export function selectModelByRequirements(
  requirements: {
    speed?: 'fast' | 'normal' | 'slow';
    quality?: 'standard' | 'enhanced' | 'premium';
    cost?: 'low' | 'medium' | 'high';
    capabilities?: string[];
    functionCalling?: boolean;
  }
): string {
  const models = Object.entries(AVAILABLE_MODELS);
  
  // Score each model based on requirements
  const scores = models.map(([id, model]) => {
    let score = 0;
    
    if (requirements.speed && model.responseTime === requirements.speed) score += 3;
    if (requirements.quality && model.quality === requirements.quality) score += 3;
    if (requirements.cost && model.cost === requirements.cost) score += 2;
    if (requirements.functionCalling && model.supportsFunctionCalling) score += 2;
    
    if (requirements.capabilities) {
      const matchedCapabilities = requirements.capabilities.filter(
        cap => model.capabilities.includes(cap)
      );
      score += matchedCapabilities.length;
    }
    
    return { id, score };
  });
  
  // Sort by score and return the best match
  scores.sort((a, b) => b.score - a.score);
  return scores[0]?.id || 'gpt-4o-mini';
}

/**
 * Model configuration interface
 */
export interface ModelConfig {
  model: string;
  temperature?: number;
  maxTokens?: number;
  topP?: number;
  frequencyPenalty?: number;
  presencePenalty?: number;
  systemPrompt?: string;
  stopSequences?: string[];
}

/**
 * Default model configuration
 */
export const defaultModelConfig: ModelConfig = {
  model: 'gpt-4o-mini',
  temperature: 0.7,
  maxTokens: 500,
  topP: 1.0,
  frequencyPenalty: 0,
  presencePenalty: 0,
  systemPrompt: 'You are a helpful AI assistant in a voice conversation. Keep responses concise and natural.'
};

/**
 * Model usage tracking
 */
export interface ModelUsage {
  model: string;
  inputTokens: number;
  outputTokens: number;
  totalCost: number;
  averageLatency: number;
  requestCount: number;
}

/**
 * Calculate estimated cost for model usage
 */
export function calculateModelCost(
  model: string,
  inputTokens: number,
  outputTokens: number
): number {
  // Simplified cost calculation (actual costs vary by provider)
  const costPerMillion = {
    'gpt-4-turbo': { input: 10, output: 30 },
    'gpt-4o': { input: 5, output: 15 },
    'gpt-4o-mini': { input: 0.15, output: 0.6 },
    'gpt-3.5-turbo': { input: 0.5, output: 1.5 },
    'claude-3-opus': { input: 15, output: 75 },
    'claude-3-sonnet': { input: 3, output: 15 },
    'claude-3-haiku': { input: 0.25, output: 1.25 },
    'gemini-1.5-pro': { input: 3.5, output: 10.5 },
    'gemini-1.5-flash': { input: 0.35, output: 1.05 },
    'llama-3.1-70b': { input: 0.59, output: 0.79 },
    'mixtral-8x7b': { input: 0.27, output: 0.27 },
    'nova-2': { input: 0.0008, output: 0 }
  };
  
  const costs = costPerMillion[model as keyof typeof costPerMillion] || { input: 1, output: 2 };
  
  return (inputTokens * costs.input + outputTokens * costs.output) / 1000000;
}