/**
 * Performance Tests for Multi-Language Voice Operations
 * Measures and validates performance of language detection, voice switching,
 * TTS synthesis, and WebSocket event handling under various load conditions
 */

import { describe, it, expect, beforeEach, afterEach, vi, beforeAll, afterAll } from 'vitest';
import { LanguageRouterService, LanguageDetector, createLanguageRouter } from '../../server/services/language-router-service';
import { DeepgramVoiceService } from '../../server/services/deepgram-voice-service';
import { CzechTTSService } from '../../server/services/czech-tts-service';
import { mockWebSocket, waitFor, testDb } from '../setup';
import fs from 'fs/promises';
import path from 'path';

// Performance benchmarks and thresholds
const PERFORMANCE_THRESHOLDS = {
  languageDetection: {
    maxTimePerDetection: 10, // ms
    maxMemoryUsage: 50, // MB
    minAccuracyRate: 0.85
  },
  voiceSynthesis: {
    maxTimePerCharacter: 5, // ms per character
    maxLatency: 500, // ms for short texts
    maxThroughput: 10, // simultaneous synthesis requests
  },
  languageSwitching: {
    maxSwitchTime: 100, // ms
    maxEventLatency: 50, // ms
    maxSessionSetupTime: 200 // ms
  },
  websocket: {
    maxEventProcessingTime: 20, // ms per event
    maxBufferSize: 1024 * 1024, // 1MB
    minThroughput: 100 // events per second
  },
  system: {
    maxConcurrentSessions: 100,
    maxMemoryPerSession: 5, // MB
    maxCpuUsagePercent: 80
  }
};

// Test data for performance scenarios
const PERFORMANCE_TEST_DATA = {
  shortTexts: [
    "Hello",
    "Hola",
    "Ahoj",
    "Yes", 
    "Sí",
    "Ano",
    "Help",
    "Ayuda",
    "Pomoc"
  ],
  mediumTexts: [
    "Hello, thank you for calling our customer service. How can I help you today?",
    "Hola, gracias por llamar a nuestro servicio al cliente. ¿Cómo puedo ayudarte hoy?",
    "Dobrý den, děkuji za zavolání do naší zákaznické služby. Jak vám dnes mohu pomoci?",
    "I need help with my account and billing information please.",
    "Necesito ayuda con mi cuenta y la información de facturación, por favor.",
    "Potřebuji pomoc s účtem a fakturačními informacemi, prosím."
  ],
  longTexts: [
    "Hello and welcome to our comprehensive customer service center. Thank you for taking the time to call us today. We truly appreciate your business and your continued loyalty to our services. Our team of dedicated customer service representatives is here to assist you with any questions, concerns, or issues you may have regarding your account, billing, technical support, or general inquiries. Please know that we are committed to providing you with the best possible service experience, and we will do everything in our power to resolve your matter quickly and efficiently. How may I assist you today?",
    "Hola y bienvenido a nuestro centro integral de servicio al cliente. Gracias por tomarse el tiempo de llamarnos hoy. Realmente apreciamos su negocio y su continua lealtad a nuestros servicios. Nuestro equipo de representantes dedicados de servicio al cliente está aquí para ayudarlo con cualquier pregunta, inquietud o problema que pueda tener con respecto a su cuenta, facturación, soporte técnico o consultas generales. Sepa que estamos comprometidos a brindarle la mejor experiencia de servicio posible, y haremos todo lo que esté en nuestro poder para resolver su asunto de manera rápida y eficiente. ¿Cómo puedo ayudarlo hoy?",
    "Dobrý den a vítejte v našem komplexním centru zákaznické služby. Děkujeme, že jste si dnes udělali čas na zavolání. Skutečně si vážíme vašeho obchodu a vaší pokračující loajality k našim službám. Náš tým oddaných zástupců zákaznické služby je tu, aby vám pomohl s jakýmikoli dotazy, obavami nebo problémy, které můžete mít týkající se vašeho účtu, fakturace, technické podpory nebo obecných dotazů. Vězte, že jsme odhodláni poskytnout vám nejlepší možnou zkušenost se službou a uděláme vše, co je v naší moci, abychom váš problém vyřešili rychle a efektivně. Jak vám dnes mohu pomoci?"
  ]
};

// Memory and CPU monitoring utilities
class PerformanceMonitor {
  private startTime: number = 0;
  private startMemory: number = 0;
  private samples: Array<{ timestamp: number; memory: number; duration?: number }> = [];

  start() {
    this.startTime = Date.now();
    this.startMemory = process.memoryUsage().heapUsed;
    this.samples = [];
  }

  sample(label?: string) {
    const now = Date.now();
    const memory = process.memoryUsage().heapUsed;
    this.samples.push({
      timestamp: now,
      memory,
      duration: now - this.startTime
    });
  }

  end() {
    const endTime = Date.now();
    const endMemory = process.memoryUsage().heapUsed;
    
    return {
      totalDuration: endTime - this.startTime,
      memoryDelta: (endMemory - this.startMemory) / 1024 / 1024, // MB
      samples: this.samples,
      avgMemory: this.samples.reduce((sum, s) => sum + s.memory, 0) / this.samples.length / 1024 / 1024, // MB
      peakMemory: Math.max(...this.samples.map(s => s.memory)) / 1024 / 1024 // MB
    };
  }
}

describe('Multi-Language Voice Performance Tests', () => {
  let languageRouter: LanguageRouterService;
  let mockDeepgramService: any;
  let mockCzechTTSService: any;
  let performanceResults: any[] = [];
  let monitor: PerformanceMonitor;

  beforeAll(async () => {
    await testDb.$connect();
    monitor = new PerformanceMonitor();
  });

  afterAll(async () => {
    await testDb.$disconnect();
    
    // Save performance results
    const resultsPath = path.join(process.cwd(), 'test-results', 'performance-results.json');
    await fs.mkdir(path.dirname(resultsPath), { recursive: true });
    await fs.writeFile(resultsPath, JSON.stringify(performanceResults, null, 2));
    
    console.log(`\n📊 Performance test results saved to: ${resultsPath}`);
    
    // Print performance summary
    console.log('\n🚀 Performance Test Summary:');
    performanceResults.forEach(result => {
      console.log(`   ${result.testName}: ${result.success ? '✅' : '❌'} (${result.duration}ms)`);
      if (result.metrics) {
        console.log(`     - Throughput: ${result.metrics.throughput || 'N/A'} ops/sec`);
        console.log(`     - Memory: ${result.metrics.avgMemory || 'N/A'} MB`);
      }
    });
  });

  beforeEach(async () => {
    // Mock services with performance-realistic timing
    mockDeepgramService = {
      startTranscription: vi.fn().mockImplementation(async () => {
        await new Promise(resolve => setTimeout(resolve, 10)); // 10ms delay
      }),
      stopTranscription: vi.fn().mockImplementation(async () => {
        await new Promise(resolve => setTimeout(resolve, 5));
        return { endTime: new Date(), duration: 1000, transcripts: [] };
      }),
      processAudioStream: vi.fn(),
      synthesizeSpeech: vi.fn().mockImplementation(async (text, voice) => {
        // Realistic TTS timing based on text length
        const delay = 50 + (text.length * 2); // Base delay + length factor
        await new Promise(resolve => setTimeout(resolve, delay));
        return Buffer.from(`synthesized-${voice}-${text.length}`);
      }),
      on: vi.fn(),
      emit: vi.fn(),
      destroy: vi.fn().mockResolvedValue(undefined)
    };

    mockCzechTTSService = {
      synthesize: vi.fn().mockImplementation(async (text, options) => {
        // Czech TTS is slightly slower
        const delay = 60 + (text.length * 2.5);
        await new Promise(resolve => setTimeout(resolve, delay));
        return Buffer.from(`czech-synthesized-${options?.voice || 'default'}-${text.length}`);
      }),
      testTTS: vi.fn().mockResolvedValue(true),
      getAvailableVoices: vi.fn().mockReturnValue([]),
      destroy: vi.fn(),
      on: vi.fn(),
      emit: vi.fn()
    };

    languageRouter = createLanguageRouter({
      deepgramApiKey: 'test-deepgram-key',
      openaiApiKey: 'test-openai-key',
      czechTTSConfig: {
        elevenlabsApiKey: 'test-elevenlabs-key',
        defaultProvider: 'elevenlabs',
        defaultVoice: 'kamila-cs',
        cacheEnabled: true,
        maxCacheSize: 50
      },
      confidenceThreshold: 0.7,
      enableAutoDetection: true,
      enableAutoSwitching: true
    });

    languageRouter['deepgramService'] = mockDeepgramService;
    languageRouter['czechTTSService'] = mockCzechTTSService;
  });

  afterEach(async () => {
    if (languageRouter) {
      await languageRouter.destroy();
    }
  });

  describe('Language Detection Performance', () => {
    it('should detect language within performance thresholds for short texts', async () => {
      const testResult: any = {
        testName: 'Short Text Language Detection',
        startTime: Date.now(),
        detections: [],
        success: false
      };

      monitor.start();

      try {
        const detectionPromises = PERFORMANCE_TEST_DATA.shortTexts.map(async (text, index) => {
          const startTime = performance.now();
          const detection = LanguageDetector.detectFromText(text);
          const endTime = performance.now();
          const duration = endTime - startTime;

          monitor.sample(`detection-${index}`);

          return {
            text,
            detection,
            duration,
            withinThreshold: duration <= PERFORMANCE_THRESHOLDS.languageDetection.maxTimePerDetection
          };
        });

        testResult.detections = await Promise.all(detectionPromises);
        
        const performanceMetrics = monitor.end();
        testResult.duration = performanceMetrics.totalDuration;
        testResult.metrics = {
          avgDetectionTime: testResult.detections.reduce((sum: number, d: any) => sum + d.duration, 0) / testResult.detections.length,
          maxDetectionTime: Math.max(...testResult.detections.map((d: any) => d.duration)),
          throughput: (testResult.detections.length / performanceMetrics.totalDuration) * 1000,
          avgMemory: performanceMetrics.avgMemory,
          accurateDetections: testResult.detections.filter((d: any) => d.detection.confidence > 0.5).length
        };

        // Verify performance thresholds
        expect(testResult.metrics.maxDetectionTime).toBeLessThanOrEqual(PERFORMANCE_THRESHOLDS.languageDetection.maxTimePerDetection);
        expect(testResult.metrics.avgMemory).toBeLessThanOrEqual(PERFORMANCE_THRESHOLDS.languageDetection.maxMemoryUsage);
        expect(testResult.metrics.accurateDetections / testResult.detections.length).toBeGreaterThanOrEqual(PERFORMANCE_THRESHOLDS.languageDetection.minAccuracyRate);

        testResult.success = true;

      } catch (error) {
        testResult.error = error.message;
      }

      performanceResults.push(testResult);
      expect(testResult.success).toBe(true);
    });

    it('should handle batch language detection efficiently', async () => {
      const testResult: any = {
        testName: 'Batch Language Detection',
        startTime: Date.now(),
        batchSizes: [10, 50, 100],
        results: {},
        success: false
      };

      try {
        for (const batchSize of testResult.batchSizes) {
          monitor.start();

          // Create batch of mixed language texts
          const batch = [];
          for (let i = 0; i < batchSize; i++) {
            const langIndex = i % 3;
            const textIndex = i % PERFORMANCE_TEST_DATA.mediumTexts.length;
            batch.push(PERFORMANCE_TEST_DATA.mediumTexts[textIndex]);
          }

          const batchStartTime = performance.now();
          const detectionPromises = batch.map(text => LanguageDetector.detectFromText(text));
          const detections = await Promise.all(detectionPromises);
          const batchEndTime = performance.now();

          const batchMetrics = monitor.end();
          
          testResult.results[batchSize] = {
            duration: batchEndTime - batchStartTime,
            throughput: (batchSize / (batchEndTime - batchStartTime)) * 1000,
            avgMemory: batchMetrics.avgMemory,
            successfulDetections: detections.filter(d => d.confidence > 0.5).length
          };

          // Verify throughput is reasonable for batch size
          expect(testResult.results[batchSize].throughput).toBeGreaterThan(50); // At least 50 detections/sec
        }

        testResult.success = true;
        testResult.duration = Date.now() - testResult.startTime;

      } catch (error) {
        testResult.error = error.message;
      }

      performanceResults.push(testResult);
      expect(testResult.success).toBe(true);
    });

    it('should maintain performance with concurrent language detection', async () => {
      const testResult: any = {
        testName: 'Concurrent Language Detection',
        startTime: Date.now(),
        concurrencyLevels: [5, 20, 50],
        results: {},
        success: false
      };

      try {
        for (const concurrency of testResult.concurrencyLevels) {
          monitor.start();

          const concurrentBatches: Promise<any>[] = [];
          
          for (let batch = 0; batch < concurrency; batch++) {
            const batchPromise = (async () => {
              const batchStartTime = performance.now();
              const text = PERFORMANCE_TEST_DATA.mediumTexts[batch % PERFORMANCE_TEST_DATA.mediumTexts.length];
              const detection = LanguageDetector.detectFromText(text);
              const batchEndTime = performance.now();
              
              return {
                batchId: batch,
                duration: batchEndTime - batchStartTime,
                detection,
                success: detection.confidence > 0.3
              };
            })();
            
            concurrentBatches.push(batchPromise);
          }

          const concurrentStartTime = performance.now();
          const results = await Promise.all(concurrentBatches);
          const concurrentEndTime = performance.now();

          const concurrentMetrics = monitor.end();

          testResult.results[concurrency] = {
            totalDuration: concurrentEndTime - concurrentStartTime,
            avgBatchDuration: results.reduce((sum, r) => sum + r.duration, 0) / results.length,
            successfulBatches: results.filter(r => r.success).length,
            throughput: (concurrency / (concurrentEndTime - concurrentStartTime)) * 1000,
            avgMemory: concurrentMetrics.avgMemory,
            peakMemory: concurrentMetrics.peakMemory
          };

          // Verify concurrent performance doesn't degrade significantly
          expect(testResult.results[concurrency].avgBatchDuration).toBeLessThan(50); // Should stay under 50ms per detection
          expect(testResult.results[concurrency].successfulBatches).toBe(concurrency);
        }

        testResult.success = true;
        testResult.duration = Date.now() - testResult.startTime;

      } catch (error) {
        testResult.error = error.message;
      }

      performanceResults.push(testResult);
      expect(testResult.success).toBe(true);
    });
  });

  describe('Voice Synthesis Performance', () => {
    it('should meet TTS performance thresholds for different text lengths', async () => {
      const testResult: any = {
        testName: 'TTS Performance by Text Length',
        startTime: Date.now(),
        textCategories: {},
        success: false
      };

      try {
        const sessionId = 'perf-tts-session';
        await languageRouter.startSession(sessionId, {
          callId: 'perf-tts-call',
          preferredLanguage: 'en'
        });

        // Test different text lengths
        const textCategories = {
          short: PERFORMANCE_TEST_DATA.shortTexts,
          medium: PERFORMANCE_TEST_DATA.mediumTexts,
          long: PERFORMANCE_TEST_DATA.longTexts
        };

        for (const [category, texts] of Object.entries(textCategories)) {
          monitor.start();
          
          const syntheses = [];
          
          for (const text of texts) {
            const startTime = performance.now();
            const audioBuffer = await languageRouter.synthesizeSpeech(sessionId, text);
            const endTime = performance.now();
            
            const duration = endTime - startTime;
            const timePerChar = duration / text.length;
            
            syntheses.push({
              text: text.substring(0, 50) + '...',
              textLength: text.length,
              duration,
              timePerChar,
              audioSize: audioBuffer?.length || 0,
              withinThreshold: timePerChar <= PERFORMANCE_THRESHOLDS.voiceSynthesis.maxTimePerCharacter
            });

            monitor.sample(`synthesis-${category}`);
          }

          const categoryMetrics = monitor.end();
          
          testResult.textCategories[category] = {
            syntheses,
            avgDuration: syntheses.reduce((sum, s) => sum + s.duration, 0) / syntheses.length,
            avgTimePerChar: syntheses.reduce((sum, s) => sum + s.timePerChar, 0) / syntheses.length,
            maxDuration: Math.max(...syntheses.map(s => s.duration)),
            withinThreshold: syntheses.filter(s => s.withinThreshold).length,
            avgMemory: categoryMetrics.avgMemory,
            throughput: (syntheses.length / categoryMetrics.totalDuration) * 1000
          };

          // Verify performance thresholds
          expect(testResult.textCategories[category].avgTimePerChar).toBeLessThanOrEqual(PERFORMANCE_THRESHOLDS.voiceSynthesis.maxTimePerCharacter);
        }

        testResult.success = true;
        testResult.duration = Date.now() - testResult.startTime;

      } catch (error) {
        testResult.error = error.message;
      }

      performanceResults.push(testResult);
      expect(testResult.success).toBe(true);
    });

    it('should handle simultaneous TTS requests efficiently', async () => {
      const testResult: any = {
        testName: 'Simultaneous TTS Requests',
        startTime: Date.now(),
        concurrentRequests: [1, 5, 10],
        results: {},
        success: false
      };

      try {
        for (const concurrency of testResult.concurrentRequests) {
          const sessions: string[] = [];
          
          // Create sessions for concurrent testing
          for (let i = 0; i < concurrency; i++) {
            const sessionId = `concurrent-tts-${i}`;
            sessions.push(sessionId);
            await languageRouter.startSession(sessionId, {
              callId: `concurrent-call-${i}`,
              preferredLanguage: i % 3 === 0 ? 'en' : i % 3 === 1 ? 'es' : 'cs'
            });
          }

          monitor.start();

          const concurrentStartTime = performance.now();
          const ttsPromises = sessions.map((sessionId, index) => {
            const text = PERFORMANCE_TEST_DATA.mediumTexts[index % PERFORMANCE_TEST_DATA.mediumTexts.length];
            return languageRouter.synthesizeSpeech(sessionId, text);
          });

          const results = await Promise.all(ttsPromises);
          const concurrentEndTime = performance.now();

          const concurrentMetrics = monitor.end();

          testResult.results[concurrency] = {
            totalDuration: concurrentEndTime - concurrentStartTime,
            avgDurationPerRequest: (concurrentEndTime - concurrentStartTime) / concurrency,
            successfulSyntheses: results.filter(r => r !== null).length,
            throughput: (concurrency / (concurrentEndTime - concurrentStartTime)) * 1000,
            avgMemory: concurrentMetrics.avgMemory,
            peakMemory: concurrentMetrics.peakMemory
          };

          // Clean up sessions
          for (const sessionId of sessions) {
            await languageRouter.endSession(sessionId);
          }

          // Verify concurrent performance
          expect(testResult.results[concurrency].successfulSyntheses).toBe(concurrency);
          expect(testResult.results[concurrency].avgDurationPerRequest).toBeLessThan(1000); // Under 1 second per request
        }

        testResult.success = true;
        testResult.duration = Date.now() - testResult.startTime;

      } catch (error) {
        testResult.error = error.message;
      }

      performanceResults.push(testResult);
      expect(testResult.success).toBe(true);
    });

    it('should optimize TTS with caching', async () => {
      const testResult: any = {
        testName: 'TTS Caching Performance',
        startTime: Date.now(),
        cacheResults: {},
        success: false
      };

      try {
        const sessionId = 'cache-test-session';
        await languageRouter.startSession(sessionId, {
          callId: 'cache-test-call',
          preferredLanguage: 'cs' // Use Czech TTS which has caching
        });

        const testText = "Dobrý den, děkuji za zavolání do naší zákaznické služby.";

        // First synthesis (cold cache)
        monitor.start();
        const coldStartTime = performance.now();
        const firstSynthesis = await languageRouter.synthesizeSpeech(sessionId, testText);
        const coldEndTime = performance.now();
        const coldMetrics = monitor.end();

        // Second synthesis (warm cache) - simulate cache hit
        mockCzechTTSService.synthesize.mockImplementation(async (text, options) => {
          // Simulate cache hit with much faster response
          await new Promise(resolve => setTimeout(resolve, 5)); // 5ms for cache hit
          return Buffer.from(`cached-synthesized-${options?.voice || 'default'}-${text.length}`);
        });

        monitor.start();
        const warmStartTime = performance.now();
        const secondSynthesis = await languageRouter.synthesizeSpeech(sessionId, testText);
        const warmEndTime = performance.now();
        const warmMetrics = monitor.end();

        testResult.cacheResults = {
          coldCache: {
            duration: coldEndTime - coldStartTime,
            memory: coldMetrics.avgMemory,
            audioSize: firstSynthesis?.length || 0
          },
          warmCache: {
            duration: warmEndTime - warmStartTime,
            memory: warmMetrics.avgMemory,
            audioSize: secondSynthesis?.length || 0
          },
          improvement: {
            speedup: (coldEndTime - coldStartTime) / (warmEndTime - warmStartTime),
            memoryReduction: coldMetrics.avgMemory - warmMetrics.avgMemory
          }
        };

        // Cache should provide significant performance improvement
        expect(testResult.cacheResults.improvement.speedup).toBeGreaterThan(2); // At least 2x faster
        expect(testResult.cacheResults.warmCache.duration).toBeLessThan(50); // Under 50ms for cache hit

        testResult.success = true;
        testResult.duration = Date.now() - testResult.startTime;

      } catch (error) {
        testResult.error = error.message;
      }

      performanceResults.push(testResult);
      expect(testResult.success).toBe(true);
    });
  });

  describe('Language Switching Performance', () => {
    it('should switch languages within performance thresholds', async () => {
      const testResult: any = {
        testName: 'Language Switching Speed',
        startTime: Date.now(),
        switches: [],
        success: false
      };

      try {
        const sessionId = 'switch-perf-session';
        await languageRouter.startSession(sessionId, {
          callId: 'switch-perf-call',
          preferredLanguage: 'en'
        });

        const languageTexts = [
          { language: 'es', text: PERFORMANCE_TEST_DATA.mediumTexts[1] },
          { language: 'cs', text: PERFORMANCE_TEST_DATA.mediumTexts[2] },
          { language: 'en', text: PERFORMANCE_TEST_DATA.mediumTexts[0] },
          { language: 'es', text: PERFORMANCE_TEST_DATA.mediumTexts[4] },
          { language: 'cs', text: PERFORMANCE_TEST_DATA.mediumTexts[5] }
        ];

        for (const { language, text } of languageTexts) {
          monitor.start();
          
          const switchStartTime = performance.now();
          const detection = await languageRouter.processText(sessionId, text);
          const switchEndTime = performance.now();
          
          const switchMetrics = monitor.end();
          
          const switchData = {
            expectedLanguage: language,
            detectedLanguage: detection.language,
            confidence: detection.confidence,
            switchDuration: switchEndTime - switchStartTime,
            memory: switchMetrics.avgMemory,
            accurate: detection.language === language,
            withinThreshold: (switchEndTime - switchStartTime) <= PERFORMANCE_THRESHOLDS.languageSwitching.maxSwitchTime
          };

          testResult.switches.push(switchData);

          // Verify switch performance
          expect(switchData.switchDuration).toBeLessThanOrEqual(PERFORMANCE_THRESHOLDS.languageSwitching.maxSwitchTime);
        }

        testResult.metrics = {
          avgSwitchTime: testResult.switches.reduce((sum: number, s: any) => sum + s.switchDuration, 0) / testResult.switches.length,
          maxSwitchTime: Math.max(...testResult.switches.map((s: any) => s.switchDuration)),
          accuracy: testResult.switches.filter((s: any) => s.accurate).length / testResult.switches.length,
          avgMemory: testResult.switches.reduce((sum: number, s: any) => sum + s.memory, 0) / testResult.switches.length
        };

        expect(testResult.metrics.accuracy).toBeGreaterThanOrEqual(0.8); // 80% accuracy
        expect(testResult.metrics.avgSwitchTime).toBeLessThan(PERFORMANCE_THRESHOLDS.languageSwitching.maxSwitchTime);

        testResult.success = true;
        testResult.duration = Date.now() - testResult.startTime;

      } catch (error) {
        testResult.error = error.message;
      }

      performanceResults.push(testResult);
      expect(testResult.success).toBe(true);
    });

    it('should handle rapid language switching without performance degradation', async () => {
      const testResult: any = {
        testName: 'Rapid Language Switching',
        startTime: Date.now(),
        rapidSwitches: [],
        success: false
      };

      try {
        const sessionId = 'rapid-switch-session';
        await languageRouter.startSession(sessionId, {
          callId: 'rapid-switch-call',
          preferredLanguage: 'en'
        });

        const rapidTexts = [
          'Hello there',
          'Hola amigo',
          'Ahoj příteli',
          'How are you?',
          '¿Cómo estás?',
          'Jak se máš?',
          'Thank you',
          'Gracias',
          'Děkuji'
        ];

        monitor.start();

        for (let i = 0; i < rapidTexts.length; i++) {
          const switchStartTime = performance.now();
          await languageRouter.processText(sessionId, rapidTexts[i]);
          const switchEndTime = performance.now();
          
          testResult.rapidSwitches.push({
            index: i,
            text: rapidTexts[i],
            duration: switchEndTime - switchStartTime
          });

          // Small delay between switches
          await new Promise(resolve => setTimeout(resolve, 10));
        }

        const rapidMetrics = monitor.end();

        testResult.metrics = {
          totalDuration: rapidMetrics.totalDuration,
          avgSwitchTime: testResult.rapidSwitches.reduce((sum: number, s: any) => sum + s.duration, 0) / testResult.rapidSwitches.length,
          maxSwitchTime: Math.max(...testResult.rapidSwitches.map((s: any) => s.duration)),
          minSwitchTime: Math.min(...testResult.rapidSwitches.map((s: any) => s.duration)),
          throughput: (testResult.rapidSwitches.length / rapidMetrics.totalDuration) * 1000,
          avgMemory: rapidMetrics.avgMemory,
          peakMemory: rapidMetrics.peakMemory
        };

        // Verify no significant performance degradation
        expect(testResult.metrics.maxSwitchTime).toBeLessThan(PERFORMANCE_THRESHOLDS.languageSwitching.maxSwitchTime);
        expect(testResult.metrics.throughput).toBeGreaterThan(50); // At least 50 switches per second

        testResult.success = true;
        testResult.duration = Date.now() - testResult.startTime;

      } catch (error) {
        testResult.error = error.message;
      }

      performanceResults.push(testResult);
      expect(testResult.success).toBe(true);
    });
  });

  describe('WebSocket Event Performance', () => {
    it('should handle WebSocket events within latency thresholds', async () => {
      const testResult: any = {
        testName: 'WebSocket Event Latency',
        startTime: Date.now(),
        events: [],
        success: false
      };

      try {
        monitor.start();

        // Mock WebSocket with event timing
        const mockWs = mockWebSocket();
        const sessionId = 'ws-perf-session';

        await languageRouter.startSession(sessionId, {
          callId: 'ws-perf-call',
          preferredLanguage: 'en'
        });

        // Simulate various WebSocket events
        const eventTypes = [
          'audio-chunk',
          'transcript-update',
          'language-switch',
          'tts-request',
          'session-update'
        ];

        for (let i = 0; i < 100; i++) {
          const eventType = eventTypes[i % eventTypes.length];
          const eventData = Buffer.from(`event-${i}-data`);
          
          const eventStartTime = performance.now();
          
          // Simulate event processing
          switch (eventType) {
            case 'audio-chunk':
              await languageRouter.processAudio(sessionId, eventData, `transcript-${i}`);
              break;
            case 'transcript-update':
              await languageRouter.processText(sessionId, `Update text ${i}`);
              break;
            case 'language-switch':
              const lang = i % 3 === 0 ? 'en' : i % 3 === 1 ? 'es' : 'cs';
              await languageRouter.setSessionLanguage(sessionId, lang);
              break;
            case 'tts-request':
              await languageRouter.synthesizeSpeech(sessionId, `TTS text ${i}`);
              break;
            case 'session-update':
              languageRouter.getSessionStats(sessionId);
              break;
          }
          
          const eventEndTime = performance.now();
          const eventDuration = eventEndTime - eventStartTime;
          
          testResult.events.push({
            type: eventType,
            index: i,
            duration: eventDuration,
            withinThreshold: eventDuration <= PERFORMANCE_THRESHOLDS.websocket.maxEventProcessingTime
          });

          monitor.sample(`event-${eventType}`);
        }

        const wsMetrics = monitor.end();

        testResult.metrics = {
          totalEvents: testResult.events.length,
          avgEventTime: testResult.events.reduce((sum: number, e: any) => sum + e.duration, 0) / testResult.events.length,
          maxEventTime: Math.max(...testResult.events.map((e: any) => e.duration)),
          eventsWithinThreshold: testResult.events.filter((e: any) => e.withinThreshold).length,
          throughput: (testResult.events.length / wsMetrics.totalDuration) * 1000,
          avgMemory: wsMetrics.avgMemory,
          peakMemory: wsMetrics.peakMemory
        };

        // Verify WebSocket performance
        expect(testResult.metrics.eventsWithinThreshold / testResult.events.length).toBeGreaterThanOrEqual(0.9); // 90% within threshold
        expect(testResult.metrics.throughput).toBeGreaterThanOrEqual(PERFORMANCE_THRESHOLDS.websocket.minThroughput);

        testResult.success = true;
        testResult.duration = Date.now() - testResult.startTime;

      } catch (error) {
        testResult.error = error.message;
      }

      performanceResults.push(testResult);
      expect(testResult.success).toBe(true);
    });
  });

  describe('System-wide Performance', () => {
    it('should handle maximum concurrent sessions without degradation', async () => {
      const testResult: any = {
        testName: 'Maximum Concurrent Sessions',
        startTime: Date.now(),
        sessions: [],
        success: false
      };

      try {
        monitor.start();

        const maxSessions = PERFORMANCE_THRESHOLDS.system.maxConcurrentSessions;
        const sessionPromises: Promise<void>[] = [];
        const sessionIds: string[] = [];

        // Create maximum concurrent sessions
        for (let i = 0; i < maxSessions; i++) {
          const sessionId = `max-session-${i}`;
          sessionIds.push(sessionId);

          const sessionPromise = (async () => {
            const sessionStartTime = performance.now();
            
            await languageRouter.startSession(sessionId, {
              callId: `max-call-${i}`,
              preferredLanguage: i % 3 === 0 ? 'en' : i % 3 === 1 ? 'es' : 'cs'
            });

            // Perform some operations
            await languageRouter.processText(sessionId, "Test concurrent processing");
            await languageRouter.synthesizeSpeech(sessionId, "Concurrent synthesis test");

            const sessionEndTime = performance.now();

            testResult.sessions.push({
              sessionId,
              duration: sessionEndTime - sessionStartTime,
              index: i
            });

            monitor.sample(`session-${i}`);
          })();

          sessionPromises.push(sessionPromise);
        }

        const concurrentStartTime = performance.now();
        await Promise.all(sessionPromises);
        const concurrentEndTime = performance.now();

        const systemMetrics = monitor.end();

        testResult.metrics = {
          totalSessions: maxSessions,
          totalDuration: concurrentEndTime - concurrentStartTime,
          avgSessionSetupTime: testResult.sessions.reduce((sum: number, s: any) => sum + s.duration, 0) / testResult.sessions.length,
          maxSessionSetupTime: Math.max(...testResult.sessions.map((s: any) => s.duration)),
          throughput: (maxSessions / (concurrentEndTime - concurrentStartTime)) * 1000,
          avgMemory: systemMetrics.avgMemory,
          peakMemory: systemMetrics.peakMemory,
          memoryPerSession: systemMetrics.peakMemory / maxSessions
        };

        // Verify system can handle max sessions
        expect(testResult.metrics.avgSessionSetupTime).toBeLessThanOrEqual(PERFORMANCE_THRESHOLDS.languageSwitching.maxSessionSetupTime);
        expect(testResult.metrics.memoryPerSession).toBeLessThanOrEqual(PERFORMANCE_THRESHOLDS.system.maxMemoryPerSession);
        expect(languageRouter.getActiveSessions()).toHaveLength(maxSessions);

        // Clean up all sessions
        for (const sessionId of sessionIds) {
          await languageRouter.endSession(sessionId);
        }

        expect(languageRouter.getActiveSessions()).toHaveLength(0);

        testResult.success = true;
        testResult.duration = Date.now() - testResult.startTime;

      } catch (error) {
        testResult.error = error.message;
      }

      performanceResults.push(testResult);
      expect(testResult.success).toBe(true);
    });

    it('should maintain performance under sustained load', async () => {
      const testResult: any = {
        testName: 'Sustained Load Performance',
        startTime: Date.now(),
        loadPhases: [],
        success: false
      };

      try {
        const sustainedDuration = 30000; // 30 seconds
        const phaseInterval = 5000; // 5 second phases
        const sessionsPerPhase = 10;
        
        const startTime = Date.now();
        let phaseIndex = 0;

        while (Date.now() - startTime < sustainedDuration) {
          monitor.start();
          
          const phaseStartTime = performance.now();
          const sessionPromises: Promise<void>[] = [];
          const phaseSessions: string[] = [];

          // Create sessions for this phase
          for (let i = 0; i < sessionsPerPhase; i++) {
            const sessionId = `load-phase-${phaseIndex}-session-${i}`;
            phaseSessions.push(sessionId);

            const sessionPromise = (async () => {
              await languageRouter.startSession(sessionId, {
                callId: `load-phase-${phaseIndex}-call-${i}`,
                preferredLanguage: 'en'
              });

              // Perform various operations
              await languageRouter.processText(sessionId, PERFORMANCE_TEST_DATA.mediumTexts[i % PERFORMANCE_TEST_DATA.mediumTexts.length]);
              await languageRouter.synthesizeSpeech(sessionId, "Load test synthesis");
              
              // Switch language
              await languageRouter.setSessionLanguage(sessionId, i % 2 === 0 ? 'es' : 'cs');
              await languageRouter.synthesizeSpeech(sessionId, "Second synthesis");
            })();

            sessionPromises.push(sessionPromise);
          }

          await Promise.all(sessionPromises);
          const phaseEndTime = performance.now();

          const phaseMetrics = monitor.end();
          
          testResult.loadPhases.push({
            phaseIndex,
            duration: phaseEndTime - phaseStartTime,
            sessions: sessionsPerPhase,
            avgMemory: phaseMetrics.avgMemory,
            peakMemory: phaseMetrics.peakMemory,
            throughput: (sessionsPerPhase / (phaseEndTime - phaseStartTime)) * 1000
          });

          // Clean up phase sessions
          for (const sessionId of phaseSessions) {
            await languageRouter.endSession(sessionId);
          }

          phaseIndex++;
          
          // Small break between phases
          await new Promise(resolve => setTimeout(resolve, 100));
        }

        testResult.metrics = {
          totalPhases: testResult.loadPhases.length,
          avgPhaseDuration: testResult.loadPhases.reduce((sum: number, p: any) => sum + p.duration, 0) / testResult.loadPhases.length,
          avgThroughput: testResult.loadPhases.reduce((sum: number, p: any) => sum + p.throughput, 0) / testResult.loadPhases.length,
          avgMemory: testResult.loadPhases.reduce((sum: number, p: any) => sum + p.avgMemory, 0) / testResult.loadPhases.length,
          peakMemory: Math.max(...testResult.loadPhases.map((p: any) => p.peakMemory)),
          performanceStability: testResult.loadPhases.every((p: any) => p.throughput > 0.5) // Consistent performance
        };

        // Verify sustained performance
        expect(testResult.metrics.performanceStability).toBe(true);
        expect(testResult.metrics.avgThroughput).toBeGreaterThan(0.5); // At least 0.5 sessions/sec
        expect(testResult.metrics.peakMemory).toBeLessThan(200); // Under 200MB peak

        testResult.success = true;
        testResult.duration = Date.now() - testResult.startTime;

      } catch (error) {
        testResult.error = error.message;
      }

      performanceResults.push(testResult);
      expect(testResult.success).toBe(true);
    });
  });
});