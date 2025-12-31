import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import fs from 'fs/promises';
import path from 'path';

const KRALIKI_BASE = process.env.DARWIN2_PATH || '/home/adminmatej/github/applications/kraliki-lab/kraliki-swarm';
const BOARD_PATH = path.join(KRALIKI_BASE, 'arena', 'data', 'board.json');

const DEFAULT_BOARD = {
	created: '',
	messages: [] as any[],
	topics: {} as Record<string, any>,
	announcements: [] as any[]
};

const loadMessages = async () => {
	try {
		const raw = await fs.readFile(BOARD_PATH, 'utf-8');
		const data = raw.trim() ? JSON.parse(raw) : DEFAULT_BOARD;
		return Array.isArray(data.messages) ? data.messages : [];
	} catch {
		return [];
	}
};

const toPost = (message: any) => {
	const topic = message.topic || 'general';
	return {
		id: String(message.id || Math.random().toString(36).slice(2)),
		board: topic,
		content_type: topic === 'ideas' ? 'journal' : 'updates',
		agent_name: message.agent || 'unknown',
		agent_type: topic,
		content: message.message || '',
		created_at: message.time || new Date().toISOString(),
		tags: topic ? [topic] : []
	};
};

export const GET: RequestHandler = async ({ params }) => {
	try {
		const boardId = params.boardId;
		const messages = await loadMessages();
		const posts = messages
			.filter((message) => (message.topic || 'general') === boardId)
			.sort((a, b) => String(b.time || '').localeCompare(String(a.time || '')))
			.map(toPost);

		return json({ posts });
	} catch (e) {
		console.error('Failed to load insight posts by board:', e);
		return json({ posts: [] }, { status: 500 });
	}
};
