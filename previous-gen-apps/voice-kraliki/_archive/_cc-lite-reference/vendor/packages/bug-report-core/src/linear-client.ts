import { LinearClient } from '@linear/sdk';
import { BugReport, LinearIssue, BugReportResult } from './types';
import { BugReportConfigManager } from './config';

export class LinearBugReportClient {
  private client: LinearClient | null = null;
  private teamId: string | null = null;
  private configManager: BugReportConfigManager;

  constructor() {
    this.configManager = BugReportConfigManager.getInstance();
    this.initialize();
  }

  private initialize(): void {
    const { apiKey, teamId } = this.configManager.getLinearConfig();
    
    if (apiKey) {
      this.client = new LinearClient({ apiKey });
      this.teamId = teamId || null;
    }
  }

  async createIssue(report: BugReport): Promise<BugReportResult> {
    if (!this.client) {
      return {
        success: false,
        error: 'Linear client not initialized. Missing API key.'
      };
    }

    try {
      const title = `Bug Report: ${report.message.substring(0, 100)}`;
      const description = this.formatDescription(report);

      const issuePayload: any = {
        title,
        description,
        priority: this.getPriorityFromReport(report)
      };

      // Add team if configured
      if (this.teamId) {
        issuePayload.teamId = this.teamId;
      }

      // Add labels for bug reports
      const labels = await this.getOrCreateLabels(['bug', 'user-reported']);
      if (labels.length > 0) {
        issuePayload.labelIds = labels.map(l => l.id);
      }

      // Create the issue
      const issue = await this.client.createIssue(issuePayload);

      // Handle screenshot attachment if present
      if (report.imageFile && (issue as any).id) {
        await this.attachScreenshot((issue as any).id, report.imageFile);
      }

      return {
        success: true,
        issueId: (issue as any).identifier || 'unknown',
        linearIssueId: (issue as any).id || 'unknown',
        issueUrl: (issue as any).url || '#'
      };
    } catch (error) {
      console.error('Error creating Linear issue:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to create Linear issue'
      };
    }
  }

  private formatDescription(report: BugReport): string {
    const sections = [
      `**Description:**`,
      report.message,
      '',
      `**Reporter:** ${report.name || 'Anonymous'}`,
      `**URL:** ${report.url}`,
      `**Timestamp:** ${new Date(report.timestamp).toLocaleString()}`,
      `**User Agent:** ${report.userAgent}`,
    ];

    if (report.appVersion) {
      sections.push(`**App Version:** ${report.appVersion}`);
    }

    if (report.environment) {
      sections.push(`**Environment:** ${report.environment}`);
    }

    if (report.metadata) {
      sections.push('', '**Additional Metadata:**');
      Object.entries(report.metadata).forEach(([key, value]) => {
        sections.push(`- ${key}: ${JSON.stringify(value)}`);
      });
    }

    return sections.join('\n');
  }

  private getPriorityFromReport(report: BugReport): number {
    // Priority levels in Linear: 0 (No priority), 1 (Urgent), 2 (High), 3 (Normal), 4 (Low)
    
    // Check for keywords indicating severity
    const message = report.message.toLowerCase();
    
    if (message.includes('crash') || message.includes('critical') || message.includes('broken')) {
      return 1; // Urgent
    }
    
    if (message.includes('error') || message.includes('fail') || message.includes('bug')) {
      return 2; // High
    }
    
    if (report.environment === 'production') {
      return 2; // High for production issues
    }
    
    if (report.environment === 'alpha' || report.environment === 'beta') {
      return 3; // Normal for alpha/beta
    }
    
    return 3; // Default to Normal
  }

  private async getOrCreateLabels(labelNames: string[]): Promise<any[]> {
    if (!this.client) return [];
    
    try {
      const labels = [];
      
      for (const name of labelNames) {
        // Try to find existing label
        const existingLabels = await this.client.issueLabels({
          filter: { name: { eq: name } }
        });
        
        const nodes = await existingLabels.nodes;
        
        if (nodes.length > 0) {
          labels.push(nodes[0]);
        } else {
          // Create new label if it doesn't exist
          try {
            const newLabel = await this.client.createIssueLabel({
              name,
              color: this.getLabelColor(name)
            });
            labels.push(newLabel);
          } catch (err) {
            console.warn(`Could not create label ${name}:`, err);
          }
        }
      }
      
      return labels;
    } catch (error) {
      console.error('Error managing labels:', error);
      return [];
    }
  }

  private getLabelColor(labelName: string): string {
    const colors: Record<string, string> = {
      'bug': '#d73a4a',
      'user-reported': '#0075ca',
      'alpha': '#fbca04',
      'beta': '#e4e669',
      'production': '#b60205',
      'crash': '#b60205',
      'ui': '#7057ff'
    };
    
    return colors[labelName.toLowerCase()] || '#008672';
  }

  private async attachScreenshot(issueId: string, imageFile: File): Promise<void> {
    if (!this.client) return;
    
    try {
      // Convert File to base64 for attachment
      const base64 = await this.fileToBase64(imageFile);
      
      // Create attachment
      await this.client.createAttachment({
        issueId,
        title: imageFile.name || 'screenshot.png',
        subtitle: `Screenshot uploaded at ${new Date().toISOString()}`,
        url: base64, // In production, this should be a proper URL after uploading to storage
      });
    } catch (error) {
      console.error('Error attaching screenshot:', error);
    }
  }

  private fileToBase64(file: File): Promise<string> {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.readAsDataURL(file);
      reader.onload = () => resolve(reader.result as string);
      reader.onerror = error => reject(error);
    });
  }

  async getIssue(issueId: string): Promise<LinearIssue | null> {
    if (!this.client) return null;
    
    try {
      const issue = await this.client.issue(issueId);
      
      return {
        id: issue.id,
        identifier: issue.identifier,
        title: issue.title,
        description: issue.description,
        state: (await issue.state)?.name || 'Unknown',
        priority: issue.priority,
        url: issue.url,
        createdAt: issue.createdAt.toISOString(),
        updatedAt: issue.updatedAt.toISOString()
      };
    } catch (error) {
      console.error('Error fetching issue:', error);
      return null;
    }
  }
}