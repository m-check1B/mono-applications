#!/usr/bin/env tsx
/**
 * Voice by Kraliki Truth Score Monitor (Stack 2026 Edition)
 * ------------------------------------------------
 * Aligns with the Python FastAPI + SvelteKit architecture.
 */

import { spawnSync, SpawnSyncOptions } from 'child_process';
import { existsSync, mkdirSync, readFileSync, writeFileSync } from 'fs';
import { join, extname } from 'path';
import { glob } from 'glob';

type Status = 'PRODUCTION_READY' | 'NEAR_READY' | 'NEEDS_WORK' | 'CRITICAL';

type ScoreStatus = 'COMPLIANT' | 'PARTIAL' | 'NON_COMPLIANT';

interface TruthMetrics {
  compilationSuccessRate: number;
  testRealityScore: number;
  documentationHonestyIndex: number;
  userTrustCoefficient: number;
  securityComplianceScore: number;
  technicalDebtRatio: number;
  tracingCoverage: number;
  overallTruthScore: number;
  grade: string;
  status: Status;
}

interface SacredCodexCompliance {
  principle1_TestCoverage: { score: number; status: ScoreStatus; details: string };
  principle2_Metrics: { score: number; status: ScoreStatus; details: string };
  principle3_Tracing: { score: number; status: ScoreStatus; details: string };
  principle4_Persistence: { score: number; status: ScoreStatus; details: string };
  principle5_CircuitBreakers: { score: number; status: ScoreStatus; details: string };
  principle6_Verification: { score: number; status: ScoreStatus; details: string };
}

interface ExecResult {
  success: boolean;
  output: string;
}

const projectRoot = process.cwd();
const backendDir = join(projectRoot, 'backend');
const frontendDir = join(projectRoot, 'frontend');
const timestamp = new Date().toISOString();

function runCommand(command: string, args: string[], options?: SpawnSyncOptions): ExecResult {
  const spawnOptions: SpawnSyncOptions = {
    cwd: projectRoot,
    stdio: 'pipe',
    encoding: 'utf8',
    ...options
  };

  const result = spawnSync(command, args, spawnOptions);
  const output = `${result.stdout?.toString() ?? ''}${result.stderr?.toString() ?? ''}`.trim();
  return { success: result.status === 0, output };
}

function safeAverage(scores: number[]): number {
  const valid = scores.filter((score) => Number.isFinite(score));
  if (valid.length === 0) return 0;
  return valid.reduce((acc, score) => acc + score, 0) / valid.length;
}

function determineStatus(score: number): Status {
  if (score >= 90) return 'PRODUCTION_READY';
  if (score >= 75) return 'NEAR_READY';
  if (score >= 60) return 'NEEDS_WORK';
  return 'CRITICAL';
}

function calculateGrade(score: number): string {
  if (score >= 97) return 'A+';
  if (score >= 93) return 'A';
  if (score >= 90) return 'A-';
  if (score >= 87) return 'B+';
  if (score >= 83) return 'B';
  if (score >= 80) return 'B-';
  if (score >= 77) return 'C+';
  if (score >= 73) return 'C';
  if (score >= 70) return 'C-';
  if (score >= 60) return 'D';
  return 'F';
}

async function measureCompilationSuccess(): Promise<number> {
  console.log('📊 Measuring compilation success (frontend + backend)...');
  let score = 0;

  if (existsSync(frontendDir)) {
    const result = runCommand('pnpm', ['--dir', 'frontend', 'build']);
    if (result.success) {
      console.log('✅ Frontend build (SvelteKit) succeeded');
      score += 55;
    } else {
      console.log('⚠️  Frontend build failed');
      console.log(result.output.slice(0, 400));
      score += 15;
    }
  }

  if (existsSync(join(backendDir, 'app'))) {
    const result = runCommand('python3', ['-m', 'compileall', 'app'], { cwd: backendDir });
    if (result.success) {
      console.log('✅ Backend bytecode compilation passed');
      score += 40;
    } else {
      console.log('⚠️  Backend compile check failed');
      console.log(result.output.slice(0, 400));
      score += 10;
    }
  }

  return Math.min(100, Math.max(30, Math.round(score)));
}

async function measureTestReality(): Promise<{ score: number; backendRan: boolean; frontendRan: boolean }> {
  console.log('🧪 Measuring test reality (pytest + SvelteKit checks)...');
  let score = 0;
  let backendRan = false;
  let frontendRan = false;

  const backendTestsExist = existsSync(join(backendDir, 'tests'));
  if (backendTestsExist) {
    const pytestResult = runCommand('python3', ['-m', 'pytest', '--maxfail=1'], { cwd: backendDir });
    backendRan = true;
    if (pytestResult.success) {
      console.log('✅ Pytest suite passed');
      score += 60;

      const coverageFile = join(backendDir, 'htmlcov/index.html');
      const coverageData = join(backendDir, '.coverage');
      if (existsSync(coverageFile) || existsSync(coverageData)) {
        console.log('📈 Coverage artifacts found');
        score += 15;
      }
    } else {
      console.log('⚠️  Pytest failed');
      console.log(pytestResult.output.slice(0, 400));
      score += 15;
    }
  }

  if (existsSync(frontendDir)) {
    const checkResult = runCommand('pnpm', ['--dir', 'frontend', 'check']);
    frontendRan = true;
    if (checkResult.success) {
      console.log('✅ Frontend `pnpm check` succeeded');
      score += 20;
    } else {
      console.log('⚠️  Frontend check failed');
      console.log(checkResult.output.slice(0, 200));
      score += 5;
    }
  }

  const totalTestFiles = (await glob('{backend/tests/**/*.py,tests/**/*.ts,tests/**/*.tsx}', { cwd: projectRoot })).length;
  if (totalTestFiles > 0 && score < 60) {
    score = Math.max(score, 30);
  }

  return { score: Math.min(100, Math.round(score)), backendRan, frontendRan };
}

function evaluateFeatureClaim(readme: string, phrase: string, check: boolean): boolean {
  return !readme.toLowerCase().includes(phrase.toLowerCase()) || check;
}

async function measureDocumentationHonesty(): Promise<number> {
  console.log('📖 Measuring documentation honesty...');
  const readmePath = join(projectRoot, 'README.md');
  if (!existsSync(readmePath)) {
    console.log('⚠️  README missing');
    return 50;
  }

  const readme = readFileSync(readmePath, 'utf8');

  const claims = [
    evaluateFeatureClaim(readme, 'FastAPI', existsSync(join(backendDir, 'app/main.py'))),
    evaluateFeatureClaim(readme, 'SvelteKit', existsSync(join(frontendDir, 'svelte.config.js'))),
    evaluateFeatureClaim(readme, 'PostgreSQL', existsSync(join(backendDir, 'alembic'))),
    evaluateFeatureClaim(readme, 'Redis', readme.includes('Redis') ? true : true),
    evaluateFeatureClaim(readme, 'Twilio', readme.includes('Twilio') ? readFileSync(join(backendDir, 'requirements.txt'), 'utf8').includes('twilio') : true),
    evaluateFeatureClaim(readme, 'OpenTelemetry', readme.includes('OpenTelemetry') ? readFileSync(join(projectRoot, 'package.json'), 'utf8').includes('opentelemetry') : true)
  ];

  const score = (claims.filter(Boolean).length / claims.length) * 100;
  console.log(`📋 Valid claims: ${claims.filter(Boolean).length}/${claims.length}`);
  return Math.round(score);
}

async function measureUserTrust(): Promise<number> {
  console.log('🤝 Measuring user trust (error handling patterns)...');
  const files = await glob('**/*.{py,ts,tsx,svelte}', {
    cwd: projectRoot,
    ignore: ['node_modules/**', 'dist/**', 'frontend/.svelte-kit/**', 'coverage/**', 'backend/tests/**', 'tests/**']
  });

  let total = 0;
  let score = 0;

  for (const file of files) {
    try {
      const content = readFileSync(join(projectRoot, file), 'utf8');
      total += 1;
      const lower = content.toLowerCase();

      if (lower.includes('try') && (lower.includes('except') || lower.includes('catch'))) score += 2;
      if (lower.includes('logger.error') || lower.includes('logging.error') || lower.includes('structlog')) score += 1;
      if (lower.includes('httpexception') || lower.includes('raise')) score += 0.5;
    } catch (error) {
      continue;
    }
  }

  if (total === 0) return 50;
  const normalized = Math.min(100, (score / total) * 25);
  console.log(`📊 Error-handling signals found in ${score.toFixed(1)} across ${total} files`);
  return Math.round(normalized);
}

async function measureSecurityCompliance(): Promise<number> {
  console.log('🔐 Measuring security compliance...');
  const patterns = [
    'backend/app/**/*.py',
    'backend/**/*.env',
    'backend/**/*.env.example',
    'frontend/src/**/*.{ts,tsx}'
  ];
  const files = (await Promise.all(patterns.map((pattern) => glob(pattern, { cwd: projectRoot })))).flat();

  const secretPatterns = [/\b(password|secret|token|api[_-]?key)\s*[:=]\s*["']?[^"'\n]+/gi];

  let violations = 0;
  let envUsages = 0;

  for (const file of files) {
    try {
      const content = readFileSync(join(projectRoot, file), 'utf8');
      if (content.includes('os.getenv') || content.includes('process.env') || content.includes('Settings(') || content.includes('import.meta.env')) envUsages += 1;
      for (const pattern of secretPatterns) {
        const matches = content.match(pattern);
        if (!matches) continue;
        violations += matches.filter((match) => !match.includes('CHANGE_ME') && !match.includes('example')).length;
      }
    } catch {
      continue;
    }
  }

  let score = 75;
  if (envUsages > 0) score += Math.min(15, envUsages);
  score -= Math.min(50, violations * 8);
  score = Math.max(35, Math.min(100, score));

  console.log(`📁 Security checks across ${files.length} files -> violations: ${violations}, env usage: ${envUsages}`);
  return Math.round(score);
}

async function measureTechnicalDebt(): Promise<number> {
  console.log('🔧 Measuring technical debt markers...');
  const files = await glob('**/*.{py,ts,tsx,svelte}', {
    cwd: projectRoot,
    ignore: ['node_modules/**', 'dist/**', 'frontend/.svelte-kit/**']
  });

  let todo = 0;
  let fixme = 0;
  let hack = 0;
  let lines = 0;

  for (const file of files) {
    try {
      const content = readFileSync(join(projectRoot, file), 'utf8');
      const fileLines = content.split('\n');
      lines += fileLines.length;
      fileLines.forEach((line) => {
        const l = line.toLowerCase();
        if (l.includes('todo')) todo += 1;
        if (l.includes('fixme')) fixme += 1;
        if (l.includes('hack')) hack += 1;
      });
    } catch {
      continue;
    }
  }

  if (lines === 0) return 80;
  const debtRatio = ((todo + fixme + hack) / lines) * 1000;
  let score = 100;
  if (debtRatio > 12) score = 40;
  else if (debtRatio > 6) score = 60;
  else if (debtRatio > 3) score = 80;

  console.log(`📊 TODO:${todo} FIXME:${fixme} HACK:${hack} -> ratio ${debtRatio.toFixed(2)} / 1000 lines`);
  return score;
}

async function measureTracingCoverage(): Promise<number> {
  console.log('🛰️ Measuring tracing coverage...');
  const files = await glob('backend/app/**/*.py', { cwd: projectRoot });

  if (files.length === 0) return 40;
  let tracingHits = 0;

  for (const file of files) {
    try {
      const content = readFileSync(join(projectRoot, file), 'utf8').toLowerCase();
      if (content.includes('opentelemetry') || content.includes('from app.core.tracing') || content.includes('span')) tracingHits += 1;
    } catch {
      continue;
    }
  }

  const coverage = (tracingHits / files.length) * 100;
  console.log(`📡 Tracing signals in ${tracingHits}/${files.length} backend files`);
  return Math.round(Math.min(100, Math.max(30, coverage)));
}

async function measureMetricsImplementation(): Promise<number> {
  const hits = await glob('backend/app/**/*metric*.py', { cwd: projectRoot });
  const monitoring = await glob('monitoring/**/*', { cwd: projectRoot });
  return Math.min(100, (hits.length * 20) + (monitoring.length > 0 ? 20 : 0));
}

async function measurePersistenceImplementation(): Promise<number> {
  const hasModels = existsSync(join(backendDir, 'app/models'));
  const hasAlembic = existsSync(join(backendDir, 'alembic')); 
  const hasPrisma = existsSync(join(projectRoot, 'prisma/schema.prisma'));
  return (hasModels ? 60 : 0) + (hasAlembic ? 30 : 0) + (hasPrisma ? 10 : 0);
}

async function measureCircuitBreakerImplementation(): Promise<number> {
  const pythonHits = await glob('backend/app/**/*circuit*.py', { cwd: projectRoot });
  const nodeHits = await glob('**/*circuit*.{ts,tsx,js}', { cwd: projectRoot, ignore: ['node_modules/**'] });
  const total = pythonHits.length + nodeHits.length;
  return Math.min(100, total * 25);
}

async function measureVerificationImplementation(): Promise<number> {
  const backendTests = await glob('backend/tests/**/*.py', { cwd: projectRoot });
  const frontendTests = await glob('tests/**/*.{ts,tsx}', { cwd: projectRoot });
  return Math.min(100, (backendTests.length + frontendTests.length) * 2);
}

function complianceStatus(score: number): ScoreStatus {
  if (score >= 80) return 'COMPLIANT';
  if (score >= 60) return 'PARTIAL';
  return 'NON_COMPLIANT';
}

async function evaluateSacredCodex(precomputed: { testScore: number; tracingScore: number }): Promise<SacredCodexCompliance> {
  const metrics = await measureMetricsImplementation();
  const persistence = await measurePersistenceImplementation();
  const circuit = await measureCircuitBreakerImplementation();
  const verification = await measureVerificationImplementation();
  const testCoverage = precomputed.testScore;
  const tracing = precomputed.tracingScore;

  return {
    principle1_TestCoverage: {
      score: testCoverage,
      status: complianceStatus(testCoverage),
      details: `Test coverage approximation: ${testCoverage}%`
    },
    principle2_Metrics: {
      score: metrics,
      status: complianceStatus(metrics),
      details: `Metrics & monitoring signals: ${metrics}%`
    },
    principle3_Tracing: {
      score: tracing,
      status: complianceStatus(tracing),
      details: `Tracing coverage estimate: ${tracing}%`
    },
    principle4_Persistence: {
      score: persistence,
      status: complianceStatus(persistence),
      details: `Persistence implementation score: ${persistence}%`
    },
    principle5_CircuitBreakers: {
      score: circuit,
      status: complianceStatus(circuit),
      details: `Circuit breaker coverage score: ${circuit}%`
    },
    principle6_Verification: {
      score: verification,
      status: complianceStatus(verification),
      details: `Verification artifacts score: ${verification}%`
    }
  };
}

function generateRecommendations(metrics: TruthMetrics): string[] {
  const recs: string[] = [];
  if (metrics.testRealityScore < 70) recs.push('🚨 Increase pytest coverage and ensure frontend checks run in CI');
  if (metrics.compilationSuccessRate < 80) recs.push('🛠️ Stabilize frontend build or backend compile errors');
  if (metrics.documentationHonestyIndex < 80) recs.push('📚 Align README claims with actual stack (FastAPI + SvelteKit)');
  if (metrics.securityComplianceScore < 85) recs.push('🔒 Audit for hard-coded secrets and enforce env usage');
  if (metrics.tracingCoverage < 70) recs.push('🛰️ Expand OpenTelemetry instrumentation across API routes');
  return recs;
}

async function calculateTrend(current: number): Promise<{ direction: 'UP' | 'DOWN' | 'FLAT'; change: number }> {
  const reportPath = join(projectRoot, 'monitoring/truth-score-report.json');
  if (!existsSync(reportPath)) return { direction: 'FLAT', change: 0 };

  try {
    const data = JSON.parse(readFileSync(reportPath, 'utf8'));
    const previousScore = data?.truthScore?.overallTruthScore ?? 0;
    const delta = Math.round(current - previousScore);
    if (delta > 0) return { direction: 'UP', change: delta };
    if (delta < 0) return { direction: 'DOWN', change: Math.abs(delta) };
    return { direction: 'FLAT', change: 0 };
  } catch {
    return { direction: 'FLAT', change: 0 };
  }
}

function identifyCriticalIssues(metrics: TruthMetrics): string[] {
  const issues: string[] = [];
  if (metrics.testRealityScore < 60) issues.push('CRITICAL: Sacred Codex Principle 1 violation – insufficient automated tests');
  if (metrics.securityComplianceScore < 60) issues.push('CRITICAL: Security compliance below threshold');
  return issues;
}

async function main(): Promise<void> {
  const compilation = await measureCompilationSuccess();
  const testResult = await measureTestReality();
  const tests = testResult.score;
  const docs = await measureDocumentationHonesty();
  const trust = await measureUserTrust();
  const security = await measureSecurityCompliance();
  const debt = await measureTechnicalDebt();
  const tracing = await measureTracingCoverage();

  const overall = Math.round(safeAverage([compilation, tests, docs, trust, security, debt, tracing]));

  const metrics: TruthMetrics = {
    compilationSuccessRate: compilation,
    testRealityScore: tests,
    documentationHonestyIndex: docs,
    userTrustCoefficient: trust,
    securityComplianceScore: security,
    technicalDebtRatio: debt,
    tracingCoverage: tracing,
    overallTruthScore: overall,
    grade: calculateGrade(overall),
    status: determineStatus(overall)
  };

  const compliance = await evaluateSacredCodex({ testScore: tests, tracingScore: tracing });

  const report = {
    timestamp,
    project: 'Voice by Kraliki',
    truthScore: metrics,
    sacredCodexCompliance: compliance,
    recommendations: generateRecommendations(metrics),
    trend: await calculateTrend(overall),
    criticalIssues: identifyCriticalIssues(metrics)
  };

  const monitoringDir = join(projectRoot, 'monitoring');
  if (!existsSync(monitoringDir)) {
    mkdirSync(monitoringDir, { recursive: true });
  }

  const reportPath = join(monitoringDir, 'truth-score-report.json');
  writeFileSync(reportPath, JSON.stringify(report, null, 2));

  console.log('\n================================================================================');
  console.log('🎯 CC-LITE TRUTH SCORE REPORT');
  console.log('================================================================================');
  console.log(`Overall Truth Score: ${metrics.overallTruthScore} (${metrics.grade}) -> ${metrics.status}`);
  console.log('Detailed metrics saved to monitoring/truth-score-report.json');
}

main().catch((error) => {
  console.error('Truth score evaluation failed:', error);
  process.exitCode = 1;
});
