/** Demo configuration and feature flags for the Voice by Kraliki frontend.
 * 
 * This file provides centralized configuration for different demo scenarios
 * and feature flags to control UI functionality.
 */

export interface FeatureFlags {
  // AI Provider Features
  enableOpenAIRealtime: boolean;
  enableGeminiNativeAudio: boolean;
  enableDeepgramNova3: boolean;
  
  // Telephony Features
  enableTwilioMediaStream: boolean;
  enableTelnyxCallControl: boolean;
  enableWebhookValidation: boolean;
  
  // Session Management
  enablePersistentSessions: boolean;
  enableSessionRecovery: boolean;
  enableSessionAnalytics: boolean;
  
  // AI Automation Features
  enableFunctionCalling: boolean;
  enableAutoExecution: boolean;
  enableSentimentAnalysis: boolean;
  enableIntentDetection: boolean;
  
  // UI Features
  enableProviderSwitching: boolean;
  enableRealtimeTranscripts: boolean;
  enableSuggestionPanels: boolean;
  
  // Browser Channel
  enableBrowserChat: boolean;
  enableCobrowse: boolean;
  
  // Compliance and Security
  enableConsentCapture: boolean;
  enableRetentionControls: boolean;
  enableAuditLogging: boolean;
  
  // Monitoring and Observability
  enableMetricsCollection: boolean;
  enableDistributedTracing: boolean;
  enableHealthProbes: boolean;
  
  // Demo Specific
  demoMode: boolean;
  mockProviders: boolean;
  stressTestMode: boolean;
}

export interface DemoConfig {
  name: string;
  description: string;
  features: Partial<FeatureFlags>;
  providers: string[];
  scenarios: string[];
  ui: {
    theme: 'light' | 'dark' | 'auto';
    layout: 'compact' | 'full' | 'minimal';
    showAdvanced: boolean;
    showDebug: boolean;
  };
}

// Default feature flags
export const DEFAULT_FEATURE_FLAGS: FeatureFlags = {
  enableOpenAIRealtime: true,
  enableGeminiNativeAudio: true,
  enableDeepgramNova3: false,
  
  enableTwilioMediaStream: true,
  enableTelnyxCallControl: true,
  enableWebhookValidation: false,
  
  enablePersistentSessions: false,
  enableSessionRecovery: false,
  enableSessionAnalytics: false,
  
  enableFunctionCalling: false,
  enableAutoExecution: false,
  enableSentimentAnalysis: false,
  enableIntentDetection: false,
  
  enableProviderSwitching: true,
  enableRealtimeTranscripts: true,
  enableSuggestionPanels: false,
  
  enableBrowserChat: false,
  enableCobrowse: false,
  
  enableConsentCapture: false,
  enableRetentionControls: false,
  enableAuditLogging: true,
  
  enableMetricsCollection: false,
  enableDistributedTracing: false,
  enableHealthProbes: false,
  
  demoMode: false,
  mockProviders: false,
  stressTestMode: false,
};

// Demo configurations
export const DEMO_CONFIGS: Record<string, DemoConfig> = {
  basic_demo: {
    name: 'Basic AI Operator',
    description: 'Basic AI operator demo with single provider',
    features: {
      enableOpenAIRealtime: true,
      enableRealtimeTranscripts: true,
      demoMode: true,
    },
    providers: ['openai'],
    scenarios: ['inbound_call', 'outbound_call'],
    ui: {
      theme: 'light',
      layout: 'full',
      showAdvanced: false,
      showDebug: false,
    },
  },
  
  multi_provider_demo: {
    name: 'Multi-Provider Demo',
    description: 'Advanced demo with provider switching',
    features: {
      enableOpenAIRealtime: true,
      enableGeminiNativeAudio: true,
      enableProviderSwitching: true,
      enableRealtimeTranscripts: true,
      demoMode: true,
    },
    providers: ['openai', 'gemini'],
    scenarios: ['provider_switch', 'failover'],
    ui: {
      theme: 'dark',
      layout: 'full',
      showAdvanced: true,
      showDebug: true,
    },
  },
  
  ai_first_demo: {
    name: 'AI-First Experience',
    description: 'Full AI-first experience with automation',
    features: {
      enableOpenAIRealtime: true,
      enableGeminiNativeAudio: true,
      enableDeepgramNova3: true,
      enableFunctionCalling: true,
      enableAutoExecution: true,
      enableSentimentAnalysis: true,
      enableIntentDetection: true,
      enableSuggestionPanels: true,
      enableRealtimeTranscripts: true,
      demoMode: true,
    },
    providers: ['openai', 'gemini', 'deepgram'],
    scenarios: ['ai_automation', 'sentiment_analysis', 'intent_detection'],
    ui: {
      theme: 'dark',
      layout: 'full',
      showAdvanced: true,
      showDebug: true,
    },
  },
  
  compliance_demo: {
    name: 'Compliance Demo',
    description: 'Demo with compliance and consent features',
    features: {
      enableConsentCapture: true,
      enableRetentionControls: true,
      enableAuditLogging: true,
      demoMode: true,
    },
    providers: ['openai'],
    scenarios: ['consent_capture', 'data_retention'],
    ui: {
      theme: 'light',
      layout: 'compact',
      showAdvanced: true,
      showDebug: false,
    },
  },
  
  browser_channel_demo: {
    name: 'Browser Channel Demo',
    description: 'Browser-based engagement demo',
    features: {
      enableBrowserChat: true,
      enableCobrowse: true,
      enableRealtimeTranscripts: true,
      demoMode: true,
    },
    providers: ['openai'],
    scenarios: ['browser_chat', 'cobrowse'],
    ui: {
      theme: 'light',
      layout: 'full',
      showAdvanced: false,
      showDebug: true,
    },
  },
};

// Get current demo configuration from environment or localStorage
export function getCurrentDemoConfig(): DemoConfig {
  // Check environment variable first
  const demoType = import.meta.env.VITE_DEMO_TYPE || 
                   localStorage.getItem('demo_type') || 
                   'basic_demo';
  
  return DEMO_CONFIGS[demoType] || DEMO_CONFIGS.basic_demo;
}

// Get current feature flags
export function getCurrentFeatureFlags(): FeatureFlags {
  const demoConfig = getCurrentDemoConfig();
  
  // Merge default flags with demo-specific flags
  return {
    ...DEFAULT_FEATURE_FLAGS,
    ...demoConfig.features,
  };
}

// Check if a specific feature is enabled
export function isFeatureEnabled(feature: keyof FeatureFlags): boolean {
  const flags = getCurrentFeatureFlags();
  return flags[feature];
}

// Set demo configuration
export function setDemoConfig(demoType: string): void {
  if (DEMO_CONFIGS[demoType]) {
    localStorage.setItem('demo_type', demoType);
    // Reload to apply new configuration
    window.location.reload();
  }
}

// Export current configuration for easy access
export const currentDemoConfig = getCurrentDemoConfig();
export const currentFeatureFlags = getCurrentFeatureFlags();