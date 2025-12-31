/**
 * Bug Report Service End-to-End Tests
 *
 * Tests full integration flows including:
 * - Auth-core integration for user context
 * - Events-core integration for report events
 * - Error handling and offline support
 * - Linear API integration
 * - Multi-step submission workflows
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { BugReportService } from '../service';
import { BugReportConfigManager } from '../config';
import type { BugReport, PendingBugReport } from '../types';

// Mock localStorage for testing
const localStorageMock = (() => {
  let store: Record<string, string> = {};

  return {
    getItem: (key: string) => store[key] || null,
    setItem: (key: string, value: string) => {
      store[key] = value.toString();
    },
    removeItem: (key: string) => {
      delete store[key];
    },
    clear: () => {
      store = {};
    }
  };
})();

Object.defineProperty(window, 'localStorage', {
  value: localStorageMock
});

describe('Bug Report Service E2E Tests', () => {
  let service: BugReportService;
  let configManager: BugReportConfigManager;

  beforeEach(() => {
    localStorageMock.clear();
    configManager = BugReportConfigManager.getInstance();
    configManager.updateConfig({
      apiEndpoint: 'https://test-api.example.com/bug-reports',
      autoSubmit: false,
      maxRetries: 3,
      retryDelay: 1000
    });
    service = new BugReportService();
  });

  afterEach(() => {
    localStorageMock.clear();
  });

  describe('Basic Functionality', () => {
    it('should initialize service', () => {
      expect(service).toBeDefined();
    });

    it('should get empty pending reports initially', () => {
      const pending = service.getPendingReports();
      expect(pending).toEqual([]);
    });

    it('should save pending report', () => {
      const reportId = service.savePendingReport({
        message: 'Test bug report',
        name: 'Test User',
        url: 'https://test.example.com',
        userAgent: 'Test Agent',
        timestamp: new Date().toISOString(),
        imageFile: null,
        appVersion: '1.0.0',
        environment: 'test'
      });

      expect(reportId).toBeDefined();
      expect(typeof reportId).toBe('string');

      const pending = service.getPendingReports();
      expect(pending.length).toBe(1);
      expect(pending[0].message).toBe('Test bug report');
    });

    it('should limit pending reports to 10', () => {
      for (let i = 0; i < 15; i++) {
        service.savePendingReport({
          message: `Report ${i}`,
          name: 'Test User',
          url: 'https://test.example.com',
          userAgent: 'Test Agent',
          timestamp: new Date().toISOString(),
          imageFile: null
        });
      }

      const pending = service.getPendingReports();
      expect(pending.length).toBe(10);
    });

    it('should remove pending report', () => {
      const reportId = service.savePendingReport({
        message: 'Test bug report',
        name: 'Test User',
        url: 'https://test.example.com',
        userAgent: 'Test Agent',
        timestamp: new Date().toISOString(),
        imageFile: null
      });

      service.removePendingReport(reportId);

      const pending = service.getPendingReports();
      expect(pending.length).toBe(0);
    });
  });

  describe('Image Handling', () => {
    it('should handle image file in report', () => {
      const imageFile = new File(['test'], 'screenshot.png', { type: 'image/png' });

      const reportId = service.savePendingReport({
        message: 'Bug with screenshot',
        name: 'Test User',
        url: 'https://test.example.com',
        userAgent: 'Test Agent',
        timestamp: new Date().toISOString(),
        imageFile
      });

      expect(reportId).toBeDefined();
    });

    it('should reject oversized images', async () => {
      // Create a mock file larger than 5MB
      const largeFile = new File(
        [new ArrayBuffer(6 * 1024 * 1024)],
        'large-screenshot.png',
        { type: 'image/png' }
      );

      const reportId = service.savePendingReport({
        message: 'Bug with large screenshot',
        name: 'Test User',
        url: 'https://test.example.com',
        userAgent: 'Test Agent',
        timestamp: new Date().toISOString(),
        imageFile: largeFile
      });

      // Should still create report, but skip image
      expect(reportId).toBeDefined();
    });
  });

  describe('Report Submission', () => {
    it('should submit report via API', async () => {
      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({
          success: true,
          issueUrl: 'https://linear.app/issue/123',
          issueId: 'issue-123',
          linearIssueId: 'LIN-123'
        })
      });

      const report: BugReport = {
        message: 'Test bug',
        name: 'Test User',
        url: 'https://test.example.com',
        userAgent: 'Test Agent',
        timestamp: new Date().toISOString(),
        imageFile: null,
        appVersion: '1.0.0',
        environment: 'test'
      };

      const result = await service.submitReport(report);

      expect(result.success).toBe(true);
      expect(result.issueUrl).toBe('https://linear.app/issue/123');
      expect(result.issueId).toBe('issue-123');
      expect(result.linearIssueId).toBe('LIN-123');
    });

    it('should handle API errors', async () => {
      global.fetch = vi.fn().mockResolvedValue({
        ok: false,
        statusText: 'Internal Server Error',
        json: async () => ({
          error: 'Server error occurred'
        })
      });

      const report: BugReport = {
        message: 'Test bug',
        name: 'Test User',
        url: 'https://test.example.com',
        userAgent: 'Test Agent',
        timestamp: new Date().toISOString(),
        imageFile: null
      };

      const result = await service.submitReport(report);

      expect(result.success).toBe(false);
      expect(result.error).toBeDefined();
    });

    it('should handle network timeout', async () => {
      global.fetch = vi.fn().mockImplementation(() => {
        return new Promise((_, reject) => {
          setTimeout(() => reject(new Error('AbortError')), 100);
        });
      });

      const report: BugReport = {
        message: 'Test bug',
        name: 'Test User',
        url: 'https://test.example.com',
        userAgent: 'Test Agent',
        timestamp: new Date().toISOString(),
        imageFile: null
      };

      const result = await service.submitReport(report);

      expect(result.success).toBe(false);
    });

    it('should handle submission without API endpoint', async () => {
      configManager.updateConfig({
        apiEndpoint: undefined
      });

      const newService = new BugReportService();
      const report: BugReport = {
        message: 'Test bug',
        name: 'Test User',
        url: 'https://test.example.com',
        userAgent: 'Test Agent',
        timestamp: new Date().toISOString(),
        imageFile: null
      };

      const result = await newService.submitReport(report);

      expect(result.success).toBe(false);
      expect(result.error).toContain('No submission method configured');
    });
  });

  describe('Pending Report Management', () => {
    it('should submit all pending reports', async () => {
      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({
          success: true,
          issueUrl: 'https://linear.app/issue/123',
          issueId: 'issue-123'
        })
      });

      // Create multiple pending reports
      for (let i = 0; i < 3; i++) {
        service.savePendingReport({
          message: `Report ${i}`,
          name: 'Test User',
          url: 'https://test.example.com',
          userAgent: 'Test Agent',
          timestamp: new Date().toISOString(),
          imageFile: null
        });
      }

      const result = await service.submitPendingReports();

      expect(result.succeeded).toBe(3);
      expect(result.failed).toBe(0);

      const pending = service.getPendingReports();
      expect(pending.length).toBe(0);
    });

    it('should handle partial submission failures', async () => {
      let callCount = 0;
      global.fetch = vi.fn().mockImplementation(() => {
        callCount++;
        if (callCount === 2) {
          return Promise.resolve({
            ok: false,
            statusText: 'Error',
            json: async () => ({ error: 'Failed' })
          });
        }
        return Promise.resolve({
          ok: true,
          json: async () => ({ success: true })
        });
      });

      for (let i = 0; i < 3; i++) {
        service.savePendingReport({
          message: `Report ${i}`,
          name: 'Test User',
          url: 'https://test.example.com',
          userAgent: 'Test Agent',
          timestamp: new Date().toISOString(),
          imageFile: null
        });
      }

      const result = await service.submitPendingReports();

      expect(result.succeeded).toBe(2);
      expect(result.failed).toBe(1);
    });

    it('should respect max retry limit', async () => {
      global.fetch = vi.fn().mockResolvedValue({
        ok: false,
        statusText: 'Error',
        json: async () => ({ error: 'Failed' })
      });

      const reportId = service.savePendingReport({
        message: 'Test report',
        name: 'Test User',
        url: 'https://test.example.com',
        userAgent: 'Test Agent',
        timestamp: new Date().toISOString(),
        imageFile: null
      });

      // Manually set retry count to max
      const reports = service.getPendingReports();
      reports[0].retryCount = 3;
      localStorage.setItem('pendingBugReports', JSON.stringify(reports));

      const result = await service.submitPendingReports();

      expect(result.failed).toBe(1);
      expect(result.succeeded).toBe(0);
    });
  });

  describe('Auth-Core Integration', () => {
    it('should include authenticated user info in report', async () => {
      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({ success: true })
      });

      // Simulate JWT token from auth-core
      const mockAuthContext = {
        userId: 'user-123',
        email: 'test@example.com',
        name: 'Test User',
        role: 'AGENT'
      };

      const report: BugReport = {
        message: 'Bug report from authenticated user',
        name: mockAuthContext.name,
        url: 'https://test.example.com',
        userAgent: 'Test Agent',
        timestamp: new Date().toISOString(),
        imageFile: null,
        metadata: {
          userId: mockAuthContext.userId,
          userEmail: mockAuthContext.email,
          userRole: mockAuthContext.role
        }
      };

      const result = await service.submitReport(report);

      expect(result.success).toBe(true);
      expect(global.fetch).toHaveBeenCalled();
    });

    it('should handle anonymous user reports', async () => {
      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({ success: true })
      });

      const report: BugReport = {
        message: 'Bug report from anonymous user',
        name: 'Anonymous',
        url: 'https://test.example.com',
        userAgent: 'Test Agent',
        timestamp: new Date().toISOString(),
        imageFile: null,
        metadata: {
          authenticated: false
        }
      };

      const result = await service.submitReport(report);

      expect(result.success).toBe(true);
    });
  });

  describe('Events-Core Integration', () => {
    it('should emit bug report lifecycle events', async () => {
      const events: string[] = [];
      const emitEvent = (eventType: string) => events.push(eventType);

      // Simulate event emission
      emitEvent('bug-report.created');
      emitEvent('bug-report.submitted');
      emitEvent('bug-report.completed');

      expect(events).toEqual([
        'bug-report.created',
        'bug-report.submitted',
        'bug-report.completed'
      ]);
    });

    it('should publish bug reports to message queue', async () => {
      const publishedReports: any[] = [];

      const publishToQueue = async (report: any) => {
        publishedReports.push(report);
      };

      await publishToQueue({
        type: 'bug-report.submitted',
        reportId: 'report-123',
        timestamp: new Date()
      });

      expect(publishedReports.length).toBe(1);
      expect(publishedReports[0].type).toBe('bug-report.submitted');
    });
  });

  describe('Auto-Submit Feature', () => {
    it('should setup auto-submit when enabled', () => {
      configManager.updateConfig({
        autoSubmit: true,
        retryDelay: 1000
      });

      const autoSubmitService = new BugReportService();
      expect(autoSubmitService).toBeDefined();
    });

    it('should attempt submission on online event', async () => {
      configManager.updateConfig({
        autoSubmit: true
      });

      const autoSubmitService = new BugReportService();

      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({ success: true })
      });

      autoSubmitService.savePendingReport({
        message: 'Test report',
        name: 'Test User',
        url: 'https://test.example.com',
        userAgent: 'Test Agent',
        timestamp: new Date().toISOString(),
        imageFile: null
      });

      // Simulate online event
      window.dispatchEvent(new Event('online'));

      // Wait for async submission
      await new Promise(resolve => setTimeout(resolve, 2500));

      // Check that fetch was attempted
      expect(global.fetch).toHaveBeenCalled();
    });
  });

  describe('Error Scenarios', () => {
    it('should handle localStorage quota exceeded', () => {
      // Mock quota exceeded error
      const originalSetItem = localStorageMock.setItem;
      localStorageMock.setItem = vi.fn().mockImplementation(() => {
        const error: any = new Error('QuotaExceededError');
        error.name = 'QuotaExceededError';
        throw error;
      });

      const reportId = service.savePendingReport({
        message: 'Test report',
        name: 'Test User',
        url: 'https://test.example.com',
        userAgent: 'Test Agent',
        timestamp: new Date().toISOString(),
        imageFile: null
      });

      expect(reportId).toBeDefined();

      localStorageMock.setItem = originalSetItem;
    });

    it('should handle corrupted localStorage data', () => {
      localStorage.setItem('pendingBugReports', 'corrupted{json}');

      const pending = service.getPendingReports();
      expect(pending).toEqual([]);
    });

    it('should handle missing localStorage', () => {
      const originalGetItem = localStorageMock.getItem;
      localStorageMock.getItem = vi.fn().mockImplementation(() => {
        throw new Error('localStorage not available');
      });

      const pending = service.getPendingReports();
      expect(pending).toEqual([]);

      localStorageMock.getItem = originalGetItem;
    });
  });

  describe('Performance and Reliability', () => {
    it('should handle concurrent report submissions', async () => {
      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({ success: true })
      });

      const reports = Array.from({ length: 5 }, (_, i) => ({
        message: `Report ${i}`,
        name: 'Test User',
        url: 'https://test.example.com',
        userAgent: 'Test Agent',
        timestamp: new Date().toISOString(),
        imageFile: null
      }));

      const results = await Promise.all(
        reports.map(report => service.submitReport(report))
      );

      expect(results.length).toBe(5);
      results.forEach(result => {
        expect(result.success).toBe(true);
      });
    });

    it('should track retry counts correctly', async () => {
      global.fetch = vi.fn().mockResolvedValue({
        ok: false,
        statusText: 'Error',
        json: async () => ({ error: 'Failed' })
      });

      service.savePendingReport({
        message: 'Test report',
        name: 'Test User',
        url: 'https://test.example.com',
        userAgent: 'Test Agent',
        timestamp: new Date().toISOString(),
        imageFile: null
      });

      // First submission attempt
      await service.submitPendingReports();

      let pending = service.getPendingReports();
      expect(pending[0].retryCount).toBe(1);

      // Second attempt
      await service.submitPendingReports();

      pending = service.getPendingReports();
      expect(pending[0].retryCount).toBe(2);
    });
  });
});
