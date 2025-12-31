import { browser } from '$app/environment';
import { logger } from '$lib/utils/logger';

const QUEUE_KEY = 'assistant_command_queue';

export interface AssistantQueuedCommand {
	id: string;
	prompt: string;
	createdAt: string;
	context?: Record<string, unknown>;
}

function readQueue(): AssistantQueuedCommand[] {
	if (!browser) return [];
	try {
		const raw = localStorage.getItem(QUEUE_KEY);
		return raw ? (JSON.parse(raw) as AssistantQueuedCommand[]) : [];
	} catch (error) {
		logger.error('Failed to read assistant queue', error);
		return [];
	}
}

function writeQueue(queue: AssistantQueuedCommand[]) {
	if (!browser) return;
	localStorage.setItem(QUEUE_KEY, JSON.stringify(queue));
}

export function enqueueAssistantCommand(command: Omit<AssistantQueuedCommand, 'id' | 'createdAt'>) {
	if (!browser) return;
	const queue = readQueue();
	queue.push({
		id: crypto.randomUUID?.() || String(Date.now()),
		prompt: command.prompt,
		createdAt: new Date().toISOString(),
		context: command.context
	});
	writeQueue(queue);
}

export function consumeAssistantQueue(): AssistantQueuedCommand[] {
	if (!browser) return [];
	const queue = readQueue();
	localStorage.removeItem(QUEUE_KEY);
	return queue;
}
