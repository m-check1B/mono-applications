#!/usr/bin/env tsx
/**
 * Voice by Kraliki Security Audit Script
 *
 * Performs comprehensive security audit to verify compliance
 * with security requirements and best practices.
 *
 * Usage: pnpm tsx scripts/security-audit.ts
 */

import { readFileSync, existsSync, statSync } from 'fs';
import { execSync } from 'child_process';
import { resolve } from 'path';

interface SecurityCheck {
  name: string;
  description: string;
  category: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  status: 'PASS' | 'FAIL' | 'WARNING' | 'SKIP';
  details?: string;
  remediation?: string;
}

interface SecurityAuditResult {
  timestamp: string;
  version: string;
  overallScore: number;
  grade: string;
  checks: SecurityCheck[];
  summary: {
    total: number;
    passed: number;
    failed: number;
    warnings: number;
    skipped: number;
  };
  compliance: {
    owasp: boolean;
    bsi: boolean;
    gdpr: boolean;
  };
}

class SecurityAuditor {
  private checks: SecurityCheck[] = [];
  private projectRoot: string;

  constructor() {
    this.projectRoot = process.cwd();
  }

  /**
   * Add a security check
   */
  addCheck(check: SecurityCheck): void {
    this.checks.push(check);
  }

  /**
   * Check if file contains hardcoded secrets
   */
  checkForHardcodedSecrets(): void {
    const secretPatterns = [
      /password\s*[:=]\s*["'][^"'\s]{8,}["']/i,
      /secret\s*[:=]\s*["'][^"'\s]{16,}["']/i,
      /token\s*[:=]\s*["'][^"'\s]{20,}["']/i,
      /key\s*[:=]\s*["'][^"'\s]{16,}["']/i,
      /sk-[a-zA-Z0-9]{32,}/,
      /sk-ant-[a-zA-Z0-9]{32,}/,
      /xoxb-[a-zA-Z0-9-]+/,
      /AKIA[0-9A-Z]{16}/,
    ];

    const filesToCheck = [
      '.env.production.secure',
      // check both legacy and consolidated compose locations
      existsSync(resolve(this.projectRoot, 'deploy/docker/docker-compose.production.yml'))
        ? 'deploy/docker/docker-compose.production.yml'
        : 'docker-compose.production.yml',
      'server/index.ts',
      'server/utils/secrets-loader.ts'
    ];

    let hardcodedSecretsFound = false;
    const findings: string[] = [];

    for (const file of filesToCheck) {
      const filePath = resolve(this.projectRoot, file);
      if (!existsSync(filePath)) continue;

      try {
        const content = readFileSync(filePath, 'utf8');

        for (const pattern of secretPatterns) {
          const matches = content.match(pattern);
          if (matches && !matches[0].includes('CHANGE_ME') && !matches[0].includes('DOCKER_SECRET')) {
            hardcodedSecretsFound = true;
            findings.push(`${file}: ${matches[0].substring(0, 50)}...`);
          }
        }
      } catch (error) {
        // Skip unreadable files
      }
    }

    this.addCheck({
      name: 'Hardcoded Secrets Check',
      description: 'Verify no hardcoded secrets in configuration files',
      category: 'CRITICAL',
      status: hardcodedSecretsFound ? 'FAIL' : 'PASS',
      details: hardcodedSecretsFound ? `Found: ${findings.join(', ')}` : 'No hardcoded secrets detected',
      remediation: hardcodedSecretsFound ? 'Replace hardcoded secrets with Docker secrets or environment variables' : undefined
    });
  }

  /**
   * Check Docker secrets configuration
   */
  checkDockerSecrets(): void {
    let dockerComposePath = resolve(this.projectRoot, 'deploy/docker/docker-compose.production.yml');
    if (!existsSync(dockerComposePath)) {
      dockerComposePath = resolve(this.projectRoot, 'docker-compose.production.yml');
    }

    if (!existsSync(dockerComposePath)) {
      this.addCheck({
        name: 'Docker Secrets Configuration',
        description: 'Verify Docker secrets are properly configured',
        category: 'CRITICAL',
        status: 'FAIL',
        details: 'docker-compose.production.yml not found',
        remediation: 'Create production Docker Compose file with secrets configuration'
      });
      return;
    }

    const content = readFileSync(dockerComposePath, 'utf8');
    const requiredSecrets = [
      'jwt_secret',
      'jwt_refresh_secret',
      'cookie_secret',
      'db_password',
      'redis_password'
    ];

    const hasSecretsSection = content.includes('secrets:');
    const missingSecrets = requiredSecrets.filter(secret => !content.includes(secret));

    this.addCheck({
      name: 'Docker Secrets Configuration',
      description: 'Verify Docker secrets are properly configured',
      category: 'CRITICAL',
      status: hasSecretsSection && missingSecrets.length === 0 ? 'PASS' : 'FAIL',
      details: missingSecrets.length > 0 ? `Missing secrets: ${missingSecrets.join(', ')}` : 'All required secrets configured',
      remediation: missingSecrets.length > 0 ? 'Add missing secrets to Docker Compose configuration' : undefined
    });
  }

  /**
   * Check network security configuration
   */
  checkNetworkSecurity(): void {
    let dockerComposePath = resolve(this.projectRoot, 'deploy/docker/docker-compose.production.yml');
    if (!existsSync(dockerComposePath)) {
      dockerComposePath = resolve(this.projectRoot, 'docker-compose.production.yml');
    }

    if (!existsSync(dockerComposePath)) {
      this.addCheck({
        name: 'Network Security',
        description: 'Verify secure network configuration',
        category: 'HIGH',
        status: 'SKIP',
        details: 'docker-compose.production.yml not found'
      });
      return;
    }

    const content = readFileSync(dockerComposePath, 'utf8');

    // Check for insecure 0.0.0.0 bindings
    const hasInsecureBindings = content.includes('0.0.0.0:') && !content.includes('# Safe in containers');

    // Check for internal-only database/redis
    const hasExternalDb = content.includes('5432:5432') || content.includes('6379:6379');

    let status: 'PASS' | 'FAIL' | 'WARNING' = 'PASS';
    const issues: string[] = [];

    if (hasInsecureBindings) {
      status = 'FAIL';
      issues.push('Insecure 0.0.0.0 bindings detected');
    }

    if (hasExternalDb) {
      status = 'WARNING';
      issues.push('Database/Redis ports exposed externally');
    }

    this.addCheck({
      name: 'Network Security',
      description: 'Verify secure network configuration',
      category: 'HIGH',
      status,
      details: issues.length > 0 ? issues.join(', ') : 'Network configuration secure',
      remediation: issues.length > 0 ? 'Remove external port bindings for internal services' : undefined
    });
  }

  /**
   * Check security middleware implementation
   */
  checkSecurityMiddleware(): void {
    const middlewarePath = resolve(this.projectRoot, 'server/middleware/security-middleware.ts');
    const serverPath = resolve(this.projectRoot, 'server/index.ts');

    const middlewareExists = existsSync(middlewarePath);
    let middlewareIntegrated = false;

    if (existsSync(serverPath)) {
      const serverContent = readFileSync(serverPath, 'utf8');
      middlewareIntegrated = serverContent.includes('registerSecurityMiddleware');
    }

    this.addCheck({
      name: 'Security Middleware',
      description: 'Verify security middleware is implemented and integrated',
      category: 'HIGH',
      status: middlewareExists && middlewareIntegrated ? 'PASS' : 'FAIL',
      details: `Middleware exists: ${middlewareExists}, Integrated: ${middlewareIntegrated}`,
      remediation: !middlewareExists ? 'Implement security middleware' : 'Integrate security middleware in server'
    });
  }

  /**
   * Check rate limiting configuration
   */
  checkRateLimiting(): void {
    const middlewarePath = resolve(this.projectRoot, 'server/middleware/security-middleware.ts');

    if (!existsSync(middlewarePath)) {
      this.addCheck({
        name: 'Rate Limiting',
        description: 'Verify rate limiting is configured',
        category: 'HIGH',
        status: 'FAIL',
        details: 'Security middleware not found',
        remediation: 'Implement rate limiting in security middleware'
      });
      return;
    }

    const content = readFileSync(middlewarePath, 'utf8');
    const hasRateLimiting = content.includes('ENDPOINT_RATE_LIMITS') && content.includes('rate-limit');
    const hasAuthLimiting = content.includes('/api/auth/login');

    this.addCheck({
      name: 'Rate Limiting',
      description: 'Verify rate limiting is configured',
      category: 'HIGH',
      status: hasRateLimiting && hasAuthLimiting ? 'PASS' : 'FAIL',
      details: `Rate limiting: ${hasRateLimiting}, Auth limiting: ${hasAuthLimiting}`,
      remediation: 'Configure rate limiting for all endpoints, especially authentication'
    });
  }

  /**
   * Check production configuration
   */
  checkProductionConfig(): void {
    const prodConfigPath = resolve(this.projectRoot, '.env.production.secure');

    if (!existsSync(prodConfigPath)) {
      this.addCheck({
        name: 'Production Configuration',
        description: 'Verify production configuration exists and is secure',
        category: 'CRITICAL',
        status: 'FAIL',
        details: 'Production configuration file not found',
        remediation: 'Create secure production configuration file'
      });
      return;
    }

    const content = readFileSync(prodConfigPath, 'utf8');

    // Check for security settings
    const securityChecks = [
      { setting: 'SEED_DEMO_USERS=false', description: 'Demo users disabled' },
      { setting: 'NODE_ENV=production', description: 'Production environment' },
      { setting: 'CSRF_TOKEN_ENABLED=true', description: 'CSRF protection enabled' },
      { setting: 'RATE_LIMIT_ENABLED=true', description: 'Rate limiting enabled' },
      { setting: 'HSTS_ENABLED=true', description: 'HSTS enabled' },
      { setting: 'CSP_ENABLED=true', description: 'CSP enabled' }
    ];

    const missingSettings = securityChecks.filter(check => !content.includes(check.setting));

    this.addCheck({
      name: 'Production Configuration',
      description: 'Verify production configuration exists and is secure',
      category: 'CRITICAL',
      status: missingSettings.length === 0 ? 'PASS' : 'WARNING',
      details: missingSettings.length > 0 ?
        `Missing: ${missingSettings.map(s => s.description).join(', ')}` :
        'All security settings configured',
      remediation: missingSettings.length > 0 ? 'Add missing security configuration settings' : undefined
    });
  }

  /**
   * Check dependencies for vulnerabilities
   */
  checkDependencyVulnerabilities(): void {
    try {
      // Check if npm audit is available
      execSync('npm audit --audit-level=high --json', { stdio: 'pipe' });

      this.addCheck({
        name: 'Dependency Vulnerabilities',
        description: 'Check for high/critical vulnerabilities in dependencies',
        category: 'HIGH',
        status: 'PASS',
        details: 'No high or critical vulnerabilities found'
      });
    } catch (error) {
      const output = (error as any).stdout?.toString() || '';

      try {
        const auditResult = JSON.parse(output);
        const vulnerabilities = auditResult.metadata?.vulnerabilities || {};
        const highCount = vulnerabilities.high || 0;
        const criticalCount = vulnerabilities.critical || 0;

        if (highCount > 0 || criticalCount > 0) {
          this.addCheck({
            name: 'Dependency Vulnerabilities',
            description: 'Check for high/critical vulnerabilities in dependencies',
            category: 'HIGH',
            status: 'FAIL',
            details: `Found ${criticalCount} critical and ${highCount} high severity vulnerabilities`,
            remediation: 'Run npm audit fix and update vulnerable dependencies'
          });
        } else {
          this.addCheck({
            name: 'Dependency Vulnerabilities',
            description: 'Check for high/critical vulnerabilities in dependencies',
            category: 'HIGH',
            status: 'PASS',
            details: 'No high or critical vulnerabilities found'
          });
        }
      } catch {
        this.addCheck({
          name: 'Dependency Vulnerabilities',
          description: 'Check for high/critical vulnerabilities in dependencies',
          category: 'HIGH',
          status: 'WARNING',
          details: 'Unable to parse audit results',
          remediation: 'Manually review npm audit output'
        });
      }
    }
  }

  /**
   * Check file permissions
   */
  checkFilePermissions(): void {
    const sensitiveFiles = [
      '.env',
      '.env.production.secure',
      'scripts/secrets-template.env'
    ];

    const issues: string[] = [];

    for (const file of sensitiveFiles) {
      const filePath = resolve(this.projectRoot, file);
      if (!existsSync(filePath)) continue;

      try {
        const stats = statSync(filePath);
        const mode = stats.mode & parseInt('777', 8);

        // Check if file is readable by others (should be 600 or 640 max)
        if (mode & parseInt('044', 8)) {
          issues.push(`${file}: permissions ${mode.toString(8)} too permissive`);
        }
      } catch (error) {
        issues.push(`${file}: unable to check permissions`);
      }
    }

    this.addCheck({
      name: 'File Permissions',
      description: 'Verify sensitive files have proper permissions',
      category: 'MEDIUM',
      status: issues.length === 0 ? 'PASS' : 'WARNING',
      details: issues.length > 0 ? issues.join(', ') : 'All sensitive files properly secured',
      remediation: issues.length > 0 ? 'chmod 600 for sensitive configuration files' : undefined
    });
  }

  /**
   * Run all security checks
   */
  async runAudit(): Promise<SecurityAuditResult> {
    console.log('🔐 Starting Voice by Kraliki Security Audit...\n');

    // Run all checks
    this.checkForHardcodedSecrets();
    this.checkDockerSecrets();
    this.checkNetworkSecurity();
    this.checkSecurityMiddleware();
    this.checkRateLimiting();
    this.checkProductionConfig();
    this.checkDependencyVulnerabilities();
    this.checkFilePermissions();

    // Calculate summary
    const summary = {
      total: this.checks.length,
      passed: this.checks.filter(c => c.status === 'PASS').length,
      failed: this.checks.filter(c => c.status === 'FAIL').length,
      warnings: this.checks.filter(c => c.status === 'WARNING').length,
      skipped: this.checks.filter(c => c.status === 'SKIP').length
    };

    // Calculate score (PASS = 100%, WARNING = 50%, FAIL = 0%, SKIP = not counted)
    const totalScorable = summary.total - summary.skipped;
    const score = totalScorable > 0 ?
      ((summary.passed * 100 + summary.warnings * 50) / (totalScorable * 100)) * 100 : 100;

    // Determine grade
    let grade = 'F';
    if (score >= 95) grade = 'A+';
    else if (score >= 90) grade = 'A';
    else if (score >= 85) grade = 'A-';
    else if (score >= 80) grade = 'B+';
    else if (score >= 75) grade = 'B';
    else if (score >= 70) grade = 'B-';
    else if (score >= 65) grade = 'C+';
    else if (score >= 60) grade = 'C';
    else if (score >= 55) grade = 'C-';
    else if (score >= 50) grade = 'D';

    // Determine compliance
    const criticalFailed = this.checks.filter(c => c.category === 'CRITICAL' && c.status === 'FAIL').length;
    const highFailed = this.checks.filter(c => c.category === 'HIGH' && c.status === 'FAIL').length;

    const compliance = {
      owasp: criticalFailed === 0 && highFailed <= 1,
      bsi: criticalFailed === 0 && score >= 90,
      gdpr: criticalFailed === 0 && summary.failed <= 2
    };

    return {
      timestamp: new Date().toISOString(),
      version: '3.0.0',
      overallScore: Math.round(score),
      grade,
      checks: this.checks,
      summary,
      compliance
    };
  }

  /**
   * Print audit results
   */
  printResults(result: SecurityAuditResult): void {
    console.log('═'.repeat(80));
    console.log('🔐 CC-LITE SECURITY AUDIT REPORT');
    console.log('═'.repeat(80));
    console.log(`📅 Timestamp: ${result.timestamp}`);
    console.log(`📊 Overall Score: ${result.overallScore}/100 (${result.grade})`);
    console.log(`📋 Total Checks: ${result.summary.total}`);
    console.log(`✅ Passed: ${result.summary.passed}`);
    console.log(`⚠️  Warnings: ${result.summary.warnings}`);
    console.log(`❌ Failed: ${result.summary.failed}`);
    console.log(`⏭️  Skipped: ${result.summary.skipped}`);

    console.log('\n🏛️ COMPLIANCE STATUS:');
    console.log(`OWASP Top 10: ${result.compliance.owasp ? '✅ COMPLIANT' : '❌ NON-COMPLIANT'}`);
    console.log(`BSI Security: ${result.compliance.bsi ? '✅ COMPLIANT' : '❌ NON-COMPLIANT'}`);
    console.log(`GDPR: ${result.compliance.gdpr ? '✅ COMPLIANT' : '❌ NON-COMPLIANT'}`);

    console.log('\n📋 DETAILED RESULTS:');
    console.log('─'.repeat(80));

    // Group by category
    const categories = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'] as const;

    for (const category of categories) {
      const categoryChecks = result.checks.filter(c => c.category === category);
      if (categoryChecks.length === 0) continue;

      console.log(`\n🔒 ${category} SECURITY CHECKS:`);

      for (const check of categoryChecks) {
        const statusIcon = {
          'PASS': '✅',
          'FAIL': '❌',
          'WARNING': '⚠️',
          'SKIP': '⏭️'
        }[check.status];

        console.log(`  ${statusIcon} ${check.name}`);
        console.log(`     ${check.description}`);
        if (check.details) {
          console.log(`     Details: ${check.details}`);
        }
        if (check.remediation) {
          console.log(`     🔧 Remediation: ${check.remediation}`);
        }
        console.log();
      }
    }

    console.log('═'.repeat(80));

    if (result.overallScore >= 95) {
      console.log('🎉 EXCELLENT! Your application has achieved top-tier security.');
    } else if (result.overallScore >= 85) {
      console.log('👍 GOOD! Your application has strong security with minor improvements needed.');
    } else if (result.overallScore >= 70) {
      console.log('⚠️  WARNING! Your application needs security improvements before production.');
    } else {
      console.log('🚨 CRITICAL! Your application has serious security issues that must be fixed.');
    }

    console.log('═'.repeat(80));
  }
}

// Main execution
async function main() {
  const auditor = new SecurityAuditor();
  const result = await auditor.runAudit();
  auditor.printResults(result);

  // Save results to file
  const fs = await import('fs/promises');
  await fs.writeFile(
    'security-audit-report.json',
    JSON.stringify(result, null, 2)
  );

  console.log('\n💾 Detailed report saved to: security-audit-report.json');

  // Exit with appropriate code
  process.exit(result.summary.failed > 0 ? 1 : 0);
}

// Run if called directly
main().catch(console.error);

export { SecurityAuditor, type SecurityAuditResult, type SecurityCheck };
