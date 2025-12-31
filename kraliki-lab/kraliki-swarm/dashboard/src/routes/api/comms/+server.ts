import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import fs from 'fs/promises';
import path from 'path';

const DARWIN2_DIR = process.env.DARWIN2_PATH || '/home/adminmatej/github/applications/kraliki-lab/kraliki-swarm';
const BOARD_PATH = path.join(DARWIN2_DIR, 'arena', 'data', 'board.json');

const EMPTY_BOARD = {
	created: '',
	messages: [],
	topics: {},
	announcements: []
};

const ensureBoard = async () => {
	await fs.mkdir(path.dirname(BOARD_PATH), { recursive: true });
	try {
		await fs.access(BOARD_PATH);
	} catch {
		const created = new Date().toISOString();
		await fs.writeFile(
			BOARD_PATH,
			JSON.stringify({ ...EMPTY_BOARD, created }, null, 2)
		);
	}
};

const loadBoard = async () => {
	await ensureBoard();
	const raw = await fs.readFile(BOARD_PATH, 'utf-8');
	const data = raw.trim() ? JSON.parse(raw) : EMPTY_BOARD;
	return {
		...EMPTY_BOARD,
		...data,
		messages: Array.isArray(data.messages) ? data.messages : []
	};
};

const saveBoard = async (data: typeof EMPTY_BOARD & { messages: any[]; topics: Record<string, any> }) => {
	await fs.writeFile(BOARD_PATH, JSON.stringify(data, null, 2));
};

export const GET: RequestHandler = async ({ url }) => {
	try {
		const limitParam = url.searchParams.get('limit') || '30';
		const topic = url.searchParams.get('topic') || '';
		const search = url.searchParams.get('search') || '';
		const limit = Number.parseInt(limitParam, 10) || 30;
		const board = await loadBoard();

		let messages = board.messages;
		if (topic) {
			messages = messages.filter((m: any) => m.topic === topic);
		}
		if (search) {
			const needle = search.toLowerCase();
			messages = messages.filter((m: any) => {
				const messageText = String(m.message || '').toLowerCase();
				const agentText = String(m.agent || '').toLowerCase();
				const topicText = String(m.topic || '').toLowerCase();
				return messageText.includes(needle) || agentText.includes(needle) || topicText.includes(needle);
			});
		}

		messages = messages.slice(-limit).map((m: any) => ({
			timestamp: m.time?.slice(0, 16) || '',
			topic: m.topic || 'general',
			agent: m.agent || 'unknown',
			message: m.message || ''
		}));

		return json({
			messages,
			count: messages.length,
			search: search || null,
			lastUpdated: new Date().toISOString()
		});
	} catch (e) {
		console.error('Failed to read blackboard:', e);
		return json({
			messages: [],
			error: e instanceof Error ? e.message : 'Unknown error',
			lastUpdated: new Date().toISOString()
		}, { status: 500 });
	}
};

export const POST: RequestHandler = async ({ request }) => {
	try {
		const { agent, topic, message } = await request.json();

		if (!agent || !topic || !message) {
			return json({ error: 'Agent, topic, and message required' }, { status: 400 });
		}

		const board = await loadBoard();
		const timestamp = new Date().toISOString();
		const entry = {
			id: (board.messages.length || 0) + 1,
			time: timestamp,
			agent,
			topic,
			priority: 'normal',
			priority_level: 2,
			message
		};

		board.messages.push(entry);
		board.topics[topic] = board.topics[topic] || {
			created: timestamp,
			message_count: 0
		};
		board.topics[topic].message_count += 1;
		board.topics[topic].last_message = timestamp;
		await saveBoard(board);

		return json({
			success: true,
			output: entry,
			error: null
		});
	} catch (e) {
		console.error('Failed to post to blackboard:', e);
		return json({
			error: 'Failed to post',
			details: e instanceof Error ? e.message : 'Unknown error'
		}, { status: 500 });
	}
};
