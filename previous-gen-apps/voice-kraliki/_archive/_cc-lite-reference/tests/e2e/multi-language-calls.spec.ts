/**
 * Multi-Language Calls E2E Tests for Voice by Kraliki
 * Tests language detection, switching, and multi-language call handling
 */
import { test, expect, Page, Browser } from '@playwright/test';

const BASE_URL = process.env.BASE_URL || 'http://127.0.0.1:3007';
const API_BASE = process.env.API_BASE || 'http://127.0.0.1:3010';

// Test credentials for different language scenarios
const TEST_AGENTS = {
  english: {
    email: 'agent.english@cc-light.local',
    password: process.env.DEFAULT_AGENT_PASSWORD || 'agent123',
    languages: ['en']
  },
  spanish: {
    email: 'agent.spanish@cc-light.local',
    password: process.env.DEFAULT_AGENT_PASSWORD || 'agent123',
    languages: ['es', 'en']
  },
  multilingual: {
    email: 'agent.multilingual@cc-light.local',
    password: process.env.DEFAULT_AGENT_PASSWORD || 'agent123',
    languages: ['en', 'es', 'fr']
  }
};

const SUPERVISOR = {
  email: 'supervisor@cc-light.local',
  password: process.env.DEFAULT_SUPERVISOR_PASSWORD || 'supervisor123'
};

test.describe('Multi-Language Calls E2E Tests', () => {
  let browser: Browser;
  let agentPage: Page;
  let supervisorPage: Page;
  let customerPage: Page;

  test.beforeAll(async ({ browser: b }) => {
    browser = b;
  });

  test.beforeEach(async () => {
    agentPage = await browser.newPage();
    supervisorPage = await browser.newPage();
    customerPage = await browser.newPage();
  });

  test.afterEach(async () => {
    await agentPage.close();
    await supervisorPage.close();
    await customerPage.close();
  });

  describe('Language Detection and Routing', () => {
    test('should detect customer language and route to appropriate agent', async () => {
      // Login supervisor to monitor routing
      await supervisorPage.goto(`${BASE_URL}/login`);
      await supervisorPage.fill('[data-testid="email-input"]', SUPERVISOR.email);
      await supervisorPage.fill('[data-testid="password-input"]', SUPERVISOR.password);
      await supervisorPage.click('[data-testid="login-button"]');
      await supervisorPage.waitForURL(`${BASE_URL}/supervisor`);

      // Login Spanish-speaking agent
      await agentPage.goto(`${BASE_URL}/login`);
      await agentPage.fill('[data-testid="email-input"]', TEST_AGENTS.spanish.email);
      await agentPage.fill('[data-testid="password-input"]', TEST_AGENTS.spanish.password);
      await agentPage.click('[data-testid="login-button"]');
      await agentPage.waitForURL(`${BASE_URL}/operator`);

      // Set agent status to available
      await agentPage.click('[data-testid="agent-status-toggle"]');
      await agentPage.selectOption('[data-testid="status-select"]', 'available');

      // Simulate incoming Spanish call
      await customerPage.goto(`${BASE_URL}/call-simulator`);
      await customerPage.fill('[data-testid="customer-message"]', 'Hola, necesito ayuda con mi cuenta, por favor.');
      await customerPage.selectOption('[data-testid="language-preference"]', 'es');
      await customerPage.click('[data-testid="initiate-call-button"]');

      // Verify call was routed to Spanish-speaking agent
      await agentPage.waitForSelector('[data-testid="incoming-call-notification"]', { timeout: 10000 });
      const callLanguage = await agentPage.locator('[data-testid="call-language-indicator"]').textContent();
      expect(callLanguage).toBe('Spanish');

      // Accept the call
      await agentPage.click('[data-testid="accept-call-button"]');

      // Verify call details show correct language detection
      const detectedLanguage = await agentPage.locator('[data-testid="detected-language"]').textContent();
      expect(detectedLanguage).toBe('es');

      // Verify supervisor can see the language routing
      await supervisorPage.click('[data-testid="active-calls-tab"]');
      const callRow = supervisorPage.locator('[data-testid="call-row"]').first();
      const callLanguageSuper = await callRow.locator('[data-testid="call-language"]').textContent();
      expect(callLanguageSuper).toBe('Spanish');
    });

    test('should handle mixed language detection scenarios', async () => {
      await agentPage.goto(`${BASE_URL}/login`);
      await agentPage.fill('[data-testid="email-input"]', TEST_AGENTS.multilingual.email);
      await agentPage.fill('[data-testid="password-input"]', TEST_AGENTS.multilingual.password);
      await agentPage.click('[data-testid="login-button"]');
      await agentPage.waitForURL(`${BASE_URL}/operator`);

      await agentPage.click('[data-testid="agent-status-toggle"]');
      await agentPage.selectOption('[data-testid="status-select"]', 'available');

      // Simulate call with mixed language content
      await customerPage.goto(`${BASE_URL}/call-simulator`);
      await customerPage.fill('[data-testid="customer-message"]', 'Hello, je voudrais parler français s\'il vous plaît.');
      await customerPage.click('[data-testid="initiate-call-button"]');

      await agentPage.waitForSelector('[data-testid="incoming-call-notification"]');
      await agentPage.click('[data-testid="accept-call-button"]');

      // Check mixed language detection
      const languageAnalysis = await agentPage.locator('[data-testid="language-analysis"]').textContent();
      expect(languageAnalysis).toContain('Mixed');

      const detectedLanguages = await agentPage.locator('[data-testid="detected-languages"]').textContent();
      expect(detectedLanguages).toContain('English');
      expect(detectedLanguages).toContain('French');
    });

    test('should fall back to default language for unsupported languages', async () => {
      await agentPage.goto(`${BASE_URL}/login`);
      await agentPage.fill('[data-testid="email-input"]', TEST_AGENTS.english.email);
      await agentPage.fill('[data-testid="password-input"]', TEST_AGENTS.english.password);
      await agentPage.click('[data-testid="login-button"]');
      await agentPage.waitForURL(`${BASE_URL}/operator`);

      await agentPage.click('[data-testid="agent-status-toggle"]');
      await agentPage.selectOption('[data-testid="status-select"]', 'available');

      // Simulate call in unsupported language (e.g., Mandarin)
      await customerPage.goto(`${BASE_URL}/call-simulator`);
      await customerPage.fill('[data-testid="customer-message"]', '你好，我需要帮助');
      await customerPage.click('[data-testid="initiate-call-button"]');

      await agentPage.waitForSelector('[data-testid="incoming-call-notification"]');
      await agentPage.click('[data-testid="accept-call-button"]');

      // Verify fallback to English
      const fallbackNotice = await agentPage.locator('[data-testid="language-fallback-notice"]');
      await expect(fallbackNotice).toBeVisible();
      await expect(fallbackNotice).toContainText('Unsupported language detected. Defaulting to English.');

      const activeLanguage = await agentPage.locator('[data-testid="active-language"]').textContent();
      expect(activeLanguage).toBe('English');
    });
  });

  describe('Language Switching During Calls', () => {
    test('should allow seamless language switching mid-call', async () => {
      // Setup multilingual agent
      await agentPage.goto(`${BASE_URL}/login`);
      await agentPage.fill('[data-testid="email-input"]', TEST_AGENTS.multilingual.email);
      await agentPage.fill('[data-testid="password-input"]', TEST_AGENTS.multilingual.password);
      await agentPage.click('[data-testid="login-button"]');
      await agentPage.waitForURL(`${BASE_URL}/operator`);

      await agentPage.click('[data-testid="agent-status-toggle"]');
      await agentPage.selectOption('[data-testid="status-select"]', 'available');

      // Start call in English
      await customerPage.goto(`${BASE_URL}/call-simulator`);
      await customerPage.fill('[data-testid="customer-message"]', 'Hello, I need help with my account.');
      await customerPage.selectOption('[data-testid="language-preference"]', 'en');
      await customerPage.click('[data-testid="initiate-call-button"]');

      await agentPage.waitForSelector('[data-testid="incoming-call-notification"]');
      await agentPage.click('[data-testid="accept-call-button"]');

      // Verify initial language
      let activeLanguage = await agentPage.locator('[data-testid="active-language"]').textContent();
      expect(activeLanguage).toBe('English');

      // Customer switches to Spanish
      await customerPage.fill('[data-testid="customer-message"]', 'Prefiero continuar en español, por favor.');
      await customerPage.click('[data-testid="send-message-button"]');

      // Wait for language detection and switching
      await agentPage.waitForSelector('[data-testid="language-switch-notification"]');

      // Verify language switched
      activeLanguage = await agentPage.locator('[data-testid="active-language"]').textContent();
      expect(activeLanguage).toBe('Spanish');

      // Check that agent interface updated
      const agentInputPlaceholder = await agentPage.locator('[data-testid="agent-response-input"]').getAttribute('placeholder');
      expect(agentInputPlaceholder).toContain('español'); // Spanish placeholder text

      // Agent responds in Spanish
      await agentPage.fill('[data-testid="agent-response-input"]', '¡Por supuesto! Puedo ayudarle en español.');
      await agentPage.click('[data-testid="send-response-button"]');

      // Verify response sent in correct language
      const lastMessage = agentPage.locator('[data-testid="conversation-message"]').last();
      await expect(lastMessage).toContainText('español');
      const messageLanguage = await lastMessage.getAttribute('data-language');
      expect(messageLanguage).toBe('es');
    });

    test('should handle rapid language switches gracefully', async () => {
      await agentPage.goto(`${BASE_URL}/login`);
      await agentPage.fill('[data-testid="email-input"]', TEST_AGENTS.multilingual.email);
      await agentPage.fill('[data-testid="password-input"]', TEST_AGENTS.multilingual.password);
      await agentPage.click('[data-testid="login-button"]');
      await agentPage.waitForURL(`${BASE_URL}/operator`);

      await agentPage.click('[data-testid="agent-status-toggle"]');
      await agentPage.selectOption('[data-testid="status-select"]', 'available');

      await customerPage.goto(`${BASE_URL}/call-simulator`);
      await customerPage.fill('[data-testid="customer-message"]', 'Hello there');
      await customerPage.click('[data-testid="initiate-call-button"]');

      await agentPage.waitForSelector('[data-testid="incoming-call-notification"]');
      await agentPage.click('[data-testid="accept-call-button"]');

      // Rapid language switches
      const messages = [
        { text: 'Hola', expectedLang: 'Spanish' },
        { text: 'Bonjour', expectedLang: 'French' },
        { text: 'Back to English', expectedLang: 'English' },
        { text: '¿Puedes ayudarme?', expectedLang: 'Spanish' }
      ];

      for (const message of messages) {
        await customerPage.fill('[data-testid="customer-message"]', message.text);
        await customerPage.click('[data-testid="send-message-button"]');
        await agentPage.waitForTimeout(1500); // Allow for language processing

        const activeLanguage = await agentPage.locator('[data-testid="active-language"]').textContent();
        expect(activeLanguage).toBe(message.expectedLang);
      }

      // Verify no errors occurred during rapid switching
      const errorNotifications = await agentPage.locator('[data-testid="error-notification"]').count();
      expect(errorNotifications).toBe(0);
    });

    test('should maintain conversation context across language switches', async () => {
      await agentPage.goto(`${BASE_URL}/login`);
      await agentPage.fill('[data-testid="email-input"]', TEST_AGENTS.multilingual.email);
      await agentPage.fill('[data-testid="password-input"]', TEST_AGENTS.multilingual.password);
      await agentPage.click('[data-testid="login-button"]');
      await agentPage.waitForURL(`${BASE_URL}/operator`);

      await agentPage.click('[data-testid="agent-status-toggle"]');
      await agentPage.selectOption('[data-testid="status-select"]', 'available');

      await customerPage.goto(`${BASE_URL}/call-simulator`);
      await customerPage.fill('[data-testid="customer-message"]', 'My account number is 123456789 and I have a billing issue.');
      await customerPage.click('[data-testid="initiate-call-button"]');

      await agentPage.waitForSelector('[data-testid="incoming-call-notification"]');
      await agentPage.click('[data-testid="accept-call-button"]');

      // Verify context extraction
      await agentPage.waitForSelector('[data-testid="extracted-entities"]');
      const accountNumber = await agentPage.locator('[data-testid="account-number"]').textContent();
      expect(accountNumber).toBe('123456789');

      // Switch to Spanish
      await customerPage.fill('[data-testid="customer-message"]', 'Sí, es sobre esa cuenta que mencioné.');
      await customerPage.click('[data-testid="send-message-button"]');

      await agentPage.waitForTimeout(2000);

      // Verify context preserved across language switch
      const preservedAccountNumber = await agentPage.locator('[data-testid="account-number"]').textContent();
      expect(preservedAccountNumber).toBe('123456789');

      const contextPreserved = await agentPage.locator('[data-testid="context-preserved-indicator"]');
      await expect(contextPreserved).toBeVisible();
    });
  });

  describe('Multi-language Transcription and Translation', () => {
    test('should provide real-time transcription in detected language', async () => {
      await supervisorPage.goto(`${BASE_URL}/login`);
      await supervisorPage.fill('[data-testid="email-input"]', SUPERVISOR.email);
      await supervisorPage.fill('[data-testid="password-input"]', SUPERVISOR.password);
      await supervisorPage.click('[data-testid="login-button"]');
      await supervisorPage.waitForURL(`${BASE_URL}/supervisor`);

      await agentPage.goto(`${BASE_URL}/login`);
      await agentPage.fill('[data-testid="email-input"]', TEST_AGENTS.spanish.email);
      await agentPage.fill('[data-testid="password-input"]', TEST_AGENTS.spanish.password);
      await agentPage.click('[data-testid="login-button"]');
      await agentPage.waitForURL(`${BASE_URL}/operator`);

      await agentPage.click('[data-testid="agent-status-toggle"]');
      await agentPage.selectOption('[data-testid="status-select"]', 'available');

      // Enable voice transcription
      await customerPage.goto(`${BASE_URL}/call-simulator`);
      await customerPage.click('[data-testid="enable-voice-simulation"]');
      await customerPage.selectOption('[data-testid="voice-language"]', 'es');
      await customerPage.click('[data-testid="initiate-voice-call-button"]');

      await agentPage.waitForSelector('[data-testid="incoming-call-notification"]');
      await agentPage.click('[data-testid="accept-call-button"]');

      // Simulate Spanish voice input
      await customerPage.click('[data-testid="simulate-voice-input"]');
      await customerPage.fill('[data-testid="voice-simulation-text"]', 'Buenos días, tengo un problema con mi factura.');
      await customerPage.click('[data-testid="play-voice-simulation"]');

      // Verify real-time Spanish transcription
      await agentPage.waitForSelector('[data-testid="live-transcription"]');
      const transcription = await agentPage.locator('[data-testid="transcription-text"]').textContent();
      expect(transcription).toContain('factura');

      const transcriptionLanguage = await agentPage.locator('[data-testid="transcription-language"]').textContent();
      expect(transcriptionLanguage).toBe('Spanish');

      // Verify supervisor can see transcription
      await supervisorPage.click('[data-testid="active-calls-tab"]');
      await supervisorPage.click('[data-testid="call-row"]');
      const supervisorTranscription = await supervisorPage.locator('[data-testid="call-transcription"]').textContent();
      expect(supervisorTranscription).toContain('factura');
    });

    test('should provide translation assistance for non-native speakers', async () => {
      await agentPage.goto(`${BASE_URL}/login`);
      await agentPage.fill('[data-testid="email-input"]', TEST_AGENTS.english.email); // English-only agent
      await agentPage.fill('[data-testid="password-input"]', TEST_AGENTS.english.password);
      await agentPage.click('[data-testid="login-button"]');
      await agentPage.waitForURL(`${BASE_URL}/operator`);

      await agentPage.click('[data-testid="agent-status-toggle"]');
      await agentPage.selectOption('[data-testid="status-select"]', 'available');

      // Enable translation assistance
      await agentPage.click('[data-testid="enable-translation-assistant"]');

      await customerPage.goto(`${BASE_URL}/call-simulator`);
      await customerPage.fill('[data-testid="customer-message"]', 'Hola, necesito ayuda con mi cuenta.');
      await customerPage.selectOption('[data-testid="language-preference"]', 'es');
      await customerPage.click('[data-testid="initiate-call-button"]');

      await agentPage.waitForSelector('[data-testid="incoming-call-notification"]');
      await agentPage.click('[data-testid="accept-call-button"]');

      // Verify translation provided
      await agentPage.waitForSelector('[data-testid="translation-assistant"]');
      const translatedText = await agentPage.locator('[data-testid="translated-customer-message"]').textContent();
      expect(translatedText).toContain('Hello, I need help with my account');

      // Agent types response in English
      await agentPage.fill('[data-testid="agent-response-input"]', 'I can help you with your account. What specific issue are you having?');
      await agentPage.click('[data-testid="send-with-translation-button"]');

      // Verify response was translated to Spanish for customer
      const translatedResponse = await agentPage.locator('[data-testid="translated-agent-response"]').textContent();
      expect(translatedResponse).toContain('cuenta');
      expect(translatedResponse).toContain('problema');
    });

    test('should handle voice synthesis in multiple languages', async () => {
      await agentPage.goto(`${BASE_URL}/login`);
      await agentPage.fill('[data-testid="email-input"]', TEST_AGENTS.multilingual.email);
      await agentPage.fill('[data-testid="password-input"]', TEST_AGENTS.multilingual.password);
      await agentPage.click('[data-testid="login-button"]');
      await agentPage.waitForURL(`${BASE_URL}/operator`);

      await agentPage.click('[data-testid="agent-status-toggle"]');
      await agentPage.selectOption('[data-testid="status-select"]', 'available');

      // Enable voice synthesis
      await agentPage.click('[data-testid="enable-voice-synthesis"]');

      await customerPage.goto(`${BASE_URL}/call-simulator`);
      await customerPage.click('[data-testid="enable-voice-simulation"]');
      await customerPage.selectOption('[data-testid="voice-language"]', 'fr');
      await customerPage.click('[data-testid="initiate-voice-call-button"]');

      await agentPage.waitForSelector('[data-testid="incoming-call-notification"]');
      await agentPage.click('[data-testid="accept-call-button"]');

      // Customer speaks in French
      await customerPage.fill('[data-testid="voice-simulation-text"]', 'Bonjour, pouvez-vous m\'aider?');
      await customerPage.click('[data-testid="play-voice-simulation"]');

      // Agent responds with voice synthesis in French
      await agentPage.fill('[data-testid="agent-response-input"]', 'Bien sûr, je peux vous aider.');
      await agentPage.selectOption('[data-testid="synthesis-voice"]', 'fr-female-claire');
      await agentPage.click('[data-testid="send-with-voice-button"]');

      // Verify voice synthesis settings
      const synthesisLanguage = await agentPage.locator('[data-testid="current-synthesis-language"]').textContent();
      expect(synthesisLanguage).toBe('French');

      // Verify audio generated
      const audioElement = agentPage.locator('[data-testid="synthesized-audio"]');
      await expect(audioElement).toBeVisible();

      const audioDuration = await audioElement.getAttribute('data-duration');
      expect(parseFloat(audioDuration || '0')).toBeGreaterThan(0);
    });
  });

  describe('Language-specific Agent Skills and Routing', () => {
    test('should route calls based on agent language skills', async () => {
      await supervisorPage.goto(`${BASE_URL}/login`);
      await supervisorPage.fill('[data-testid="email-input"]', SUPERVISOR.email);
      await supervisorPage.fill('[data-testid="password-input"]', SUPERVISOR.password);
      await supervisorPage.click('[data-testid="login-button"]');
      await supervisorPage.waitForURL(`${BASE_URL}/supervisor`);

      // Configure agent language skills
      await supervisorPage.click('[data-testid="agents-management-tab"]');
      await supervisorPage.click('[data-testid="edit-agent-skills"]');
      await supervisorPage.selectOption('[data-testid="agent-select"]', TEST_AGENTS.spanish.email);
      await supervisorPage.check('[data-testid="language-skill-es"]');
      await supervisorPage.check('[data-testid="language-skill-en"]');
      await supervisorPage.click('[data-testid="save-agent-skills"]');

      // Start multiple agents with different language skills
      const spanishAgentPage = await browser.newPage();
      const englishAgentPage = await browser.newPage();

      await spanishAgentPage.goto(`${BASE_URL}/login`);
      await spanishAgentPage.fill('[data-testid="email-input"]', TEST_AGENTS.spanish.email);
      await spanishAgentPage.fill('[data-testid="password-input"]', TEST_AGENTS.spanish.password);
      await spanishAgentPage.click('[data-testid="login-button"]');
      await spanishAgentPage.click('[data-testid="agent-status-toggle"]');
      await spanishAgentPage.selectOption('[data-testid="status-select"]', 'available');

      await englishAgentPage.goto(`${BASE_URL}/login`);
      await englishAgentPage.fill('[data-testid="email-input"]', TEST_AGENTS.english.email);
      await englishAgentPage.fill('[data-testid="password-input"]', TEST_AGENTS.english.password);
      await englishAgentPage.click('[data-testid="login-button"]');
      await englishAgentPage.click('[data-testid="agent-status-toggle"]');
      await englishAgentPage.selectOption('[data-testid="status-select"]', 'available');

      // Simulate Spanish call
      await customerPage.goto(`${BASE_URL}/call-simulator`);
      await customerPage.fill('[data-testid="customer-message"]', 'Necesito ayuda en español.');
      await customerPage.selectOption('[data-testid="language-preference"]', 'es');
      await customerPage.click('[data-testid="initiate-call-button"]');

      // Verify Spanish call routed to Spanish-capable agent
      await spanishAgentPage.waitForSelector('[data-testid="incoming-call-notification"]', { timeout: 5000 });
      const englishAgentNotification = await englishAgentPage.locator('[data-testid="incoming-call-notification"]').count();
      expect(englishAgentNotification).toBe(0);

      await spanishAgentPage.close();
      await englishAgentPage.close();
    });

    test('should handle language skill priority and preferences', async () => {
      await supervisorPage.goto(`${BASE_URL}/login`);
      await supervisorPage.fill('[data-testid="email-input"]', SUPERVISOR.email);
      await supervisorPage.fill('[data-testid="password-input"]', SUPERVISOR.password);
      await supervisorPage.click('[data-testid="login-button"]');

      // Set language routing preferences
      await supervisorPage.click('[data-testid="call-routing-settings"]');
      await supervisorPage.selectOption('[data-testid="routing-strategy"]', 'language_priority');
      await supervisorPage.check('[data-testid="prefer-native-speakers"]');
      await supervisorPage.click('[data-testid="save-routing-settings"]');

      // Monitor routing decisions
      await customerPage.goto(`${BASE_URL}/call-simulator`);
      await customerPage.fill('[data-testid="customer-message"]', 'Je voudrais de l\'aide en français.');
      await customerPage.selectOption('[data-testid="language-preference"]', 'fr');
      await customerPage.click('[data-testid="initiate-call-button"]');

      // Check routing decision in supervisor dashboard
      await supervisorPage.click('[data-testid="routing-decisions-tab"]');
      await supervisorPage.waitForSelector('[data-testid="routing-decision-entry"]');

      const routingReason = await supervisorPage.locator('[data-testid="routing-reason"]').textContent();
      expect(routingReason).toContain('language preference');

      const selectedAgent = await supervisorPage.locator('[data-testid="routed-to-agent"]').textContent();
      expect(selectedAgent).toBe(TEST_AGENTS.multilingual.email);
    });
  });

  describe('Multi-language Analytics and Reporting', () => {
    test('should generate language-specific call analytics', async () => {
      await supervisorPage.goto(`${BASE_URL}/login`);
      await supervisorPage.fill('[data-testid="email-input"]', SUPERVISOR.email);
      await supervisorPage.fill('[data-testid="password-input"]', SUPERVISOR.password);
      await supervisorPage.click('[data-testid="login-button"]');

      // Navigate to analytics dashboard
      await supervisorPage.click('[data-testid="analytics-tab"]');
      await supervisorPage.click('[data-testid="language-analytics-subtab"]');

      // Wait for language analytics to load
      await supervisorPage.waitForSelector('[data-testid="language-distribution-chart"]');

      // Verify language distribution chart
      const chartData = await supervisorPage.locator('[data-testid="language-chart-data"]').textContent();
      expect(chartData).toContain('English');
      expect(chartData).toContain('Spanish');

      // Check language-specific metrics
      const englishCallCount = await supervisorPage.locator('[data-testid="english-call-count"]').textContent();
      const spanishCallCount = await supervisorPage.locator('[data-testid="spanish-call-count"]').textContent();

      expect(parseInt(englishCallCount || '0')).toBeGreaterThanOrEqual(0);
      expect(parseInt(spanishCallCount || '0')).toBeGreaterThanOrEqual(0);

      // Verify language-specific performance metrics
      const avgResolutionTimeEnglish = await supervisorPage.locator('[data-testid="avg-resolution-english"]').textContent();
      const avgResolutionTimeSpanish = await supervisorPage.locator('[data-testid="avg-resolution-spanish"]').textContent();

      expect(avgResolutionTimeEnglish).toMatch(/\d+:\d+/); // MM:SS format
      expect(avgResolutionTimeSpanish).toMatch(/\d+:\d+/);
    });

    test('should track language switching patterns and effectiveness', async () => {
      await supervisorPage.goto(`${BASE_URL}/login`);
      await supervisorPage.fill('[data-testid="email-input"]', SUPERVISOR.email);
      await supervisorPage.fill('[data-testid="password-input"]', SUPERVISOR.password);
      await supervisorPage.click('[data-testid="login-button"]');

      await supervisorPage.click('[data-testid="analytics-tab"]');
      await supervisorPage.click('[data-testid="language-switching-analytics"]');

      // Wait for switching analytics
      await supervisorPage.waitForSelector('[data-testid="switching-patterns-chart"]');

      // Verify switching statistics
      const totalSwitches = await supervisorPage.locator('[data-testid="total-language-switches"]').textContent();
      const avgSwitchesPerCall = await supervisorPage.locator('[data-testid="avg-switches-per-call"]').textContent();
      const switchSuccessRate = await supervisorPage.locator('[data-testid="switch-success-rate"]').textContent();

      expect(parseInt(totalSwitches || '0')).toBeGreaterThanOrEqual(0);
      expect(parseFloat(avgSwitchesPerCall || '0')).toBeGreaterThanOrEqual(0);
      expect(parseFloat(switchSuccessRate || '0')).toBeGreaterThanOrEqual(0);

      // Check most common switching patterns
      const commonPatterns = await supervisorPage.locator('[data-testid="common-switch-patterns"]');
      await expect(commonPatterns).toBeVisible();

      const patternList = await commonPatterns.locator('[data-testid="pattern-item"]').count();
      expect(patternList).toBeGreaterThan(0);
    });

    test('should export multi-language call reports', async () => {
      await supervisorPage.goto(`${BASE_URL}/login`);
      await supervisorPage.fill('[data-testid="email-input"]', SUPERVISOR.email);
      await supervisorPage.fill('[data-testid="password-input"]', SUPERVISOR.password);
      await supervisorPage.click('[data-testid="login-button"]');

      await supervisorPage.click('[data-testid="reports-tab"]');

      // Configure multi-language report
      await supervisorPage.click('[data-testid="create-new-report-button"]');
      await supervisorPage.selectOption('[data-testid="report-type"]', 'multi_language_analysis');
      await supervisorPage.selectOption('[data-testid="date-range"]', 'last_week');
      await supervisorPage.check('[data-testid="include-transcriptions"]');
      await supervisorPage.check('[data-testid="include-translations"]');
      await supervisorPage.check('[data-testid="include-language-switches"]');

      // Generate and download report
      const downloadPromise = supervisorPage.waitForEvent('download');
      await supervisorPage.click('[data-testid="generate-report-button"]');
      await supervisorPage.click('[data-testid="download-report-button"]');

      const download = await downloadPromise;
      expect(download.suggestedFilename()).toContain('multi_language');
      expect(download.suggestedFilename()).toMatch(/\.(csv|xlsx|pdf)$/);
    });
  });

  describe('Error Handling and Edge Cases', () => {
    test('should handle translation service failures gracefully', async () => {
      // Mock translation service failure
      await agentPage.route('**/api/translate', route => {
        route.fulfill({
          status: 503,
          body: JSON.stringify({ error: 'Translation service unavailable' })
        });
      });

      await agentPage.goto(`${BASE_URL}/login`);
      await agentPage.fill('[data-testid="email-input"]', TEST_AGENTS.english.email);
      await agentPage.fill('[data-testid="password-input"]', TEST_AGENTS.english.password);
      await agentPage.click('[data-testid="login-button"]');

      await agentPage.click('[data-testid="agent-status-toggle"]');
      await agentPage.selectOption('[data-testid="status-select"]', 'available');
      await agentPage.click('[data-testid="enable-translation-assistant"]');

      await customerPage.goto(`${BASE_URL}/call-simulator`);
      await customerPage.fill('[data-testid="customer-message"]', 'Hola, necesito ayuda.');
      await customerPage.click('[data-testid="initiate-call-button"]');

      await agentPage.waitForSelector('[data-testid="incoming-call-notification"]');
      await agentPage.click('[data-testid="accept-call-button"]');

      // Verify graceful failure handling
      await agentPage.waitForSelector('[data-testid="translation-error-notice"]');
      const errorMessage = await agentPage.locator('[data-testid="translation-error-notice"]').textContent();
      expect(errorMessage).toContain('Translation service unavailable');

      // Verify fallback options are provided
      await expect(agentPage.locator('[data-testid="manual-translation-mode"]')).toBeVisible();
      await expect(agentPage.locator('[data-testid="escalate-to-multilingual-agent"]')).toBeVisible();
    });

    test('should handle incomplete or corrupted language detection', async () => {
      await agentPage.goto(`${BASE_URL}/login`);
      await agentPage.fill('[data-testid="email-input"]', TEST_AGENTS.multilingual.email);
      await agentPage.fill('[data-testid="password-input"]', TEST_AGENTS.multilingual.password);
      await agentPage.click('[data-testid="login-button"]');

      await agentPage.click('[data-testid="agent-status-toggle"]');
      await agentPage.selectOption('[data-testid="status-select"]', 'available');

      // Simulate corrupted or incomplete language input
      const problematicInputs = [
        '', // Empty
        '...', // Only punctuation
        '123 456 789', // Only numbers
        'asdf qwerty zxcv', // Nonsense text
        '🙂😊😀', // Only emojis
      ];

      await customerPage.goto(`${BASE_URL}/call-simulator`);
      await customerPage.click('[data-testid="initiate-call-button"]');

      await agentPage.waitForSelector('[data-testid="incoming-call-notification"]');
      await agentPage.click('[data-testid="accept-call-button"]');

      for (const input of problematicInputs) {
        await customerPage.fill('[data-testid="customer-message"]', input);
        await customerPage.click('[data-testid="send-message-button"]');
        await agentPage.waitForTimeout(1000);

        // Verify system handles gracefully
        const errorCount = await agentPage.locator('[data-testid="language-detection-error"]').count();
        expect(errorCount).toBe(0);

        // Should default to a fallback language
        const detectedLanguage = await agentPage.locator('[data-testid="detected-language"]').textContent();
        expect(detectedLanguage).toMatch(/^(Unknown|English|Undetermined)$/);
      }
    });
  });
});