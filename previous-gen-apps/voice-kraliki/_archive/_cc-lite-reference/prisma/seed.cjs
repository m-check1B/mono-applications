/* Prisma seed for Voice by Kraliki demo users (CommonJS for compatibility) */
// eslint-disable-next-line @typescript-eslint/no-var-requires
const { PrismaClient } = require('@prisma/client');
// eslint-disable-next-line @typescript-eslint/no-var-requires
const bcrypt = require('bcrypt');

const prisma = new PrismaClient();

async function main() {
  console.log('Seeding Voice by Kraliki demo users...');

  const hashedPassword = await bcrypt.hash('Admin123!@#', 10);

  const org = await prisma.organization.upsert({
    where: { domain: 'demo.cc-light.local' },
    update: {},
    create: {
      name: 'Demo Organization',
      domain: 'demo.cc-light.local',
      settings: {}
    }
  });

  const users = [
    { email: 'admin@cc-light.local', firstName: 'Admin', lastName: 'User', role: 'ADMIN' },
    { email: 'supervisor@cc-light.local', firstName: 'Supervisor', lastName: 'User', role: 'SUPERVISOR' },
    { email: 'agent1@cc-light.local', firstName: 'Agent', lastName: 'One', role: 'AGENT' },
    { email: 'agent2@cc-light.local', firstName: 'Agent', lastName: 'Two', role: 'AGENT' }
  ];

  for (const user of users) {
    const usernameBase = user.email.split('@')[0];
    const username = `${usernameBase}_${user.role.toLowerCase()}`;

    await prisma.user.deleteMany({ where: { username } });

    await prisma.user.upsert({
      where: { email: user.email },
      update: {},
      create: {
        ...user,
        username,
        passwordHash: hashedPassword,
        organizationId: org.id,
        skills: [],
        preferences: {}
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
