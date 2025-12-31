import { BugReport, PendingBugReport, BugReportResult } from './types';
import { BugReportConfigManager } from './config';
import { dataURLtoBlob } from './utils';

export class BugReportService {
  private static storageKey = 'pendingBugReports';
  private configManager: BugReportConfigManager;

  constructor() {
    this.configManager = BugReportConfigManager.getInstance();
    
    // Setup auto-submit if enabled
    if (this.configManager.getConfig().autoSubmit) {
      this.setupAutoSubmit();
    }
  }

  /**
   * Gets any pending bug reports from localStorage
   */
  getPendingReports(): PendingBugReport[] {
    if (typeof window === 'undefined') {
      return [];
    }

    try {
      const pendingReports = localStorage.getItem(BugReportService.storageKey);
      return pendingReports ? JSON.parse(pendingReports) : [];
    } catch (error) {
      console.error('Error getting pending bug reports', error);
      return [];
    }
  }

  /**
   * Saves a bug report to localStorage for offline support
   */
  savePendingReport(report: Omit<PendingBugReport, 'id' | 'status'>): string {
    const reportId = Date.now().toString();

    try {
      const pendingReports = this.getPendingReports();
      
      const newReport: PendingBugReport = {
        ...report,
        id: reportId,
        status: 'pending',
        imageDataUrl: null,
        retryCount: 0,
        lastAttempt: new Date().toISOString()
      };

      // Handle image file
      if (report.imageFile && typeof window !== 'undefined') {
        this.processImageFile(report.imageFile, reportId);
      }

      // Limit to 10 pending bug reports
      while (pendingReports.length >= 10) {
        pendingReports.shift();
      }

      pendingReports.push(newReport);
      this.saveReportToStorage(pendingReports);

      return reportId;
    } catch (error) {
      console.error('Error saving pending bug report', error);
      return reportId;
    }
  }

  private async processImageFile(file: File, reportId: string): Promise<void> {
    try {
      const maxImageSize = 5 * 1024 * 1024; // 5MB max
      if (file.size > maxImageSize) {
        console.warn('Image file too large for localStorage (max 5MB)');
        return;
      }

      const reader = new FileReader();
      reader.onloadend = () => {
        try {
          const imageDataUrl = reader.result as string;
          const reports = this.getPendingReports();
          const reportIndex = reports.findIndex(r => r.id === reportId);
          
          if (reportIndex !== -1) {
            reports[reportIndex].imageDataUrl = imageDataUrl;
            this.saveReportToStorage(reports);
          }
        } catch (error) {
          console.error('Error updating report with image data', error);
        }
      };
      
      reader.readAsDataURL(file);
    } catch (error) {
      console.error('Error processing image for bug report', error);
    }
  }

  private saveReportToStorage(reports: PendingBugReport[]): boolean {
    try {
      localStorage.setItem(BugReportService.storageKey, JSON.stringify(reports));
      return true;
    } catch (e) {
      if (e && typeof e === 'object' && 'name' in e && e.name === 'QuotaExceededError') {
        console.error('Could not save bug report: localStorage quota exceeded');
      } else {
        console.error('Error saving bug report to localStorage', e);
      }
      return false;
    }
  }

  /**
   * Removes a submitted report from localStorage
   */
  removePendingReport(reportId: string): void {
    try {
      const pendingReports = this.getPendingReports();
      const updatedReports = pendingReports.filter(report => report.id !== reportId);
      localStorage.setItem(BugReportService.storageKey, JSON.stringify(updatedReports));
    } catch (error) {
      console.error('Error removing pending bug report', error);
    }
  }

  /**
   * Submit a single bug report to the API and Linear
   */
  async submitReport(report: BugReport | PendingBugReport): Promise<BugReportResult> {
    try {
      const config = this.configManager.getConfig();
      
      // Always use API endpoint (Linear SDK doesn't work in browser)
      if (config.apiEndpoint) {
        return await this.submitViaAPI(report);
      }

      return {
        success: false,
        error: 'No submission method configured'
      };
    } catch (error) {
      console.error('Error submitting bug report', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error occurred'
      };
    }
  }

  private async submitViaAPI(report: BugReport | PendingBugReport): Promise<BugReportResult> {
    const config = this.configManager.getConfig();
    const formData = new FormData();
    
    formData.append('description', report.message);
    formData.append('name', report.name || '');
    formData.append('url', report.url || window.location.href);
    formData.append('userAgent', report.userAgent);
    formData.append('timestamp', report.timestamp);
    
    if (report.appVersion) {
      formData.append('appVersion', report.appVersion);
    }
    
    if (report.environment) {
      formData.append('environment', report.environment);
    }
    
    if (report.metadata) {
      formData.append('metadata', JSON.stringify(report.metadata));
    }

    // Handle image attachment
    if ('imageFile' in report && report.imageFile instanceof Blob) {
      formData.append('screenshot', report.imageFile, 
        report.imageFile instanceof File ? report.imageFile.name : 'screenshot.png');
    } else if ('imageDataUrl' in report && report.imageDataUrl) {
      try {
        const blob = dataURLtoBlob(report.imageDataUrl);
        if (blob.size > 0) {
          formData.append('screenshot', blob, `screenshot_${Date.now()}.png`);
        }
      } catch (error) {
        console.error('Error converting data URL to blob', error);
      }
    }

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 15000);

    try {
      const response = await fetch(config.apiEndpoint!, {
        method: 'POST',
        body: formData,
        signal: controller.signal
      });

      clearTimeout(timeoutId);

      const responseData = await response.json();

      if (response.ok && responseData.success) {
        // If it's a pending report, remove it
        if ('id' in report) {
          this.removePendingReport(report.id);
        }
        
        return {
          success: true,
          issueUrl: responseData.issueUrl,
          issueId: responseData.issueId,
          linearIssueId: responseData.linearIssueId
        };
      } else {
        return {
          success: false,
          error: responseData.error || responseData.message || response.statusText
        };
      }
    } catch (fetchError: unknown) {
      clearTimeout(timeoutId);
      if (fetchError instanceof Error && fetchError.name === 'AbortError') {
        return {
          success: false,
          error: 'Request timed out. Please try again.'
        };
      }
      throw fetchError;
    }
  }

  /**
   * Attempts to submit pending bug reports
   */
  async submitPendingReports(): Promise<{ succeeded: number; failed: number }> {
    const pendingReports = this.getPendingReports().filter(
      report => report.status === 'pending'
    );

    if (pendingReports.length === 0) {
      return { succeeded: 0, failed: 0 };
    }

    let succeeded = 0;
    let failed = 0;

    for (const report of pendingReports) {
      try {
        const config = this.configManager.getConfig();
        const maxRetries = config.maxRetries || 3;
        
        // Check retry count
        if ((report.retryCount || 0) >= maxRetries) {
          this.updateReportStatus(report.id, 'failed');
          failed++;
          continue;
        }

        const result = await this.submitReport(report);

        if (result.success) {
          this.removePendingReport(report.id);
          succeeded++;
        } else {
          // Update retry count
          this.updateReportRetry(report.id);
          failed++;
        }
      } catch (error) {
        console.error(`Error submitting pending report ${report.id}`, error);
        this.updateReportRetry(report.id);
        failed++;
      }
    }

    return { succeeded, failed };
  }

  private updateReportStatus(reportId: string, status: PendingBugReport['status']): void {
    try {
      const reports = this.getPendingReports();
      const reportIndex = reports.findIndex(r => r.id === reportId);
      
      if (reportIndex !== -1) {
        reports[reportIndex].status = status;
        this.saveReportToStorage(reports);
      }
    } catch (error) {
      console.error('Error updating report status', error);
    }
  }

  private updateReportRetry(reportId: string): void {
    try {
      const reports = this.getPendingReports();
      const reportIndex = reports.findIndex(r => r.id === reportId);
      
      if (reportIndex !== -1) {
        reports[reportIndex].retryCount = (reports[reportIndex].retryCount || 0) + 1;
        reports[reportIndex].lastAttempt = new Date().toISOString();
        reports[reportIndex].status = 'failed';
        this.saveReportToStorage(reports);
      }
    } catch (error) {
      console.error('Error updating report retry count', error);
    }
  }

  private setupAutoSubmit(): void {
    if (typeof window === 'undefined') return;

    // Try to submit pending reports when coming online
    window.addEventListener('online', () => {
      setTimeout(() => {
        this.submitPendingReports();
      }, 2000);
    });

    // Try to submit pending reports periodically
    setInterval(() => {
      if (navigator.onLine) {
        this.submitPendingReports();
      }
    }, this.configManager.getConfig().retryDelay || 30000);

    // Try to submit on page load
    if (document.readyState === 'complete') {
      this.submitPendingReports();
    } else {
      window.addEventListener('load', () => {
        setTimeout(() => {
          this.submitPendingReports();
        }, 5000);
      });
    }
  }
}