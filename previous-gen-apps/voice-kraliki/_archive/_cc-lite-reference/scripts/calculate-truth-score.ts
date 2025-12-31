#!/usr/bin/env tsx
import { TruthScoreMonitor } from './truth-score';

async function main() {
  const monitor = new TruthScoreMonitor();
  const metrics = await monitor.calculateTruthScore();
  const compliance = await monitor.evaluateSacredCodexCompliance();

  const asJson = process.argv.includes('--json');
  if (asJson) {
    const payload = { timestamp: new Date().toISOString(), ...metrics, compliance };
    console.log(JSON.stringify(payload, null, 2));
  } else {
    // Reuse monitor display for human readable output
    // @ts-ignore accessing private is fine for CLI output reuse; fall back to simple log if signature changes
    if (typeof (monitor as any).displayResults === 'function') {
      (monitor as any).displayResults(metrics, compliance);
    } else {
      console.log('Truth Score:', metrics.overallTruthScore);
      console.log('Status:', metrics.status);
    }
  }
}

main().catch((err) => {
  console.error('Failed to calculate truth score:', err);
  process.exit(1);
});

