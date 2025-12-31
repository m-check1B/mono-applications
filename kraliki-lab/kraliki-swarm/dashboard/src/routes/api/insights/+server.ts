import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { exec } from 'child_process';
import { promisify } from 'util';
import * as fs from 'fs/promises';
import * as path from 'path';

const execAsync = promisify(exec);
const DARWIN2_DIR = process.env.DARWIN2_PATH || '/home/adminmatej/github/applications/kraliki-lab/kraliki-swarm';
const BOARD_FILE = `${DARWIN2_DIR}/arena/data/board.json`;

interface Insight {
	id: string;
	agent: string;
	category: string;
	title: string;
	content: string;
	importance: 'critical' | 'high' | 'medium' | 'low';
	timestamp: string;
	upvotes: number;
}

export const GET: RequestHandler = async () => {
	try {
		// Try to read board.json for insights
		let insights: Insight[] = [];

		try {
			const data = await fs.readFile(BOARD_FILE, 'utf-8');
			const board = JSON.parse(data);
			if (board.posts) {
				insights = board.posts.slice(0, 50).map((post: any) => ({
					id: post.id || Math.random().toString(36).substr(2, 9),
					agent: post.author || 'unknown',
					category: post.category || 'general',
					title: post.title || post.content?.substring(0, 50) || 'Untitled',
					content: post.content || '',
					importance: post.importance || 'medium',
					timestamp: post.timestamp || new Date().toISOString(),
					upvotes: post.upvotes || 0
				}));
			}
		} catch {
			// If board.json doesn't exist or is empty, return empty array
		}

		return json({
			insights,
			lastUpdated: new Date().toISOString(),
			categories: ['revenue', 'technical', 'strategy', 'blockers', 'general']
		});
	} catch (e) {
		console.error('Failed to get insights:', e);
		return json({
			insights: [],
			error: e instanceof Error ? e.message : 'Unknown error',
			lastUpdated: new Date().toISOString()
		}, { status: 500 });
	}
};

export const POST: RequestHandler = async ({ request }) => {
	try {
		const insight = await request.json();

		// Read existing board
		let board: { posts: any[] } = { posts: [] };
		try {
			const data = await fs.readFile(BOARD_FILE, 'utf-8');
			board = JSON.parse(data);
		} catch {
			// File doesn't exist, use empty board
		}

		// Add new insight
		const newInsight = {
			id: Math.random().toString(36).substr(2, 9),
			...insight,
			timestamp: new Date().toISOString(),
			upvotes: 0
		};

		board.posts = [newInsight, ...board.posts];

		// Write back
		await fs.writeFile(BOARD_FILE, JSON.stringify(board, null, 2));

		return json({ success: true, insight: newInsight });
	} catch (e) {
		console.error('Failed to post insight:', e);
		return json({
			error: 'Failed to post insight',
			details: e instanceof Error ? e.message : 'Unknown error'
		}, { status: 500 });
	}
};
