import type { PrismaClient as PrismaClientType } from '@prisma/client';

declare global {
  // eslint-disable-next-line no-var
  var __stack2025_prisma__: PrismaClientType | undefined;
}

function ensureDatabaseUrl() {
  const url = process.env.DATABASE_URL || '';
  if (!url) {
    throw new Error('DATABASE_URL is not set. Configure PostgreSQL connection.');
  }
  if (!url.includes('sslmode=require')) {
    // Encourage SSL for managed Postgres
    // Not throwing to avoid breaking local dev, but recommended.
    // eslint-disable-next-line no-console
    console.warn('[database-core] DATABASE_URL missing sslmode=require (PostgreSQL recommends SSL for production)');
  }
}

export function getPrisma(): PrismaClientType {
  ensureDatabaseUrl();
  if (globalThis.__stack2025_prisma__) return globalThis.__stack2025_prisma__;

  // Lazy import to avoid requiring @prisma/client types at module load
  const { PrismaClient } = require('@prisma/client') as { PrismaClient: new () => PrismaClientType };
  const prisma = new PrismaClient();
  globalThis.__stack2025_prisma__ = prisma;
  return prisma;
}

export async function ping(prisma: PrismaClientType = getPrisma()) {
  try {
    await prisma.$queryRaw`SELECT 1`;
    return true;
  } catch {
    return false;
  }
}

