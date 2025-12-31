#!/usr/bin/env node

/**
 * Database Setup Script for Voice by Kraliki (ESM compatible)
 * Supports PostgreSQL and generates a compatible Prisma seed.
 */

import { execSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import dotenv from 'dotenv';

dotenv.config();

const DATABASE_URL = process.env.DATABASE_URL || 'postgresql://postgres:postgres@localhost:5432/cc_lite';

console.log('🔧 Voice by Kraliki PostgreSQL Database Setup');
console.log('====================================');
console.log(`📍 Database URL: ${DATABASE_URL.replace(/:[^:@]*@/, ':****@')}`);

try {
  // Step 1: Generate Prisma Client
  console.log('\n1️⃣ Generating Prisma Client...');
  execSync('pnpm prisma generate', { stdio: 'inherit' });

  // Step 2: Ensure database exists
  console.log('\n2️⃣ Checking PostgreSQL database...');
  const dbName = DATABASE_URL.split('/').pop().split('?')[0];

  try {
    // Try to create database (will fail if exists, which is fine)
    const pgUrl = DATABASE_URL.substring(0, DATABASE_URL.lastIndexOf('/')) + '/postgres';
    execSync(`psql "${pgUrl}" -c "CREATE DATABASE ${dbName};"`, { stdio: 'ignore' });
    console.log(`   ✅ Database '${dbName}' created`);
  } catch (e) {
    console.log(`   ℹ️  Database '${dbName}' already exists (this is fine)`);
  }

  // Step 3: Run migrations
  console.log('\n3️⃣ Running database migrations...');

  if (fs.existsSync('prisma/migrations')) {
    execSync('pnpm prisma migrate deploy', { stdio: 'inherit' });
  } else {
    console.log('   Creating initial migration...');
    execSync('pnpm prisma migrate dev --name init --skip-seed', { stdio: 'inherit' });
  }

  // Step 4: Seed database
  console.log('\n4️⃣ Seeding database with demo data...');
  const shouldSeed = process.env.SEED_DEMO_USERS !== 'false';

  if (shouldSeed) {
    const hasSeed = fs.existsSync('prisma/seed.ts') || fs.existsSync('prisma/seed.js') || fs.existsSync('prisma/seed.cjs');
    if (hasSeed) {
      execSync('pnpm prisma db seed', { stdio: 'inherit' });
      console.log('   ✅ Demo data seeded');
    } else {
      console.log('   ⚠️  No seed file found, creating basic demo users...');

      // Create CommonJS seed file to work regardless of type: module
      const seedContent = `
const { PrismaClient } = require('@prisma/client');
const bcrypt = require('bcrypt');

const prisma = new PrismaClient();

async function main() {
  console.log('Seeding demo users...');

  const hashedPassword = await bcrypt.hash('Admin123!@#', 10);

  // Create demo organization
  const org = await prisma.organization.upsert({
    where: { domain: 'demo.cc-light.local' },
    update: {},
    create: {
      name: 'Demo Organization',
      domain: 'demo.cc-light.local',
      settings: {}
    }
  });

  // Create demo users
  const users = [
    { email: 'admin@cc-light.local', name: 'Admin User', role: 'ADMIN' },
    { email: 'supervisor@cc-light.local', name: 'Supervisor User', role: 'SUPERVISOR' },
    { email: 'agent1@cc-light.local', name: 'Agent One', role: 'AGENT' },
    { email: 'agent2@cc-light.local', name: 'Agent Two', role: 'AGENT' }
  ];

  for (const user of users) {
    await prisma.user.upsert({
      where: { email: user.email },
      update: {},
      create: {
        ...user,
        password: hashedPassword,
        organizationId: org.id,
        active: true
      }
    });
  }

  console.log('✅ Demo users created');
}

main()
  .catch((e) => {
    console.error('Seed error:', e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
`;

      fs.writeFileSync('prisma/seed.cjs', seedContent);

      // Update package.json to include seed script
      const packageJson = JSON.parse(fs.readFileSync('package.json', 'utf8'));
      if (!packageJson.prisma) {
        packageJson.prisma = {};
      }
      packageJson.prisma.seed = 'node prisma/seed.cjs';
      fs.writeFileSync('package.json', JSON.stringify(packageJson, null, 2));

      // Run the seed
      execSync('pnpm prisma db seed', { stdio: 'inherit' });
    }
  } else {
    console.log('   ⚠️  Skipping demo data (SEED_DEMO_USERS=false)');
  }

  // Step 5: Verify setup
  console.log('\n5️⃣ Verifying database setup...');

  const { PrismaClient } = await import('@prisma/client');
  const prisma = new PrismaClient();

  try {
    const userCount = await prisma.user.count();
    console.log(`   ✅ Database ready with ${userCount} users`);
  } catch (e) {
    console.error('   ❌ Database verification failed:', e.message);
    process.exit(1);
  } finally {
    await prisma.$disconnect();
  }

  console.log('\n✅ PostgreSQL database setup complete!');
  console.log('=====================================');
  console.log('\nYou can now run:');
  console.log('  pnpm dev        - Start development server');
  console.log('  pnpm db:studio  - Open Prisma Studio');

} catch (error) {
  console.error('\n❌ Setup failed:', error.message);
  console.error('\nTroubleshooting:');
  console.error('- Make sure PostgreSQL is running');
  console.error('- Check your DATABASE_URL in .env');
  console.error('- Try: pg_ctl start');
  console.error('- Or: sudo service postgresql start');

  process.exit(1);
}

