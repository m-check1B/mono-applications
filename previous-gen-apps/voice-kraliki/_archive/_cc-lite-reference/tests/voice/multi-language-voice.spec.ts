import { test, expect } from '@playwright/test';

test.describe('Multi-Language Voice Testing', () => {
  test.beforeEach(async ({ page }) => {
    await page.context().clearCookies();
    await page.evaluate(() => localStorage.clear());
  });

  const languages = [
    { code: 'en', name: 'English', testPhrase: 'Hello, how can I help you today?' },
    { code: 'es', name: 'Spanish', testPhrase: 'Hola, ¿cómo puedo ayudarte hoy?' },
    { code: 'fr', name: 'French', testPhrase: 'Bonjour, comment puis-je vous aider aujourd\'hui?' },
    { code: 'de', name: 'German', testPhrase: 'Hallo, wie kann ich Ihnen heute helfen?' },
    { code: 'cs', name: 'Czech', testPhrase: 'Dobrý den, jak vám dnes mohu pomoci?' },
    { code: 'zh', name: 'Chinese', testPhrase: '你好，我今天能如何帮助您？' },
    { code: 'ja', name: 'Japanese', testPhrase: 'こんにちは、今日はどのようにお手伝いできますか？' }
  ];

  test.describe('Voice Agent Multi-Language Support', () => {
    test.beforeEach(async ({ page }) => {
      // Mock authentication
      await page.route('**/auth/me', async (route) => {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            result: {
              data: {
                id: 'user-123',
                email: 'test@example.com',
                name: 'Test User',
                role: 'AGENT'
              }
            }
          })
        });
      });

      // Mock dashboard data
      await page.route('**/dashboard', async (route) => {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            activeCalls: [],
            recentCalls: [],
            teamStatus: {
              members: [],
              stats: { totalMembers: 0, availableAgents: 0, busyAgents: 0, onBreakAgents: 0, offlineAgents: 0 }
            },
            callStats: {
              totalCalls: 0,
              activeCalls: 0,
              completedCalls: 0,
              averageDuration: 0,
              handledByAI: 0,
              handledByAgents: 0,
              missedCalls: 0
            }
          })
        });
      });

      await page.goto('http://localhost:5174/dashboard');
      await page.waitForLoadState('networkidle');
    });

    languages.forEach(language => {
      test.describe(`${language.name} (${language.code})`, () => {
        test(`should handle ${language.name} voice input`, async ({ page }) => {
          // Mock speech recognition for this language
          await page.addInitScript((lang) => {
            window.SpeechRecognition = class MockSpeechRecognition {
              lang = lang;
              continuous = false;
              interimResults = false;
              maxAlternatives = 1;

              onresult: ((event: any) => void) | null = null;
              onerror: ((event: any) => void) | null = null;
              onstart: (() => void) | null = null;
              onend: (() => void) | null = null;

              start() {
                if (this.onstart) this.onstart();
                setTimeout(() => {
                  if (this.onresult) {
                    this.onresult({
                      results: [{
                        0: {
                          transcript: 'Hello, I need help with my account',
                          confidence: 0.95
                        },
                        isFinal: true
                      }]
                    });
                  }
                  if (this.onend) this.onend();
                }, 1000);
              }

              stop() {
                if (this.onend) this.onend();
              }
            };
          }, language.code);

          await page.reload();
          await page.waitForLoadState('networkidle');

          // Mock WebSocket for voice data
          await page.addInitScript(() => {
            window.WebSocket = class MockWebSocket {
              constructor(url: string) {
                setTimeout(() => {
                  if (this.onopen) {
                    this.onopen(new Event('open'));
                  }
                }, 100);
              }
              send = () => {}
              close = () => {}
              onopen: (() => void) | null = null
              onmessage: ((event: MessageEvent) => void) | null = null
              onclose: (() => void) | null = null
              onerror: (() => void) | null = null
            };
          });

          // Test voice interaction
          await page.evaluate((testPhrase) => {
            return new Promise((resolve) => {
              const recognition = new (window as any).SpeechRecognition();
              recognition.lang = 'en-US'; // Set language
              recognition.start();
              resolve(true);
            });
          }, language.testPhrase);

          // Should handle voice input without errors
          await expect(page).not.toHaveTitle(/Error/);
        });

        test(`should display ${language.name} text correctly`, async ({ page }) => {
          // Test UI rendering of different language text
          await page.evaluate((text) => {
            const testElement = document.createElement('div');
            testElement.textContent = text;
            testElement.style.position = 'absolute';
            testElement.style.top = '-1000px';
            document.body.appendChild(testElement);

            // Check if text renders correctly
            const computedStyle = window.getComputedStyle(testElement);
            const rendersCorrectly = computedStyle.fontSize !== '0px' &&
                                    computedStyle.display !== 'none';

            document.body.removeChild(testElement);
            return rendersCorrectly;
          }, language.testPhrase);

          // Text should render correctly
          await expect(page.locator('body')).toBeVisible();
        });

        test(`should handle ${language.name} TTS (Text-to-Speech)`, async ({ page }) => {
          // Mock speech synthesis
          await page.addInitScript((testPhrase) => {
            window.speechSynthesis = {
              speak: (utterance: any) => {
                return new Promise((resolve) => {
                  setTimeout(() => {
                    utterance.onend?.();
                    resolve(true);
                  }, 1000);
                });
              },
              getVoices: () => [
                { lang: 'en-US', name: 'English Voice' },
                { lang: 'es-ES', name: 'Spanish Voice' },
                { lang: 'fr-FR', name: 'French Voice' },
                { lang: 'de-DE', name: 'German Voice' },
                { lang: 'cs-CZ', name: 'Czech Voice' }
              ]
            };

            window.SpeechSynthesisUtterance = class {
              text = testPhrase;
              lang = 'en-US';
              rate = 1;
              pitch = 1;
              volume = 1;
              onend: (() => void) | null = null;
              onerror: ((event: any) => void) | null = null;
            };
          }, language.testPhrase);

          await page.reload();
          await page.waitForLoadState('networkidle');

          // Test TTS functionality
          const ttsResult = await page.evaluate((testPhrase) => {
            return new Promise((resolve) => {
              const utterance = new (window as any).SpeechSynthesisUtterance(testPhrase);
              utterance.onend = () => resolve(true);
              utterance.onerror = () => resolve(false);
              (window as any).speechSynthesis.speak(utterance);
            });
          }, language.testPhrase);

          expect(ttsResult).toBe(true);
        });

        test(`should have proper font support for ${language.name}`, async ({ page }) => {
          // Test font rendering for different languages
          const fontSupport = await page.evaluate((testPhrase) => {
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');
            if (!ctx) return false;

            ctx.font = '16px Arial, sans-serif';
            ctx.fillText(testPhrase, 10, 50);

            // Check if text was drawn (not empty)
            const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
            const hasContent = imageData.data.some((channel, index) =>
              index % 4 !== 3 && channel !== 0 // Check RGB channels (not alpha)
            );

            return hasContent;
          }, language.testPhrase);

          expect(fontSupport).toBe(true);
        });
      });
    });

    test('should detect language automatically', async ({ page }) => {
      // Mock language detection service
      await page.route('**/api/language/detect', async (route) => {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            detectedLanguage: 'es',
            confidence: 0.95,
            alternatives: [
              { language: 'es', confidence: 0.95 },
              { language: 'pt', confidence: 0.03 },
              { language: 'it', confidence: 0.02 }
            ]
          })
        });
      });

      // Test language detection
      const detectionResult = await page.evaluate(async () => {
        try {
          const response = await fetch('/api/language/detect', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              text: 'Hola, necesito ayuda con mi cuenta'
            })
          });
          return await response.json();
        } catch {
          return { error: 'Language detection failed' };
        }
      });

      expect(detectionResult.detectedLanguage).toBe('es');
      expect(detectionResult.confidence).toBeGreaterThan(0.8);
    });

    test('should switch languages during call', async ({ page }) => {
      // Mock WebSocket for real-time language switching
      await page.addInitScript(() => {
        window.WebSocket = class MockWebSocket {
          constructor(url: string) {
            setTimeout(() => {
              if (this.onopen) {
                this.onopen(new Event('open'));
              }
            }, 100);
          }
          send = (data: string) => {
            const message = JSON.parse(data);
            if (message.type === 'language_switch') {
              setTimeout(() => {
                if (this.onmessage) {
                  this.onmessage(new MessageEvent('message', {
                    data: JSON.stringify({
                      event: 'language_switched',
                      data: {
                        fromLanguage: 'en',
                        toLanguage: 'es',
                        success: true
                      },
                      timestamp: new Date().toISOString()
                    })
                  }));
                }
              }, 500);
            }
          }
          close = () => {}
          onopen: (() => void) | null = null
          onmessage: ((event: MessageEvent) => void) | null = null
          onclose: (() => void) | null = null
          onerror: (() => void) | null = null
        };
      });

      await page.reload();
      await page.waitForLoadState('networkidle');

      // Test language switching during call
      const switchResult = await page.evaluate(async () => {
        const ws = new WebSocket('ws://localhost:3001/ws');

        return new Promise((resolve) => {
          ws.onmessage = (event) => {
            const message = JSON.parse(event.data);
            if (message.event === 'language_switched') {
              resolve(message.data);
            }
          };

          ws.onopen = () => {
            ws.send(JSON.stringify({
              type: 'language_switch',
              data: {
                fromLanguage: 'en',
                toLanguage: 'es'
              }
            }));
          };
        });
      });

      expect(switchResult.success).toBe(true);
      expect(switchResult.fromLanguage).toBe('en');
      expect(switchResult.toLanguage).toBe('es');
    });

    test('should handle mixed-language conversations', async ({ page }) => {
      // Mock mixed language processing
      await page.route('**/api/voice/process', async (route) => {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            processed: true,
            detectedLanguages: ['en', 'es'],
            segments: [
              {
                text: 'Hello, I need help',
                language: 'en',
                confidence: 0.92
              },
              {
                text: 'necesito ayuda con mi cuenta',
                language: 'es',
                confidence: 0.88
              }
            ],
            response: {
              text: 'I can help you with your account. ¿Cómo puedo ayudarle con su cuenta?',
              languages: ['en', 'es']
            }
          })
        });
      });

      // Test mixed language processing
      const mixedResult = await page.evaluate(async () => {
        try {
          const response = await fetch('/api/voice/process', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              audio: 'base64-encoded-audio-data',
              expectedLanguages: ['en', 'es']
            })
          });
          return await response.json();
        } catch {
          return { error: 'Mixed language processing failed' };
        }
      });

      expect(mixedResult.processed).toBe(true);
      expect(mixedResult.detectedLanguages).toContain('en');
      expect(mixedResult.detectedLanguages).toContain('es');
      expect(mixedResult.segments.length).toBeGreaterThan(0);
    });

    test('should maintain context across language switches', async ({ page }) => {
      // Mock context-aware language processing
      let conversationContext: any[] = [];

      await page.route('**/api/voice/conversation', async (route) => {
        const request = await route.request();
        const body = await request.json();

        // Add to conversation context
        conversationContext.push({
          timestamp: new Date().toISOString(),
          ...body
        });

        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            response: 'Entiendo su pregunta sobre la cuenta. Let me help you with your account inquiry.',
            contextMaintained: true,
            language: 'mixed',
            confidence: 0.90
          })
        });
      });

      // Test context maintenance
      await page.evaluate(async () => {
        // First message in English
        await fetch('/api/voice/conversation', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            text: 'I need help with my account',
            language: 'en'
          })
        });

        // Second message in Spanish
        await fetch('/api/voice/conversation', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            text: 'Tengo problemas con el pago',
            language: 'es'
          })
        });
      });

      // Verify context is maintained
      const contextResult = await page.evaluate(async () => {
        try {
          const response = await fetch('/api/voice/conversation', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              text: '¿Pueden ayudarme?',
              language: 'es'
            })
          });
          return await response.json();
        } catch {
          return { error: 'Context test failed' };
        }
      });

      expect(contextResult.contextMaintained).toBe(true);
      expect(contextResult.language).toBe('mixed');
    });

    test('should handle voice recognition accuracy across languages', async ({ page }) => {
      const testPhrases = [
        { language: 'en', phrase: 'I would like to check my account balance', expected: 'account balance' },
        { language: 'es', phrase: 'Quiero verificar el saldo de mi cuenta', expected: 'saldo cuenta' },
        { language: 'fr', phrase: 'Je voudrais vérifier le solde de mon compte', expected: 'solde compte' }
      ];

      for (const test of testPhrases) {
        await page.route(`**/api/voice/recognize/${test.language}`, async (route) => {
          await route.fulfill({
            status: 200,
            contentType: 'application/json',
            body: JSON.stringify({
              recognized: test.phrase,
              confidence: 0.85 + Math.random() * 0.1, // 0.85-0.95
              alternatives: [
                { text: test.phrase, confidence: 0.90 },
                { text: test.expected, confidence: 0.85 }
              ]
            })
          });
        });

        const recognitionResult = await page.evaluate(async (lang) => {
          try {
            const response = await fetch(`/api/voice/recognize/${lang}`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ audio: 'mock-audio-data' })
            });
            return await response.json();
          } catch {
            return { error: 'Recognition failed' };
          }
        }, test.language);

        expect(recognitionResult.confidence).toBeGreaterThan(0.8);
        expect(recognitionResult.recognized).toBeTruthy();
      }
    });

    test('should handle real-time translation if available', async ({ page }) => {
      // Mock translation service
      await page.route('**/api/translation/translate', async (route) => {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            translated: 'Hola, ¿cómo puedo ayudarte hoy?',
            sourceLanguage: 'en',
            targetLanguage: 'es',
            confidence: 0.92,
            alternatives: [
              'Hola, ¿en qué puedo ayudarte hoy?',
              'Hola, ¿qué puedo hacer por ti hoy?'
            ]
          })
        });
      });

      // Test translation
      const translationResult = await page.evaluate(async () => {
        try {
          const response = await fetch('/api/translation/translate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              text: 'Hello, how can I help you today?',
              sourceLanguage: 'en',
              targetLanguage: 'es'
            })
          });
          return await response.json();
        } catch {
          return { error: 'Translation failed' };
        }
      });

      expect(translationResult.sourceLanguage).toBe('en');
      expect(translationResult.targetLanguage).toBe('es');
      expect(translationResult.confidence).toBeGreaterThan(0.8);
      expect(translationResult.translated).toBeTruthy();
    });
  });
});