#!/usr/bin/env node

/**
 * Security validation script for Focus by Kraliki
 * Checks for common security issues and misconfigurations
 */

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

class SecurityChecker {
  constructor() {
    this.issues = [];
    this.warnings = [];
    this.rootDir = process.cwd();
  }

  log(message, level = 'info') {
    const timestamp = new Date().toISOString();
    const prefix = level === 'error' ? '❌' : level === 'warn' ? '⚠️' : '✅';
    console.log(`${prefix} [${timestamp}] ${message}`);
  }

  addIssue(message, severity = 'high') {
    this.issues.push({ message, severity, timestamp: new Date().toISOString() });
    this.log(message, 'error');
  }

  addWarning(message) {
    this.warnings.push({ message, timestamp: new Date().toISOString() });
    this.log(message, 'warn');
  }

  // Check for exposed environment files
  checkEnvironmentFiles() {
    const envFiles = ['.env', '.env.local', '.env.production', '.env.development'];

    envFiles.forEach(file => {
      const filePath = path.join(this.rootDir, file);
      if (fs.existsSync(filePath) && !file.includes('.example') && !file.includes('.template')) {
        this.addIssue(`Environment file found in repository: ${file}`, 'critical');
      }
    });

    // Check for environment files in subdirectories
    ['backend', 'frontend'].forEach(dir => {
      const dirPath = path.join(this.rootDir, dir);
      if (fs.existsSync(dirPath)) {
        envFiles.forEach(file => {
          const filePath = path.join(dirPath, file);
          if (fs.existsSync(filePath) && !file.includes('.example')) {
            this.addIssue(`Environment file found in ${dir}: ${file}`, 'critical');
          }
        });
      }
    });
  }

  // Check for hardcoded secrets
  checkHardcodedSecrets() {
    const secretPatterns = [
      /['\"]sk-[a-zA-Z0-9]{48}['\"]/g, // OpenAI API keys
      /['\"]sk-ant-api[0-9]{2}-[a-zA-Z0-9_-]{95}['\"]/g, // Anthropic API keys
      /['\"][0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}['\"]/g, // UUID patterns
      /['\"](?:password|secret|key)['\"]\s*:\s*['\"]\w+['\"]/gi, // Generic secret patterns
      /jwt_secret\s*=\s*['\"]\w+['\"]/gi, // JWT secrets
    ];

    const checkFile = (filePath, relativePath) => {
      try {
        const content = fs.readFileSync(filePath, 'utf8');
        secretPatterns.forEach((pattern, index) => {
          const matches = content.match(pattern);
          if (matches) {
            this.addIssue(`Potential hardcoded secret found in ${relativePath}: ${matches[0].substring(0, 20)}...`, 'high');
          }
        });
      } catch (error) {
        // Ignore files that can't be read
      }
    };

    const walkDirectory = (dir, basePath = '') => {
      try {
        const entries = fs.readdirSync(dir, { withFileTypes: true });

        entries.forEach(entry => {
          const fullPath = path.join(dir, entry.name);
          const relativePath = path.join(basePath, entry.name);

          // Skip node_modules and .git
          if (entry.name === 'node_modules' || entry.name === '.git' || entry.name === 'dist' || entry.name === 'build') {
            return;
          }

          if (entry.isDirectory()) {
            walkDirectory(fullPath, relativePath);
          } else if (entry.isFile() && (entry.name.endsWith('.ts') || entry.name.endsWith('.js') || entry.name.endsWith('.json'))) {
            checkFile(fullPath, relativePath);
          }
        });
      } catch (error) {
        // Ignore directories that can't be read
      }
    };

    walkDirectory(this.rootDir);
  }

  // Check for unsafe network bindings
  checkNetworkBindings() {
    const unsafePatterns = [
      /listen\s*\(\s*['"]0\.0\.0\.0['"]/, // Express/Fastify binding to 0.0.0.0
      /host\s*:\s*['"]0\.0\.0\.0['"]/, // Vite config binding to 0.0.0.0
      /--host\s+0\.0\.0\.0/, // CLI arguments
    ];

    const checkFile = (filePath, relativePath) => {
      try {
        const content = fs.readFileSync(filePath, 'utf8');
        unsafePatterns.forEach(pattern => {
          if (pattern.test(content)) {
            this.addIssue(`Unsafe network binding (0.0.0.0) found in ${relativePath}`, 'high');
          }
        });
      } catch (error) {
        // Ignore files that can't be read
      }
    };

    // Check specific files
    const filesToCheck = [
      'backend/src/server.ts',
      'backend/src/server.js',
      'frontend/vite.config.ts',
      'frontend/vite.config.js',
      'package.json',
      'backend/package.json',
      'frontend/package.json'
    ];

    filesToCheck.forEach(file => {
      const filePath = path.join(this.rootDir, file);
      if (fs.existsSync(filePath)) {
        checkFile(filePath, file);
      }
    });
  }

  // Check Docker configurations
  checkDockerSecurity() {
    const dockerFiles = ['Dockerfile', 'docker-compose.yml', 'docker-compose.yaml'];

    dockerFiles.forEach(file => {
      const filePath = path.join(this.rootDir, file);
      if (fs.existsSync(filePath)) {
        try {
          const content = fs.readFileSync(filePath, 'utf8');

          // Check for running as root
          if (content.includes('USER root') || !content.includes('USER ')) {
            this.addWarning(`Docker file ${file} may be running as root user`);
          }

          // Check for exposed ports
          const portMatches = content.match(/EXPOSE\s+(\d+)/g);
          if (portMatches) {
            portMatches.forEach(match => {
              const port = match.split(' ')[1];
              if (parseInt(port) < 1024) {
                this.addWarning(`Docker file ${file} exposes privileged port ${port}`);
              }
            });
          }

          // Check for 0.0.0.0 bindings in docker-compose
          if (file.includes('docker-compose') && content.includes('0.0.0.0:')) {
            this.addIssue(`Docker compose file ${file} contains 0.0.0.0 binding`, 'medium');
          }

        } catch (error) {
          this.addWarning(`Could not read Docker file ${file}: ${error.message}`);
        }
      }
    });
  }

  // Check package.json for security issues
  checkPackageSecurity() {
    const packageFiles = ['package.json', 'backend/package.json', 'frontend/package.json'];

    packageFiles.forEach(file => {
      const filePath = path.join(this.rootDir, file);
      if (fs.existsSync(filePath)) {
        try {
          const packageJson = JSON.parse(fs.readFileSync(filePath, 'utf8'));

          // Check for npm scripts that might be unsafe
          if (packageJson.scripts) {
            Object.entries(packageJson.scripts).forEach(([name, script]) => {
              if (script.includes('rm -rf /') || script.includes('sudo')) {
                this.addIssue(`Potentially dangerous script in ${file}: ${name}`, 'high');
              }

              if (script.includes('--host 0.0.0.0')) {
                this.addWarning(`Script '${name}' in ${file} binds to 0.0.0.0`);
              }
            });
          }

          // Check for development dependencies in production
          if (file === 'package.json' && packageJson.dependencies) {
            const devDeps = ['nodemon', 'ts-node', 'tsx'];
            devDeps.forEach(dep => {
              if (packageJson.dependencies[dep]) {
                this.addWarning(`Development dependency ${dep} found in production dependencies in ${file}`);
              }
            });
          }

        } catch (error) {
          this.addWarning(`Could not parse package.json file ${file}: ${error.message}`);
        }
      }
    });
  }

  // Check for sensitive files that shouldn't be committed
  checkSensitiveFiles() {
    const sensitiveFiles = [
      'id_rsa',
      'id_dsa',
      '.ssh/id_rsa',
      '.ssh/id_dsa',
      'credentials.json',
      'service-account.json',
      '.aws/credentials',
      '.aws/config',
      'secrets.json',
      'private.key',
      '.pem'
    ];

    const checkDirectory = (dir, basePath = '') => {
      try {
        const entries = fs.readdirSync(dir, { withFileTypes: true });

        entries.forEach(entry => {
          const fullPath = path.join(dir, entry.name);
          const relativePath = path.join(basePath, entry.name);

          if (entry.name === 'node_modules' || entry.name === '.git') {
            return;
          }

          if (entry.isDirectory()) {
            checkDirectory(fullPath, relativePath);
          } else if (entry.isFile()) {
            sensitiveFiles.forEach(sensitive => {
              if (entry.name.includes(sensitive) || relativePath.includes(sensitive)) {
                this.addIssue(`Sensitive file found in repository: ${relativePath}`, 'critical');
              }
            });
          }
        });
      } catch (error) {
        // Ignore directories that can't be read
      }
    };

    checkDirectory(this.rootDir);
  }

  // Generate security report
  generateReport() {
    const report = {
      timestamp: new Date().toISOString(),
      summary: {
        criticalIssues: this.issues.filter(i => i.severity === 'critical').length,
        highIssues: this.issues.filter(i => i.severity === 'high').length,
        mediumIssues: this.issues.filter(i => i.severity === 'medium').length,
        warnings: this.warnings.length,
        totalIssues: this.issues.length
      },
      issues: this.issues,
      warnings: this.warnings
    };

    // Write report to file
    fs.writeFileSync('security-report.json', JSON.stringify(report, null, 2));

    return report;
  }

  // Run all security checks
  async runAllChecks() {
    this.log('Starting security validation...', 'info');

    this.log('Checking environment files...', 'info');
    this.checkEnvironmentFiles();

    this.log('Checking for hardcoded secrets...', 'info');
    this.checkHardcodedSecrets();

    this.log('Checking network bindings...', 'info');
    this.checkNetworkBindings();

    this.log('Checking Docker security...', 'info');
    this.checkDockerSecurity();

    this.log('Checking package security...', 'info');
    this.checkPackageSecurity();

    this.log('Checking for sensitive files...', 'info');
    this.checkSensitiveFiles();

    const report = this.generateReport();

    // Print summary
    console.log('\n📊 Security Check Summary:');
    console.log(`Critical Issues: ${report.summary.criticalIssues}`);
    console.log(`High Issues: ${report.summary.highIssues}`);
    console.log(`Medium Issues: ${report.summary.mediumIssues}`);
    console.log(`Warnings: ${report.summary.warnings}`);

    if (report.summary.criticalIssues > 0) {
      this.log('❌ Security validation failed - critical issues found!', 'error');
      process.exit(1);
    } else if (report.summary.highIssues > 0) {
      this.log('⚠️ Security validation completed with high-priority issues', 'warn');
      process.exit(1);
    } else {
      this.log('✅ Security validation passed!', 'info');
      process.exit(0);
    }
  }
}

// Run security checks if called directly
if (require.main === module) {
  const checker = new SecurityChecker();
  checker.runAllChecks().catch(error => {
    console.error('Security check failed:', error);
    process.exit(1);
  });
}

module.exports = SecurityChecker;