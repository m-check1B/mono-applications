import { BugReportConfig } from './types';

const DEFAULT_CONFIG: BugReportConfig = {
  enabled: true,
  mandatory: false,
  environments: ['alpha', 'beta'],
  position: 'bottom-right',
  autoSubmit: true,
  captureScreenshot: true,
  captureConsoleErrors: true,
  maxRetries: 3,
  retryDelay: 5000,
  apiEndpoint: '/api/bug-report',
  uploadEndpoint: '/api/upload'
};

export class BugReportConfigManager {
  private static instance: BugReportConfigManager;
  private config: BugReportConfig;

  private constructor() {
    this.config = { ...DEFAULT_CONFIG };
  }

  static getInstance(): BugReportConfigManager {
    if (!BugReportConfigManager.instance) {
      BugReportConfigManager.instance = new BugReportConfigManager();
    }
    return BugReportConfigManager.instance;
  }

  updateConfig(newConfig: Partial<BugReportConfig>): void {
    this.config = { ...this.config, ...newConfig };
  }

  getConfig(): BugReportConfig {
    return { ...this.config };
  }

  isEnabled(): boolean {
    const currentEnv = this.detectEnvironment();
    return this.config.enabled && this.config.environments.includes(currentEnv);
  }

  isMandatory(): boolean {
    const currentEnv = this.detectEnvironment();
    const isTargetEnv = this.config.environments.includes(currentEnv);
    return this.config.mandatory && isTargetEnv && (currentEnv === 'alpha' || currentEnv === 'beta');
  }

  private detectEnvironment(): 'development' | 'staging' | 'production' | 'alpha' | 'beta' {
    // Check various environment indicators
    if (typeof window !== 'undefined') {
      const hostname = window.location.hostname;
      
      // Check for alpha/beta in URL or version
      if (hostname.includes('alpha') || window.location.pathname.includes('alpha')) {
        return 'alpha';
      }
      if (hostname.includes('beta') || window.location.pathname.includes('beta')) {
        return 'beta';
      }
      if (hostname.includes('staging')) {
        return 'staging';
      }
      if (hostname === 'localhost' || hostname.includes('127.0.0.1')) {
        return 'development';
      }
    }

    // Check environment variables (for SSR)
    if (typeof process !== 'undefined' && process.env) {
      const nodeEnv = process.env.NODE_ENV;
      const appEnv = process.env.APP_ENV || process.env.REACT_APP_ENV;
      
      if (appEnv === 'alpha') return 'alpha';
      if (appEnv === 'beta') return 'beta';
      if (nodeEnv === 'development') return 'development';
      if (nodeEnv === 'staging' || appEnv === 'staging') return 'staging';
    }

    return 'production';
  }

  getLinearConfig(): { apiKey?: string; teamId?: string } {
    return {
      apiKey: this.config.linearApiKey || process.env.LINEAR_API_KEY || process.env.REACT_APP_LINEAR_API_KEY,
      teamId: this.config.linearTeamId || process.env.LINEAR_TEAM_ID || process.env.REACT_APP_LINEAR_TEAM_ID
    };
  }
}