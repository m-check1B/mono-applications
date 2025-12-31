/**
 * @stack-2025/byok-core - Environment Migration Scripts
 * Migration tools for moving from environment variables to BYOK system
 */

import { BYOKManager } from '../manager.js';
import { 
  ProviderType, 
  Environment, 
  MigrationPlan,
  BYOKError,
  PROVIDER_SCHEMAS
} from '../types.js';

/**
 * Environment variable patterns for different providers
 */
const ENVIRONMENT_PATTERNS: Record<ProviderType, {
  required: string[];
  optional: string[];
  validator?: (env: Record<string, string>) => boolean;
}> = {
  [ProviderType.OPENAI]: {
    required: ['OPENAI_API_KEY'],
    optional: ['OPENAI_ORGANIZATION', 'OPENAI_PROJECT', 'OPENAI_BASE_URL']
  },
  [ProviderType.ANTHROPIC]: {
    required: ['ANTHROPIC_API_KEY'],
    optional: ['ANTHROPIC_BASE_URL']
  },
  [ProviderType.GOOGLE_VERTEX]: {
    required: ['GOOGLE_VERTEX_API_KEY'],
    optional: ['GOOGLE_PROJECT_ID', 'GOOGLE_VERTEX_BASE_URL', 'GOOGLE_APPLICATION_CREDENTIALS']
  },
  [ProviderType.GOOGLE_GEMINI]: {
    required: ['GOOGLE_GEMINI_API_KEY'],
    optional: ['GOOGLE_PROJECT_ID']
  },
  [ProviderType.DEEPGRAM]: {
    required: ['DEEPGRAM_API_KEY'],
    optional: ['DEEPGRAM_PROJECT_ID']
  },
  [ProviderType.TWILIO]: {
    required: ['TWILIO_ACCOUNT_SID', 'TWILIO_AUTH_TOKEN'],
    optional: ['TWILIO_API_KEY_SID', 'TWILIO_API_KEY_SECRET']
  },
  [ProviderType.TELNYX]: {
    required: ['TELNYX_API_KEY'],
    optional: ['TELNYX_PUBLIC_KEY', 'TELNYX_APPLICATION_ID']
  },
  [ProviderType.OPENROUTER]: {
    required: ['OPENROUTER_API_KEY'],
    optional: ['OPENROUTER_BASE_URL']
  },
  [ProviderType.HUGGINGFACE]: {
    required: ['HUGGINGFACE_API_KEY'],
    optional: ['HUGGINGFACE_BASE_URL']
  },
  [ProviderType.ELEVENLABS]: {
    required: ['ELEVENLABS_API_KEY'],
    optional: []
  }
};

/**
 * Migration analyzer for environment variables
 */
export class EnvironmentMigrationAnalyzer {
  private byokManager: BYOKManager;
  private environment: Record<string, string>;

  constructor(byokManager: BYOKManager, environment?: Record<string, string>) {
    this.byokManager = byokManager;
    this.environment = environment || process.env;
  }

  /**
   * Analyze current environment for migration opportunities
   */
  async analyzeMigrationOpportunities(
    userId: string,
    options: {
      providers?: ProviderType[];
      environment?: Environment;
      preserveExisting?: boolean;
    } = {}
  ): Promise<MigrationPlan> {
    const {
      providers = Object.values(ProviderType),
      environment = Environment.PRODUCTION,
      preserveExisting = true
    } = options;

    const plan: MigrationPlan = {
      from: 'environment',
      providers,
      preserveExisting,
      dryRun: true,
      steps: [],
      estimatedDuration: 0,
      warnings: [],
      errors: []
    };

    // Check existing BYOK keys
    const existingKeys = await this.byokManager.listKeys(userId, { environment });
    const existingProviders = new Set(existingKeys.map(k => k.provider));

    // Analyze each provider
    for (const provider of providers) {
      const step = await this.analyzeProvider(provider, userId, existingProviders.has(provider));
      plan.steps.push(step);

      if (step.action === 'migrate') {
        plan.estimatedDuration += 30; // 30 seconds per migration
      }
    }

    // Add overall warnings
    if (plan.steps.filter(s => s.action === 'migrate').length === 0) {
      plan.warnings.push('No environment variables found for migration');
    }

    if (existingKeys.length > 0 && !preserveExisting) {
      plan.warnings.push(`${existingKeys.length} existing BYOK keys will be replaced`);
    }

    return plan;
  }

  /**
   * Execute migration plan
   */
  async executeMigration(
    userId: string,
    plan: MigrationPlan
  ): Promise<{
    successful: Array<{
      provider: ProviderType;
      keyId: string;
      migrated: boolean;
    }>;
    failed: Array<{
      provider: ProviderType;
      error: string;
      reason: string;
    }>;
    skipped: Array<{
      provider: ProviderType;
      reason: string;
    }>;
  }> {
    if (plan.dryRun) {
      throw new BYOKError('Cannot execute dry run plan. Set dryRun to false.', 'DRY_RUN_EXECUTION');
    }

    const results = {
      successful: [] as Array<{ provider: ProviderType; keyId: string; migrated: boolean }>,
      failed: [] as Array<{ provider: ProviderType; error: string; reason: string }>,
      skipped: [] as Array<{ provider: ProviderType; reason: string }>
    };

    for (const step of plan.steps) {
      try {
        if (step.action === 'migrate' && step.existingConfig) {
          // Migrate this provider
          const keyId = await this.byokManager.addKey({
            userId,
            provider: step.provider,
            keyData: step.existingConfig,
            alias: `Migrated from environment`,
            description: `Automatically migrated from environment variables on ${new Date().toISOString()}`,
            environment: Environment.PRODUCTION
          });

          results.successful.push({
            provider: step.provider,
            keyId,
            migrated: true
          });

        } else if (step.action === 'skip') {
          results.skipped.push({
            provider: step.provider,
            reason: step.reason || 'No migration needed'
          });
        }
      } catch (error) {
        results.failed.push({
          provider: step.provider,
          error: error instanceof Error ? error.message : 'Unknown error',
          reason: `Migration failed for ${step.provider}`
        });
      }
    }

    return results;
  }

  /**
   * Create backup of environment variables
   */
  createEnvironmentBackup(providers: ProviderType[]): {
    backup: Record<string, string>;
    timestamp: Date;
    providers: ProviderType[];
  } {
    const backup: Record<string, string> = {};

    for (const provider of providers) {
      const pattern = ENVIRONMENT_PATTERNS[provider];
      if (!pattern) continue;

      // Backup required and optional variables
      const allVars = [...pattern.required, ...pattern.optional];
      for (const varName of allVars) {
        if (this.environment[varName]) {
          backup[varName] = this.environment[varName];
        }
      }
    }

    return {
      backup,
      timestamp: new Date(),
      providers
    };
  }

  /**
   * Generate migration report
   */
  async generateMigrationReport(
    userId: string,
    plan: MigrationPlan,
    executionResults?: any
  ): Promise<{
    summary: {
      totalProviders: number;
      providersToMigrate: number;
      existingKeys: number;
      estimatedTime: number;
    };
    providerDetails: Array<{
      provider: ProviderType;
      status: 'migrate' | 'skip' | 'manual';
      reason: string;
      hasEnvironmentVars: boolean;
      hasExistingKey: boolean;
      variables: string[];
    }>;
    recommendations: string[];
    warnings: string[];
    backup?: Record<string, string>;
  }> {
    const existingKeys = await this.byokManager.listKeys(userId);
    const existingProviders = new Set(existingKeys.map(k => k.provider));

    const providerDetails = plan.steps.map(step => ({
      provider: step.provider,
      status: step.action,
      reason: step.reason || '',
      hasEnvironmentVars: !!step.existingConfig,
      hasExistingKey: existingProviders.has(step.provider),
      variables: this.getProviderVariables(step.provider)
    }));

    const recommendations: string[] = [];
    
    // Add recommendations based on analysis
    const migrateCount = plan.steps.filter(s => s.action === 'migrate').length;
    if (migrateCount > 0) {
      recommendations.push(`Consider migrating ${migrateCount} providers to BYOK for better security and management`);
    }

    const skipCount = plan.steps.filter(s => s.action === 'skip').length;
    if (skipCount > 0) {
      recommendations.push(`${skipCount} providers already configured or don't need migration`);
    }

    // Security recommendations
    if (migrateCount > 0) {
      recommendations.push('After migration, consider removing environment variables from production');
      recommendations.push('Test all integrations after migration to ensure functionality');
      recommendations.push('Set up key validation monitoring for migrated keys');
    }

    return {
      summary: {
        totalProviders: plan.steps.length,
        providersToMigrate: migrateCount,
        existingKeys: existingKeys.length,
        estimatedTime: plan.estimatedDuration
      },
      providerDetails,
      recommendations,
      warnings: plan.warnings,
      backup: this.createEnvironmentBackup(plan.providers).backup
    };
  }

  // Private helper methods

  private async analyzeProvider(
    provider: ProviderType,
    userId: string,
    hasExistingKey: boolean
  ) {
    const pattern = ENVIRONMENT_PATTERNS[provider];
    if (!pattern) {
      return {
        provider,
        action: 'skip' as const,
        reason: `No migration pattern defined for ${provider}`
      };
    }

    // Check if required environment variables exist
    const hasRequiredVars = pattern.required.every(varName => 
      this.environment[varName] && this.environment[varName].trim() !== ''
    );

    if (!hasRequiredVars) {
      return {
        provider,
        action: 'skip' as const,
        reason: `Missing required environment variables: ${pattern.required.join(', ')}`
      };
    }

    // If user already has a key and we're preserving existing keys
    if (hasExistingKey) {
      return {
        provider,
        action: 'skip' as const,
        reason: 'User already has a BYOK key for this provider'
      };
    }

    // Extract configuration from environment
    const existingConfig = this.extractProviderConfig(provider, pattern);
    
    // Validate the configuration
    try {
      const schema = PROVIDER_SCHEMAS[provider];
      if (schema) {
        schema.parse(existingConfig);
      }
    } catch (error) {
      return {
        provider,
        action: 'manual' as const,
        reason: `Configuration validation failed: ${error}`
      };
    }

    return {
      provider,
      action: 'migrate' as const,
      existingConfig
    };
  }

  private extractProviderConfig(provider: ProviderType, pattern: typeof ENVIRONMENT_PATTERNS[ProviderType]) {
    const config: Record<string, any> = {};

    // Extract configuration based on provider type
    switch (provider) {
      case ProviderType.OPENAI:
        config.apiKey = this.environment.OPENAI_API_KEY;
        if (this.environment.OPENAI_ORGANIZATION) {
          config.organization = this.environment.OPENAI_ORGANIZATION;
        }
        if (this.environment.OPENAI_PROJECT) {
          config.project = this.environment.OPENAI_PROJECT;
        }
        break;

      case ProviderType.ANTHROPIC:
        config.apiKey = this.environment.ANTHROPIC_API_KEY;
        break;

      case ProviderType.GOOGLE_VERTEX:
      case ProviderType.GOOGLE_GEMINI:
        config.apiKey = this.environment[`${provider.toUpperCase()}_API_KEY`];
        if (this.environment.GOOGLE_PROJECT_ID) {
          config.projectId = this.environment.GOOGLE_PROJECT_ID;
        }
        break;

      case ProviderType.DEEPGRAM:
        config.apiKey = this.environment.DEEPGRAM_API_KEY;
        if (this.environment.DEEPGRAM_PROJECT_ID) {
          config.projectId = this.environment.DEEPGRAM_PROJECT_ID;
        }
        break;

      case ProviderType.TWILIO:
        config.accountSid = this.environment.TWILIO_ACCOUNT_SID;
        config.authToken = this.environment.TWILIO_AUTH_TOKEN;
        if (this.environment.TWILIO_API_KEY_SID) {
          config.apiKeySid = this.environment.TWILIO_API_KEY_SID;
        }
        if (this.environment.TWILIO_API_KEY_SECRET) {
          config.apiKeySecret = this.environment.TWILIO_API_KEY_SECRET;
        }
        break;

      case ProviderType.TELNYX:
        config.apiKey = this.environment.TELNYX_API_KEY;
        if (this.environment.TELNYX_PUBLIC_KEY) {
          config.publicKey = this.environment.TELNYX_PUBLIC_KEY;
        }
        if (this.environment.TELNYX_APPLICATION_ID) {
          config.applicationId = this.environment.TELNYX_APPLICATION_ID;
        }
        break;

      default:
        // Generic handling for other providers
        const apiKeyVar = `${provider.toUpperCase().replace('-', '_')}_API_KEY`;
        config.apiKey = this.environment[apiKeyVar];
        break;
    }

    return config;
  }

  private getProviderVariables(provider: ProviderType): string[] {
    const pattern = ENVIRONMENT_PATTERNS[provider];
    if (!pattern) return [];
    
    return [...pattern.required, ...pattern.optional].filter(varName => 
      this.environment[varName]
    );
  }
}

/**
 * Interactive migration wizard
 */
export class MigrationWizard {
  private analyzer: EnvironmentMigrationAnalyzer;

  constructor(byokManager: BYOKManager, environment?: Record<string, string>) {
    this.analyzer = new EnvironmentMigrationAnalyzer(byokManager, environment);
  }

  /**
   * Start interactive migration process
   */
  async startMigration(userId: string, options: {
    providers?: ProviderType[];
    autoConfirm?: boolean;
    createBackup?: boolean;
  } = {}): Promise<{
    plan: MigrationPlan;
    results?: any;
    backup?: any;
    report: any;
  }> {
    const {
      providers,
      autoConfirm = false,
      createBackup = true
    } = options;

    console.log('🔐 Starting BYOK Migration Wizard...\n');

    // Step 1: Analyze migration opportunities
    console.log('📊 Analyzing environment variables...');
    const plan = await this.analyzer.analyzeMigrationOpportunities(userId, {
      providers,
      preserveExisting: true
    });

    // Step 2: Generate and display report
    const report = await this.analyzer.generateMigrationReport(userId, plan);
    this.displayMigrationReport(report);

    // Step 3: Create backup if requested
    let backup;
    if (createBackup && plan.steps.some(s => s.action === 'migrate')) {
      console.log('\n💾 Creating environment backup...');
      backup = this.analyzer.createEnvironmentBackup(plan.providers);
      console.log(`Backup created with ${Object.keys(backup.backup).length} variables`);
    }

    // Step 4: Confirm migration
    let shouldProceed = autoConfirm;
    if (!autoConfirm && plan.steps.some(s => s.action === 'migrate')) {
      // In a real implementation, this would prompt the user
      console.log('\n❓ Would you like to proceed with the migration? (This is a simulation - proceeding automatically)');
      shouldProceed = true;
    }

    let results;
    if (shouldProceed && plan.steps.some(s => s.action === 'migrate')) {
      console.log('\n🚀 Executing migration...');
      
      // Execute the migration
      plan.dryRun = false;
      results = await this.analyzer.executeMigration(userId, plan);
      
      this.displayMigrationResults(results);
    } else {
      console.log('\n⏭️  Migration cancelled or no changes needed');
    }

    return {
      plan,
      results,
      backup,
      report
    };
  }

  private displayMigrationReport(report: any) {
    console.log('\n📋 Migration Analysis Report');
    console.log('================================');
    console.log(`Total Providers: ${report.summary.totalProviders}`);
    console.log(`Providers to Migrate: ${report.summary.providersToMigrate}`);
    console.log(`Existing BYOK Keys: ${report.summary.existingKeys}`);
    console.log(`Estimated Time: ${report.summary.estimatedTime} seconds\n`);

    console.log('Provider Details:');
    for (const detail of report.providerDetails) {
      const status = detail.status === 'migrate' ? '✅' : 
                     detail.status === 'skip' ? '⏭️' : '⚠️';
      console.log(`${status} ${detail.provider}: ${detail.reason}`);
      if (detail.variables.length > 0) {
        console.log(`   Variables: ${detail.variables.join(', ')}`);
      }
    }

    if (report.warnings.length > 0) {
      console.log('\n⚠️  Warnings:');
      report.warnings.forEach((warning: string) => console.log(`   - ${warning}`));
    }

    if (report.recommendations.length > 0) {
      console.log('\n💡 Recommendations:');
      report.recommendations.forEach((rec: string) => console.log(`   - ${rec}`));
    }
  }

  private displayMigrationResults(results: any) {
    console.log('\n✅ Migration Results');
    console.log('====================');
    
    if (results.successful.length > 0) {
      console.log(`✅ Successfully migrated ${results.successful.length} providers:`);
      results.successful.forEach((result: any) => {
        console.log(`   - ${result.provider}: ${result.keyId}`);
      });
    }

    if (results.failed.length > 0) {
      console.log(`\n❌ Failed to migrate ${results.failed.length} providers:`);
      results.failed.forEach((result: any) => {
        console.log(`   - ${result.provider}: ${result.error}`);
      });
    }

    if (results.skipped.length > 0) {
      console.log(`\n⏭️  Skipped ${results.skipped.length} providers:`);
      results.skipped.forEach((result: any) => {
        console.log(`   - ${result.provider}: ${result.reason}`);
      });
    }
  }
}

/**
 * Factory function to create migration tools
 */
export function createMigrationTools(byokManager: BYOKManager) {
  return {
    analyzer: new EnvironmentMigrationAnalyzer(byokManager),
    wizard: new MigrationWizard(byokManager)
  };
}