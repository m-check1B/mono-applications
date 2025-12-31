import { describe, expect, it, beforeEach, afterEach } from 'vitest';
import { DeepgramAgentService } from '../../server/services/deepgram-agent-service';

const ORIGINAL_ENV = { ...process.env };

describe('DeepgramAgentService OpenRouter integration', () => {
  beforeEach(() => {
    process.env = { ...ORIGINAL_ENV };
    process.env.OPENROUTER_API_KEY = 'test-openrouter-key';
    process.env.OPENROUTER_MODEL = 'openrouter/openai/gpt-5';
    process.env.OPENROUTER_BASE_URL = 'https://openrouter.ai/api/v1';
  });

  afterEach(() => {
    process.env = { ...ORIGINAL_ENV };
  });

  it('uses OpenRouter as LLM provider when key present', () => {
    const service = new DeepgramAgentService({
      apiKey: 'deepgram-test',
      openRouterApiKey: process.env.OPENROUTER_API_KEY,
      enableLanguageDetection: true,
      enableLanguageRouting: true,
    });

    const config = service.getAgentConfig();
    expect(config.think.provider).toBe('openrouter');
    expect(config.think.model).toBe('openrouter/openai/gpt-5');
  });

  it('selects the Spanish voice model when language is es', () => {
    const service = new DeepgramAgentService({
      apiKey: 'deepgram-test',
      openRouterApiKey: process.env.OPENROUTER_API_KEY,
      language: 'es',
    });

    const config = service.getAgentConfig();
    expect(config.listen.language).toBe('es');
    expect(config.speak.model).toMatch(/aura-2-/);
  });
});
