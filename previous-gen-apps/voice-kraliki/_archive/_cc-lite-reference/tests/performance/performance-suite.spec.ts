import { test, expect } from '@playwright/test';

test.describe('Performance Suite', () => {
  test.beforeEach(async ({ page }) => {
    await page.context().clearCookies();
    await page.evaluate(() => localStorage.clear());

    // Enable performance metrics
    await page.goto('http://localhost:5174', {
      waitUntil: 'networkidle'
    });
  });

  test.describe('Page Load Performance', () => {
    test('should load login page within performance thresholds', async ({ page }) => {
      const metrics = await page.goto('http://localhost:5174/login', {
        waitUntil: 'networkidle'
      });

      expect(metrics?.ok()).toBe(true);

      // Check load time
      const timing = await page.evaluate(() => {
        const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
        return {
          domContentLoaded: navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart,
          loadComplete: navigation.loadEventEnd - navigation.loadEventStart,
          firstPaint: performance.getEntriesByType('paint')
            .find(entry => entry.name === 'first-paint')?.startTime || 0,
          firstContentfulPaint: performance.getEntriesByType('paint')
            .find(entry => entry.name === 'first-contentful-paint')?.startTime || 0
        };
      });

      console.log('Performance metrics:', timing);

      // Performance thresholds (adjust based on your requirements)
      expect(timing.domContentLoaded).toBeLessThan(3000); // 3 seconds
      expect(timing.loadComplete).toBeLessThan(5000); // 5 seconds
      expect(timing.firstContentfulPaint).toBeLessThan(2000); // 2 seconds
    });

    test('should have minimal bundle size', async ({ page }) => {
      const resources = await page.evaluate(() => {
        return performance.getEntriesByType('resource').map(resource => ({
          name: resource.name,
          size: (resource as any).transferSize || 0,
          type: resource.initiatorType
        }));
      });

      const jsResources = resources.filter(r => r.type === 'script' && r.name.includes('.js'));
      const cssResources = resources.filter(r => r.type === 'link' && r.name.includes('.css'));

      const totalJsSize = jsResources.reduce((sum, r) => sum + r.size, 0);
      const totalCssSize = cssResources.reduce((sum, r) => sum + r.size, 0);

      console.log('JS bundle sizes:', jsResources.map(r => ({ name: r.name, size: r.size })));
      console.log('CSS bundle sizes:', cssResources.map(r => ({ name: r.name, size: r.size })));

      // Bundle size thresholds (adjust based on your requirements)
      expect(totalJsSize).toBeLessThan(2000000); // 2MB
      expect(totalCssSize).toBeLessThan(500000); // 500KB
    });

    test('should implement proper caching headers', async ({ page }) => {
      const response = await page.goto('http://localhost:5174/login');
      const headers = response?.headers() || {};

      expect(headers['cache-control']).toBeTruthy();
      expect(headers['etag']).toBeTruthy();
    });
  });

  test.describe('Runtime Performance', () => {
    test('should maintain smooth frame rate during interactions', async ({ page }) => {
      await page.goto('http://localhost:5174/login');

      // Measure frame rate during form interaction
      const frameRates = await page.evaluate(async () => {
        const frames: number[] = [];
        let lastTime = performance.now();

        return new Promise((resolve) => {
          const measureFrame = (timestamp: number) => {
            const deltaTime = timestamp - lastTime;
            const fps = 1000 / deltaTime;
            frames.push(fps);
            lastTime = timestamp;

            if (frames.length < 60) { // Measure for 60 frames
              requestAnimationFrame(measureFrame);
            } else {
              resolve(frames);
            }
          };

          requestAnimationFrame(measureFrame);
        });
      });

      const avgFps = frameRates.reduce((sum, fps) => sum + fps, 0) / frameRates.length;
      const minFps = Math.min(...frameRates);

      console.log('Average FPS:', avgFps);
      console.log('Minimum FPS:', minFps);

      expect(avgFps).toBeGreaterThan(30); // Should maintain 30+ FPS
      expect(minFps).toBeGreaterThan(15); // No severe frame drops
    });

    test('should have minimal main thread blocking', async ({ page }) => {
      await page.goto('http://localhost:5174/login');

      const longTasks = await page.evaluate(() => {
        return new Promise((resolve) => {
          const observer = new PerformanceObserver((list) => {
            const entries = list.getEntries();
            resolve(entries.map(entry => ({
              duration: entry.duration,
              name: entry.name,
              startTime: entry.startTime
            })));
          });

          observer.observe({ entryTypes: ['longtask'] });

          // Wait a bit to collect tasks
          setTimeout(() => {
            observer.disconnect();
            resolve([]);
          }, 3000);
        });
      });

      console.log('Long tasks:', longTasks);

      // Should have minimal long tasks (>50ms)
      const significantLongTasks = longTasks.filter(task => task.duration > 100);
      expect(significantLongTasks.length).toBeLessThan(3);
    });

    test('should handle memory efficiently', async ({ page }) => {
      await page.goto('http://localhost:5174/login');

      const memoryMetrics = await page.evaluate(async () => {
        const samples: any[] = [];

        for (let i = 0; i < 10; i++) {
          if ((performance as any).memory) {
            samples.push({
              usedJSHeapSize: (performance as any).memory.usedJSHeapSize,
              totalJSHeapSize: (performance as any).memory.totalJSHeapSize,
              jsHeapSizeLimit: (performance as any).memory.jsHeapSizeLimit
            });
          }
          await new Promise(resolve => setTimeout(resolve, 500));
        }

        return samples;
      });

      if (memoryMetrics.length > 0) {
        const initialMemory = memoryMetrics[0].usedJSHeapSize;
        const finalMemory = memoryMetrics[memoryMetrics.length - 1].usedJSHeapSize;
        const memoryGrowth = finalMemory - initialMemory;

        console.log('Memory metrics:', memoryMetrics);
        console.log('Memory growth:', memoryGrowth);

        // Memory should not grow significantly during normal operation
        expect(memoryGrowth).toBeLessThan(5000000); // 5MB growth threshold
      }
    });
  });

  test.describe('Network Performance', () => {
    test('should minimize API calls', async ({ page }) => {
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

      // Wait for page to stabilize
      await page.waitForLoadState('networkidle');

      // Monitor network requests
      const requests: string[] = [];
      page.on('request', request => {
        if (request.url().includes('/api/') || request.url().includes('/trpc/')) {
          requests.push(request.url());
        }
      });

      // Wait and observe network activity
      await page.waitForTimeout(5000);

      console.log('API requests:', requests);

      // Should not make excessive API calls
      expect(requests.length).toBeLessThan(10);
    });

    test('should implement proper request throttling', async ({ page }) => {
      // This test verifies that rapid user interactions don't cause excessive API calls

      await page.goto('http://localhost:5174/login');

      const apiCalls: string[] = [];
      page.on('request', request => {
        if (request.url().includes('/api/')) {
          apiCalls.push(request.url());
        }
      });

      // Simulate rapid form interactions
      const emailInput = page.locator('input[type="email"]');
      await emailInput.fill('t');
      await emailInput.fill('te');
      await emailInput.fill('tes');
      await emailInput.fill('test');
      await emailInput.fill('test@');
      await emailInput.fill('test@e');
      await emailInput.fill('test@ex');
      await emailInput.fill('test@exa');
      await emailInput.fill('test@exam');
      await emailInput.fill('test@examp');
      await emailInput.fill('test@exampl');
      await emailInput.fill('test@example.com');

      await page.waitForTimeout(1000);

      console.log('API calls during rapid typing:', apiCalls);

      // Should have minimal API calls during rapid typing (debounced/throttled)
      expect(apiCalls.length).toBeLessThan(3);
    });

    test('should handle network failures gracefully', async ({ page }) => {
      // Mock network failure
      await page.route('**/dashboard', async (route) => {
        await route.abort('failed');
      });

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

      const startTime = Date.now();
      await page.goto('http://localhost:5174/dashboard');
      const endTime = Date.now();

      const loadTime = endTime - startTime;
      console.log('Load time with network failure:', loadTime);

      // Should handle network failure within reasonable time
      expect(loadTime).toBeLessThan(10000); // 10 seconds

      // Should show error state
      await expect(page.locator('text=Connection Error')).toBeVisible({ timeout: 5000 });
    });
  });

  test.describe('WebSocket Performance', () => {
    test('should handle high-frequency WebSocket messages efficiently', async ({ page }) => {
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

      await page.goto('http://localhost:5174/dashboard');

      // Mock WebSocket with high-frequency messages
      await page.addInitScript(() => {
        window.WebSocket = class MockWebSocket {
          constructor(url: string) {
            setTimeout(() => {
              if (this.onopen) {
                this.onopen(new Event('open'));
              }

              // Send high-frequency messages
              let messageCount = 0;
              const interval = setInterval(() => {
                if (this.onmessage && messageCount < 100) {
                  this.onmessage(new MessageEvent('message', {
                    data: JSON.stringify({
                      event: 'call.updated',
                      data: { id: `call-${messageCount}`, status: 'ACTIVE' },
                      timestamp: new Date().toISOString()
                    })
                  }));
                  messageCount++;
                } else {
                  clearInterval(interval);
                }
              }, 50); // 20 messages per second
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

      await page.reload();

      // Monitor performance during high-frequency updates
      const frameRates = await page.evaluate(async () => {
        const frames: number[] = [];
        let lastTime = performance.now();

        return new Promise((resolve) => {
          const measureFrame = (timestamp: number) => {
            const deltaTime = timestamp - lastTime;
            const fps = 1000 / deltaTime;
            frames.push(fps);
            lastTime = timestamp;

            if (frames.length < 120) { // Measure for 2 seconds at 60fps
              requestAnimationFrame(measureFrame);
            } else {
              resolve(frames);
            }
          };

          requestAnimationFrame(measureFrame);
        });
      });

      const avgFps = frameRates.reduce((sum, fps) => sum + fps, 0) / frameRates.length;
      const minFps = Math.min(...frameRates);

      console.log('Average FPS during WebSocket updates:', avgFps);
      console.log('Minimum FPS during WebSocket updates:', minFps);

      // Should maintain decent frame rate even with high-frequency updates
      expect(avgFps).toBeGreaterThan(20);
      expect(minFps).toBeGreaterThan(10);
    });
  });

  test.describe('Mobile Performance', () => {
    test.beforeEach(async ({ page }) => {
      await page.setViewportSize({ width: 375, height: 667 });
    });

    test('should perform well on mobile devices', async ({ page }) => {
      await page.goto('http://localhost:5174/login');

      const metrics = await page.evaluate(() => {
        const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
        return {
          domContentLoaded: navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart,
          loadComplete: navigation.loadEventEnd - navigation.loadEventStart,
          firstContentfulPaint: performance.getEntriesByType('paint')
            .find(entry => entry.name === 'first-contentful-paint')?.startTime || 0
        };
      });

      console.log('Mobile performance metrics:', metrics);

      // Mobile performance thresholds (slightly more lenient)
      expect(metrics.domContentLoaded).toBeLessThan(4000); // 4 seconds
      expect(metrics.loadComplete).toBeLessThan(6000); // 6 seconds
      expect(metrics.firstContentfulPaint).toBeLessThan(3000); // 3 seconds
    });

    test('should handle touch interactions smoothly', async ({ page }) => {
      await page.goto('http://localhost:5174/login');

      // Measure response time for touch interactions
      const touchResponseTimes = await page.evaluate(async () => {
        const times: number[] = [];
        const button = document.querySelector('button[type="submit"]');

        if (button) {
          for (let i = 0; i < 5; i++) {
            const startTime = performance.now();

            // Simulate touch event
            const touchEvent = new TouchEvent('touchstart', {
              bubbles: true,
              cancelable: true,
              touches: [new Touch({
                identifier: 1,
                target: button,
                clientX: 100,
                clientY: 100
              })]
            });

            button.dispatchEvent(touchEvent);
            times.push(performance.now() - startTime);

            await new Promise(resolve => setTimeout(resolve, 100));
          }
        }

        return times;
      });

      const avgResponseTime = touchResponseTimes.reduce((sum, time) => sum + time, 0) / touchResponseTimes.length;
      console.log('Average touch response time:', avgResponseTime);

      expect(avgResponseTime).toBeLessThan(100); // Should respond within 100ms
    });
  });
});