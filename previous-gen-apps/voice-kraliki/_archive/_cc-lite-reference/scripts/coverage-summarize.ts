#!/usr/bin/env tsx
import { readFileSync, writeFileSync, existsSync, mkdirSync } from 'node:fs';
import { resolve } from 'node:path';

type Metric = { total: number; covered: number; skipped: number; pct: number };
type Summary = { total: Metric; [k: string]: any };

function pct(covered: number, total: number): number {
  return total === 0 ? 100 : Math.round((covered / total) * 10000) / 100;
}

function summarize() {
  const finalPath = resolve('coverage/coverage-final.json');
  if (!existsSync(finalPath)) {
    console.error('coverage-final.json not found, run vitest with coverage first');
    process.exit(1);
  }
  const data = JSON.parse(readFileSync(finalPath, 'utf8')) as Record<string, any>;
  let sTotal = 0, sCovered = 0, bTotal = 0, bCovered = 0, fTotal = 0, fCovered = 0;
  for (const file of Object.keys(data)) {
    const m = data[file];
    if (m && m.s) {
      const sKeys = Object.keys(m.s);
      sTotal += sKeys.length;
      sCovered += sKeys.reduce((acc, k) => acc + (m.s[k] > 0 ? 1 : 0), 0);
    }
    if (m && m.b) {
      const bKeys = Object.keys(m.b);
      bTotal += bKeys.reduce((acc, k) => acc + (Array.isArray(m.b[k]) ? m.b[k].length : 1), 0);
      bCovered += bKeys.reduce((acc, k) => {
        const v = m.b[k];
        if (Array.isArray(v)) return acc + v.filter((x: number) => x > 0).length;
        return acc + (v > 0 ? 1 : 0);
      }, 0);
    }
    if (m && m.f) {
      const fKeys = Object.keys(m.f);
      fTotal += fKeys.length;
      fCovered += fKeys.reduce((acc, k) => acc + (m.f[k] > 0 ? 1 : 0), 0);
    }
  }
  const summary: Summary = {
    total: {
      lines: { total: sTotal, covered: sCovered, skipped: 0, pct: pct(sCovered, sTotal) },
      statements: { total: sTotal, covered: sCovered, skipped: 0, pct: pct(sCovered, sTotal) },
      functions: { total: fTotal, covered: fCovered, skipped: 0, pct: pct(fCovered, fTotal) },
      branches: { total: bTotal, covered: bCovered, skipped: 0, pct: pct(bCovered, bTotal) },
    }
  } as any;
  const outPath = resolve('coverage/coverage-summary.json');
  mkdirSync(resolve('coverage'), { recursive: true });
  writeFileSync(outPath, JSON.stringify(summary, null, 2));
  console.log('coverage summary written to', outPath);
}

summarize();
