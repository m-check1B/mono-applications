#!/usr/bin/env tsx
/**
 * Generate Ed25519 Keys for Voice by Kraliki Production
 *
 * This script generates cryptographically secure Ed25519 key pairs
 * and other secrets required for production deployment.
 *
 * Usage: pnpm tsx scripts/gen-keys.ts
 */

import { generateKeyPairSync, randomBytes } from 'crypto';

interface GeneratedSecrets {
  authKeys: {
    publicKey: string;
    privateKey: string;
  };
  jwt: {
    secret: string;
    refreshSecret: string;
  };
  session: {
    cookieSecret: string;
    encryptionKey: string;
    csrfSecret: string;
  };
  database: {
    password: string;
  };
  redis: {
    password: string;
  };
  rabbitmq: {
    password: string;
  };
  webhook: {
    secret: string;
  };
  monitoring: {
    authKey: string;
  };
}

function generateSecureSecret(length: number): string {
  return randomBytes(length).toString('base64');
}

function generatePassword(length: number = 24): string {
  const charset = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*';
  let password = '';
  for (let i = 0; i < length; i++) {
    password += charset.charAt(Math.floor(Math.random() * charset.length));
  }
  return password;
}

function generateSecrets(): GeneratedSecrets {
  console.log('🔐 Generating secure secrets for Voice by Kraliki production...\n');

  // Generate Ed25519 key pair
  console.log('🔑 Generating Ed25519 authentication keys...');
  const { publicKey, privateKey } = generateKeyPairSync('ed25519', {
    publicKeyEncoding: {
      type: 'spki',
      format: 'pem'
    },
    privateKeyEncoding: {
      type: 'pkcs8',
      format: 'pem'
    }
  });

  // Generate all secrets
  console.log('🔒 Generating JWT secrets...');
  const jwtSecret = generateSecureSecret(32);
  const jwtRefreshSecret = generateSecureSecret(32);

  console.log('🍪 Generating session secrets...');
  const cookieSecret = generateSecureSecret(32);
  const encryptionKey = generateSecureSecret(32);
  const csrfSecret = generateSecureSecret(32);

  console.log('🗄️ Generating database credentials...');
  const dbPassword = generatePassword(24);

  console.log('📦 Generating Redis credentials...');
  const redisPassword = generatePassword(24);

  console.log('🐰 Generating RabbitMQ credentials...');
  const rabbitmqPassword = generatePassword(24);

  console.log('🪝 Generating webhook secrets...');
  const webhookSecret = generateSecureSecret(32);

  console.log('📊 Generating monitoring secrets...');
  const monitoringAuthKey = generateSecureSecret(32);

  return {
    authKeys: {
      publicKey: publicKey.replace(/\n/g, '\\n'),
      privateKey: privateKey.replace(/\n/g, '\\n')
    },
    jwt: {
      secret: jwtSecret,
      refreshSecret: jwtRefreshSecret
    },
    session: {
      cookieSecret,
      encryptionKey,
      csrfSecret
    },
    database: {
      password: dbPassword
    },
    redis: {
      password: redisPassword
    },
    rabbitmq: {
      password: rabbitmqPassword
    },
    webhook: {
      secret: webhookSecret
    },
    monitoring: {
      authKey: monitoringAuthKey
    }
  };
}

function displaySecrets(secrets: GeneratedSecrets) {
  console.log('\n✅ All secrets generated successfully!\n');
  console.log('🚨 CRITICAL: Store these secrets securely and NEVER commit them to git!\n');

  console.log('═══════════════════════════════════════════');
  console.log('🔑 AUTHENTICATION KEYS (Ed25519)');
  console.log('═══════════════════════════════════════════');
  console.log(`AUTH_PUBLIC_KEY="${secrets.authKeys.publicKey}"`);
  console.log(`AUTH_PRIVATE_KEY="${secrets.authKeys.privateKey}"`);

  console.log('\n═══════════════════════════════════════════');
  console.log('🔐 JWT SECRETS');
  console.log('═══════════════════════════════════════════');
  console.log(`JWT_SECRET="${secrets.jwt.secret}"`);
  console.log(`JWT_REFRESH_SECRET="${secrets.jwt.refreshSecret}"`);

  console.log('\n═══════════════════════════════════════════');
  console.log('🍪 SESSION SECRETS');
  console.log('═══════════════════════════════════════════');
  console.log(`COOKIE_SECRET="${secrets.session.cookieSecret}"`);
  console.log(`SESSION_ENCRYPTION_KEY="${secrets.session.encryptionKey}"`);
  console.log(`CSRF_SECRET="${secrets.session.csrfSecret}"`);

  console.log('\n═══════════════════════════════════════════');
  console.log('🗄️ DATABASE CREDENTIALS');
  console.log('═══════════════════════════════════════════');
  console.log(`DB_PASSWORD="${secrets.database.password}"`);
  console.log(`DATABASE_URL="postgresql://cc_user:${secrets.database.password}@postgres:5432/cc_light_prod?sslmode=require"`);

  console.log('\n═══════════════════════════════════════════');
  console.log('📦 REDIS CREDENTIALS');
  console.log('═══════════════════════════════════════════');
  console.log(`REDIS_PASSWORD="${secrets.redis.password}"`);
  console.log(`REDIS_URL="redis://:${secrets.redis.password}@redis:6379"`);

  console.log('\n═══════════════════════════════════════════');
  console.log('🐰 RABBITMQ CREDENTIALS');
  console.log('═══════════════════════════════════════════');
  console.log(`RABBITMQ_PASSWORD="${secrets.rabbitmq.password}"`);

  console.log('\n═══════════════════════════════════════════');
  console.log('🪝 WEBHOOK & MONITORING');
  console.log('═══════════════════════════════════════════');
  console.log(`WEBHOOK_SECRET="${secrets.webhook.secret}"`);
  console.log(`MONITORING_AUTH_KEY="${secrets.monitoring.authKey}"`);

  console.log('\n═══════════════════════════════════════════');
  console.log('📋 DOCKER SECRETS COMMANDS');
  console.log('═══════════════════════════════════════════');
  console.log('# Create Docker secrets (run these commands):');
  console.log(`echo "${secrets.jwt.secret}" | docker secret create jwt_secret -`);
  console.log(`echo "${secrets.jwt.refreshSecret}" | docker secret create jwt_refresh_secret -`);
  console.log(`echo "${secrets.session.cookieSecret}" | docker secret create cookie_secret -`);
  console.log(`echo "${secrets.database.password}" | docker secret create db_password -`);
  console.log(`echo "${secrets.redis.password}" | docker secret create redis_password -`);
  console.log(`echo "${secrets.rabbitmq.password}" | docker secret create rabbitmq_password -`);

  console.log('\n🔒 SECURITY REMINDERS:');
  console.log('  ✓ Never commit these secrets to git');
  console.log('  ✓ Store in Docker secrets or HashiCorp Vault');
  console.log('  ✓ Rotate secrets regularly (every 90 days)');
  console.log('  ✓ Use different secrets for each environment');
  console.log('  ✓ Monitor secret access and usage');

  console.log(`\n🕐 Generated at: ${new Date().toISOString()}`);
  console.log('🔢 Secrets version: 3.0.0\n');
}

function saveSecretsTemplate(secrets: GeneratedSecrets) {
  const template = `# Voice by Kraliki Production Secrets Template
# Generated: ${new Date().toISOString()}
# Version: 3.0.0
#
# 🚨 CRITICAL SECURITY WARNING:
# - These are TEMPLATE values for Docker secrets setup
# - NEVER use these actual values in production
# - Replace ALL values with your own generated secrets
# - Store actual secrets in Docker secrets or Vault

# Authentication Keys (Ed25519)
AUTH_PUBLIC_KEY_TEMPLATE="${secrets.authKeys.publicKey}"
AUTH_PRIVATE_KEY_TEMPLATE="${secrets.authKeys.privateKey}"

# JWT Secrets
JWT_SECRET_TEMPLATE="${secrets.jwt.secret}"
JWT_REFRESH_SECRET_TEMPLATE="${secrets.jwt.refreshSecret}"

# Session Secrets
COOKIE_SECRET_TEMPLATE="${secrets.session.cookieSecret}"
SESSION_ENCRYPTION_KEY_TEMPLATE="${secrets.session.encryptionKey}"
CSRF_SECRET_TEMPLATE="${secrets.session.csrfSecret}"

# Database
DB_PASSWORD_TEMPLATE="${secrets.database.password}"

# Redis
REDIS_PASSWORD_TEMPLATE="${secrets.redis.password}"

# RabbitMQ
RABBITMQ_PASSWORD_TEMPLATE="${secrets.rabbitmq.password}"

# Webhooks
WEBHOOK_SECRET_TEMPLATE="${secrets.webhook.secret}"

# Monitoring
MONITORING_AUTH_KEY_TEMPLATE="${secrets.monitoring.authKey}"
`;

  import('fs').then(fs => {
    fs.writeFileSync('scripts/secrets-template.env', template);
    console.log('💾 Secrets template saved to: scripts/secrets-template.env');
  });
}

// Main execution
const secrets = generateSecrets();
displaySecrets(secrets);
saveSecretsTemplate(secrets);

console.log('\n🎉 Secret generation completed successfully!');
console.log('🔐 Use the displayed values to configure your production environment.');

export { generateSecrets, type GeneratedSecrets };