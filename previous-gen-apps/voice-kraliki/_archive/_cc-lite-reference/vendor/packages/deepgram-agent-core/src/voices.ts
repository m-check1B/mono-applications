/**
 * Deepgram Voice Agent - Voice Configuration
 * Comprehensive voice settings for Deepgram's Voice Agent API
 */

export interface VoiceCharacteristics {
  name: string;
  model: string;
  gender: 'male' | 'female' | 'neutral';
  accent: string;
  language: string;
  style: string;
  pitch?: 'low' | 'medium' | 'high';
  speed?: 'slow' | 'normal' | 'fast';
  description: string;
  useCase: string[];
  emotionalRange?: string[];
}

/**
 * Deepgram's Aura voices - High-quality TTS voices
 */
export const DEEPGRAM_VOICES: Record<string, VoiceCharacteristics> = {
  // English voices
  'asteria-en': {
    name: 'Asteria',
    model: 'aura-asteria-en',
    gender: 'female',
    accent: 'American',
    language: 'en-US',
    style: 'professional',
    pitch: 'medium',
    description: 'Clear, professional American female voice',
    useCase: ['customer service', 'business', 'education'],
    emotionalRange: ['neutral', 'friendly', 'professional']
  },
  'luna-en': {
    name: 'Luna',
    model: 'aura-luna-en',
    gender: 'female',
    accent: 'British',
    language: 'en-GB',
    style: 'warm',
    pitch: 'medium',
    description: 'Warm, friendly British female voice',
    useCase: ['hospitality', 'healthcare', 'support'],
    emotionalRange: ['empathetic', 'caring', 'supportive']
  },
  'stella-en': {
    name: 'Stella',
    model: 'aura-stella-en',
    gender: 'female',
    accent: 'American',
    language: 'en-US',
    style: 'energetic',
    pitch: 'high',
    description: 'Energetic, youthful American female voice',
    useCase: ['marketing', 'entertainment', 'retail'],
    emotionalRange: ['enthusiastic', 'upbeat', 'cheerful']
  },
  'athena-en': {
    name: 'Athena',
    model: 'aura-athena-en',
    gender: 'female',
    accent: 'British',
    language: 'en-GB',
    style: 'authoritative',
    pitch: 'low',
    description: 'Authoritative British female voice',
    useCase: ['news', 'documentation', 'corporate'],
    emotionalRange: ['confident', 'serious', 'trustworthy']
  },
  'hera-en': {
    name: 'Hera',
    model: 'aura-hera-en',
    gender: 'female',
    accent: 'American',
    language: 'en-US',
    style: 'sophisticated',
    pitch: 'medium',
    description: 'Sophisticated American female voice',
    useCase: ['luxury', 'finance', 'consulting'],
    emotionalRange: ['elegant', 'refined', 'professional']
  },
  'orion-en': {
    name: 'Orion',
    model: 'aura-orion-en',
    gender: 'male',
    accent: 'American',
    language: 'en-US',
    style: 'professional',
    pitch: 'medium',
    description: 'Professional American male voice',
    useCase: ['business', 'technical', 'education'],
    emotionalRange: ['neutral', 'informative', 'clear']
  },
  'perseus-en': {
    name: 'Perseus',
    model: 'aura-perseus-en',
    gender: 'male',
    accent: 'American',
    language: 'en-US',
    style: 'friendly',
    pitch: 'medium',
    description: 'Friendly, approachable American male voice',
    useCase: ['support', 'sales', 'hospitality'],
    emotionalRange: ['warm', 'helpful', 'engaging']
  },
  'angus-en': {
    name: 'Angus',
    model: 'aura-angus-en',
    gender: 'male',
    accent: 'Irish',
    language: 'en-IE',
    style: 'conversational',
    pitch: 'medium',
    description: 'Conversational Irish male voice',
    useCase: ['storytelling', 'tourism', 'entertainment'],
    emotionalRange: ['friendly', 'charming', 'engaging']
  },
  'arcas-en': {
    name: 'Arcas',
    model: 'aura-arcas-en',
    gender: 'male',
    accent: 'American',
    language: 'en-US',
    style: 'authoritative',
    pitch: 'low',
    description: 'Deep, authoritative American male voice',
    useCase: ['announcements', 'security', 'emergency'],
    emotionalRange: ['serious', 'commanding', 'trustworthy']
  },
  'zeus-en': {
    name: 'Zeus',
    model: 'aura-zeus-en',
    gender: 'male',
    accent: 'American',
    language: 'en-US',
    style: 'powerful',
    pitch: 'low',
    description: 'Powerful, commanding American male voice',
    useCase: ['executive', 'leadership', 'broadcasting'],
    emotionalRange: ['confident', 'decisive', 'strong']
  },

  // Multilingual voices - Aura-2 Spanish Voices
  
  // Peninsular Spanish voices
  'nestor-es': {
    name: 'Nestor',
    model: 'aura-2-nestor-es',
    gender: 'male',
    accent: 'Peninsular Spanish',
    language: 'es-ES',
    style: 'professional',
    pitch: 'medium',
    description: 'Calm, professional, approachable Spanish male voice',
    useCase: ['customer service', 'casual chat', 'business'],
    emotionalRange: ['calm', 'confident', 'clear']
  },
  'carina-es': {
    name: 'Carina',
    model: 'aura-2-carina-es',
    gender: 'female',
    accent: 'Peninsular Spanish',
    language: 'es-ES',
    style: 'energetic',
    pitch: 'medium',
    description: 'Professional, energetic Spanish female voice with raspy quality',
    useCase: ['customer service', 'IVR', 'interview'],
    emotionalRange: ['professional', 'confident', 'energetic']
  },
  'alvaro-es': {
    name: 'Alvaro',
    model: 'aura-2-alvaro-es',
    gender: 'male',
    accent: 'Peninsular Spanish',
    language: 'es-ES',
    style: 'professional',
    pitch: 'medium',
    description: 'Calm, professional, knowledgeable Spanish male voice',
    useCase: ['interview', 'customer service', 'education'],
    emotionalRange: ['calm', 'clear', 'approachable']
  },
  'diana-es': {
    name: 'Diana',
    model: 'aura-2-diana-es',
    gender: 'female',
    accent: 'Peninsular Spanish',
    language: 'es-ES',
    style: 'expressive',
    pitch: 'medium',
    description: 'Professional, confident, expressive Spanish female voice',
    useCase: ['storytelling', 'advertising', 'entertainment'],
    emotionalRange: ['confident', 'expressive', 'polite']
  },

  // Latin American Spanish voices
  'aquila-es': {
    name: 'Aquila',
    model: 'aura-2-aquila-es',
    gender: 'male',
    accent: 'Latin American Spanish',
    language: 'es-LA',
    style: 'enthusiastic',
    pitch: 'medium',
    description: 'Expressive, enthusiastic Latin American Spanish male voice',
    useCase: ['casual chat', 'informative', 'entertainment'],
    emotionalRange: ['enthusiastic', 'confident', 'casual']
  },
  'selena-es': {
    name: 'Selena',
    model: 'aura-2-selena-es',
    gender: 'female',
    accent: 'Latin American Spanish',
    language: 'es-LA',
    style: 'friendly',
    pitch: 'medium',
    description: 'Approachable, friendly Latin American Spanish female voice',
    useCase: ['customer service', 'informative', 'support'],
    emotionalRange: ['friendly', 'calm', 'positive']
  },

  // Mexican Spanish voices
  'estrella-es': {
    name: 'Estrella',
    model: 'aura-2-estrella-es',
    gender: 'female',
    accent: 'Mexican Spanish',
    language: 'es-MX',
    style: 'natural',
    pitch: 'medium',
    description: 'Approachable, natural Mexican Spanish female voice',
    useCase: ['casual chat', 'interview', 'hospitality'],
    emotionalRange: ['natural', 'calm', 'expressive']
  },
  'sirio-es': {
    name: 'Sirio',
    model: 'aura-2-sirio-es',
    gender: 'male',
    accent: 'Mexican Spanish',
    language: 'es-MX',
    style: 'empathetic',
    pitch: 'low',
    description: 'Calm, empathetic Mexican Spanish male voice with baritone quality',
    useCase: ['casual chat', 'interview', 'healthcare'],
    emotionalRange: ['empathetic', 'calm', 'comfortable']
  },

  // Colombian Spanish voice
  'celeste-es': {
    name: 'Celeste',
    model: 'aura-2-celeste-es',
    gender: 'female',
    accent: 'Colombian Spanish',
    language: 'es-CO',
    style: 'energetic',
    pitch: 'high',
    description: 'Clear, energetic Colombian Spanish female voice',
    useCase: ['casual chat', 'marketing', 'entertainment'],
    emotionalRange: ['energetic', 'positive', 'friendly']
  },

  // Legacy multilingual voice (keeping for compatibility)
  'asteria-es': {
    name: 'Asteria (Spanish)',
    model: 'aura-asteria-es',
    gender: 'female',
    accent: 'Neutral Spanish',
    language: 'es',
    style: 'professional',
    pitch: 'medium',
    description: 'Professional Spanish female voice (legacy)',
    useCase: ['customer service', 'business', 'education'],
    emotionalRange: ['neutral', 'friendly', 'professional']
  },
  'asteria-fr': {
    name: 'Asteria (French)',
    model: 'aura-asteria-fr',
    gender: 'female',
    accent: 'Parisian',
    language: 'fr',
    style: 'professional',
    pitch: 'medium',
    description: 'Professional French female voice',
    useCase: ['customer service', 'business', 'education'],
    emotionalRange: ['neutral', 'friendly', 'professional']
  },
  'asteria-de': {
    name: 'Asteria (German)',
    model: 'aura-asteria-de',
    gender: 'female',
    accent: 'Standard German',
    language: 'de',
    style: 'professional',
    pitch: 'medium',
    description: 'Professional German female voice',
    useCase: ['customer service', 'business', 'education'],
    emotionalRange: ['neutral', 'friendly', 'professional']
  },

  // Czech voices (Note: Deepgram doesn't have native Czech Aura voices yet)
  // These would fallback to external TTS providers
  'external-czech-kamila': {
    name: 'Kamila (Czech)',
    model: 'external-tts-czech-kamila',
    gender: 'female',
    accent: 'Czech',
    language: 'cs',
    style: 'professional',
    pitch: 'medium',
    description: 'Professional Czech female voice (external TTS)',
    useCase: ['customer service', 'business', 'education'],
    emotionalRange: ['neutral', 'friendly', 'professional']
  },
  'external-czech-pavel': {
    name: 'Pavel (Czech)',
    model: 'external-tts-czech-pavel',
    gender: 'male',
    accent: 'Czech',
    language: 'cs',
    style: 'friendly',
    pitch: 'medium',
    description: 'Friendly Czech male voice (external TTS)',
    useCase: ['support', 'sales', 'hospitality'],
    emotionalRange: ['warm', 'helpful', 'engaging']
  }
};

/**
 * Voice presets for different use cases
 */
export const VOICE_PRESETS = {
  customerService: {
    voice: 'asteria-en',
    speed: 'normal' as const,
    pitch: 'medium' as const,
    emotionalTone: 'friendly'
  },
  sales: {
    voice: 'perseus-en',
    speed: 'normal' as const,
    pitch: 'medium' as const,
    emotionalTone: 'enthusiastic'
  },
  support: {
    voice: 'luna-en',
    speed: 'normal' as const,
    pitch: 'medium' as const,
    emotionalTone: 'empathetic'
  },
  corporate: {
    voice: 'hera-en',
    speed: 'normal' as const,
    pitch: 'medium' as const,
    emotionalTone: 'professional'
  },
  emergency: {
    voice: 'arcas-en',
    speed: 'fast' as const,
    pitch: 'low' as const,
    emotionalTone: 'urgent'
  },
  education: {
    voice: 'orion-en',
    speed: 'slow' as const,
    pitch: 'medium' as const,
    emotionalTone: 'clear'
  },
  
  // Czech presets
  czechCustomerService: {
    voice: 'external-czech-kamila',
    speed: 'normal' as const,
    pitch: 'medium' as const,
    emotionalTone: 'professional'
  },
  czechSupport: {
    voice: 'external-czech-pavel',
    speed: 'normal' as const,
    pitch: 'medium' as const,
    emotionalTone: 'friendly'
  },

  // Spanish presets - Customer Service
  spanishCustomerService: {
    voice: 'nestor-es',
    speed: 'normal' as const,
    pitch: 'medium' as const,
    emotionalTone: 'professional'
  },
  spanishCustomerServiceFemale: {
    voice: 'selena-es',
    speed: 'normal' as const,
    pitch: 'medium' as const,
    emotionalTone: 'friendly'
  },

  // Spanish presets - Healthcare
  spanishHealthcare: {
    voice: 'sirio-es',
    speed: 'normal' as const,
    pitch: 'low' as const,
    emotionalTone: 'empathetic'
  },
  spanishHealthcareFemale: {
    voice: 'estrella-es',
    speed: 'normal' as const,
    pitch: 'medium' as const,
    emotionalTone: 'caring'
  },

  // Spanish presets - Sales
  spanishSales: {
    voice: 'aquila-es',
    speed: 'normal' as const,
    pitch: 'medium' as const,
    emotionalTone: 'enthusiastic'
  },
  spanishSalesFemale: {
    voice: 'celeste-es',
    speed: 'normal' as const,
    pitch: 'high' as const,
    emotionalTone: 'energetic'
  },

  // Spanish presets - Professional/Corporate
  spanishCorporate: {
    voice: 'alvaro-es',
    speed: 'normal' as const,
    pitch: 'medium' as const,
    emotionalTone: 'professional'
  },
  spanishCorporateFemale: {
    voice: 'carina-es',
    speed: 'normal' as const,
    pitch: 'medium' as const,
    emotionalTone: 'confident'
  },

  // Spanish presets - Entertainment/Marketing
  spanishMarketing: {
    voice: 'diana-es',
    speed: 'normal' as const,
    pitch: 'medium' as const,
    emotionalTone: 'expressive'
  }
};

/**
 * Voice mapping for compatibility with other providers
 */
export const VOICE_MAPPING = {
  // OpenAI to Deepgram mapping
  'alloy': 'orion-en',
  'echo': 'perseus-en',
  'fable': 'angus-en',
  'onyx': 'arcas-en',
  'nova': 'asteria-en',
  'shimmer': 'stella-en',
  
  // New OpenAI voices (2024)
  'ash': 'zeus-en',
  'ballad': 'angus-en',
  'coral': 'luna-en',
  'sage': 'athena-en',
  'verse': 'hera-en',
  
  // Gemini to Deepgram mapping
  'Aoede': 'asteria-en',
  'Puck': 'perseus-en',
  'Charon': 'arcas-en',
  'Kore': 'luna-en',
  'Fenrir': 'zeus-en',
  'Leda': 'hera-en',
  'Orus': 'orion-en',
  'Zephyr': 'stella-en'
};

/**
 * Get voice by characteristics
 */
export function findVoiceByCharacteristics(
  gender?: 'male' | 'female',
  style?: string,
  language?: string
): string {
  const voices = Object.entries(DEEPGRAM_VOICES);
  
  for (const [key, voice] of voices) {
    if (gender && voice.gender !== gender) continue;
    if (style && voice.style !== style) continue;
    if (language && !voice.language.startsWith(language)) continue;
    
    return key;
  }
  
  return 'asteria-en'; // Default voice
}

/**
 * Get voice configuration
 */
export function getVoiceConfig(voiceName: string): VoiceCharacteristics | undefined {
  return DEEPGRAM_VOICES[voiceName] || 
         DEEPGRAM_VOICES[VOICE_MAPPING[voiceName as keyof typeof VOICE_MAPPING]];
}

/**
 * Get available voices for a language
 */
export function getVoicesForLanguage(language: string): VoiceCharacteristics[] {
  return Object.values(DEEPGRAM_VOICES).filter(
    voice => voice.language.startsWith(language)
  );
}

/**
 * Voice selection configuration
 */
export interface VoiceSelectionConfig {
  defaultVoice: string;
  allowVoiceSelection: boolean;
  voiceSelectionMode: 'simple' | 'advanced';
  availableVoices: string[];
  voicePresets: typeof VOICE_PRESETS;
}

export const defaultVoiceConfig: VoiceSelectionConfig = {
  defaultVoice: 'asteria-en',
  allowVoiceSelection: true,
  voiceSelectionMode: 'simple',
  availableVoices: Object.keys(DEEPGRAM_VOICES),
  voicePresets: VOICE_PRESETS
};