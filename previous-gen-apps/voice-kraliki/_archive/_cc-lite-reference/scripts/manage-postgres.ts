#!/usr/bin/env tsx

/**
 * Lightweight PostgreSQL manager that keeps the database inside the project workspace.
 * Designed for Replit and local development environments where Docker is unavailable.
 */

import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';

const ACTION = process.argv[2] ?? 'start';
const projectRoot = process.cwd();
const dataDir = path.resolve(projectRoot, process.env.PG_DATA_DIR ?? path.join('.data', 'postgres', 'data'));
const logFile = path.join(path.dirname(dataDir), 'postgres.log');
const configMarker = '# Voice by Kraliki managed configuration';

const port = process.env.PGPORT ?? process.env.LOCAL_PG_PORT ?? '5432';
const user = process.env.LOCAL_DB_USER ?? 'postgres';
const password = process.env.LOCAL_DB_PASSWORD ?? 'postgres';
const database = process.env.LOCAL_DB_NAME ?? 'cc_lite';

const defaultBinCandidates = [
  process.env.PG_BIN_DIR,
  '/usr/lib/postgresql/16/bin',
  '/usr/lib/postgresql/15/bin',
  '/usr/lib/postgresql/14/bin',
  '/usr/lib/postgresql/13/bin'
].filter((p): p is string => Boolean(p) && fs.existsSync(p));

const effectivePath = [
  ...defaultBinCandidates,
  process.env.PATH ?? ''
].filter(Boolean).join(path.delimiter);

const baseEnv = {
  ...process.env,
  PGDATA: dataDir,
  PGPORT: port,
  PGUSER: user,
  PGPASSWORD: password,
  PGHOST: '127.0.0.1',
  PATH: effectivePath
};

function ensureCommand(command: string) {
  const checker = process.platform === 'win32' ? 'where' : 'which';
  const args = [command];
  const result = spawnSync(checker, args, { stdio: 'ignore', env: { PATH: effectivePath } });
  if (result.status !== 0) {
    throw new Error(`Required PostgreSQL binary '${command}' not found in PATH.`);
  }
}

function run(command: string, args: string[], env: NodeJS.ProcessEnv = baseEnv) {
  const result = spawnSync(command, args, { env, stdio: 'inherit' });
  if (result.status !== 0) {
    throw new Error(`${command} ${args.join(' ')} failed with exit code ${result.status}`);
  }
}

function runQuiet(command: string, args: string[], env: NodeJS.ProcessEnv = baseEnv) {
  return spawnSync(command, args, { env, stdio: 'ignore' });
}

function initDatabaseIfNeeded() {
  if (fs.existsSync(path.join(dataDir, 'PG_VERSION'))) {
    return;
  }

  fs.mkdirSync(path.dirname(dataDir), { recursive: true });
  fs.mkdirSync(path.dirname(logFile), { recursive: true });

  if (fs.existsSync(dataDir)) {
    fs.rmSync(dataDir, { recursive: true, force: true });
  }

  console.log(`🆕 Initialising fresh PostgreSQL cluster at ${dataDir}`);

  const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'cc-lite-pg-'));
  const passwordFile = path.join(tmpDir, 'pgpass');
  fs.writeFileSync(passwordFile, `${password}\n`);

  try {
    run('initdb', [
      '-D',
      dataDir,
      '--username',
      user,
      '--pwfile',
      passwordFile,
      '--auth-host=scram-sha-256',
      '--auth-local=trust'
    ]);
  } finally {
    fs.rmSync(tmpDir, { recursive: true, force: true });
  }

  const confPath = path.join(dataDir, 'postgresql.conf');
  const confContents = fs.readFileSync(confPath, 'utf8');
  if (!confContents.includes(configMarker)) {
    fs.appendFileSync(
      confPath,
      `\n${configMarker}\nlisten_addresses = '127.0.0.1'\nport = ${port}\nunix_socket_directories = '${dataDir}'\nshared_buffers = 128MB\n`);
  }

  const hbaPath = path.join(dataDir, 'pg_hba.conf');
  const hbaContents = fs.readFileSync(hbaPath, 'utf8');
  if (!hbaContents.includes(configMarker)) {
    fs.appendFileSync(
      hbaPath,
      `\n${configMarker}\nlocal   all             all                                     trust\nhost    all             all             127.0.0.1/32            scram-sha-256\nhost    all             all             ::1/128                 scram-sha-256\n`);
  }
}

function isRunning(): boolean {
  if (!fs.existsSync(path.join(dataDir, 'postmaster.pid'))) {
    return false;
  }
  const status = runQuiet('pg_ctl', ['-D', dataDir, 'status']);
  return status.status === 0;
}

function startServer() {
  initDatabaseIfNeeded();

  if (isRunning()) {
    console.log('✅ PostgreSQL is already running.');
    ensureDatabase();
    return;
  }

  console.log(`🚀 Starting PostgreSQL on port ${port} (data dir: ${dataDir})`);

  run('pg_ctl', ['-D', dataDir, '-l', logFile, '-o', `-p ${port}`, 'start', '-w']);

  waitForServer();
  ensureDatabase();
  console.log('✅ PostgreSQL ready. Connection URL: postgresql://postgres:****@localhost:' + port + '/' + database);
}

function stopServer() {
  if (!isRunning()) {
    console.log('ℹ️  PostgreSQL is not running.');
    return;
  }

  console.log('🛑 Stopping PostgreSQL...');
  run('pg_ctl', ['-D', dataDir, 'stop', '-m', 'fast']);
  console.log('✅ PostgreSQL stopped.');
}

function statusServer() {
  if (!fs.existsSync(path.join(dataDir, 'PG_VERSION'))) {
    console.log('ℹ️  PostgreSQL has not been initialised.');
    return;
  }

  const result = runQuiet('pg_ctl', ['-D', dataDir, 'status']);
  if (result.status === 0) {
    console.log(`✅ PostgreSQL running (port ${port}).`);
  } else {
    console.log('⚠️  PostgreSQL is stopped.');
  }
}

function restartServer() {
  stopServer();
  startServer();
}

function resetServer() {
  stopServer();
  console.log('🧹 Removing existing data directory...');
  fs.rmSync(dataDir, { recursive: true, force: true });
  startServer();
}

function waitForServer() {
  console.log('⏳ Waiting for PostgreSQL to accept connections...');
  for (let i = 0; i < 20; i += 1) {
    const res = runQuiet('pg_isready', ['-h', '127.0.0.1', '-p', port, '-U', user]);
    if (res.status === 0) {
      return;
    }
    Atomics.wait(new Int32Array(new SharedArrayBuffer(4)), 0, 0, 250);
  }
  throw new Error('PostgreSQL did not become ready in time. Check logs at ' + logFile);
}

function ensureDatabase() {
  const env = { ...baseEnv };
  const result = runQuiet('psql', ['-lqt'], env);
  if (result.status !== 0) {
    console.warn('⚠️  Unable to list databases. Attempting to create database directly.');
  }

  const createResult = runQuiet('createdb', ['-h', '127.0.0.1', '-p', port, '-U', user, database], env);
  if (createResult.status === 0) {
    console.log(`📦 Created database '${database}'.`);
  } else {
    console.log(`ℹ️  Database '${database}' already exists.`);
  }
}

function printUsage() {
  console.log('Usage: pnpm db:cluster:start | db:cluster:stop | db:cluster:status | db:cluster:restart | db:cluster:reset');
}

try {
  ensureCommand('pg_ctl');
  ensureCommand('initdb');
  ensureCommand('createdb');
  ensureCommand('pg_isready');
  ensureCommand('psql');

  switch (ACTION) {
    case 'start':
      startServer();
      break;
    case 'stop':
      stopServer();
      break;
    case 'status':
      statusServer();
      break;
    case 'restart':
      restartServer();
      break;
    case 'reset':
      resetServer();
      break;
    default:
      printUsage();
      process.exitCode = 1;
  }
} catch (error) {
  console.error('❌ PostgreSQL manager error:', (error as Error).message);
  process.exitCode = 1;
}
