export interface BugReport {
  message: string;
  name: string;
  url: string;
  userAgent: string;
  timestamp: string;
  imageFile?: File | null;
  appVersion?: string;
  environment?: 'development' | 'staging' | 'production' | 'alpha' | 'beta';
  metadata?: Record<string, any>;
}

export interface PendingBugReport extends BugReport {
  id: string;
  status: 'pending' | 'sent' | 'failed';
  imageDataUrl?: string | null;
  retryCount?: number;
  lastAttempt?: string;
}

export interface BugReportResult {
  success: boolean;
  error?: string;
  issueUrl?: string;
  issueId?: string;
  linearIssueId?: string;
}

export interface BugReportConfig {
  enabled: boolean;
  mandatory: boolean;
  linearApiKey?: string;
  linearTeamId?: string;
  apiEndpoint?: string;
  uploadEndpoint?: string;
  maxRetries?: number;
  retryDelay?: number;
  environments: ('development' | 'staging' | 'production' | 'alpha' | 'beta')[];
  position?: 'bottom-right' | 'bottom-left' | 'top-right' | 'top-left';
  autoSubmit?: boolean;
  captureScreenshot?: boolean;
  captureConsoleErrors?: boolean;
  customFields?: Record<string, any>;
}

export interface LinearIssue {
  id: string;
  identifier: string;
  title: string;
  description?: string;
  state: string;
  priority: number;
  url: string;
  createdAt: string;
  updatedAt: string;
}

export interface AppVersionInfo {
  version: string;
  buildNumber?: string;
  environment: 'development' | 'staging' | 'production' | 'alpha' | 'beta';
  releaseDate?: string;
  gitCommit?: string;
}