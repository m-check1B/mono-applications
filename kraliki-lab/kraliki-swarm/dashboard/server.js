// Custom server with WebSocket support for terminal
import express from 'express';
import { WebSocketServer } from 'ws';
import { spawn } from 'node-pty';
import { createServer } from 'http';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

function loadEnvFile(filePath) {
	if (!fs.existsSync(filePath)) {
		return;
	}

	const lines = fs.readFileSync(filePath, 'utf-8').split(/\r?\n/);
	for (const rawLine of lines) {
		const line = rawLine.trim();
		if (!line || line.startsWith('#') || !line.includes('=')) {
			continue;
		}

		const [keyPart, ...valueParts] = line.split('=');
		const key = keyPart.trim();
		if (!key || (process.env[key] ?? '') !== '') {
			continue;
		}

		let value = valueParts.join('=').trim();
		if (
			(value.startsWith('"') && value.endsWith('"')) ||
			(value.startsWith("'") && value.endsWith("'"))
		) {
			value = value.slice(1, -1);
		}
		process.env[key] = value;
	}
}

function loadEnvFiles() {
	const envPaths = [
		path.join(__dirname, '.env'),
		'/home/adminmatej/github/secrets/kraliki-dashboard.env',
		'/home/adminmatej/github/secrets/kraliki-swarm-dashboard.env'
	];

	for (const envPath of envPaths) {
		loadEnvFile(envPath);
	}
}

loadEnvFiles();

const app = express();
const server = createServer(app);
const wss = new WebSocketServer({ server, path: '/ws/terminal' });

const PORT = process.env.PORT || 8099;
const HOST = process.env.HOST || '172.17.0.1';

// Terminal sessions map
const sessions = new Map();

// WebSocket terminal handler
wss.on('connection', (ws, req) => {
	const url = new URL(req.url, `http://${req.headers.host}`);
	const sessionId = url.searchParams.get('sessionId') || Math.random().toString(36).substring(7);
	
	console.log(`[TERMINAL] Connection for session: ${sessionId}`);

	let session = sessions.get(sessionId);

	if (session) {
		console.log(`[TERMINAL] Reattaching to session: ${sessionId}`);
		// Close previous socket if it exists and is open
		if (session.ws && session.ws !== ws && session.ws.readyState === ws.OPEN) {
			session.ws.close();
		}
		session.ws = ws;

		// Send buffer to the new client
		if (session.buffer) {
			ws.send(session.buffer);
		}
	} else {
		console.log(`[TERMINAL] Creating new session: ${sessionId}`);
		// Spawn PTY for proper terminal emulation
		const pty = spawn('/bin/bash', ['-i'], {
			name: 'xterm-256color',
			cols: 80,
			rows: 24,
			cwd: '/home/adminmatej/github',
			env: {
				...process.env,
				TERM: 'xterm-256color',
				COLORTERM: 'truecolor',
				PS1: '\\[\\033[01;32m\\]kraliki\\[\\033[00m\\]:\\[\\033[01;34m\\]\\w\\[\\033[00m\\]\\$ '
			}
		});

		session = {
			pty,
			ws,
			buffer: '',
			lastActivity: Date.now()
		};
		sessions.set(sessionId, session);

		pty.onData((data) => {
			session.lastActivity = Date.now();
			// Add to buffer (keep last 100KB)
			session.buffer += data;
			if (session.buffer.length > 102400) {
				session.buffer = session.buffer.substring(session.buffer.length - 102400);
			}

			// Send to current WebSocket
			if (session.ws && session.ws.readyState === ws.OPEN) {
				session.ws.send(data);
			}
		});

		pty.onExit(({ exitCode, signal }) => {
			console.log(`[TERMINAL] Shell exited with code ${exitCode}, signal ${signal} for session ${sessionId}`);
			if (session.ws && session.ws.readyState === ws.OPEN) {
				session.ws.send(`\r\n[Shell exited with code ${exitCode}]\r\n`);
				session.ws.close();
			}
			sessions.delete(sessionId);
		});
	}

	// Handle input from client
	ws.on('message', (data) => {
		session.lastActivity = Date.now();
		try {
			const message = JSON.parse(data.toString());
			if (message.type === 'resize' && message.cols && message.rows) {
				session.pty.resize(message.cols, message.rows);
			} else if (message.type === 'input' && message.data) {
				session.pty.write(message.data);
			} else if (message.type === 'kill') {
				console.log(`[TERMINAL] Killing session: ${sessionId}`);
				session.pty.kill();
				sessions.delete(sessionId);
			}
		} catch (e) {
			// Legacy: treat raw data as input
			session.pty.write(data.toString());
		}
	});

	// Handle client disconnect
	ws.on('close', () => {
		console.log(`[TERMINAL] Client disconnected from session: ${sessionId} (PTY remains)`);
		if (session.ws === ws) {
			session.ws = null;
		}
	});

	ws.on('error', (err) => {
		console.error(`[TERMINAL] WebSocket error for session ${sessionId}:`, err);
		if (session.ws === ws) {
			session.ws = null;
		}
	});
});

// Periodic cleanup of abandoned sessions (no client for > 1 hour)
setInterval(() => {
	const now = Date.now();
	sessions.forEach((session, sessionId) => {
		if (!session.ws && now - session.lastActivity > 3600000) {
			console.log(`[TERMINAL] Cleaning up abandoned session: ${sessionId}`);
			session.pty.kill();
			sessions.delete(sessionId);
		}
	});
}, 600000);

async function start() {
	const { handler } = await import('./build/handler.js');

	// SvelteKit handler
	app.use(handler);

	// Start server
	server.listen(PORT, HOST, () => {
		console.log(`Listening on http://${HOST}:${PORT}`);
		console.log(`WebSocket terminal available at ws://${HOST}:${PORT}/ws/terminal`);
	});

	// Cleanup on exit
	process.on('SIGTERM', () => {
		console.log('[TERMINAL] Cleaning up sessions...');
		sessions.forEach(({ pty }) => {
			if (pty) {
				pty.kill();
			}
		});
		server.close();
		process.exit(0);
	});
}

start();
