/**
 * II-Agent Integration Utility
 * Bridges II-Agent WebSocket events with assistantStore
 */

import { IIAgentClient } from '$lib/agent/iiAgentClient';
import { assistantStore } from '$lib/stores/assistant';
import { contextPanelStore } from '$lib/stores/contextPanel';
import { EventType } from '$lib/agent/types';
import type { RealtimeEvent, AgentConfig } from '$lib/agent/types';
import type { WorkflowPlan, ExecutionEntry } from '$lib/stores/assistant';
import { logger } from '$lib/utils/logger';

export class IIAgentIntegration {
	private client: IIAgentClient;
	private streamingMessageId: string | null = null;
	private unsubscribers: Array<() => void> = [];

	constructor(wsUrl?: string) {
		this.client = new IIAgentClient(wsUrl);
		this.setupEventHandlers();
	}

	/**
	 * Connect to II-Agent and initialize session
	 */
	async connect(sessionUuid: string, agentToken: string, config?: AgentConfig): Promise<void> {
		try {
			// Connect WebSocket
			await this.client.connect(sessionUuid, agentToken);

			// Update store
			assistantStore.setIIAgentConnection(true, sessionUuid, agentToken);

			// Initialize agent if config provided
			if (config) {
				this.client.initAgent(config);
			}
		} catch (error: any) {
			logger.error('[IIAgentIntegration] Connection failed:', error);
			assistantStore.setIIAgentError(error.message);
			throw error;
		}
	}

	/**
	 * Disconnect from II-Agent
	 */
	disconnect(): void {
		this.client.disconnect();
		this.cleanup();
		assistantStore.setIIAgentConnection(false);
		assistantStore.setIIAgentInitialized(false);
	}

	/**
	 * Initialize agent with configuration
	 */
	initAgent(config: AgentConfig): void {
		try {
			this.client.initAgent(config);
		} catch (error: any) {
			logger.error('[IIAgentIntegration] Init agent failed:', error);
			assistantStore.setIIAgentError(error.message);
		}
	}

	/**
	 * Send a query to II-Agent
	 */
	sendQuery(text: string, files: string[] = []): void {
		try {
			// Add user message to store
			assistantStore.addMessage({
				role: 'user',
				content: text,
				source: 'ii-agent'
			});

			// Send to II-Agent
			this.client.sendQuery(text, files);
			assistantStore.setIIAgentProcessing(true);
		} catch (error: any) {
			logger.error('[IIAgentIntegration] Send query failed:', error);
			assistantStore.setIIAgentError(error.message);
		}
	}

	/**
	 * Cancel current operation
	 */
	cancel(): void {
		try {
			this.client.cancel();
			assistantStore.setIIAgentProcessing(false);
			this.streamingMessageId = null;
		} catch (error: any) {
			logger.error('[IIAgentIntegration] Cancel failed:', error);
		}
	}

	/**
	 * Get connection status
	 */
	isConnected(): boolean {
		return this.client.getConnectionStatus();
	}

	/**
	 * Cleanup resources
	 */
	cleanup(): void {
		this.unsubscribers.forEach(unsub => unsub());
		this.unsubscribers = [];
		this.streamingMessageId = null;
	}

	// ========== Private Methods ==========

	private setupEventHandlers(): void {
		// Event handler
		const unsubEvent = this.client.onEvent((event) => this.handleEvent(event));
		this.unsubscribers.push(unsubEvent);

		// Error handler
		const unsubError = this.client.onError((error) => this.handleError(error));
		this.unsubscribers.push(unsubError);

		// Close handler
		const unsubClose = this.client.onClose(() => this.handleClose());
		this.unsubscribers.push(unsubClose);
	}

	private handleEvent(event: RealtimeEvent): void {
		// Log to store
		assistantStore.addIIAgentEvent(event);

		// Route to specific handler
		switch (event.type) {
			case EventType.CONNECTION_ESTABLISHED:
				this.handleConnectionEstablished(event);
				break;
			case EventType.AGENT_INITIALIZED:
				this.handleAgentInitialized(event);
				break;
			case EventType.PROCESSING:
				this.handleProcessing(event);
				break;
			case EventType.AGENT_THINKING:
				this.handleThinking(event);
				break;
			case EventType.AGENT_RESPONSE:
				this.handleResponse(event);
				break;
			case EventType.TOOL_CALL:
				this.handleToolCall(event);
				break;
			case EventType.TOOL_RESULT:
				this.handleToolResult(event);
				break;
			case EventType.STREAM_COMPLETE:
				this.handleStreamComplete(event);
				break;
			case EventType.ERROR:
				this.handleEventError(event);
				break;
			case EventType.WORKSPACE_INFO:
				this.handleWorkspaceInfo(event);
				break;
			default:
				logger.info('[IIAgentIntegration] Unhandled event:', { type: event.type });
		}
	}

	private handleConnectionEstablished(event: RealtimeEvent): void {
		assistantStore.setIIAgentConnection(true);
		logger.info('[IIAgentIntegration] Connection established');
	}

	private handleAgentInitialized(event: RealtimeEvent): void {
		const modelName = event.content.model_name || event.content.model;
		assistantStore.setIIAgentInitialized(true, modelName);
		logger.info('[IIAgentIntegration] Agent initialized:', { modelName });
	}

	private handleProcessing(event: RealtimeEvent): void {
		assistantStore.setIIAgentProcessing(true);
	}

	private handleThinking(event: RealtimeEvent): void {
		const thinking = event.content.thinking || event.content.text || 'Thinking...';

		if (this.streamingMessageId) {
			// Update existing message
			assistantStore.updateMessage(this.streamingMessageId, {
				metadata: { thinking }
			});
		} else {
			// Create new assistant message with thinking state
			const msg = assistantStore.addMessage({
				role: 'assistant',
				content: '',
				source: 'ii-agent',
				metadata: { thinking }
			});
			this.streamingMessageId = msg.id;
		}
	}

	private handleResponse(event: RealtimeEvent): void {
		const text = event.content.text || event.content.content || '';

		if (this.streamingMessageId) {
			// Append to existing message
			const state = assistantStore.getState();
			const currentMsg = state.messages.find(m => m.id === this.streamingMessageId);
			const currentContent = currentMsg?.content || '';

			assistantStore.updateMessage(this.streamingMessageId, {
				content: currentContent + text,
				metadata: {
					...currentMsg?.metadata,
					thinking: undefined // Clear thinking state
				}
			});
		} else {
			// Create new message
			const msg = assistantStore.addMessage({
				role: 'assistant',
				content: text,
				source: 'ii-agent'
			});
			this.streamingMessageId = msg.id;
		}
	}

	private handleToolCall(event: RealtimeEvent): void {
		const toolName = event.content.tool_name || event.content.name || 'unknown';
		const toolArgs = event.content.arguments || event.content.args || {};
		const toolId = event.content.tool_id || crypto.randomUUID?.() || String(Date.now());

		if (this.streamingMessageId) {
			const state = assistantStore.getState();
			const currentMsg = state.messages.find(m => m.id === this.streamingMessageId);
			const toolCalls = currentMsg?.metadata?.toolCalls || [];

			assistantStore.updateMessage(this.streamingMessageId, {
				metadata: {
					...currentMsg?.metadata,
					toolCalls: [
						...toolCalls,
						{
							id: toolId,
							name: toolName,
							arguments: toolArgs,
							status: 'running',
							timestamp: new Date()
						}
					]
				}
			});
		}

		// Check if this is a Focus Tool and extract execution data
		this.extractExecutionFromToolCall(toolName, toolArgs);
	}

	private handleToolResult(event: RealtimeEvent): void {
		const toolName = event.content.tool_name || event.content.name;
		const toolId = event.content.tool_id;
		const result = event.content.result || event.content.output;
		const isError = event.content.is_error || false;

		if (this.streamingMessageId) {
			const state = assistantStore.getState();
			const currentMsg = state.messages.find(m => m.id === this.streamingMessageId);
			const toolCalls = currentMsg?.metadata?.toolCalls || [];

			// Update matching tool call
			const updatedToolCalls = toolCalls.map(tc => {
				const matches = toolId ? tc.id === toolId : tc.name === toolName && tc.status === 'running';
				if (matches) {
					return {
						...tc,
						result,
						status: isError ? 'error' : 'completed'
					} as const;
				}
				return tc;
			});

			assistantStore.updateMessage(this.streamingMessageId, {
				metadata: {
					...currentMsg?.metadata,
					toolCalls: updatedToolCalls
				}
			});
		}

		// Extract execution results
		this.extractExecutionFromToolResult(toolName, result);
	}

	private handleStreamComplete(event: RealtimeEvent): void {
		assistantStore.setIIAgentProcessing(false);
		this.streamingMessageId = null;
		logger.info('[IIAgentIntegration] Stream complete');
	}

	private handleEventError(event: RealtimeEvent): void {
		const error = event.content.error || event.content.message || 'Unknown error';
		assistantStore.setIIAgentError(error);
		assistantStore.setIIAgentProcessing(false);

		// Add error message
		assistantStore.addMessage({
			role: 'system',
			content: `Error: ${error}`,
			source: 'ii-agent'
		});

		this.streamingMessageId = null;
	}

	private handleWorkspaceInfo(event: RealtimeEvent): void {
		logger.info('[IIAgentIntegration] Workspace info:', { content: event.content });
	}

	private handleError(error: Error): void {
		logger.error('[IIAgentIntegration] Error:', error);
		assistantStore.setIIAgentError(error.message);
	}

	private handleClose(): void {
		assistantStore.setIIAgentConnection(false);
		assistantStore.setIIAgentInitialized(false);
		this.streamingMessageId = null;
		logger.info('[IIAgentIntegration] Connection closed');
	}

	// ========== Execution Extraction ==========

	/**
	 * Extract execution entries from Focus Tool calls
	 */
	private extractExecutionFromToolCall(toolName: string, args: any): void {
		// Map tool calls to execution entries
		switch (toolName) {
			case 'create_task':
			case 'update_task':
				this.createTaskExecution(args);
				// ✨ AUTO-OPEN TASKS PANEL (Gap #4 fix)
				contextPanelStore.open('tasks', args);
				logger.info(`[AI-First] Auto-opened tasks panel after ${toolName}`);
				break;
			case 'create_knowledge_item':
			case 'update_knowledge_item':
				this.createKnowledgeExecution(args);
				// ✨ AUTO-OPEN KNOWLEDGE PANEL (Gap #4 fix)
				contextPanelStore.open('knowledge', args);
				logger.info(`[AI-First] Auto-opened knowledge panel after ${toolName}`);
				break;
			case 'create_calendar_event':
			case 'update_calendar_event':
				this.createEventExecution(args);
				// ✨ AUTO-OPEN CALENDAR PANEL (Gap #4 fix)
				contextPanelStore.open('calendar', args);
				logger.info(`[AI-First] Auto-opened calendar panel after ${toolName}`);
				break;
		}
	}

	/**
	 * Extract execution results from tool outputs
	 */
	private extractExecutionFromToolResult(toolName: string, result: any): void {
		if (!result || typeof result !== 'object') return;

		// Extract created entities from results
		if (result.task_id || result.id) {
			switch (toolName) {
				case 'create_task':
				case 'update_task':
					this.updateTaskExecution(result);
					break;
				case 'create_knowledge_item':
				case 'update_knowledge_item':
					this.updateKnowledgeExecution(result);
					break;
				case 'create_calendar_event':
				case 'update_calendar_event':
					this.updateEventExecution(result);
					break;
			}
		}
	}

	private createTaskExecution(args: any): void {
		if (!args.title) return;

		assistantStore.addExecutionEntry({
			type: 'task',
			title: args.title,
			status: args.status || 'pending',
			meta: args.due_date ? `Due ${new Date(args.due_date).toLocaleDateString()}` : undefined,
			typeLabel: 'Task',
			content: args.description,
			sourceMessageId: this.streamingMessageId || undefined
		});
	}

	private updateTaskExecution(result: any): void {
		// Task created/updated successfully - execution entry already added
		logger.info('[IIAgentIntegration] Task execution:', { result });
	}

	private createKnowledgeExecution(args: any): void {
		if (!args.title) return;

		assistantStore.addExecutionEntry({
			type: 'knowledge',
			title: args.title,
			status: args.completed ? 'completed' : 'active',
			meta: args.type_id ? `Type: ${args.type_id}` : undefined,
			typeLabel: 'Knowledge',
			content: args.content,
			sourceMessageId: this.streamingMessageId || undefined
		});
	}

	private updateKnowledgeExecution(result: any): void {
		logger.info('[IIAgentIntegration] Knowledge execution:', { result });
	}

	private createEventExecution(args: any): void {
		if (!args.title) return;

		assistantStore.addExecutionEntry({
			type: 'event',
			title: args.title,
			status: 'scheduled',
			meta: args.start_time ? `Scheduled ${new Date(args.start_time).toLocaleString()}` : undefined,
			typeLabel: 'Calendar Event',
			content: args.description,
			sourceMessageId: this.streamingMessageId || undefined
		});
	}

	private updateEventExecution(result: any): void {
		logger.info('[IIAgentIntegration] Event execution:', { result });
	}
}

/**
 * Create singleton integration instance
 */
export function createIIAgentIntegration(wsUrl?: string): IIAgentIntegration {
	return new IIAgentIntegration(wsUrl);
}
