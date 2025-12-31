import { writeFileSync, existsSync, mkdirSync } from 'fs';
import { join } from 'path';

/**
 * Test Reporting Utilities for Voice by Kraliki
 * Generates comprehensive test reports and coverage summaries
 */

interface TestSuite {
  name: string;
  tests: number;
  passing: number;
  failing: number;
  skipped: number;
  duration: number;
  coverage: {
    lines: number;
    functions: number;
    branches: number;
    statements: number;
  };
}

interface TestResult {
  timestamp: string;
  totalSuites: number;
  totalTests: number;
  totalPassing: number;
  totalFailing: number;
  totalSkipped: number;
  totalDuration: number;
  overallCoverage: {
    lines: number;
    functions: number;
    branches: number;
    statements: number;
  };
  suites: TestSuite[];
  performanceMetrics: {
    avgResponseTime: number;
    maxResponseTime: number;
    throughput: number;
    memoryUsage: number;
  };
  securityTests: {
    total: number;
    passed: number;
    failed: number;
    vulnerabilities: string[];
  };
}

export class TestReporter {
  private reportsDir: string;
  private coverageDir: string;

  constructor() {
    this.reportsDir = join(process.cwd(), 'tests', 'reports');
    this.coverageDir = join(process.cwd(), 'coverage');

    // Ensure directories exist
    if (!existsSync(this.reportsDir)) {
      mkdirSync(this.reportsDir, { recursive: true });
    }
    if (!existsSync(this.coverageDir)) {
      mkdirSync(this.coverageDir, { recursive: true });
    }
  }

  /**
   * Generate comprehensive test report
   */
  generateTestReport(results: TestResult): void {
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');

    // Generate JSON report
    this.generateJSONReport(results, timestamp);

    // Generate HTML report
    this.generateHTMLReport(results, timestamp);

    // Generate Markdown summary
    this.generateMarkdownSummary(results, timestamp);

    // Generate coverage badge
    this.generateCoverageBadge(results.overallCoverage);

    // Generate CI/CD report
    this.generateCIReport(results, timestamp);

    console.log(`\n📊 Test reports generated:`);
    console.log(`   • JSON: tests/reports/test-report-${timestamp}.json`);
    console.log(`   • HTML: tests/reports/test-report-${timestamp}.html`);
    console.log(`   • Summary: tests/reports/TESTING-SUMMARY.md`);
    console.log(`   • Coverage Badge: tests/reports/coverage-badge.svg`);
  }

  private generateJSONReport(results: TestResult, timestamp: string): void {
    const jsonReport = {
      ...results,
      metadata: {
        generatedAt: new Date().toISOString(),
        version: '1.0.0',
        environment: process.env.NODE_ENV || 'test',
        node: process.version,
        platform: process.platform,
      },
    };

    writeFileSync(
      join(this.reportsDir, `test-report-${timestamp}.json`),
      JSON.stringify(jsonReport, null, 2)
    );
  }

  private generateHTMLReport(results: TestResult, timestamp: string): void {
    const html = `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Voice by Kraliki Test Report - ${new Date().toLocaleDateString()}</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .header h1 {
            margin: 0;
            font-size: 2.5em;
        }
        .header p {
            margin: 10px 0 0 0;
            opacity: 0.9;
        }
        .summary {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 30px;
        }
        .metric {
            text-align: center;
            padding: 20px;
            border-radius: 8px;
            background: #f8f9fa;
        }
        .metric.success { border-left: 4px solid #28a745; }
        .metric.danger { border-left: 4px solid #dc3545; }
        .metric.warning { border-left: 4px solid #ffc107; }
        .metric.info { border-left: 4px solid #17a2b8; }
        .metric h3 {
            margin: 0 0 10px 0;
            color: #495057;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .metric .value {
            font-size: 2em;
            font-weight: bold;
            color: #212529;
        }
        .coverage-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin: 30px;
        }
        .coverage-item {
            text-align: center;
            padding: 15px;
            border-radius: 6px;
            background: #e9ecef;
        }
        .coverage-bar {
            width: 100%;
            height: 8px;
            background: #dee2e6;
            border-radius: 4px;
            overflow: hidden;
            margin: 10px 0;
        }
        .coverage-fill {
            height: 100%;
            transition: width 0.3s ease;
        }
        .coverage-excellent { background: #28a745; }
        .coverage-good { background: #ffc107; }
        .coverage-poor { background: #dc3545; }
        .suites {
            margin: 30px;
        }
        .suite {
            border: 1px solid #dee2e6;
            border-radius: 6px;
            margin-bottom: 15px;
            overflow: hidden;
        }
        .suite-header {
            background: #f8f9fa;
            padding: 15px;
            font-weight: bold;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .suite-stats {
            font-size: 0.9em;
            color: #6c757d;
        }
        .suite-content {
            padding: 15px;
        }
        .performance, .security {
            margin: 30px;
            padding: 20px;
            border-radius: 6px;
            background: #f8f9fa;
        }
        .performance h2, .security h2 {
            margin-top: 0;
            color: #495057;
        }
        .footer {
            background: #343a40;
            color: white;
            padding: 20px 30px;
            text-align: center;
            font-size: 0.9em;
        }
        .status-pass { color: #28a745; }
        .status-fail { color: #dc3545; }
        .status-skip { color: #ffc107; }
    </style>
</head>
<body>
    <div class="container">
        <header class="header">
            <h1>🧪 Voice by Kraliki Test Report</h1>
            <p>Generated on ${new Date().toLocaleString()}</p>
        </header>

        <section class="summary">
            <div class="metric success">
                <h3>Total Tests</h3>
                <div class="value">${results.totalTests}</div>
            </div>
            <div class="metric ${results.totalFailing > 0 ? 'danger' : 'success'}">
                <h3>Passing</h3>
                <div class="value">${results.totalPassing}</div>
            </div>
            <div class="metric ${results.totalFailing > 0 ? 'danger' : 'info'}">
                <h3>Failing</h3>
                <div class="value">${results.totalFailing}</div>
            </div>
            <div class="metric ${results.totalSkipped > 0 ? 'warning' : 'info'}">
                <h3>Skipped</h3>
                <div class="value">${results.totalSkipped}</div>
            </div>
            <div class="metric info">
                <h3>Duration</h3>
                <div class="value">${(results.totalDuration / 1000).toFixed(1)}s</div>
            </div>
            <div class="metric ${results.overallCoverage.lines >= 80 ? 'success' : results.overallCoverage.lines >= 60 ? 'warning' : 'danger'}">
                <h3>Coverage</h3>
                <div class="value">${results.overallCoverage.lines.toFixed(1)}%</div>
            </div>
        </section>

        <section class="coverage-grid">
            ${['lines', 'functions', 'branches', 'statements'].map(type => `
                <div class="coverage-item">
                    <h4>${type.charAt(0).toUpperCase() + type.slice(1)}</h4>
                    <div class="coverage-bar">
                        <div class="coverage-fill ${this.getCoverageClass(results.overallCoverage[type])}"
                             style="width: ${results.overallCoverage[type]}%"></div>
                    </div>
                    <strong>${results.overallCoverage[type].toFixed(1)}%</strong>
                </div>
            `).join('')}
        </section>

        <section class="suites">
            <h2>📋 Test Suites</h2>
            ${results.suites.map(suite => `
                <div class="suite">
                    <div class="suite-header">
                        <span>${suite.name}</span>
                        <span class="suite-stats">
                            <span class="status-pass">${suite.passing} passed</span>
                            ${suite.failing > 0 ? `<span class="status-fail">${suite.failing} failed</span>` : ''}
                            ${suite.skipped > 0 ? `<span class="status-skip">${suite.skipped} skipped</span>` : ''}
                        </span>
                    </div>
                    <div class="suite-content">
                        <p><strong>Duration:</strong> ${(suite.duration / 1000).toFixed(1)}s</p>
                        <p><strong>Coverage:</strong> ${suite.coverage.lines.toFixed(1)}% lines</p>
                    </div>
                </div>
            `).join('')}
        </section>

        <section class="performance">
            <h2>⚡ Performance Metrics</h2>
            <div class="summary">
                <div class="metric info">
                    <h3>Avg Response Time</h3>
                    <div class="value">${results.performanceMetrics.avgResponseTime.toFixed(0)}ms</div>
                </div>
                <div class="metric info">
                    <h3>Max Response Time</h3>
                    <div class="value">${results.performanceMetrics.maxResponseTime.toFixed(0)}ms</div>
                </div>
                <div class="metric info">
                    <h3>Throughput</h3>
                    <div class="value">${results.performanceMetrics.throughput.toFixed(1)}/s</div>
                </div>
                <div class="metric info">
                    <h3>Memory Usage</h3>
                    <div class="value">${results.performanceMetrics.memoryUsage.toFixed(1)}MB</div>
                </div>
            </div>
        </section>

        <section class="security">
            <h2>🔒 Security Tests</h2>
            <div class="summary">
                <div class="metric success">
                    <h3>Total Tests</h3>
                    <div class="value">${results.securityTests.total}</div>
                </div>
                <div class="metric ${results.securityTests.failed > 0 ? 'danger' : 'success'}">
                    <h3>Passed</h3>
                    <div class="value">${results.securityTests.passed}</div>
                </div>
                <div class="metric ${results.securityTests.failed > 0 ? 'danger' : 'success'}">
                    <h3>Failed</h3>
                    <div class="value">${results.securityTests.failed}</div>
                </div>
            </div>
            ${results.securityTests.vulnerabilities.length > 0 ? `
                <div style="margin-top: 20px;">
                    <h3>⚠️ Security Issues Found:</h3>
                    <ul>
                        ${results.securityTests.vulnerabilities.map(vuln => `<li>${vuln}</li>`).join('')}
                    </ul>
                </div>
            ` : '<div style="margin-top: 20px; color: #28a745;"><strong>✅ No security vulnerabilities found</strong></div>'}
        </section>

        <footer class="footer">
            <p>Generated by Voice by Kraliki Test Suite • ${new Date().toISOString()}</p>
        </footer>
    </div>
</body>
</html>`;

    writeFileSync(
      join(this.reportsDir, `test-report-${timestamp}.html`),
      html
    );
  }

  private generateMarkdownSummary(results: TestResult, timestamp: string): void {
    const coverageEmoji = (percentage: number) => {
      if (percentage >= 80) return '🟢';
      if (percentage >= 60) return '🟡';
      return '🔴';
    };

    const markdown = `# 🧪 Voice by Kraliki Testing Summary

**Generated:** ${new Date().toLocaleString()}

## 📊 Overall Results

| Metric | Value | Status |
|--------|-------|--------|
| Total Tests | ${results.totalTests} | ✅ |
| Passing | ${results.totalPassing} | ${results.totalFailing === 0 ? '✅' : '⚠️'} |
| Failing | ${results.totalFailing} | ${results.totalFailing === 0 ? '✅' : '❌'} |
| Skipped | ${results.totalSkipped} | ${results.totalSkipped === 0 ? '✅' : '⚠️'} |
| Duration | ${(results.totalDuration / 1000).toFixed(1)}s | ⏱️ |

## 📈 Coverage Metrics

| Type | Coverage | Status |
|------|----------|--------|
| Lines | ${results.overallCoverage.lines.toFixed(1)}% | ${coverageEmoji(results.overallCoverage.lines)} |
| Functions | ${results.overallCoverage.functions.toFixed(1)}% | ${coverageEmoji(results.overallCoverage.functions)} |
| Branches | ${results.overallCoverage.branches.toFixed(1)}% | ${coverageEmoji(results.overallCoverage.branches)} |
| Statements | ${results.overallCoverage.statements.toFixed(1)}% | ${coverageEmoji(results.overallCoverage.statements)} |

${results.overallCoverage.lines >= 80 ? '🎉 **Excellent coverage! Target of 80% achieved.**' :
  results.overallCoverage.lines >= 60 ? '⚠️ **Good coverage, but can be improved. Target: 80%**' :
  '❌ **Coverage below acceptable threshold. Target: 80%**'}

## 🏃‍♂️ Performance Metrics

| Metric | Value |
|--------|-------|
| Average Response Time | ${results.performanceMetrics.avgResponseTime.toFixed(0)}ms |
| Maximum Response Time | ${results.performanceMetrics.maxResponseTime.toFixed(0)}ms |
| Throughput | ${results.performanceMetrics.throughput.toFixed(1)} req/s |
| Memory Usage | ${results.performanceMetrics.memoryUsage.toFixed(1)} MB |

## 🔒 Security Test Results

| Metric | Value | Status |
|--------|-------|--------|
| Total Security Tests | ${results.securityTests.total} | ✅ |
| Passed | ${results.securityTests.passed} | ${results.securityTests.failed === 0 ? '✅' : '⚠️'} |
| Failed | ${results.securityTests.failed} | ${results.securityTests.failed === 0 ? '✅' : '❌'} |

${results.securityTests.vulnerabilities.length > 0 ?
  `### ⚠️ Security Issues Found:\n${results.securityTests.vulnerabilities.map(v => `- ${v}`).join('\n')}` :
  '✅ **No security vulnerabilities detected**'}

## 📋 Test Suite Breakdown

${results.suites.map(suite => `
### ${suite.name}
- **Tests:** ${suite.tests}
- **Passing:** ${suite.passing} ✅
- **Failing:** ${suite.failing} ${suite.failing > 0 ? '❌' : ''}
- **Skipped:** ${suite.skipped} ${suite.skipped > 0 ? '⚠️' : ''}
- **Duration:** ${(suite.duration / 1000).toFixed(1)}s
- **Coverage:** ${suite.coverage.lines.toFixed(1)}% lines
`).join('')}

## 🚀 Recommendations

${this.generateRecommendations(results)}

---
*Report generated by Voice by Kraliki Test Suite on ${new Date().toISOString()}*
`;

    writeFileSync(
      join(this.reportsDir, 'TESTING-SUMMARY.md'),
      markdown
    );
  }

  private generateCoverageBadge(coverage: any): void {
    const percentage = coverage.lines;
    const color = percentage >= 80 ? 'brightgreen' : percentage >= 60 ? 'yellow' : 'red';

    const badge = `<svg xmlns="http://www.w3.org/2000/svg" width="104" height="20">
      <linearGradient id="b" x2="0" y2="100%">
        <stop offset="0" stop-color="#bbb" stop-opacity=".1"/>
        <stop offset="1" stop-opacity=".1"/>
      </linearGradient>
      <clipPath id="a">
        <rect width="104" height="20" rx="3" fill="#fff"/>
      </clipPath>
      <g clip-path="url(#a)">
        <path fill="#555" d="M0 0h63v20H0z"/>
        <path fill="${color === 'brightgreen' ? '#4c1' : color === 'yellow' ? '#dfb317' : '#e05d44'}" d="M63 0h41v20H63z"/>
        <path fill="url(#b)" d="M0 0h104v20H0z"/>
      </g>
      <g fill="#fff" text-anchor="middle" font-family="DejaVu Sans,Verdana,Geneva,sans-serif" font-size="110">
        <text x="325" y="150" fill="#010101" fill-opacity=".3" transform="scale(.1)" textLength="530">coverage</text>
        <text x="325" y="140" transform="scale(.1)" textLength="530">coverage</text>
        <text x="825" y="150" fill="#010101" fill-opacity=".3" transform="scale(.1)" textLength="310">${percentage.toFixed(0)}%</text>
        <text x="825" y="140" transform="scale(.1)" textLength="310">${percentage.toFixed(0)}%</text>
      </g>
    </svg>`;

    writeFileSync(
      join(this.reportsDir, 'coverage-badge.svg'),
      badge
    );
  }

  private generateCIReport(results: TestResult, timestamp: string): void {
    const ciReport = {
      status: results.totalFailing === 0 ? 'success' : 'failure',
      coverage: results.overallCoverage.lines,
      tests: {
        total: results.totalTests,
        passed: results.totalPassing,
        failed: results.totalFailing,
        skipped: results.totalSkipped,
      },
      performance: {
        avgResponseTime: results.performanceMetrics.avgResponseTime,
        maxResponseTime: results.performanceMetrics.maxResponseTime,
      },
      security: {
        passed: results.securityTests.passed,
        failed: results.securityTests.failed,
        vulnerabilities: results.securityTests.vulnerabilities.length,
      },
      timestamp: results.timestamp,
    };

    writeFileSync(
      join(this.reportsDir, 'ci-report.json'),
      JSON.stringify(ciReport, null, 2)
    );
  }

  private getCoverageClass(percentage: number): string {
    if (percentage >= 80) return 'coverage-excellent';
    if (percentage >= 60) return 'coverage-good';
    return 'coverage-poor';
  }

  private generateRecommendations(results: TestResult): string {
    const recommendations = [];

    // Coverage recommendations
    if (results.overallCoverage.lines < 80) {
      recommendations.push('🎯 **Coverage:** Increase test coverage to reach the 80% target. Focus on service layer and critical components.');
    }

    // Performance recommendations
    if (results.performanceMetrics.avgResponseTime > 300) {
      recommendations.push('⚡ **Performance:** Average response time is above 300ms. Consider optimizing database queries and API endpoints.');
    }

    // Security recommendations
    if (results.securityTests.failed > 0) {
      recommendations.push('🔒 **Security:** Address failing security tests immediately. Review authentication and input validation.');
    }

    // Test failure recommendations
    if (results.totalFailing > 0) {
      recommendations.push('🔧 **Reliability:** Fix failing tests to ensure system stability. Investigate root causes and improve error handling.');
    }

    // Memory recommendations
    if (results.performanceMetrics.memoryUsage > 512) {
      recommendations.push('💾 **Memory:** Memory usage is high. Review for memory leaks and optimize resource usage.');
    }

    if (recommendations.length === 0) {
      recommendations.push('🎉 **Excellent!** All metrics are within acceptable ranges. Keep up the good work!');
    }

    return recommendations.join('\n\n');
  }

  /**
   * Create sample test results for demonstration
   */
  static createSampleResults(): TestResult {
    return {
      timestamp: new Date().toISOString(),
      totalSuites: 8,
      totalTests: 247,
      totalPassing: 235,
      totalFailing: 2,
      totalSkipped: 10,
      totalDuration: 45678,
      overallCoverage: {
        lines: 83.4,
        functions: 87.2,
        branches: 79.8,
        statements: 84.1,
      },
      suites: [
        {
          name: 'Service Layer Unit Tests',
          tests: 89,
          passing: 87,
          failing: 1,
          skipped: 1,
          duration: 12456,
          coverage: { lines: 91.2, functions: 94.1, branches: 88.7, statements: 92.3 },
        },
        {
          name: 'tRPC Router Integration Tests',
          tests: 64,
          passing: 62,
          failing: 1,
          skipped: 1,
          duration: 8934,
          coverage: { lines: 85.3, functions: 89.2, branches: 82.1, statements: 86.7 },
        },
        {
          name: 'Security Tests',
          tests: 45,
          passing: 45,
          failing: 0,
          skipped: 0,
          duration: 7123,
          coverage: { lines: 78.9, functions: 82.3, branches: 75.4, statements: 80.1 },
        },
        {
          name: 'Performance Tests',
          tests: 25,
          passing: 22,
          failing: 0,
          skipped: 3,
          duration: 15234,
          coverage: { lines: 69.4, functions: 72.8, branches: 65.2, statements: 71.1 },
        },
        {
          name: 'Component Tests',
          tests: 24,
          passing: 19,
          failing: 0,
          skipped: 5,
          duration: 1931,
          coverage: { lines: 76.5, functions: 80.9, branches: 73.2, statements: 78.3 },
        },
      ],
      performanceMetrics: {
        avgResponseTime: 145,
        maxResponseTime: 892,
        throughput: 48.7,
        memoryUsage: 287.4,
      },
      securityTests: {
        total: 45,
        passed: 45,
        failed: 0,
        vulnerabilities: [],
      },
    };
  }
}

// Export utility function for generating reports
export function generateTestReport(results?: TestResult): void {
  const reporter = new TestReporter();
  const testResults = results || TestReporter.createSampleResults();
  reporter.generateTestReport(testResults);
}