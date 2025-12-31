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

const BOARD_META: Record<string, { icon: string; color: string }> = {
	general: { icon: '📌', color: '#16a085' },
	ideas: { icon: '💡', color: '#1e90ff' },
	promotions: { icon: '📣', color: '#8e44ad' },
	alerts: { icon: '⚠️', color: '#f39c12' },
	critical: { icon: '🔥', color: '#e74c3c' },
	system: { icon: '🧠', color: '#7f8c8d' }
};

const titleize = (value: string) => value.replace(/[-_]+/g, ' ').trim();

const loadBoard = async () => {
	try {
		const raw = await fs.readFile(BOARD_PATH, 'utf-8');
		const data = raw.trim() ? JSON.parse(raw) : DEFAULT_BOARD;
		return {
			...DEFAULT_BOARD,
			...data,
			messages: Array.isArray(data.messages) ? data.messages : []
		};
	} catch {
		return DEFAULT_BOARD;
	}
};

export const GET: RequestHandler = async () => {
	try {
		const board = await loadBoard();
		const stats = new Map<string, { count: number; agents: Set<string> }>();

		for (const message of board.messages) {
			const topic = message.topic || 'general';
			const entry = stats.get(topic) || { count: 0, agents: new Set<string>() };
			entry.count += 1;
			entry.agents.add(message.agent || 'unknown');
			stats.set(topic, entry);
		}

		const boards = Array.from(stats.entries()).map(([topic, entry]) => {
			const meta = BOARD_META[topic] || { icon: '🗂️', color: '#2c3e50' };
			return {
				id: topic,
				name: titleize(topic),
				icon: meta.icon,
				color: meta.color,
				post_count: entry.count,
				agent_count: entry.agents.size
			};
		});

		return json(boards);
	} catch (e) {
		console.error('Failed to load insights boards:', e);
		return json([], { status: 500 });
	}
};
